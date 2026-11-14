# TASK-010 — HOST_REFERENCE_TRUST_BOUNDARY (Stage E2)

| Item | Value |
|---|---|
| Status | **OPEN — SA RELEASED FOR OWNER ASSIGNMENT** |
| Parent | `main` `4c7c92524837c8c728d0f206e5ba4655f9513399` after PR #9 merge |
| Scope | G0-A1 **PC_SIM_ONLY / TEST_ONLY REFERENCE COMPARISON** |
| Allowed Developer write scope | `Source/host_trust_boundary/**` **ONLY** |
| Branch suggestion | `feature/TASK-010-host-trust-boundary` |
| PR/merge | Developer may create PR only after Owner UAT PASS and explicit authorization; Owner alone merges |

## Objective

Implement a **negative-only host reference checker**. Consume a real TASK-001 accepted/rejected preflight result, exact raw canonical policy byte vector, and a separately supplied **test-synthetic** `ClaimedHostFingerprint`. Compare all 11 host candidate fields against a fixed TEST_ONLY tuple; compare `sha256(exact_policy_raw_bytes)` with approved digest `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. Even a perfect match returns **NO AUTHORITY**. Never create a trusted runtime allowlist or deployable host identity, never assert that engine/scheduler binary has been independently attested.

## Mandatory reading and immutable references

1. Workflow rules: `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`.
2. Normative R1/1.1: exact files `Design/115`, **`116`**, `117`, `118`, `132`, `134`, `141` and machine schemas; **read complete documents**, do not infer filename suffixes.
3. Read-only TASK-001 preflight source `Source/host_preflight_m0` and previous TASK-009 snapshot shell (no run/commit call in new module).
4. New release: **`Design/181_TASK009_MERGE_CLOSEOUT_AND_TASK010_BASELINE.md`**, **`Design/182_G0A1_HOST_REFERENCE_BINDING_STAGE_E2_CONTRACT.md`**, `Design/183_TASK010_REFERENCE_BINDING_ORACLES_AND_SA_REVIEW.md`, `Design/fixtures/P222_HOST_REFERENCE_ORACLE_INDEX.json`, `Design/P222_TASK010_RELEASE_MANIFEST.json`.
5. Verify exact base and every Git blob pin in Design/181 before coding; a mismatch is `BLOCKED — DESIGN CLARIFICATION` and no rebaseline. Policy SHA-256 `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10` must be verified from exact frozen bytes **without newline**.

## Source implementation

- Create pip-installable Python >=3.11 module `bb-host-trust-boundary==0.1.0` under **only** `Source/host_trust_boundary/**` with frozen `ClaimedHostFingerprint`, `HostReferenceAssessment`, `HostReferenceOutcome`, `HostReferenceReason` and pure `assess_reference_host_boundary(...)` per Design/182.
- Exactly eight result fields, always `runtime_authorized=False`, `requires_trusted_host_provisioning=True`, `requires_full_fsm=True`. Support accepted/rejected TASK-001 typed inputs. No file/OS/env reads, trust token, callback, positive output path, network or hardware.
- Matching approved policy raw bytes and fixed E2 TEST_ONLY pins => `REFERENCE_MATCH_NO_AUTHORITY`. Policy/header/host mismatch => `REFERENCE_MISMATCH`, with deterministic fixed ordered reasons. Rejected preflight takes precedence and yields `UPSTREAM_REJECTED`; no run or candidate digest. Strict type validation and fail closed for malformed wrappers and forged data.
- Never use Design/owner chat approval JSON as runtime permission, nor promote P210 design-trace engine/scheduler version to an actual trusted executable. No driver, physical actuator, full FSM, transaction journal, trace writer, real allowlist, ACK, S1 or TASK-006 PASS/ADMITTED adapter.

## AC-01…AC-10

| AC | Observable acceptance |
|---|---|
| AC-01 | Only new `Source/host_trust_boundary/**` plus immutable Owner-released six Design/Task files in PR; old source/policy/schemas/Design untouched. |
| AC-02 | All **48 P222-T01…T48** run through real TASK-001 `validate_wire` before E2, correct accepted/rejected status, deterministic exact eight-field output. |
| AC-03 | Exact original policy bytes match approved R1 SHA-256; modified whitespace/BOM/LF/key order/numeric values/approved key always mismatch. |
| AC-04 | Eleven fixed E2 synthetic fingerprint fields validated independently, strict type equality, stable ordered reasons for combinations. |
| AC-05 | Accepted matching test pins still `runtime_authorized=False`, no runtime allowlist or executable attestation; two permanent missing-trust reasons. |
| AC-06 | Rejected preflight takes precedence even if test host claim matches; scenario cannot inject approved, owner, engine, scheduler, policy, trust, or sink. |
| AC-07 | 18 mandatory negative test families N01…N18, wrong Python types, forged wrappers/digests/approval, deterministic locale/TZ, no security bypass. |
| AC-08 | Pure immutable bounded work (O(policy byte length) hash plus O(1) header fields), no event rescan, filesystem, environment, network, output, trace/ledger, code execution or real hardware. |
| AC-09 | Actual unit/integration tests; 48 named oracles, dev/wheel smoke, dependency/build/install checks and read-only TASK-001…009 regressions, compact honest machine evidence and exact provenance/hashes. |
| AC-10 | Owner UAT 3 PowerShell commands + full verify. Do not rerun expensive regression solely for PR packaging after unchanged Owner UAT; PR only on explicit owner permission; no Developer merge. |

## Test and handoff

- Implement all 48 machine oracle cases and 18 adversarial families from Design/183, using pinned legal P210 fixture and raw policy bytes, test-synthetic fingerprint outside wire JSON. Each case is an actual call to genuine TASK-001 followed by TASK-010. Invalid wire is rejected by TASK-001, not silently fixed.
- `scripts/verify.py` checks pinned base, release SHA256/Git blob values, build/install/dev+wheel smoke, pytest/JUnit, pip check and independent read-only regressions of TASK-001–009 from their own working directories. Report actual counts, errors, warnings, skip and whether full verification was run. Do not hide historical test failures.
- Provide 3 PowerShell UAT commands and one aggregate full verification after preparing local `.venv`.

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
# Optional Owner full final UAT, once:
.\.venv\Scripts\python.exe scripts\verify.py
```

- Developer reports READY FOR OWNER UAT with real output and concise evidence pointers; Owner tests and explicitly authorizes PR. If test/script/runtime/dependency changed after Owner UAT, rerun relevant checks before approval. On full verification PASS with unchanged bytes, Developer may prepare PR without rerunning all regressions just to write prose.

## STOP / future gate

If asked to install real trust allowlist, authorize host, sign/certify engine, assert digest equals trust, run FSM, advance committed history, create PASS/ADMITTED verdict, output virtual/real actuator, touch firmware, change R1/R1.1 policy/schema: **STOP — DESIGN CLARIFICATION**. These need separate SA/Owner approval. Physical receiver/servo/flapping-wing flight remains **NO-GO**.
