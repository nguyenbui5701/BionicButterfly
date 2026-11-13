from dataclasses import FrozenInstanceError, asdict, fields

import pytest

from bb_host_safety_priority_kernel import SafetyState, SafetyPriorityAssessment, assess_safety_priority
from scripts.scenarios import load_oracles, pipeline, wire_bytes

ORACLES = load_oracles()


@pytest.mark.parametrize("case", ORACLES["cases"], ids=lambda c: c["id"])
def test_p217_real_pipeline(case):
    accepted, batch, observations, prior, temporal = pipeline(case)
    before = repr(accepted), repr(observations), asdict(prior), asdict(temporal)
    state = SafetyState(case["pre_state"])  # Synthetic test input, never wire state.
    result = assess_safety_priority(state, observations, temporal)
    expected = dict(case["expected"], tick_index=case["eval_at_us"] // 5000,
                    eval_at_us=case["eval_at_us"], pre_state=state)
    if expected["provisional_next_state"] is not None:
        expected["provisional_next_state"] = SafetyState(expected["provisional_next_state"])
    assert type(result) is SafetyPriorityAssessment
    assert asdict(result) == expected
    assert {f.name for f in fields(result)} == set(expected)
    for name, value in expected.items():
        assert type(getattr(result, name)) is type(value)
    assert result.requires_full_fsm is True
    assert assess_safety_priority(state, observations, temporal) == result
    assert before == (repr(accepted), repr(observations), asdict(prior), asdict(temporal))
    assert observations.source_events is batch.events
    for instance, name in ((observations, "eval_at_us"), (prior, "last_committed_eval_at_us"),
                           (temporal, "eval_at_us"), (result, "provisional_next_state")):
        with pytest.raises(FrozenInstanceError):
            setattr(instance, name, 999)
    with pytest.raises(TypeError):
        accepted.scenario["events"][0]["event_at_us"] = 999
    raw = wire_bytes(case)
    assert b'"pre_state"' not in raw and b'"prior_snapshot"' not in raw


def test_oracle_inventory():
    assert ORACLES["count"] == len(ORACLES["cases"]) == 22
    assert [c["id"] for c in ORACLES["cases"]] == [f"P217-T{i:02}" for i in range(1, 23)]
    assert ORACLES["baseline_commit"] == "efe7fa3aff1beeb01af98b98a06593bd8e7af192"
