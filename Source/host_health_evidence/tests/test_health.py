"""Malformed callers are synthetic negatives, never authenticated inputs."""

import ast
import builtins
from copy import deepcopy
from dataclasses import replace
from decimal import localcontext
from enum import Enum
import inspect
import locale
from pathlib import Path
import random
import socket
import sys
import time
from types import MappingProxyType as MP

import pytest

import bb_host_health_evidence.health as runtime
from bb_host_health_evidence import (assess_health_evidence as assess, RFStatus,
                                    RFEvidenceKind as RF, ControlEvidenceKind as Control)
from bb_host_preflight_m0 import RejectedPreflight, validate_wire
from bb_host_safety_priority_kernel import SafetyState
from scripts.scenarios import load_oracles, pipeline, wire_bytes, DESIGN

CASES = load_oracles()["cases"]


def inputs(number=21):
    _, _, obs, _, temporal, priority, prior = pipeline(CASES[number - 1])
    return obs, temporal, priority, prior


def rebuild(recipe):
    _, _, obs, _, temporal, priority, prior = pipeline(recipe)
    return assess(obs, temporal, priority, prior)


@pytest.mark.parametrize("position", range(4))
@pytest.mark.parametrize("bad", [None, {}, [], True, "record", 1])
def test_wrong_top_level_types(position, bad):
    args = list(inputs())
    args[position] = bad
    with pytest.raises(TypeError):
        assess(*args)


@pytest.mark.parametrize("position", range(4))
def test_record_subclass_rejected(position):
    args = list(inputs())
    record = args[position]
    subclass = type("ForgedSubclass", (type(record),), {})
    args[position] = subclass(**{name: getattr(record, name) for name in record.__dataclass_fields__})
    with pytest.raises(TypeError):
        assess(*args)


@pytest.mark.parametrize("position", range(3))
@pytest.mark.parametrize("name,bad", [("tick_index", True), ("tick_index", -1), ("tick_index", 12001),
                                    ("tick_index", 2), ("eval_at_us", True), ("eval_at_us", 4999),
                                    ("eval_at_us", 60000001), ("eval_at_us", float("nan")),
                                    ("eval_at_us", 5000.0)])
def test_mismatched_ticks(position, name, bad):
    args = list(inputs())
    args[position] = replace(args[position], **{name: bad})
    with pytest.raises((TypeError, ValueError)):
        assess(*args)


@pytest.mark.parametrize("name,bad", [
    ("last_committed_eval_at_us", None), ("last_committed_eval_at_us", True),
    ("last_committed_eval_at_us", -1), ("last_committed_eval_at_us", 1),
    ("last_committed_eval_at_us", 5000), ("last_committed_eval_at_us", float("inf")),
    ("last_rf_status", "HEALTHY"), ("last_rf_status", RFStatus.HEALTHY),
    ("last_rf_original_at_us", 0), ("last_rf_original_at_us", True)])
def test_bad_prior_pair_or_commit(name, bad):
    obs, temporal, priority, prior = inputs()
    with pytest.raises((TypeError, ValueError)):
        assess(obs, temporal, priority, replace(prior, **{name: bad}))


@pytest.mark.parametrize("at", [True, -1, 5001, 200001, 5000.0, float("nan")])
def test_healthy_timestamp_mismatch(at):
    obs, temporal, priority, prior = inputs(12)
    with pytest.raises((TypeError, ValueError)):
        assess(obs, temporal, priority, replace(prior, last_rf_original_at_us=at))


def test_fake_enums_and_missing_rf_with_old_healthy_age():
    obs, temporal, priority, prior = inputs(12)
    class Fake(str, Enum):
        HEALTHY = "HEALTHY"
    with pytest.raises(TypeError):
        assess(obs, temporal, priority, replace(prior, last_rf_status=Fake.HEALTHY))
    with pytest.raises(TypeError):
        assess(obs, temporal, replace(priority, pre_state="DISARMED"), prior)
    with pytest.raises(ValueError):
        assess(obs, temporal, priority, replace(prior, last_rf_status=None, last_rf_original_at_us=None))


