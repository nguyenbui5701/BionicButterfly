import ast
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
import importlib.metadata
import locale
import os
from pathlib import Path
import sys
import time
from types import MappingProxyType
from unittest.mock import Mock

import pytest
from bb_host_preflight_m0 import RejectedPreflight
from bb_host_virtual_ticks import VirtualTickBatch
import bb_host_batch_observations.normalizer as normalizer
from bb_host_batch_observations import normalize_tick_observations as normalize

from conftest import control, observation
from scripts.scenarios import pipeline, wire_bytes
from test_oracles import FLAGS


@pytest.mark.parametrize("first,second", [("0.1000000", "1e-1"), ("0", "-0"), ("1", "1.000000"),
                                         ("0.000001", "1e-6"), ("0.25", "250000e-6")])
def test_exact_equivalence_without_float(first, second, make_batch):
    _, batch = make_batch([control("z", 6000, flap=first), control("a", 9999, flap=second)])
    with localcontext() as context:
        context.prec = 2
        result = normalize(batch)
    assert len(result.valid_control_groups) == 1
    group = result.valid_control_groups[0]
    assert group.event_ids == ("a", "z")
    assert group.latest_original_at_us == 9999
    assert [e["event_id"] for e in group.member_events] == ["z", "a"]
    assert result.has_duplicate_semantic_control and not result.has_distinct_valid_control_conflict
    assert group.semantic_control["flap_demand"] == Decimal(first)


@pytest.mark.parametrize("change", [dict(arm=True), dict(flap="0.100001"), dict(steer="-0.000001")])
def test_each_variable_control_dimension_is_part_of_key(change, make_batch):
    first = control("one", flap="0.1")
    second = control("two", flap=change.get("flap", "0.1"), arm=change.get("arm", False), steer=change.get("steer", "0"))
    _, batch = make_batch([first, second])
    result = normalize(batch)
    assert len(result.valid_control_groups) == 2
    assert result.has_distinct_valid_control_conflict and not result.has_duplicate_semantic_control


@pytest.mark.parametrize("invalid_first", [True, False])
def test_all_three_control_flags_coexist_and_later_observations_survive(invalid_first, make_batch):
    events = [control("a"), control("b", arm=True), control("c"),
              observation("rf", "RF_LOST"), observation("cat", "CATA")]
    bad = observation("bad", "CONTROL_INVALID")
    events.insert(0 if invalid_first else len(events), bad)
    _, batch = make_batch(events)
    result = normalize(batch)
    assert result.has_invalid_control and result.has_distinct_valid_control_conflict and result.has_duplicate_semantic_control
    assert result.rf_has_lost and result.has_catastrophe
    assert len(result.source_events) == len(events)
    assert [g.event_ids for g in result.valid_control_groups] == [("a", "c"), ("b",)]


def test_all_rf_and_lifecycle_facts_independent(make_batch):
    kinds = ["RF_UNKNOWN", "RF_HEALTHY", "RF_LOST", "RESET", "ACK", "CATA", "ACK"]
    _, batch = make_batch([observation(str(i), kind) for i, kind in enumerate(kinds)])
    result = normalize(batch)
    assert result.rf_has_healthy and result.rf_has_lost and result.rf_has_unknown
    assert result.has_reset and result.has_ack and result.has_catastrophe and not result.has_boot
    assert [e["event_id"] for e in result.rf_events] == ["0", "1", "2"]
    assert len(result.source_events) == 7


def test_unicode_metadata_order_does_not_change_groups_or_source(make_batch):
    names = ["\U0001f600", "\u00e9", "e\u0301", "\u4e2d", "a", "~", "/"]
    _, batch = make_batch([control(name) for name in names])
    result = normalize(batch)
    expected = tuple(sorted(names, key=lambda value: value.encode("utf-8")))
    assert result.causal_event_ids == result.valid_control_groups[0].event_ids == expected
    assert [e["event_id"] for e in result.source_events] == names
    assert "\u00e9" in expected and "e\u0301" in expected
    assert len(expected) == len(names)


