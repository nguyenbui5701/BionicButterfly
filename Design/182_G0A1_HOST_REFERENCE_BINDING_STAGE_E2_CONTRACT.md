# G0-A1 — Stage E2 Host Reference Binding / Authority-Denial Boundary

- ID **BB-P222-182**, version E2.1 · Baseline `4c7c92524837c8c728d0f206e5ba4655f9513399`.
- **Derived test-only verification contract**; no new owner-approved R1/R1.1 policy, new wire fields, new E_/P_ codes or authorization token.
- **Scope:** PC_SIM_ONLY; no task-local output or positive host execution permission.
- Authoritative precedence: Design/115, 116, 117, 118, 132, 134, 141. TASK-001 is a strict syntax/semantic preflight, not trusted host approval. TASK-009 is an in-memory TEST_ONLY ledger, not a canonical trace/real FSM.

## 1. Separation of concerns

Stage E2 does **not** provision a trusted runtime allowlist or authenticate a host binary. It **compares** a caller-presented host fingerprint (synthetic TEST_ONLY claim) against a fixed, independently declared E2 *reference tuple*, and compares approved canonical SIM policy **raw bytes** against its frozen SHA-256. The reference tuple is embedded in the new package as a read-only constant, not taken from a scenario/GUI. Equality of an arbitrary string identifier to a constant is not a cryptographic signature, hardware identity or build attestation.

Even perfect reference matching MUST yield `REFERENCE_MATCH_NO_AUTHORITY`, `runtime_authorized=False`, `requires_trusted_host_provisioning=True`, `requires_full_fsm=True`. No code in E2 may invert that into `PASS`, `ADMITTED`, `can_arm`, `output_allowed`, producer token, committed state or a physical command. E2 neither creates nor feeds the TASK-006 hypothetical verdict. It must not call TASK-009 to advance a snapshot.

Host fingerprint values **`G0A1_E2_TEST_ENGINE_ONLY`**, **`G0A1_E2_TEST_SCHEDULER_ONLY`** and **`G0A1_R11_E2_TEST_REFERENCE_ONLY`** are deliberately labeled TEST_ONLY. They are **not** approved engine/scheduler/contract allowlist values. The frozen R1.1 design trace's engine/scheduler sample values are also NOT live binary identities. Only a later owner-approved and independently provisioned host allowlist can decide real runtime authority.

## 2. Inputs and closed output API

```python
@dataclass(frozen=True, slots=True)
class ClaimedHostFingerprint:                 # TEST_ONLY synthetic; not authenticated
    context: str
    scope: str
    owner: str
    contract_revision: str
    engine_revision: str
    scheduler_revision: str
    scheduler_step_us: int
    scenario_wire_schema_version: int
    result_contract_version: int
    trace_format_version: int
    mixer_revision: str

assess_reference_host_boundary(
    preflight: AcceptedPreflight | RejectedPreflight,  # exact TASK-001 types, from real validate_wire
    approved_policy_raw_bytes: bytes,                 # caller-provided raw bytes; content only, not authenticity
    claimed_host: ClaimedHostFingerprint,             # synthetic test input, NOT scenario/GUI data
) -> HostReferenceAssessment
```

`preflight` must be the actual TASK-001 result in integration tests; a manually forged exact-type wrapper cannot be authenticated and must **never** lead to positive runtime authorization. Wrong exact Python types, bool-as-int, wrong enums, mutable input wrappers, invalid domain shapes are **TypeError/ValueError** (not new P_/E_ runtime errors). Do not parse a scenario from inside this function and do not read any files or environment at runtime.

The output has **exactly eight** frozen/slotted fields:

```text
HostReferenceAssessment:
    outcome: HostReferenceOutcome        # REFERENCE_MATCH_NO_AUTHORITY | REFERENCE_MISMATCH | UPSTREAM_REJECTED
    candidate_policy_sha256: str | None  # SHA256 of exact raw bytes; None for REJECTED preflight
    wire_schema_version: int | None      # 2 if valid accepted input; None for REJECTED
    reasons: tuple[HostReferenceReason, ...] # deterministic ordered diagnostics
    reference_pin_match: bool            # true ONLY for all reference pins matching and accepted preflight
    runtime_authorized: bool            # ALWAYS FALSE
    requires_trusted_host_provisioning: bool # ALWAYS TRUE
    requires_full_fsm: bool             # ALWAYS TRUE
```

`HostReferenceReason` enum exactly these **15 internal** ASCII tokens in this order:

```text
UPSTREAM_REJECTED
POLICY_BYTES_MISMATCH
CONTEXT_MISMATCH
SCOPE_MISMATCH
OWNER_MISMATCH
CONTRACT_REVISION_MISMATCH
ENGINE_REVISION_MISMATCH
SCHEDULER_REVISION_MISMATCH
SCHEDULER_STEP_MISMATCH
WIRE_VERSION_MISMATCH
RESULT_VERSION_MISMATCH
TRACE_VERSION_MISMATCH
MIXER_REVISION_MISMATCH
HOST_IDENTITY_NOT_ATTESTED
TRUST_NOT_PROVISIONED
```

