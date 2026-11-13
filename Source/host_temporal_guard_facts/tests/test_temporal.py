import ast
import builtins
from dataclasses import FrozenInstanceError, asdict, fields, replace
from decimal import Decimal, localcontext
import locale
from pathlib import Path
import random
import socket
import sys
import time
from types import MappingProxyType

import pytest

from bb_host_batch_observations import NormalizedTickObservations, normalize_tick_observations
from bb_host_temporal_guard_facts import PriorCommittedTimestampFacts as Prior
from bb_host_temporal_guard_facts import TemporalGuardFacts, evaluate_temporal_guard_facts as evaluate
import bb_host_temporal_guard_facts.temporal as runtime
from scripts.scenarios import pipeline, recipe_at


def event(kind, at=4999, identity="e", **extra):
    return dict(id=identity, event_at_us=at, kind=kind, **extra)


def control(at=4999, identity="v", **extra):
    return event("CONTROL_VALID", at, identity, **dict(arm=False, flap="0.1", steer="0") | extra)


def observed(tick=5000, *events):
    return pipeline(recipe_at(tick, *events))[2]


@pytest.mark.parametrize("value", [None, {}, [], b"{}", True, 1, "observations", object()])
def test_wrong_observations_type(value):
    with pytest.raises(TypeError):
        evaluate(value, Prior(None, None, None))


@pytest.mark.parametrize("value", [None, {}, [], (0, None, None), True, object()])
def test_wrong_prior_type(value):
    with pytest.raises(TypeError):
        evaluate(observed(), value)


def test_exact_types_reject_subclasses():
    class ForgedObservations(NormalizedTickObservations):
        pass
    class ForgedPrior(Prior):
        pass
    original = observed()
    clone = ForgedObservations(**{f.name: getattr(original, f.name) for f in fields(original)})
    with pytest.raises(TypeError):
        evaluate(clone, Prior(0, None, None))
    with pytest.raises(TypeError):
        evaluate(original, ForgedPrior(0, None, None))


@pytest.mark.parametrize("committed", [None, True, False, 0.0, Decimal(0), -5000, 1, 199999, 205000, 210000])
def test_invalid_prior_commit(committed):
    with pytest.raises((TypeError, ValueError)):
        evaluate(observed(205000), Prior(committed, None, None))


@pytest.mark.parametrize("field", ["last_accepted_control_at_us", "last_uncontested_healthy_rf_at_us"])
@pytest.mark.parametrize("timestamp", [True, False, 1.0, Decimal(1), -1, 200001, 205001, [], "1"])
def test_invalid_prior_original_timestamp(field, timestamp):
    prior = replace(Prior(200000, None, None), **{field: timestamp})
    with pytest.raises((TypeError, ValueError)):
        evaluate(observed(205000), prior)


@pytest.mark.parametrize("prior", [Prior(0, None, None), Prior(None, 0, None), Prior(None, None, 0),
                                  Prior(False, None, None), Prior(None, True, None)])
def test_t0_requires_all_none(prior):
    with pytest.raises(ValueError):
        evaluate(observed(0), prior)


@pytest.mark.parametrize("changes", [
    {"tick_index": True}, {"tick_index": -1}, {"tick_index": 12001}, {"tick_index": 1.0},
    {"eval_at_us": True}, {"eval_at_us": 5000.0}, {"eval_at_us": -1}, {"eval_at_us": 5001},
    {"eval_at_us": 10000}, {"rf_events": []}, {"valid_control_groups": []}, {"source_events": []},
    {"causal_event_ids": []}, {"invalid_control_event_ids": []}, {"has_invalid_control": 1},
    {"has_invalid_control": True}, {"has_distinct_valid_control_conflict": True},
    {"rf_has_healthy": 1}, {"rf_has_healthy": True}, {"rf_has_lost": True}, {"rf_has_unknown": True},
])
def test_malformed_observation_envelope(changes):
    with pytest.raises((TypeError, ValueError)):
        evaluate(replace(observed(), **changes), Prior(0, None, None))


@pytest.mark.parametrize("timestamp", [True, False, 1.0, Decimal(1), -1, 0, 5001, None])
@pytest.mark.parametrize("channel", ["control", "rf"])
def test_malformed_current_timestamps_before_output(timestamp, channel, monkeypatch):
    observation = observed(5000, control() if channel == "control" else event("RF_HEALTHY"))
    if channel == "control":
        group = replace(observation.valid_control_groups[0], latest_original_at_us=timestamp)
        observation = replace(observation, valid_control_groups=(group,))
    else:
        record = MappingProxyType(dict(observation.rf_events[0], event_at_us=timestamp))
        observation = replace(observation, rf_events=(record,))
    def forbidden(*args, **kwargs):
        pytest.fail("a malformed input constructed output")
    monkeypatch.setattr(runtime, "TemporalGuardFacts", forbidden)
    with pytest.raises((TypeError, ValueError)):
        evaluate(observation, Prior(0, None, None))


