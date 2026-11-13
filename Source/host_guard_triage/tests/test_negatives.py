"""P220 N01..N18: adversarial callers, continuity and structural boundaries."""

import ast
import builtins
from copy import deepcopy
from dataclasses import fields, FrozenInstanceError, replace
from decimal import localcontext
from enum import Enum
import inspect
import json
import locale
from pathlib import Path
import random
import socket
import sys
import time

import pytest

import bb_host_guard_triage.triage as runtime
from bb_host_guard_triage import (triage_guard_evidence as triage, GuardReason as Reason,
                                  RFGuardLane as RF, ControlGuardLane as Control,
                                  ArmedContinuityLane as Continuity)
from bb_host_health_evidence import RFEvidenceKind, ControlEvidenceKind
from bb_host_preflight_m0 import RejectedPreflight, validate_wire
from bb_host_safety_priority_kernel import SafetyState
from scripts.scenarios import load_source_oracles, load_oracles, pipeline, wire_bytes, DESIGN

RECIPES = load_source_oracles()["cases"]
FORBIDDEN = ("health", "control", "approved", "rf_effective", "can_arm", "output_allowed", "state_after",
             "post_state", "accepted_control_at_us", "accepted_rf_at_us", "control_accepted", "reason_codes",
             "left_micro_effort", "right_micro_effort", "trace_ack")


def args_for(recipe):
    _, _, obs, _, temporal, priority, _, health = pipeline(recipe)
    return obs, temporal, priority, health


def inputs(number=21):
    return args_for(RECIPES[number - 1])


def armed_recipe(state="ACTUATION_ACTIVE", control_age=200000, rf_age=200000):
    recipe = deepcopy(RECIPES[31])
    recipe["pre_state"] = state
    recipe["prior_timestamp_snapshot"].update(
        last_accepted_control_at_us=None if control_age is None else 205000 - control_age,
        last_uncontested_healthy_rf_at_us=None if rf_age is None else 205000 - rf_age)
    recipe["prior_rf_snapshot"].update(last_rf_status=None if rf_age is None else "HEALTHY",
        last_rf_original_at_us=None if rf_age is None else 205000 - rf_age)
    return recipe


@pytest.mark.parametrize("position", range(4))
@pytest.mark.parametrize("bad", [None, {}, [], True, "record", 1])
def test_N01_wrong_exact_classes(position, bad):
    args = list(inputs()); args[position] = bad
    with pytest.raises(TypeError): triage(*args)


@pytest.mark.parametrize("position", range(4))
def test_N01_subclass_is_not_upstream_type(position):
    args = list(inputs()); obj = args[position]
    subclass = type("ForgedSubclass", (type(obj),), {})
    args[position] = subclass(**{f.name: getattr(obj, f.name) for f in fields(obj)})
    with pytest.raises(TypeError): triage(*args)


@pytest.mark.parametrize("position", range(4))
@pytest.mark.parametrize("name,bad", [("tick_index", True), ("tick_index", -1), ("tick_index", 12001),
    ("tick_index", 2), ("eval_at_us", True), ("eval_at_us", 4999), ("eval_at_us", 60000001),
    ("eval_at_us", 5000.0), ("eval_at_us", float("inf")), ("eval_at_us", float("nan"))])
def test_N01_tick_domain_and_mirrors(position, name, bad):
    args = list(inputs()); args[position] = replace(args[position], **{name: bad})
    with pytest.raises((TypeError, ValueError)): triage(*args)


@pytest.mark.parametrize("field,value", [("pre_state", "DISARMED"), ("rf_evidence", "HEALTHY_CURRENT"),
                                        ("control_evidence", "SINGLE_CANDIDATE")])
def test_N01_strings_and_fake_enums_rejected(field, value):
    args = list(inputs())
    for bad in (value, Enum("Fake", {value: value}, type=str)[value]):
        args[3] = replace(inputs()[3], **{field: bad})
        with pytest.raises(TypeError): triage(*args)


@pytest.mark.parametrize("number", [1, 4, 5, 7, 8, 10, 11, 12, 14, 16, 25, 26, 33, 34])
def test_N02_forged_healthy_current(number):
    obs, temporal, priority, health = inputs(number)
    with pytest.raises(ValueError):
        triage(obs, temporal, priority, replace(health, rf_evidence=RFEvidenceKind.HEALTHY_CURRENT))


