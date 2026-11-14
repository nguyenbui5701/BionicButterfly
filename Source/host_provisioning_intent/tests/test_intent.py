"""Explicit N01-N18 adversarial families. Full N18 operations live in verify.py."""

import ast
import builtins
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal, localcontext
from enum import Enum
import hashlib
import inspect
import json
import locale
import os
from pathlib import Path
import random
import socket
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest
import bb_host_trust_boundary as e2
import bb_host_preflight_m0 as preflight_api
import bb_host_provisioning_intent as api
from bb_host_provisioning_intent import (ProvisioningIntentOutcome as Outcome,
                                       ProvisioningIntentReason as Reason,
                                       inspect_provisioning_intent as check)
from bb_host_provisioning_intent import intent
from scripts.scenarios import (INDEX, E2_INDEX, SCHEMA, WIRE, POLICY, ENGINE, SCHEDULER,
                               ROOT, BASE_INTENT, canonical, upstream, exercise, intent_variant)


@pytest.fixture
def reference():
    return upstream()


def call(reference, raw=BASE_INTENT, policy=POLICY, engine=ENGINE, scheduler=SCHEDULER):
    return check(reference, raw, policy, engine, scheduler)


def denied(result):
    assert result.runtime_authorized is False
    assert result.requires_owner_provisioning is True and result.requires_full_fsm is True
    assert result.reasons[-3:] == (Reason.OWNER_SIGNOFF_MISSING, Reason.PROTECTED_INSTALL_NOT_PROVEN,
                                  Reason.HOST_IDENTITY_NOT_ATTESTED)


def malformed(result):
    denied(result)
    assert result.outcome is Outcome.MALFORMED_INTENT and result.content_consistent is False
    assert (result.policy_sha256, result.engine_artifact_sha256, result.scheduler_artifact_sha256) == (None, None, None)
    assert result.reasons == (Reason.MALFORMED_INTENT, Reason.OWNER_SIGNOFF_MISSING,
                              Reason.PROTECTED_INSTALL_NOT_PROVEN, Reason.HOST_IDENTITY_NOT_ATTESTED)


def forbidden(*args, **kwargs):
    raise AssertionError("forbidden parse/hash/IO/authority path invoked")


class StringSubclass(str):
    pass


class BytesSubclass(bytes):
    def __bytes__(self):
        raise AssertionError("no conversion")


class TupleSubclass(tuple):
    pass


class WrongEnum(str, Enum):
    MATCH = "REFERENCE_MATCH_NO_AUTHORITY"


@pytest.mark.parametrize("wrong", [None, {}, [], True, SimpleNamespace(), lambda: True, object()])
def test_N01_wrong_reference_type(wrong):
    with pytest.raises(TypeError):
        call(wrong)


@pytest.mark.parametrize("slot", range(4))
@pytest.mark.parametrize("wrong", [None, "bytes", bytearray(b"bytes"), memoryview(b"bytes"), BytesSubclass(b"bytes"), {}, lambda: b"bytes"])
def test_N01_exact_payload_types(reference, slot, wrong, monkeypatch):
    args = [BASE_INTENT, POLICY, ENGINE, SCHEDULER]
    args[slot] = wrong
    with monkeypatch.context() as patch:
        patch.setattr(intent.json, "loads", forbidden)
        patch.setattr(intent.hashlib, "sha256", forbidden)
        with pytest.raises(TypeError):
            check(reference, *args)