@pytest.mark.parametrize("name,value", [("last_committed_eval_at_us", 0), ("last_rf_status", RFStatus.HEALTHY),
                                      ("last_rf_original_at_us", 0)])
def test_t0_has_no_prior_history(name, value):
    obs, temporal, priority, prior = inputs(1)
    with pytest.raises(ValueError):
        assess(obs, temporal, priority, replace(prior, **{name: value}))


@pytest.mark.parametrize("name", runtime._FLAGS)
def test_bool_flags_require_exact_bool(name):
    obs, temporal, priority, prior = inputs()
    with pytest.raises(ValueError):
        assess(replace(obs, **{name: int(getattr(obs, name))}), temporal, priority, prior)


@pytest.mark.parametrize("name", ["source_events", "causal_event_ids", "valid_control_groups", "rf_events", "invalid_control_event_ids"])
def test_mutable_outer_collections_rejected(name):
    obs, temporal, priority, prior = inputs()
    with pytest.raises(ValueError):
        assess(replace(obs, **{name: list(getattr(obs, name))}), temporal, priority, prior)


@pytest.mark.parametrize("name", ["has_rf_lost_observation", "has_rf_unknown_observation", "has_invalid_control_observation", "has_valid_control_conflict"])
@pytest.mark.parametrize("bad", [True, 0])
def test_temporal_mirrors(name, bad):
    obs, temporal, priority, prior = inputs()
    with pytest.raises(ValueError):
        assess(obs, replace(temporal, **{name: bad}), priority, prior)


@pytest.mark.parametrize("channel", ["rf", "control"])
@pytest.mark.parametrize("bad", [True, -1, 0, 4999, 5001, 5000.0, float("inf")])
def test_bad_ages_and_timeout_mirror(channel, bad):
    obs, temporal, priority, prior = inputs()
    with pytest.raises(ValueError):
        assess(obs, replace(temporal, **{f"prior_{channel}_age_us": bad}), priority, prior)


@pytest.mark.parametrize("channel", ["rf", "control"])
@pytest.mark.parametrize("bad", [True, 0])
def test_timeout_bool(channel, bad):
    obs, temporal, priority, prior = inputs()
    with pytest.raises(ValueError):
        assess(obs, replace(temporal, **{f"prior_{channel}_within_timeout": bad}), priority, prior)


@pytest.mark.parametrize("name", ["observed_uncontested_valid_control_at_us", "observed_uncontested_healthy_rf_at_us"])
@pytest.mark.parametrize("bad", [None, True, 0, 5001, 4997, 4999.0])
def test_candidate_cross_checks(name, bad):
    obs, temporal, priority, prior = inputs()
    with pytest.raises(ValueError):
        assess(obs, replace(temporal, **{name: bad}), priority, prior)


@pytest.mark.parametrize("mode", ["mutable", "payload_mutable", "missing", "extra", "payload_extra", "bad_kind", "bool_time",
                                 "before_tick", "after_tick", "status", "enum_status", "provenance", "id", "bad_payload"])
def test_rf_records_are_immutable_and_exact(mode):
    obs, temporal, priority, prior = inputs()
    event = dict(obs.rf_events[0]); body = dict(event["payload"])
    if mode == "mutable":
        replacement = event
    else:
        if mode == "missing": del event["event_id"]
        elif mode == "extra": event["approved"] = True
        elif mode == "payload_extra": body["approved"] = True
        elif mode == "bad_kind": event["type"] = "SIM_CONTROL_FRAME"
        elif mode == "bool_time": event["event_at_us"] = True
        elif mode == "before_tick": event["event_at_us"] = 0
        elif mode == "after_tick": event["event_at_us"] = 5001
        elif mode == "status": body["rf_health"] = "BAD"
        elif mode == "enum_status": body["rf_health"] = RFStatus.HEALTHY
        elif mode == "provenance": body["rf_provenance"] = "REAL_RF"
        elif mode == "id": event["event_id"] = False
        event["payload"] = body if mode == "payload_mutable" else MP(body)
        if mode == "bad_payload": event["payload"] = None
        replacement = MP(event)
    with pytest.raises((TypeError, ValueError)):
        assess(replace(obs, rf_events=(replacement,)), temporal, priority, prior)


