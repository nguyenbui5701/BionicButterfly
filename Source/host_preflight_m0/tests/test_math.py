from decimal import Decimal, localcontext
import json

import pytest

from bb_host_preflight_m0 import normalize_exact_micros, mix_m0
from conftest import FIXTURES

VECTORS = json.loads((FIXTURES / "P210_M0_GOLDEN_VECTORS.json").read_text(), parse_float=str, parse_int=str)["vectors"]


@pytest.mark.parametrize("vector", VECTORS, ids=lambda v: v["id"])
def test_frozen_golden(vector):
    assert mix_m0(normalize_exact_micros(vector["flap_demand"]),
                  normalize_exact_micros(vector["steering_demand"])) == (
        int(vector["left_micro_effort"]), int(vector["right_micro_effort"]), tuple(vector["mixer_clip_tags"]))


@pytest.mark.parametrize("token,expected", [
    ("1e-6", 1), ("-0", 0), ("-0.000000", 0), ("1", 1000000),
    ("-1", -1000000), ("0.123456", 123456), ("0.1000000", 100000),
    ("1000000e-6", 1000000), ("1e-0000006", 1), ("0E+99999999999999999", 0),
    ("0." + "0" * 5000 + "1e5001", 1000000),
])
def test_exact_decimal(token, expected):
    with localcontext() as context:
        context.prec = 2
        assert normalize_exact_micros(token) == expected


@pytest.mark.parametrize("token", [
    "0.0000005", "0.1234567", "1e-7", "NaN", "Infinity", "-Infinity",
    True, False, 1, 0.5, Decimal("0.5"), None, "01", "+1", ".5", "1.", " 1",
    "1e999999999999999999999999999", "1e-999999999999999999999999999",
    "1.0000000000000000000000000000000000001",
])
def test_rejected_decimal(token):
    with pytest.raises((TypeError, ValueError)):
        normalize_exact_micros(token)


@pytest.mark.parametrize("flap,steer", [(-1, 0), (1000001, 0), (0, -1000001), (0, 1000001),
                                          (True, 0), (0, False), (0.5, 0), (0, "0"), (None, 0)])
def test_invalid_direct_mixer(flap, steer):
    with pytest.raises((TypeError, ValueError)):
        mix_m0(flap, steer)


@pytest.mark.parametrize("flap,steer", [(0, 0), (1000000, 0), (500000, 500000), (500000, -500000)])
def test_equality_is_not_clipping(flap, steer):
    assert mix_m0(flap, steer)[2] == ()