@pytest.mark.parametrize("shape", ["mutable_event", "mutable_payload", "bad_status", "wrong_type", "missing_time"])
def test_malformed_rf_shapes(shape):
    observation = observed(5000, event("RF_HEALTHY"))
    record = dict(observation.rf_events[0])
    if shape == "mutable_payload":
        record["payload"] = dict(record["payload"])
    elif shape == "bad_status":
        record["payload"] = MappingProxyType(dict(record["payload"], rf_health="MAYBE"))
    elif shape == "wrong_type":
        record["type"] = "SIM_RESET"
    elif shape == "missing_time":
        del record["event_at_us"]
    if shape != "mutable_event":
        record = MappingProxyType(record)
    with pytest.raises(ValueError):
        evaluate(replace(observation, rf_events=(record,)), Prior(0, None, None))


@pytest.mark.parametrize("channel", ["control", "rf"])
@pytest.mark.parametrize("age", [199999, 200000, 200001])
def test_independent_boundary_at_final_allowed_tick(channel, age):
    prior = Prior(59995000, 60000000 - age if channel == "control" else None,
                  60000000 - age if channel == "rf" else None)
    result = evaluate(observed(60000000), prior)
    assert result.tick_index == 12000
    assert getattr(result, f"prior_{channel}_age_us") == age
    assert getattr(result, f"prior_{channel}_within_timeout") is (age <= 200000)
    other = "rf" if channel == "control" else "control"
    assert getattr(result, f"prior_{other}_age_us") is None
    assert getattr(result, f"prior_{other}_within_timeout") is False


def test_prior_commit_may_skip_ticks_and_original_zero_is_not_absent():
    result = evaluate(observed(200000), Prior(0, 0, 0))
    assert result.prior_control_age_us == result.prior_rf_age_us == 200000
    assert result.prior_control_within_timeout and result.prior_rf_within_timeout


def test_duplicate_exact_controls_candidate_uses_latest_original_time():
    observation = observed(5000, control(4000, "a", flap="0.1000000"), control(4999, "b", flap="1e-1"))
    assert observation.has_duplicate_semantic_control
    assert len(observation.valid_control_groups) == 1
    result = evaluate(observation, Prior(0, None, None))
    assert result.observed_uncontested_valid_control_at_us == 4999
    assert result.prior_control_age_us is None


@pytest.mark.parametrize("hazard", ["RF_LOST", "RF_UNKNOWN", "RESET", "ACK", "CATA"])
def test_other_hazards_do_not_accept_or_suppress_control_candidate(hazard):
    observation = observed(5000, control(), event(hazard, 5000, "hazard"))
    prior = Prior(0, None, None)
    result = evaluate(observation, prior)
    assert result.observed_uncontested_valid_control_at_us == 4999
    assert result.prior_control_age_us is None and not result.prior_control_within_timeout
    assert prior == Prior(0, None, None)


@pytest.mark.parametrize("kinds", [("RF_HEALTHY", "RF_UNKNOWN"), ("RF_UNKNOWN", "RF_HEALTHY"),
                                   ("RF_LOST", "RF_HEALTHY"), ("RF_HEALTHY", "RF_LOST"),
                                   ("RF_UNKNOWN",), ("RF_HEALTHY", "RF_LOST", "RF_UNKNOWN")])
def test_rf_mixed_statuses_never_promote_candidate(kinds):
    observation = observed(205000, *(event(kind, 204990+i, str(i)) for i, kind in enumerate(kinds)))
    result = evaluate(observation, Prior(200000, None, 5000))
    assert result.observed_uncontested_healthy_rf_at_us is None
    assert result.prior_rf_within_timeout  # arithmetic remains independent of hazards
    assert result.has_rf_lost_observation is ("RF_LOST" in kinds)
    assert result.has_rf_unknown_observation is ("RF_UNKNOWN" in kinds)


def test_conflict_without_invalid_has_no_candidate():
    observation = observed(5000, control(4998, "a"), control(4999, "b", arm=True))
    result = evaluate(observation, Prior(0, None, None))
    assert result.has_valid_control_conflict and not result.has_invalid_control_observation
    assert result.observed_uncontested_valid_control_at_us is None


def test_current_rf_does_not_refresh_stale_prior_and_no_history():
    prior = Prior(200000, 4999, 4999)
    observation = observed(205000, event("RF_HEALTHY", 204999))
    result = evaluate(observation, prior)
    assert result.observed_uncontested_healthy_rf_at_us == 204999
    assert result.prior_rf_age_us == result.prior_control_age_us == 200001
    assert not result.prior_rf_within_timeout and not result.prior_control_within_timeout
    later = evaluate(observed(210000), Prior(205000, 4999, 4999))
    assert later.observed_uncontested_healthy_rf_at_us is None
    assert later.prior_rf_age_us == 205001
    assert evaluate(observation, prior) == result


