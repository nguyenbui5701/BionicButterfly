"""Actual failure injection and adversarial TEST_ONLY snapshot boundaries."""

import ast
import builtins
from copy import deepcopy
from dataclasses import asdict, fields, FrozenInstanceError, replace
from decimal import localcontext
from enum import Enum
import inspect
import json
import locale
from pathlib import Path
import random
import socket
import time

import pytest

from bb_host_snapshot_commit_gate import (OwnerSnapshot, genesis_snapshot, CommitOutcome as Outcome,
    JournalFaultMode as Fault, TestOnlyAtomicJournal as Journal, TestOnlySnapshotLedger as Ledger)
from bb_host_snapshot_commit_gate._testing import _seed_for_test
import bb_host_snapshot_commit_gate.ledger as ledger_module
import bb_host_snapshot_commit_gate._validation as validation
from bb_host_safety_priority_kernel import SafetyState
from bb_host_health_evidence import RFStatus, RFEvidenceKind, ControlEvidenceKind
from bb_host_guard_triage import RFGuardLane, ControlGuardLane, ArmedContinuityLane, GuardReason
from bb_host_preflight_m0 import validate_wire, RejectedPreflight
from scripts.scenarios import load_oracles, recipe_for, seed_snapshot, pipeline, exercise, wire_bytes, DESIGN

CASES = load_oracles()["cases"]
HISTORY = ("last_accepted_control_at_us", "last_uncontested_healthy_rf_at_us", "last_rf_status", "last_rf_original_at_us")
FORBIDDEN = ("output_allowed", "can_arm", "state_after", "post_state", "health", "control", "approved",
             "trace_sha256", "control_trace_sha256", "receipt", "left_micro_effort", "right_micro_effort")


def arguments(recipe):
    records = pipeline(recipe)
    return records[2], records[4], records[5], records[7], records[8]


def prepared(number=21, **kwargs):
    recipe = recipe_for(CASES[number - 1])
    return _seed_for_test(seed_snapshot(recipe), **kwargs), arguments(recipe)


def from_snapshot(snapshot, tick=None, events=()):
    """Independent TEST_ONLY wire recipe, with claimed history outside JSON."""
    tick = (0 if snapshot.last_tick_index is None else snapshot.last_eval_at_us + 5000) if tick is None else tick
    return dict(eval_at_us=tick, pre_state=snapshot.state.value,
        pseudo_events=[dict(id="boot", event_at_us=0, kind="BOOT"), *events],
        prior_timestamp_snapshot=dict(last_committed_eval_at_us=snapshot.last_eval_at_us,
            last_accepted_control_at_us=snapshot.last_accepted_control_at_us,
            last_uncontested_healthy_rf_at_us=snapshot.last_uncontested_healthy_rf_at_us),
        prior_rf_snapshot=dict(last_committed_eval_at_us=snapshot.last_eval_at_us,
            last_rf_status=None if snapshot.last_rf_status is None else snapshot.last_rf_status.value,
            last_rf_original_at_us=snapshot.last_rf_original_at_us))


def test_genesis_and_public_surface():
    genesis = genesis_snapshot()
    assert len(fields(genesis)) == 14 and genesis.generation == 0 and genesis.state is SafetyState.BOOT
    assert genesis.last_tick_index is genesis.last_eval_at_us is None
    assert genesis.recoverable_causes == () and genesis.held_micro_effort is None
    ledger = Ledger()
    assert ledger.snapshot == genesis and ledger.journal_records == () and ledger.failure_status is None
    assert not hasattr(ledger, "__dict__")
    with pytest.raises(AttributeError): ledger.snapshot = genesis
    for name in ("restore", "journal", "receipt", "publish", *FORBIDDEN): assert not hasattr(ledger, name)


