from dataclasses import fields
from decimal import Decimal

import pytest
from bb_host_batch_observations import normalize_tick_observations

from conftest import ORACLES
from scripts.scenarios import pipeline, wire_bytes

FORBIDDEN = {"state_after", "reason_codes", "rf_effective", "accepted_frame_at_us", "control_authorized",
             "can_arm", "output_allowed", "left_micro_effort", "right_micro_effort"}
FLAGS = {"has_invalid_control", "has_distinct_valid_control_conflict", "has_duplicate_semantic_control",
         "rf_has_healthy", "rf_has_lost", "rf_has_unknown", "has_boot", "has_reset", "has_ack", "has_catastrophe"}


@pytest.mark.parametrize("recipe", ORACLES, ids=lambda row: row["id"])
def test_p215(recipe):
    accepted, batches = pipeline(recipe)
    batch = batches[recipe["target_tick_us"] // 5000]
    # Exercise previous ticks too, so T18 detects accidental carryover.
    for earlier in batches[:batch.tick_index]:
        normalize_tick_observations(earlier)
    result = normalize_tick_observations(batch)
    expected = recipe["expected"]
    assert result.tick_index == batch.tick_index
    assert result.eval_at_us == recipe["target_tick_us"]
    assert result.source_events is batch.events
    assert [e["event_id"] for e in result.source_events] == expected["source_ids"]
    assert list(result.causal_event_ids) == expected["causal_ids_utf8_sorted"]
    assert list(result.invalid_control_event_ids) == expected["invalid_control_event_ids_utf8_sorted"]
    assert [e["payload"]["rf_health"] for e in result.rf_events] == expected["rf_observation_statuses"]
    assert {name: getattr(result, name) for name in FLAGS} == expected["flags"]
    assert all(type(getattr(result, name)) is bool for name in FLAGS)
    assert {f.name for f in fields(result)} == FLAGS | {
        "tick_index", "eval_at_us", "source_events", "causal_event_ids", "valid_control_groups",
        "invalid_control_event_ids", "rf_events"}
    assert FORBIDDEN.isdisjoint({f.name for f in fields(result)})
    assert len(result.valid_control_groups) == len(expected["valid_control_groups"])
    for group, wanted in zip(result.valid_control_groups, expected["valid_control_groups"]):
        semantic = wanted["semantic_control"]
        assert group.semantic_control == {
            "uart_frame_status": "VALID", "arm_switch": semantic["arm_switch"],
            "flap_demand": Decimal(semantic["flap_exact"]), "steering_demand": Decimal(semantic["steer_exact"]),
            "map_revision": semantic["map_revision"],
        }
        assert list(group.event_ids) == wanted["member_ids_utf8_sorted"]
        assert group.latest_original_at_us == wanted["latest_original_at_us"]
        expected_members = tuple(e for e in batch.events if e["event_id"] in set(wanted["member_ids_utf8_sorted"]))
        assert len(group.member_events) == len(expected_members)
        assert all(a is b for a, b in zip(group.member_events, expected_members))
        assert group.semantic_control is expected_members[0]["payload"]
    rf = tuple(e for e in batch.events if e["type"] == "SIM_RF_STATUS")
    assert len(rf) == len(result.rf_events)
    assert all(a is b for a, b in zip(rf, result.rf_events))
    by_id = {e["event_id"]: e for e in accepted.scenario["events"]}
    assert all(event is by_id[event["event_id"]] for event in result.source_events)
    assert normalize_tick_observations(batch) == result


def test_all_eighteen_oracles_present():
    assert [row["id"] for row in ORACLES] == [f"P215-T{i:02d}" for i in range(1, 19)]


def test_decimal_recipe_uses_unquoted_exact_tokens():
    raw = wire_bytes(next(row for row in ORACLES if row["id"] == "P215-T17"))
    assert b'"flap_demand":0.1000000' in raw
    assert b'"flap_demand":1e-1' in raw
    assert b'"flap_demand":"' not in raw
