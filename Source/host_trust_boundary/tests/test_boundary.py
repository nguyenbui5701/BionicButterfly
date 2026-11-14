"""N01-N18 adversarial families. N18's full builds/regressions run in verify.py."""

import ast
import builtins
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal, localcontext
from enum import Enum
import hashlib
import importlib.metadata
import inspect
import json
import locale
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from types import MappingProxyType, SimpleNamespace

import pytest
import bb_host_preflight_m0
from bb_host_preflight_m0 import AcceptedPreflight, RejectedPreflight, validate_wire
import bb_host_trust_boundary as api
from bb_host_trust_boundary import (ClaimedHostFingerprint, HostReferenceOutcome as Outcome,
                                   HostReferenceReason as Reason, assess_reference_host_boundary as assess)
from bb_host_trust_boundary import boundary
from scripts.scenarios import INDEX, SCHEMA, WIRE, POLICY, ROOT, claim, policy_variant, wire_variant, exercise


@pytest.fixture
def accepted():
    result = validate_wire(WIRE, SCHEMA)
    assert type(result) is AcceptedPreflight
    return result


@pytest.fixture
def rejected():
    result = validate_wire(wire_variant("UNKNOWN_APPROVED"), SCHEMA)
    assert type(result) is RejectedPreflight
    return result


def denied(result):
    assert result.runtime_authorized is False
    assert result.requires_trusted_host_provisioning is True and result.requires_full_fsm is True
    assert result.reasons[-2:] == (Reason.HOST_IDENTITY_NOT_ATTESTED, Reason.TRUST_NOT_PROVISIONED)


class StringSubclass(str):
    def __eq__(self, other):
        raise AssertionError("must not invoke claimant equality")


class IntSubclass(int):
    pass


class BytesSubclass(bytes):
    pass


class TupleSubclass(tuple):
    def __iter__(self):
        raise AssertionError("must not scan events")


class WrongEnum(str, Enum):
    VALUE = "PC_SIM"


@pytest.mark.parametrize("wrong", [None, {}, [], True, SimpleNamespace(status="ACCEPTED_PREFLIGHT"),
                                   lambda: True, object()])
def test_N01_wrong_preflight_type(wrong):
    with pytest.raises(TypeError):
        assess(wrong, POLICY, claim())


@pytest.mark.parametrize("kind", [AcceptedPreflight, RejectedPreflight])
def test_N01_subclasses_and_uninitialized(kind, accepted, rejected):
    class Spoof(kind):
        pass
    source = accepted if kind is AcceptedPreflight else rejected
    with pytest.raises(TypeError):
        assess(Spoof(**vars(source)), POLICY, claim())
    with pytest.raises((TypeError, ValueError)):
        assess(object.__new__(kind), POLICY, claim())
    # A byte-identical fabricated wrapper is data, never a credential.
    denied(assess(kind(**vars(source)), POLICY, claim()))


@pytest.mark.parametrize("field,value", [
    ("schema_version", True), ("schema_version", 1), ("schema_version", 2.0),
    ("context", "RC_PRIMARY"), ("context", StringSubclass("PC_SIM")),
    ("provenance", "RF_PRIMARY"), ("config_id", "custom"), ("approved", True),
    ("scenario_id", ""), ("scenario_id", 4), ("scenario_id", "\x00bad"),
    ("scenario_id", "é" * 129), ("scenario_id", "x" * 257), ("scenario_id", "\ud800"),
    ("duration_us", True), ("duration_us", Decimal(5000)), ("duration_us", 0),
    ("duration_us", 5001), ("duration_us", 60_005_000),
    ("events", []), ("events", ()), ("events", (None,) * 20_001), ("events", TupleSubclass((None,))),
    ("clock", {"start_us": 0, "step_us": 5000}),
    ("clock", MappingProxyType({"start_us": False, "step_us": 5000})),
    ("clock", MappingProxyType({"start_us": 0, "step_us": 5000.0})),
    ("clock", MappingProxyType({"start_us": 1, "step_us": 5000})),
    ("clock", MappingProxyType({"start_us": 0, "step_us": 10000})),
    ("clock", MappingProxyType({"start_us": 0, "step_us": 5000, "approved": True})),
])
def test_N01_forged_accepted_header(accepted, field, value):
    wrapper = AcceptedPreflight(MappingProxyType(dict(accepted.scenario) | {field: value}))
    with pytest.raises((TypeError, ValueError)):
        assess(wrapper, POLICY, claim())


