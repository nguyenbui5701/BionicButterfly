from dataclasses import asdict, fields, FrozenInstanceError

import pytest

from bb_host_arm_qualification import ArmQualificationProposal, ProposalKind, propose_arm_qualification
from bb_host_safety_priority_kernel import SafetyState
from scripts.scenarios import load_oracles, pipeline, wire_bytes

ORACLES = load_oracles()


@pytest.mark.parametrize("case", ORACLES["cases"], ids=lambda c: c["id"])
def test_p218_real_pipeline(case):
    accepted, batch, obs, prior, temporal, priority, window, verdict = pipeline(case)
    before = repr(accepted), repr(obs), asdict(prior), asdict(temporal), asdict(priority), asdict(window), asdict(verdict)
    result = propose_arm_qualification(obs, temporal, priority, window, verdict)
    expected = dict(case["expected"], tick_index=case["eval_at_us"] // 5000,
                    eval_at_us=case["eval_at_us"], pre_state=SafetyState(case["pre_state"]))
    expected["proposal_kind"] = ProposalKind(expected["proposal_kind"])
    assert type(result) is ArmQualificationProposal and asdict(result) == expected
    assert {f.name for f in fields(result)} == set(expected)
    for name, value in expected.items():
        assert type(getattr(result, name)) is type(value)
    assert result.requires_full_fsm is True
    assert result == propose_arm_qualification(obs, temporal, priority, window, verdict)
    assert before == (repr(accepted), repr(obs), asdict(prior), asdict(temporal), asdict(priority), asdict(window), asdict(verdict))
    assert obs.source_events is batch.events
    for obj, name in ((obs, "eval_at_us"), (temporal, "eval_at_us"), (priority, "pre_state"),
                      (window, "low_first_original_at_us"), (verdict, "health"), (result, "proposal_kind")):
        with pytest.raises(FrozenInstanceError):
            setattr(obj, name, None)
    with pytest.raises(TypeError):
        accepted.scenario["events"][0]["event_at_us"] = 123
    raw = wire_bytes(case)
    for name in ("pre_state", "prior_timestamp_snapshot", "prior_qualification_window", "hypothetical_verdict"):
        assert ('"'+name+'"').encode() not in raw


def test_oracle_inventory():
    assert ORACLES["count"] == len(ORACLES["cases"]) == 32
    assert [c["id"] for c in ORACLES["cases"]] == [f"P218-T{i:02}" for i in range(1, 33)]
    assert ORACLES["baseline_commit"] == "f2c9237bd4a1e2e077c15db6eb4c22ed2a250d5d"