@pytest.mark.parametrize("number", [1, 2, 5, 8, 13, 16, 17, 18, 21, 24, 32])
def test_N03_forged_healthy_carried(number):
    obs, temporal, priority, health = inputs(number)
    with pytest.raises(ValueError):
        triage(obs, temporal, priority, replace(health, rf_evidence=RFEvidenceKind.HEALTHY_CARRIED))


@pytest.mark.parametrize("number", [1, 2, 4, 5, 6, 7, 10, 11, 12, 16, 21, 26])
def test_N04_forged_ambiguous_without_healthy_unknown(number):
    obs, temporal, priority, health = inputs(number)
    with pytest.raises(ValueError):
        triage(obs, temporal, priority, replace(health, rf_evidence=RFEvidenceKind.AMBIGUOUS_CURRENT))


@pytest.mark.parametrize("number", [1, 2, 19, 20, 22, 24, 25, 26, 27, 28, 30, 34, 35, 36])
def test_N05_forged_single_candidate(number):
    obs, temporal, priority, health = inputs(number)
    with pytest.raises(ValueError):
        triage(obs, temporal, priority, replace(health, control_evidence=ControlEvidenceKind.SINGLE_CANDIDATE))


@pytest.mark.parametrize("number", [1, 2, 13, 16, 19, 20, 22, 24, 25, 26, 27, 28, 30, 35, 36])
def test_N06_negative_evidence_has_no_positive_authority(number):
    result = triage(*inputs(number))
    assert result.requires_full_fsm and result.unresolved_reasons[-1] is Reason.TRUST_NOT_PROVEN
    assert all(not hasattr(result, name) for name in FORBIDDEN)
    assert not any(label.value in ("PASS", "ADMITTED", "ACTIVE") for label in (result.rf_lane, result.control_lane, result.armed_continuity_lane))


@pytest.mark.parametrize("field,bad", [("latest_current_rf_original_at_us", None), ("latest_current_rf_original_at_us", 4997),
    ("latest_current_rf_original_at_us", True), ("latest_current_rf_original_at_us", 0),
    ("latest_current_rf_original_at_us", 5001), ("observed_control_candidate_original_at_us", None),
    ("observed_control_candidate_original_at_us", 4998), ("observed_control_candidate_original_at_us", True),
    ("pre_state", SafetyState.ARMED_IDLE), ("requires_full_fsm", False), ("requires_full_fsm", 1)])
def test_N07_d1_timestamp_state_and_marker_mirrors(field, bad):
    obs, temporal, priority, health = inputs()
    with pytest.raises((TypeError, ValueError)): triage(obs, temporal, priority, replace(health, **{field: bad}))


@pytest.mark.parametrize("field", runtime._FLAGS)
def test_N07_observation_flags_are_exact_bool(field):
    obs, temporal, priority, health = inputs()
    with pytest.raises(ValueError): triage(replace(obs, **{field: int(getattr(obs, field))}), temporal, priority, health)


@pytest.mark.parametrize("field", ["has_rf_lost_observation", "has_rf_unknown_observation", "has_invalid_control_observation", "has_valid_control_conflict"])
@pytest.mark.parametrize("bad", [True, 0])
def test_N07_temporal_flag_mirrors(field, bad):
    obs, temporal, priority, health = inputs()
    with pytest.raises(ValueError): triage(obs, replace(temporal, **{field: bad}), priority, health)


@pytest.mark.parametrize("field", ["source_events", "causal_event_ids", "valid_control_groups", "invalid_control_event_ids", "rf_events"])
def test_N07_mutable_collections(field):
    obs, temporal, priority, health = inputs()
    with pytest.raises(ValueError): triage(replace(obs, **{field: list(getattr(obs, field))}), temporal, priority, health)


@pytest.mark.parametrize("channel", ["rf", "control"])
@pytest.mark.parametrize("bad", [True, -1, 0, 4999, 5001, 5000.0, float("nan")])
def test_N07_prior_age_type_domain_or_freshness_mirror(channel, bad):
    obs, temporal, priority, health = inputs()
    with pytest.raises(ValueError): triage(obs, replace(temporal, **{f"prior_{channel}_age_us": bad}), priority, health)


@pytest.mark.parametrize("number", [1, 19, 20, 25, 26, 27, 28, 30, 35, 36])
def test_N07_c1_blocker_cannot_be_inverted(number):
    obs, temporal, priority, health = inputs(number)
    assert priority.blocks_control_qualification
    with pytest.raises(ValueError): triage(obs, temporal, replace(priority, blocks_control_qualification=False), health)


