# TASK-004 — HOST_TEMPORAL_GUARD_FACTS (SafetySupervisor Stage B)

| Field | Value |
|---|---|
| Status | **OPEN — SA RELEASED / OWNER TO ASSIGN** |
| Baseline | `ed106d22c52647090768ef60fb1e4c33384e9227` (merged PR #3) |
| Task / safety scope | G0-A1 `PC_SIM_ONLY`; **pure read-only temporal age and candidate facts only** |
| Allowed write subtree | `Source/host_temporal_guard_facts/**` **only** |
| Suggested branch | `feature/TASK-004-host-temporal-guard-facts` |
| PR policy | Developer must await Owner UAT acceptance and explicit instruction **“Tạo Pull Request TASK-004”** |

## Goal

Implement one small deterministic Python 3.11+ library that consumes **an actual TASK-003 `NormalizedTickObservations` object** and a separate immutable **prior-committed timestamp-facts input**. It computes **two independent, exact 200,000µs age checks** plus clearly uncommitted RF/control candidate timestamps. It must never mistake a new observation for an accepted signal or override SafetySupervisor state/authority. This is Stage B only; the eight-state FSM and trace transaction remain later tasks.

## Required reading (before code)

1. `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md` (role, branch, PR gates).
2. `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` (R1 clock and authority); `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md` (2 independent 200ms timeouts); `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md` (do not invent runtime codes); `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` (precedence).
3. `Design/contracts/SIM_POLICY_22A_R1.canonical.json` (exact policy digest domain); `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` (frozen wire v2).
4. `Design/158_G0A1_VIRTUAL_TICK_SCHEDULER_CONTRACT_DERIVED_R11.md`, `Design/161_G0A1_TICK_OBSERVATION_NORMALIZATION_CONTRACT.md` (TASK-002/003 boundaries).
5. **New:** `Design/163_TASK003_MERGE_CLOSEOUT_AND_TASK004_BASELINE.md`, `Design/164_G0A1_TEMPORAL_GUARD_FACTS_CONTRACT.md`, `Design/165_TASK004_TEMPORAL_GUARD_TEST_AND_REVIEW.md`, `Design/fixtures/P216_TEMPORAL_GUARD_ORACLE_INDEX.json` (22 expected cases).
6. `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py`, `Source/host_virtual_ticks/src/bb_host_virtual_ticks/scheduler.py`, `Source/host_batch_observations/src/bb_host_batch_observations/normalizer.py` and their package `__init__.py` (use existing libraries unchanged).
7. Read original R1 conformance vectors `Design/120_G0A1_R1_CONFORMANCE_ORACLES_AND_TRACEABILITY.md` (especially P28-T13/T14/T26), but do not claim state-transition or output cases PASS at this Stage B.

**Must pin source Git commit to `ed106d22c52647090768ef60fb1e4c33384e9227` and verify frozen Design paths**, not rely only on moving `main`. Policy JSON bytes retain approved SHA-256 `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`.

## Required implementation

- Place all code, tests, scripts, local packaging and evidence **only under** `Source/host_temporal_guard_facts/**`; no edits in `Design/`, `Task/`, existing `Source/` packages, firmware, `.github/` or `ReviewPR/`.
- Expose a pure API equivalent to `evaluate_temporal_guard_facts(observations: NormalizedTickObservations, prior: PriorCommittedTimestampFacts) -> TemporalGuardFacts`; immutable result fields, input invariants, exact age/candidate semantics follow `Design/164` **without replacing them by inferred rules**.
- Reject malformed caller, future/non-grid prior commit times, `bool` masquerading as `int`, negative/future observation timestamp. `None` means never accepted/observed and implies `age=None`, not fresh.
- Exact freshness: `age_us <= 200000`; at 200001 stale. Original timestamp must not be snapped to tick time. Two sources independent, no cross-refresh.
- Candidate timestamps from current batch are **UNCOMMITTED**, NOT an accepted pilot frame or effective RF. Single uncontested VALID control group only; RF candidate only when all RF observations are HEALTHY. With RF LOST/UNKNOWN, leave no healthy candidate; preserve hazard flags. No assumption about the unapproved HEALTHY+UNKNOWN effective-priority rule.
- Do not mutate or return an updated prior snapshot; **no history or state machine**. No `can_arm`, `rf_effective`, `control_accepted`, `output_allowed`, `reason_codes`, virtual effort, M0, trace, output callbacks, wall time/sleep/RNG, network, filesystem or hardware.

## Acceptance criteria (all required)

| ID | Acceptance | Proof |
|---|---|---|
| AC-01 | Only allowed Source subtree, no prohibited IO/FSM/output imports | `git diff` & import/call audit |
| AC-02 | All **22** P216 oracle cases executed via real TASK-001→002→003 positive pipeline and exact output comparison | Oracle-driven pytest |
| AC-03 | Independent 200000/200001µs boundary checks for frame and RF, no float/rounding and no absent-as-fresh | T03–T11 |
| AC-04 | Correct uncommitted current RF candidates, mixed HEALTHY/LOST or UNKNOWN fails closed (no effective health assigned) | T12–T16 |
| AC-05 | VALID control candidate without authorization, INVALID/conflict detection, RESET does not auto-accept | T17–T20 |
| AC-06 | Prior freshness can coexist with current hazard; new VALID candidate **cannot** refresh prior stale timestamp | T21–T22 |
| AC-07 | Source and prior deeply immutable, deterministic repeated calls, rejects wrong types/future timestamps/`True` as int | Extra negative tests |
| AC-08 | No state/authority fields or timestamp commits; exactly described output contract | Structural tests and review |
| AC-09 | TASK-001, 002, 003 regression **attempted and reported**; build/wheel/unit/smoke/pip-check executed; no invented PASS | Actual counts, logs/versions |
| AC-10 | Three simple Windows UAT commands and short report; PR only by Owner authorization | README & handoff |

### Owner UAT (after Developer sets up `.venv` and dependencies)

Run from `Source/host_temporal_guard_facts`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

If the actual environment differs, Developer must provide equally copy-pastable commands. Owner handles unzip/docs Git and runs these commands instead of asking AI to repeat them. Developer tests/debugs, reports PASS/FAIL accurately, and **does not create PR** until Owner accepts UAT. Then Developer opens a PR referencing TASK-004, source pin and AC-01..10, **does not merge**. SA reviews in isolated `ReviewPR/pr-<id>`; Owner decides merge.

## Stop / escalation conditions

Any request to decide RF effective health (especially UNKNOWN+HEALTHY), accept/refresh pilot authority, implement 20ms/100ms ARM qualification, FSM transition/RESET/ACK, invoke M0/output, write trace, add wire fields/reason codes, enable physical sensors/servo/flight, or modify approved policy requires **BLOCKED — DESIGN CLARIFICATION** to SA. TASK-004 intentionally has **no simulator runner, no host execution allowlist and no flight authorization**.

**At issue:** Implementation NOT STARTED; all design oracles NOT RUN on TASK-004; no PR yet.
