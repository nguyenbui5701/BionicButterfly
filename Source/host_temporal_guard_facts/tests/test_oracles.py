from dataclasses import FrozenInstanceError, asdict, fields

import pytest

from bb_host_temporal_guard_facts import TemporalGuardFacts, evaluate_temporal_guard_facts
from scripts.scenarios import load_oracles, pipeline, synthetic_prior, wire_bytes

ORACLES = load_oracles()


@pytest.mark.parametrize("case", ORACLES["cases"], ids=lambda case: case["id"])
def test_p216_real_pipeline(case):
    accepted, batch, observations = pipeline(case)
    prior = synthetic_prior(case)
    before = repr(accepted), repr(observations), asdict(prior)
    result = evaluate_temporal_guard_facts(observations, prior)
    assert type(result) is TemporalGuardFacts
    assert asdict(result) == case["expected"]
    # Python bool compares equal to int: assert exact field types as well.
    for name, expected in case["expected"].items():
        assert type(getattr(result, name)) is type(expected)
    assert {f.name for f in fields(result)} == set(case["expected"])
    assert observations.source_events is batch.events
    for event in batch.events:
        assert any(event is original for original in accepted.scenario["events"])
    assert evaluate_temporal_guard_facts(observations, prior) == result
    assert before == (repr(accepted), repr(observations), asdict(prior))
    with pytest.raises(FrozenInstanceError):
        result.eval_at_us = 999
    with pytest.raises(FrozenInstanceError):
        prior.last_accepted_control_at_us = 999
    with pytest.raises(FrozenInstanceError):
        observations.eval_at_us = 999
    with pytest.raises(TypeError):
        accepted.scenario["events"][0]["event_at_us"] = 999
    assert b"prior_snapshot" not in wire_bytes(case)


def test_oracle_inventory():
    assert ORACLES["total"] == len(ORACLES["cases"]) == 22
    assert [c["id"] for c in ORACLES["cases"]] == [f"P216-T{i:02}" for i in range(1, 23)]
    assert ORACLES["baseline_commit"] == "ed106d22c52647090768ef60fb1e4c33384e9227"
