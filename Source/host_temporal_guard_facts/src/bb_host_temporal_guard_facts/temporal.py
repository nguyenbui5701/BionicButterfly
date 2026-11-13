"""Exact ages of prior facts and uncommitted observations for one tick."""

from dataclasses import dataclass
from types import MappingProxyType

from bb_host_batch_observations import NormalizedTickObservations, ValidControlGroup


@dataclass(frozen=True, slots=True)
class PriorCommittedTimestampFacts:
    """Input from a future trusted state owner; tests use synthetic snapshots.

    Construction grants no trust. The evaluator checks the timestamp invariants
    against the current tick before producing any result.
    """

    last_committed_eval_at_us: int | None
    last_accepted_control_at_us: int | None
    last_uncontested_healthy_rf_at_us: int | None


@dataclass(frozen=True, slots=True)
class TemporalGuardFacts:
    tick_index: int
    eval_at_us: int
    prior_control_age_us: int | None
    prior_rf_age_us: int | None
    prior_control_within_timeout: bool
    prior_rf_within_timeout: bool
    observed_uncontested_valid_control_at_us: int | None
    observed_uncontested_healthy_rf_at_us: int | None
    has_rf_lost_observation: bool
    has_rf_unknown_observation: bool
    has_invalid_control_observation: bool
    has_valid_control_conflict: bool


def _require(condition):
    if not condition:
        raise ValueError("expected immutable normalized observations and valid prior timestamps")


def _original_time(value, tick):
    _require(type(value) is int)
    _require(value == 0 if tick == 0 else tick - 5000 < value <= tick)
    return value


def _age(tick, timestamp):
    return None if timestamp is None else tick - timestamp


def evaluate_temporal_guard_facts(
    observations: NormalizedTickObservations, prior: PriorCommittedTimestampFacts
) -> TemporalGuardFacts:
    """Compute independent 200000us inclusive ages without refreshing history.

    Inputs must come from the real normalizer and an independent committed state
    owner. Boundary checks are not authentication or a second normalization pass.
    Only consumed timestamps/flags and outer collection shapes are inspected;
    original events and semantic grouping remain TASK-003's responsibility.
    Cost is O(RF observations), with O(1) additional memory and no retained state.
    """
    if type(observations) is not NormalizedTickObservations:
        raise TypeError("expected exact TASK-003 NormalizedTickObservations")
    if type(prior) is not PriorCommittedTimestampFacts:
        raise TypeError("expected exact PriorCommittedTimestampFacts")
    tick = observations.eval_at_us
    _require(type(observations.tick_index) is int and 0 <= observations.tick_index <= 12000)
    _require(type(tick) is int and tick == observations.tick_index * 5000)
    for name in ("source_events", "causal_event_ids", "valid_control_groups",
                 "invalid_control_event_ids", "rf_events"):
        _require(type(getattr(observations, name)) is tuple)
    for name in ("has_invalid_control", "has_distinct_valid_control_conflict",
                 "has_duplicate_semantic_control", "rf_has_healthy", "rf_has_lost",
                 "rf_has_unknown", "has_boot", "has_reset", "has_ack", "has_catastrophe"):
        _require(type(getattr(observations, name)) is bool)
    committed = prior.last_committed_eval_at_us
    control_at = prior.last_accepted_control_at_us
    rf_at = prior.last_uncontested_healthy_rf_at_us
    if tick == 0:
        _require(committed is None and control_at is None and rf_at is None)
    else:
        _require(type(committed) is int and 0 <= committed < tick and committed % 5000 == 0)
        for timestamp in (control_at, rf_at):
            _require(timestamp is None or (type(timestamp) is int and 0 <= timestamp <= committed))

    groups = observations.valid_control_groups
    _require(observations.has_distinct_valid_control_conflict == (len(groups) > 1))
    _require(observations.has_invalid_control == bool(observations.invalid_control_event_ids))
    control_candidate = None
    if len(groups) == 1:
        group = groups[0]
        _require(type(group) is ValidControlGroup)
        _require(type(group.semantic_control) is MappingProxyType)
        _require(type(group.member_events) is tuple and bool(group.member_events))
        _require(type(group.event_ids) is tuple and bool(group.event_ids))
        latest = _original_time(group.latest_original_at_us, tick)
        if not observations.has_invalid_control:
            control_candidate = latest

    healthy = lost = unknown = False
    latest_rf = None
    for event in observations.rf_events:
        _require(type(event) is MappingProxyType)
        _require(set(event) == {"event_id", "event_at_us", "type", "payload"})
        _require(event["type"] == "SIM_RF_STATUS")
        at = _original_time(event["event_at_us"], tick)
        body = event["payload"]
        _require(type(body) is MappingProxyType and set(body) == {"rf_health", "rf_provenance"})
        status = body["rf_health"]
        _require(type(status) is str and status in ("HEALTHY", "LOST", "UNKNOWN"))
        _require(type(body["rf_provenance"]) is str and body["rf_provenance"] == "INJECTED_SIM")
        healthy |= status == "HEALTHY"
        lost |= status == "LOST"
        unknown |= status == "UNKNOWN"
        latest_rf = at if latest_rf is None else max(latest_rf, at)
    _require((healthy, lost, unknown) == (
        observations.rf_has_healthy, observations.rf_has_lost, observations.rf_has_unknown))
    control_age, rf_age = _age(tick, control_at), _age(tick, rf_at)
    return TemporalGuardFacts(
        tick_index=observations.tick_index, eval_at_us=tick,
        prior_control_age_us=control_age, prior_rf_age_us=rf_age,
        prior_control_within_timeout=control_age is not None and control_age <= 200000,
        prior_rf_within_timeout=rf_age is not None and rf_age <= 200000,
        observed_uncontested_valid_control_at_us=control_candidate,
        observed_uncontested_healthy_rf_at_us=latest_rf if healthy and not lost and not unknown else None,
        has_rf_lost_observation=observations.rf_has_lost,
        has_rf_unknown_observation=observations.rf_has_unknown,
        has_invalid_control_observation=observations.has_invalid_control,
        has_valid_control_conflict=observations.has_distinct_valid_control_conflict,
    )