@pytest.mark.parametrize("keyword", ["snapshot", "journal", "receipt", "approved", "callback", "output", "state"])
def test_no_public_restore_journal_receipt_or_callback(keyword):
    with pytest.raises(TypeError): Ledger(**{keyword: object()})
    ledger, args = prepared()
    with pytest.raises(TypeError): ledger.commit_tick(*args, **{keyword: object()})
    assert ledger.journal_records == () and ledger.snapshot.generation == 0


@pytest.mark.parametrize("field,bad", [
    ("generation", True), ("generation", -1), ("generation", 1.0),
    ("last_tick_index", True), ("last_tick_index", -1), ("last_tick_index", 12001),
    ("last_eval_at_us", 199999), ("last_eval_at_us", True), ("last_eval_at_us", None),
    ("last_eval_at_us", float("nan")), ("state", "ARMED_IDLE"), ("state", SafetyState.BOOT),
    ("last_accepted_control_at_us", 200001), ("last_accepted_control_at_us", True),
    ("last_uncontested_healthy_rf_at_us", -1), ("last_uncontested_healthy_rf_at_us", 199999),
    ("last_rf_status", "HEALTHY"), ("last_rf_status", None), ("last_rf_original_at_us", None),
    ("last_rf_original_at_us", 200001), ("last_rf_original_at_us", True),
    ("low_first_original_at_us", 1), ("high_edge_original_at_us", 1),
    ("held_micro_effort", (0, 0)), ("held_micro_effort", (1000001, 0)), ("held_micro_effort", [0, 0]),
    ("recoverable_causes", []), ("recoverable_causes", (1,))])
def test_snapshot_invariants_reject(field, bad):
    seed = seed_snapshot(recipe_for(CASES[40]))
    with pytest.raises((TypeError, ValueError)): _seed_for_test(replace(seed, **{field: bad}))


def test_snapshot_exact_types_and_rf_pairing():
    seed = seed_snapshot(recipe_for(CASES[40]))
    class FakeRF(str, Enum): HEALTHY = "HEALTHY"
    class FakeState(str, Enum): ARMED_IDLE = "ARMED_IDLE"
    class FakeSnapshot(OwnerSnapshot): pass
    for bad in (None, {}, FakeSnapshot(**{f.name: getattr(seed, f.name) for f in fields(seed)})):
        with pytest.raises(TypeError): _seed_for_test(bad)
    for change in (dict(last_rf_status=FakeRF.HEALTHY), dict(state=FakeState.ARMED_IDLE)):
        with pytest.raises(TypeError): _seed_for_test(replace(seed, **change))
    with pytest.raises(ValueError): _seed_for_test(replace(seed, last_rf_status=None, last_rf_original_at_us=None))
    with pytest.raises(ValueError): _seed_for_test(replace(seed, last_rf_status=RFStatus.LOST, last_rf_original_at_us=199999))
    with pytest.raises(ValueError): _seed_for_test(replace(genesis_snapshot(), last_accepted_control_at_us=0))


@pytest.mark.parametrize("change", [dict(low_qualified_committed_eval_at_us=35000),
    dict(low_first_original_at_us=15001, low_qualified_committed_eval_at_us=35000),
    dict(low_first_original_at_us=15000, low_qualified_committed_eval_at_us=35001),
    dict(high_edge_original_at_us=40000, high_edge_committed_eval_at_us=40000),
    dict(low_first_original_at_us=True)])
def test_disarmed_window_invariants(change):
    seed = replace(seed_snapshot(recipe_for(CASES[40])), state=SafetyState.DISARMED)
    with pytest.raises(ValueError): _seed_for_test(replace(seed, **change))


@pytest.mark.parametrize("change", [dict(low_first_original_at_us=15000), dict(high_edge_original_at_us=40000),
    dict(high_edge_committed_eval_at_us=40000), dict(high_edge_original_at_us=40001, high_edge_committed_eval_at_us=40000),
    dict(high_edge_original_at_us=40000, high_edge_committed_eval_at_us=40001)])
