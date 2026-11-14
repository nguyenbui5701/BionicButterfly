# G0-A1 Stage E3 — Offline Host Provisioning Intent Inspection

- ID **BB-P223-185** · Status: SA-derived DESIGN CONTRACT, **not a new owner-approved runtime policy or executable trust issuance**.
- Baseline: `7872c415c73146e33a5596b010320f76596588cb`. Controlling R1/R1.1: Design/115–118, 132, 134, 141; E2: Design/182, TASK-010. TASK-009 internal journal is unrelated to authority.
- Stage name: **HOST_PROVISIONING_INTENT_V1** / PC_SIM_ONLY **TEST_ONLY**. Unlike E2's standalone header comparison, E3 binds a proposed offline provisioning manifest to independently supplied **raw artifact bytes** and the frozen R1 policy. It is an inspect-only intake; **no trusted provisioning occurs**.

## 1. Non-negotiable trust separation

A match of `sha256(engine_artifact_bytes)` to `engine_artifact_sha256` **declared in the same untrusted request** merely proves internal consistency, not the identity of the built executable. Likewise for scheduler. A digest or owner-chat approval JSON is not a signature; a TEST_ONLY reference or P210 design engine revision is not approved runtime identity; the Python model is not an OS protection boundary. **Even all E2+E3 checks pass, the only favorable result is `INTENT_CONSISTENT_UNPROVISIONED`.** No API may return trusted host, `runtime_authorized=True`, PASS/ADMITTED, ARM, output, install receipt, launch token, secure-attestation proof, or real signing key.

### Actual future release gates (explicitly NOT IMPLEMENTED by TASK-011)

1. Owner must approve a **real** engine/scheduler build revision and selected contract revision; a source SHA alone is not an executable build attestation.
2. Identify and approve a signer/trust root and protected host installer/build channel; choose cryptographic signature algorithm, key lifecycle, revocation and rotation through a separate SA/Owner security decision. No private keys in repository, scenario, tests, ZIP, logs, or user chat.
3. Independently provision verified, access-controlled allowlist/trust anchor outside scenario/GUI/working-tree and bind policy + executable digest + scheduler + scope + review to that anchor. A locally editable JSON or repo document is insufficient.
4. Before a real PC-only runner exists, independently verify process/executable identity, provenance and trust root; validate scenario and policy; fail closed on mismatch. Later complete FSM and canonical R1 JCS+LF append-before-publish must be implemented and tested separately. **Hardware and flight require their own design and approvals.**

These are owner-gated future tasks; do not invent signed installer or imply Windows ACLs/TPM/certificates actually provisioned in E3.

## 2. Closed input/output API (pure; no files)

```python
inspect_provisioning_intent(
    reference: HostReferenceAssessment, # exact TASK-010 result from real TASK-001->E2 in integration tests
    intent_raw: bytes,                  # untrusted proposed JSON; max 4096 bytes
    policy_raw: bytes,                  # raw frozen R1 bytes in positive tests; max 1 MiB
    engine_artifact: bytes,             # SYNTHETIC TEST_ONLY artifact bytes, 1..1 MiB
    scheduler_artifact: bytes,          # SYNTHETIC TEST_ONLY artifact bytes, 1..1 MiB
) -> ProvisioningIntentAssessment
```

`reference` has no real authorization claim. Verify its **exact** TASK-010 type, frozen fields, enum/outcome consistency and `(runtime_authorized=False, requires_trusted_host_provisioning=True, requires_full_fsm=True)`; malformed/forged shapes are TypeError/ValueError; even identical fake wrapper cannot grant authority. If `reference.outcome` is `REFERENCE_MISMATCH` or `UPSTREAM_REJECTED`, return `UPSTREAM_NOT_ELIGIBLE` **before parsing `intent_raw` or hashing any bytes**. Real E2 reference must still be independently produced from real TASK-001 and canonical R1 bytes in integration tests; do not construct a positive fake object as a test oracle.

`ProvisioningIntentAssessment` is frozen/slotted **exactly nine fields**:

```text
  outcome: ProvisioningIntentOutcome   # INTENT_CONSISTENT_UNPROVISIONED | INTENT_MISMATCH | MALFORMED_INTENT | UPSTREAM_NOT_ELIGIBLE
  policy_sha256: str | None
  engine_artifact_sha256: str | None
  scheduler_artifact_sha256: str | None
  reasons: tuple[ProvisioningIntentReason, ...]
  content_consistent: bool
  runtime_authorized: bool            # ALWAYS False, field(init=False)
  requires_owner_provisioning: bool   # ALWAYS True, field(init=False)
  requires_full_fsm: bool            # ALWAYS True, field(init=False)
```

`reasons` is a frozen tuple with a CLOSED enum and this **exact order**:

```text
UPSTREAM_NOT_ELIGIBLE
MALFORMED_INTENT
FORMAT_MISMATCH
CONTEXT_MISMATCH
SCOPE_MISMATCH
OWNER_MISMATCH
POLICY_DIGEST_MISMATCH
CONTRACT_REVISION_MISMATCH
ENGINE_REVISION_MISMATCH
SCHEDULER_REVISION_MISMATCH
SCHEDULER_STEP_MISMATCH
WIRE_VERSION_MISMATCH
RESULT_VERSION_MISMATCH
TRACE_VERSION_MISMATCH
MIXER_REVISION_MISMATCH
ENGINE_DIGEST_MISMATCH
SCHEDULER_DIGEST_MISMATCH
REVIEW_REFERENCE_MISMATCH
OWNER_SIGNOFF_MISSING
PROTECTED_INSTALL_NOT_PROVEN
HOST_IDENTITY_NOT_ATTESTED
```

Every assessment **must end** in `(OWNER_SIGNOFF_MISSING, PROTECTED_INSTALL_NOT_PROVEN, HOST_IDENTITY_NOT_ATTESTED)` including malformed/upstream cases. These labels are **internal**, not new public R1 E_/P_ errors.

## 3. Closed E3 JSON manifest: test-only proposal, not a credential

`Design/fixtures/P223_HOST_PROVISIONING_INTENT_ORACLE_INDEX.json` supplies exactly the following **16-field** base fixture (machine file is authoritative for these TEST_ONLY example values):

```json
{
  "context": "PC_SIM",
  "contract_revision": "G0A1_R11_E3_TEST_REFERENCE_ONLY",
  "engine_artifact_sha256": "566fdd854b288227721050c168bdc4278cba64d43717b3c899d6021a0a421546",
  "engine_revision": "G0A1_E3_TEST_ENGINE_ONLY",
  "format": "BB_E3_PROVISIONING_INTENT_V1",
  "mixer_revision": "G0A1_M0_R11",
  "owner": "SIMULATOR",
  "policy_sha256": "d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10",
  "result_contract_version": 2,
  "review_reference": "P223_TEST_REVIEW_NOT_OWNER_APPROVAL",
  "scenario_wire_schema_version": 2,
  "scheduler_artifact_sha256": "3b2d0e531ac73c6664b970fb1658bc9704f476fc22a95c1d14c7afbf97f8f9b7",
  "scheduler_revision": "G0A1_E3_TEST_SCHEDULER_ONLY",
  "scheduler_step_us": 5000,
  "scope": "PC_SIM_ONLY",
  "trace_format_version": 1
}
```