@pytest.mark.parametrize("field", ["schema_version", "context", "provenance", "config_id", "clock", "duration_us", "events", "scenario_id"])
def test_N01_missing_header(accepted, field):
    data = dict(accepted.scenario)
    del data[field]
    with pytest.raises(ValueError):
        assess(AcceptedPreflight(MappingProxyType(data)), POLICY, claim())


@pytest.mark.parametrize("status", [None, True, "VALIDATION_REJECTED", StringSubclass("ACCEPTED_PREFLIGHT")])
def test_N01_accepted_status(accepted, status):
    with pytest.raises((TypeError, ValueError)):
        assess(replace(accepted, status=status), POLICY, claim())


def test_N01_mutable_or_extra_wrapper(accepted, rejected):
    with pytest.raises(TypeError):
        assess(AcceptedPreflight(dict(accepted.scenario)), POLICY, claim())
    for wrapper in (accepted, rejected):
        object.__setattr__(wrapper, "approved", True)
        with pytest.raises(ValueError):
            assess(wrapper, POLICY, claim())


@pytest.mark.parametrize("field,value", [
    ("diagnostic_format_version", True), ("scope", "RC"), ("run_status", "COMPLETED"),
    ("evaluated_tick_count", 1), ("evaluated_tick_count", False), ("evidence_complete", True),
    ("evidence_complete", 0), ("raw_input_sha256", "0" * 63), ("raw_input_sha256", "G" * 64),
    ("raw_input_sha256", b"0" * 64), ("primary_issue", {}), ("approved", True),
])
def test_N01_forged_rejection(rejected, field, value):
    with pytest.raises((TypeError, ValueError)):
        assess(RejectedPreflight(rejected.diagnostic | {field: value}), POLICY, claim())


@pytest.mark.parametrize("field,value", [("code", "PASS"), ("code", 0), ("stage", "RAW"),
    ("json_pointer", "bad"), ("json_pointer", []), ("frozen_base_error_code", "E_CONTEXT_DENIED"), ("approved", True)])
def test_N01_forged_rejection_issue(rejected, field, value):
    data = deepcopy(rejected.diagnostic)
    data["primary_issue"][field] = value
    with pytest.raises((TypeError, ValueError)):
        assess(RejectedPreflight(data), POLICY, claim())


@pytest.mark.parametrize("field", INDEX["host_fields"])
@pytest.mark.parametrize("wrong", [None, True, 2.0, float("nan"), Decimal("2"), Decimal("NaN"),
                                   [], {}, StringSubclass("PC_SIM"), WrongEnum.VALUE, IntSubclass(2)])
def test_N02_strict_host_fields(accepted, rejected, field, wrong):
    for wrapper in (accepted, rejected):
        with pytest.raises(TypeError):
            assess(wrapper, POLICY, replace(claim(), **{field: wrong}))


@pytest.mark.parametrize("wrong", [None, {}, SimpleNamespace(**INDEX["reference_host_claim"]), lambda: claim()])
def test_N02_host_wrapper(accepted, wrong):
    with pytest.raises(TypeError):
        assess(accepted, POLICY, wrong)


def test_N02_subclass_uninitialized_and_kwargs(accepted):
    class Spoof(ClaimedHostFingerprint):
        pass
    with pytest.raises(TypeError):
        assess(accepted, POLICY, Spoof(**INDEX["reference_host_claim"]))
    with pytest.raises(ValueError):
        assess(accepted, POLICY, object.__new__(ClaimedHostFingerprint))
    with pytest.raises(TypeError):
        claim(approved=True)
    with pytest.raises(TypeError):
        assess(accepted, POLICY, claim(), approved=True)


@pytest.mark.parametrize("wrong", [bytearray(POLICY), memoryview(POLICY), POLICY.decode(), BytesSubclass(POLICY),
                                   None, {"sha256": hashlib.sha256(POLICY).hexdigest()}, lambda: POLICY])