def test_armcheck_window_invariants(change):
    seed = replace(seed_snapshot(recipe_for(CASES[40])), state=SafetyState.ARM_CHECK)
    with pytest.raises(ValueError): _seed_for_test(replace(seed, **change))


@pytest.mark.parametrize("position", range(5))
@pytest.mark.parametrize("bad", [None, {}, [], "record", True])
def test_upstream_exact_classes(position, bad):
    ledger, args = prepared(); args = list(args); args[position] = bad
    with pytest.raises((TypeError, ValueError)): ledger.commit_tick(*args)
    assert ledger.snapshot.generation == 0 and ledger.journal_records == ()


@pytest.mark.parametrize("position", range(5))
def test_upstream_subclasses(position):
    ledger, args = prepared(); args = list(args); obj = args[position]
    cls = type("Forged", (type(obj),), {})
    args[position] = cls(**{f.name: getattr(obj, f.name) for f in fields(obj)})
    with pytest.raises(TypeError): ledger.commit_tick(*args)


@pytest.mark.parametrize("position", range(5))
@pytest.mark.parametrize("field,bad", [("tick_index", True), ("tick_index", -1), ("tick_index", 12001),
    ("tick_index", 2), ("eval_at_us", 4999), ("eval_at_us", True), ("eval_at_us", 5000.0), ("eval_at_us", float("nan"))])
def test_upstream_tick_mismatch(position, field, bad):
    ledger, args = prepared(); args = list(args); args[position] = replace(args[position], **{field: bad})
    with pytest.raises((TypeError, ValueError)): ledger.commit_tick(*args)


@pytest.mark.parametrize("position,change", [
    (0, dict(has_reset=True)), (0, dict(rf_events=[])), (0, dict(rf_has_healthy=1)),
    (1, dict(has_rf_lost_observation=True)), (1, dict(prior_rf_within_timeout=True)),
    (1, dict(observed_uncontested_valid_control_at_us=4998)),
    (2, dict(pre_state=SafetyState.ARMED_IDLE)), (2, dict(provisional_next_state=SafetyState.SELF_TEST)),
    (2, dict(blocks_control_qualification=True)), (2, dict(requires_full_fsm=1)),
    (3, dict(rf_evidence=RFEvidenceKind.HEALTHY_CARRIED)), (3, dict(control_evidence="ADMITTED")),
    (3, dict(requires_full_fsm=False)), (3, dict(pre_state=SafetyState.ARMED_IDLE)),
    (4, dict(pre_state=SafetyState.SELF_TEST)), (4, dict(requires_full_fsm=1)),
    (4, dict(rf_lane=RFGuardLane.NOT_HEALTHY)), (4, dict(control_lane=ControlGuardLane.NO_CANDIDATE)),
    (4, dict(armed_continuity_lane=ArmedContinuityLane.POTENTIAL_S1_UNVERIFIED)),
    (4, dict(current_rf_candidate_original_at_us=4999)), (4, dict(current_control_candidate_original_at_us=None)),
    (4, dict(unresolved_reasons=[])), (4, dict(unresolved_reasons=("TRUST_NOT_PROVEN",))),
    (4, dict(unresolved_reasons=(GuardReason.PRIORITY_BLOCKED, GuardReason.TRUST_NOT_PROVEN)))])
def test_cross_stage_contradictions(position, change):
    ledger, args = prepared(); args = list(args); args[position] = replace(args[position], **change)
    with pytest.raises((TypeError, ValueError)): ledger.commit_tick(*args)
    assert ledger.snapshot.generation == 0 and ledger.failure_status is None


def test_history_bound_to_owner_not_forged_freshness():
    recipe = recipe_for(CASES[40]); seed = seed_snapshot(recipe)
    ledger = _seed_for_test(replace(seed, last_accepted_control_at_us=4999))
    with pytest.raises(ValueError): ledger.commit_tick(*arguments(recipe))
    silent = from_snapshot(seed)
    ledger = _seed_for_test(replace(seed, last_rf_status=RFStatus.LOST))
    with pytest.raises(ValueError): ledger.commit_tick(*arguments(silent))


