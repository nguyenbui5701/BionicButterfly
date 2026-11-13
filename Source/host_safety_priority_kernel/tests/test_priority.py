import ast
import builtins
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal, localcontext
from enum import Enum
import locale
from pathlib import Path
import random
import socket
import sys
import time

import pytest

from bb_host_batch_observations import NormalizedTickObservations
from bb_host_temporal_guard_facts import TemporalGuardFacts
from bb_host_safety_priority_kernel import SafetyState as S, SafetyPriorityAssessment, assess_safety_priority as assess
import bb_host_safety_priority_kernel.priority as runtime
from scripts.scenarios import pipeline, recipe_at

LATER = tuple(s for s in S if s is not S.BOOT)
ARMED = (S.ARM_CHECK, S.ARMED_IDLE, S.ACTUATION_ACTIVE)


def event(kind, at=5000, identity="e", **extra):
    return dict(event_id=identity, event_at_us=at, kind=kind, **extra)


def valid(identity="v", at=5000, **extra):
    return event("CONTROL_VALID", at, identity, **(dict(arm=False, flap="0.1", steer="0") | extra))


def facts(*events, tick=5000, prior_times=None):
    recipe = recipe_at(tick, *events)
    if prior_times is not None:
        recipe["prior_snapshot"]["last_accepted_control_at_us"], recipe["prior_snapshot"]["last_uncontested_healthy_rf_at_us"] = prior_times
    return pipeline(recipe)[2::2]  # observations and temporal; synthetic prior stays separate


def decision(state, *events, **kwargs):
    return assess(state, *facts(*events, **kwargs))


@pytest.mark.parametrize("state", LATER)
def test_catastrophe_dominates_all_other_current_hazards(state):
    result = decision(state, event("RESET", identity="reset"), event("ACK", identity="ack"),
                      valid("low"), valid("high", arm=True), event("CONTROL_INVALID", identity="bad"),
                      event("RF_LOST", identity="lost"), event("CATA", identity="cat"))
    assert result.provisional_next_state is S.FAULT_LATCHED
    assert result.priority_category == ("LATCH_PERSISTS" if state is S.FAULT_LATCHED else "CATASTROPHIC_FAULT")
    assert result.blocks_control_qualification and result.requires_full_fsm


@pytest.mark.parametrize("kind", ["RESET", "ACK", "RF_HEALTHY", "CATA"])
def test_prior_latch_persists_with_all_recovery_like_stimuli(kind):
    result = decision(S.FAULT_LATCHED, event(kind), prior_times=(0, 0))
    assert result.provisional_next_state is S.FAULT_LATCHED
    assert result.priority_category == "LATCH_PERSISTS"


@pytest.mark.parametrize("state", ARMED)
@pytest.mark.parametrize("hazard", ["RF_LOST", "RF_UNKNOWN", "CONTROL_INVALID", "CONFLICT", "HEALTHY_LOST"])
def test_armed_explicit_hazard_outranks_reset_even_with_fresh_prior(state, hazard):
    if hazard == "CONFLICT":
        events = [valid("a"), valid("b", arm=True)]
    elif hazard == "HEALTHY_LOST":
        events = [event("RF_HEALTHY", identity="h"), event("RF_LOST", identity="l")]
    else:
        events = [event(hazard)]
    result = decision(state, *events, event("RESET", identity="reset"), prior_times=(0, 0))
    assert result.provisional_next_state is S.CONTINGENCY
    assert result.priority_category == "ARMED_OBSERVED_HAZARD"
    assert result.blocks_control_qualification


@pytest.mark.parametrize("state", (S.SELF_TEST, S.DISARMED, *ARMED))
def test_ordinary_reset_when_no_higher_observed_hazard(state):
    result = decision(state, event("RESET"), valid())
    assert result.provisional_next_state is S.SELF_TEST
    assert result.priority_category == "ORDINARY_RESET" and result.blocks_control_qualification


@pytest.mark.parametrize("reset", [False, True])
def test_contingency_ack_never_completes_recovery(reset):
    events = [event("RF_HEALTHY", identity="rf"), valid(), event("ACK", identity="ack")]
    if reset:
        events.append(event("RESET", identity="reset"))
    result = decision(S.CONTINGENCY, *events, prior_times=(0, 0))
    assert result.provisional_next_state is S.CONTINGENCY
    assert result.priority_category == "CONTINGENCY_HOLD" and result.requires_full_fsm