def test_multiple_invalid_controls_keep_refs_and_sorted_ids(make_batch):
    _, batch = make_batch([observation("z", "CONTROL_INVALID", 6000), observation("a", "CONTROL_INVALID", 9999)])
    result = normalize(batch)
    assert result.invalid_control_event_ids == ("a", "z")
    assert [e["event_at_us"] for e in result.source_events] == [6000, 9999]
    assert result.source_events is batch.events


def test_deep_immutability(make_batch):
    accepted, batch = make_batch([control("a"), control("b"), observation("rf", "RF_HEALTHY")])
    original = accepted.scenario["events"]
    result = normalize(batch)
    group = result.valid_control_groups[0]
    with pytest.raises(FrozenInstanceError):
        result.has_ack = True
    with pytest.raises(FrozenInstanceError):
        group.latest_original_at_us = 123
    with pytest.raises(TypeError):
        group.semantic_control["flap_demand"] = 1
    with pytest.raises(TypeError):
        group.member_events[0]["payload"]["arm_switch"] = True
    with pytest.raises(TypeError):
        group.event_ids[0] = "changed"
    with pytest.raises(TypeError):
        result.source_events[0] = {}
    with pytest.raises(TypeError):
        result.rf_events[0]["payload"]["rf_health"] = "LOST"
    assert accepted.scenario["events"] is original
    assert normalize(batch) == result


@pytest.mark.parametrize("value", [None, {}, b"{}", "{}", (), 1, True, RejectedPreflight({})])
def test_wrong_type_fails_before_result_construction(value, monkeypatch):
    output = Mock(side_effect=AssertionError("must not construct a result"))
    monkeypatch.setattr(normalizer, "NormalizedTickObservations", output)
    with pytest.raises(TypeError):
        normalize(value)
    output.assert_not_called()


@pytest.mark.parametrize("mutation", ["event_list", "mutable_event", "mutable_payload", "float", "nan", "bool_number",
                                      "wrong_tick", "wrong_time", "unknown_type", "duplicate_id", "extra_payload"])
def test_malformed_forged_wrapper_rejected(mutation, make_batch, monkeypatch):
    _, batch = make_batch([control("a")])
    event = dict(batch.events[0])
    body = dict(event["payload"])
    if mutation == "event_list":
        bad = replace(batch, events=list(batch.events))
    elif mutation == "mutable_event":
        bad = replace(batch, events=(event,))
    elif mutation == "wrong_tick":
        bad = replace(batch, tick_index=True)
    elif mutation == "duplicate_id":
        bad = replace(batch, events=batch.events * 2)
    else:
        if mutation == "mutable_payload":
            event["payload"] = body
        elif mutation in ("float", "nan", "bool_number"):
            body["flap_demand"] = {"float": 0.1, "nan": Decimal("NaN"), "bool_number": True}[mutation]
            event["payload"] = MappingProxyType(body)
        elif mutation == "wrong_time":
            event["event_at_us"] = 5000  # Left edge belongs to preceding tick.
        elif mutation == "unknown_type":
            event["type"] = "SIM_MOTOR"
        else:
            body["injected"] = []
            event["payload"] = MappingProxyType(body)
        bad = replace(batch, events=(MappingProxyType(event),))
    output = Mock(side_effect=AssertionError("no partial observation result"))
    monkeypatch.setattr(normalizer, "NormalizedTickObservations", output)
    with pytest.raises(ValueError):
        normalize(bad)
    output.assert_not_called()


def test_repeats_across_locales_and_decimal_context(make_batch):
    _, batch = make_batch([control("\u00e9", flap="0.123456"), control("e\u0301", flap="123456e-6"),
                          observation("lost", "RF_LOST")])
    expected = normalize(batch)
    original_locale, original_tz = locale.setlocale(locale.LC_ALL), os.environ.get("TZ")
    try:
        for loc, zone in (("C", "UTC0"), ("English_United States.1252", "ICT-7")):
            locale.setlocale(locale.LC_ALL, loc)
            os.environ["TZ"] = zone
            if hasattr(time, "tzset"):
                time.tzset()
            with localcontext() as context:
                context.prec = 2
                for _ in range(10):
                    assert normalize(batch) == expected
    finally:
        locale.setlocale(locale.LC_ALL, original_locale)
        if original_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = original_tz
        if hasattr(time, "tzset"):
            time.tzset()