def test_two_disarmed_commits_duplicate_and_gap_rejection():
    seed = seed_snapshot(recipe_for(CASES[20])); ledger = _seed_for_test(seed)
    args = arguments(from_snapshot(seed)); before = repr(args)
    one = ledger.commit_tick(*args)
    assert (seed.generation, one.snapshot_generation) == (0, 1) and seed.last_tick_index == 0
    first = ledger.snapshot
    with pytest.raises(ValueError): ledger.commit_tick(*args)
    with pytest.raises(ValueError): ledger.commit_tick(*arguments(from_snapshot(first, tick=15000)))
    two = ledger.commit_tick(*arguments(from_snapshot(first)))
    assert two.snapshot_generation == 2 and ledger.snapshot.last_tick_index == 2
    assert first.generation == 1 and ledger.journal_acknowledged_append_count == len(ledger.journal_records) == 2
    assert repr(args) == before
    assert [json.loads(raw)["tick_index"] for raw in ledger.journal_records] == [1, 2]


def test_genesis_then_selftest_bookkeeping_is_not_readiness():
    ledger = Ledger()
    for _ in range(3):
        assert ledger.commit_tick(*arguments(from_snapshot(ledger.snapshot))).outcome is Outcome.COMMITTED_TEST_ONLY
        assert ledger.snapshot.state is SafetyState.SELF_TEST
    assert ledger.snapshot.generation == 3 and ledger.snapshot.last_tick_index == 2


def test_actual_append_ack_before_snapshot_swap(monkeypatch):
    ledger, args = prepared(); prior = ledger.snapshot; seen = []
    append, check = Journal._append, Journal._is_full_ack
    def append_probe(journal, raw):
        assert ledger.snapshot is prior
        seen.append("before_append")
        ack = append(journal, raw)
        assert journal.acknowledged_append_count == 1 and ledger.snapshot is prior
        seen.append("full_append_ack")
        return ack
    def check_probe(journal, ack, raw, count):
        assert ledger.snapshot is prior
        assert check(journal, ack, raw, count)
        seen.append("ack_verified")
        return True
    monkeypatch.setattr(Journal, "_append", append_probe); monkeypatch.setattr(Journal, "_is_full_ack", check_probe)
    result = ledger.commit_tick(*args)
    assert seen == ["before_append", "full_append_ack", "ack_verified"]
    assert result.outcome is Outcome.COMMITTED_TEST_ONLY and ledger.snapshot is not prior


@pytest.mark.parametrize("mode", [m for m in Fault if m is not Fault.NONE])
def test_every_failure_sticky_without_snapshot_advance(mode):
    ledger, args = prepared(fault_mode=mode); prior = ledger.snapshot
    result = ledger.commit_tick(*args)
    assert result.outcome is Outcome.FAILED_INCOMPLETE_EVIDENCE and result.snapshot_generation is None
    assert ledger.snapshot is prior and ledger.journal_acknowledged_append_count == 0
    assert bool(ledger.journal_records) == (mode is Fault.FAIL_AFTER_WRITE_BEFORE_ACK)
    assert bool(ledger.journal_partial_bytes) == (mode is Fault.SHORT_WRITE)
    if ledger.journal_partial_bytes: assert not ledger.journal_partial_bytes.endswith(b"\n")
    for attempted in (args, arguments(from_snapshot(prior, tick=10000))):
        with pytest.raises(ValueError): ledger.commit_tick(*attempted)
    assert ledger.snapshot is prior and ledger.failure_status is Outcome.FAILED_INCOMPLETE_EVIDENCE


@pytest.mark.parametrize("bad_ack", [None, False, True, 1, b"receipt", object()])
def test_false_forged_append_ack_is_not_a_commit(monkeypatch, bad_ack):
    ledger, args = prepared(); prior = ledger.snapshot
    monkeypatch.setattr(Journal, "_append", lambda self, record: bad_ack)
    assert ledger.commit_tick(*args).outcome is Outcome.FAILED_INCOMPLETE_EVIDENCE
    assert ledger.snapshot is prior and ledger.journal_records == ()


