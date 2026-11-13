"""P219 recipes use real preflight/scheduling/normalization and synthetic priors."""

import json
from pathlib import Path

from bb_host_preflight_m0 import AcceptedPreflight, validate_wire
from bb_host_virtual_ticks import iter_virtual_ticks
from bb_host_batch_observations import normalize_tick_observations
from bb_host_temporal_guard_facts import PriorCommittedTimestampFacts, evaluate_temporal_guard_facts

from bb_host_safety_priority_kernel import SafetyState, assess_safety_priority
from bb_host_health_evidence import PriorCommittedRFStatus, RFStatus, assess_health_evidence

DESIGN = Path(__file__).resolve().parents[3] / "Design"


def load_source_oracles():
    return json.loads((DESIGN / "fixtures/P219_HEALTH_EVIDENCE_ORACLE_INDEX.json").read_text(encoding="utf-8"))


def dump(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def wire_bytes(recipe):
    base = json.loads((DESIGN / "fixtures/P210_MINIMAL_WIRE_V2.json").read_text(encoding="utf-8"))
    base.pop("events")
    base["duration_us"] = max(5000, recipe["eval_at_us"])
    events = []
    # Recipes are pseudo events, not wire order. Stable chronological expansion
    # enforces wire-v2 ordering while retaining source order at equal timestamps.
    for event in sorted(recipe["pseudo_events"], key=lambda e: e["event_at_us"]):
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
        envelope = {"event_id": event["id"], "event_at_us": event["event_at_us"], "type": tag}
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
    priority = assess_safety_priority(SafetyState(recipe["pre_state"]), observations, temporal)
    rf = dict(recipe["prior_rf_snapshot"])
    if rf["last_rf_status"] is not None:
        rf["last_rf_status"] = RFStatus(rf["last_rf_status"])
    prior_rf = PriorCommittedRFStatus(**rf)
    health = assess_health_evidence(observations, temporal, priority, prior_rf)
    return accepted, batch, observations, prior, temporal, priority, prior_rf, health


def synthetic_prior(recipe):
    """A separate, explicitly test-only history fixture, never parsed from wire."""
    return PriorCommittedTimestampFacts(**recipe["prior_timestamp_snapshot"])




def load_oracles():
    return json.loads((DESIGN / "fixtures/P220_GUARD_TRIAGE_ORACLE_INDEX.json").read_text(encoding="utf-8"))


def source_recipe(case):
    return next(recipe for recipe in load_source_oracles()["cases"] if recipe["id"] == case["source_case_id"])


def expected_fields(case, obs, temporal, priority):
    """Two closed declarative bindings; no fixture expression evaluation."""
    from bb_host_guard_triage import RFGuardLane, ControlGuardLane, ArmedContinuityLane, GuardReason
    expected = dict(case["expected"])
    assert expected["current_rf_candidate_original_at_us"] == "=temporal.observed_uncontested_healthy_rf_at_us"
    assert expected["current_control_candidate_original_at_us"] == "=temporal.observed_uncontested_valid_control_at_us"
    expected.update(tick_index=obs.tick_index, eval_at_us=obs.eval_at_us, pre_state=priority.pre_state,
        rf_lane=RFGuardLane(expected["rf_lane"]), control_lane=ControlGuardLane(expected["control_lane"]),
        armed_continuity_lane=ArmedContinuityLane(expected["armed_continuity_lane"]),
        unresolved_reasons=tuple(GuardReason(reason) for reason in expected["unresolved_reasons"]),
        current_rf_candidate_original_at_us=temporal.observed_uncontested_healthy_rf_at_us,
        current_control_candidate_original_at_us=temporal.observed_uncontested_valid_control_at_us)
    return expected
