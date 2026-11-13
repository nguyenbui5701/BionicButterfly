from dataclasses import asdict, fields, FrozenInstanceError

import pytest

from bb_host_health_evidence import (HealthEvidenceFacts, RFEvidenceKind, ControlEvidenceKind,
                                     assess_health_evidence)
from bb_host_safety_priority_kernel import SafetyState
from scripts.scenarios import load_oracles, pipeline, wire_bytes

ORACLES = load_oracles()


@pytest.mark.parametrize("case", ORACLES["cases"], ids=lambda c: c["id"])
def test_p219_real_pipeline(case):
    accepted, batch, obs, prior, temporal, priority, prior_rf = pipeline(case)
    before = repr(accepted), repr(obs), asdict(prior), asdict(temporal), asdict(priority), asdict(prior_rf)
    result = assess_health_evidence(obs, temporal, priority, prior_rf)
    expected = dict(case["expected"])
    expected.update(pre_state=SafetyState(expected["pre_state"]),
                    rf_evidence=RFEvidenceKind(expected["rf_evidence"]),
                    control_evidence=ControlEvidenceKind(expected["control_evidence"]))
    assert type(result) is HealthEvidenceFacts and asdict(result) == expected
    assert {f.name for f in fields(result)} == set(expected) and len(fields(result)) == 8
    for name, value in expected.items():
        assert type(getattr(result, name)) is type(value)
    assert result.requires_full_fsm is True
    assert result == assess_health_evidence(obs, temporal, priority, prior_rf)
    assert before == (repr(accepted), repr(obs), asdict(prior), asdict(temporal), asdict(priority), asdict(prior_rf))
    assert obs.source_events is batch.events
    for event in obs.rf_events:
        assert any(event is original for original in batch.events)
    for group in obs.valid_control_groups:
        assert all(any(member is event for event in batch.events) for member in group.member_events)
    for obj, name in ((prior_rf, "last_rf_status"), (result, "rf_evidence")):
        with pytest.raises(FrozenInstanceError):
            setattr(obj, name, None)
        assert not hasattr(obj, "__dict__")
    raw = wire_bytes(case)
    for name in ("pre_state", "prior_timestamp_snapshot", "prior_rf_snapshot", "requires_full_fsm"):
        assert ('"' + name + '"').encode() not in raw


def test_oracle_inventory_and_closed_enums():
    assert ORACLES["count"] == len(ORACLES["cases"]) == 36
    assert [c["id"] for c in ORACLES["cases"]] == [f"P219-T{i:02}" for i in range(1, 37)]
    assert [e.value for e in RFEvidenceKind] == ORACLES["rf_evidence_enum"]
    assert [e.value for e in ControlEvidenceKind] == ORACLES["control_evidence_enum"]
    assert ORACLES["baseline_commit"] == "a47dc157453547125f5172b4ef165c3b522ff0c8"