@pytest.mark.parametrize("change", [dict(provisional_next_state=SafetyState.SELF_TEST), dict(priority_category="ORDINARY_RESET"),
    dict(requires_full_fsm=False), dict(requires_full_fsm=1), dict(blocks_control_qualification=0),
    dict(pre_state=SafetyState.BOOT), dict(pre_state="DISARMED")])
def test_N07_c1_shape_and_prestate(change):
    obs, temporal, priority, health = inputs()
    with pytest.raises((TypeError, ValueError)): triage(obs, temporal, replace(priority, **change), health)


@pytest.mark.parametrize("state", ["ARM_CHECK", "ARMED_IDLE", "ACTUATION_ACTIVE"])
@pytest.mark.parametrize("channel", ["rf", "control"])
@pytest.mark.parametrize("age", [199999, 200000, 200001])
def test_N08_independent_inclusive_boundaries(state, channel, age):
    recipe = armed_recipe(state, **{channel + "_age": age})
    args = args_for(recipe); before = repr(args[1])
    result = triage(*args)
    assert getattr(args[1], f"prior_{channel}_age_us") == age
    assert result.rf_lane is RF.CURRENT_HEALTHY_UNCOMMITTED
    assert result.armed_continuity_lane is (Continuity.POTENTIAL_S1_UNVERIFIED if age <= 200000 else Continuity.PRIOR_STALE_OR_MISSING)
    assert result.current_control_candidate_original_at_us == 204999
    assert result.current_rf_candidate_original_at_us == 204998
    assert repr(args[1]) == before  # Current originals do not refresh either age.


@pytest.mark.parametrize("state", ["ARM_CHECK", "ARMED_IDLE", "ACTUATION_ACTIVE"])
@pytest.mark.parametrize("current_rf", [False, True])
def test_N09_no_frame_potential_s1_is_unverified(state, current_rf):
    recipe = armed_recipe(state)
    recipe["pseudo_events"] = [e for e in recipe["pseudo_events"] if e["kind"] == "BOOT" or (current_rf and e["kind"].startswith("RF_"))]
    result = triage(*args_for(recipe))
    assert result.armed_continuity_lane is Continuity.POTENTIAL_S1_UNVERIFIED
    assert result.control_lane is Control.NO_CANDIDATE and result.current_control_candidate_original_at_us is None
    assert result.unresolved_reasons == (Reason.NO_UNCONTESTED_CONTROL, Reason.TRUST_NOT_PROVEN)
    assert all(not hasattr(result, name) for name in FORBIDDEN)


@pytest.mark.parametrize("age", [None, 200001, 205000])
@pytest.mark.parametrize("state", ["ARM_CHECK", "ARMED_IDLE", "ACTUATION_ACTIVE"])
def test_N10_current_valid_cannot_rescue_prior_control(state, age):
    result = triage(*args_for(armed_recipe(state, control_age=age)))
    assert result.armed_continuity_lane is Continuity.PRIOR_STALE_OR_MISSING
    assert result.control_lane is Control.PRIORITY_BLOCKED
    assert result.unresolved_reasons == (Reason.ARMED_PRIOR_CONTROL_STALE_OR_MISSING, Reason.TRUST_NOT_PROVEN)


@pytest.mark.parametrize("age", [None, 200001, 205000])
@pytest.mark.parametrize("state", ["ARM_CHECK", "ARMED_IDLE", "ACTUATION_ACTIVE"])
def test_N11_current_healthy_cannot_rescue_prior_rf(state, age):
    result = triage(*args_for(armed_recipe(state, rf_age=age)))
    assert result.armed_continuity_lane is Continuity.PRIOR_STALE_OR_MISSING
    assert result.control_lane is Control.PRIORITY_BLOCKED
    assert result.unresolved_reasons == (Reason.ARMED_PRIOR_RF_STALE_OR_MISSING, Reason.TRUST_NOT_PROVEN)


