"""Design/182 E2 diagnostic comparison; no runtime authorization or host attestation.

The caller must obtain preflight from genuine TASK-001 validate_wire. Exact Python
types and header checks detect malformed data, not its origin. An identical forged
object cannot be authenticated here and receives no more authority than real data.
"""

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from types import MappingProxyType

from bb_host_preflight_m0 import AcceptedPreflight, RejectedPreflight
from bb_host_preflight_m0.diagnostics import STAGES


class HostReferenceOutcome(str, Enum):
    REFERENCE_MATCH_NO_AUTHORITY = "REFERENCE_MATCH_NO_AUTHORITY"
    REFERENCE_MISMATCH = "REFERENCE_MISMATCH"
    UPSTREAM_REJECTED = "UPSTREAM_REJECTED"


class HostReferenceReason(str, Enum):
    UPSTREAM_REJECTED = "UPSTREAM_REJECTED"
    POLICY_BYTES_MISMATCH = "POLICY_BYTES_MISMATCH"
    CONTEXT_MISMATCH = "CONTEXT_MISMATCH"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    OWNER_MISMATCH = "OWNER_MISMATCH"
    CONTRACT_REVISION_MISMATCH = "CONTRACT_REVISION_MISMATCH"
    ENGINE_REVISION_MISMATCH = "ENGINE_REVISION_MISMATCH"
    SCHEDULER_REVISION_MISMATCH = "SCHEDULER_REVISION_MISMATCH"
    SCHEDULER_STEP_MISMATCH = "SCHEDULER_STEP_MISMATCH"
    WIRE_VERSION_MISMATCH = "WIRE_VERSION_MISMATCH"
    RESULT_VERSION_MISMATCH = "RESULT_VERSION_MISMATCH"
    TRACE_VERSION_MISMATCH = "TRACE_VERSION_MISMATCH"
    MIXER_REVISION_MISMATCH = "MIXER_REVISION_MISMATCH"
    HOST_IDENTITY_NOT_ATTESTED = "HOST_IDENTITY_NOT_ATTESTED"
    TRUST_NOT_PROVISIONED = "TRUST_NOT_PROVISIONED"


@dataclass(frozen=True, slots=True)
class ClaimedHostFingerprint:
    context: str
    scope: str
    owner: str
    contract_revision: str
    engine_revision: str
    scheduler_revision: str
    scheduler_step_us: int
    scenario_wire_schema_version: int
    result_contract_version: int
    trace_format_version: int
    mixer_revision: str


@dataclass(frozen=True, slots=True)
class HostReferenceAssessment:
    outcome: HostReferenceOutcome
    candidate_policy_sha256: str | None
    wire_schema_version: int | None
    reasons: tuple[HostReferenceReason, ...]
    reference_pin_match: bool
    runtime_authorized: bool = field(default=False, init=False)
    requires_trusted_host_provisioning: bool = field(default=True, init=False)
    requires_full_fsm: bool = field(default=True, init=False)


# A fixed TEST_ONLY comparison vector, never a runtime allowlist or configuration.
_REFERENCE = ClaimedHostFingerprint(
    "PC_SIM", "PC_SIM_ONLY", "SIMULATOR", "G0A1_R11_E2_TEST_REFERENCE_ONLY",
    "G0A1_E2_TEST_ENGINE_ONLY", "G0A1_E2_TEST_SCHEDULER_ONLY", 5000, 2, 2, 1, "G0A1_M0_R11")
_FIELDS = tuple(ClaimedHostFingerprint.__dataclass_fields__)
_MISMATCH_REASONS = tuple(HostReferenceReason)[2:13]
_TRUST_DEFICITS = (HostReferenceReason.HOST_IDENTITY_NOT_ATTESTED,
                   HostReferenceReason.TRUST_NOT_PROVISIONED)
_POLICY_SHA256 = "d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10"


def _closed_mapping(value, expected_type, keys):
    if type(value) is not expected_type:
        raise TypeError("incorrect preflight mapping type")
    # Check size first; do not iterate potentially unbounded caller containers.
    if len(value) != len(keys) or any(key not in value for key in keys):
        raise ValueError("incorrect preflight field set")


def _fixed(value, expected):
    if type(value) is not type(expected):
        raise TypeError("incorrect preflight field type")
    if value != expected:
        raise ValueError("incorrect preflight field value")


def _digest_shape(value):
    if type(value) is not str:
        raise TypeError("digest must be str")
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("invalid digest shape")