@pytest.mark.parametrize("state", (S.SELF_TEST, S.DISARMED, *ARMED))
@pytest.mark.parametrize("reset", [False, True])
def test_unknown_healthy_is_unresolved_but_blocks(state, reset):
    events = [event("RF_UNKNOWN", identity="u"), event("RF_HEALTHY", identity="h")]
    if reset:
        events.append(event("RESET", identity="reset"))
    result = decision(state, *events, prior_times=(0, 0))
    assert result.provisional_next_state is (S.SELF_TEST if reset else None)
    assert result.priority_category == ("ORDINARY_RESET" if reset else None)
    assert result.blocks_control_qualification and result.requires_full_fsm


@pytest.mark.parametrize("state", ARMED)
@pytest.mark.parametrize("prior_times", [(None, None), (None, 5000), (5000, None), (4999, 5000), (5000, 4999), (4999, 4999), (5000, 5000)])
def test_prior_missing_or_stale_blocks_without_age_based_transition(state, prior_times):
    result = decision(state, valid(at=204999), event("RF_HEALTHY", 205000, "h"),
                      tick=205000, prior_times=prior_times)
    assert result.provisional_next_state is None and result.priority_category is None
    assert result.blocks_control_qualification is (prior_times != (5000, 5000))
    assert result.requires_full_fsm


@pytest.mark.parametrize("state", [S.SELF_TEST, S.DISARMED])
def test_unarmed_stale_history_alone_does_not_invent_block_or_readiness(state):
    result = decision(state, tick=205000, prior_times=(4999, 4999))
    assert result.provisional_next_state is None and result.priority_category is None
    assert not result.blocks_control_qualification and result.requires_full_fsm


@pytest.mark.parametrize("state", (S.SELF_TEST, S.DISARMED, *ARMED))
def test_no_arm_or_self_test_completion_from_high_and_fresh_age(state):
    result = decision(state, valid(arm=True, flap="0.8"), event("RF_HEALTHY", identity="rf"), prior_times=(0, 0))
    assert result.provisional_next_state is None
    assert result.priority_category is None and result.requires_full_fsm
    assert not result.blocks_control_qualification


@pytest.mark.parametrize("channel", ["state", "observations", "temporal"])
@pytest.mark.parametrize("bad", [None, True, 1, "BOOT", {}, [], b"{}"])
def test_wrong_caller_types(channel, bad):
    obs, temporal = facts()
    args = [S.DISARMED, obs, temporal]
    args[["state", "observations", "temporal"].index(channel)] = bad
    with pytest.raises(TypeError):
        assess(*args)


def test_forged_enum_and_upstream_subclasses_rejected():
    class Other(str, Enum):
        DISARMED = "DISARMED"
    class ForgedObs(NormalizedTickObservations):
        pass
    class ForgedTemporal(TemporalGuardFacts):
        pass
    obs, temporal = facts()
    with pytest.raises(TypeError):
        assess(Other.DISARMED, obs, temporal)
    with pytest.raises(TypeError):
        assess(S.DISARMED, ForgedObs(**{f.name: getattr(obs, f.name) for f in fields(obs)}), temporal)
    with pytest.raises(TypeError):
        assess(S.DISARMED, obs, ForgedTemporal(**{f.name: getattr(temporal, f.name) for f in fields(temporal)}))


@pytest.mark.parametrize("channel", ["observations", "temporal"])
@pytest.mark.parametrize("change", [{"tick_index": True}, {"tick_index": 1.0}, {"tick_index": -1},
                                    {"tick_index": 12001}, {"eval_at_us": True}, {"eval_at_us": 5000.0},
                                    {"eval_at_us": -1}, {"eval_at_us": 5001},
                                    {"tick_index": 2, "eval_at_us": 10000}])
def test_bad_tick_grid_and_mismatched_tick_reject_before_result(channel, change, monkeypatch):
    obs, temporal = facts()
    if channel == "observations":
        obs = replace(obs, **change)
    else:
        temporal = replace(temporal, **change)
    def forbidden(*args, **kwargs):
        pytest.fail("constructed an assessment for an invalid caller")
    monkeypatch.setattr(runtime, "SafetyPriorityAssessment", forbidden)
    with pytest.raises(ValueError):
        assess(S.DISARMED, obs, temporal)


