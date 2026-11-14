"""P222 test recipes; fixture I/O stays outside the pure runtime package."""

from dataclasses import fields, FrozenInstanceError
from hashlib import sha256
import json
from pathlib import Path

from bb_host_preflight_m0 import AcceptedPreflight, RejectedPreflight, validate_wire
from bb_host_trust_boundary import (ClaimedHostFingerprint, HostReferenceAssessment,
                                   HostReferenceOutcome, HostReferenceReason,
                                   assess_reference_host_boundary)

ROOT = Path(__file__).resolve().parents[3]
INDEX = json.loads((ROOT / "Design/fixtures/P222_HOST_REFERENCE_ORACLE_INDEX.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_text(encoding="utf-8"))
WIRE = (ROOT / INDEX["source_wire_fixture"]).read_bytes()
POLICY = (ROOT / INDEX["source_policy_bytes"]).read_bytes()


def claim(**overrides):
    return ClaimedHostFingerprint(**(INDEX["reference_host_claim"] | overrides))


def policy_variant(name):
    if name == "EXACT":
        return POLICY
    if name == "BYTE_FLIP":
        assert POLICY[:1] == b"{"
        result = b"[" + POLICY[1:]
    elif name == "TRAILING_LF":
        result = POLICY + b"\n"
    elif name == "LEADING_BOM":
        result = b"\xef\xbb\xbf" + POLICY
    elif name == "WHITESPACE":
        result = POLICY.replace(b":", b": ", 1)
    elif name == "REORDERED_KEYS":
        original = json.loads(POLICY)
        reversed_keys = dict(reversed(tuple(original.items())))
        result = json.dumps(reversed_keys, separators=(",", ":"), ensure_ascii=True, sort_keys=False).encode("ascii")
        assert json.loads(result) == original and list(reversed_keys) == list(original)[::-1]
    elif name == "APPROVED_TRUE_KEY":
        assert POLICY[-1:] == b"}"
        result = POLICY[:-1] + b',"approved":true}'
    elif name == "EMPTY":
        result = b""
    elif name == "INVALID_UTF8":
        result = b"\xff"
    else:
        before, after = {
            "STEP_10000": (b'"scheduler_step_us":5000', b'"scheduler_step_us":10000'),
            "OWNER_USER": (b'"owner":"SIMULATOR"', b'"owner":"USER"'),
            "RF_TIMEOUT_200001": (b'"rf_status_timeout_us":200000', b'"rf_status_timeout_us":200001'),
        }[name]
        assert POLICY.count(before) == 1
        result = POLICY.replace(before, after)
    assert type(result) is bytes and result != POLICY
    return result


def wire_variant(name):
    if name == "VALID_MINIMAL":
        return WIRE
    if name == "WIRE_BOM":
        return b"\xef\xbb\xbf" + WIRE
    if name == "DUPLICATE_JSON_KEY":
        assert WIRE.count(b'"context"') == 1
        raw = WIRE.replace(b"{", b'{"context":"PC_SIM",', 1)
        assert raw.count(b'"context"') == 2
        return raw
    data = json.loads(WIRE)
    changes = {
        "UNKNOWN_APPROVED": ("approved", True), "UNKNOWN_OWNER": ("owner", "SIMULATOR"),
        "UNKNOWN_SINK": ("output_adapter", "PWM"), "UNKNOWN_ALLOWLIST": ("policy_allowlist", ["fake"]),
        "UNKNOWN_ENGINE": ("engine_revision", "G0A1_E2_TEST_ENGINE_ONLY"),
        "UNKNOWN_SCHEDULER": ("scheduler_revision", "G0A1_E2_TEST_SCHEDULER_ONLY"),
        "WRONG_CONTEXT": ("context", "RC_PRIMARY"), "WRONG_VERSION": ("schema_version", 1),
        "WRONG_PROVENANCE": ("provenance", "RF_PRIMARY"), "WRONG_CONFIG": ("config_id", "unauthorized-config"),
    }
    if name in changes:
        key, value = changes[name]
        assert data.get(key) != value
        data[key] = value
    elif name == "WRONG_CLOCK":
        data["clock"]["step_us"] = 10000
    elif name in ("UNKNOWN_EVENT", "DUPLICATE_BOOT"):
        data["events"].append(dict(event_id="illegal" if name == "UNKNOWN_EVENT" else "boot-two",
                                   event_at_us=5000, type="UNSUPPORTED_EVENT" if name == "UNKNOWN_EVENT" else "BOOT", payload={}))
    else:
        raise ValueError("unknown wire recipe: " + name)
    assert data != json.loads(WIRE)
    return json.dumps(data, ensure_ascii=True).encode("utf-8")


def assert_assessment(result, expected):
    assert type(result) is HostReferenceAssessment
    assert [f.name for f in fields(result)] == ["outcome", "candidate_policy_sha256", "wire_schema_version",
        "reasons", "reference_pin_match", "runtime_authorized", "requires_trusted_host_provisioning", "requires_full_fsm"]
    assert not hasattr(result, "__dict__")
    assert type(result.outcome) is HostReferenceOutcome
    assert type(result.reasons) is tuple and all(type(r) is HostReferenceReason for r in result.reasons)
    assert result.runtime_authorized is False
    assert result.requires_trusted_host_provisioning is True and result.requires_full_fsm is True
    assert type(result.reference_pin_match) is bool
    assert result.wire_schema_version is None or type(result.wire_schema_version) is int
    assert result.candidate_policy_sha256 is None or type(result.candidate_policy_sha256) is str
    actual = {f.name: getattr(result, f.name) for f in fields(result)}
    actual["outcome"] = result.outcome.value
    actual["reasons"] = [r.value for r in result.reasons]
    assert actual == expected
    assert actual["reasons"][-2:] == ["HOST_IDENTITY_NOT_ATTESTED", "TRUST_NOT_PROVISIONED"]
    try:
        result.runtime_authorized = True
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("mutable assessment")


def exercise(case):
    raw = wire_variant(case["wire_case"])
    selected_policy = policy_variant(case["policy_raw_variant"])
    host = claim(**case["host_overrides"])
    # Always genuine TASK-001, never a handcrafted accepted wrapper for an oracle.
    preflight = validate_wire(raw, SCHEMA)
    accepted = case["wire_case"] == "VALID_MINIMAL"
    assert type(preflight) is (AcceptedPreflight if accepted else RejectedPreflight)
    if not accepted:
        assert preflight.diagnostic["evaluated_tick_count"] == 0
        assert preflight.diagnostic["evidence_complete"] is False
    before = repr((preflight, selected_policy, host))
    result = assess_reference_host_boundary(preflight, selected_policy, host)
    expected = dict(case["expected"])
    if expected["candidate_policy_sha256"] is not None:
        assert expected["candidate_policy_sha256"] == "=sha256(selected_raw_policy_bytes).hexdigest()"
        expected["candidate_policy_sha256"] = sha256(selected_policy).hexdigest()
    assert_assessment(result, expected)
    assert assess_reference_host_boundary(preflight, selected_policy, host) == result
    assert repr((preflight, selected_policy, host)) == before
    return result