- Every result includes `HOST_IDENTITY_NOT_ATTESTED` then `TRUST_NOT_PROVISIONED` as its **last two** reasons. They are never omitted, including on matching reference pins.
- A rejected TASK-001 result has outcome `UPSTREAM_REJECTED`, `candidate_policy_sha256=None`, `wire_schema_version=None`, `reference_pin_match=False` and reasons exactly `(UPSTREAM_REJECTED, HOST_IDENTITY_NOT_ATTESTED, TRUST_NOT_PROVISIONED)`. No further candidate hashing, conversion or host fingerprint comparison for this branch after input type checks. Zero simulation core ticks, no trace/outputs.
- For an accepted TASK-001 result, compute SHA-256 over the supplied **exact** immutable bytes, no UTF-8 decoding/reformatting/JCS recanonicalizing or terminal newline. Compare it to the digest from Design/116. The proposed policy remains *caller-supplied*; a hash equality establishes only content identity. Mismatch yields `POLICY_BYTES_MISMATCH`.
- Match the 11 **claimed host** fields against this fixed E2 reference tuple (see below). A per-field mismatch appends the corresponding reason in the exact enum order, independent of caller field ordering. Do not use scenario fields to populate the claimed host fields.
- An accepted preflight scenario must have `schema_version=2`, `context=PC_SIM`, `provenance=SIM_ONLY`, `config_id=sim-only-c0-v1`, and `clock.start_us=0, clock.step_us=5000`; otherwise fail closed with TypeError/ValueError as an invalid/forged accepted wrapper. The `wire_schema_version` output is 2 from the already validated scenario, not from the claimant.
- If accepted and neither a policy mismatch nor an 11-field mismatch occurs, outcome is `REFERENCE_MATCH_NO_AUTHORITY`, `reference_pin_match=True`. In all other accepted cases outcome `REFERENCE_MISMATCH`, `reference_pin_match=False`. Every result retains the two trust deficits, so no state is authorized.
- `Owner approval` text/provenance/JSON record and policy/hash are **not** trust provision; there is no consent-to-execution field in the input/output. The source may not expose a generic `AuthorizedHost`, `approval_token`, `trusted_host=True`, `grant()`, etc.

### Fixed E2 comparison tuple (TEST_ONLY, NOT runtime allowlist)

```json
{
  "context": "PC_SIM",
  "scope": "PC_SIM_ONLY",
  "owner": "SIMULATOR",
  "contract_revision": "G0A1_R11_E2_TEST_REFERENCE_ONLY",
  "engine_revision": "G0A1_E2_TEST_ENGINE_ONLY",
  "scheduler_revision": "G0A1_E2_TEST_SCHEDULER_ONLY",
  "scheduler_step_us": 5000,
  "scenario_wire_schema_version": 2,
  "result_contract_version": 2,
  "trace_format_version": 1,
  "mixer_revision": "G0A1_M0_R11"
}
```

These exact string values are internal E2 version-test sentinels, not new normative runtime revisions. In real host launch work the Owner must separately approve actual engine/scheduler revisions and a protected, immutable allowlist. Any difference must be denied until then; no auto-learning or configuration from wire can update the expected tuple.

## 3. Ordering and required checks

1. Strict TASK-001 wire-v2 `validate_wire(raw, frozen_schema)` runs FIRST outside this function. Rejected preflight must never be upgraded by a good digest/claimed host and returns `UPSTREAM_REJECTED`.
2. On accepted preflight, validate immutable exact-type wrappers and frozen basic scenario fields (no reparse). Do **not** add event types, change schema version, or read any untrusted scenario-supplied host/engine/owner/sink/approval field: schema must already reject unknown keys.
3. Verify `sha256(raw policy bytes)` against frozen `{POL}` and compare all 11 host claim fields to fixed TEST_ONLY pins. Require strict integer types for step and version fields: bool/float/Decimal/string numeric -> invalid typed input, never treated equal to int.
4. `REFERENCE_MATCH_NO_AUTHORITY` is not a positive guard: always set the three terminal output booleans `(reference_pin_match, runtime_authorized, requires_trusted_host_provisioning)` to `(True, False, True)` in the match case; `requires_full_fsm=True` always. No callbacks, output sink, external mutation, trace writer, state owner or policy loader.
5. Use constant-time *asymptotic* work relative to event count except hashing the supplied raw policy bytes, and only O(1) inspection of the accepted frozen scenario header fields; no event iteration or sorting. Cryptographic constant-time string comparison is NOT a security property for this diagnostic-only stage.
6. Wrong types and forged `AcceptedPreflight`/`RejectedPreflight` wrappers (outside their actual invariant shape) must not be interpreted as trusted; reject malformed shapes and guarantee no authorization even for a syntactically identical forged object. TASK-001 caller remains responsible for establishing actual preflight provenance. Treat results as DATA, never credentials.

## 4. Fail-closed scope restrictions

- No runtime allowlist file, OS-level protected provisioning, cryptographic signature verification, binary/executable attestation, code signing, CI trust issuance, remote authorization service, environment secrets, config/GUI approval booleans, or physical SDK.
- No `HostTrustVerdict.PASS`, `HealthVerdict.PASS`, `ControlVerdict.ADMITTED`, `can_arm`, committed RF/control timestamp, real FSM transition, M0 virtual output, physical output, trace publication or user-notified launch success. Scenario cannot specify engine/scheduler revisions or any policy allowlist. These are **future owner-gated** facilities.
- No new P_* / E_* error-code vocabulary: reasons are task-internal evidence diagnostics, not public v2 protocol messages.
- `G0-A1 PC_SIM_ONLY`; G0-B/G4 physical RC/servo/flapping wing/flight **NO-GO**. If a task requires a real allowlist, stop with `BLOCKED — DESIGN CLARIFICATION` and separate owner sign-off.
