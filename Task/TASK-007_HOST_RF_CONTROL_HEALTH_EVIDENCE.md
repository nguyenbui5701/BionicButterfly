# TASK-007 — HOST_RF_CONTROL_HEALTH_EVIDENCE (Stage D1)

| Field | Value |
|---|---|
| Status | **OPEN — SA RELEASED / OWNER TO ASSIGN** |
| Git baseline | `a47dc157453547125f5172b4ef165c3b522ff0c8` after PR #6 merge |
| Project scope | G0-A1 **PC_SIM_ONLY**, evidence-only; NO authoritative health PASS/ADMITTED |
| Allowed Developer write tree | `Source/host_health_evidence/**` **ONLY** |
| Suggested branch | `feature/TASK-007-host-health-evidence` |
| PR | Owner UAT PASS and **explicit approval** before creation; Developer never merges |

## Goal and task boundary

Create a pure, deterministic Python 3.11+ library computing **current RF batch evidence, carried prior RF status evidence, and observed control candidate diagnostics** using genuine TASK-003/004/005 results and an independently supplied **synthetic TEST-ONLY** prior RF status. Implement `Design/173` exactly. The output is **not** an effective RF status, accepted control, safety transition, approved guard, command or permission. It must not produce or pass a real `HypotheticalQualificationVerdict(PASS, ADMITTED)` into TASK-006.

This repairs an important information gap: even if prior healthy-RF timestamp age is still fresh, a later committed RF LOST must block claims of carried HEALTHY. Same-tick HEALTHY+LOST follows R1 LOST dominance; HEALTHY+UNKNOWN remains explicitly ambiguous without inventing a new priority.

## Mandatory reading and hash pin

1. `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`.
2. Frozen R1/R1.1: `Design/115`, `116`, `117`, `118`, `141`, wire `132` and closed schema `contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json`. Use full filenames in the repository.
3. Previous task boundary contracts `Design/161`, `164`, `167`, `170`. Read-only packages `Source/host_preflight_m0/**`, `host_virtual_ticks/**`, `host_batch_observations/**`, `host_temporal_guard_facts/**`, `host_safety_priority_kernel/**`, `host_arm_qualification/**`.
4. **New:** `Design/172_TASK006_MERGE_CLOSEOUT_AND_TASK007_BASELINE.md`, **`Design/173_G0A1_RF_CONTROL_HEALTH_EVIDENCE_STAGE_D1.md`** (normative derived boundary), `Design/174_TASK007_HEALTH_EVIDENCE_ORACLES_REVIEW.md`, `Design/fixtures/P219_HEALTH_EVIDENCE_ORACLE_INDEX.json` (36 design-only cases) and `Design/P219_TASK007_RELEASE_MANIFEST.json`.
5. Assert parent Git baseline and immutable source path hashes from Design/172; policy SHA-256 `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. Never edit approved R1 or replace frozen source/policy bytes.

## Acceptance criteria AC-01…AC-10

| AC | Required actual proof |
|---|---|
| AC-01 | Only task-local `Source/host_health_evidence/**` code, tests, scripts and evidence. No changed prior modules/Design/Task, policy, schema, hardware, `.github` or ReviewPR. Owner-issued Design/Task artifacts may be tracked unchanged if Owner explicitly requests. |
| AC-02 | All **36** P219-T01…T36 pass via actual TASK-001→002→003→004→005 pipeline; exact eight output fields, types, enum labels and no synthetic history/state in wire JSON. |
| AC-03 | Same-tick RF HEALTHY+LOST resolves LOST independently of source order; HEALTHY+UNKNOWN yields `AMBIGUOUS_CURRENT` with no promoted healthy; carry prior status correctly. |
| AC-04 | Independent prior RF age boundary: 200000us inclusive; 200001us stale. Prior LOST/UNKNOWN must override still-fresh older healthy RF evidence. Current later HEALTHY visible but uncommitted. |
| AC-05 | INVALID + VALID and distinct valid groups deny all current control candidates; equivalent valid groups produce one timestamp candidate. No RF/control cross-refresh. |
| AC-06 | Candidate with RF lost/unknown/stale/missing blocked; RESET/catastrophe/CONTINGENCY/latch and armed stale prior blocked. No real PASS/ADMITTED/control/state/effort outputs. |
| AC-07 | Reject malformed prior status/timestamp and mismatch with TASK-004; wrong Python types, bool time, mutable RF records, incompatible mirrored flags. No forged wrapper treated as authentication. |
| AC-08 | Pure, immutable exact eight fields, deterministic; scans current RF only O(N_RF), no source-control-event/member rescan; no clocks/IO/trace/mixer/host output or retained memory. |
| AC-09 | Run honest unit/integration, build/wheel, pip check, smoke and read-only TASK-001…006 regressions; counts/errors/warnings and revision hashes in compact machine-readable evidence, with no invented PASS. |
| AC-10 | Owner final UAT uses 3 copy-paste Windows commands; Developer does not duplicate full verification for PR packaging if **same code/test/dependencies/evidence** remained accepted; PR only upon explicit Owner authorization; no self-merge. |

## Implementation and tests

Recommended package: `bb-host-health-evidence` 0.1.0 with pure public API `assess_health_evidence(...)` and frozen `PriorCommittedRFStatus`, `HealthEvidenceFacts`, `RFEvidenceKind`, `ControlEvidenceKind`. No new E_ reason code or an authority-bearing adapter. The prior RF record is a **test fixture at this stage**. Do not expose it as a writable host control/config source.

The 36 P219 cases must run real strict wire preflight → scheduler → normalization → temporal → priority, then consume separate synthetic prior RF status. Fixture semantics, order and expected enums follow `Design/173` exactly. Also add mandatory negative, determinism, O(N_RF) and no-IO tests from Design/174. Avoid unnecessary duplicate full-suite reruns for a commit containing only unchanged owner documents.

## Owner UAT (after Developer sets up virtual environment)

From `BionicButterfly/Source/host_health_evidence`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Developer can additionally provide one `scripts/verify.py` command for full regressions, artifact build and source SHA verification; Owner runs it once for final acceptance. If anything affecting execution changes later, rerun relevant tests and reapprove. Evidence should contain exact commit/source revision and machine-readable per-case JUnit, **not a verbose narrative of 36 rows**.

## PR and stop conditions

Developer: implement in allowed subtree, test during development, deliver short result plus UAT commands. **Wait for Owner's UAT PASS and explicit request to create PR**, then include only approved changes and attach short evidence links and HEAD. SA reviews the PR independently for safety/hierarchy; Owner alone merges.

STOP with `BLOCKED — DESIGN CLARIFICATION` if asked to resolve HEALTHY+UNKNOWN as healthy, fabricate critical power/scheduler wire events, implement current RF effective status as authority, invent user approval tokens, alter R1 policy, connect outputs/actuators or implement full FSM without a new task. G0-B/G4 physical/flight remain NO-GO.