def test_N03_exact_policy_bytes(accepted, rejected, wrong):
    for wrapper in (accepted, rejected):
        with pytest.raises(TypeError):
            assess(wrapper, wrong, claim())


@pytest.mark.parametrize("variant", [v for v in INDEX["policy_variant_mutations"] if v != "EXACT"])
def test_N04_policy_raw_mutation(accepted, variant):
    raw = policy_variant(variant)
    result = assess(accepted, raw, claim())
    assert result.outcome is Outcome.REFERENCE_MISMATCH
    assert result.candidate_policy_sha256 == hashlib.sha256(raw).hexdigest()
    assert result.reasons == (Reason.POLICY_BYTES_MISMATCH, Reason.HOST_IDENTITY_NOT_ATTESTED, Reason.TRUST_NOT_PROVISIONED)
    denied(result)


def test_N05_frozen_vector_content_only(accepted):
    assert hashlib.sha256(POLICY).hexdigest() == "d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10"
    assert not POLICY.endswith(b"\n")
    for policy in (POLICY, hashlib.sha256(POLICY).hexdigest().encode("ascii")):
        denied(assess(accepted, policy, claim()))
    assert assess(accepted, hashlib.sha256(POLICY).hexdigest().encode(), claim()).reference_pin_match is False


def test_N06_rejected_never_hashes_or_compares(rejected, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("rejected branch hashed/compared candidate")
    monkeypatch.setattr(boundary, "sha256", forbidden)
    monkeypatch.setattr(boundary, "_REFERENCE", object())
    for policy in (POLICY, b"", b"\xff", POLICY + b"\n"):
        result = assess(rejected, policy, claim(engine_revision="BAD", scheduler_step_us=-1))
        denied(result)
        assert result.outcome is Outcome.UPSTREAM_REJECTED
        assert result.candidate_policy_sha256 is None and result.wire_schema_version is None
        assert result.reference_pin_match is False
        assert result.reasons[0] is Reason.UPSTREAM_REJECTED
    assert rejected.diagnostic["evaluated_tick_count"] == 0


@pytest.mark.parametrize("key,value", [("approved", True), ("owner", "SIMULATOR"), ("engine_revision", "G0A1_E2_TEST_ENGINE_ONLY"),
    ("scheduler_revision", "G0A1_E2_TEST_SCHEDULER_ONLY"), ("trusted_host", True), ("output_adapter", "PWM"),
    ("policy_allowlist", [hashlib.sha256(POLICY).hexdigest()]), ("approval_token", "signed"), ("scope", "PC_SIM_ONLY")])
def test_N07_wire_injections(key, value):
    data = json.loads(WIRE) | {key: value}
    wrapper = validate_wire(json.dumps(data).encode(), SCHEMA)
    assert type(wrapper) is RejectedPreflight
    assert wrapper.diagnostic["primary_issue"]["code"] == "P_SCHEMA_UNKNOWN_FIELD"
    assert assess(wrapper, POLICY, claim()).outcome is Outcome.UPSTREAM_REJECTED


def test_N08_match_is_permanent_denial(accepted):
    result = assess(accepted, POLICY, claim())
    assert result.outcome is Outcome.REFERENCE_MATCH_NO_AUTHORITY and result.reference_pin_match is True
    assert len(result.reasons) == 2
    denied(result)


@pytest.mark.parametrize("case", INDEX["cases"][12:28] + INDEX["cases"][47:], ids=lambda c: c["id"])
def test_N09_independent_and_combined_order(case):
    result = exercise(case)
    ordered = list(Reason)
    assert list(result.reasons) == sorted(set(result.reasons), key=ordered.index)


def test_N10_closed_immutable_api(accepted):
    result = assess(accepted, POLICY, claim())
    assert len(fields(result)) == 8 and len(fields(ClaimedHostFingerprint)) == 11
    assert api.__all__ == ["ClaimedHostFingerprint", "HostReferenceAssessment", "HostReferenceOutcome", "HostReferenceReason", "assess_reference_host_boundary"]
    assert list(inspect.signature(assess).parameters) == ["preflight", "approved_policy_raw_bytes", "claimed_host"]
    for name in ("runtime_authorized", "requires_full_fsm", "requires_trusted_host_provisioning"):
        with pytest.raises(ValueError):
            replace(result, **{name: not getattr(result, name)})
    for obj in (result, claim(), boundary._REFERENCE):
        assert not hasattr(obj, "__dict__")
        for f in fields(obj):
            with pytest.raises(FrozenInstanceError):
                setattr(obj, f.name, None)


@pytest.mark.parametrize("count", [1, 20_000])
def test_N11_event_count_independent_no_rescan(count):
    data = json.loads(WIRE)
    data["events"] = data["events"][:1] + [dict(event_id=f"reset-{i}", event_at_us=5000, type="SIM_RESET", payload={}) for i in range(count - 1)]
    wrapper = validate_wire(json.dumps(data, separators=(",", ":")).encode(), SCHEMA)
    assert type(wrapper) is AcceptedPreflight and len(wrapper.scenario["events"]) == count
    observed_lines = []
    def trace(frame, event, arg):
        if event == "line" and frame.f_globals.get("__name__") == boundary.__name__:
            observed_lines.append((frame.f_code.co_name, frame.f_lineno))
        return trace
    previous = sys.gettrace()
    try:
        sys.settrace(trace)
        result = assess(wrapper, POLICY, claim())
    finally:
        sys.settrace(previous)
    assert result.reference_pin_match is True
    # Fixed header path executes the same lines at max_events and one event.
    minimal = validate_wire(WIRE, SCHEMA)
    first = tuple(observed_lines)
    observed_lines.clear()
    try:
        sys.settrace(trace)
        assess(minimal, POLICY, claim())
    finally:
        sys.settrace(previous)
    assert tuple(observed_lines) == first


def test_N11_no_event_dereference(accepted):
    class Poison:
        def __getattribute__(self, name):
            raise AssertionError("event dereferenced")
    # Forged fixture used ONLY to instrument O(1), not as an accepted oracle.
    fake = AcceptedPreflight(MappingProxyType(dict(accepted.scenario) | {"events": (Poison(),) * 20_000}))
    denied(assess(fake, POLICY, claim()))


def test_N12_runtime_import_and_call_inventory():
    allowed_imports = {"dataclasses", "enum", "hashlib", "types", "bb_host_preflight_m0", "bb_host_preflight_m0.diagnostics", "boundary"}
    forbidden_names = {"open", "eval", "exec", "compile", "__import__", "validate_wire", "mix_m0", "commit_tick", "getenv", "getattr_static"}
    for path in Path(boundary.__file__).parent.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in allowed_imports for alias in node.names)
            if isinstance(node, ast.ImportFrom):
                assert node.module in allowed_imports
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
                assert name not in forbidden_names