def test_empty_tick_does_not_retain_any_facts(make_batch):
    _, full = make_batch([control("v"), observation("bad", "CONTROL_INVALID"), observation("rf", "RF_LOST")])
    _, empty = make_batch([])
    for _ in range(3):
        assert normalize(full).has_invalid_control
        result = normalize(empty)
        assert all(not getattr(result, name) for name in FLAGS)
        assert result.source_events == result.causal_event_ids == result.valid_control_groups == result.rf_events == ()


@pytest.mark.parametrize("mode", ["max_events_mixed", "many_distinct_controls"])
def test_instrumented_linear_event_visits(mode, monkeypatch):
    controls = 2000 if mode == "max_events_mixed" else 6000
    events = [control(str(i), flap="0." + f"{i % 1000 if mode == 'max_events_mixed' else i:06d}") for i in range(controls)]
    if mode == "max_events_mixed":
        events += [observation(str(i), "RESET") for i in range(controls, 19999)]
    recipe = dict(duration_us=15000, events=[observation("boot", "BOOT", 0), *events])
    raw = wire_bytes(recipe)
    assert len(raw) <= 2097152
    _, batches = pipeline(recipe)
    batch = batches[2]
    visits, lines = [], 0
    inspect_event = normalizer._inspect_event

    def counted(event):
        visits.append(event)
        return inspect_event(event)

    def trace(frame, event, arg):
        nonlocal lines
        if event == "line" and frame.f_code.co_filename == normalizer.__file__:
            lines += 1
        return trace

    monkeypatch.setattr(normalizer, "_inspect_event", counted)
    previous_trace = sys.gettrace()
    try:
        sys.settrace(trace)
        result = normalize(batch)
    finally:
        sys.settrace(previous_trace)
    assert len(visits) == len(events)
    assert all(a is b for a, b in zip(visits, batch.events))
    assert result.source_events is batch.events
    assert sum(len(g.member_events) for g in result.valid_control_groups) == controls
    assert len(result.valid_control_groups) == (1000 if mode == "max_events_mixed" else 6000)
    assert result.has_duplicate_semantic_control is (mode == "max_events_mixed")
    assert len(result.causal_event_ids) == len(events)
    assert lines < 100 * (len(events) + len(result.valid_control_groups))


def test_no_runtime_pipeline_rerun_or_io(make_batch, monkeypatch):
    import builtins
    import bb_host_preflight_m0 as preflight
    import bb_host_preflight_m0.wire as wire
    import bb_host_preflight_m0.mixer as mixer
    import bb_host_virtual_ticks as ticks
    import bb_host_virtual_ticks.scheduler as scheduler
    _, batch = make_batch([control("v"), observation("rf", "RF_LOST")])
    forbidden = Mock(side_effect=AssertionError("normalizer must be pure"))
    with monkeypatch.context() as patch:
        for module, names in ((preflight, ("validate_wire", "validateWire", "mix_m0", "mixM0", "normalizeExactMicros")),
                              (wire, ("validate_wire", "validateWire")), (mixer, ("mix_m0", "mixM0")),
                              (ticks, ("iter_virtual_ticks",)), (scheduler, ("iter_virtual_ticks",)), (builtins, ("open",))):
            for name in names:
                patch.setattr(module, name, forbidden)
        result = normalize(batch)
    assert result.rf_has_lost
    forbidden.assert_not_called()


def test_runtime_import_call_and_dependency_audit():
    for path in Path(normalizer.__file__).parent.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            assert not isinstance(node, ast.Import)
            if isinstance(node, ast.ImportFrom) and node.level == 0:
                assert node.module in {"collections.abc", "dataclasses", "decimal", "types", "bb_host_virtual_ticks"}
                if node.module == "bb_host_virtual_ticks":
                    assert [n.name for n in node.names] == ["VirtualTickBatch"]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"float", "open", "exec", "eval", "compile", "__import__", "input"}
    for name in ("bb-host-preflight-m0", "bb-host-virtual-ticks", "bb-host-batch-observations"):
        assert importlib.metadata.version(name) == "0.1.0"
