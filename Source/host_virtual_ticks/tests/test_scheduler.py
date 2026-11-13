import ast
import builtins
from dataclasses import replace
import importlib.metadata
import json
from pathlib import Path
import sys
from types import MappingProxyType
from unittest.mock import Mock

import pytest
import bb_host_preflight_m0 as preflight
import bb_host_preflight_m0.mixer as mixer
import bb_host_preflight_m0.wire as wire
import bb_host_virtual_ticks.scheduler as scheduler
from bb_host_virtual_ticks import iter_virtual_ticks

from conftest import DESIGN, reset


@pytest.mark.parametrize("at,tick", [(1, 1), (4999, 1), (5000, 1), (5001, 2), (9999, 2), (10000, 2)])
def test_exact_boundary_and_final_tick(at, tick, minimal, accept):
    minimal["duration_us"] = 10000
    minimal["events"].append(reset("edge", at))
    accepted = accept(minimal)
    batches = tuple(iter_virtual_ticks(accepted))
    assert [[e["event_id"] for e in b.events] for b in batches] == [
        ["boot"], ["edge"] if tick == 1 else [], ["edge"] if tick == 2 else []]
    assert batches[tick].events[0]["event_at_us"] == at


def test_equivalent_controls_and_nonlexical_order_preserved(minimal, accept):
    body = {"uart_frame_status": "VALID", "flap_demand": 0.5, "steering_demand": 0,
            "arm_switch": True, "map_revision": "sim-map-v1"}
    minimal["events"] += [dict(event_id=name, event_at_us=5000, type="SIM_CONTROL_FRAME", payload=body)
                           for name in ("z", "a", "m")]
    batches = tuple(iter_virtual_ticks(accept(minimal)))
    assert [e["event_id"] for e in batches[1].events] == ["z", "a", "m"]
    assert len(batches[1].events) == 3
    assert all(event["payload"] == body for event in batches[1].events)


