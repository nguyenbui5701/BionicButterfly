import ast
import locale
import os
from pathlib import Path
import time
from unittest.mock import Mock

import pytest

import bb_host_preflight_m0
import bb_host_preflight_m0.wire as wire
import bb_host_preflight_m0.mixer as mixer
from bb_host_preflight_m0 import validate_wire, canonical_sidecar
from conftest import encode


def test_rejection_never_constructs_accepted_scenario_or_mixes(monkeypatch, schema):
    construction = Mock(side_effect=AssertionError("must not build a rejected scenario"))
    mixing = Mock(side_effect=AssertionError("preflight must not mix"))
    monkeypatch.setattr(wire, "_freeze", construction)
    monkeypatch.setattr(mixer, "mix_m0", mixing)
    for raw in (b"\xff", b'{"a":NaN}', b"{}"):
        result = validate_wire(raw, schema)
        assert result.status == "VALIDATION_REJECTED"
        assert set(vars(result)) == {"status", "diagnostic"}
    construction.assert_not_called()
    mixing.assert_not_called()


def test_runtime_has_only_pure_standard_library_imports():
    """Explicit absence of runner/trace/actuator integration, not fake tick counters."""
    package = Path(bb_host_preflight_m0.__file__).parent
    allowed = {"dataclasses", "decimal", "re", "hashlib", "json", "types", "typing"}
    forbidden_calls = {"open", "exec", "eval", "compile", "__import__", "input", "breakpoint"}
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(name.name.split(".")[0] in allowed for name in node.names), path.name
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                assert node.module.split(".")[0] in allowed, path.name
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls, (path.name, node.func.id)


def test_repeated_results_across_locales_and_timezone_environment(minimal, nominal, schema):
    original_locale = locale.setlocale(locale.LC_ALL)
    original_tz = os.environ.get("TZ")
    raw = encode(nominal)
    accepted = validate_wire(raw, schema)
    minimal["scenario_id"] = "é" * 129
    rejected_raw = encode(minimal)
    expected = canonical_sidecar(validate_wire(rejected_raw, schema).diagnostic)
    configured = []
    try:
        for locale_name, zone in (("C", "UTC0"), ("English_United States.1252", "ICT-7")):
            locale.setlocale(locale.LC_ALL, locale_name)
            configured.append(locale_name)
            os.environ["TZ"] = zone
            if hasattr(time, "tzset"):
                time.tzset()
            for _ in range(10):
                assert validate_wire(raw, schema) == accepted
                assert canonical_sidecar(validate_wire(rejected_raw, schema).diagnostic) == expected
    finally:
        locale.setlocale(locale.LC_ALL, original_locale)
        if original_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = original_tz
        if hasattr(time, "tzset"):
            time.tzset()
    assert len(configured) == 2


def test_accepted_preflight_does_not_call_mixer(monkeypatch, nominal, schema):
    spy = Mock(side_effect=AssertionError("no virtual output from preflight"))
    monkeypatch.setattr(mixer, "mix_m0", spy)
    result = validate_wire(encode(nominal), schema)
    assert result.status == "ACCEPTED_PREFLIGHT"
    assert set(vars(result)) == {"scenario", "status"}
    spy.assert_not_called()
