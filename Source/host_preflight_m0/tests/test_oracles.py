"""Independent frozen machine-oracle assertions and explicit raw recipes."""

import copy
from hashlib import sha256

import pytest
from jsonschema import Draft202012Validator

from bb_host_preflight_m0 import validate_wire, RejectedPreflight, AcceptedPreflight
from bb_host_preflight_m0.diagnostics import STAGES
from conftest import CONTRACTS, FIXTURES, read_json, encode

ORACLES = read_json(FIXTURES / "P212_PREFLIGHT_NEGATIVE_ORACLE_INDEX.json")["test_cases"]
REGISTRY = read_json(CONTRACTS / "G0A1_PREFLIGHT_ISSUE_REGISTRY_V1_CANDIDATE.json")["issues"]
SIDECAR = Draft202012Validator(read_json(CONTRACTS / "G0A1_PREFLIGHT_DIAGNOSTIC_V1_CANDIDATE.schema.json"))


def construct(case, minimal, nominal):
    """The mutation recipe is executable evidence; serialization stays compact."""
    number = int(case["test_id"][-2:])
    raw_cases = {
        1: b"x" * 2_097_153, 2: b"\xff", 3: b"\xef\xbb\xbf" + encode(minimal),
        4: b'{"a":}', 5: b'{"schema_version":2,"schema_version":2}',
        6: b"[" * 17 + b"0" + b"]" * 17,
    }
    if number in raw_cases:
        return raw_cases[number]
    data = copy.deepcopy(nominal if number in (8, 17, 18, 19, 20, 23) else minimal)
    if number == 7:
        data["scenario_id"] = "\ud800"
    elif number == 8:
        data["events"][2]["payload"]["flap_demand"] = float("nan")
    elif number == 9:
        del data["duration_us"]
    elif number == 10:
        data["approved"] = True
    elif number == 11:
        data["schema_version"] = 1
    elif number == 12:
        data["context"] = "FLIGHT_TEST_APPROVED"
    elif number == 13:
        data["provenance"] = "REAL_RF"
    elif number == 14:
        data["config_id"] = "unapproved"
    elif number == 15:
        data["events"][0]["type"] = "SIM_MOTOR"
    elif number == 16:
        data["duration_us"] = 5001
    elif number == 17:
        data["events"][2]["event_id"] = data["events"][1]["event_id"]
    elif number == 18:
        data["events"].insert(1, dict(event_id="boot2", event_at_us=5000, type="BOOT", payload={}))
    elif number == 19:
        data["events"][1], data["events"][2] = data["events"][2], data["events"][1]
    elif number == 20:
        data["events"][7]["event_at_us"] = 160000
    elif number == 21:
        data["scenario_id"] = "\u00e9" * 129
    elif number == 22:
        data["scenario_id"] = "\u0085"
    elif number == 23:
        data["events"][2]["payload"]["flap_demand"] = 0.0000005
    elif number == 24:
        data["events"] += [dict(event_id=str(i), event_at_us=5000, type="SIM_RESET", payload={})
                           for i in range(20000)]
    elif number == 25:
        data["events"][0]["event_at_us"] = True
    elif number == 26:
        return (FIXTURES / "P212_POSITIVE_INBAND_UART_INVALID_V2.json").read_bytes()
    return encode(data)


@pytest.mark.parametrize("case", ORACLES, ids=lambda c: c["test_id"])
def test_p212(case, minimal, nominal, schema):
    raw = construct(case, minimal, nominal)
    result = validate_wire(raw, schema)
    assert result.status == case["expected_run_status"]
    if case["expected_issue"] is None:
        assert isinstance(result, AcceptedPreflight)
        assert not hasattr(result, "diagnostic")
        return
    assert isinstance(result, RejectedPreflight)
    assert not hasattr(result, "scenario")
    diagnostic = result.diagnostic
    SIDECAR.validate(diagnostic)
    assert diagnostic["primary_issue"] == {
        "code": case["expected_issue"], "stage": case["expected_stage"],
        "json_pointer": case["expected_pointer"],
        "frozen_base_error_code": case["expected_base_error_code"],
    }
    assert diagnostic["raw_input_sha256"] == sha256(raw).hexdigest()
    assert diagnostic["evaluated_tick_count"] == case["expected_core_ticks"] == 0
    assert diagnostic["evidence_complete"] is False


@pytest.mark.parametrize("row", REGISTRY, ids=lambda row: row["code"])
def test_all_registry_codes(row, minimal, nominal, schema):
    oracle = next((case for case in ORACLES if case["expected_issue"] == row["code"]), None)
    if oracle:
        raw = construct(oracle, minimal, nominal)
    elif row["code"] == "P_SCHEMA_ENUM":
        nominal["events"][1]["payload"]["rf_health"] = "BAD"
        raw = encode(nominal)
    else:
        assert row["code"] == "P_SCHEMA_RANGE"
        nominal["events"][2]["payload"]["flap_demand"] = 2
        raw = encode(nominal)
    diagnostic = validate_wire(raw, schema).diagnostic
    SIDECAR.validate(diagnostic)
    assert diagnostic["primary_issue"]["code"] == row["code"]
    assert diagnostic["primary_issue"]["stage"] == row["stage"] == STAGES[row["code"]]
    assert diagnostic["primary_issue"]["frozen_base_error_code"] == row["frozen_base_error_code"]


@pytest.mark.parametrize("filename", [
    "P210_MINIMAL_WIRE_V2.json", "P210_NOMINAL_M0_WIRE_V2.json",
    "P210_RESET_CATA_WIRE_V2.json", "P210_ACK_SHAPE_ONLY_V2.json",
    "P210_INVALID_UART_WIRE_V2.json", "P212_POSITIVE_INBAND_UART_INVALID_V2.json",
])
def test_all_positive_examples(filename, schema):
    assert validate_wire((FIXTURES / filename).read_bytes(), schema).status == "ACCEPTED_PREFLIGHT"


@pytest.mark.parametrize("case", read_json(FIXTURES / "P212_REFERENCE_REJECTION_DIAGNOSTICS.json")["cases"])
def test_reference_sidecars(case, schema):
    raw = (FIXTURES / case["fixture"].split("/")[-1]).read_bytes()
    assert validate_wire(raw, schema).diagnostic == case["expected_diagnostic"]


def test_registry_inventory():
    assert len(REGISTRY) == len(STAGES) == 27
    assert set(STAGES) == {row["code"] for row in REGISTRY}
