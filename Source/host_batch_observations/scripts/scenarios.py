"""Test-only recipe serialization. Decimal strings become raw numeric tokens."""

import json
from pathlib import Path

from bb_host_preflight_m0 import AcceptedPreflight, validate_wire
from bb_host_virtual_ticks import iter_virtual_ticks

DESIGN = Path(__file__).resolve().parents[3] / "Design"


def load_oracles():
    return json.loads((DESIGN / "fixtures/P215_BATCH_NORMALIZER_ORACLE_INDEX.json").read_text(encoding="utf-8"))


def dump(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def wire_bytes(recipe):
    base = json.loads((DESIGN / "fixtures/P210_MINIMAL_WIRE_V2.json").read_text(encoding="utf-8"))
    base.pop("events")
    base["duration_us"] = recipe["duration_us"]
    events = []
    for event in recipe["events"]:
        kind = event["kind"]
        if kind == "CONTROL_VALID":
            tag = "SIM_CONTROL_FRAME"
            common = {"uart_frame_status": "VALID", "arm_switch": event["arm"], "map_revision": "sim-map-v1"}
            payload = (dump(common)[:-1] + ',"flap_demand":' + event["flap_token"]
                       + ',"steering_demand":' + event["steer_token"] + "}")
        elif kind == "CONTROL_INVALID":
            tag, payload = "SIM_CONTROL_FRAME", dump({"uart_frame_status": "INVALID"})
        elif kind.startswith("RF_"):
            tag = "SIM_RF_STATUS"
            payload = dump({"rf_health": kind[3:], "rf_provenance": "INJECTED_SIM"})
        else:
            tag = {"BOOT": "BOOT", "RESET": "SIM_RESET", "ACK": "SIM_ACK_FAULT", "CATA": "SIM_CATASTROPHIC_FAULT"}[kind]
            payload = "{}"
        envelope = {"event_id": event["id"], "event_at_us": event["at_us"], "type": tag}
        events.append(dump(envelope)[:-1] + ',"payload":' + payload + "}")
    return (dump(base)[:-1] + ',"events":[' + ",".join(events) + "]}").encode("utf-8")


def pipeline(recipe):
    raw = wire_bytes(recipe)
    schema = json.loads((DESIGN / "contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_text(encoding="utf-8"))
    accepted = validate_wire(raw, schema)
    assert type(accepted) is AcceptedPreflight, accepted
    return accepted, tuple(iter_virtual_ticks(accepted))


def target_batch(recipe):
    _, batches = pipeline(recipe)
    return batches[recipe["target_tick_us"] // 5000]