@pytest.mark.parametrize("obs_name,temporal_name", [
    ("rf_has_lost", "has_rf_lost_observation"), ("rf_has_unknown", "has_rf_unknown_observation"),
    ("has_invalid_control", "has_invalid_control_observation"),
    ("has_distinct_valid_control_conflict", "has_valid_control_conflict")])
@pytest.mark.parametrize("change_observations", [False, True])
def test_mirrored_hazards_must_match(obs_name, temporal_name, change_observations):
    obs, temporal = facts()
    if change_observations:
        obs = replace(obs, **{obs_name: True})
    else:
        temporal = replace(temporal, **{temporal_name: True})
    with pytest.raises(ValueError):
        assess(S.ACTUATION_ACTIVE, obs, temporal)


@pytest.mark.parametrize("name", runtime._OBS_FLAGS)
def test_observation_flags_are_exact_bool(name):
    obs, temporal = facts()
    with pytest.raises(ValueError):
        assess(S.DISARMED, replace(obs, **{name: 0}), temporal)


@pytest.mark.parametrize("name", ["has_rf_lost_observation", "has_rf_unknown_observation", "has_invalid_control_observation",
                                 "has_valid_control_conflict", "prior_control_within_timeout", "prior_rf_within_timeout"])
def test_temporal_flags_are_exact_bool(name):
    obs, temporal = facts()
    with pytest.raises(ValueError):
        assess(S.DISARMED, obs, replace(temporal, **{name: 0}))


@pytest.mark.parametrize("name", ["source_events", "causal_event_ids", "valid_control_groups", "invalid_control_event_ids", "rf_events"])
def test_mutable_outer_collections_rejected(name):
    obs, temporal = facts()
    with pytest.raises(ValueError):
        assess(S.DISARMED, replace(obs, **{name: []}), temporal)


@pytest.mark.parametrize("name", ["prior_control_age_us", "prior_rf_age_us",
                                 "observed_uncontested_valid_control_at_us", "observed_uncontested_healthy_rf_at_us"])
@pytest.mark.parametrize("value", [True, 1.0, Decimal(1), -1, 5001, "1"])
def test_malformed_temporal_numeric_fields(name, value):
    obs, temporal = facts()
    with pytest.raises(ValueError):
        assess(S.DISARMED, obs, replace(temporal, **{name: value}))


@pytest.mark.parametrize("name", ["prior_control_within_timeout", "prior_rf_within_timeout"])
def test_absent_age_cannot_be_fresh(name):
    obs, temporal = facts()
    with pytest.raises(ValueError):
        assess(S.DISARMED, obs, replace(temporal, **{name: True}))


@pytest.mark.parametrize("state", LATER)
def test_non_boot_prestate_at_t0_rejected(state):
    with pytest.raises(ValueError):
        assess(state, *facts(tick=0))


def test_boot_cannot_appear_later_or_be_absent_at_zero():
    obs, temporal = facts()
    with pytest.raises(ValueError):
        assess(S.BOOT, obs, temporal)
    with pytest.raises(ValueError):
        assess(S.DISARMED, replace(obs, has_boot=True), temporal)
    obs, temporal = facts(tick=0)
    with pytest.raises(ValueError):
        assess(S.BOOT, replace(obs, has_boot=False), temporal)


@pytest.mark.parametrize("name", ["has_catastrophe", "has_reset", "has_ack", "rf_has_healthy", "has_duplicate_semantic_control"])
def test_impossible_t0_flags_rejected_before_priority(name):
    obs, temporal = facts(tick=0)
    with pytest.raises(ValueError):
        assess(S.BOOT, replace(obs, **{name: True}), temporal)


def test_final_allowed_tick_and_strict_result_contract():
    result = decision(S.ACTUATION_ACTIVE, tick=60000000, prior_times=(59800000, 59800000))
    assert result.tick_index == 12000 and result.eval_at_us == 60000000
    assert result.provisional_next_state is None and not result.blocks_control_qualification
    expected = {"tick_index", "eval_at_us", "pre_state", "provisional_next_state", "priority_category",
                "blocks_control_qualification", "requires_full_fsm"}
    assert {f.name for f in fields(result)} == expected
    assert [s.value for s in S] == ["BOOT", "SELF_TEST", "DISARMED", "ARM_CHECK", "ARMED_IDLE", "ACTUATION_ACTIVE", "CONTINGENCY", "FAULT_LATCHED"]
    assert not hasattr(result, "__dict__")
    for name in expected:
        with pytest.raises(FrozenInstanceError):
            setattr(result, name, None)
        with pytest.raises(FrozenInstanceError):
            delattr(result, name)


