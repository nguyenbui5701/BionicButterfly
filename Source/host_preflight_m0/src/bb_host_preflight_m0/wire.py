"""Pure preflight boundary. No runner, clock, sink, mixer or adapter is called."""

from dataclasses import dataclass
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Literal, Mapping

from .diagnostics import Issue, sidecar
from .exact_decimal import ExactNumber
from .lexer import Reader
from .schema import check

WIRE_SCHEMA_FINGERPRINT = "af147b6b2d19a4176822404537bce876246fd83e3e6a954b53cb614f623221c8"


@dataclass(frozen=True)
class PolicyLimits:
    """The frozen TASK-001 limits; not a host policy approval/allowlist."""
    max_input_bytes: int = 2_097_152
    max_depth: int = 16
    max_events: int = 20_000


@dataclass(frozen=True)
class AcceptedPreflight:
    scenario: Mapping
    status: Literal["ACCEPTED_PREFLIGHT"] = "ACCEPTED_PREFLIGHT"


@dataclass(frozen=True)
class RejectedPreflight:
    diagnostic: dict
    status: Literal["VALIDATION_REJECTED"] = "VALIDATION_REJECTED"


def _semantic(data: dict):
    events = data["events"]
    seen = set()
    for index, event in enumerate(events):
        if event["event_id"] in seen:
            raise Issue("P_EVENT_ID_DUPLICATE", ("events", index, "event_id"))
        seen.add(event["event_id"])
    for index, event in enumerate(events):
        zero = event["event_at_us"].compare_int(0) == 0
        boot = event["type"] == "BOOT"
        if (index == 0 and not (zero and boot)) or (index > 0 and (zero or boot)):
            raise Issue("P_BOOT_SEQUENCE", ("events", index))
    times = [event["event_at_us"].bounded_int() for event in events]
    for index in range(1, len(times)):
        if times[index] < times[index - 1]:
            raise Issue("P_EVENT_TIMESTAMP_ORDER", ("events", index, "event_at_us"))
    duration = data["duration_us"].bounded_int()
    for index, time in enumerate(times):
        if time > duration:
            raise Issue("P_EVENT_TIMESTAMP_RANGE", ("events", index, "event_at_us"))
    # Canonical path order inside each semantic category: events before scenario_id.
    identifiers = [(("events", i, "event_id"), event["event_id"], 64)
                   for i, event in enumerate(events)]
    identifiers.append((("scenario_id",), data["scenario_id"], 256))
    for path, value, limit in identifiers:
        if len(value.encode("utf-8")) > limit:
            raise Issue("P_IDENTIFIER_BYTES", path)
    for path, value, _ in identifiers:
        if any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in value):
            raise Issue("P_IDENTIFIER_CONTROL", path)
    for index, event in enumerate(events):
        if event["type"] == "SIM_CONTROL_FRAME" and event["payload"]["uart_frame_status"] == "VALID":
            for name in ("flap_demand", "steering_demand"):
                try:
                    event["payload"][name].micros()
                except ValueError:
                    raise Issue("P_DECIMAL_PRECISION", ("events", index, "payload", name)) from None


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(value[key]) for key in sorted(value, key=lambda x: x.encode("utf-8"))})
    if isinstance(value, list):
        return tuple(map(_freeze, value))
    if isinstance(value, ExactNumber):
        return value.accepted_value()
    return value


def validate_wire(raw_bytes: bytes, frozen_wire_v2_schema: dict,
                  policy_limits: PolicyLimits = PolicyLimits()) -> AcceptedPreflight | RejectedPreflight:
    """Validate original bytes; wrong trusted-call arguments raise, never P_*.

    Schema must be the approved decoded JSON object. Its serialization order is
    immaterial. Altered schemas/limits are caller errors, not scenario errors.
    A successful result contains deeply immutable exact numeric scenario data.
    """
    if type(raw_bytes) is not bytes:
        raise TypeError("raw_bytes must be immutable bytes")
    if type(policy_limits) is not PolicyLimits or any(
        type(value) is not int for value in vars(policy_limits).values()
    ) or policy_limits != PolicyLimits():
        raise ValueError("only frozen TASK-001 limits are supported")
    encoded_schema = json.dumps(frozen_wire_v2_schema, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if sha256(encoded_schema).hexdigest() != WIRE_SCHEMA_FINGERPRINT:
        raise ValueError("wire schema differs from the approved contract")
    try:
        if len(raw_bytes) > policy_limits.max_input_bytes:
            raise Issue("P_INPUT_TOO_LARGE")
        try:
            text = raw_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            raise Issue("P_UTF8_INVALID") from None
        if text.startswith("\ufeff"):
            raise Issue("P_UTF8_BOM")
        data = Reader(text).read()
        check(data, frozen_wire_v2_schema)
        _semantic(data)
        return AcceptedPreflight(_freeze(data))
    except Issue as issue:
        return RejectedPreflight(sidecar(raw_bytes, issue))


validateWire = validate_wire