@pytest.mark.parametrize("status", ["LOST", "UNKNOWN", "AMBIGUOUS"])
@pytest.mark.parametrize("state", ["ARM_CHECK", "ARMED_IDLE", "ACTUATION_ACTIVE"])
def test_N12_armed_fresh_but_current_hazard(state, status):
    recipe = armed_recipe(state)
    for event in recipe["pseudo_events"]:
        if event["kind"].startswith("RF_"): event["kind"] = "RF_" + ("UNKNOWN" if status == "AMBIGUOUS" else status)
    if status == "AMBIGUOUS": recipe["pseudo_events"].append(dict(id="healthy", kind="RF_HEALTHY", event_at_us=204999))
    result = triage(*args_for(recipe))
    assert result.armed_continuity_lane is Continuity.HAZARD_OR_UNRESOLVED
    assert result.rf_lane is (RF.AMBIGUOUS if status == "AMBIGUOUS" else RF.NOT_HEALTHY)


@pytest.mark.parametrize("channel", ["rf", "control", "both"])
def test_N12_reset_never_erases_prior_stale(channel):
    recipe = armed_recipe(control_age=200001 if channel in ("control", "both") else 200000,
                          rf_age=200001 if channel in ("rf", "both") else 200000)
    recipe["pseudo_events"].append(dict(id="reset", kind="RESET", event_at_us=205000))
    result = triage(*args_for(recipe))
    assert result.armed_continuity_lane is Continuity.PRIOR_STALE_OR_MISSING
    assert result.unresolved_reasons[0] is Reason.PRIORITY_BLOCKED


@pytest.mark.parametrize("state", ["SELF_TEST", "DISARMED", "CONTINGENCY", "FAULT_LATCHED"])
def test_N12_other_states_are_not_armed(state):
    recipe = armed_recipe(state, control_age=200001, rf_age=200001)
    result = triage(*args_for(recipe))
    assert result.armed_continuity_lane is Continuity.NOT_ARMED
    assert (Reason.PRIORITY_BLOCKED in result.unresolved_reasons) == (state in ("CONTINGENCY", "FAULT_LATCHED"))


def line_cost(args):
    count = 0
    def trace(frame, event, arg):
        nonlocal count
        if event == "line" and frame.f_code.co_filename == runtime.__file__: count += 1
        return trace
    previous = sys.gettrace()
    try:
        sys.settrace(trace); triage(*args)
    finally:
        sys.settrace(previous)
    return count


def bulk_args(controls, rf):
    recipe = deepcopy(RECIPES[20]); recipe["pseudo_events"] = recipe["pseudo_events"][:1]
    recipe["pseudo_events"] += [dict(id=f"c{i}", kind="CONTROL_VALID", event_at_us=4999, arm=False, flap="0.1", steer="0") for i in range(controls)]
    recipe["pseudo_events"] += [dict(id=f"r{i}", kind="RF_HEALTHY", event_at_us=4999) for i in range(rf)]
    return args_for(recipe)


def test_N13_constant_work_zero_one_5000_controls():
    counts = [line_cost(bulk_args(n, 0)) for n in (0, 1, 5000)]
    assert len(set(counts)) == 1, counts


def test_N14_constant_work_one_5000_rf_and_no_nested_rescan():
    small, large = bulk_args(1, 1), bulk_args(5000, 5000)
    assert line_cost(small) == line_cost(large)
    obs, temporal, priority, health = large
    poison = object()
    altered = replace(obs, source_events=(poison,), causal_event_ids=(poison,), rf_events=(poison,), valid_control_groups=(poison,))
    assert triage(altered, temporal, priority, health) == triage(*large)
    # D2 only cross-checks metadata. This is NOT proof that forged wrappers are trusted.


