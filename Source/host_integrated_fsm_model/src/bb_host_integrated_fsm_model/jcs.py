"""Strict I-JSON boundary around reviewed/pinned rfc8785 0.1.4.

Binary64 is used only for JCS serialization. Model demand arithmetic stays exact
Decimal/integer. No normalization or coercion of arbitrary application objects.
"""
from decimal import Decimal
import json
import math

import rfc8785

MAX_BYTES = 16_777_216


def _validate(value, depth=0):
    if depth > 16:
        raise ValueError("JCS nesting quota")
    kind = type(value)
    if value is None or kind is bool:
        return
    if kind is str:
        value.encode("utf-8", "strict")
    elif kind is int:
        if abs(value) > 9007199254740991:
            raise ValueError("integer outside interoperable I-JSON domain")
    elif kind is float:
        if not math.isfinite(value):
            raise ValueError("nonfinite JCS number")
    elif kind is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise TypeError("JCS object keys must be strings")
            _validate(key, depth + 1)
            _validate(child, depth + 1)
    elif kind in (list, tuple):
        for child in value:
            _validate(child, depth + 1)
    else:
        raise TypeError("unsupported JCS value type")


def dumps(value):
    _validate(value)
    raw = rfc8785.dumps(value)
    if len(raw) > MAX_BYTES:
        raise ValueError("JCS byte quota")
    return raw


def loads(raw):
    if type(raw) is not bytes:
        raise TypeError("strict JSON requires bytes")
    if len(raw) > MAX_BYTES or raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("JSON quota or BOM")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def constant(value):
        raise ValueError("non-I-JSON constant")
    def number(token):
        value = float(token)
        if not math.isfinite(value) or (value == 0 and Decimal(token) != 0):
            raise ValueError("number outside binary64 range")
        return value
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                       parse_float=number, parse_constant=constant)
    _validate(value)
    return value
