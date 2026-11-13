"""Deterministic evaluator of the pinned wire-v2 schema's keyword subset.

This is deliberately not a general-purpose JSON Schema implementation. The
public boundary verifies the complete schema fingerprint before invoking it.
Only the two frozen tagged unions exist; their discriminants select a single
branch before payload traversal, independent of backend oneOf error order.
"""

from .diagnostics import Issue
from .exact_decimal import ExactNumber


def same(value, expected):
    if isinstance(value, ExactNumber):
        return type(expected) is int and value.compare_int(expected) == 0
    return type(value) is type(expected) and value == expected


def check(value, schema: dict, path: tuple = ()):
    if "oneOf" in schema:
        is_event = len(path) == 2 and path[0] == "events"
        tag = "type" if is_event else "uart_frame_status"
        if not isinstance(value, dict):
            raise Issue("P_SCHEMA_TYPE", path)
        if tag not in value:
            raise Issue("P_SCHEMA_REQUIRED", path + (tag,))
        if not isinstance(value[tag], str):
            raise Issue("P_SCHEMA_TYPE", path + (tag,))
        branch = next((item for item in schema["oneOf"]
                       if item["properties"][tag]["const"] == value[tag]), None)
        if branch is None:
            raise Issue("P_EVENT_TYPE" if is_event else "P_SCHEMA_ENUM", path + (tag,))
        return check(value, branch, path)

    kind = schema.get("type")
    valid_type = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "boolean": type(value) is bool,
        "number": isinstance(value, ExactNumber),
        "integer": isinstance(value, ExactNumber) and value.integral,
    }
    if kind and not valid_type[kind]:
        raise Issue("P_SCHEMA_TYPE", path)
    if ("const" in schema and not same(value, schema["const"])) or (
        "enum" in schema and not any(same(value, x) for x in schema["enum"])
    ):
        code = {
            ("schema_version",): "P_WIRE_VERSION", ("context",): "P_CONTEXT_DENIED",
            ("provenance",): "P_PROVENANCE_DENIED", ("config_id",): "P_CONFIG_ID",
        }.get(path, "P_SCHEMA_ENUM")
        raise Issue(code, path)
    if isinstance(value, ExactNumber):
        bad_range = ("minimum" in schema and value.compare_int(schema["minimum"]) < 0) or (
            "maximum" in schema and value.compare_int(schema["maximum"]) > 0
        )
        if not bad_range and "multipleOf" in schema:
            bad_range = value.bounded_int() % schema["multipleOf"] != 0
        if bad_range:
            raise Issue("P_DURATION_GRID" if path == ("duration_us",) else "P_SCHEMA_RANGE", path)
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", len(value)):
            raise Issue("P_SCHEMA_RANGE", path)
    if isinstance(value, list):
        if len(value) > schema.get("maxItems", len(value)):
            raise Issue("P_EVENT_COUNT" if path == ("events",) else "P_SCHEMA_RANGE", path)
        if len(value) < schema.get("minItems", 0):
            raise Issue("P_SCHEMA_RANGE", path)
        for index, item in enumerate(value):
            check(item, schema["items"], path + (index,))
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in sorted(set(value) | set(required), key=lambda item: item.encode("utf-8")):
            child = path + (key,)
            if key not in value:
                raise Issue("P_SCHEMA_REQUIRED", child)
            if key not in properties:
                raise Issue("P_SCHEMA_UNKNOWN_FIELD", child)
            check(value[key], properties[key], child)
