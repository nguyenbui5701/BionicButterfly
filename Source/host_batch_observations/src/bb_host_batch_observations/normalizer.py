"""Classify every scheduled observation; never choose an accepted intent."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from types import MappingProxyType

from bb_host_virtual_ticks import VirtualTickBatch


@dataclass(frozen=True, slots=True)
class ValidControlGroup:
    semantic_control: Mapping
    member_events: tuple[Mapping, ...]
    event_ids: tuple[str, ...]
    latest_original_at_us: int


@dataclass(frozen=True, slots=True)
class NormalizedTickObservations:
    tick_index: int
    eval_at_us: int
    source_events: tuple[Mapping, ...]
    causal_event_ids: tuple[str, ...]
    valid_control_groups: tuple[ValidControlGroup, ...]
    invalid_control_event_ids: tuple[str, ...]
    has_invalid_control: bool
    has_distinct_valid_control_conflict: bool
    has_duplicate_semantic_control: bool
    rf_events: tuple[Mapping, ...]
    rf_has_healthy: bool
    rf_has_lost: bool
    rf_has_unknown: bool
    has_boot: bool
    has_reset: bool
    has_ack: bool
    has_catastrophe: bool


@dataclass(slots=True)
class _Group:
    body: Mapping
    latest: int
    members: list = field(default_factory=list)
    ids: list = field(default_factory=list)


def _require(condition: bool):
    if not condition:
        raise ValueError("expected an immutable batch from preflight and scheduler")


def _sorted_ids(ids) -> tuple[str, ...]:
    return tuple(sorted(ids, key=lambda value: value.encode("utf-8")))


def _inspect_event(event):
    """Guard the immutable API shape, not a second wire parser/schema pass."""
    _require(type(event) is MappingProxyType)
    _require(set(event) == {"event_id", "event_at_us", "type", "payload"})
    identity, at, kind, body = event["event_id"], event["event_at_us"], event["type"], event["payload"]
    _require(type(identity) is str and bool(identity) and type(at) is int)
    _require(type(kind) is str and type(body) is MappingProxyType)
    return identity, at, kind, body


def _control_key(body):
    _require(set(body) == {"uart_frame_status", "arm_switch", "flap_demand", "steering_demand", "map_revision"})
    _require(type(body["arm_switch"]) is bool and type(body["map_revision"]) is str)
    for name in ("flap_demand", "steering_demand"):
        value = body[name]
        _require(type(value) is int or (type(value) is Decimal and value.is_finite()))
    # int and Decimal have exact cross-type equality/hash, including zero.
    return body["arm_switch"], body["flap_demand"], body["steering_demand"], body["map_revision"]


def normalize_tick_observations(batch: VirtualTickBatch) -> NormalizedTickObservations:
    """Return immutable facts about one genuine TASK-002 batch, without effects.

    Wrong types fail synchronously with TypeError, malformed boundary objects
    with ValueError. These checks confer no trust and do not replace preflight.
    Classification visits each event once; metadata ID sorting is separate.
    """
    if type(batch) is not VirtualTickBatch:
        raise TypeError("expected TASK-002 VirtualTickBatch")
    _require(type(batch.tick_index) is int and 0 <= batch.tick_index <= 12000)
    _require(type(batch.eval_at_us) is int and batch.eval_at_us == batch.tick_index * 5000)
    _require(type(batch.events) is tuple and len(batch.events) <= 20000)
    ids, invalid_ids, rf_events = [], [], []
    seen, rf_statuses, lifecycle = set(), set(), set()
    groups = {}
    previous_at = -1
    for event in batch.events:
        identity, at, kind, body = _inspect_event(event)
        _require(identity not in seen)
        _require(at >= previous_at and (at == 0 if batch.tick_index == 0 else batch.eval_at_us - 5000 < at <= batch.eval_at_us))
        previous_at = at
        seen.add(identity)
        ids.append(identity)
        if kind == "SIM_CONTROL_FRAME":
            status = body.get("uart_frame_status")
            _require(type(status) is str)
            if status == "VALID":
                key = _control_key(body)
                if key not in groups:
                    groups[key] = _Group(body, at)
                group = groups[key]
                group.members.append(event)
                group.ids.append(identity)
                group.latest = max(group.latest, at)
            else:
                _require(status == "INVALID" and set(body) == {"uart_frame_status"})
                invalid_ids.append(identity)
        elif kind == "SIM_RF_STATUS":
            _require(set(body) == {"rf_health", "rf_provenance"})
            _require(type(body["rf_health"]) is str and body["rf_health"] in ("HEALTHY", "LOST", "UNKNOWN"))
            _require(type(body["rf_provenance"]) is str)
            rf_events.append(event)
            rf_statuses.add(body["rf_health"])
        else:
            _require(kind in ("BOOT", "SIM_RESET", "SIM_ACK_FAULT", "SIM_CATASTROPHIC_FAULT") and not body)
            lifecycle.add(kind)
    frozen_groups = tuple(ValidControlGroup(group.body, tuple(group.members), _sorted_ids(group.ids), group.latest)
                          for group in groups.values())
    return NormalizedTickObservations(
        tick_index=batch.tick_index, eval_at_us=batch.eval_at_us,
        source_events=batch.events, causal_event_ids=_sorted_ids(ids), valid_control_groups=frozen_groups,
        invalid_control_event_ids=_sorted_ids(invalid_ids), has_invalid_control=bool(invalid_ids),
        has_distinct_valid_control_conflict=len(frozen_groups) > 1,
        has_duplicate_semantic_control=any(len(group.event_ids) > 1 for group in frozen_groups),
        rf_events=tuple(rf_events), rf_has_healthy="HEALTHY" in rf_statuses,
        rf_has_lost="LOST" in rf_statuses, rf_has_unknown="UNKNOWN" in rf_statuses,
        has_boot="BOOT" in lifecycle, has_reset="SIM_RESET" in lifecycle,
        has_ack="SIM_ACK_FAULT" in lifecycle, has_catastrophe="SIM_CATASTROPHIC_FAULT" in lifecycle,
    )