def test_private_marker_without_full_append_is_not_enough(monkeypatch):
    ledger, args = prepared(); prior = ledger.snapshot
    monkeypatch.setattr(Journal, "_append", lambda self, record: self._TestOnlyAtomicJournal__marker)
    assert ledger.commit_tick(*args).outcome is Outcome.FAILED_INCOMPLETE_EVIDENCE
    assert ledger.snapshot is prior


def test_real_serializer_exception_and_real_quota_boundary(monkeypatch):
    def broken(*args, **kwargs): raise TypeError("serializer fault")
    ledger, args = prepared(); prior = ledger.snapshot
    with monkeypatch.context() as m:
        m.setattr(ledger_module.json, "dumps", broken)
        assert ledger.commit_tick(*args).outcome is Outcome.FAILED_INCOMPLETE_EVIDENCE
    assert ledger.snapshot is prior and ledger.journal_records == ()
    good, args = prepared(); good.commit_tick(*args); size = len(good.journal_records[0])
    for quota, outcome in ((size - 1, Outcome.FAILED_INCOMPLETE_EVIDENCE), (size, Outcome.COMMITTED_TEST_ONLY)):
        ledger, args = prepared(byte_quota=quota)
        assert ledger.commit_tick(*args).outcome is outcome


@pytest.mark.parametrize("number", [41, 42, 43, 44])
def test_deferred_ticks_never_append_or_advance_even_with_fault(number):
    ledger, args = prepared(number, fault_mode=Fault.FAIL_BEFORE_APPEND); prior = ledger.snapshot
    for _ in range(2): assert ledger.commit_tick(*args).outcome is Outcome.DEFERRED_NEEDS_FULL_FSM
    assert ledger.snapshot is prior and ledger.failure_status is None and ledger.journal_records == ()
    with pytest.raises(ValueError): ledger.commit_tick(*arguments(from_snapshot(prior, tick=210000)))


@pytest.mark.parametrize("state", [SafetyState.ARM_CHECK, SafetyState.ARMED_IDLE, SafetyState.ACTUATION_ACTIVE])
@pytest.mark.parametrize("channel", ["control", "rf"])
@pytest.mark.parametrize("age", [200000, 200001])
def test_armed_stale_before_reset_at_independent_boundary(state, channel, age):
    seed = replace(seed_snapshot(recipe_for(CASES[40])), state=state)
    at = 205000 - age
    seed = replace(seed, **({"last_accepted_control_at_us": at} if channel == "control" else
        {"last_uncontested_healthy_rf_at_us": at, "last_rf_original_at_us": at}))
    events = [dict(id="reset", kind="RESET", event_at_us=204997), dict(id="rf", kind="RF_HEALTHY", event_at_us=204998),
              dict(id="control", kind="CONTROL_VALID", event_at_us=204999, arm=True, flap="0.5", steer="0")]
    ledger = _seed_for_test(seed); result = ledger.commit_tick(*arguments(from_snapshot(seed, events=events)))
    assert result.outcome is (Outcome.DEFERRED_NEEDS_FULL_FSM if age == 200000 else Outcome.COMMITTED_TEST_ONLY)
    if age > 200000: assert ledger.snapshot.state is SafetyState.CONTINGENCY
    assert all(getattr(ledger.snapshot, field) == getattr(seed, field) for field in HISTORY)


