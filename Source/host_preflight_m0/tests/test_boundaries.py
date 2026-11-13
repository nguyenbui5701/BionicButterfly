import copy
from decimal import Decimal, localcontext
import json

import pytest
from jsonschema import Draft202012Validator

from bb_host_preflight_m0 import validate_wire, PolicyLimits, canonical_sidecar
from conftest import encode


def issue(raw, schema, code, pointer=""):
    result = validate_wire(raw, schema)
    assert result.status == "VALIDATION_REJECTED"
    assert result.diagnostic["primary_issue"]["code"] == code
    assert result.diagnostic["primary_issue"]["json_pointer"] == pointer


@pytest.mark.parametrize("raw,code,pointer", [
    (b'\xef\xbb\xbf\xff', "P_UTF8_INVALID", ""),
    (b'\xef\xbb\xbf{"x":NaN}', "P_UTF8_BOM", ""),
    (b'{"approved":true,"x":NaN}', "P_JSON_NONFINITE", ""),
    (b'{"a":0,"a":0,"b":NaN}', "P_JSON_DUPLICATE_KEY", "/a"),
    (b'{"a":NaN,"b":0,"b":0}', "P_JSON_NONFINITE", ""),
    (b'{"a":,"b":NaN}', "P_JSON_SYNTAX", ""),
    (b'{"a":"\\ud800","a":0}', "P_JSON_SURROGATE", ""),
    (b'{"a":"\\ud800\\x"}', "P_JSON_SYNTAX", ""),
    (b'{"a":[{"~/":1,"\\u007e/":2}]}', "P_JSON_DUPLICATE_KEY", "/a/0/~0~1"),
    ('{"é":1,"é":2,"z":NaN}'.encode(), "P_JSON_DUPLICATE_KEY", "/é"),
    (b'{"a":1,"a" NaN}', "P_JSON_DUPLICATE_KEY", "/a"),
])
def test_multiple_lexical_errors(raw, code, pointer, schema):
    issue(raw, schema, code, pointer)


@pytest.mark.parametrize("raw", [
    b"", b" ", b"{}{}", b"//comment", b"/*comment*/{}", b'{"a":1,}', b"[1,]",
    b"[01]", b"[1.]", b"[+1]", b"[.5]", b"[1e]", b"[truex]", b"[NaNx]",
    b'{a:1}', b'{"a" 1}', b'"bad\nstring"', b'"\\q"', b'"unterminated',
    b"[}", b"{]", b"null false", b"\x0b{}",
])
def test_strict_syntax(raw, schema):
    issue(raw, schema, "P_JSON_SYNTAX")


@pytest.mark.parametrize("raw", [b"\xc0\xaf", b"\xed\xa0\x80", b"\xf4\x90\x80\x80", b"\xe2\x82"])
def test_strict_utf8(raw, schema):
    issue(raw, schema, "P_UTF8_INVALID")


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite(token, schema):
    issue(token.encode(), schema, "P_JSON_NONFINITE")


@pytest.mark.parametrize("depth", [1, 2, 8, 15, 16])
def test_duplicate_at_any_permitted_depth(depth, schema):
    raw = b'{"x":' * (depth - 1) + b'{"k":1,"k":2}' + b'}' * (depth - 1)
    issue(raw, schema, "P_JSON_DUPLICATE_KEY", "/x" * (depth - 1) + "/k")


def test_raw_and_depth_limits(minimal, schema):
    raw = encode(minimal)
    assert validate_wire(raw + b" " * (2097152 - len(raw)), schema).status == "ACCEPTED_PREFLIGHT"
    issue(b"\xff" * 2097153, schema, "P_INPUT_TOO_LARGE")
    issue(b"[" * 16 + b"0" + b"]" * 16, schema, "P_SCHEMA_TYPE")
    issue(b"[" * 17 + b"0" + b"]" * 17, schema, "P_JSON_DEPTH")


def test_event_capacity_boundary(minimal, schema):
    minimal["events"] += [dict(event_id=str(i), event_at_us=5000, type="SIM_RESET", payload={})
                          for i in range(19999)]
    raw = encode(minimal)
    assert len(raw) < 2097152
    assert validate_wire(raw, schema).status == "ACCEPTED_PREFLIGHT"
    minimal["events"].append(dict(event_id="last", event_at_us=5000, type="SIM_RESET", payload={}))
    issue(encode(minimal), schema, "P_EVENT_COUNT", "/events")