def test_no_event_or_group_content_access():
    class Poison:
        def __getitem__(self, key):
            raise AssertionError("event/group content read")
        def __getattr__(self, key):
            raise AssertionError("event/group attribute read")
        def __iter__(self):
            raise AssertionError("event/group iteration")
    obs, temporal = facts(valid(), event("RF_HEALTHY", identity="rf"), prior_times=(0, 0))
    poisoned = replace(obs, source_events=(Poison(),) * 19999, valid_control_groups=(Poison(),), rf_events=(Poison(),) * 19999)
    assert assess(S.DISARMED, poisoned, temporal) == assess(S.DISARMED, obs, temporal)


def test_constant_work_for_real_small_and_large_batches():
    pairs = []
    for count in (1, 5000):
        pairs.append(facts(*(event("RF_HEALTHY", identity=str(i)) for i in range(count)), prior_times=(0, 0)))
    counts = []
    for obs, temporal in pairs:
        lines = 0
        def trace(frame, action, arg):
            nonlocal lines
            if frame.f_code.co_filename == runtime.__file__ and action == "line":
                lines += 1
            return trace
        previous = sys.gettrace()
        try:
            sys.settrace(trace)
            result = assess(S.ACTUATION_ACTIVE, obs, temporal)
        finally:
            sys.settrace(previous)
        assert result.provisional_next_state is None
        counts.append(lines)
    assert counts[0] == counts[1] and counts[0] < 300


def test_no_io_or_pipeline_rerun(monkeypatch):
    import bb_host_preflight_m0
    import bb_host_virtual_ticks
    import bb_host_batch_observations
    import bb_host_temporal_guard_facts
    obs, temporal = facts(event("RESET"))
    expected = assess(S.DISARMED, obs, temporal)
    def forbidden(*args, **kwargs):
        raise AssertionError("prohibited side effect or upstream rerun")
    with monkeypatch.context() as m:
        for module, names in ((builtins, ("open",)), (time, ("time", "monotonic", "sleep")), (random, ("random",)),
                              (socket, ("socket",)), (bb_host_preflight_m0, ("validate_wire", "mix_m0", "mixM0")),
                              (bb_host_virtual_ticks, ("iter_virtual_ticks",)),
                              (bb_host_batch_observations, ("normalize_tick_observations",)),
                              (bb_host_temporal_guard_facts, ("evaluate_temporal_guard_facts",))):
            for name in names:
                m.setattr(module, name, forbidden)
        assert assess(S.DISARMED, obs, temporal) == expected


def test_import_and_call_architecture():
    allowed = {"dataclasses", "enum", "bb_host_batch_observations", "bb_host_temporal_guard_facts", "priority"}
    prohibited = {"open", "print", "eval", "exec", "compile", "__import__", "float", "sleep", "time", "mix_m0",
                  "mixM0", "normalize_tick_observations", "evaluate_temporal_guard_facts", "iter_virtual_ticks", "validate_wire"}
    for path in Path(runtime.__file__).parent.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                assert all(a.name in allowed for a in node.names)
            if isinstance(node, ast.ImportFrom):
                assert node.module in allowed
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
                assert name not in prohibited


def test_repeated_determinism_and_no_retained_latch(monkeypatch):
    obs, temporal = facts(valid(at=204999), tick=205000, prior_times=(4999, 5000))
    expected = assess(S.ACTUATION_ACTIVE, obs, temporal)
    saved = locale.setlocale(locale.LC_ALL)
    try:
        for name in ("C", "English_United States.1252"):
            locale.setlocale(locale.LC_ALL, name)
            for tz in ("UTC0", "ICT-7"):
                monkeypatch.setenv("TZ", tz)
                with localcontext() as context:
                    context.prec = 2
                    assert decision(S.FAULT_LATCHED).provisional_next_state is S.FAULT_LATCHED
                    assert assess(S.ACTUATION_ACTIVE, obs, temporal) == expected
    finally:
        locale.setlocale(locale.LC_ALL, saved)