- All strings and numeric fields of the TEST_ONLY E3 manifest are strictly ASCII; only integers (not bool) allowed in scheduler_step_us and three version fields, and 64-character lowercase hex strings for SHA-256. No nested objects, arrays, float/exponent/NaN/Infinity, duplicate keys or unknown keys. Exactly sixteen fields.
- Candidate `intent_raw` is strictly UTF-8 **ASCII subset**, single closed JSON object, encoded `json.dumps(mapping, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')` for this **restricted test-only ASCII domain**. It has **no BOM, no whitespace and no final LF**. This is not a general RFC8785 JCS implementation, and future production signing requires a reviewed standard serializer/validator.
- Strict decoder: byte quota before decode; reject duplicate keys with `object_pairs_hook`, reject invalid constants with `parse_constant`, reject arrays, unknown/missing keys, nested/Unicode/decimal/bool substitutions, noncanonical raw bytes or incorrectly shaped fields. Malformed raw candidate returns `MALFORMED_INTENT`, all three hashes None; do not hash raw artifact/policy in this case. Wrong Python argument types raise TypeError/ValueError instead.
- `engine_artifact` and `scheduler_artifact` are required bytes with length 1..1048576; `policy_raw` is bytes <=1048576 and may be empty (a mismatch, not successful). Input lengths checked before hashing. Oversized, empty synthetic artifacts or invalid input arg types raise TypeError/ValueError rather than allocating large buffers or hashing.
- After valid canonical intent, compute **three** SHA256 values from the independently supplied exact policy/engine/scheduler bytes. Compare both the **declared** SHA fields to recomputed digests and the policy digest to **approved frozen R1** SHA `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. A policy request declaring an alternate digest that matches altered policy bytes remains `POLICY_DIGEST_MISMATCH` because the frozen approval is unchanged.
- Match every non-hash manifest field to the fixed **E3 TEST_ONLY** reference tuple; field mismatches collected in the exact order declared above. The string `P223_TEST_REVIEW_NOT_OWNER_APPROVAL` is a placeholder, NEVER a review authorization. Fake `OWNER_APPROVED`, `approved`, `trusted_host`, `signature` do not confer trust.
- For canonical, typed manifest and valid raw-argument lengths: all claimed bytes, frozen policy, and E3 reference fields consistent -> `INTENT_CONSISTENT_UNPROVISIONED`, `content_consistent=True`, three actual digest outputs; otherwise `INTENT_MISMATCH`, false, mismatch reasons; permanent three deficits last. Invalid/malformed request -> `MALFORMED_INTENT`, false, digest outputs null; upstream ineligible -> `UPSTREAM_NOT_ELIGIBLE`, false and digests null.

### Policy hash comparison nuance

`POLICY_DIGEST_MISMATCH` iff **either** `intent.policy_sha256 != sha256(policy_raw)` **or** `sha256(policy_raw) != d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. The same reason is emitted once only. For engine/scheduler, compare declared digest with actual bytes; **no approved executable identity digest exists** at E3. Thus match only attests self-consistency, not trust.

## 4. Strict execution order and side-effect restrictions

1. Validate exact input Python types (`HostReferenceAssessment`, bytes for four payloads), lengths and E2 fixed flags. Reject forged mutated E2 output shapes; no trust even when exact-type forgery has consistent fields.
2. If E2 outcome is not `REFERENCE_MATCH_NO_AUTHORITY`, short-circuit to `UPSTREAM_NOT_ELIGIBLE` with no E3 JSON parse/hash. Require E2 output has expected last-two reasons and reference_pin_match only when match; no running TASK-010/E2 again inside E3.
3. Parse/canonical-check the **manifest only** and its 16 exact fields; on malformed return `MALFORMED_INTENT` (no hash).
4. Hash bounded policy/artifact inputs, compare fixed E3 tuple and R1 policy; return immutable inspection. Never publish, never mutate, never install a certificate/allowlist, never call TASK-009 or virtual-clock runner.

Pure runtime uses Python 3.11+ stdlib `json`, `hashlib`, `dataclasses`, `enum` and exact TASK-010 types only. No file/OS/env/network/subprocess/clock/RNG/cryptographic signing, no protected persistence, no hardware drivers/RC/UART/servo/GPIO/PWM, and no callback/transport/UI output. No mutable globals, profile updates, event rescan or scenario-derived key/claim. O(size of three bounded byte arrays + <=4096 byte intent), not per-event work. It does **not** read a running executable or calculate its identity; input byte strings are caller-supplied synthetic data.

**STOP and request separate Owner-approved security design before any real provision, signature verification, authority or output.**
