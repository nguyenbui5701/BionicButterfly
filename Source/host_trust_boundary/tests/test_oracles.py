import pytest
from scripts.scenarios import INDEX, exercise
from bb_host_trust_boundary import HostReferenceReason


@pytest.mark.parametrize("case", INDEX["cases"], ids=lambda c: c["id"])
def test_p222_real_preflight(case):
    exercise(case)


def test_oracle_inventory():
    assert [c["id"] for c in INDEX["cases"]] == [f"P222-T{i:02}" for i in range(1, 49)]
    assert [r.value for r in HostReferenceReason] == INDEX["ordered_reasons"]
    assert len(INDEX["mandatory_negative_test_families"]) == 18