@pytest.mark.parametrize("field,value", [
    ("outcome", "REFERENCE_MATCH_NO_AUTHORITY"), ("outcome", WrongEnum.MATCH),
    ("outcome", e2.HostReferenceOutcome.REFERENCE_MISMATCH),
    ("outcome", e2.HostReferenceOutcome.UPSTREAM_REJECTED),
    ("runtime_authorized", True), ("runtime_authorized", 0),
    ("requires_trusted_host_provisioning", False), ("requires_trusted_host_provisioning", 1),
    ("requires_full_fsm", False), ("requires_full_fsm", 1),
    ("reference_pin_match", 1), ("reference_pin_match", False),
    ("wire_schema_version", True), ("wire_schema_version", 2.0),
    ("wire_schema_version", Decimal(2)), ("wire_schema_version", "2"), ("wire_schema_version", None),
    ("candidate_policy_sha256", None), ("candidate_policy_sha256", "0" * 64),
    ("candidate_policy_sha256", "g" * 64), ("candidate_policy_sha256", "a" * 63),
    ("candidate_policy_sha256", StringSubclass(INDEX["base_intent"]["policy_sha256"])),
    ("reasons", []), ("reasons", ()), ("reasons", tuple(e2.HostReferenceReason) * 1000),
    ("reasons", ("HOST_IDENTITY_NOT_ATTESTED", "TRUST_NOT_PROVISIONED")),
    ("reasons", TupleSubclass(tuple(e2.HostReferenceReason)[-2:])),
    ("reasons", tuple(e2.HostReferenceReason)[-2:][::-1]),
    ("reasons", (e2.HostReferenceReason.OWNER_MISMATCH,) + tuple(e2.HostReferenceReason)[-2:]),
])
def test_N01_tampered_e2_fields(reference, field, value):
    object.__setattr__(reference, field, value)
    with pytest.raises((TypeError, ValueError)):
        call(reference)


@pytest.mark.parametrize("mode", ["UPSTREAM_REJECTED", "REFERENCE_MISMATCH"])
@pytest.mark.parametrize("field,value", [("reference_pin_match", True), ("reasons", tuple(e2.HostReferenceReason)[-2:]),
                                         ("wire_schema_version", False), ("candidate_policy_sha256", "bad")])
def test_N01_nonmatch_inconsistent_fields(mode, field, value):
    ref = upstream(mode)
    object.__setattr__(ref, field, value)
    with pytest.raises((TypeError, ValueError)):
        call(ref)


def test_N01_reference_subclass_uninitialized_and_kwargs(reference):
    class Spoof(e2.HostReferenceAssessment):
        pass
    args = {f.name: getattr(reference, f.name) for f in fields(reference) if f.init}
    with pytest.raises(TypeError):
        call(Spoof(**args))
    with pytest.raises(ValueError):
        call(object.__new__(e2.HostReferenceAssessment))
    with pytest.raises(TypeError):
        check(reference, BASE_INTENT, POLICY, ENGINE, SCHEDULER, approved=True)


@pytest.mark.parametrize("size", [4096, 4097])
def test_N02_manifest_exact_quota(reference, size, monkeypatch):
    data = dict(INDEX["base_intent"])
    data["review_reference"] = ""
    data["review_reference"] = "T" * (size - len(canonical(data)))
    raw = canonical(data)
    assert len(raw) == size
    if size == 4096:
        result = call(reference, raw)
        assert result.reasons[0] is Reason.REVIEW_REFERENCE_MISMATCH
        assert result.outcome is Outcome.INTENT_MISMATCH
    else:
        with monkeypatch.context() as patch:
            patch.setattr(intent.json, "loads", forbidden)
            patch.setattr(intent.hashlib, "sha256", forbidden)
            malformed(call(reference, raw))


