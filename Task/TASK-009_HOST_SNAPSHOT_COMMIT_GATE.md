# TASK-009 — HOST_SNAPSHOT_COMMIT_GATE (SafetySupervisor Stage E1)

| Attribute | Required |
|---|---|
| Status | **OPEN — SA RELEASED / OWNER TO ASSIGN** |
| Baseline `main` | `e61f97e388662a48a13ccb6b308954436cbb87ec` after PR #8 merged |
| Scope | **G0-A1 PC_SIM_ONLY; TEST_ONLY transaction/snapshot gate** |
| Developer may write | `Source/host_snapshot_commit_gate/**` **ONLY** |
| Branch recommendation | `feature/TASK-009-host-snapshot-commit-gate` |
| PR | Only after Owner UAT PASS + explicit authorization; no self-merge |

## Objective

Implement **TestOnlySnapshotLedger** that holds one frozen OwnerSnapshot, prepares a conservative candidate from actual TASK-003/004/005/007/008 facts, appends one complete **internal** test-only record, and advances the snapshot **ONLY after private journal full-append acknowledgment**. On any append/serialization/quota failure no snapshot advances, the ledger becomes terminal FAILED_INCOMPLETE_EVIDENCE and no output can be exposed. All non-approved positive ARM/RF/command transitions DEFER without append.

**Not** the final full R1 Committed State Owner. This is Stage E1 test-only shell and cannot be imported by physical flight code. Its internal journal is **not** the approved `Design/118/134` full R1 canonical trace writer; no runtime trust, credential, JCS full trace, ACTIVE output, complete FSM, ACK recovery or accepted RF/control timestamp advancement may be claimed.

## Mandatory reading before coding

1. `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`.
2. Controlling frozen R1 Design/115, /116, /117, **/118**, /132, /134, /141 and `Design/contracts/SIM_POLICY_22A_R1.canonical.json` (SHA-256 `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`).
3. Read-only derived interfaces Design/164, /167, /170, /173, /176 and public Python interfaces under `Source/host_temporal_guard_facts`, `host_safety_priority_kernel`, `host_health_evidence`, `host_guard_triage`; prior TASK-001..008 packages remain immutable.
4. **New:** `Design/178_TASK008_MERGE_CLOSEOUT_AND_TASK009_BASELINE.md`, **`Design/179_G0A1_COMMITTED_SNAPSHOT_GATE_STAGE_E1.md`**, `Design/180_TASK009_SNAPSHOT_GATE_ORACLES_AND_SA_REVIEW.md`, `Design/fixtures/P221_SNAPSHOT_GATE_ORACLE_INDEX.json`, `Design/P221_TASK009_RELEASE_MANIFEST.json`.
5. Check pinned `main` SHA and frozen Git blob hashes from Design/178; on mismatch stop: `BLOCKED — DESIGN CLARIFICATION`. Do not modify Design or old Source to satisfy tests.

## Implementation

- Python >=3.11, pip-installable local package `bb-host-snapshot-commit-gate` version 0.1.0; no external runtime dependencies beyond pinned local previous packages and stdlib; tests can use pytest/build.
- Implement frozen 14-field `OwnerSnapshot`, test-only genesis + **private test fixture seed**, `TestOnlyAtomicJournal`, frozen five-field `SnapshotCommitResult`, and `TestOnlySnapshotLedger.commit_tick(...)` exactly as Design/179. Strongly prefer no generic production adapter/public receipt method.
- Enforce consecutive 5000µs ticks from last acknowledged tick, in-sync upstream typed records and original timestamps; when pre-state `FAULT_LATCHED` or current catastrophe, latch; when armed explicit LOST/INVALID/conflict or stale prior health, CONTINGENCY even with RESET; ordinary RESET only from non-armed state; BOOT T0 only. Defer all unresolved armed, healthy ACTIVE, ACK recovery and positive RF/frame/window/effort cases.
- For *every* acknowledged E1 tick preserve prior accepted RF/control history; clear windows/held intent on fault/RESET transitions; never create a new accepted RF/control timestamp or REAL trace digest.
- Fault-test journal modes before-append/short-write/after-write-before-ack/quota/serialization, sticky failure status; no snapshot advance or retry after failure, no output or post-state publication before ack. E1 success means **test-only journal ack**, not R1 full-run success.

## Acceptance criteria

| AC | Observable PASS condition |
|---|---|
| AC-01 | All changes to new `Source/host_snapshot_commit_gate/**`; upstream and frozen R1/R1.1 unchanged. |
| AC-02 | All **48 P221-T01…T48** oracles via genuine upstream pipeline or explicit legal supplemental batches; source prior/pre-state/journal fault modes are synthetic test-only, not scenario JSON. |
| AC-03 | Immutable 14-field snapshot with full historical invariants; snapshot only changes generation/last tick, approved negative state and clearing fields after complete internal append ack. |
| AC-04 | LATCH persistence/catastrophe/CONTINGENCY dominance, armed explicit hazard or independently stale prior → CONTINGENCY before RESET, nonarmed RESET → SELF_TEST, BOOT → SELF_TEST. |
| AC-05 | Positive ARM, healthy ACTIVE/S1, same-tick ambiguous UNKNOWN/HEALTHY, ACK recovery and any candidate/accepted timestamp refresh **DEFER**, no journal append. |
| AC-06 | Deterministic internal record bytes, one complete append per eligible tick, only private ack triggers snapshot swap; no R1 trace completeness claims. |
| AC-07 | Serialization/quota/short write/before-append/after-write-before-ack failure leaves old snapshot unchanged and terminal FAILED_INCOMPLETE_EVIDENCE; never retry. |
| AC-08 | Exact immutable typed outputs, false/forged receipts rejected, no wall-clock/file/network/external IO, no M0/virtual or physical output, no mutable snapshot exposure. |
| AC-09 | Real unit/integration tests; 48 named oracles, negatives, dev+wheel smoke, build/install/pip and read-only TASK-001..008 regressions; provenance and actual PASS/FAIL/SKIP recorded. |
| AC-10 | Owner receives 3 PowerShell UAT commands and optional full verify; no unnecessary duplicated full tests after unchanged Owner UAT; no PR without explicit Owner permission. |

## UAT & PR handoff

Developer prepares an isolated `.venv`, reports exact run status with JUnit/JSON and three commands. From `Source/host_snapshot_commit_gate` Owner runs:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
# Optional full final verification once:
.\.venv\Scripts\python.exe scripts\verify.py
```

Developer tests/debugs while implementing. Owner signs off final full UAT, and only then explicitly authorizes PR. If unchanged, do not rerun regression just to write a long handoff; re-run appropriate tests after code/test/dependency alterations. PR contains new task Source plus unchanged Owner-issued Design/Task documents; no merges without Owner. SA reviews in isolated `ReviewPR/pr-<N>` where available; don't touch Developer workspace.

## STOP

If fulfilling this task would require positive host approval, a general journal receipt credential, real trace writer, `HealthVerdict.PASS`, `ControlVerdict.ADMITTED`, accepted RF/control timestamp updates, ARM/ACTIVE output, S1, ACK recovery, real voltage/scheduler event, servo/PWM/RC access, or changing frozen policy, **STOP — DESIGN CLARIFICATION**. G0-B/G4 and physical flight remain NO-GO.
