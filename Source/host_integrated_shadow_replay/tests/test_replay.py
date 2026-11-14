import ast
import builtins
from dataclasses import fields, replace, FrozenInstanceError
from decimal import Decimal, localcontext
import inspect
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import tracemalloc

import pytest
from bb_host_integrated_shadow_replay import run_shadow_replay, ShadowReplayReport, ShadowTick, ShadowReplayOutcome as Outcome
from bb_host_integrated_shadow_replay import replay, diagnostic
from bb_host_snapshot_commit_gate import TestOnlyAtomicJournal as AtomicJournal, TestOnlySnapshotLedger as SnapshotLedger, CommitOutcome, SnapshotCommitResult, JournalFaultMode
from scripts.fixtures import inputs
from scripts import demo


def forbidden(*args, **kwargs):
    raise AssertionError("unexpected call")


def encode(data):
    return json.dumps(data, separators=(",", ":")).encode()


@pytest.mark.parametrize("name", ["scenario_raw", "policy_raw", "intent_raw", "engine_artifact", "scheduler_artifact"])
@pytest.mark.parametrize("value", [None, True, b"x".decode(), bytearray(b"x"), memoryview(b"x")])
def test_exact_byte_types(name, value):
    values = inputs("minimal")
    values[name] = value
    with pytest.raises((TypeError, ValueError)):
        run_shadow_replay(**values)


@pytest.mark.parametrize("key,value", [("schema_version", True), ("approved", True), ("owner", "SIMULATOR"),
    ("engine_revision", "FAKE"), ("output_adapter", "PWM"), ("plugin", "local.py"), ("scenario_id", "\ud800")])
def test_bad_wire_blocks_before_scheduler(key, value, monkeypatch):
    values = inputs("minimal")
    values["scenario_raw"] = encode(json.loads(values["scenario_raw"]) | {key: value})
    monkeypatch.setattr(replay, "iter_virtual_ticks", forbidden)
    report = run_shadow_replay(**values)
    assert report.outcome is Outcome.INPUT_REJECTED and report.shadow_tick_count == 0


def test_schema_and_closed_signature():
    values = inputs("minimal")
    assert len(inspect.signature(run_shadow_replay).parameters) == 7
    for name in ("initial_snapshot", "ledger", "output_sink", "callback", "authorized", "receipt"):
        with pytest.raises(TypeError):
            run_shadow_replay(**values, **{name: True})
    values["frozen_wire_v2_schema"] = {}
    with pytest.raises(ValueError):
        run_shadow_replay(**values)


@pytest.mark.parametrize("change", ["policy", "intent", "claim"])
def test_gates_stop_before_any_tick(change, monkeypatch):
    values = inputs("minimal")
    if change == "policy":
        values["policy_raw"] += b"\n"
    elif change == "intent":
        values["intent_raw"] += b"\n"
    else:
        values["claimed_host"] = replace(values["claimed_host"], scope="PHYSICAL")
    monkeypatch.setattr(replay, "iter_virtual_ticks", forbidden)
    monkeypatch.setattr(replay, "TestOnlySnapshotLedger", forbidden)
    assert run_shadow_replay(**values).outcome is Outcome.REFERENCE_OR_INTENT_BLOCKED


def test_real_pipeline_order_and_prior_bridge(monkeypatch):
    calls = []
    names = ("validate_wire", "assess_reference_host_boundary", "inspect_provisioning_intent", "iter_virtual_ticks",
             "normalize_tick_observations", "evaluate_temporal_guard_facts", "assess_safety_priority", "assess_health_evidence", "triage_guard_evidence")
    originals = {name: getattr(replay, name) for name in names}
    for name in names:
        def track(*args, _name=name, **kwargs):
            calls.append(_name)
            if _name == "evaluate_temporal_guard_facts":
                obs, prior = args
                assert prior.last_committed_eval_at_us == (obs.eval_at_us - 5000 if obs.tick_index else None)
                assert prior.last_accepted_control_at_us is None and prior.last_uncontested_healthy_rf_at_us is None
            if _name == "assess_health_evidence":
                assert args[-1].last_rf_status is None and args[-1].last_rf_original_at_us is None
            return originals[_name](*args, **kwargs)
        monkeypatch.setattr(replay, name, track)
    values = inputs("pilot")
    before = repr(values)
    report = run_shadow_replay(**values)
    assert repr(values) == before
    assert calls[:4] == list(names[:4])
    assert calls[4:] == list(names[4:]) * 8
    assert report.shadow_tick_count == 8


