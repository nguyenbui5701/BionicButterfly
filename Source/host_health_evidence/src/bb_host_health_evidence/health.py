"""Stage D1 diagnostic evidence only; no health verdict or control authority."""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType

from bb_host_batch_observations import NormalizedTickObservations, ValidControlGroup
from bb_host_temporal_guard_facts import TemporalGuardFacts
from bb_host_safety_priority_kernel import SafetyPriorityAssessment, SafetyState


class RFStatus(str, Enum):
    HEALTHY = "HEALTHY"
    LOST = "LOST"
    UNKNOWN = "UNKNOWN"


class RFEvidenceKind(str, Enum):
    MISSING = "MISSING"
    STALE_PRIOR = "STALE_PRIOR"
    HEALTHY_CURRENT = "HEALTHY_CURRENT"
    HEALTHY_CARRIED = "HEALTHY_CARRIED"
    LOST_CURRENT = "LOST_CURRENT"
    LOST_CARRIED = "LOST_CARRIED"
    UNKNOWN_CURRENT = "UNKNOWN_CURRENT"
    UNKNOWN_CARRIED = "UNKNOWN_CARRIED"
    AMBIGUOUS_CURRENT = "AMBIGUOUS_CURRENT"


class ControlEvidenceKind(str, Enum):
    ABSENT = "ABSENT"
    SINGLE_CANDIDATE = "SINGLE_CANDIDATE"
    INVALID = "INVALID"
    CONFLICT = "CONFLICT"
    INVALID_AND_CONFLICT = "INVALID_AND_CONFLICT"
    BLOCKED_RF = "BLOCKED_RF"
    BLOCKED_PRIORITY = "BLOCKED_PRIORITY"
    DEFER_RF_AMBIGUOUS = "DEFER_RF_AMBIGUOUS"


@dataclass(frozen=True, slots=True)
class PriorCommittedRFStatus:
    """Separate TEST_ONLY snapshot at D1. Construction does not authenticate it."""

    last_committed_eval_at_us: int | None
    last_rf_status: RFStatus | None
    last_rf_original_at_us: int | None


@dataclass(frozen=True, slots=True)
class HealthEvidenceFacts:
    tick_index: int
    eval_at_us: int
    pre_state: SafetyState
    rf_evidence: RFEvidenceKind
    latest_current_rf_original_at_us: int | None
    control_evidence: ControlEvidenceKind
    observed_control_candidate_original_at_us: int | None
    requires_full_fsm: bool


_ARMED = (SafetyState.ARM_CHECK, SafetyState.ARMED_IDLE, SafetyState.ACTUATION_ACTIVE)
_RESTRICTED = (SafetyState.CONTINGENCY, SafetyState.FAULT_LATCHED)
_FLAGS = ("has_invalid_control", "has_distinct_valid_control_conflict", "has_duplicate_semantic_control",
          "rf_has_healthy", "rf_has_lost", "rf_has_unknown", "has_boot", "has_reset", "has_ack", "has_catastrophe")


def _require(condition):
    if not condition:
        raise ValueError("inconsistent upstream facts or synthetic prior RF snapshot")


def _time(value, maximum):
    _require(type(value) is int and 0 <= value <= maximum)


def _original(value, tick):
    _time(value, tick)
    _require(tick > 0 and tick - 5000 < value)


