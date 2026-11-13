from dataclasses import fields, FrozenInstanceError
import json

import pytest

from bb_host_snapshot_commit_gate import CommitOutcome, SnapshotCommitResult, OwnerSnapshot
from scripts.scenarios import load_oracles, recipe_for, exercise, wire_bytes

ORACLES = load_oracles()
HISTORY = ("last_accepted_control_at_us", "last_uncontested_healthy_rf_at_us", "last_rf_status", "last_rf_original_at_us")


@pytest.mark.parametrize("case", ORACLES["cases"], ids=lambda c: c["id"])
def test_p221_real_pipeline(case):
    ledger, prior, result, records = exercise(case)
    expected = case["expected"]
    assert type(result) is SnapshotCommitResult and len(fields(result)) == 5
    assert type(result.outcome) is CommitOutcome and result.outcome.value == expected["outcome"]
    assert type(result.tick_index) is type(result.eval_at_us) is int
    assert (result.tick_index, result.eval_at_us) == (records[2].tick_index, records[2].eval_at_us)
    assert result.requires_full_fsm is expected["requires_full_fsm"] is True
    assert type(ledger.snapshot) is OwnerSnapshot and len(fields(ledger.snapshot)) == 14
    assert ledger.snapshot.generation == prior.generation + expected["snapshot_advance"]
    assert ledger.journal_acknowledged_append_count == expected["journal_acknowledged_append_count"]
    assert expected["accepted_history_changed"] is False
    assert all(getattr(ledger.snapshot, name) == getattr(prior, name) for name in HISTORY)
    assert ledger.snapshot.held_micro_effort is None
    if expected["snapshot_advance"]:
        assert ledger.snapshot is not prior and ledger.snapshot.state.value == expected["next_test_state"]
        assert type(result.snapshot_generation) is int and result.snapshot_generation == ledger.snapshot.generation
        assert ledger.snapshot.last_eval_at_us == result.eval_at_us
        assert ledger.snapshot.last_tick_index == result.tick_index
        assert len(ledger.journal_records) == 1
    else:
        assert ledger.snapshot is prior and result.snapshot_generation is None
        assert expected["next_test_state"] is None
    for raw in ledger.journal_records:
        expected_record = dict(format="BB_E1_TEST_JOURNAL_V1", tick_index=result.tick_index, eval_at_us=result.eval_at_us,
                               pre_state=prior.state.value, next_test_state=(expected["next_test_state"] or prior.state.value),
                               decision_kind=expected["decision_kind"])
        assert json.loads(raw) == expected_record
        assert raw == (json.dumps(expected_record, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
    if result.outcome is CommitOutcome.DEFERRED_NEEDS_FULL_FSM:
        assert ledger.journal_records == () and ledger.journal_partial_bytes == b"" and ledger.failure_status is None
    if result.outcome is CommitOutcome.FAILED_INCOMPLETE_EVIDENCE:
        assert ledger.failure_status is CommitOutcome.FAILED_INCOMPLETE_EVIDENCE
        with pytest.raises(ValueError): ledger.commit_tick(records[2], records[4], records[5], records[7], records[8])
        assert ledger.snapshot is prior and ledger.journal_acknowledged_append_count == 0
    _, _, repeated, repeated_records = exercise(case)
    assert repeated == result
    assert tuple(repr(x) for x in records) == tuple(repr(x) for x in repeated_records)
    assert records[2].source_events is records[1].events
    assert all(any(rf is original for original in records[1].events) for rf in records[2].rf_events)
    for obj, name in ((prior, "generation"), (ledger.snapshot, "state"), (result, "outcome")):
        assert not hasattr(obj, "__dict__")
        with pytest.raises(FrozenInstanceError): setattr(obj, name, None)
    raw = wire_bytes(recipe_for(case))
    for key in ("test_only_seed", "pre_state", "prior_timestamp_snapshot", "prior_rf_snapshot", "test_journal_fault_mode", "receipt", "approved"):
        assert ('"' + key + '"').encode() not in raw


def test_oracle_inventory():
    assert ORACLES["count"] == len(ORACLES["cases"]) == 48
    assert [c["id"] for c in ORACLES["cases"]] == [f"P221-T{i:02}" for i in range(1, 49)]
    assert ORACLES["source_main_commit"] == "e61f97e388662a48a13ccb6b308954436cbb87ec"
