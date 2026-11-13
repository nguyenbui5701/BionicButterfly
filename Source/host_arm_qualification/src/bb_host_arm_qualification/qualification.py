"""R1 LOW/HIGH timing proposals, not a health arbiter or committed FSM."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from types import MappingProxyType

from bb_host_batch_observations import NormalizedTickObservations, ValidControlGroup
from bb_host_temporal_guard_facts import TemporalGuardFacts
from bb_host_safety_priority_kernel import SafetyPriorityAssessment, SafetyState


class HealthVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"


class ControlVerdict(str, Enum):
    ADMITTED = "ADMITTED"
    ABSENT = "ABSENT"
    DENIED = "DENIED"
    UNRESOLVED = "UNRESOLVED"


class ProposalKind(str, Enum):
    DEFER = "DEFER"
    NO_CHANGE = "NO_CHANGE"
    HOLD_WINDOW = "HOLD_WINDOW"
    LOW_START = "LOW_START"
    LOW_PENDING = "LOW_PENDING"
    LOW_QUALIFIED = "LOW_QUALIFIED"
    HIGH_EDGE_ELIGIBLE = "HIGH_EDGE_ELIGIBLE"
    HIGH_PENDING = "HIGH_PENDING"
    HIGH_CONFIRMED = "HIGH_CONFIRMED"
    DEMAND_OBSERVED = "DEMAND_OBSERVED"
    LOW_DISARM_OBSERVED = "LOW_DISARM_OBSERVED"
    BLOCKED_CLEAR = "BLOCKED_CLEAR"
    CLEAR_WINDOW = "CLEAR_WINDOW"


@dataclass(frozen=True, slots=True)
class PriorQualificationWindow:
    last_committed_eval_at_us: int | None
    low_first_original_at_us: int | None
    low_qualified_committed_eval_at_us: int | None
    high_edge_original_at_us: int | None
    high_edge_committed_eval_at_us: int | None


@dataclass(frozen=True, slots=True)
class HypotheticalQualificationVerdict:
    """Test-only assumption; construction grants no authority or host trust."""

    health: HealthVerdict
    control: ControlVerdict


@dataclass(frozen=True, slots=True)
class ArmQualificationProposal:
    tick_index: int
    eval_at_us: int
    pre_state: SafetyState
    proposal_kind: ProposalKind
    proposed_low_first_original_at_us: int | None
    proposed_low_qualified_committed_eval_at_us: int | None
    proposed_high_edge_original_at_us: int | None
    proposed_high_edge_committed_eval_at_us: int | None
    requires_full_fsm: bool


_ARMED = (SafetyState.ARM_CHECK, SafetyState.ARMED_IDLE, SafetyState.ACTUATION_ACTIVE)
_WINDOW_STATES = (SafetyState.DISARMED, SafetyState.ARM_CHECK)
_BLOCKING_NEXT = (SafetyState.SELF_TEST, SafetyState.CONTINGENCY, SafetyState.FAULT_LATCHED)
_FLAP_NEUTRAL = Decimal("0.02")
_STEER_NEUTRAL = Decimal("0.05")
_STEER_NEGATIVE = Decimal("-0.05")
_DEMAND_THRESHOLD = Decimal("0.05")


def _require(condition):
    if not condition:
        raise ValueError("inconsistent upstream facts, prior window or hypothetical verdict")


def _time(value, maximum):
    _require(type(value) is int and 0 <= value <= maximum)


def _window_values(window):
    return (window.low_first_original_at_us, window.low_qualified_committed_eval_at_us,
            window.high_edge_original_at_us, window.high_edge_committed_eval_at_us)


def _validate_window(window, tick, state):
    commit = window.last_committed_eval_at_us
    low, qualified, edge, edge_commit = _window_values(window)
    if tick == 0:
        _require(commit is None and all(v is None for v in _window_values(window)))
        return
    _time(commit, tick - 1)
    _require(commit % 5000 == 0)
    for value in _window_values(window):
        if value is not None:
            _time(value, commit)
    if qualified is not None:
        _require(low is not None and qualified % 5000 == 0 and qualified - low >= 20000)
    _require((edge is None) == (edge_commit is None))
    if edge is not None:
        _require(edge <= edge_commit and edge_commit % 5000 == 0)
    if state is SafetyState.DISARMED:
        _require(edge is None)
    elif state is SafetyState.ARM_CHECK:
        _require(low is None and qualified is None)
    else:
        _require(all(v is None for v in _window_values(window)))


def _validate(observations, temporal, priority, window, verdict):
    for obj, cls in ((observations, NormalizedTickObservations), (temporal, TemporalGuardFacts),
                     (priority, SafetyPriorityAssessment), (window, PriorQualificationWindow),
                     (verdict, HypotheticalQualificationVerdict)):
        if type(obj) is not cls:
            raise TypeError("expected exact upstream records and declared hypothetical input types")
    if type(verdict.health) is not HealthVerdict or type(verdict.control) is not ControlVerdict:
        raise TypeError("expected exact hypothetical verdict enums")
    if type(priority.pre_state) is not SafetyState:
        raise TypeError("expected exact SafetyState")
    tick = observations.eval_at_us
    for record in (observations, temporal, priority):
        _time(record.tick_index, 12000)
        _time(record.eval_at_us, 60000000)
        _require(record.eval_at_us == record.tick_index * 5000)
        _require(record.tick_index == observations.tick_index and record.eval_at_us == tick)
    _require(priority.requires_full_fsm is True and type(priority.blocks_control_qualification) is bool)
    _require(priority.provisional_next_state is None or type(priority.provisional_next_state) is SafetyState)
    categories = (("BOOT_INITIALIZATION", SafetyState.SELF_TEST), ("LATCH_PERSISTS", SafetyState.FAULT_LATCHED),
                  ("CATASTROPHIC_FAULT", SafetyState.FAULT_LATCHED), ("CONTINGENCY_HOLD", SafetyState.CONTINGENCY),
                  ("ARMED_OBSERVED_HAZARD", SafetyState.CONTINGENCY), ("ORDINARY_RESET", SafetyState.SELF_TEST))
    _require((priority.priority_category is None and priority.provisional_next_state is None) or
             (type(priority.priority_category) is str and (priority.priority_category, priority.provisional_next_state) in categories))
    for name in ("source_events", "causal_event_ids", "valid_control_groups", "invalid_control_event_ids", "rf_events"):
        _require(type(getattr(observations, name)) is tuple)
    for name in ("has_invalid_control", "has_distinct_valid_control_conflict", "has_duplicate_semantic_control",
                 "rf_has_healthy", "rf_has_lost", "rf_has_unknown", "has_boot", "has_reset", "has_ack", "has_catastrophe"):
        _require(type(getattr(observations, name)) is bool)
    for left, right in (("has_invalid_control", "has_invalid_control_observation"),
                        ("has_distinct_valid_control_conflict", "has_valid_control_conflict"),
                        ("rf_has_lost", "has_rf_lost_observation"), ("rf_has_unknown", "has_rf_unknown_observation")):
        _require(type(getattr(temporal, right)) is bool and getattr(observations, left) == getattr(temporal, right))
    for channel in ("control", "rf"):
        age, within = getattr(temporal, f"prior_{channel}_age_us"), getattr(temporal, f"prior_{channel}_within_timeout")
        if age is not None:
            _time(age, tick)
        _require(type(within) is bool and within == (age is not None and age <= 200000))
    for name in ("observed_uncontested_valid_control_at_us", "observed_uncontested_healthy_rf_at_us"):
        value = getattr(temporal, name)
        if value is not None:
            _time(value, tick)
            _require(max(0, tick - 5000) < value)
    _require(observations.has_boot == (tick == 0))
    _require((priority.pre_state is SafetyState.BOOT) == (tick == 0))
    _validate_window(window, tick, priority.pre_state)

    blocked = (observations.has_catastrophe or observations.has_reset or observations.has_invalid_control
               or observations.has_distinct_valid_control_conflict or observations.rf_has_lost or observations.rf_has_unknown
               or priority.pre_state in (SafetyState.CONTINGENCY, SafetyState.FAULT_LATCHED)
               or priority.provisional_next_state in _BLOCKING_NEXT
               or (priority.pre_state in _ARMED and
                   (not temporal.prior_control_within_timeout or not temporal.prior_rf_within_timeout)))
    _require(priority.blocks_control_qualification == blocked)
    groups = observations.valid_control_groups
    _require(observations.has_distinct_valid_control_conflict == (len(groups) > 1))
    _require(observations.has_invalid_control == bool(observations.invalid_control_event_ids))
    candidate = temporal.observed_uncontested_valid_control_at_us
    body = None
    uncontested = len(groups) == 1 and not observations.has_invalid_control
    _require((candidate is not None) == uncontested)
    if uncontested:
        group = groups[0]
        _require(type(group) is ValidControlGroup)
        _time(group.latest_original_at_us, tick)
        _require(max(0, tick - 5000) < group.latest_original_at_us == candidate)
        body = group.semantic_control
        _require(type(body) is MappingProxyType and set(body) ==
                 {"uart_frame_status", "arm_switch", "flap_demand", "steering_demand", "map_revision"})
        _require(body["uart_frame_status"] == "VALID" and body["map_revision"] == "sim-map-v1" and type(body["arm_switch"]) is bool)
        for key, lower, upper in (("flap_demand", 0, 1), ("steering_demand", -1, 1)):
            value = body[key]
            _require(type(value) is int or (type(value) is Decimal and value.is_finite()))
            _require(lower <= value <= upper)
    if verdict.health is HealthVerdict.PASS:
        _require(not blocked)
    if verdict.control is ControlVerdict.ADMITTED:
        _require(verdict.health is HealthVerdict.PASS and uncontested)
        # No committed HIGH edge means no possible confirming frame snapshot.
        if priority.pre_state is SafetyState.ARM_CHECK and body["arm_switch"]:
            _require(window.high_edge_original_at_us is not None)
    elif verdict.control is ControlVerdict.ABSENT:
        _require(candidate is None)
    elif verdict.control is ControlVerdict.DENIED:
        _require(candidate is not None)
    return body, candidate


def propose_arm_qualification(observations: NormalizedTickObservations, temporal: TemporalGuardFacts,
                              priority: SafetyPriorityAssessment, prior_window: PriorQualificationWindow,
                              verdict: HypotheticalQualificationVerdict) -> ArmQualificationProposal:
    """Evaluate synthetic guard hypotheses without accepting, arming or committing.

    All validation precedes proposals, including contradictory PASS/ADMITTED.
    Constant-size metadata and one semantic body only; no events/member scans,
    upstream reruns, state, IO or clock. None of these inputs confer host trust.
    """
    body, original = _validate(observations, temporal, priority, prior_window, verdict)
    state, tick = priority.pre_state, observations.eval_at_us
    empty = (None, None, None, None)
    previous = _window_values(prior_window)
    low, qualified, edge, edge_commit = previous

    def result(kind, values=empty):
        return ArmQualificationProposal(observations.tick_index, tick, state, kind, *values, True)

    if state is SafetyState.CONTINGENCY:
        return result(ProposalKind.DEFER)
    if priority.provisional_next_state in _BLOCKING_NEXT or priority.blocks_control_qualification or verdict.health is HealthVerdict.FAIL:
        return result(ProposalKind.BLOCKED_CLEAR)
    if state in (SafetyState.BOOT, SafetyState.SELF_TEST, SafetyState.FAULT_LATCHED):
        return result(ProposalKind.DEFER)
    if verdict.health is HealthVerdict.UNRESOLVED or verdict.control is ControlVerdict.UNRESOLVED:
        return result(ProposalKind.DEFER, previous)
    if verdict.control is ControlVerdict.DENIED:
        return result(ProposalKind.CLEAR_WINDOW)
    if verdict.control is ControlVerdict.ABSENT:
        return result(ProposalKind.HOLD_WINDOW if any(v is not None for v in previous) else ProposalKind.NO_CHANGE, previous)

    high = body["arm_switch"]
    # Avoid abs(Decimal) or arithmetic that can round under the caller's context.
    neutral = body["flap_demand"] <= _FLAP_NEUTRAL and _STEER_NEGATIVE <= body["steering_demand"] <= _STEER_NEUTRAL
    if state is SafetyState.DISARMED:
        if not high:
            if low is None:
                return result(ProposalKind.LOW_START, (original, None, None, None))
            if qualified is not None:
                return result(ProposalKind.HOLD_WINDOW, previous)
            if original - low < 20000:
                return result(ProposalKind.LOW_PENDING, previous)
            return result(ProposalKind.LOW_QUALIFIED, (low, tick, None, None))
        if qualified is not None and qualified < tick and neutral:
            return result(ProposalKind.HIGH_EDGE_ELIGIBLE, (None, None, original, tick))
        return result(ProposalKind.CLEAR_WINDOW)
    if not high:
        return result(ProposalKind.LOW_DISARM_OBSERVED)
    if state is SafetyState.ARM_CHECK:
        if not neutral:
            return result(ProposalKind.CLEAR_WINDOW)
        if original - edge < 100000:
            return result(ProposalKind.HIGH_PENDING, previous)
        return result(ProposalKind.HIGH_CONFIRMED)
    if state is SafetyState.ARMED_IDLE and body["flap_demand"] > _DEMAND_THRESHOLD:
        return result(ProposalKind.DEMAND_OBSERVED)
    return result(ProposalKind.NO_CHANGE)
