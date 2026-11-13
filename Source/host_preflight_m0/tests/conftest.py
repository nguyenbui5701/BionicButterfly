from pathlib import Path
import json

import pytest

ROOT = Path(__file__).resolve().parents[3]
DESIGN = ROOT / "Design"
FIXTURES = DESIGN / "fixtures"
CONTRACTS = DESIGN / "contracts"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def encode(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


@pytest.fixture
def schema():
    return read_json(CONTRACTS / "G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json")


@pytest.fixture
def minimal():
    return read_json(FIXTURES / "P210_MINIMAL_WIRE_V2.json")


@pytest.fixture
def nominal():
    return read_json(FIXTURES / "P210_NOMINAL_M0_WIRE_V2.json")