def test_N12_runtime_io_spies(accepted, rejected, monkeypatch):
    host = claim()
    def forbidden(*args, **kwargs):
        raise AssertionError("runtime attempted IO/execution")
    with monkeypatch.context() as patch:
        for obj, name in [(builtins, "open"), (Path, "open"), (os, "getenv"), (socket, "socket"),
                          (subprocess, "Popen"), (time, "time"), (time, "monotonic"),
                          (bb_host_preflight_m0, "validate_wire"), (bb_host_preflight_m0, "mix_m0")]:
            patch.setattr(obj, name, forbidden)
        for wrapper in (accepted, rejected):
            denied(assess(wrapper, POLICY, host))


def test_N13_design_trace_and_chat_are_not_credentials(accepted):
    header = json.loads((ROOT / "Design/fixtures/P210_MINIMAL_DESIGN_TRACE.jsonl").read_bytes().splitlines()[0])
    result = assess(accepted, POLICY, claim(engine_revision=header["engine_revision"], scheduler_revision=header["scheduler_revision"]))
    assert result.reasons[:2] == (Reason.ENGINE_REVISION_MISMATCH, Reason.SCHEDULER_REVISION_MISMATCH)
    raw = (ROOT / "Design/contracts/G0A1_OWNER_APPROVAL_R1.record.json").read_bytes()
    assert json.loads(raw)["trusted_runtime_policy_allowlist_provisioned"] is False
    assert assess(accepted, raw, claim()).reference_pin_match is False
    with pytest.raises(TypeError):
        assess(accepted, POLICY, json.loads(raw))
    denied(result)


