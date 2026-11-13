import json
from pathlib import Path

import pytest
from bb_host_preflight_m0 import AcceptedPreflight, validate_wire

ROOT = Path(__file__).resolve().parents[3]
DESIGN = ROOT / "Design"
ORACLES = json.loads((DESIGN / "fixtures/P214_TICK_BATCH_ORACLE_INDEX.json").read_text(encoding="utf-8"))["cases"]


@pytest.fixture
def schema():
    return json.loads((DESIGN / "contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_text(encoding="utf-8"))


@pytest.fixture
def minimal():
    return json.loads((DESIGN / "fixtures/P210_MINIMAL_WIRE_V2.json").read_text(encoding="utf-8"))


@pytest.fixture
def accept(schema):
    def preflight(data):
        raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
        result = validate_wire(raw, schema)
        assert isinstance(result, AcceptedPreflight), result
        return result
    return preflight


def from_recipe(recipe, minimal):
    """Fill only the payloads requested by the frozen pseudo-event recipes."""
    minimal["duration_us"] = recipe["duration_us"]
    minimal["events"] = []
    for event in recipe["events"]:
        payload = {}
        if event["type"] == "SIM_RF_STATUS":
            payload = {"rf_health": "LOST" if event["event_id"] == "rf_lost" else "HEALTHY",
                       "rf_provenance": "INJECTED_SIM"}
        elif event["type"] == "SIM_CONTROL_FRAME":
            payload = {"uart_frame_status": "INVALID"}
            if event["event_id"] != "uart_invalid":
                payload = {"uart_frame_status": "VALID", "flap_demand": 0.2 if event["event_id"] == "c_a" else 0.7,
                           "steering_demand": 0, "arm_switch": True, "map_revision": "sim-map-v1"}
        minimal["events"].append(dict(event, payload=payload))
    return minimal


def reset(event_id, at):
    return {"event_id": event_id, "event_at_us": at, "type": "SIM_RESET", "payload": {}}
