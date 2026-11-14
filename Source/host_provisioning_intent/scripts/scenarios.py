"""P223 independent fixture recipes; all file access is test harness only."""

from dataclasses import fields, FrozenInstanceError
from hashlib import sha256
import json
from pathlib import Path

from bb_host_preflight_m0 import AcceptedPreflight, RejectedPreflight, validate_wire
from bb_host_trust_boundary import (ClaimedHostFingerprint, HostReferenceOutcome,
                                   assess_reference_host_boundary)
from bb_host_provisioning_intent import (ProvisioningIntentAssessment, ProvisioningIntentOutcome,
                                       ProvisioningIntentReason, inspect_provisioning_intent)

ROOT = Path(__file__).resolve().parents[3]
INDEX = json.loads((ROOT / "Design/fixtures/P223_HOST_PROVISIONING_INTENT_ORACLE_INDEX.json").read_text(encoding="utf-8"))
E2_INDEX = json.loads((ROOT / "Design/fixtures/P222_HOST_REFERENCE_ORACLE_INDEX.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / INDEX["source_wire_schema"]).read_text(encoding="utf-8"))
WIRE = (ROOT / INDEX["source_wire_fixture"]).read_bytes()
POLICY = (ROOT / INDEX["source_policy_bytes"]).read_bytes()
ENGINE = INDEX["engine_artifact_utf8_test_only"].encode("ascii")
SCHEDULER = INDEX["scheduler_artifact_utf8_test_only"].encode("ascii")
assert b"SYNTHETIC" in ENGINE and b"TEST_ONLY" in ENGINE
assert b"SYNTHETIC" in SCHEDULER and b"TEST_ONLY" in SCHEDULER


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


BASE_INTENT = canonical(INDEX["base_intent"])


def upstream(mode="MATCH", raw_wire=WIRE):
    if mode == "UPSTREAM_REJECTED":
        raw_wire = canonical(json.loads(raw_wire) | {"approved": True})
    preflight = validate_wire(raw_wire, SCHEMA)
    assert type(preflight) is (RejectedPreflight if mode == "UPSTREAM_REJECTED" else AcceptedPreflight)
    if type(preflight) is RejectedPreflight:
        assert preflight.diagnostic["evaluated_tick_count"] == 0
    reference = assess_reference_host_boundary(preflight, POLICY + (b"\n" if mode == "REFERENCE_MISMATCH" else b""),
                                               ClaimedHostFingerprint(**E2_INDEX["reference_host_claim"]))
    expected = "REFERENCE_MATCH_NO_AUTHORITY" if mode == "MATCH" else mode
    assert reference.outcome is HostReferenceOutcome(expected)
    assert reference.runtime_authorized is False
    return reference


def intent_variant(name="CANONICAL", overrides=None):
    value = INDEX["base_intent"] | (overrides or {})
    for key, changed in (overrides or {}).items():
        assert changed != INDEX["base_intent"][key], "ineffective field override"
    raw = canonical(value)
    if name == "CANONICAL":
        return raw
    if name == "WHITESPACE_INSERTION":
        result = raw.replace(b":", b": ", 1)
    elif name == "TRAILING_LF":
        result = raw + b"\n"
    elif name == "LEADING_BOM":
        result = b"\xef\xbb\xbf" + raw
    elif name == "DUPLICATE_JSON_KEY":
        assert raw.count(b'"context"') == 1
        result = raw.replace(b"{", b'{"context":"PC_SIM",', 1)
        assert result.count(b'"context"') == 2
    elif name in ("UNKNOWN_APPROVED_KEY", "UNKNOWN_SIGNATURE_KEY", "UNKNOWN_TRUSTED_HOST_KEY"):
        key, entry = {"UNKNOWN_APPROVED_KEY": ("approved", True), "UNKNOWN_SIGNATURE_KEY": ("signature", "fake"),
                      "UNKNOWN_TRUSTED_HOST_KEY": ("trusted_host", True)}[name]
        result = canonical(value | {key: entry})
    elif name == "MISSING_REVIEW_REFERENCE":
        del value["review_reference"]
        result = canonical(value)
    elif name == "INVALID_UTF8":
        result = b"\xff" + raw
    elif name == "JSON_ARRAY":
        result = b"[]"
    elif name == "RAW_NAN_TOKEN":
        assert raw.count(b'"scheduler_step_us":5000') == 1
        result = raw.replace(b'"scheduler_step_us":5000', b'"scheduler_step_us":NaN')
    elif name == "REVERSED_KEY_ORDER":
        ordered = json.loads(raw)
        result = json.dumps(dict(reversed(tuple(ordered.items()))), separators=(",", ":"), ensure_ascii=True).encode("ascii")
        assert json.loads(result) == ordered
    elif name == "OVERSIZED_4097":
        result = b" " * 4097
    else:
        raise ValueError(name)
    assert result != raw and type(result) is bytes
    return result


def bytes_variant(raw, name):
    if name == "EXACT":
        return raw
    if name in ("TRAILING_LF", "APPEND_LF"):
        result = raw + b"\n"
    elif name == "FLIP_FIRST":
        result = (b"Z" if raw[:1] != b"Z" else b"Y") + raw[1:]
    elif name == "TRUNCATE_LAST":
        result = raw[:-1]
        assert result
    else:
        raise ValueError(name)
    assert result != raw
    return result


def assert_result(result, expected):
    assert type(result) is ProvisioningIntentAssessment
    assert [f.name for f in fields(result)] == INDEX["output_fields"]
    assert not hasattr(result, "__dict__")
    assert type(result.outcome) is ProvisioningIntentOutcome
    assert type(result.content_consistent) is bool
    assert type(result.reasons) is tuple and all(type(r) is ProvisioningIntentReason for r in result.reasons)
    assert result.runtime_authorized is False and result.requires_owner_provisioning is True and result.requires_full_fsm is True
    assert result.reasons[-3:] == tuple(ProvisioningIntentReason)[-3:]
    for name in ("policy_sha256", "engine_artifact_sha256", "scheduler_artifact_sha256"):
        assert getattr(result, name) is None or type(getattr(result, name)) is str
    actual = {f.name: getattr(result, f.name) for f in fields(result)}
    actual["outcome"] = result.outcome.value
    actual["reasons"] = [r.value for r in result.reasons]
    assert actual == expected
    try:
        result.runtime_authorized = True
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("mutable assessment")


def exercise(case):
    reference = upstream(case["upstream_e2"])
    raw = intent_variant(case["raw_variant"], case["intent_field_overrides"])
    policy = bytes_variant(POLICY, case["policy_bytes_variant"])
    engine = bytes_variant(ENGINE, case["engine_bytes_variant"])
    scheduler = bytes_variant(SCHEDULER, case["scheduler_bytes_variant"])
    args = (reference, raw, policy, engine, scheduler)
    before = repr(args)
    result = inspect_provisioning_intent(*args)
    expected = dict(case["expected"])
    for field_name, label, selected in (("policy_sha256", "policy", policy), ("engine_artifact_sha256", "engine", engine),
                                        ("scheduler_artifact_sha256", "scheduler", scheduler)):
        if expected[field_name] is not None:
            assert expected[field_name] == f"=sha256(selected_{label}_bytes).hexdigest()"
            expected[field_name] = sha256(selected).hexdigest()
    assert_result(result, expected)
    assert inspect_provisioning_intent(*args) == result
    assert repr(args) == before
    return result