def test_subgrid_times_and_grouping_preserved(monkeypatch):
    values = inputs("pilot")
    wire = json.loads(values["scenario_raw"])
    wire["events"][1]["event_at_us"] = 4998
    wire["events"][2]["event_at_us"] = 4999
    values["scenario_raw"] = encode(wire)
    original = replay.evaluate_temporal_guard_facts
    candidates = []
    def temporal(*args):
        result = original(*args)
        candidates.append((result.observed_uncontested_valid_control_at_us, result.observed_uncontested_healthy_rf_at_us))
        return result
    monkeypatch.setattr(replay, "evaluate_temporal_guard_facts", temporal)
    report = run_shadow_replay(**values)
    assert candidates[1] == (4999, 4998)
    assert report.shadow_ticks[1].eval_at_us == 5000


@pytest.mark.parametrize("precision", [2, 28, 60])
def test_decimal_exact_preview_clipping(precision):
    values = inputs("pilot")
    raw = values["scenario_raw"].replace(b'"flap_demand": 0.4', b'"flap_demand": 0.999999').replace(b'"steering_demand": 0.2', b'"steering_demand": 0.000002')
    assert raw != values["scenario_raw"]
    values["scenario_raw"] = raw
    with localcontext() as context:
        context.prec = precision
        report = run_shadow_replay(**values)
    row = report.shadow_ticks[2]
    assert (row.preview_left_micro, row.preview_right_micro) == (999997, 1000000)
    assert row.preview_clip_tags == ("RIGHT_HIGH",)


@pytest.mark.parametrize("rf", ["LOST", "UNKNOWN", "MISSING", "AMBIGUOUS"])
def test_unhealthy_or_missing_rf_never_preview(rf):
    values = inputs("pilot")
    wire = json.loads(values["scenario_raw"])
    event = wire["events"][3]
    assert event["event_id"] == "rf-h-10"
    if rf == "MISSING":
        wire["events"].remove(event)
    elif rf == "AMBIGUOUS":
        wire["events"].insert(4, dict(event_id="unknown-10", event_at_us=10000, type="SIM_RF_STATUS", payload=dict(rf_health="UNKNOWN", rf_provenance="INJECTED_SIM")))
    else:
        event["payload"]["rf_health"] = rf
    values["scenario_raw"] = encode(wire)
    report = run_shadow_replay(**values)
    assert report.shadow_ticks[2].preview_left_micro is None


@pytest.mark.parametrize("mode", [JournalFaultMode.FAIL_BEFORE_APPEND, JournalFaultMode.FAIL_AFTER_WRITE_BEFORE_ACK,
                                   JournalFaultMode.SHORT_WRITE, JournalFaultMode.QUOTA_DENIED, JournalFaultMode.SERIALIZATION_FAILED])
def test_journal_fault_stops_without_preview_retry(mode, monkeypatch):
    original_init = AtomicJournal.__init__
    original_commit = SnapshotLedger.commit_tick
    seen = []
    def initialize(journal):
        original_init(journal)
        journal._configure_test_fault(mode, 16777216)
    def commit(ledger, *args):
        seen.append(args[0].tick_index)
        return original_commit(ledger, *args)
    monkeypatch.setattr(AtomicJournal, "__init__", initialize)
    monkeypatch.setattr(SnapshotLedger, "commit_tick", commit)
    monkeypatch.setattr(replay, "mix_m0", forbidden)
    report = run_shadow_replay(**inputs("pilot"))
    assert report.outcome is Outcome.SHADOW_EVIDENCE_INCOMPLETE
    assert report.shadow_ticks == () and seen == [0]


def test_later_append_failure_no_tentative_row(monkeypatch):
    original = AtomicJournal._append
    seen = []
    def append(journal, raw):
        tick = json.loads(raw)["tick_index"]
        seen.append(tick)
        if tick == 2:
            raise OSError("TEST_ONLY failure at preview tick")
        return original(journal, raw)
    monkeypatch.setattr(AtomicJournal, "_append", append)
    report = run_shadow_replay(**inputs("pilot"))
    assert report.shadow_tick_count == 2 and report.blocked_at_tick == 2 and seen == [0, 1, 2]
    assert report.outcome is Outcome.SHADOW_EVIDENCE_INCOMPLETE


def test_negative_defer_path_no_forged_positive_snapshot(monkeypatch):
    original = SnapshotLedger.commit_tick
    def commit(ledger, obs, *args):
        if obs.tick_index == 1:
            return SnapshotCommitResult(CommitOutcome.DEFERRED_NEEDS_FULL_FSM, 1, 5000, None, True)
        return original(ledger, obs, *args)
    monkeypatch.setattr(SnapshotLedger, "commit_tick", commit)
    report = run_shadow_replay(**inputs("minimal"))
    assert report.outcome is Outcome.BLOCKED_NEEDS_FULL_FSM and report.blocked_at_tick == 1
    assert report.shadow_tick_count == 1