def _validate_fixed(obs, temporal, priority, prior):
    for value, cls in ((obs, NormalizedTickObservations), (temporal, TemporalGuardFacts),
                       (priority, SafetyPriorityAssessment), (prior, PriorCommittedRFStatus)):
        if type(value) is not cls:
            raise TypeError("expected exact upstream and prior RF record types")
    if type(priority.pre_state) is not SafetyState:
        raise TypeError("expected exact SafetyState")
    tick = obs.eval_at_us
    for record in (obs, temporal, priority):
        _time(record.tick_index, 12000)
        _time(record.eval_at_us, 60000000)
        _require(record.eval_at_us == record.tick_index * 5000 and record.eval_at_us == tick)
    for name in ("source_events", "causal_event_ids", "valid_control_groups", "invalid_control_event_ids", "rf_events"):
        _require(type(getattr(obs, name)) is tuple)
    for name in _FLAGS:
        _require(type(getattr(obs, name)) is bool)
    for left, right in (("rf_has_lost", "has_rf_lost_observation"), ("rf_has_unknown", "has_rf_unknown_observation"),
                        ("has_invalid_control", "has_invalid_control_observation"),
                        ("has_distinct_valid_control_conflict", "has_valid_control_conflict")):
        _require(type(getattr(temporal, right)) is bool and getattr(obs, left) == getattr(temporal, right))
    for channel in ("control", "rf"):
        age = getattr(temporal, f"prior_{channel}_age_us")
        within = getattr(temporal, f"prior_{channel}_within_timeout")
        if age is not None:
            _time(age, tick)
            _require(age >= 5000)
        _require(type(within) is bool and within == (age is not None and age <= 200000))
    for name in ("observed_uncontested_valid_control_at_us", "observed_uncontested_healthy_rf_at_us"):
        value = getattr(temporal, name)
        if value is not None:
            _original(value, tick)
    _require(obs.has_boot == (tick == 0) and (priority.pre_state is SafetyState.BOOT) == (tick == 0))
    if tick == 0:
        _require(not any(getattr(obs, name) for name in _FLAGS if name != "has_boot"))
        _require(len(obs.source_events) == len(obs.causal_event_ids) == 1)
        _require(not obs.rf_events and not obs.valid_control_groups and not obs.invalid_control_event_ids)
    commit, status, at = prior.last_committed_eval_at_us, prior.last_rf_status, prior.last_rf_original_at_us
    if tick == 0:
        _require(commit is None and status is None and at is None)
    else:
        _time(commit, tick - 1)
        _require(commit % 5000 == 0)
    _require((status is None) == (at is None))
    if status is not None:
        if type(status) is not RFStatus:
            raise TypeError("expected exact RFStatus enum")
        _time(at, commit)
    if status is RFStatus.HEALTHY:
        _require(temporal.prior_rf_age_us is not None and at == tick - temporal.prior_rf_age_us)
    elif status is None:
        _require(temporal.prior_rf_age_us is None)

    groups = obs.valid_control_groups
    _require(obs.has_distinct_valid_control_conflict == (len(groups) > 1))
    _require(obs.has_invalid_control == bool(obs.invalid_control_event_ids))
    candidate = temporal.observed_uncontested_valid_control_at_us
    _require((candidate is not None) == (len(groups) == 1 and not obs.has_invalid_control))
    if len(groups) == 1:
        group = groups[0]
        _require(type(group) is ValidControlGroup and type(group.semantic_control) is MappingProxyType)
        _require(type(group.member_events) is tuple and bool(group.member_events))
        _require(type(group.event_ids) is tuple and bool(group.event_ids))
        _original(group.latest_original_at_us, tick)
        _require(obs.has_duplicate_semantic_control == (len(group.event_ids) > 1))
        if candidate is not None:
            _require(candidate == group.latest_original_at_us)
    elif not groups:
        _require(not obs.has_duplicate_semantic_control)
    # Group bodies and members belong to TASK-003; no control-event rescan here.
    _validate_priority(obs, temporal, priority)


def _validate_priority(obs, temporal, priority):
    """Check the fixed C1 contract, without calling/rerunning its adjudicator."""
    state = priority.pre_state
    expected_next = category = None
    if state is SafetyState.FAULT_LATCHED:
        expected_next, category = SafetyState.FAULT_LATCHED, "LATCH_PERSISTS"
    elif obs.has_catastrophe:
        expected_next, category = SafetyState.FAULT_LATCHED, "CATASTROPHIC_FAULT"
    elif state is SafetyState.CONTINGENCY:
        expected_next, category = SafetyState.CONTINGENCY, "CONTINGENCY_HOLD"
    elif state in _ARMED and (obs.has_invalid_control or obs.has_distinct_valid_control_conflict
                              or obs.rf_has_lost or (obs.rf_has_unknown and not obs.rf_has_healthy)):
        expected_next, category = SafetyState.CONTINGENCY, "ARMED_OBSERVED_HAZARD"
    elif obs.has_reset:
        expected_next, category = SafetyState.SELF_TEST, "ORDINARY_RESET"
    elif state is SafetyState.BOOT:
        expected_next, category = SafetyState.SELF_TEST, "BOOT_INITIALIZATION"
    _require(priority.provisional_next_state is expected_next)
    _require(type(priority.priority_category) is type(category) and priority.priority_category == category)
    blocked = (obs.has_catastrophe or obs.has_reset or obs.has_invalid_control or obs.has_distinct_valid_control_conflict
               or obs.rf_has_lost or obs.rf_has_unknown or state in _RESTRICTED
               or expected_next in (SafetyState.SELF_TEST, *_RESTRICTED)
               or (state in _ARMED and (not temporal.prior_control_within_timeout or not temporal.prior_rf_within_timeout)))
    _require(type(priority.blocks_control_qualification) is bool and priority.blocks_control_qualification == blocked)
    _require(priority.requires_full_fsm is True)