@pytest.mark.parametrize("state", [SafetyState.CONTINGENCY, SafetyState.FAULT_LATCHED])
def test_restricted_states_hold_despite_ack_reset_healthy(state):
    seed = replace(seed_snapshot(recipe_for(CASES[40])), state=state, recoverable_causes=("E_RF_NOT_HEALTHY",))
    events = [dict(id="ack", kind="ACK", event_at_us=204997), dict(id="reset", kind="RESET", event_at_us=204998),
              dict(id="healthy", kind="RF_HEALTHY", event_at_us=204999)]
    ledger = _seed_for_test(seed)
    assert ledger.commit_tick(*arguments(from_snapshot(seed, events=events))).outcome is Outcome.COMMITTED_TEST_ONLY
    assert ledger.snapshot.state is state and ledger.snapshot.recoverable_causes == seed.recoverable_causes


@pytest.mark.parametrize("kind,state", [("RESET", SafetyState.SELF_TEST), ("CATA", SafetyState.FAULT_LATCHED)])
def test_admin_clear_windows_causes_but_not_accepted_history(kind, state):
    seed = replace(seed_snapshot(recipe_for(CASES[40])), state=SafetyState.DISARMED,
        low_first_original_at_us=15000, low_qualified_committed_eval_at_us=35000, recoverable_causes=("historical-test-cause",))
    ledger = _seed_for_test(seed)
    ledger.commit_tick(*arguments(from_snapshot(seed, events=[dict(id="event", kind=kind, event_at_us=204999)])))
    assert ledger.snapshot.state is state and ledger.snapshot.low_first_original_at_us is None
    assert ledger.snapshot.low_qualified_committed_eval_at_us is None and ledger.snapshot.recoverable_causes == ()
    assert all(getattr(ledger.snapshot, name) == getattr(seed, name) for name in HISTORY)


def test_armcheck_hazard_clears_high_window_and_catastrophe_outranks_ambiguity():
    seed = replace(seed_snapshot(recipe_for(CASES[40])), state=SafetyState.ARM_CHECK,
                   high_edge_original_at_us=40000, high_edge_committed_eval_at_us=40000)
    events = [dict(id="lost", kind="RF_LOST", event_at_us=204999)]
    ledger = _seed_for_test(seed); ledger.commit_tick(*arguments(from_snapshot(seed, events=events)))
    assert ledger.snapshot.state is SafetyState.CONTINGENCY
    assert ledger.snapshot.high_edge_original_at_us is ledger.snapshot.high_edge_committed_eval_at_us is None
    events = [dict(id="h", kind="RF_HEALTHY", event_at_us=204996), dict(id="u", kind="RF_UNKNOWN", event_at_us=204997),
              dict(id="reset", kind="RESET", event_at_us=204998), dict(id="cata", kind="CATA", event_at_us=204999)]
    ledger = _seed_for_test(seed); ledger.commit_tick(*arguments(from_snapshot(seed, events=events)))
    assert ledger.snapshot.state is SafetyState.FAULT_LATCHED


def test_nonarmed_hold_preserves_historical_windows_and_lost_status():
    seed = replace(seed_snapshot(recipe_for(CASES[40])), state=SafetyState.DISARMED,
        last_rf_status=RFStatus.LOST, low_first_original_at_us=15000, low_qualified_committed_eval_at_us=35000)
    events = [dict(id="healthy", kind="RF_HEALTHY", event_at_us=204998),
              dict(id="ctrl", kind="CONTROL_VALID", event_at_us=204999, arm=True, flap="0", steer="0")]
    ledger = _seed_for_test(seed); ledger.commit_tick(*arguments(from_snapshot(seed, events=events)))
    assert ledger.snapshot.last_rf_status is RFStatus.LOST
    assert ledger.snapshot.low_first_original_at_us == 15000 and ledger.snapshot.low_qualified_committed_eval_at_us == 35000
    assert all(getattr(ledger.snapshot, name) == getattr(seed, name) for name in HISTORY)


def test_complete_internal_bytes_deterministic_and_not_r1_trace():
    a, args = prepared(); b, _ = prepared()
    a.commit_tick(*args); b.commit_tick(*args)
    assert a.journal_records == b.journal_records and type(a.journal_records) is tuple
    record = json.loads(a.journal_records[0])
    assert set(record) == {"format", "tick_index", "eval_at_us", "pre_state", "next_test_state", "decision_kind"}
    assert record["format"] == "BB_E1_TEST_JOURNAL_V1"
    assert all(not hasattr(a.commit_tick, name) for name in FORBIDDEN)
    with pytest.raises(TypeError): a.journal_records[0] = b"forged"


