from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
import json
import locale
import os
import time

import pytest
from bb_host_preflight_m0 import validate_wire
from bb_host_virtual_ticks import VirtualTickBatch, iter_virtual_ticks

from conftest import ORACLES, from_recipe


def assert_immutable(accepted, batches):
    first = batches[0]
    assert [field.name for field in fields(first)] == ["tick_index", "eval_at_us", "events"]
    with pytest.raises(FrozenInstanceError):
        first.eval_at_us = 1
    with pytest.raises(FrozenInstanceError):
        first.events = ()
    with pytest.raises(TypeError):
        first.events[0] = {}
    with pytest.raises(TypeError):
        first.events[0]["event_at_us"] = 1
    with pytest.raises(TypeError):
        first.events[0]["payload"]["injected"] = True
    assert tuple(iter_virtual_ticks(accepted)) == batches


def check_determinism(accepted, expected):
    original_locale = locale.setlocale(locale.LC_ALL)
    original_tz = os.environ.get("TZ")
    try:
        for locale_name, zone in (("C", "UTC0"), ("English_United States.1252", "ICT-7")):
            locale.setlocale(locale.LC_ALL, locale_name)
            os.environ["TZ"] = zone
            if hasattr(time, "tzset"):
                time.tzset()
            for _ in range(10):
                assert tuple(iter_virtual_ticks(accepted)) == expected
    finally:
        locale.setlocale(locale.LC_ALL, original_locale)
        if original_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = original_tz
        if hasattr(time, "tzset"):
            time.tzset()


@pytest.mark.parametrize("recipe", ORACLES, ids=lambda row: row["id"])
def test_p214(recipe, minimal, accept, schema):
    data = from_recipe(recipe, minimal)
    accepted = accept(data)
    source_events = accepted.scenario["events"]
    batches = tuple(iter_virtual_ticks(accepted))
    assert len(batches) == recipe["expected_tick_count"]
    assert all(type(batch) is VirtualTickBatch for batch in batches)
    assert [batch.tick_index for batch in batches] == list(range(len(batches)))
    assert [batch.eval_at_us for batch in batches] == list(range(0, data["duration_us"] + 1, 5000))
    observed_ids = [[event["event_id"] for event in batch.events] for batch in batches]
    if recipe["id"] == "P214-T11":
        assert observed_ids == [["boot"]] + [[] for _ in range(12000)]
    elif recipe["id"] == "P214-T12":
        # The recipe's count=2 is the valid control. Its null expected_batches
        # and explicit negative assertions require zero output for bad callers.
        for invalid in (data, b"{}", validate_wire(b"{}", schema)):
            emitted = []
            with pytest.raises(TypeError):
                emitted.extend(iter_virtual_ticks(invalid))
            assert emitted == []
    else:
        assert observed_ids == recipe["expected_batches"]
    flattened = [event for batch in batches for event in batch.events]
    assert len(flattened) == len(source_events)
    assert all(actual is original for actual, original in zip(flattened, source_events))
    assert [event["event_at_us"] for event in flattened] == [event["event_at_us"] for event in data["events"]]
    # Wire numbers are exact decimals; Python float 0.2 is a different value.
    expected_events = json.loads(json.dumps(data["events"]), parse_float=Decimal)
    assert flattened == expected_events
    assert accepted.scenario["events"] is source_events
    assert len({id(batch) for batch in batches}) == len(batches)
    if recipe["id"] == "P214-T07":
        assert batches[1].events[0]["payload"] == {"uart_frame_status": "INVALID"}
    elif recipe["id"] == "P214-T08":
        assert batches[2].events[0]["payload"] != batches[2].events[1]["payload"]
    elif recipe["id"] == "P214-T09":
        assert [e["payload"]["rf_health"] for e in batches[2].events] == ["HEALTHY", "LOST"]
    elif recipe["id"] == "P214-T13":
        assert_immutable(accepted, batches)
    elif recipe["id"] == "P214-T14":
        check_determinism(accepted, batches)


def test_oracle_inventory():
    assert [row["id"] for row in ORACLES] == [f"P214-T{i:02d}" for i in range(1, 15)]
