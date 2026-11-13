"""P217 recipes use real preflight/scheduling/normalization and synthetic priors."""

import json
from pathlib import Path

from bb_host_preflight_m0 import AcceptedPreflight, validate_wire
from bb_host_virtual_ticks import iter_virtual_ticks
from bb_host_batch_observations import normalize_tick_observations
from bb_host_temporal_guard_facts import PriorCommittedTimestampFacts, evaluate_temporal_guard_facts

DESIGN = Path(__file__).resolve().parents[3] / "Design"


def load_oracles():
    return json.loads((DESIGN / "fixtures/P217_SAFETY_PRIORITY_ORACLE_INDEX.json").read_text(encoding="utf-8"))


def dump(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def wire_bytes(recipe):
    base = json.loads((DESIGN / "fixtures/P210_MINIMAL_WIRE_V2.json").read_text(encoding="utf-8"))
    base.pop("events")
    base["duration_us"] = max(5000, recipe["eval_at_us"])
    events = []
    for event in recipe["pseudo_events"]:
        kind = event["kind"]
        if kind == "CONTROL_VALID":
            tag = "SIM_CONTROL_FRAME"
            common = {"uart_frame_status": "VALID", "arm_switch": event["arm"], "map_revision": "sim-map-v1"}
            # Preserve the recipe's original number spelling, with no float round-trip.
            payload = (dump(common)[:-1] + ',"flap_demand":' + event["flap"]
                       + ',"steering_demand":' + event["steer"] + "}")
        elif kind == "CONTROL_INVALID":
            tag, payload = "SIM_CONTROL_FRAME", dump({"uart_frame_status": "INVALID"})
        elif kind.startswith("RF_"):
            tag = "SIM_RF_STATUS"
            payload = dump({"rf_health": kind[3:], "rf_provenance": "INJECTED_SIM"})
        else:
            tag = {"BOOT": "BOOT", "RESET": "SIM_RESET", "ACK": "SIM_ACK_FAULT", "CATA": "SIM_CATASTROPHIC_FAULT"}[kind]
            payload = "{}"
        envelope = {"event_id": event["event_id"], "event_at_us": event["event_at_us"], "type": tag}
        events.append(dump(envelope)[:-1] + ',"payload":' + payload + "}")
    return (dump(base)[:-1] + ',"events":[' + ",".join(events) + "]}").encode("utf-8")


def pipeline(recipe):
    schema = json.loads((DESIGN / "contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_text(encoding="utf-8"))
    accepted = validate_wire(wire_bytes(recipe), schema)
    assert type(accepted) is AcceptedPreflight, accepted
    batch = next(batch for batch in iter_virtual_ticks(accepted) if batch.eval_at_us == recipe["eval_at_us"])
    observations = normalize_tick_observations(batch)
    prior = synthetic_prior(recipe)
    temporal = evaluate_temporal_guard_facts(observations, prior)
    return accepted, batch, observations, prior, temporal


def synthetic_prior(recipe):
    """A separate, explicitly test-only history fixture, never parsed from wire."""
    return PriorCommittedTimestampFacts(**recipe["prior_snapshot"])


def recipe_at(eval_at_us, *events):
    return {"eval_at_us": eval_at_us, "prior_snapshot": {
        "last_committed_eval_at_us": None if eval_at_us == 0 else eval_at_us - 5000,
        "last_accepted_control_at_us": None, "last_uncontested_healthy_rf_at_us": None},
        "pseudo_events": [
        {"event_id": "boot", "event_at_us": 0, "kind": "BOOT"}, *events]}