@pytest.mark.parametrize("character", ["\0", "\n", "\u001f", "\u007f", "\u0080", "\u0085", "\u009f"])
def test_identifier_controls(character, minimal, schema):
    minimal["events"][0]["event_id"] = character
    issue(encode(minimal), schema, "P_IDENTIFIER_CONTROL", "/events/0/event_id")


def test_identifier_byte_boundaries(minimal, schema):
    minimal["scenario_id"] = "é" * 128
    minimal["events"][0]["event_id"] = "😀" * 16
    assert validate_wire(encode(minimal), schema).status == "ACCEPTED_PREFLIGHT"
    minimal["events"][0]["event_id"] += "a"
    issue(encode(minimal), schema, "P_IDENTIFIER_BYTES", "/events/0/event_id")


def test_no_identifier_normalization(nominal, schema):
    nominal["events"][1]["event_id"] = "é"
    nominal["events"][2]["event_id"] = "e\u0301"
    assert validate_wire(encode(nominal), schema).status == "ACCEPTED_PREFLIGHT"


def test_surrogate_pair_and_escaped_keys(minimal, schema):
    minimal["scenario_id"] = "😀"
    assert validate_wire(encode(minimal), schema).scenario["scenario_id"] == "😀"
    minimal["~/"] = 0
    issue(encode(minimal), schema, "P_SCHEMA_UNKNOWN_FIELD", "/~0~1")


def test_schema_canonical_traversal(minimal, schema):
    minimal["approved"] = True
    minimal["context"] = "FLIGHT_TEST_APPROVED"
    minimal["schema_version"] = 1
    expected = validate_wire(encode(minimal), schema).diagnostic["primary_issue"]
    assert expected["code"] == "P_SCHEMA_UNKNOWN_FIELD"
    assert expected["json_pointer"] == "/approved"
    reversed_data = dict(reversed(list(minimal.items())))
    reversed_schema = dict(reversed(list(schema.items())))
    assert validate_wire(encode(reversed_data), reversed_schema).diagnostic["primary_issue"] == expected


def test_union_discriminant_precedes_payload(nominal, schema):
    nominal["events"][2]["type"] = "SIM_VOLTAGE_WARNING_RECOVERED"
    nominal["events"][2]["payload"] = {"bad": True}
    issue(encode(nominal), schema, "P_EVENT_TYPE", "/events/2/type")


def test_schema_before_semantics(nominal, schema):
    nominal["events"][2]["event_id"] = "boot"
    nominal["events"][7]["payload"]["flap_demand"] = 2
    issue(encode(nominal), schema, "P_SCHEMA_RANGE", "/events/7/payload/flap_demand")


def test_semantic_category_order(nominal, schema):
    nominal["events"][2]["event_id"] = "boot"
    nominal["events"][1]["event_at_us"] = 0
    nominal["events"][7]["event_at_us"] = 100
    nominal["scenario_id"] = "é" * 129
    issue(encode(nominal), schema, "P_EVENT_ID_DUPLICATE", "/events/2/event_id")
    nominal["events"][2]["event_id"] = "unique"
    issue(encode(nominal), schema, "P_BOOT_SEQUENCE", "/events/1")
    nominal["events"][1]["event_at_us"] = 10000
    issue(encode(nominal), schema, "P_EVENT_TIMESTAMP_ORDER", "/events/7/event_at_us")
    nominal["events"][7]["event_at_us"] = 160000
    issue(encode(nominal), schema, "P_EVENT_TIMESTAMP_RANGE", "/events/7/event_at_us")
    nominal["events"][7]["event_at_us"] = 150000
    nominal["events"][0]["event_id"] = "\u0085"
    issue(encode(nominal), schema, "P_IDENTIFIER_BYTES", "/scenario_id")
    nominal["scenario_id"] = "valid"
    nominal["events"][2]["payload"]["flap_demand"] = 0.0000005
    issue(encode(nominal), schema, "P_IDENTIFIER_CONTROL", "/events/0/event_id")
    nominal["events"][0]["event_id"] = "boot"
    issue(encode(nominal), schema, "P_DECIMAL_PRECISION", "/events/2/payload/flap_demand")