@pytest.mark.parametrize("name", ["rf_has_healthy", "rf_has_lost", "rf_has_unknown"])
def test_rf_presence_mismatch(name):
    obs, temporal, priority, prior = inputs()
    with pytest.raises(ValueError):
        assess(replace(obs, **{name: not getattr(obs, name)}), temporal, priority, prior)


@pytest.mark.parametrize("number", [1, 19, 20, 25, 26, 27, 28, 30, 34, 35, 36])
def test_cannot_invert_priority_blocker(number):
    obs, temporal, priority, prior = inputs(number)
    assert priority.blocks_control_qualification
    with pytest.raises(ValueError):
        assess(obs, temporal, replace(priority, blocks_control_qualification=False), prior)


@pytest.mark.parametrize("changes", [dict(requires_full_fsm=False), dict(requires_full_fsm=1),
    dict(blocks_control_qualification=0), dict(blocks_control_qualification=True),
    dict(provisional_next_state=SafetyState.SELF_TEST), dict(priority_category="ORDINARY_RESET"),
    dict(pre_state=SafetyState.BOOT)])
def test_priority_shape_and_consistency(changes):
    obs, temporal, priority, prior = inputs()
    with pytest.raises((TypeError, ValueError)):
        assess(obs, temporal, replace(priority, **changes), prior)


@pytest.mark.parametrize("changes", [dict(latest_original_at_us=True), dict(latest_original_at_us=4998),
    dict(semantic_control={}), dict(member_events=[]), dict(member_events=()), dict(event_ids=[]), dict(event_ids=())])
def test_one_group_shape_and_candidate(changes):
    obs, temporal, priority, prior = inputs()
    group = replace(obs.valid_control_groups[0], **changes)
    with pytest.raises(ValueError):
        assess(replace(obs, valid_control_groups=(group,)), temporal, priority, prior)


@pytest.mark.parametrize("name", ["has_invalid_control", "has_distinct_valid_control_conflict", "has_duplicate_semantic_control"])
def test_control_group_flag_mismatch(name):
    obs, temporal, priority, prior = inputs()
    with pytest.raises(ValueError):
        assess(replace(obs, **{name: True}), temporal, priority, prior)


@pytest.mark.parametrize("number,expected", [(14, RF.LOST_CARRIED), (15, RF.UNKNOWN_CARRIED), (33, RF.UNKNOWN_CARRIED)])
def test_nonhealthy_prior_never_promoted_by_old_healthy_age(number, expected):
    obs, temporal, priority, prior = inputs(number)
    assert assess(obs, temporal, priority, prior).rf_evidence is expected


@pytest.mark.parametrize("prior_status", [None, "HEALTHY", "LOST", "UNKNOWN"])
@pytest.mark.parametrize("order", [("HEALTHY", "UNKNOWN"), ("UNKNOWN", "HEALTHY"), ("HEALTHY", "LOST"), ("LOST", "HEALTHY")])
def test_mixed_rf_order_and_prior_cannot_rescue(prior_status, order):
    recipe = deepcopy(CASES[24])
    for e in recipe["pseudo_events"]:
        e["event_at_us"] += 5000 if e["kind"] != "BOOT" else 0
    recipe["eval_at_us"] = 10000
    recipe["prior_timestamp_snapshot"] = dict(last_committed_eval_at_us=5000, last_accepted_control_at_us=None,
        last_uncontested_healthy_rf_at_us=4999 if prior_status is not None else None)
    recipe["prior_rf_snapshot"] = dict(last_committed_eval_at_us=5000, last_rf_status=prior_status,
        last_rf_original_at_us=4999 if prior_status is not None else None)
    rf = [e for e in recipe["pseudo_events"] if e["kind"].startswith("RF_")]
    for e, status in zip(rf, order): e["kind"] = "RF_" + status
    result = rebuild(recipe)
    assert result.rf_evidence is (RF.LOST_CURRENT if "LOST" in order else RF.AMBIGUOUS_CURRENT)
    assert result.control_evidence is (Control.BLOCKED_RF if "LOST" in order else Control.DEFER_RF_AMBIGUOUS)


