"""D2 diagnostic triage over fixed upstream metadata; no admission authority."""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType

from bb_host_batch_observations import NormalizedTickObservations
from bb_host_temporal_guard_facts import TemporalGuardFacts
from bb_host_safety_priority_kernel import SafetyPriorityAssessment, SafetyState
from bb_host_health_evidence import HealthEvidenceFacts, RFEvidenceKind, ControlEvidenceKind


class RFGuardLane(str, Enum):
    CURRENT_HEALTHY_UNCOMMITTED = "CURRENT_HEALTHY_UNCOMMITTED"
    CARRIED_HEALTHY_UNVERIFIED = "CARRIED_HEALTHY_UNVERIFIED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_HEALTHY = "NOT_HEALTHY"


class ControlGuardLane(str, Enum):
    NO_CANDIDATE = "NO_CANDIDATE"
    UNTRUSTED_CANDIDATE = "UNTRUSTED_CANDIDATE"
    INVALID_OR_CONFLICT = "INVALID_OR_CONFLICT"
    RF_BLOCKED = "RF_BLOCKED"
    RF_AMBIGUOUS = "RF_AMBIGUOUS"
    PRIORITY_BLOCKED = "PRIORITY_BLOCKED"


class ArmedContinuityLane(str, Enum):
    NOT_ARMED = "NOT_ARMED"
    PRIOR_STALE_OR_MISSING = "PRIOR_STALE_OR_MISSING"
    HAZARD_OR_UNRESOLVED = "HAZARD_OR_UNRESOLVED"
    POTENTIAL_S1_UNVERIFIED = "POTENTIAL_S1_UNVERIFIED"


class GuardReason(str, Enum):
    PRIORITY_BLOCKED = "PRIORITY_BLOCKED"
    RF_AMBIGUOUS = "RF_AMBIGUOUS"
    RF_NOT_HEALTHY = "RF_NOT_HEALTHY"
    CONTROL_INVALID = "CONTROL_INVALID"
    CONTROL_CONFLICT = "CONTROL_CONFLICT"
    NO_UNCONTESTED_CONTROL = "NO_UNCONTESTED_CONTROL"
    ARMED_PRIOR_RF_STALE_OR_MISSING = "ARMED_PRIOR_RF_STALE_OR_MISSING"
    ARMED_PRIOR_CONTROL_STALE_OR_MISSING = "ARMED_PRIOR_CONTROL_STALE_OR_MISSING"
    TRUST_NOT_PROVEN = "TRUST_NOT_PROVEN"


@dataclass(frozen=True, slots=True)
class GuardTriageFacts:
    tick_index: int
    eval_at_us: int
    pre_state: SafetyState
    rf_lane: RFGuardLane
    control_lane: ControlGuardLane
    armed_continuity_lane: ArmedContinuityLane
    current_rf_candidate_original_at_us: int | None
    current_control_candidate_original_at_us: int | None
    unresolved_reasons: tuple[GuardReason, ...]
    requires_full_fsm: bool


_ARMED = (SafetyState.ARM_CHECK, SafetyState.ARMED_IDLE, SafetyState.ACTUATION_ACTIVE)
_RESTRICTED = (SafetyState.CONTINGENCY, SafetyState.FAULT_LATCHED)
_BLOCKING_NEXT = (SafetyState.SELF_TEST, *_RESTRICTED)
_FLAGS = ("has_invalid_control", "has_distinct_valid_control_conflict", "has_duplicate_semantic_control",
          "rf_has_healthy", "rf_has_lost", "rf_has_unknown", "has_boot", "has_reset", "has_ack", "has_catastrophe")
_HEALTHY = (RFEvidenceKind.HEALTHY_CURRENT, RFEvidenceKind.HEALTHY_CARRIED)
_RF_LANES = MappingProxyType({
    RFEvidenceKind.HEALTHY_CURRENT: RFGuardLane.CURRENT_HEALTHY_UNCOMMITTED,
    RFEvidenceKind.HEALTHY_CARRIED: RFGuardLane.CARRIED_HEALTHY_UNVERIFIED,
    RFEvidenceKind.AMBIGUOUS_CURRENT: RFGuardLane.AMBIGUOUS,
    RFEvidenceKind.MISSING: RFGuardLane.NOT_HEALTHY,
    RFEvidenceKind.STALE_PRIOR: RFGuardLane.NOT_HEALTHY,
    RFEvidenceKind.LOST_CURRENT: RFGuardLane.NOT_HEALTHY,
    RFEvidenceKind.LOST_CARRIED: RFGuardLane.NOT_HEALTHY,
    RFEvidenceKind.UNKNOWN_CURRENT: RFGuardLane.NOT_HEALTHY,
    RFEvidenceKind.UNKNOWN_CARRIED: RFGuardLane.NOT_HEALTHY,
})
_CONTROL_LANES = MappingProxyType({
    ControlEvidenceKind.ABSENT: ControlGuardLane.NO_CANDIDATE,
    ControlEvidenceKind.SINGLE_CANDIDATE: ControlGuardLane.UNTRUSTED_CANDIDATE,
    ControlEvidenceKind.INVALID: ControlGuardLane.INVALID_OR_CONFLICT,
    ControlEvidenceKind.CONFLICT: ControlGuardLane.INVALID_OR_CONFLICT,
    ControlEvidenceKind.INVALID_AND_CONFLICT: ControlGuardLane.INVALID_OR_CONFLICT,
    ControlEvidenceKind.BLOCKED_RF: ControlGuardLane.RF_BLOCKED,
    ControlEvidenceKind.DEFER_RF_AMBIGUOUS: ControlGuardLane.RF_AMBIGUOUS,
    ControlEvidenceKind.BLOCKED_PRIORITY: ControlGuardLane.PRIORITY_BLOCKED,
})