def _rf_evidence(obs, temporal, prior):
    healthy = lost = unknown = False
    latest = None
    for event in obs.rf_events:
        _require(type(event) is MappingProxyType and len(event) == 4)
        _require(set(event) == {"event_id", "event_at_us", "type", "payload"})
        _require(type(event["event_id"]) is str and bool(event["event_id"]))
        _require(type(event["type"]) is str and event["type"] == "SIM_RF_STATUS")
        at, body = event["event_at_us"], event["payload"]
        _original(at, obs.eval_at_us)
        _require(type(body) is MappingProxyType and len(body) == 2)
        _require(set(body) == {"rf_health", "rf_provenance"})
        status = body["rf_health"]
        _require(type(status) is str and status in ("HEALTHY", "LOST", "UNKNOWN"))
        _require(type(body["rf_provenance"]) is str and body["rf_provenance"] == "INJECTED_SIM")
        healthy |= status == "HEALTHY"
        lost |= status == "LOST"
        unknown |= status == "UNKNOWN"
        latest = at if latest is None else max(latest, at)
    _require((healthy, lost, unknown) == (obs.rf_has_healthy, obs.rf_has_lost, obs.rf_has_unknown))
    _require(temporal.observed_uncontested_healthy_rf_at_us == (latest if healthy and not lost and not unknown else None))
    if lost:
        kind = RFEvidenceKind.LOST_CURRENT
    elif healthy and unknown:
        kind = RFEvidenceKind.AMBIGUOUS_CURRENT
    elif unknown:
        kind = RFEvidenceKind.UNKNOWN_CURRENT
    elif healthy:
        kind = RFEvidenceKind.HEALTHY_CURRENT
    elif prior.last_rf_status is RFStatus.HEALTHY:
        kind = RFEvidenceKind.HEALTHY_CARRIED if temporal.prior_rf_within_timeout else RFEvidenceKind.STALE_PRIOR
    elif prior.last_rf_status is RFStatus.LOST:
        kind = RFEvidenceKind.LOST_CARRIED
    elif prior.last_rf_status is RFStatus.UNKNOWN:
        kind = RFEvidenceKind.UNKNOWN_CARRIED
    else:
        kind = RFEvidenceKind.MISSING
    return kind, latest


def assess_health_evidence(observations: NormalizedTickObservations, temporal: TemporalGuardFacts,
                           priority: SafetyPriorityAssessment, prior_rf: PriorCommittedRFStatus) -> HealthEvidenceFacts:
    """Classify diagnostics in O(N_RF) time and constant extra memory.

    Inputs must be genuine upstream records plus a separate TEST_ONLY prior.
    Shape checks do not authenticate forged wrappers or prove committed history.
    No control is accepted; no history is updated, including on current HEALTHY.
    """
    _validate_fixed(observations, temporal, priority, prior_rf)
    rf, latest = _rf_evidence(observations, temporal, prior_rf)
    candidate = temporal.observed_uncontested_valid_control_at_us
    if observations.has_invalid_control and observations.has_distinct_valid_control_conflict:
        control = ControlEvidenceKind.INVALID_AND_CONFLICT
    elif observations.has_invalid_control:
        control = ControlEvidenceKind.INVALID
    elif observations.has_distinct_valid_control_conflict:
        control = ControlEvidenceKind.CONFLICT
    elif candidate is None:
        control = ControlEvidenceKind.ABSENT
    elif observations.has_reset or observations.has_catastrophe or priority.pre_state in _RESTRICTED:
        control = ControlEvidenceKind.BLOCKED_PRIORITY
    elif rf is RFEvidenceKind.AMBIGUOUS_CURRENT:
        control = ControlEvidenceKind.DEFER_RF_AMBIGUOUS
    elif rf not in (RFEvidenceKind.HEALTHY_CURRENT, RFEvidenceKind.HEALTHY_CARRIED):
        control = ControlEvidenceKind.BLOCKED_RF
    elif priority.blocks_control_qualification:
        control = ControlEvidenceKind.BLOCKED_PRIORITY
    else:
        control = ControlEvidenceKind.SINGLE_CANDIDATE
    return HealthEvidenceFacts(observations.tick_index, observations.eval_at_us, priority.pre_state,
                               rf, latest, control, candidate, True)