@pytest.mark.parametrize("age,kind", [(199999, RF.HEALTHY_CARRIED), (200000, RF.HEALTHY_CARRIED), (200001, RF.STALE_PRIOR)])
def test_inclusive_rf_age_boundary(age, kind):
    recipe = deepcopy(CASES[22])
    at = recipe["eval_at_us"] - age
    recipe["prior_rf_snapshot"]["last_rf_original_at_us"] = at
    recipe["prior_timestamp_snapshot"]["last_uncontested_healthy_rf_at_us"] = at
    assert rebuild(recipe).rf_evidence is kind


@pytest.mark.parametrize("state", ["ARM_CHECK", "ARMED_IDLE", "ACTUATION_ACTIVE"])
@pytest.mark.parametrize("channel", ["rf", "control"])
def test_armed_stale_prior_stays_blocked_with_fresh_current(state, channel):
    recipe = deepcopy(CASES[31]); recipe["pre_state"] = state
    recipe["prior_timestamp_snapshot"]["last_accepted_control_at_us"] = 5000
    recipe["prior_timestamp_snapshot"]["last_uncontested_healthy_rf_at_us"] = 5000
    recipe["prior_rf_snapshot"]["last_rf_original_at_us"] = 5000
    if channel == "rf":
        recipe["prior_rf_snapshot"]["last_rf_original_at_us"] = 4999
        recipe["prior_timestamp_snapshot"]["last_uncontested_healthy_rf_at_us"] = 4999
    else:
        recipe["prior_timestamp_snapshot"]["last_accepted_control_at_us"] = 4999
    result = rebuild(recipe)
    assert result.rf_evidence is RF.HEALTHY_CURRENT and result.control_evidence is Control.BLOCKED_PRIORITY


@pytest.mark.parametrize("state", ["CONTINGENCY", "FAULT_LATCHED"])
def test_restricted_states_block_even_with_ack(state):
    recipe = deepcopy(CASES[20]); recipe["pre_state"] = state
    recipe["pseudo_events"].append(dict(id="ack", event_at_us=5000, kind="ACK"))
    assert rebuild(recipe).control_evidence is Control.BLOCKED_PRIORITY


def test_current_recovery_does_not_persist_history_or_cross_refresh():
    _, _, obs, prior_time, temporal, priority, prior = pipeline(CASES[16])
    before = (repr(prior), repr(prior_time), repr(temporal))
    assert assess(obs, temporal, priority, prior).rf_evidence is RF.HEALTHY_CURRENT
    silent = deepcopy(CASES[16]); silent["pseudo_events"] = silent["pseudo_events"][:1]
    assert rebuild(silent).rf_evidence is RF.LOST_CARRIED
    assert before == (repr(prior), repr(prior_time), repr(temporal))
    # A current candidate does not fabricate a prior accepted-control timestamp.
    obs, temporal, priority, prior = inputs(21)
    assert temporal.prior_control_age_us is None
    assert assess(obs, temporal, priority, prior).control_evidence is Control.SINGLE_CANDIDATE
    assert temporal.prior_control_age_us is None


@pytest.mark.parametrize("key,value", [("approved", True), ("health", "PASS"), ("control", "ADMITTED"),
                                      ("pre_state", "ARMED_IDLE"), ("prior_rf_snapshot", {})])