@pytest.mark.parametrize("field", [f for f, v in INDEX["reference_host_claim"].items() if type(v) is str])
@pytest.mark.parametrize("spoof", ["pc_sim", "PC_SIM ", " PC_SIM", "PC_SІM", "ＳＩＭＵＬＡＴＯＲ", "chủ sở hữu", "\x00", "\n", "\ud800", "", "signed:OWNER_APPROVED"])
def test_N14_string_spoofing(accepted, field, spoof):
    result = assess(accepted, POLICY, replace(claim(), **{field: spoof}))
    assert result.outcome is Outcome.REFERENCE_MISMATCH
    denied(result)


def test_N15_external_input_cannot_rotate_reference(accepted, monkeypatch):
    baseline = assess(accepted, POLICY, claim())
    for name in ("APPROVED", "TRUSTED_HOST", "POLICY_ALLOWLIST", "ENGINE_REVISION"):
        monkeypatch.setenv(name, "true")
    assert assess(accepted, POLICY, claim()) == baseline
    for key in ("allowlist", "owner_approval", "trusted_host", "approval_token", "callback"):
        with pytest.raises(TypeError):
            assess(accepted, POLICY, claim(), **{key: True})
    assert assess(accepted, POLICY, claim(engine_revision="new signed engine")).reference_pin_match is False
    assert assess(accepted, POLICY, claim()) == baseline


@pytest.mark.parametrize("loc", ["C", "English_United States.1252"])
@pytest.mark.parametrize("tz", ["UTC0", "ICT-7"])
@pytest.mark.parametrize("precision", [2, 50])
def test_N16_determinism_and_immutability(accepted, rejected, loc, tz, precision, monkeypatch):
    previous_locale = locale.setlocale(locale.LC_ALL)
    previous_tz = os.environ.get("TZ")
    expected = [assess(p, POLICY, claim()) for p in (accepted, rejected)]
    before = repr((accepted, rejected, POLICY, claim()))
    try:
        locale.setlocale(locale.LC_ALL, loc)
        monkeypatch.setenv("TZ", tz)
        if hasattr(time, "tzset"):
            time.tzset()
        with localcontext() as ctx:
            ctx.prec = precision
            for _ in range(3):
                assert [assess(p, POLICY, claim()) for p in (accepted, rejected)] == expected
        assert repr((accepted, rejected, POLICY, claim())) == before
    finally:
        locale.setlocale(locale.LC_ALL, previous_locale)
        if previous_tz is None:
            monkeypatch.delenv("TZ", raising=False)
        else:
            monkeypatch.setenv("TZ", previous_tz)
        if hasattr(time, "tzset"):
            time.tzset()


def test_N17_no_downstream_authority_or_ledger(accepted, rejected, monkeypatch):
    from bb_host_snapshot_commit_gate import TestOnlySnapshotLedger
    ledger = TestOnlySnapshotLedger()
    prior = ledger.snapshot
    def forbidden(*args, **kwargs):
        raise AssertionError("E2 advanced E1")
    monkeypatch.setattr(TestOnlySnapshotLedger, "commit_tick", forbidden)
    for wrapper in (accepted, rejected):
        result = assess(wrapper, POLICY, claim())
        denied(result)
        for name in ("can_arm", "output_allowed", "state", "snapshot", "accepted_control_at_us", "approval_token", "grant"):
            assert not hasattr(result, name) and not hasattr(api, name)
    assert ledger.snapshot is prior and ledger.journal_records == ()
    assert set(Outcome.__members__) == {"REFERENCE_MATCH_NO_AUTHORITY", "REFERENCE_MISMATCH", "UPSTREAM_REJECTED"}


def test_N18_installed_local_prerequisite_and_release_provenance():
    from scripts.verify import provenance, installed_dependencies, PACKAGE
    provenance()
    installed_dependencies(Path(sys.prefix))
    assert importlib.metadata.version("bb-host-preflight-m0") == "0.1.0"
    # Full build, wheel smoke and nine read-only regressions are executed and
    # recorded by verify.py, not inferred from this unit test.
    assert PACKAGE.name == "host_trust_boundary"