@pytest.mark.parametrize("filename", [
    "P210_MINIMAL_WIRE_V2.json", "P210_NOMINAL_M0_WIRE_V2.json", "P210_RESET_CATA_WIRE_V2.json",
    "P210_ACK_SHAPE_ONLY_V2.json", "P210_INVALID_UART_WIRE_V2.json", "P212_POSITIVE_INBAND_UART_INVALID_V2.json",
])
def test_merged_preflight_integration(filename, schema):
    raw = (DESIGN / "fixtures" / filename).read_bytes()
    accepted = preflight.validate_wire(raw, schema)
    assert type(accepted) is preflight.AcceptedPreflight
    batches = tuple(iter_virtual_ticks(accepted))
    assert len(batches) == accepted.scenario["duration_us"] // 5000 + 1
    # Independent per-event ceiling oracle (not the implementation's cursor).
    expected = [[] for _ in batches]
    for event in accepted.scenario["events"]:
        expected[(event["event_at_us"] + 4999) // 5000].append(event["event_id"])
    assert [[e["event_id"] for e in b.events] for b in batches] == expected


@pytest.mark.parametrize("invalid", [None, True, {}, [], b"{}", "{}", 1])
def test_wrong_call_fails_immediately(invalid):
    with pytest.raises(TypeError):
        iter_virtual_ticks(invalid)


def test_mutable_or_malformed_manual_wrapper_rejected(minimal, accept):
    accepted = accept(minimal)
    with pytest.raises(ValueError):
        iter_virtual_ticks(preflight.AcceptedPreflight(minimal))
    with pytest.raises(ValueError):
        iter_virtual_ticks(replace(accepted, status="VALIDATION_REJECTED"))
    for duration in (True, 0, 5001, 60000001, 5000.0):
        bad = MappingProxyType(dict(accepted.scenario, duration_us=duration))
        with pytest.raises(ValueError):
            iter_virtual_ticks(preflight.AcceptedPreflight(bad))


def test_iterators_are_one_shot_and_independent(minimal, accept):
    accepted = accept(minimal)
    first, second = iter_virtual_ticks(accepted), iter_virtual_ticks(accepted)
    assert iter(first) is first
    assert next(first) == next(second)
    assert next(first) == next(second)
    assert tuple(first) == tuple(second) == ()
    assert len(tuple(iter_virtual_ticks(accepted))) == 2


@pytest.mark.parametrize("distribution", ["sparse", "spread", "dense_final"])
def test_instrumented_linear_traversal_and_lazy_batches(distribution, minimal, accept, monkeypatch):
    minimal["duration_us"] = 60000000
    count = 2 if distribution == "sparse" else 20000
    minimal["events"] += [reset(str(i), 60000000 if distribution != "spread" else i * 3000)
                           for i in range(1, count)]
    accepted = accept(minimal)
    source = accepted.scenario["events"]
    reads, produced, line_visits = [], [], 0
    real_batch = scheduler.VirtualTickBatch

    def counted_iter(events):
        assert events is source
        for index, event in enumerate(events):
            reads.append(index)
            yield event

    def counted_batch(*args):
        produced.append(args[0])
        return real_batch(*args)

    runtime_file = scheduler.__file__

    def count_lines(frame, event, arg):
        nonlocal line_visits
        if frame.f_code.co_filename == runtime_file and event == "line":
            line_visits += 1
        return count_lines

    monkeypatch.setattr(scheduler, "iter", counted_iter, raising=False)
    monkeypatch.setattr(scheduler, "VirtualTickBatch", counted_batch)
    iterator = iter_virtual_ticks(accepted)
    assert reads == produced == []
    previous_trace = sys.gettrace()
    actual_events = []
    try:
        sys.settrace(count_lines)
        first = next(iterator)
        assert first.events == (source[0],)
        assert reads == [0, 1]  # Current event plus exactly one lookahead.
        assert produced == [0]  # Not 12001 eagerly allocated batches.
        actual_events.extend(first.events)
        for batch in iterator:
            actual_events.extend(batch.events)
    finally:
        sys.settrace(previous_trace)
    assert reads == list(range(count))  # Every source event visited exactly once.
    assert produced == list(range(12001))
    assert len(actual_events) == count
    assert all(a is b for a, b in zip(actual_events, source))
    assert line_visits < 30 * (12001 + count)  # Instrumentation, not a timing guess.


def test_early_stop_does_not_construct_future_batches(minimal, accept, monkeypatch):
    minimal["duration_us"] = 60000000
    accepted = accept(minimal)
    constructor = Mock(wraps=scheduler.VirtualTickBatch)
    monkeypatch.setattr(scheduler, "VirtualTickBatch", constructor)
    iterator = iter_virtual_ticks(accepted)
    assert next(iterator).tick_index == 0
    iterator.close()
    assert constructor.call_count == 1


def test_no_parser_mixer_or_io_calls(minimal, accept, monkeypatch):
    accepted = accept(minimal)
    forbidden = Mock(side_effect=AssertionError("scheduler must be data-only"))
    with monkeypatch.context() as patch:
        for module, names in ((preflight, ("validate_wire", "validateWire", "mix_m0", "mixM0")),
                              (wire, ("validate_wire", "validateWire")), (mixer, ("mix_m0", "mixM0"))):
            for name in names:
                patch.setattr(module, name, forbidden)
        patch.setattr(builtins, "open", forbidden)
        batches = tuple(iter_virtual_ticks(accepted))
    assert len(batches) == 2
    forbidden.assert_not_called()


def test_runtime_import_and_call_isolation():
    for path in Path(scheduler.__file__).parent.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            assert not isinstance(node, ast.Import), path.name
            if isinstance(node, ast.ImportFrom) and node.level == 0:
                assert node.module in {"collections.abc", "dataclasses", "types", "bb_host_preflight_m0"}
                if node.module == "bb_host_preflight_m0":
                    assert [name.name for name in node.names] == ["AcceptedPreflight"]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"eval", "exec", "open", "__import__", "input", "compile"}


def test_dependency_version():
    assert importlib.metadata.version("bb-host-preflight-m0") == "0.1.0"
    assert importlib.metadata.version("bb-host-virtual-ticks") == "0.1.0"
