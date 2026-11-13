from dataclasses import asdict, fields, FrozenInstanceError

import pytest

from bb_host_guard_triage import GuardTriageFacts, GuardReason, triage_guard_evidence
from scripts.scenarios import load_oracles, pipeline, source_recipe, expected_fields, wire_bytes

ORACLES = load_oracles()


@pytest.mark.parametrize("case", ORACLES["cases"], ids=lambda c: c["id"])
def test_p220_real_pipeline(case):
    recipe = source_recipe(case)
    accepted, batch, obs, prior, temporal, priority, prior_rf, health = pipeline(recipe)
    before = tuple(repr(obj) for obj in (accepted, batch, obs, prior, temporal, priority, prior_rf, health))
    result = triage_guard_evidence(obs, temporal, priority, health)
    expected = expected_fields(case, obs, temporal, priority)
    assert type(result) is GuardTriageFacts and asdict(result) == expected
    assert {f.name for f in fields(result)} == set(expected) and len(fields(result)) == 10
    for name, value in expected.items():
        assert type(getattr(result, name)) is type(value)
    assert all(type(reason) is GuardReason for reason in result.unresolved_reasons)
    assert result.unresolved_reasons[-1] is GuardReason.TRUST_NOT_PROVEN
    assert result.requires_full_fsm is True
    assert result == triage_guard_evidence(obs, temporal, priority, health)
    assert before == tuple(repr(obj) for obj in (accepted, batch, obs, prior, temporal, priority, prior_rf, health))
    assert obs.source_events is batch.events
    assert all(any(rf is original for original in batch.events) for rf in obs.rf_events)
    assert all(any(member is original for original in batch.events) for g in obs.valid_control_groups for member in g.member_events)
    assert not hasattr(result, "__dict__")
    with pytest.raises(FrozenInstanceError):
        result.requires_full_fsm = False
    raw = wire_bytes(recipe)
    for name in ("pre_state", "prior_timestamp_snapshot", "prior_rf_snapshot", "requires_full_fsm"):
        assert ('"' + name + '"').encode() not in raw


def test_oracle_inventory():
    assert ORACLES["count"] == len(ORACLES["cases"]) == 36
    assert [c["id"] for c in ORACLES["cases"]] == [f"P220-T{i:02}" for i in range(1, 37)]
    assert [c["source_case_id"] for c in ORACLES["cases"]] == [f"P219-T{i:02}" for i in range(1, 37)]
    assert ORACLES["source_main_commit"] == "7c09bb5ab4d05d16bfa53439b5dab5b465ec8b05"
    assert [s[:3] for s in ORACLES["mandatory_negative_test_families"]] == [f"N{i:02}" for i in range(1, 19)]