@pytest.mark.parametrize("mode", ["missing", "late", "nonzero", "extra", "other_t0"])
def test_boot_rules(mode, nominal, schema):
    pointer = "/events/0"
    if mode == "missing":
        nominal["events"][0]["type"] = "SIM_RESET"
    elif mode == "late":
        nominal["events"][0], nominal["events"][1] = nominal["events"][1], nominal["events"][0]
    elif mode == "nonzero":
        nominal["events"][0]["event_at_us"] = 1
    elif mode == "extra":
        nominal["events"][1].update(type="BOOT", payload={})
        pointer = "/events/1"
    else:
        nominal["events"][1]["event_at_us"] = 0
        pointer = "/events/1"
    issue(encode(nominal), schema, "P_BOOT_SEQUENCE", pointer)


def test_same_tick_distinct_controls_and_original_times(nominal, schema):
    nominal["events"][3]["event_at_us"] = nominal["events"][2]["event_at_us"] + 1
    nominal["events"][3]["payload"]["flap_demand"] = 0.5
    result = validate_wire(encode(nominal), schema)
    assert result.status == "ACCEPTED_PREFLIGHT"
    assert result.scenario["events"][3]["event_at_us"] == 15001


@pytest.mark.parametrize("token,code", [
    ("1e-6", None), ("-0", None), ("0.123456", None), ("0.1000000", None),
    ("0.0000005", "P_DECIMAL_PRECISION"), ("1e-999999999999999999999", "P_DECIMAL_PRECISION"),
    ("1e99999999999999999999999", "P_SCHEMA_RANGE"),
    ("1.00000000000000000000000000000000000001", "P_SCHEMA_RANGE"),
    ("true", "P_SCHEMA_TYPE"),
])
def test_wire_exact_tokens(token, code, nominal, schema):
    raw = encode(nominal).replace(b'"flap_demand":0,', b'"flap_demand":' + token.encode() + b",", 1)
    with localcontext() as context:
        context.prec = 2
        if code:
            issue(raw, schema, code, "/events/2/payload/flap_demand")
        else:
            result = validate_wire(raw, schema)
            assert result.scenario["events"][2]["payload"]["flap_demand"] == Decimal(token)


def test_result_is_deeply_immutable(nominal, schema):
    result = validate_wire(encode(nominal), schema)
    with pytest.raises(TypeError):
        result.scenario["events"][0]["event_id"] = "changed"
    with pytest.raises(TypeError):
        result.scenario["events"][0] = {}
    with pytest.raises(AttributeError):
        result.status = "OTHER"


def test_trusted_call_preconditions(minimal, schema):
    with pytest.raises(TypeError):
        validate_wire("{}", schema)
    with pytest.raises(ValueError):
        validate_wire(encode(minimal), schema, PolicyLimits(max_input_bytes=99999999))
    schema["additionalProperties"] = True
    with pytest.raises(ValueError):
        validate_wire(encode(minimal), schema)


def test_differential_schema_mutation_corpus(nominal, schema):
    """Reference validator checks schema acceptance independently of our traversal."""
    reference = Draft202012Validator(schema)
    paths = []

    def walk(value, path=()):
        paths.append(path)
        if isinstance(value, dict):
            for key, item in value.items():
                walk(item, path + (key,))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, path + (index,))

    walk(nominal)
    count = 0
    for path in paths:
        for replacement in (None, True, False, "bad", -1, 0.5, 60000001, {}, []):
            data = copy.deepcopy(nominal)
            if path:
                parent = data
                for segment in path[:-1]:
                    parent = parent[segment]
                parent[path[-1]] = replacement
            else:
                data = replacement
            expected_schema_valid = reference.is_valid(data)
            actual = validate_wire(encode(data), schema)
            actual_schema_valid = actual.status == "ACCEPTED_PREFLIGHT" or actual.diagnostic["primary_issue"]["stage"] == "SEMANTIC"
            assert actual_schema_valid == expected_schema_valid, (path, replacement)
            count += 1
    assert count > 500


def test_negative_truncation_corpus(nominal, schema):
    raw = encode(nominal)
    for index in range(len(raw)):
        first = validate_wire(raw[:index], schema)
        assert first.status == "VALIDATION_REJECTED", index
        assert first.diagnostic["primary_issue"]["code"] == "P_JSON_SYNTAX", index
        assert canonical_sidecar(first.diagnostic) == canonical_sidecar(validate_wire(raw[:index], schema).diagnostic)