def test_no_nested_rescan_no_upstream_rerun_or_io(monkeypatch):
    import bb_host_preflight_m0, bb_host_virtual_ticks, bb_host_batch_observations
    import bb_host_temporal_guard_facts, bb_host_safety_priority_kernel, bb_host_health_evidence, bb_host_guard_triage
    ledger, args = prepared(); obs, temporal, priority, health, triage = args
    poison = object(); obs = replace(obs, source_events=(poison,), causal_event_ids=(poison,), rf_events=(poison,), valid_control_groups=(poison,))
    def forbidden(*args, **kwargs): raise AssertionError("forbidden IO or upstream rerun")
    targets = [(builtins, "open"), (Path, "open"), (time, "time"), (time, "monotonic"), (time, "sleep"),
        (random, "random"), (socket, "socket"), (bb_host_preflight_m0, "validate_wire"), (bb_host_preflight_m0, "mix_m0"),
        (bb_host_virtual_ticks, "iter_virtual_ticks"), (bb_host_batch_observations, "normalize_tick_observations"),
        (bb_host_temporal_guard_facts, "evaluate_temporal_guard_facts"), (bb_host_safety_priority_kernel, "assess_safety_priority"),
        (bb_host_health_evidence, "assess_health_evidence"), (bb_host_guard_triage, "triage_guard_evidence")]
    with monkeypatch.context() as m:
        for obj, name in targets: m.setattr(obj, name, forbidden)
        assert ledger.commit_tick(obs, temporal, priority, health, triage).outcome is Outcome.COMMITTED_TEST_ONLY


def test_source_has_no_external_adapter_trust_or_callback():
    directory = Path(ledger_module.__file__).parent
    allowed = {"dataclasses", "enum", "json", "types", "bb_host_batch_observations", "bb_host_temporal_guard_facts",
        "bb_host_safety_priority_kernel", "bb_host_health_evidence", "bb_host_guard_triage"}
    for path in directory.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): assert all(a.name in allowed for a in node.names)
            if isinstance(node, ast.ImportFrom) and not node.level: assert node.module in allowed
            assert not isinstance(node, (ast.Global, ast.Nonlocal))
    assert tuple(inspect.signature(Ledger.commit_tick).parameters) == ("self", "observations", "temporal", "priority", "health", "triage")


@pytest.mark.parametrize("field,value", [("receipt", True), ("approved", True), ("health", "PASS"),
    ("control", "ADMITTED"), ("snapshot", {}), ("test_journal_fault_mode", "NONE")])
def test_wire_cannot_supply_snapshot_or_receipt(field, value):
    raw = json.loads(wire_bytes(recipe_for(CASES[20]))); raw[field] = value
    schema = json.loads((DESIGN / "contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_bytes())
    assert type(validate_wire(json.dumps(raw).encode(), schema)) is RejectedPreflight


@pytest.mark.parametrize("loc", ["C", "English_United States.1252"])
@pytest.mark.parametrize("tz", ["UTC0", "ICT-7"])
@pytest.mark.parametrize("precision", [2, 28])
def test_deterministic_locale_tz_decimal(loc, tz, precision, monkeypatch):
    old = locale.setlocale(locale.LC_ALL)
    expected = [(exercise(case)[0].journal_records, exercise(case)[2]) for case in CASES]
    try:
        locale.setlocale(locale.LC_ALL, loc); monkeypatch.setenv("TZ", tz)
        with localcontext() as context:
            context.prec = precision
            assert [(exercise(case)[0].journal_records, exercise(case)[2]) for case in CASES] == expected
    finally:
        locale.setlocale(locale.LC_ALL, old)