def test_wire_cannot_supply_permissions(key, value):
    import json
    raw = json.loads(wire_bytes(CASES[20]))
    schema = json.loads((DESIGN / "contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_bytes())
    raw[key] = value
    assert type(validate_wire(json.dumps(raw).encode(), schema)) is RejectedPreflight


def test_no_control_source_or_member_scan():
    obs, temporal, priority, prior = inputs(31)
    poison = object()
    group = replace(obs.valid_control_groups[0], member_events=(poison, poison))
    altered = replace(obs, source_events=(poison,), causal_event_ids=(poison,), valid_control_groups=(group,))
    assert assess(altered, temporal, priority, prior) == assess(obs, temporal, priority, prior)


def line_cost(args):
    count = 0
    def trace(frame, event, arg):
        nonlocal count
        if event == "line" and frame.f_code.co_filename == runtime.__file__: count += 1
        return trace
    previous = sys.gettrace()
    try:
        sys.settrace(trace); assess(*args)
    finally:
        sys.settrace(previous)
    return count


def test_cost_constant_in_control_count_linear_in_rf_count():
    def arguments(control_count, rf_count):
        recipe = deepcopy(CASES[20]); recipe["pseudo_events"] = [recipe["pseudo_events"][0]]
        recipe["pseudo_events"] += [dict(id=f"c{i}", event_at_us=4999, kind="CONTROL_VALID", arm=False, flap="0", steer="0") for i in range(control_count)]
        recipe["pseudo_events"] += [dict(id=f"r{i}", event_at_us=4999, kind="RF_HEALTHY") for i in range(rf_count)]
        _, _, obs, _, temporal, priority, prior = pipeline(recipe)
        return obs, temporal, priority, prior
    assert line_cost(arguments(1, 1)) == line_cost(arguments(5000, 1))
    a, b, c = (line_cost(arguments(1, n)) for n in (1, 101, 201))
    assert 0 < b - a == c - b


def test_no_io_clocks_random_or_upstream_reruns(monkeypatch):
    args = inputs()
    expected = assess(*args)
    def forbidden(*args, **kwargs): raise AssertionError("forbidden side effect/upstream call")
    import bb_host_preflight_m0, bb_host_virtual_ticks, bb_host_batch_observations
    import bb_host_temporal_guard_facts, bb_host_safety_priority_kernel
    with monkeypatch.context() as m:
        for obj, name in [(builtins, "open"), (Path, "open"), (time, "time"), (time, "monotonic"),
                          (time, "perf_counter"), (time, "sleep"), (random, "random"), (socket, "socket"),
                          (bb_host_preflight_m0, "validate_wire"), (bb_host_preflight_m0, "mix_m0"),
                          (bb_host_virtual_ticks, "iter_virtual_ticks"), (bb_host_batch_observations, "normalize_tick_observations"),
                          (bb_host_temporal_guard_facts, "evaluate_temporal_guard_facts"), (bb_host_safety_priority_kernel, "assess_safety_priority")]:
            m.setattr(obj, name, forbidden)
        assert assess(*args) == expected


def test_runtime_imports_and_forbidden_api_surface():
    tree = ast.parse(inspect.getsource(runtime))
    modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert modules <= {"dataclasses", "enum", "types", "bb_host_batch_observations", "bb_host_temporal_guard_facts", "bb_host_safety_priority_kernel"}
    assert not any(isinstance(node, ast.Import) for node in ast.walk(tree))
    result = assess(*inputs())
    for name in ("can_arm", "health", "control", "approved", "accepted_control_at_us", "rf_effective", "output_allowed", "post_state", "state_after", "reason_codes"):
        assert not hasattr(result, name)


@pytest.mark.parametrize("locale_name", ["C", "English_United States.1252"])
@pytest.mark.parametrize("tz", ["UTC0", "ICT-7"])
@pytest.mark.parametrize("precision", [2, 28])
def test_locale_tz_decimal_determinism(locale_name, tz, precision, monkeypatch):
    expected = [rebuild(c) for c in CASES]
    previous = locale.setlocale(locale.LC_ALL)
    try:
        locale.setlocale(locale.LC_ALL, locale_name)
        monkeypatch.setenv("TZ", tz)
        with localcontext() as ctx:
            ctx.prec = precision
            assert [rebuild(c) for c in CASES] == expected
    finally:
        locale.setlocale(locale.LC_ALL, previous)