def _require(condition):
    if not condition:
        raise ValueError("inconsistent upstream guard evidence")


def _optional_current(value, tick):
    _require(value is None or (type(value) is int and tick > 0 and tick - 5000 < value <= tick))


def _validate_metadata(obs, temporal, priority, health):
    for value, cls in ((obs, NormalizedTickObservations), (temporal, TemporalGuardFacts),
                       (priority, SafetyPriorityAssessment), (health, HealthEvidenceFacts)):
        if type(value) is not cls:
            raise TypeError("expected exact TASK-003/004/005/007 records")
    for value, cls in ((priority.pre_state, SafetyState), (health.pre_state, SafetyState),
                       (health.rf_evidence, RFEvidenceKind), (health.control_evidence, ControlEvidenceKind)):
        if type(value) is not cls:
            raise TypeError("expected exact upstream enum types")
    tick = obs.eval_at_us
    for record in (obs, temporal, priority, health):
        _require(type(record.tick_index) is int and 0 <= record.tick_index <= 12000)
        _require(type(record.eval_at_us) is int and record.eval_at_us == record.tick_index * 5000)
        _require(record.eval_at_us == tick)
    _require(priority.pre_state is health.pre_state)
    _require(priority.requires_full_fsm is True and health.requires_full_fsm is True)
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
        _require(age is None or (type(age) is int and 5000 <= age <= tick))
        _require(type(within) is bool and within == (age is not None and age <= 200000))
    for value in (temporal.observed_uncontested_healthy_rf_at_us, temporal.observed_uncontested_valid_control_at_us,
                  health.latest_current_rf_original_at_us, health.observed_control_candidate_original_at_us):
        _optional_current(value, tick)
    _require(health.observed_control_candidate_original_at_us == temporal.observed_uncontested_valid_control_at_us)
    _require(obs.has_boot == (tick == 0) and (priority.pre_state is SafetyState.BOOT) == (tick == 0))
    _require(obs.has_distinct_valid_control_conflict == (len(obs.valid_control_groups) > 1))
    _require(obs.has_invalid_control == bool(obs.invalid_control_event_ids))
    _require(not obs.has_duplicate_semantic_control or bool(obs.valid_control_groups))
    uncontested = len(obs.valid_control_groups) == 1 and not obs.has_invalid_control
    _require((temporal.observed_uncontested_valid_control_at_us is not None) == uncontested)
    _require(bool(obs.rf_events) == (obs.rf_has_healthy or obs.rf_has_lost or obs.rf_has_unknown))
    _require((health.latest_current_rf_original_at_us is not None) == bool(obs.rf_events))
    if tick == 0:
        _require(not any(getattr(obs, name) for name in _FLAGS if name != "has_boot"))
        _require(len(obs.source_events) == len(obs.causal_event_ids) == 1)
        _require(not obs.rf_events and not obs.valid_control_groups and not obs.invalid_control_event_ids)
        _require(health.rf_evidence is RFEvidenceKind.MISSING)


def _validate_priority(obs, temporal, priority):
    """Fixed C1 consistency check, never invoking the upstream adjudicator."""
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
               or obs.rf_has_lost or obs.rf_has_unknown or state in _RESTRICTED or expected_next in _BLOCKING_NEXT
               or (state in _ARMED and (not temporal.prior_control_within_timeout or not temporal.prior_rf_within_timeout)))
    _require(type(priority.blocks_control_qualification) is bool and priority.blocks_control_qualification == blocked)


