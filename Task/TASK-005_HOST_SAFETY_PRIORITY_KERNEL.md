# TASK-005 — HOST_SAFETY_PRIORITY_KERNEL (SafetySupervisor Stage C1)

| Field | Value |
|---|---|
| Status | **OPEN — SA RELEASED, OWNER TO ASSIGN** |
| Baseline | `efe7fa3aff1beeb01af98b98a06593bd8e7af192` after PR #4 merge |
| Scope | G0-A1 / PC_SIM_ONLY, **partial high-priority FSM adjudication only** |
| Allowed Developer write subtree | `Source/host_safety_priority_kernel/**` only |
| Branch | `feature/TASK-005-host-safety-priority-kernel` |
| PR policy | After Owner UAT and explicit permission ONLY; no automatic merge |

## 1. Goal

Implement a tiny, pure, deterministic **high-priority decision kernel** over one TASK-003 normalized tick and matching TASK-004 temporal facts with an independently supplied synthetic/committed `pre_state`. It may compute only **provisional R1 priority constraints** (BOOT→SELF_TEST, catastrophic fault latch, persistent latch, provisional CONTINGENCY hold, observed armed-state hazards, ordinary RESET). All other behavior returns **DEFER**, never `RETAIN_CURRENT_STATE_AS_SAFE` or `can_arm`.

**Explicitly not** the full SafetySupervisor eight-state FSM, ARM qualification, accepted timestamps owner, complete ACK recovery, age-based health arbitration, self-test authority, trace transaction, or output. No executable simulator or real-flight authority.

## 2. Mandatory reading before coding

- `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`.
- `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` (blob `e6d988d160773219811d28cdb346b5a4590a0fa0`), `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md`, `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md`, `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md`.
- `Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md`, `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md`.
- `Design/161_G0A1_TICK_OBSERVATION_NORMALIZATION_CONTRACT.md`, `Design/164_G0A1_TEMPORAL_GUARD_FACTS_CONTRACT.md`.
- **New:** `Design/166_TASK004_CLOSEOUT_AND_TASK005_BASELINE.md`, `Design/167_G0A1_SAFETY_PRIORITY_KERNEL_STAGE_C1_CONTRACT.md` (normative task boundary), `Design/168_TASK005_PRIORITY_KERNEL_ORACLES_AND_REVIEW.md`, `Design/fixtures/P217_SAFETY_PRIORITY_ORACLE_INDEX.json` (22 positive cases NOT RUN).
- `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py`, `Source/host_virtual_ticks/src/bb_host_virtual_ticks/scheduler.py`, `Source/host_batch_observations/src/bb_host_batch_observations/normalizer.py` and `Source/host_temporal_guard_facts/src/bb_host_temporal_guard_facts/temporal.py`, plus their public exports. **Read-only**.
- `Design/contracts/SIM_POLICY_22A_R1.canonical.json` (policy SHA-256 `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`), and closed wire-v2 schema.

Verify the pinned parent Git SHA and frozen blobs before coding. If source/schema/Design changed, halt with `BLOCKED — DESIGN CLARIFICATION` instead of guessing.

## 3. Implementation constraints

- Python 3.11+; standard library runtime plus local exact 0.1.0 packages TASK-003 and TASK-004 (tests use local TASK-001/002 too). All written files under the allowed subtree. No changes to Design/Task/ReviewPR or previously merged Source.
- Expose an immutable 8-state enum and the pure 
  `assess_safety_priority(pre_state, observations, temporal) -> SafetyPriorityAssessment`.
- Implement **exact A→G priority order** and exact seven-field output from `Design/167` (no public reason/error field, positive authority, output or committed transition).
- Full-batch facts first: catastrophe outranks RESET and observed hazards; prior latch persists; prior CONTINGENCY holds only provisionally; armed-state explicit LOST, standalone UNKNOWN, INVALID or distinct valid conflict outranks RESET; ordinary RESET forces SELF_TEST; BOOT at T0 forces SELF_TEST; everything else **DEFER**.
- For RF HEALTHY+UNKNOWN without LOST, **no invented RF effective priority**: defer but set negative control-qualification block. Prior stale timestamp age does not itself force state in C1; leave to later health FSM. Both cases prohibit any claim of safety/output readiness.
- `blocks_control_qualification` negative-only from explicit hazards, RESET, restricted states and missing/expired prior ages in armed pre-states; its false value MUST NEVER be used as arm/output permission.
- Validate exact upstream types and consistent tick/flag fields, reject malformed caller before producing result, no side effects, no event scan or pipeline rerun. No `can_arm`, current accepted timestamp update, `state_after`, trace/commit, physical adapter or M0 effort.

## 4. Acceptance criteria

| ID | Observable evidence required |
|---|---|
| AC-01 | Developer modified only `Source/host_safety_priority_kernel/**`; runtime imports no IO, policy, trace, devices, mixer, clock or dynamic plugins. |
| AC-02 | All **22** P217-T01..T22 oracle recipes run through real TASK-001→TASK-002→TASK-003→TASK-004; TASK-005 compared exact typed output; synthetic pre-state/prior stay outside JSON. |
| AC-03 | Pre-latched persistence and catastrophe high priority over RESET/ACK/control/RF, across states. |
| AC-04 | Active-state current LOST, standalone UNKNOWN, INVALID and valid conflict force provisional CONTINGENCY before RESET. |
| AC-05 | CONTINGENCY hold is explicitly **provisional** pending full ACK recovery; RESET cannot clear it in C1. |
| AC-06 | Ordinary RESET→SELF_TEST; initial T0 BOOT→SELF_TEST; invalid BOOT/pre-state/tick combos rejected. |
| AC-07 | Unresolved cases return DEFER and never imply accepted control, no age-health decision, SELF_TEST completion, arm window or output. |
| AC-08 | Output records strictly frozen, fields/count exact, flags mirrored across TASK-003/004, O(1), wrong types rejected, deterministic. |
| AC-09 | Actual build/install/pytest/smoke/pip check + read-only TASK-001..004 regressions, pinned provenance and no fabricated PASS. |
| AC-10 | Owner UAT: three copy/paste PowerShell commands; no PR until Owner explicitly authorizes, no self-merge. |

## 5. Tests, UAT and handoff

Implement positive pytest IDs P217-T01..22 and negatives for incorrect caller/shape/type/mismatched flags, immutable results, repeated determinism, A-over-D/E precedence and 0 event scan; compile and package a local wheel. Run **read-only** TASK-001..TASK-004 regression tests from their own directories; report actual count and errors. Store concise evidence (not huge duplicative logs unless needed), include source hashes and Git diff inventory.

From `Source/host_safety_priority_kernel`, after Developer installs an isolated `.venv`, Owner runs:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Developer reports `READY FOR OWNER UAT` with exact PASS/FAIL/SKIP and these commands. Do **not** create PR until Owner says “Tạo Pull Request TASK-005”. Once authorized, Developer commits/pushes the allowed subtree, includes SA-authored docs only where Owner requested, and opens PR into main. SA reviews in isolated `ReviewPR/pr-<number>`; Owner merges.

## 6. Stop conditions

Any attempt to complete ACK recovery, add wire events for power/scheduler, create new public `E_*` reasons, treat HEALTHY+UNKNOWN as effective healthy, authorize ARM/ACTIVE, refresh accepted timestamps, publish output or trace, provision host allowlist or control PWM/UART/RF/servo is **BLOCKED — DESIGN CLARIFICATION**. Hardware G0-B/G4 still NO-GO.

Initial TASK-005 implementation **NOT STARTED**; Design oracles **NOT RUN** against future code. No new safety/runtime authorization is implied.