def _accepted_shape(preflight):
    _closed_mapping(vars(preflight), dict, ("scenario", "status"))
    _fixed(preflight.status, "ACCEPTED_PREFLIGHT")
    scenario = preflight.scenario
    _closed_mapping(scenario, MappingProxyType, (
        "schema_version", "scenario_id", "context", "provenance", "config_id", "clock", "duration_us", "events"))
    for name, expected in (("schema_version", 2), ("context", "PC_SIM"),
                           ("provenance", "SIM_ONLY"), ("config_id", "sim-only-c0-v1")):
        _fixed(scenario[name], expected)
    clock = scenario["clock"]
    _closed_mapping(clock, MappingProxyType, ("start_us", "step_us"))
    _fixed(clock["start_us"], 0)
    _fixed(clock["step_us"], 5000)
    duration = scenario["duration_us"]
    if type(duration) is not int:
        raise TypeError("duration must be int")
    if not 5000 <= duration <= 60_000_000 or duration % 5000:
        raise ValueError("invalid duration")
    identifier = scenario["scenario_id"]
    if type(identifier) is not str:
        raise TypeError("scenario_id must be str")
    if not 1 <= len(identifier) <= 256 or any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in identifier):
        raise ValueError("invalid scenario_id")
    try:
        if len(identifier.encode("utf-8")) > 256:
            raise ValueError("scenario_id exceeds byte limit")
    except UnicodeEncodeError:
        raise ValueError("invalid scenario_id Unicode") from None
    events = scenario["events"]
    if type(events) is not tuple:
        raise TypeError("events must be frozen tuple")
    if not 1 <= len(events) <= 20_000:
        raise ValueError("invalid event count")
    # Deliberately no event access/scan: TASK-001 owns full semantic validation.


def _rejected_shape(preflight):
    _closed_mapping(vars(preflight), dict, ("diagnostic", "status"))
    _fixed(preflight.status, "VALIDATION_REJECTED")
    diagnostic = preflight.diagnostic
    # TASK-001 genuinely returns a dict here. Read bounded metadata only, never
    # mutate it or mistake this mutable rejection sidecar for a trust credential.
    _closed_mapping(diagnostic, dict, ("diagnostic_format_version", "scope", "run_status",
                                      "evaluated_tick_count", "evidence_complete", "raw_input_sha256", "primary_issue"))
    for name, expected in (("diagnostic_format_version", 1), ("scope", "PC_SIM_ONLY"),
                           ("run_status", "VALIDATION_REJECTED"), ("evaluated_tick_count", 0),
                           ("evidence_complete", False)):
        _fixed(diagnostic[name], expected)
    _digest_shape(diagnostic["raw_input_sha256"])
    issue = diagnostic["primary_issue"]
    _closed_mapping(issue, dict, ("code", "stage", "json_pointer", "frozen_base_error_code"))
    code = issue["code"]
    if type(code) is not str or type(issue["stage"]) is not str or type(issue["json_pointer"]) is not str:
        raise TypeError("invalid diagnostic issue type")
    if len(code) > 64 or code not in STAGES or issue["stage"] != STAGES[code]:
        raise ValueError("invalid diagnostic code/stage")
    pointer = issue["json_pointer"]
    if pointer and not pointer.startswith("/"):
        raise ValueError("invalid diagnostic pointer")
    base = "E_DUPLICATE_EVENT_ID" if code == "P_EVENT_ID_DUPLICATE" else (
        "E_CONTEXT_DENIED" if code in ("P_CONTEXT_DENIED", "P_PROVENANCE_DENIED") else None)
    _fixed(issue["frozen_base_error_code"], base)


def assess_reference_host_boundary(
    preflight: AcceptedPreflight | RejectedPreflight,
    approved_policy_raw_bytes: bytes,
    claimed_host: ClaimedHostFingerprint,
) -> HostReferenceAssessment:
    """Return reference diagnostics only; all branches permanently deny authority."""
    if type(preflight) not in (AcceptedPreflight, RejectedPreflight):
        raise TypeError("expected exact TASK-001 preflight result")
    if type(approved_policy_raw_bytes) is not bytes:
        raise TypeError("policy must be exact immutable bytes")
    if type(claimed_host) is not ClaimedHostFingerprint:
        raise TypeError("expected exact synthetic ClaimedHostFingerprint")
    try:
        for name in _FIELDS:
            expected_type = int if name in ("scheduler_step_us", "scenario_wire_schema_version",
                                            "result_contract_version", "trace_format_version") else str
            if type(getattr(claimed_host, name)) is not expected_type:
                raise TypeError("invalid claimed host field type: " + name)
        if type(preflight) is RejectedPreflight:
            _rejected_shape(preflight)
            return HostReferenceAssessment(HostReferenceOutcome.UPSTREAM_REJECTED, None, None,
                                           (HostReferenceReason.UPSTREAM_REJECTED,) + _TRUST_DEFICITS, False)
        _accepted_shape(preflight)
    except (AttributeError, KeyError):
        raise ValueError("incomplete preflight or host claim") from None
    digest = sha256(approved_policy_raw_bytes).hexdigest()
    reasons = []
    if digest != _POLICY_SHA256:
        reasons.append(HostReferenceReason.POLICY_BYTES_MISMATCH)
    for name, reason in zip(_FIELDS, _MISMATCH_REASONS):
        if getattr(claimed_host, name) != getattr(_REFERENCE, name):
            reasons.append(reason)
    match = not reasons
    outcome = (HostReferenceOutcome.REFERENCE_MATCH_NO_AUTHORITY if match
               else HostReferenceOutcome.REFERENCE_MISMATCH)
    return HostReferenceAssessment(outcome, digest, preflight.scenario["schema_version"],
                                   tuple(reasons) + _TRUST_DEFICITS, match)
