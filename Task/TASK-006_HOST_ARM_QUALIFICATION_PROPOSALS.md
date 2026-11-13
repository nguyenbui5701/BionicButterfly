# TASK-006 — HOST_ARM_QUALIFICATION_PROPOSALS (SafetySupervisor Stage C2)

| Field | Value |
|---|---|
| Status | OPEN — SA RELEASED / OWNER TO ASSIGN |
| Baseline `main` | `f2c9237bd4a1e2e077c15db6eb4c22ed2a250d5d` (merged PR #5) |
| Scope | G0-A1 `PC_SIM_ONLY` — pure proposal, not committed FSM / output |
| Allowed Developer write area | `Source/host_arm_qualification/**` ONLY |
| Proposed branch | `feature/TASK-006-host-arm-qualification` |
| PR gate | Owner UAT and explicit PR permission first; Developer does not merge |

## Goal

Implement deterministic, immutable **LOW/HIGH/ARM/DISARM qualification proposals** from genuine TASK-003, TASK-004 and TASK-005 outputs plus independently supplied *synthetic, hypothetical* prior-window and guard-adjudication test inputs. Implement the exact R1 timing mechanics in `Design/170`, **without** claiming any frame was actually admitted by a trusted health arbiter, committing a safety state or publishing an output.

This task MUST NOT create a complete FSM, effective RF resolver, host allowlist, accepted-control timestamp state owner, ACK recovery, trace writer, mixer output, motor/servo/RC interface or real-flight control. A positive proposal is **not** `can_arm` or actuator permission.

## Required read-only material (in this order)

1. Repo rules: `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`.
2. Frozen authority: `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` (Git blob `e6d988d160773219811d28cdb346b5a4590a0fa0`), `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md`, `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md`, `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md`, `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md`.
3. R1.1 wire and mixer: `Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md`, `Design/133_R11_VIRTUAL_MIXER_M0_EXACT_ARITHMETIC_CANDIDATE.md`; `Design/contracts/SIM_POLICY_22A_R1.canonical.json`, approved SHA-256 `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`.
4. Earlier contracts `Design/158`, `161`, `164`, `167` (find complete filenames within Design). New: `Design/169_TASK005_CLOSEOUT_AND_TASK006_BASELINE.md`, **`Design/170_G0A1_ARM_QUALIFICATION_PROPOSALS_STAGE_C2.md`**, `Design/171_TASK006_ARM_QUALIFICATION_ORACLES_AND_REVIEW.md`, `Design/fixtures/P218_ARM_QUALIFICATION_ORACLE_INDEX.json` and `Design/P218_TASK006_RELEASE_MANIFEST.json`.
5. Read upstream packages and public APIs: `Source/host_preflight_m0/`, `Source/host_virtual_ticks/`, `Source/host_batch_observations/`, `Source/host_temporal_guard_facts/`, `Source/host_safety_priority_kernel/` (all **read-only**).

Before coding, verify exact parent commit and frozen bytes. Any discrepancy: STOP with `BLOCKED — DESIGN CLARIFICATION`, do not silently rewrite Design or policy.

## Implementation acceptance criteria

| ID | Observable acceptance / proof |
|---|---|
| AC-01 | All new implementation/tests/scripts/evidence in `Source/host_arm_qualification/**`; no preceding module or frozen contract changed. |
| AC-02 | All **32** P218-T01..T32 oracles executed via actual preflight→scheduler→normalizer→temporal→priority→qualification, exact nine-field proposals and types; synthetic history/verdict **never in wire**. |
| AC-03 | LOW 19,999/20,000/20,001µs boundaries; two **distinct ticks**, original timestamps, exact Decimal, no empty/duplicate same-tick false qualification. |
| AC-04 | HIGH edge needs a **prior committed tick** of LOW qualification, neutral HIGH with flap ≤0.02 and |steer| ≤0.05; no direct ARM permission. |
| AC-05 | HIGH confirm 99,999 vs 100,000 vs 100,001µs; later **new frame/tick** required, never timer-only. |
| AC-06 | LOW disarm from ARM_CHECK/ARMED_IDLE/ACTIVE does not double-count as new LOW; demand threshold strictly flap >0.05 in ARMED_IDLE; no state/output. |
| AC-07 | FAIL/UNRESOLVED, INVALID, conflict, RF LOST/UNKNOWN, RESET, catastrophe and stale prior health cannot cause a positive proposal; contradictory PASS/ADMITTED synthetic verdict rejected. |
| AC-08 | Closed enum/immutable nine-field result; correct window invariants/validation, no authorization/accepted timestamp/effort/reason code; O(1), deterministic, no event scans or I/O. |
| AC-09 | Actual unit/integration + read-only TASK-001..005 regressions, compile/build/install, dev/wheel smoke, pip check, environment and provenance logs with actual PASS/FAIL/SKIP. |
| AC-10 | Three short copy/paste Windows UAT commands; Owner explicitly authorizes PR after UAT; no self-merge. |

## Implementation guidance

- Python >=3.11, standard-library runtime plus pinned *local* upstream packages. Choose package `bb-host-arm-qualification` 0.1.0 if no collision. Match `Design/170` precisely; do not reinterpret its synthetic hypothetical guard verdict as a trusted runtime decision.
- Preserve first LOW original timestamp, later committed LOW qualification tick, HIGH edge original timestamp/committed tick, and distinct-tick requirements. Exact boundary math. Keep proposed windows and outcomes deeply frozen. Pure function with no global mutable state.
- For `CONTINGENCY`, **defer** ACK-LOW qualification and recovery to a future task; TASK-005 `CONTINGENCY_HOLD` is provisional and cannot be promoted into a permanent recovery ban.
- For `ARMED_IDLE` a HIGH demand >0.05 is *only* DEMAND_OBSERVED. Any ACTUATION_ACTIVE output/hold (S1) remains for a later full FSM/trace task.
- Never generate new E_ codes, assume HEALTHY+UNKNOWN effective RF priority, invent power/scheduler events, alter APPROVED 22A policy, authorize user JSON state, or add firmware/hardware adapters.

## Test/UAT/PR handoff

Developer sets up isolated `.venv` with local pinned prerequisites. From `Source/host_arm_qualification`, Owner runs these three commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Developer reruns read-only regressions from each upstream package directory to avoid `scripts.scenarios` name collision; records real counts/warnings and a short file inventory. After Owner UAT PASS, **wait** for explicit PR permission. Owner manages Design/Task docs staging/push, Developer commits only authorized task code and requested owner-issued release docs in the PR, SA reviews in `ReviewPR/pr-<number>` isolation, and only Owner merges.

**Release status: specification only; no TASK-006 runtime source or test PASS yet.** Real RC, actuator outputs, physical bench and flight remain NO-GO.
