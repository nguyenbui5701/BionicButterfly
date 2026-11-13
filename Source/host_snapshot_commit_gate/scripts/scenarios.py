"""P219 recipes use real preflight/scheduling/normalization and synthetic priors."""

import json
from pathlib import Path

from bb_host_preflight_m0 import AcceptedPreflight, validate_wire
from bb_host_virtual_ticks import iter_virtual_ticks
from bb_host_batch_observations import normalize_tick_observations
from bb_host_temporal_guard_facts import PriorCommittedTimestampFacts, evaluate_temporal_guard_facts

from bb_host_safety_priority_kernel import SafetyState, assess_safety_priority
from bb_host_guard_triage import triage_guard_evidence
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
    triage = triage_guard_evidence(observations, temporal, priority, health)
    return accepted, batch, observations, prior, temporal, priority, prior_rf, health, triage


def synthetic_prior(recipe):
    """A separate, explicitly test-only history fixture, never parsed from wire."""
    return PriorCommittedTimestampFacts(**recipe["prior_timestamp_snapshot"])





def load_oracles():
    return json.loads((DESIGN / "fixtures/P221_SNAPSHOT_GATE_ORACLE_INDEX.json").read_text(encoding="utf-8"))


def recipe_for(case):
    if case["source_case_id"] is not None:
        return next(c for c in load_source_oracles()["cases"] if c["id"] == case["source_case_id"])
    source = case["supplemental_test_recipe"]
    events = [{"id": "boot", "event_at_us": 0, "kind": "BOOT"}]
    for event in source["current_tick_pseudo_events"]:
        events.append({("id" if key == "event_id" else key): value for key, value in event.items()})
    return dict(eval_at_us=source["eval_at_us"], pre_state=case["pre_state"], pseudo_events=events,
        prior_timestamp_snapshot=dict(last_committed_eval_at_us=source["prior_committed_eval_at_us"],
            last_accepted_control_at_us=source["last_accepted_control_at_us"],
            last_uncontested_healthy_rf_at_us=source["last_uncontested_healthy_rf_at_us"]),
        prior_rf_snapshot=dict(last_committed_eval_at_us=source["prior_committed_eval_at_us"],
            last_rf_status=source["last_rf_status"], last_rf_original_at_us=source["last_rf_original_at_us"]))


def seed_snapshot(recipe):
    """TEST_ONLY prior owner fixture, separate from raw wire and runtime API."""
    from bb_host_snapshot_commit_gate import OwnerSnapshot, genesis_snapshot
    if recipe["eval_at_us"] == 0:
        return genesis_snapshot()
    times, rf = recipe["prior_timestamp_snapshot"], recipe["prior_rf_snapshot"]
    assert times["last_committed_eval_at_us"] == rf["last_committed_eval_at_us"] == recipe["eval_at_us"] - 5000
    return OwnerSnapshot(0, times["last_committed_eval_at_us"] // 5000, times["last_committed_eval_at_us"],
        SafetyState(recipe["pre_state"]), times["last_accepted_control_at_us"], times["last_uncontested_healthy_rf_at_us"],
        None if rf["last_rf_status"] is None else RFStatus(rf["last_rf_status"]), rf["last_rf_original_at_us"],
        None, None, None, None, None, ())


def exercise(case):
    from bb_host_snapshot_commit_gate import JournalFaultMode
    from bb_host_snapshot_commit_gate._testing import _seed_for_test
    recipe = recipe_for(case)
    records = pipeline(recipe)
    before = tuple(repr(record) for record in records)
    ledger = _seed_for_test(seed_snapshot(recipe), fault_mode=JournalFaultMode(case.get("test_journal_fault_mode", "NONE")))
    prior = ledger.snapshot
    prior_before = repr(prior)
    result = ledger.commit_tick(records[2], records[4], records[5], records[7], records[8])
    assert before == tuple(repr(record) for record in records)
    assert repr(prior) == prior_before
    return ledger, prior, result, records