def test_exact_result_and_prior_shapes_are_frozen():
    expected = {"tick_index", "eval_at_us", "prior_control_age_us", "prior_rf_age_us",
                "prior_control_within_timeout", "prior_rf_within_timeout",
                "observed_uncontested_valid_control_at_us", "observed_uncontested_healthy_rf_at_us",
                "has_rf_lost_observation", "has_rf_unknown_observation",
                "has_invalid_control_observation", "has_valid_control_conflict"}
    prior = Prior(0, None, None)
    result = evaluate(observed(), prior)
    assert {f.name for f in fields(TemporalGuardFacts)} == expected
    assert len(fields(Prior)) == 3
    for instance in (prior, result):
        assert not hasattr(instance, "__dict__")
        for f in fields(instance):
            with pytest.raises(FrozenInstanceError):
                setattr(instance, f.name, None)
            with pytest.raises(FrozenInstanceError):
                delattr(instance, f.name)


def test_no_runtime_io_clock_random_or_upstream_reruns(monkeypatch):
    import bb_host_preflight_m0
    import bb_host_virtual_ticks
    import bb_host_batch_observations
    observation = observed(5000, control(), event("RF_HEALTHY", 5000, "rf"))
    prior = Prior(0, None, None)
    expected = evaluate(observation, prior)
    def forbidden(*args, **kwargs):
        raise AssertionError("prohibited side effect or upstream rerun")
    with monkeypatch.context() as m:
        for module, names in ((builtins, ("open",)), (time, ("time", "monotonic", "sleep")),
                              (random, ("random",)), (socket, ("socket",)),
                              (bb_host_preflight_m0, ("validate_wire", "mixM0", "mix_m0")),
                              (bb_host_virtual_ticks, ("iter_virtual_ticks",)),
                              (bb_host_batch_observations, ("normalize_tick_observations",))):
            for name in names:
                m.setattr(module, name, forbidden)
        assert evaluate(observation, prior) == expected


def test_static_import_and_call_boundary():
    package = Path(runtime.__file__).parent
    allowed = {"dataclasses", "types", "bb_host_batch_observations", "temporal"}
    prohibited = {"open", "print", "eval", "exec", "compile", "__import__", "float", "time", "sleep",
                  "mix_m0", "mixM0", "normalize_tick_observations", "iter_virtual_ticks", "validate_wire"}
    for file in package.glob("*.py"):
        tree = ast.parse(file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(a.name in allowed for a in node.names)
            if isinstance(node, ast.ImportFrom):
                assert node.module in allowed
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
                assert name not in prohibited


def test_large_rf_scan_is_linear_and_checks_last_timestamp(monkeypatch):
    observation = observed(5000, *(event("RF_HEALTHY", 4999, str(i)) for i in range(5000)))
    calls = []
    original = runtime._original_time
    def counted(value, tick):
        calls.append(value)
        return original(value, tick)
    monkeypatch.setattr(runtime, "_original_time", counted)
    result = evaluate(observation, Prior(0, None, None))
    assert len(calls) == 5000
    assert result.observed_uncontested_healthy_rf_at_us == 4999
    bad_last = MappingProxyType(dict(observation.rf_events[-1], event_at_us=5001))
    with pytest.raises(ValueError):
        evaluate(replace(observation, rf_events=observation.rf_events[:-1] + (bad_last,)), Prior(0, None, None))


def test_no_source_or_group_rescan():
    observation = observed(5000, *(control(4999, str(i), flap=f"0.{i:03}") for i in range(1000)))
    lines = 0
    def trace(frame, action, arg):
        nonlocal lines
        if frame.f_code.co_filename == runtime.__file__ and action == "line":
            lines += 1
        return trace
    old = sys.gettrace()
    try:
        sys.settrace(trace)
        result = evaluate(observation, Prior(0, None, None))
    finally:
        sys.settrace(old)
    assert result.has_valid_control_conflict
    assert lines < 300  # independent of 1000 original controls/groups


def test_repeat_determinism_under_locale_decimal_and_tz(monkeypatch):
    observation = observed(205000, control(204999))
    prior = Prior(200000, 4999, 5000)
    expected = asdict(evaluate(observation, prior))
    previous = locale.setlocale(locale.LC_ALL)
    try:
        for name in ("C", "English_United States.1252"):
            locale.setlocale(locale.LC_ALL, name)
            for tz in ("UTC0", "ICT-7"):
                monkeypatch.setenv("TZ", tz)
                with localcontext() as ctx:
                    ctx.prec = 2
                    assert asdict(evaluate(observation, prior)) == expected
    finally:
        locale.setlocale(locale.LC_ALL, previous)
