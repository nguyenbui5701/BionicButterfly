"""Integration boundaries which must stop rather than synthesize success."""
from dataclasses import replace, fields
import json
from types import UnionType
from typing import get_args, get_origin, get_type_hints

import pytest
from bb_host_integrated_shadow_replay import run_shadow_replay, ShadowReplayOutcome
from bb_host_integrated_shadow_replay import replay
from scripts.fixtures import inputs
from scripts import verify


@pytest.mark.parametrize("mutation", ["bool_time", "bool_duration", "second_boot", "boot_later", "missing_boot"])
def test_t0_and_time_contract_rejected(mutation):
    values = inputs("minimal")
    wire = json.loads(values["scenario_raw"])
    if mutation == "bool_time":
        wire["events"][0]["event_at_us"] = False
    elif mutation == "bool_duration":
        wire["duration_us"] = True
    elif mutation == "second_boot":
        wire["events"].append(dict(wire["events"][0], event_id="second"))
    elif mutation == "boot_later":
        wire["events"][0]["event_at_us"] = 1
    else:
        wire["events"] = []
    values["scenario_raw"] = json.dumps(wire).encode()
    report = run_shadow_replay(**values)
    assert report.outcome is ShadowReplayOutcome.INPUT_REJECTED and report.shadow_ticks == ()


@pytest.mark.parametrize("mutation", ["skip", "duplicate", "extra"])
def test_scheduler_contract_error_cannot_be_success(mutation, monkeypatch):
    genuine = replay.iter_virtual_ticks
    def broken(preflight):
        batches = list(genuine(preflight))
        if mutation == "skip":
            yield batches[0]
        elif mutation == "duplicate":
            yield batches[0]
            yield batches[0]
        else:
            yield from batches
            yield replace(batches[-1], tick_index=2, eval_at_us=10000)
    monkeypatch.setattr(replay, "iter_virtual_ticks", broken)
    with pytest.raises(ValueError, match="TEST_ONLY integration"):
        run_shadow_replay(**inputs("minimal"))


@pytest.mark.parametrize("claim", [None, {}, True, "TEST_ONLY"])
def test_impossible_host_claim_type(claim):
    values = inputs("minimal")
    values["claimed_host"] = claim
    with pytest.raises(TypeError):
        run_shadow_replay(**values)


def test_developer_mode_schedules_no_old_regressions():
    assert verify.regression_targets(False) == ()
    targets = verify.regression_targets(True)
    assert len(targets) == 11 and [n for n, _ in targets] == list(range(1, 12))
    assert targets[-1][1] == ("host_provisioning_intent", "bb_host_provisioning_intent")


@pytest.mark.parametrize("preset", ["pilot", "hazard", "conflict", "minimal"])
def test_every_public_field_has_exact_contract_type(preset):
    def matches(value, annotation):
        origin = get_origin(annotation)
        if origin is UnionType:
            return any(matches(value, part) for part in get_args(annotation))
        if origin is tuple:
            element, repeated = get_args(annotation)
            assert repeated is Ellipsis
            return type(value) is tuple and all(matches(item, element) for item in value)
        return type(value) is annotation
    report = run_shadow_replay(**inputs(preset))
    for obj in (report, *report.shadow_ticks):
        hints = get_type_hints(type(obj))
        for field in fields(obj):
            assert matches(getattr(obj, field.name), hints[field.name]), field.name


@pytest.mark.parametrize("reverse", [False, True])
def test_simultaneous_reset_catastrophe_cannot_clear_latch(reverse):
    values = inputs("hazard")
    wire = json.loads(values["scenario_raw"])
    reset = dict(event_id="reset-with-catastrophe", event_at_us=20000, type="SIM_RESET", payload={})
    at = next(i for i, event in enumerate(wire["events"]) if event["event_id"] == "fault-20")
    wire["events"].insert(at + int(reverse), reset)
    values["scenario_raw"] = json.dumps(wire).encode()
    report = run_shadow_replay(**values)
    assert report.outcome is ShadowReplayOutcome.SHADOW_DIAGNOSTICS_COMPLETE
    assert report.shadow_ticks[4].causal_event_ids == ("fault-20", "reset-with-catastrophe")
    for row in report.shadow_ticks[4:]:
        assert row.test_state_after.value == "FAULT_LATCHED"
        assert row.preview_left_micro is None and row.preview_right_micro is None