def test_N15_closed_enums_exact_fields_and_frozen_reason_order():
    assert [x.value for x in RF] == ["CURRENT_HEALTHY_UNCOMMITTED", "CARRIED_HEALTHY_UNVERIFIED", "AMBIGUOUS", "NOT_HEALTHY"]
    assert [x.value for x in Control] == ["NO_CANDIDATE", "UNTRUSTED_CANDIDATE", "INVALID_OR_CONFLICT", "RF_BLOCKED", "RF_AMBIGUOUS", "PRIORITY_BLOCKED"]
    assert [x.value for x in Continuity] == ["NOT_ARMED", "PRIOR_STALE_OR_MISSING", "HAZARD_OR_UNRESOLVED", "POTENTIAL_S1_UNVERIFIED"]
    reasons = ["PRIORITY_BLOCKED", "RF_AMBIGUOUS", "RF_NOT_HEALTHY", "CONTROL_INVALID", "CONTROL_CONFLICT", "NO_UNCONTESTED_CONTROL", "ARMED_PRIOR_RF_STALE_OR_MISSING", "ARMED_PRIOR_CONTROL_STALE_OR_MISSING", "TRUST_NOT_PROVEN"]
    assert [x.value for x in Reason] == reasons
    recipe = armed_recipe(control_age=200001, rf_age=200001)
    recipe["pseudo_events"].extend([dict(id="bad", kind="CONTROL_INVALID", event_at_us=205000),
        dict(id="different", kind="CONTROL_VALID", event_at_us=205000, arm=True, flap="1", steer="0"),
        dict(id="lost", kind="RF_LOST", event_at_us=205000), dict(id="reset", kind="RESET", event_at_us=205000)])
    outcomes = [triage(*inputs(i)) for i in range(1, 37)] + [triage(*args_for(recipe))]
    for result in outcomes:
        assert len(fields(result)) == 10 and not hasattr(result, "__dict__")
        assert type(result.unresolved_reasons) is tuple
        assert result.unresolved_reasons == tuple(x for x in Reason if x in result.unresolved_reasons)
        assert result.unresolved_reasons[-1] is Reason.TRUST_NOT_PROVEN
        assert all(type(x) is Reason and not x.value.startswith(("E_", "P_")) for x in result.unresolved_reasons)
        with pytest.raises(FrozenInstanceError): result.unresolved_reasons = ()
        with pytest.raises(TypeError): result.unresolved_reasons[-1] = None
    assert outcomes[-1].unresolved_reasons == tuple(x for x in Reason if x is not Reason.RF_AMBIGUOUS)


@pytest.mark.parametrize("name,value", [("approved", True), ("health", "PASS"), ("control", "ADMITTED"),
    ("pre_state", "ARMED_IDLE"), ("prior_rf_snapshot", {}), ("unresolved_reasons", []), ("output_allowed", True)])
