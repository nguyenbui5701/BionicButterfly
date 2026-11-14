"""Design/185 E3: bounded content consistency, permanently unprovisioned.

Caller-supplied synthetic artifact bytes and matching digests cannot authenticate
an executable. Exact E2 type/shape checks are not provenance authentication.
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

from bb_host_trust_boundary import HostReferenceAssessment, HostReferenceOutcome, HostReferenceReason


class ProvisioningIntentOutcome(str, Enum):
    INTENT_CONSISTENT_UNPROVISIONED = "INTENT_CONSISTENT_UNPROVISIONED"
    INTENT_MISMATCH = "INTENT_MISMATCH"
    MALFORMED_INTENT = "MALFORMED_INTENT"
    UPSTREAM_NOT_ELIGIBLE = "UPSTREAM_NOT_ELIGIBLE"


class ProvisioningIntentReason(str, Enum):
    UPSTREAM_NOT_ELIGIBLE = "UPSTREAM_NOT_ELIGIBLE"
    MALFORMED_INTENT = "MALFORMED_INTENT"
    FORMAT_MISMATCH = "FORMAT_MISMATCH"
    CONTEXT_MISMATCH = "CONTEXT_MISMATCH"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    OWNER_MISMATCH = "OWNER_MISMATCH"
    POLICY_DIGEST_MISMATCH = "POLICY_DIGEST_MISMATCH"
    CONTRACT_REVISION_MISMATCH = "CONTRACT_REVISION_MISMATCH"
    ENGINE_REVISION_MISMATCH = "ENGINE_REVISION_MISMATCH"
    SCHEDULER_REVISION_MISMATCH = "SCHEDULER_REVISION_MISMATCH"
    SCHEDULER_STEP_MISMATCH = "SCHEDULER_STEP_MISMATCH"
    WIRE_VERSION_MISMATCH = "WIRE_VERSION_MISMATCH"
    RESULT_VERSION_MISMATCH = "RESULT_VERSION_MISMATCH"
    TRACE_VERSION_MISMATCH = "TRACE_VERSION_MISMATCH"
    MIXER_REVISION_MISMATCH = "MIXER_REVISION_MISMATCH"
    ENGINE_DIGEST_MISMATCH = "ENGINE_DIGEST_MISMATCH"
    SCHEDULER_DIGEST_MISMATCH = "SCHEDULER_DIGEST_MISMATCH"
    REVIEW_REFERENCE_MISMATCH = "REVIEW_REFERENCE_MISMATCH"
    OWNER_SIGNOFF_MISSING = "OWNER_SIGNOFF_MISSING"
    PROTECTED_INSTALL_NOT_PROVEN = "PROTECTED_INSTALL_NOT_PROVEN"
    HOST_IDENTITY_NOT_ATTESTED = "HOST_IDENTITY_NOT_ATTESTED"


@dataclass(frozen=True, slots=True)
class ProvisioningIntentAssessment:
    outcome: ProvisioningIntentOutcome
    policy_sha256: str | None
    engine_artifact_sha256: str | None
    scheduler_artifact_sha256: str | None
    reasons: tuple[ProvisioningIntentReason, ...]
    content_consistent: bool
    runtime_authorized: bool = field(default=False, init=False)
    requires_owner_provisioning: bool = field(default=True, init=False)
    requires_full_fsm: bool = field(default=True, init=False)


_POLICY_SHA256 = "d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10"
_MAX_ARTIFACT_BYTES = 1_048_576
_MAX_INTENT_BYTES = 4096
_DEFICITS = (ProvisioningIntentReason.OWNER_SIGNOFF_MISSING,
             ProvisioningIntentReason.PROTECTED_INSTALL_NOT_PROVEN,
             ProvisioningIntentReason.HOST_IDENTITY_NOT_ATTESTED)
_E2_DEFICITS = (HostReferenceReason.HOST_IDENTITY_NOT_ATTESTED, HostReferenceReason.TRUST_NOT_PROVISIONED)
_E2_ORDER = tuple(HostReferenceReason)
_DIGEST_FIELDS = ("policy_sha256", "engine_artifact_sha256", "scheduler_artifact_sha256")
# Immutable TEST_ONLY labels, not an allowlist of authenticated executable IDs.
# This order is the Design/185 diagnostic order; None marks recomputed digest.
_REFERENCE = (
    ("format", "BB_E3_PROVISIONING_INTENT_V1"), ("context", "PC_SIM"),
    ("scope", "PC_SIM_ONLY"), ("owner", "SIMULATOR"), ("policy_sha256", None),
    ("contract_revision", "G0A1_R11_E3_TEST_REFERENCE_ONLY"),
    ("engine_revision", "G0A1_E3_TEST_ENGINE_ONLY"),
    ("scheduler_revision", "G0A1_E3_TEST_SCHEDULER_ONLY"),
    ("scheduler_step_us", 5000), ("scenario_wire_schema_version", 2),
    ("result_contract_version", 2), ("trace_format_version", 1),
    ("mixer_revision", "G0A1_M0_R11"), ("engine_artifact_sha256", None),
    ("scheduler_artifact_sha256", None), ("review_reference", "P223_TEST_REVIEW_NOT_OWNER_APPROVAL"),
)
_MISMATCH_REASONS = tuple(ProvisioningIntentReason)[2:18]


def _is_digest(value):
    return (type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def _validate_reference(reference):
    if type(reference) is not HostReferenceAssessment:
        raise TypeError("reference must be exact TASK-010 assessment")
    try:
        if type(reference.outcome) is not HostReferenceOutcome:
            raise TypeError("invalid E2 outcome type")
        if (reference.runtime_authorized is not False
                or reference.requires_trusted_host_provisioning is not True
                or reference.requires_full_fsm is not True):
            raise ValueError("invalid E2 permanent flags")
        if type(reference.reference_pin_match) is not bool:
            raise TypeError("invalid E2 pin-match type")
        reasons = reference.reasons
        if type(reasons) is not tuple:
            raise TypeError("E2 reasons must be an exact frozen tuple")
        if not 2 <= len(reasons) <= len(_E2_ORDER):
            raise ValueError("invalid E2 reason count")
        if any(type(r) is not HostReferenceReason for r in reasons):
            raise TypeError("invalid E2 reason type")
        if reasons[-2:] != _E2_DEFICITS or tuple(sorted(set(reasons), key=_E2_ORDER.index)) != reasons:
            raise ValueError("invalid E2 reason order/deficits")
        if reference.outcome is HostReferenceOutcome.UPSTREAM_REJECTED:
            if (reference.candidate_policy_sha256 is not None or reference.wire_schema_version is not None
                    or reference.reference_pin_match or reasons != (HostReferenceReason.UPSTREAM_REJECTED,) + _E2_DEFICITS):
                raise ValueError("inconsistent rejected E2 result")
            return
        if type(reference.wire_schema_version) is not int or reference.wire_schema_version != 2:
            raise ValueError("invalid E2 wire version")
        if not _is_digest(reference.candidate_policy_sha256):
            raise ValueError("invalid E2 policy digest shape")
        policy_mismatch = reference.candidate_policy_sha256 != _POLICY_SHA256
        if (HostReferenceReason.POLICY_BYTES_MISMATCH in reasons) != policy_mismatch:
            raise ValueError("E2 policy diagnostic contradicts digest")
        if reference.outcome is HostReferenceOutcome.REFERENCE_MATCH_NO_AUTHORITY:
            if reference.reference_pin_match is not True or reasons != _E2_DEFICITS:
                raise ValueError("inconsistent matching E2 result")
        elif (reference.reference_pin_match is not False or len(reasons) < 3
              or HostReferenceReason.UPSTREAM_REJECTED in reasons):
            raise ValueError("inconsistent mismatching E2 result")
    except AttributeError:
        raise ValueError("incomplete E2 assessment") from None


def _reject_number(token):
    raise ValueError("only JSON integer tokens are permitted")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _parse_intent(raw):
    # Oversized manifest is malformed request data (P223-T36), not an artifact
    # argument error. Check without decode/parse/hash and never truncate it.
    if len(raw) > _MAX_INTENT_BYTES:
        return None
    try:
        value = json.loads(raw.decode("ascii"), object_pairs_hook=_unique_object,
                           parse_float=_reject_number, parse_constant=_reject_number)
        if type(value) is not dict or len(value) != 16:
            return None
        for name, expected in _REFERENCE:
            if name not in value:
                return None
            actual = value[name]
            if name in _DIGEST_FIELDS:
                if not _is_digest(actual):
                    return None
            elif type(expected) is int:
                if type(actual) is not int:
                    return None
            elif type(actual) is not str or not actual.isascii():
                return None
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False).encode("ascii")
        return value if canonical == raw else None
    except (ValueError, UnicodeError, RecursionError):
        return None


def inspect_provisioning_intent(
    reference: HostReferenceAssessment, intent_raw: bytes, policy_raw: bytes,
    engine_artifact: bytes, scheduler_artifact: bytes,
) -> ProvisioningIntentAssessment:
    """Inspect a proposal, never authenticate, provision or authorize execution."""
    for value in (intent_raw, policy_raw, engine_artifact, scheduler_artifact):
        if type(value) is not bytes:
            raise TypeError("all four payload arguments must be exact immutable bytes")
    if len(policy_raw) > _MAX_ARTIFACT_BYTES:
        raise ValueError("policy byte quota exceeded")
    for artifact in (engine_artifact, scheduler_artifact):
        if not 1 <= len(artifact) <= _MAX_ARTIFACT_BYTES:
            raise ValueError("synthetic artifact length must be 1..1048576 bytes")
    _validate_reference(reference)
    if reference.outcome is not HostReferenceOutcome.REFERENCE_MATCH_NO_AUTHORITY:
        return ProvisioningIntentAssessment(ProvisioningIntentOutcome.UPSTREAM_NOT_ELIGIBLE, None, None, None,
            (ProvisioningIntentReason.UPSTREAM_NOT_ELIGIBLE,) + _DEFICITS, False)
    intent = _parse_intent(intent_raw)
    if intent is None:
        return ProvisioningIntentAssessment(ProvisioningIntentOutcome.MALFORMED_INTENT, None, None, None,
            (ProvisioningIntentReason.MALFORMED_INTENT,) + _DEFICITS, False)
    digests = tuple(hashlib.sha256(raw).hexdigest() for raw in (policy_raw, engine_artifact, scheduler_artifact))
    reasons = []
    for (name, expected), reason in zip(_REFERENCE, _MISMATCH_REASONS):
        if name in _DIGEST_FIELDS:
            expected = digests[_DIGEST_FIELDS.index(name)]
        if intent[name] != expected or (name == "policy_sha256" and expected != _POLICY_SHA256):
            reasons.append(reason)
    consistent = not reasons
    outcome = (ProvisioningIntentOutcome.INTENT_CONSISTENT_UNPROVISIONED if consistent
               else ProvisioningIntentOutcome.INTENT_MISMATCH)
    return ProvisioningIntentAssessment(outcome, *digests, tuple(reasons) + _DEFICITS, consistent)