@pytest.mark.parametrize("slot", ["policy", "engine", "scheduler"])
@pytest.mark.parametrize("size", [0, 1, 1_048_576, 1_048_577])
def test_N02_artifact_policy_quotas(reference, slot, size, monkeypatch):
    payload = (b"TEST_ONLY_SYNTHETIC_" * ((size // 20) + 2))[:size]
    assert len(payload) == size
    kwargs = {slot: payload}
    if size > 1_048_576 or (size == 0 and slot != "policy"):
        with monkeypatch.context() as patch:
            patch.setattr(intent.json, "loads", forbidden)
            patch.setattr(intent.hashlib, "sha256", forbidden)
            with pytest.raises(ValueError):
                call(reference, **kwargs)
    else:
        result = call(reference, **kwargs)
        assert result.outcome is Outcome.INTENT_MISMATCH
        denied(result)
        field = "policy_sha256" if slot == "policy" else slot + "_artifact_sha256"
        assert getattr(result, field) == hashlib.sha256(payload).hexdigest()


@pytest.mark.parametrize("mode", ["UPSTREAM_REJECTED", "REFERENCE_MISMATCH"])
def test_N02_wrong_argument_quota_precedes_upstream(mode):
    ref = upstream(mode)
    for args in ({"engine": b""}, {"scheduler": b""}, {"policy": b"T" * 1_048_577}):
        with pytest.raises(ValueError):
            call(ref, **args)
    assert call(ref, b" " * 4097).outcome is Outcome.UPSTREAM_NOT_ELIGIBLE


@pytest.mark.parametrize("variant", [name for name in INDEX["raw_variant_instructions"] if name != "CANONICAL"])
def test_N03_raw_manifest_variants_no_hash(reference, variant, monkeypatch):
    raw = intent_variant(variant)
    with monkeypatch.context() as patch:
        patch.setattr(intent.hashlib, "sha256", forbidden)
        malformed(call(reference, raw))


@pytest.mark.parametrize("raw", [b"", b"null", b"true", b"0", b'"text"', b"{}{}", b"{", b"\x00", b"\xff",
    b"[" * 1500 + b"]" * 1500,
    BASE_INTENT.replace(b"PC_SIM", b"PC_S\\u0406M", 1),
    BASE_INTENT.replace(b"PC_SIM", b"\\u0050C_SIM", 1),
    BASE_INTENT.replace(b"PC_SIM", "PC_SІM".encode("utf-8"), 1),
    BASE_INTENT + b"\r\n", b" " + BASE_INTENT])
def test_N03_ascii_encoding_and_syntax(reference, raw, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr(intent.hashlib, "sha256", forbidden)
        malformed(call(reference, raw))


@pytest.mark.parametrize("field", INDEX["base_intent"])
def test_N04_each_missing_and_duplicate_field(reference, field):
    data = dict(INDEX["base_intent"])
    del data[field]
    malformed(call(reference, canonical(data)))
    duplicate = canonical({field: INDEX["base_intent"][field]})[1:-1]
    raw = b"{" + duplicate + b"," + BASE_INTENT[1:]
    malformed(call(reference, raw))


@pytest.mark.parametrize("field", INDEX["base_intent"])
@pytest.mark.parametrize("value", [{}, [], {"context": "PC_SIM"}, ["TEST_ONLY"]])
def test_N04_nested_or_array_field(reference, field, value):
    malformed(call(reference, canonical(INDEX["base_intent"] | {field: value})))


NUMERIC_FIELDS = [key for key, value in INDEX["base_intent"].items() if type(value) is int]


@pytest.mark.parametrize("field", NUMERIC_FIELDS)
@pytest.mark.parametrize("token", [b"NaN", b"Infinity", b"-Infinity", b"true", b"false", b"null", b"2.0", b"5e3", b'"5000"', b"01", b"-0"])
def test_N05_strict_numeric_tokens(reference, field, token, monkeypatch):
    original = canonical({field: INDEX["base_intent"][field]})[1:-1]
    raw = BASE_INTENT.replace(original, b'"' + field.encode() + b'":' + token)
    assert raw != BASE_INTENT
    with monkeypatch.context() as patch:
        patch.setattr(intent.hashlib, "sha256", forbidden)
        malformed(call(reference, raw))


@pytest.mark.parametrize("field", ["policy_sha256", "engine_artifact_sha256", "scheduler_artifact_sha256"])
@pytest.mark.parametrize("value", ["A" * 64, "g" * 64, "a" * 63, "a" * 65, "", True, 1, None, "é" * 64, "0x" + "a" * 62])
def test_N06_digest_shape(reference, field, value, monkeypatch):
    raw = canonical(INDEX["base_intent"] | {field: value})
    with monkeypatch.context() as patch:
        patch.setattr(intent.hashlib, "sha256", forbidden)
        malformed(call(reference, raw))


@pytest.mark.parametrize("case", INDEX["cases"][1:25], ids=lambda c: c["id"])
def test_N07_reference_field_mismatches(case):
    denied(exercise(case))


@pytest.mark.parametrize("policy", [POLICY + b"\n", b"\xef\xbb\xbf" + POLICY, b"", POLICY.replace(b":", b": ", 1), POLICY[:-1]])
def test_N08_self_declared_changed_policy_still_mismatch(reference, policy):
    data = INDEX["base_intent"] | {"policy_sha256": hashlib.sha256(policy).hexdigest()}
    result = call(reference, canonical(data), policy=policy)
    assert result.outcome is Outcome.INTENT_MISMATCH
    assert result.reasons.count(Reason.POLICY_DIGEST_MISMATCH) == 1
    assert len(result.reasons) == 4
    assert result.policy_sha256 == hashlib.sha256(policy).hexdigest()
    denied(result)


def test_N08_frozen_digest(reference):
    assert hashlib.sha256(POLICY).hexdigest() == "d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10"
    assert not POLICY.endswith(b"\n")
    result = call(reference, canonical(INDEX["base_intent"] | {"policy_sha256": "0" * 64}))
    assert result.reasons[0] is Reason.POLICY_DIGEST_MISMATCH
    denied(result)


@pytest.mark.parametrize("payload", [ENGINE + b"\n", ENGINE[:-1], b"T", b"TEST_ONLY_NEW_SYNTHETIC_ENGINE"])
def test_N09_engine_binding_not_identity(reference, payload):
    mismatch = call(reference, engine=payload)
    assert mismatch.reasons[0] is Reason.ENGINE_DIGEST_MISMATCH
    data = INDEX["base_intent"] | {"engine_artifact_sha256": hashlib.sha256(payload).hexdigest()}
    consistent = call(reference, canonical(data), engine=payload)
    assert consistent.outcome is Outcome.INTENT_CONSISTENT_UNPROVISIONED
    denied(consistent)


@pytest.mark.parametrize("payload", [SCHEDULER + b"\n", SCHEDULER[:-1], b"T", b"TEST_ONLY_NEW_SYNTHETIC_SCHEDULER"])
def test_N10_scheduler_binding_not_identity(reference, payload):
    mismatch = call(reference, scheduler=payload)
    assert mismatch.reasons[0] is Reason.SCHEDULER_DIGEST_MISMATCH
    data = INDEX["base_intent"] | {"scheduler_artifact_sha256": hashlib.sha256(payload).hexdigest()}
    consistent = call(reference, canonical(data), scheduler=payload)
    assert consistent.outcome is Outcome.INTENT_CONSISTENT_UNPROVISIONED
    denied(consistent)


@pytest.mark.parametrize("key", ["signature", "trusted_host", "approved", "owner_approval", "allowlist", "approval_token", "install_receipt", "output_adapter"])
def test_N11_injected_authority_fields(reference, key):
    malformed(call(reference, canonical(INDEX["base_intent"] | {key: "TEST_ONLY_FAKE_ASSERTION"})))
    with pytest.raises(TypeError):
        check(reference, BASE_INTENT, POLICY, ENGINE, SCHEDULER, **{key: True})


def test_N11_owner_chat_and_e2_e3_separation(reference):
    approval = (ROOT / "Design/contracts/G0A1_OWNER_APPROVAL_R1.record.json").read_bytes()
    assert json.loads(approval)["trusted_runtime_policy_allowlist_provisioned"] is False
    malformed(call(reference, approval))
    e3_claim = E2_INDEX["reference_host_claim"] | {
        "engine_revision": INDEX["base_intent"]["engine_revision"],
        "scheduler_revision": INDEX["base_intent"]["scheduler_revision"]}
    preflight = preflight_api.validate_wire(WIRE, SCHEMA)
    ref = e2.assess_reference_host_boundary(preflight, POLICY, e2.ClaimedHostFingerprint(**e3_claim))
    assert ref.outcome is e2.HostReferenceOutcome.REFERENCE_MISMATCH
    assert call(ref).outcome is Outcome.UPSTREAM_NOT_ELIGIBLE


@pytest.mark.parametrize("mode", ["UPSTREAM_REJECTED", "REFERENCE_MISMATCH"])
@pytest.mark.parametrize("raw", [BASE_INTENT, b"\xff", b" " * 4097])
def test_N12_ineligible_short_circuit(mode, raw, monkeypatch):
    ref = upstream(mode)
    with monkeypatch.context() as patch:
        patch.setattr(intent.json, "loads", forbidden)
        patch.setattr(intent.hashlib, "sha256", forbidden)
        result = call(ref, raw)
    assert result.outcome is Outcome.UPSTREAM_NOT_ELIGIBLE
    assert result.content_consistent is False
    assert (result.policy_sha256, result.engine_artifact_sha256, result.scheduler_artifact_sha256) == (None, None, None)
    assert result.reasons[0] is Reason.UPSTREAM_NOT_ELIGIBLE
    denied(result)


def test_N12_malformed_reference_before_parser_hash(reference, monkeypatch):
    object.__setattr__(reference, "runtime_authorized", True)
    with monkeypatch.context() as patch:
        patch.setattr(intent.json, "loads", forbidden)
        patch.setattr(intent.hashlib, "sha256", forbidden)
        with pytest.raises(ValueError):
            call(reference)


def test_N13_identical_forgery_is_not_credential(reference):
    fake = e2.HostReferenceAssessment(**{f.name: getattr(reference, f.name) for f in fields(reference) if f.init})
    assert fake == reference and fake is not reference
    result = call(fake)
    assert result.outcome is Outcome.INTENT_CONSISTENT_UNPROVISIONED
    denied(result)


def test_N14_exact_reason_order_and_deduplication(reference):
    assert [r.value for r in Reason] == INDEX["ordered_reasons"] and len(Reason) == 21
    result = call(reference, canonical(INDEX["base_intent"] | INDEX["field_mismatch_values"]))
    assert result.reasons == tuple(Reason)[2:]
    assert result.content_consistent is False
    denied(result)


@pytest.mark.parametrize("loc", ["C", "English_United States.1252"])
@pytest.mark.parametrize("tz", ["UTC0", "ICT-7"])
@pytest.mark.parametrize("precision", [2, 50])
def test_N14_locale_timezone_decimal_independence(reference, loc, tz, precision, monkeypatch):
    expected = call(reference)
    previous_locale = locale.setlocale(locale.LC_ALL)
    previous_tz = os.environ.get("TZ")
    before = repr((reference, BASE_INTENT, POLICY, ENGINE, SCHEDULER))
    try:
        locale.setlocale(locale.LC_ALL, loc)
        monkeypatch.setenv("TZ", tz)
        if hasattr(time, "tzset"):
            time.tzset()
        with localcontext() as ctx:
            ctx.prec = precision
            for _ in range(3):
                assert call(reference) == expected
        assert repr((reference, BASE_INTENT, POLICY, ENGINE, SCHEDULER)) == before
    finally:
        locale.setlocale(locale.LC_ALL, previous_locale)
        if previous_tz is None:
            monkeypatch.delenv("TZ", raising=False)
        else:
            monkeypatch.setenv("TZ", previous_tz)
        if hasattr(time, "tzset"):
            time.tzset()


def test_N15_frozen_closed_nine_field_api(reference):
    result = call(reference)
    assert [f.name for f in fields(result)] == INDEX["output_fields"]
    assert len(fields(result)) == 9 and not hasattr(result, "__dict__")
    assert api.__all__ == ("ProvisioningIntentAssessment", "ProvisioningIntentOutcome", "ProvisioningIntentReason", "inspect_provisioning_intent")
    assert list(inspect.signature(check).parameters) == ["reference", "intent_raw", "policy_raw", "engine_artifact", "scheduler_artifact"]
    for f in fields(result):
        with pytest.raises(FrozenInstanceError):
            setattr(result, f.name, None)
    for name in ("runtime_authorized", "requires_owner_provisioning", "requires_full_fsm"):
        with pytest.raises(ValueError):
            replace(result, **{name: False})
        assert next(f for f in fields(result) if f.name == name).init is False
    denied(result)


def test_N16_runtime_imports_and_no_mutable_global_vectors():
    allowed = {"dataclasses", "enum", "hashlib", "json", "bb_host_trust_boundary", "intent"}
    banned = {"open", "exec", "eval", "compile", "__import__", "validate_wire", "assess_reference_host_boundary", "commit_tick", "mix_m0"}
    for path in Path(intent.__file__).parent.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(a.name in allowed for a in node.names)
            if isinstance(node, ast.ImportFrom):
                assert node.module in allowed
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
                assert name not in banned
        for node in tree.body:
            if isinstance(node, ast.Assign):
                assert not isinstance(node.value, (ast.Dict, ast.List, ast.Set))


def test_N16_runtime_side_effect_spies(reference, monkeypatch):
    with monkeypatch.context() as patch:
        for obj, name in ((builtins, "open"), (Path, "open"), (os, "getenv"), (socket, "socket"),
                          (subprocess, "Popen"), (time, "time"), (time, "monotonic"),
                          (random, "random"), (os, "urandom")):
            patch.setattr(obj, name, forbidden)
        denied(call(reference))
        malformed(call(reference, b"[]"))


@pytest.mark.parametrize("count", [1, 1000, 20_000])
def test_N17_no_event_rescan_or_upstream_reevaluation(count, monkeypatch):
    data = json.loads(WIRE)
    data["events"] = data["events"][:1] + [dict(event_id=f"reset-{i}", event_at_us=5000, type="SIM_RESET", payload={}) for i in range(count - 1)]
    reference = upstream(raw_wire=canonical(data))
    with monkeypatch.context() as patch:
        patch.setattr(preflight_api, "validate_wire", forbidden)
        patch.setattr(preflight_api, "mix_m0", forbidden)
        patch.setattr(e2, "assess_reference_host_boundary", forbidden)
        denied(call(reference))
    # The sole upstream input to E3 is the fixed eight-field E2 result, which
    # carries no events/scenario reference. No event-scaled work can be requested.
    assert not hasattr(reference, "events") and not hasattr(reference, "scenario")


def test_N17_no_ledger_adapter_or_authority(reference, monkeypatch):
    from bb_host_snapshot_commit_gate import TestOnlySnapshotLedger
    ledger = TestOnlySnapshotLedger()
    prior = ledger.snapshot
    monkeypatch.setattr(TestOnlySnapshotLedger, "commit_tick", forbidden)
    before = repr(reference)
    result = call(reference)
    assert repr(reference) == before
    assert ledger.snapshot is prior and ledger.journal_records == ()
    for name in ("can_arm", "grant", "approval_token", "install_receipt", "output_allowed", "accepted_control_at_us", "state"):
        assert not hasattr(result, name) and not hasattr(api, name)
    denied(result)


def test_N18_installed_baseline_and_release_hashes():
    from scripts.verify import provenance, installed_dependencies, PACKAGE
    provenance()
    installed_dependencies(Path(sys.prefix))
    assert PACKAGE.name == "host_provisioning_intent"
    # Full build/wheel/smoke and ten regressions are executed by verify.py and
    # recorded there; a passing unit check alone does not claim those ran.