def test_append_ack_before_mixer_and_public_row(monkeypatch):
    original_append = AtomicJournal._append
    original_mix = replay.mix_m0
    acknowledgements = []
    def append(journal, raw):
        ack = original_append(journal, raw)
        acknowledgements.append(json.loads(raw)["tick_index"])
        return ack
    mixes = []
    def mix(*args):
        mixes.append(acknowledgements[-1])
        return original_mix(*args)
    monkeypatch.setattr(AtomicJournal, "_append", append)
    monkeypatch.setattr(replay, "mix_m0", mix)
    run_shadow_replay(**inputs("pilot"))
    assert acknowledgements == list(range(8)) and mixes == [1, 2, 3, 5]


def test_frozen_fields_and_determinism():
    values = inputs("pilot")
    report = run_shadow_replay(**values)
    assert run_shadow_replay(**values) == report
    assert [f.name for f in fields(report)] == ['outcome','preflight_status','e2_outcome','e3_outcome','shadow_ticks','shadow_tick_count','blocked_at_tick','runtime_authorized','requires_full_fsm','actual_virtual_output','physical_output','canonical_control_trace_sha256']
    assert [f.name for f in fields(ShadowTick)] == ['tick_index','eval_at_us','causal_event_ids','pre_state','test_state_after','rf_evidence','control_evidence','triage_reasons','e1_outcome','arm_switch_requested','preview_left_micro','preview_right_micro','preview_clip_tags','runtime_authorized','actual_virtual_output','physical_output']
    for obj in (report, *report.shadow_ticks):
        assert not hasattr(obj, "__dict__")
        for f in fields(obj):
            with pytest.raises(FrozenInstanceError):
                setattr(obj, f.name, None)
        with pytest.raises(ValueError):
            replace(obj, runtime_authorized=True)
    raw = diagnostic.diagnostic_bytes(report)
    assert raw == diagnostic.diagnostic_bytes(run_shadow_replay(**values))
    records = [json.loads(line) for line in raw.splitlines()]
    assert len(records) == 10
    for record in records:
        assert record["authority"] == "NONE" and record["physical_output"] is None and record["actual_virtual_output"] is None
        assert "record_type" not in record and "control_trace_sha256" not in record


def test_core_has_no_io_or_hypothetical_authority(monkeypatch):
    values = inputs("pilot")
    with monkeypatch.context() as patch:
        for obj, name in ((builtins, "open"), (Path, "open"), (socket, "socket"), (os, "getenv"), (subprocess, "Popen"), (time, "time")):
            patch.setattr(obj, name, forbidden)
        assert run_shadow_replay(**values).shadow_tick_count == 8
    for path in Path(replay.__file__).parent.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(n.name in ("json",) for n in node.names)
            if isinstance(node, ast.ImportFrom):
                assert node.module not in ("os", "socket", "subprocess", "serial", "pathlib", "bb_host_arm_qualification")
            if isinstance(node, ast.Call):
                assert getattr(node.func, "id", "") not in ("open", "eval", "exec", "__import__", "OwnerSnapshot", "AcceptedPreflight", "_seed_for_test")


def test_long_60s_20000_events_bounded_work(monkeypatch):
    values = inputs("minimal")
    wire = json.loads(values["scenario_raw"])
    wire["duration_us"] = 60_000_000
    wire["events"] += [dict(event_id=f"a{i}", event_at_us=5000, type="SIM_ACK_FAULT", payload={}) for i in range(19999)]
    values["scenario_raw"] = encode(wire)
    assert len(values["scenario_raw"]) <= 2097152
    original = replay.normalize_tick_observations
    seen = []
    def normalize(batch):
        seen.append(len(batch.events))
        return original(batch)
    monkeypatch.setattr(replay, "normalize_tick_observations", normalize)
    tracemalloc.start()
    started = time.perf_counter()
    try:
        report = run_shadow_replay(**values)
        raw = diagnostic.diagnostic_bytes(report)
        elapsed = time.perf_counter() - started
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert report.shadow_tick_count == 12001 and len(seen) == 12001
    assert seen[:2] == [1, 19999] and sum(seen[2:]) == 0
    assert len(raw) <= 16_777_216
    Path("evidence/performance.json").write_text(json.dumps(dict(ticks=12001, events=20000,
        elapsed_seconds=elapsed, peak_python_tracemalloc_bytes=peak, diagnostic_bytes=len(raw),
        process_peak_memory="NOT MEASURED", scope="TASK012 DEV CHECK, no prior regression"), indent=2)+"\n", encoding="utf-8")
