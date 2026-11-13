"""Design/167 A-to-G priority constraints over validated full-tick facts."""

from dataclasses import dataclass
from enum import Enum

from bb_host_batch_observations import NormalizedTickObservations
from bb_host_temporal_guard_facts import TemporalGuardFacts


class SafetyState(str, Enum):
    BOOT = "BOOT"
    SELF_TEST = "SELF_TEST"
    DISARMED = "DISARMED"
    ARM_CHECK = "ARM_CHECK"
    ARMED_IDLE = "ARMED_IDLE"
    ACTUATION_ACTIVE = "ACTUATION_ACTIVE"
    CONTINGENCY = "CONTINGENCY"
    FAULT_LATCHED = "FAULT_LATCHED"


@dataclass(frozen=True, slots=True)
class SafetyPriorityAssessment:
    tick_index: int
    eval_at_us: int
    pre_state: SafetyState
    provisional_next_state: SafetyState | None
    priority_category: str | None
    blocks_control_qualification: bool
    requires_full_fsm: bool


_ARMED = frozenset((SafetyState.ARM_CHECK, SafetyState.ARMED_IDLE, SafetyState.ACTUATION_ACTIVE))
_RESTRICTED = frozenset((SafetyState.CONTINGENCY, SafetyState.FAULT_LATCHED))
_BLOCKING_NEXT = _RESTRICTED | frozenset((SafetyState.SELF_TEST,))
_OBS_FLAGS = ("has_invalid_control", "has_distinct_valid_control_conflict", "has_duplicate_semantic_control",
              "rf_has_healthy", "rf_has_lost", "rf_has_unknown", "has_boot", "has_reset", "has_ack", "has_catastrophe")
_MIRRORS = (("rf_has_lost", "has_rf_lost_observation"), ("rf_has_unknown", "has_rf_unknown_observation"),
            ("has_invalid_control", "has_invalid_control_observation"),
            ("has_distinct_valid_control_conflict", "has_valid_control_conflict"))


def _require(condition):
    if not condition:
        raise ValueError("expected matching immutable upstream tick facts and a valid pre-state")


def _validate(pre_state, observations, temporal):
    if type(pre_state) is not SafetyState:
        raise TypeError("expected exact SafetyState enum")
    if type(observations) is not NormalizedTickObservations:
        raise TypeError("expected exact TASK-003 NormalizedTickObservations")
    if type(temporal) is not TemporalGuardFacts:
        raise TypeError("expected exact TASK-004 TemporalGuardFacts")
    for record in (observations, temporal):
        _require(type(record.tick_index) is int and 0 <= record.tick_index <= 12000)
        _require(type(record.eval_at_us) is int and record.eval_at_us == record.tick_index * 5000)
    _require(observations.tick_index == temporal.tick_index and observations.eval_at_us == temporal.eval_at_us)
    for name in _OBS_FLAGS:
        _require(type(getattr(observations, name)) is bool)
    for obs_name, temporal_name in _MIRRORS:
        _require(type(getattr(temporal, temporal_name)) is bool)
        _require(getattr(observations, obs_name) == getattr(temporal, temporal_name))
    # O(1) outer-shape checks only. The real normalizer owns event/group contents.
    for name in ("source_events", "causal_event_ids", "valid_control_groups", "invalid_control_event_ids", "rf_events"):
        _require(type(getattr(observations, name)) is tuple)
    _require(observations.has_distinct_valid_control_conflict == (len(observations.valid_control_groups) > 1))
    _require(observations.has_invalid_control == bool(observations.invalid_control_event_ids))
    for channel in ("control", "rf"):
        age = getattr(temporal, f"prior_{channel}_age_us")
        within = getattr(temporal, f"prior_{channel}_within_timeout")
        _require(age is None or (type(age) is int and 0 <= age <= temporal.eval_at_us))
        _require(type(within) is bool and within == (age is not None and age <= 200000))
    for name in ("observed_uncontested_valid_control_at_us", "observed_uncontested_healthy_rf_at_us"):
        candidate = getattr(temporal, name)
        _require(candidate is None or (type(candidate) is int and
                 max(0, temporal.eval_at_us - 5000) < candidate <= temporal.eval_at_us))
    if observations.tick_index == 0:
        _require(pre_state is SafetyState.BOOT and observations.has_boot)
        _require(not any(getattr(observations, name) for name in _OBS_FLAGS if name != "has_boot"))
        _require(len(observations.source_events) == 1 and len(observations.causal_event_ids) == 1)
        _require(not observations.valid_control_groups and not observations.invalid_control_event_ids and not observations.rf_events)
        _require(temporal.prior_control_age_us is None and temporal.prior_rf_age_us is None)
    else:
        _require(pre_state is not SafetyState.BOOT and not observations.has_boot)


def assess_safety_priority(
    pre_state: SafetyState, observations: NormalizedTickObservations, temporal: TemporalGuardFacts
) -> SafetyPriorityAssessment:
    """Return provisional priority constraints, never a complete state decision.

    None/None means DEFER, not permission to retain state safely. The negative
    block flag cannot be inverted into authority. Inputs must come from actual
    upstream libraries and a separate trusted state owner (synthetic in tests).
    Fixed-size validation and flag adjudication are O(1); no event/group scan,
    upstream rerun, retained history, mutation, clock, IO or output occurs.
    """
    _validate(pre_state, observations, temporal)
    next_state = category = None
    if pre_state is SafetyState.FAULT_LATCHED:                         # A
        next_state, category = SafetyState.FAULT_LATCHED, "LATCH_PERSISTS"
    elif observations.has_catastrophe:                                # B
        next_state, category = SafetyState.FAULT_LATCHED, "CATASTROPHIC_FAULT"
    elif pre_state is SafetyState.CONTINGENCY:                          # C
        next_state, category = SafetyState.CONTINGENCY, "CONTINGENCY_HOLD"
    elif pre_state in _ARMED and (                                    # D
        observations.has_invalid_control or observations.has_distinct_valid_control_conflict
        or observations.rf_has_lost or (observations.rf_has_unknown and not observations.rf_has_healthy)
    ):
        next_state, category = SafetyState.CONTINGENCY, "ARMED_OBSERVED_HAZARD"
    elif observations.has_reset:                                      # E
        next_state, category = SafetyState.SELF_TEST, "ORDINARY_RESET"
    elif pre_state is SafetyState.BOOT:                                # F
        next_state, category = SafetyState.SELF_TEST, "BOOT_INITIALIZATION"
    # G: all remaining decisions belong to a later complete FSM.
    blocked = (observations.has_catastrophe or observations.has_reset or observations.has_invalid_control
               or observations.has_distinct_valid_control_conflict or observations.rf_has_lost
               or observations.rf_has_unknown or pre_state in _RESTRICTED or next_state in _BLOCKING_NEXT
               or (pre_state in _ARMED and
                   (not temporal.prior_control_within_timeout or not temporal.prior_rf_within_timeout)))
    return SafetyPriorityAssessment(
        tick_index=observations.tick_index, eval_at_us=observations.eval_at_us, pre_state=pre_state,
        provisional_next_state=next_state, priority_category=category,
        blocks_control_qualification=blocked, requires_full_fsm=True,
    )
