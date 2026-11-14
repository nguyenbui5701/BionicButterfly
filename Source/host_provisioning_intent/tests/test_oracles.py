import pytest
from scripts.scenarios import INDEX, exercise
from bb_host_provisioning_intent import ProvisioningIntentReason


@pytest.mark.parametrize("case", INDEX["cases"], ids=lambda c: c["id"])
def test_p223_real_pipeline(case):
    exercise(case)


def test_oracle_inventory():
    assert [c["id"] for c in INDEX["cases"]] == [f"P223-T{i:02}" for i in range(1, 49)]
    assert [r.value for r in ProvisioningIntentReason] == INDEX["ordered_reasons"]
    assert [f["id"] for f in INDEX["mandatory_negative_test_families"]] == [f"N{i:02}" for i in range(1, 19)]
