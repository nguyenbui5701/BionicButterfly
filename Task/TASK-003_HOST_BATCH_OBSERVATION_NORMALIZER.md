# TASK-003 — HOST_BATCH_OBSERVATION_NORMALIZER (SafetySupervisor Stage A)

| Field | Value |
|---|---|
| Status | OPEN — SA RELEASED; OWNER ASSIGNS |
| Source `main` baseline | `12b4ee1355d146080810d028843d24481f88af77` (merged PR #2) |
| Scope | G0-A1 / PC_SIM_ONLY; pure read-only observations, **not** full SafetySupervisor |
| Allowed writes | `Source/host_batch_observations/**` ONLY |
| Suggested branch | `feature/TASK-003-host-batch-observations` |
| PR gate | Developer waits for explicit Owner UAT acceptance / “Tạo Pull Request” |

## 1. Task goal

Implement a deterministic library taking a TASK-002 `VirtualTickBatch`, returning a deeply immutable view of **all** observations in that tick, grouped by exact valid control semantic equivalence, with flags for UART INVALID, valid-control conflicts, RF presence and BOOT/RESET/ACK/catastrophe. Preserve all original identities and timestamps, and emit no runtime state, accepted intent or output.

This is **Stage A** preparing the SafetySupervisor; full ARM/FSM/freshness/failsafe remain future tasks.

## 2. Required reading (read only)

- `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`.
- `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` (blob `e6d988d160773219811d28cdb346b5a4590a0fa0`).
- `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md`, `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md`, `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md`.
- `Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md`, `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md`.
- `Design/158_G0A1_VIRTUAL_TICK_SCHEDULER_CONTRACT_DERIVED_R11.md`, new `Design/160_...`, `Design/161_G0A1_TICK_OBSERVATION_NORMALIZATION_CONTRACT.md`, `Design/162_G0A1_TASK003_NORMALIZER_ORACLES_AND_REVIEW.md`.
- `Design/fixtures/P215_BATCH_NORMALIZER_ORACLE_INDEX.json`, `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` (blob `1d10c76e34be70880a65252d89a6bca89839fea9`).
- `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py` (blob `506aa23cbe5e01671f3f51c1f2fd64444d7f0578`) and `Source/host_virtual_ticks/src/bb_host_virtual_ticks/scheduler.py` (blob `755e74b740f1a68eb6f095b6895d80cba3831928`).

Verify pinned file blob SHA against baseline. If source/Design changed, report `BLOCKED — DESIGN CLARIFICATION`. Historical `_CANDIDATE` filenames refer to owner-approved frozen bytes; do not rename.

## 3. Implementation boundaries

- Create package **only** in `Source/host_batch_observations/**`, Python >=3.11; runtime standard library plus local pinned TASK-001/TASK-002 dependencies.
- Public API e.g. `normalize_tick_observations(batch: VirtualTickBatch) -> NormalizedTickObservations`.
- Follow **all details** in `Design/161`: original immutable source event refs/order, causal IDs sorted unsigned UTF-8, VALID controls in first-seen semantic groups, group latest **original** timestamp and sorted group IDs, INVALID controls, independent conflict flags, raw RF presence facts, lifecycle event flags.
- Never turn exact Decimal into Python float; accept different JSON spellings with same exact value as equivalent. `0.1000000` vs `1e-1` must group, not conflict. Never Unicode-normalize event IDs.
- If INVALID and two distinct valid bodies appear in same tick, **both** has-invalid and has-conflict flags must be true. Do not choose reason priority or suppress observations.
- No `state_after`, `reason_codes`, `rf_effective`, `can_arm`, `accepted_frame_at_us`, `output_allowed`, M0 efforts or any partial execution authority fields.
- No filesystem/network/runtime hardware IO, wall-clock, RNG, sleeping, policy or schema mutation, parser reimplementation, scheduler rewrite, FSM, trace, GPIO, real UART/RF, PWM, servo or flight control.
- Wrong API caller type rejects at call time without creating a `P_*` diagnostic sidecar or tick.

## 4. Acceptance criteria

| ID | Required proof |
|---|---|
| AC-01 | Git diff strictly in allowed Source subtree; no IO/side effects in runtime (import/call scan). |
| AC-02 | All **18** P215-T01..T18 executable oracle cases from real TASK-001 preflight + TASK-002 scheduler; exact expected results. |
| AC-03 | UTF-8 ID sorting, no Unicode normalization, original member event identity/source order. |
| AC-04 | Equivalent controls grouped once, latest original timestamp; different control bodies conflict flag. |
| AC-05 | INVALID in-band alone/mixed retained; INVALID and control conflict can coexist without short circuit. |
| AC-06 | RF HEALTHY, LOST, UNKNOWN all retained; no `rf_effective` or freshness update. |
| AC-07 | BOOT/RESET/ACK/catastrophe presence, multiple ACK preservation, no transition priority. |
| AC-08 | Empty/subsequent ticks contain no invented or carried-over observations. |
| AC-09 | Deep immutability, repeated deterministic output, invalid callers, legal near-20k batch O(N) instrumented. |
| AC-10 | Build/install/pytest/smoke/pip-check logs; read-only TASK-001 and TASK-002 regression results; three concise Windows UAT commands. |

No Design fixture marked PASS in advance. On failure fix only within allowed subtree. Report explicit PASS/FAIL/SKIP/NOT RUN.

## 5. UAT and handoff protocol

After creating a `.venv` and installing local dependencies, Developer shall supply **at most these three commands** for owner to run from `Source/host_batch_observations`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Owner runs UAT; only Owner explicitly instructs creation of Pull Request. On permission, Developer commits/pushes task branch with AC-01..10 test proof, full diff, pinned SHA, versions and constraints, and **does not merge**. SA reviews PR in isolated `ReviewPR/pr-<number>/`, Owner decides merge. If unresolved contract ambiguity arises, STOP and request SA rather than inventing a new policy.

## 6. Safety stop conditions

Any request to implement ARM, RF timeout/freshness, fault state priority, ACK recovery, controlled output, policy trust allowlist, trace commit, new wire/`E_*` codes, hardware, flight, or change frozen Design: **BLOCKED — DESIGN CLARIFICATION**. Such tasks require separately scoped approval and test oracles. Real hardware and flight remain NO-GO.

**Initial status:** task specification created; Developer implementation NOT RUN; no runtime PASS claimed by SA.