def test_N15_no_wire_permission_fields(name, value):
    schema = json.loads((DESIGN / "contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_bytes())
    wire = json.loads(wire_bytes(RECIPES[20])); wire[name] = value
    assert type(validate_wire(json.dumps(wire).encode(), schema)) is RejectedPreflight


def test_N16_no_side_effects_upstream_rerun_or_task006_adapter(monkeypatch):
    import bb_host_preflight_m0, bb_host_virtual_ticks, bb_host_batch_observations
    import bb_host_temporal_guard_facts, bb_host_safety_priority_kernel, bb_host_health_evidence, bb_host_arm_qualification
    args = inputs(); expected = triage(*args)
    def forbidden(*args, **kwargs): raise AssertionError("forbidden side effect or upstream/authority call")
    targets = [(builtins, "open"), (Path, "open"), (socket, "socket"), (random, "random"),
        (time, "time"), (time, "monotonic"), (time, "perf_counter"), (time, "sleep"),
        (bb_host_preflight_m0, "validate_wire"), (bb_host_preflight_m0, "mix_m0"),
        (bb_host_virtual_ticks, "iter_virtual_ticks"), (bb_host_batch_observations, "normalize_tick_observations"),
        (bb_host_temporal_guard_facts, "evaluate_temporal_guard_facts"), (bb_host_safety_priority_kernel, "assess_safety_priority"),
        (bb_host_health_evidence, "assess_health_evidence"), (bb_host_arm_qualification, "HypotheticalQualificationVerdict"),
        (bb_host_arm_qualification, "propose_arm_qualification")]
    with monkeypatch.context() as m:
        for obj, name in targets: m.setattr(obj, name, forbidden)
        assert triage(*args) == expected


def test_N16_runtime_imports_and_no_retained_mutable_state():
    tree = ast.parse(inspect.getsource(runtime))
    assert not any(isinstance(n, (ast.Import, ast.Global, ast.Nonlocal)) for n in ast.walk(tree))
    assert {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} <= {
        "dataclasses", "enum", "types", "bb_host_batch_observations", "bb_host_temporal_guard_facts", "bb_host_safety_priority_kernel", "bb_host_health_evidence"}
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert not names.intersection({"eval", "exec", "open", "__import__", "getattr_from_wire", "HealthVerdict", "ControlVerdict"})
    before = {k: repr(v) for k, v in vars(runtime).items() if not k.startswith("__")}
    assert not any(type(v) in (dict, list, set) for k, v in vars(runtime).items() if not k.startswith("__"))
    for i in range(1, 37): triage(*inputs(i))
    assert before == {k: repr(v) for k, v in vars(runtime).items() if not k.startswith("__")}
    with pytest.raises(TypeError): runtime._RF_LANES[RFEvidenceKind.MISSING] = RF.CURRENT_HEALTHY_UNCOMMITTED


@pytest.mark.parametrize("snapshot,field,value", [
    ("prior_rf_snapshot", "last_committed_eval_at_us", True), ("prior_rf_snapshot", "last_committed_eval_at_us", 205000),
    ("prior_rf_snapshot", "last_committed_eval_at_us", 199999), ("prior_rf_snapshot", "last_rf_original_at_us", 200001),
    ("prior_rf_snapshot", "last_rf_original_at_us", None), ("prior_rf_snapshot", "last_rf_status", None),
    ("prior_rf_snapshot", "last_rf_status", "BAD"), ("prior_rf_snapshot", "last_rf_original_at_us", 4999),
    ("prior_timestamp_snapshot", "last_accepted_control_at_us", True),
    ("prior_timestamp_snapshot", "last_committed_eval_at_us", None),
    ("prior_timestamp_snapshot", "last_uncontested_healthy_rf_at_us", -1)])
def test_N17_malformed_synthetic_prior_rejected_upstream(snapshot, field, value):
    recipe = armed_recipe(); recipe[snapshot][field] = value
    with pytest.raises((TypeError, ValueError)) as caught: args_for(recipe)
    assert not str(caught.value).startswith(("E_", "P_"))


@pytest.mark.parametrize("number,rf", [(2, RFEvidenceKind.MISSING), (12, RFEvidenceKind.STALE_PRIOR),
                                      (13, RFEvidenceKind.MISSING), (4, RFEvidenceKind.LOST_CARRIED),
                                      (7, RFEvidenceKind.UNKNOWN_CARRIED)])
def test_N17_contradictory_negative_rf_labels_also_raise(number, rf):
    obs, temporal, priority, health = inputs(number)
    with pytest.raises(ValueError) as caught: triage(obs, temporal, priority, replace(health, rf_evidence=rf))
    assert not str(caught.value).startswith(("E_", "P_"))


@pytest.mark.parametrize("label", [x for x in ControlEvidenceKind if x is not ControlEvidenceKind.SINGLE_CANDIDATE])
def test_N17_forged_negative_control_labels(label):
    obs, temporal, priority, health = inputs()
    with pytest.raises(ValueError): triage(obs, temporal, priority, replace(health, control_evidence=label))


@pytest.mark.parametrize("locale_name", ["C", "English_United States.1252"])
@pytest.mark.parametrize("tz", ["UTC0", "ICT-7"])
@pytest.mark.parametrize("precision", [2, 28])
def test_N18_locale_tz_decimal_and_repeatability(locale_name, tz, precision, monkeypatch):
    expected = [triage(*inputs(i)) for i in range(1, 37)]
    previous = locale.setlocale(locale.LC_ALL)
    try:
        locale.setlocale(locale.LC_ALL, locale_name); monkeypatch.setenv("TZ", tz)
        with localcontext() as ctx:
            ctx.prec = precision
            assert [triage(*inputs(i)) for i in range(1, 37)] == expected
    finally:
        locale.setlocale(locale.LC_ALL, previous)


@pytest.mark.parametrize("statuses", [("HEALTHY", "LOST"), ("HEALTHY", "UNKNOWN"), ("UNKNOWN", "LOST"), ("HEALTHY", "LOST", "UNKNOWN")])
def test_N18_equal_time_source_order_does_not_promote_health(statuses):
    recipe = deepcopy(RECIPES[20])
    recipe["pseudo_events"] = [e for e in recipe["pseudo_events"] if not e["kind"].startswith("RF_")]
    rf = [dict(id=f"rf{i}", kind="RF_" + status, event_at_us=4999) for i, status in enumerate(statuses)]
    forward = deepcopy(recipe); forward["pseudo_events"].extend(rf)
    reverse = deepcopy(recipe); reverse["pseudo_events"].extend(reversed(rf))
    assert triage(*args_for(forward)) == triage(*args_for(reverse))


def test_negative_family_inventory():
    declared = {name.split("_")[1] for name in globals() if name.startswith("test_N")}
    expected = {family[:3] for family in load_oracles()["mandatory_negative_test_families"]}
    assert declared == expected == {f"N{i:02}" for i in range(1, 19)}
