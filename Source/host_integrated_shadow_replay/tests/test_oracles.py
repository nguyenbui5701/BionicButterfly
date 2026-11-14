"""Exactly 20 authored P224 cases; positive paths use genuine upstream APIs."""
from dataclasses import replace, fields
import json
import pytest

from bb_host_integrated_shadow_replay import run_shadow_replay, ShadowReplayOutcome as Outcome
from bb_host_snapshot_commit_gate import TestOnlyAtomicJournal as AtomicJournal, JournalFaultMode, TestOnlySnapshotLedger as SnapshotLedger
from scripts.fixtures import index, inputs

CASES = index()["cases"]


def assert_no_authority(report):
    assert report.runtime_authorized is False and report.requires_full_fsm is True
    assert report.actual_virtual_output is None and report.physical_output is None
    assert report.canonical_control_trace_sha256 is None
    assert type(report.shadow_ticks) is tuple and report.shadow_tick_count == len(report.shadow_ticks)
    for row in report.shadow_ticks:
        assert row.runtime_authorized is False and row.actual_virtual_output is None and row.physical_output is None
        assert row.test_state_after.value in ("SELF_TEST", "FAULT_LATCHED")
        assert row.e1_outcome.value == "COMMITTED_TEST_ONLY"
        assert (row.preview_left_micro is None) == (row.preview_right_micro is None)
        assert row.causal_event_ids == tuple(sorted(set(row.causal_event_ids), key=lambda x: x.encode("utf-8")))


def preview(row):
    return row.preview_left_micro, row.preview_right_micro


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_p224_real_pipeline(case, monkeypatch):
    values = inputs(case["preset"])
    mutation = case["mutation"]
    journals = []
    snapshots = []
    original_commit = SnapshotLedger.commit_tick
    def commit(ledger, *args):
        result = original_commit(ledger, *args)
        snapshots.append(ledger.snapshot)
        return result
    # Observation-only wrapper; does not substitute any positive upstream data.
    monkeypatch.setattr(SnapshotLedger, "commit_tick", commit)
    if mutation == "inject_unknown_approval":
        values["scenario_raw"] = json.dumps(json.loads(values["scenario_raw"]) | {"approved": True}).encode()
    elif mutation == "policy_add_lf":
        values["policy_raw"] += b"\n"
    elif mutation == "manifest_bad_policy_digest":
        data = json.loads(values["intent_raw"]) | {"policy_sha256": "0" * 64}
        values["intent_raw"] = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    elif mutation == "synthetic_engine_modified":
        values["engine_artifact"] += b"\n"
    elif mutation == "E2_engine_claim_bad":
        values["claimed_host"] = replace(values["claimed_host"], engine_revision="BAD_ENGINE")
    elif mutation in ("E1_before_append_fault", "E1_after_write_no_ack"):
        original = AtomicJournal._append
        def append(journal, raw):
            journals.append(journal)
            mode = (JournalFaultMode.FAIL_BEFORE_APPEND if mutation == "E1_before_append_fault"
                    else JournalFaultMode.FAIL_AFTER_WRITE_BEFORE_ACK)
            journal._configure_test_fault(mode, 16777216)
            return original(journal, raw)
        monkeypatch.setattr(AtomicJournal, "_append", append)
    else:
        assert mutation == "valid"
    report = run_shadow_replay(**values)
    assert_no_authority(report)
    for snapshot in snapshots:
        assert snapshot.last_accepted_control_at_us is None and snapshot.last_uncontested_healthy_rf_at_us is None
        assert snapshot.last_rf_status is None and snapshot.last_rf_original_at_us is None
        assert snapshot.low_first_original_at_us is None and snapshot.low_qualified_committed_eval_at_us is None
        assert snapshot.high_edge_original_at_us is None and snapshot.high_edge_committed_eval_at_us is None
        assert snapshot.held_micro_effort is None
    n = int(case["id"][-2:])
    if n < 14:
        assert report.outcome is Outcome.SHADOW_DIAGNOSTICS_COMPLETE
        assert report.shadow_tick_count == {"minimal": 2, "pilot": 8, "hazard": 6, "conflict": 4}[case["preset"]]
        assert [s.generation for s in snapshots] == list(range(1, report.shadow_tick_count + 1))
        rows = report.shadow_ticks
        if n == 1:
            assert [r.test_state_after.value for r in rows] == ["SELF_TEST", "SELF_TEST"]
            assert all(preview(r) == (None, None) for r in rows)
        elif n == 2:
            assert [r.eval_at_us for r in rows] == list(range(0, 35001, 5000))
        elif n == 3:
            assert preview(rows[1]) == (0, 0) and rows[1].rf_evidence.value == "HEALTHY_CURRENT"
        elif n == 4:
            assert rows[2].arm_switch_requested is True and rows[2].test_state_after.value == "SELF_TEST"
            assert preview(rows[2]) == (200000, 600000)
        elif n == 5:
            assert preview(rows[3]) == (750000, 250000) and rows[3].preview_clip_tags == ()
        elif n == 6:
            assert rows[4].test_state_after.value == "SELF_TEST" and preview(rows[4]) == (None, None)
        elif n == 7:
            assert rows[6].rf_evidence.value == "LOST_CURRENT" and preview(rows[6]) == (None, None)
        elif n == 8:
            assert rows[7].test_state_after.value == "FAULT_LATCHED" and preview(rows[7]) == (None, None)
        elif n == 9:
            assert rows[2].control_evidence.value == "INVALID" and rows[2].rf_evidence.value == "LOST_CURRENT"
            assert preview(rows[2]) == (None, None)
        elif n == 10:
            assert [r.test_state_after.value for r in rows[-2:]] == ["FAULT_LATCHED", "FAULT_LATCHED"]
        elif n == 11:
            assert rows[1].control_evidence.value == "CONFLICT" and preview(rows[1]) == (None, None)
        elif n == 12:
            assert rows[2].causal_event_ids == ("frame-c-10", "frame-d-10", "rf-h-10")
            assert preview(rows[2]) == (200000, 400000)
        elif n == 13:
            assert rows[3].control_evidence.value == "INVALID" and preview(rows[3]) == (None, None)
    elif n < 19:
        assert report.outcome is (Outcome.INPUT_REJECTED if n == 14 else Outcome.REFERENCE_OR_INTENT_BLOCKED)
        assert report.shadow_tick_count == 0 and not snapshots
        assert report.e2_outcome.value == ("UPSTREAM_REJECTED" if n == 14 else
            "REFERENCE_MATCH_NO_AUTHORITY" if n in (16, 17) else "REFERENCE_MISMATCH")
        assert report.e3_outcome.value == ("INTENT_MISMATCH" if n in (16, 17) else "UPSTREAM_NOT_ELIGIBLE")
    else:
        assert report.outcome is Outcome.SHADOW_EVIDENCE_INCOMPLETE and report.blocked_at_tick == 0
        assert report.shadow_tick_count == 0 and len(journals) == 1
        assert snapshots[0].generation == 0 and snapshots[0].state.value == "BOOT"
        assert journals[0].acknowledged_append_count == 0
        assert len(journals[0].records) == (1 if n == 20 else 0)


def test_inventory():
    assert [c["id"] for c in CASES] == [f"P224-T{i:02}" for i in range(1, 21)]
