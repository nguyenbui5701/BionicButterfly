"""P225 authored expectations; all positive upstream calls are genuine."""
import pytest
from bb_host_integrated_fsm_model import run_fsm_model, ModelOutcome
from scripts.fixtures import inputs, index

CASES = index()["cases"]


def denied(report):
    assert report.runtime_authorized is False and report.output_allowed is False
    assert report.actual_virtual_output is None and report.physical_output is None
    assert report.control_trace_sha256 is None
    for row in report.model_ticks:
        assert row.runtime_authorized is False and row.output_allowed is False
        assert row.actual_virtual_output is None and row.physical_output is None
        assert row.airborne_estimate == "UNKNOWN" and "TRUST_NOT_PROVEN" in row.triage_reasons


@pytest.mark.parametrize("case", CASES, ids=lambda c:c["id"])
def test_p225_real_pipeline(case):
    report = run_fsm_model(**inputs(case["fixture"]))
    denied(report)
    assert report.outcome is ModelOutcome.MODEL_REPLAY_COMPLETE, report.diagnostic
    row = report.model_ticks[case["eval_at_us"] // 5000]
    assert row.model_state.value == case["expected_model_state"]
    n = int(case["id"][-2:])
    snapshot = row.model_snapshot
    if n in (1,2):
        assert snapshot.control_at_us is None and row.model_effort_left_micro is None
    elif n == 3:
        assert snapshot.low_first_at_us == 15000 and snapshot.low_qualified_eval_us is None
    elif n in (4,11):
        assert snapshot.low_qualified_eval_us == row.eval_at_us
    elif n in (5,13,20):
        assert snapshot.high_edge_at_us == row.eval_at_us and snapshot.low_first_at_us is None
    elif n in (6,14):
        assert snapshot.high_edge_at_us is None and row.model_effort_left_micro is None
    elif n in (7,8):
        assert (row.model_effort_left_micro,row.model_effort_right_micro)==(250000,750000)
        assert snapshot.control_at_us==145000
        assert row.model_input_mode == ("FRESH" if n==7 else "S1_HELD")
    elif n in (9,10,21):
        assert row.model_effort_left_micro is None and "E_RF_NOT_HEALTHY" in snapshot.causes
    elif n in (12,22):
        assert snapshot.low_qualified_eval_us is None and snapshot.causes==()
        assert "R_ACK_ACCEPTED" in row.model_reasons
    elif n == 15:
        assert (row.model_effort_left_micro,row.model_effort_right_micro)==(700000,500000)
    elif n in (16,17,24):
        assert row.model_effort_left_micro is None and snapshot.held_input is None
    elif n in (18,19):
        assert snapshot.low_qualified_eval_us is None and snapshot.high_edge_at_us is None
    elif n==23:
        assert snapshot.control_at_us==10000 and snapshot.low_first_at_us is None
        assert "E_CONTROL_BATCH_CONFLICT" in row.model_reasons
    assert report.shadow_comparator_outcome == "SHADOW_DIAGNOSTICS_COMPLETE"
    assert report.shadow_comparator_tick_count == report.model_tick_count