def _validate_health(obs, temporal, priority, health):
    """Cross-check D1 labels against metadata, never read nested events/groups.

    Carried LOST/UNKNOWN provenance cannot be recovered from these records.
    D1 owns that synthetic snapshot pairing; D2 cannot authenticate it.
    """
    rf = health.rf_evidence
    has_rf = bool(obs.rf_events)
    all_healthy = obs.rf_has_healthy and not obs.rf_has_lost and not obs.rf_has_unknown
    ambiguous = obs.rf_has_healthy and obs.rf_has_unknown and not obs.rf_has_lost
    _require((temporal.observed_uncontested_healthy_rf_at_us is not None) == all_healthy)
    _require(rf is not RFEvidenceKind.HEALTHY_CURRENT or all_healthy)
    _require(not all_healthy or rf is RFEvidenceKind.HEALTHY_CURRENT)
    _require(not all_healthy or health.latest_current_rf_original_at_us == temporal.observed_uncontested_healthy_rf_at_us)
    _require(rf is not RFEvidenceKind.LOST_CURRENT or obs.rf_has_lost)
    _require(not obs.rf_has_lost or rf is RFEvidenceKind.LOST_CURRENT)
    _require((rf is RFEvidenceKind.AMBIGUOUS_CURRENT) == ambiguous)
    _require((rf is RFEvidenceKind.UNKNOWN_CURRENT) == (obs.rf_has_unknown and not obs.rf_has_healthy and not obs.rf_has_lost))
    _require(rf is not RFEvidenceKind.HEALTHY_CARRIED or (not has_rf and temporal.prior_rf_within_timeout))
    _require(rf is not RFEvidenceKind.STALE_PRIOR or (not has_rf and temporal.prior_rf_age_us is not None and not temporal.prior_rf_within_timeout))
    _require(rf is not RFEvidenceKind.MISSING or (not has_rf and temporal.prior_rf_age_us is None))
    _require(rf not in (RFEvidenceKind.LOST_CARRIED, RFEvidenceKind.UNKNOWN_CARRIED) or not has_rf)

    ce = health.control_evidence
    invalid, conflict = obs.has_invalid_control, obs.has_distinct_valid_control_conflict
    clean = not invalid and not conflict
    candidate = temporal.observed_uncontested_valid_control_at_us is not None
    restricted = obs.has_reset or obs.has_catastrophe or priority.pre_state in _RESTRICTED
    healthy = rf in _HEALTHY
    # Every implication is checked: a forged negative label is also contradictory.
    _require((ce is ControlEvidenceKind.INVALID_AND_CONFLICT) == (invalid and conflict))
    _require((ce is ControlEvidenceKind.INVALID) == (invalid and not conflict))
    _require((ce is ControlEvidenceKind.CONFLICT) == (conflict and not invalid))
    _require((ce is ControlEvidenceKind.ABSENT) == (clean and not candidate))
    _require((ce is ControlEvidenceKind.SINGLE_CANDIDATE) == (clean and candidate and healthy and not priority.blocks_control_qualification))
    _require((ce is ControlEvidenceKind.DEFER_RF_AMBIGUOUS) == (clean and candidate and not restricted and ambiguous))
    _require((ce is ControlEvidenceKind.BLOCKED_RF) == (clean and candidate and not restricted and not ambiguous and not healthy))
    _require((ce is ControlEvidenceKind.BLOCKED_PRIORITY) == (clean and candidate and (restricted or (healthy and priority.blocks_control_qualification))))


def triage_guard_evidence(observations: NormalizedTickObservations, temporal: TemporalGuardFacts,
                          priority: SafetyPriorityAssessment, health: HealthEvidenceFacts) -> GuardTriageFacts:
    """Return ten immutable diagnostic fields, in O(1) time/space after D1.

    A matching Python wrapper is not authenticated history. Even favorable
    evidence retains TRUST_NOT_PROVEN; no candidate/intent/state is committed.
    """
    _validate_metadata(observations, temporal, priority, health)
    _validate_priority(observations, temporal, priority)
    _validate_health(observations, temporal, priority, health)
    rf_lane, control_lane = _RF_LANES[health.rf_evidence], _CONTROL_LANES[health.control_evidence]
    armed = priority.pre_state in _ARMED
    stale = not temporal.prior_rf_within_timeout or not temporal.prior_control_within_timeout
    priority_risk = observations.has_reset or observations.has_catastrophe or priority.pre_state in _RESTRICTED or priority.provisional_next_state in _BLOCKING_NEXT
    hazard = rf_lane in (RFGuardLane.NOT_HEALTHY, RFGuardLane.AMBIGUOUS) or priority.blocks_control_qualification or priority_risk
    continuity = (ArmedContinuityLane.NOT_ARMED if not armed else ArmedContinuityLane.PRIOR_STALE_OR_MISSING if stale
                  else ArmedContinuityLane.HAZARD_OR_UNRESOLVED if hazard else ArmedContinuityLane.POTENTIAL_S1_UNVERIFIED)
    flags = (priority_risk, rf_lane is RFGuardLane.AMBIGUOUS, rf_lane is RFGuardLane.NOT_HEALTHY,
             observations.has_invalid_control, observations.has_distinct_valid_control_conflict,
             temporal.observed_uncontested_valid_control_at_us is None,
             armed and not temporal.prior_rf_within_timeout, armed and not temporal.prior_control_within_timeout, True)
    reasons = tuple(reason for reason, present in zip(GuardReason, flags) if present)
    return GuardTriageFacts(observations.tick_index, observations.eval_at_us, priority.pre_state,
                            rf_lane, control_lane, continuity, temporal.observed_uncontested_healthy_rf_at_us,
                            temporal.observed_uncontested_valid_control_at_us, reasons, True)
