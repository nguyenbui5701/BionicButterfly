# TASK-002 — HOST_VIRTUAL_TICK_SCHEDULER (PC-only Pure Tick Enumerator)

| Field | Value |
|---|---|
| Task ID | **TASK-002** |
| Status | **OPEN — OWNER REQUESTED / SA ISSUED**, developer starts only on owner instruction |
| Role | AI Software Developer |
| Source baseline | `ca457f784975c2d0959b1baf988483fa042f5c67` (merged PR #1) |
| Scope | `G0-A1 / PC_SIM_ONLY` |
| Allowed source/test write area | `Source/host_virtual_ticks/**` **only** |
| Proposed PR branch | `feature/TASK-002-host-virtual-ticks` |
| Task authority | Existing approved R1/R1.1 tick rules (`115`, `116`, `132`, `141`) and `Design/158` derived interpretation |

## 1. Objective

Build a **small, pure, deterministic virtual tick scheduler** accepting the already-validated immutable `AcceptedPreflight` from TASK-001 and returning an iterable of immutable `VirtualTickBatch` records (`tick_index`, `eval_at_us`, ordered original `events`). Implement only **event eligibility and virtual time enumeration**, not the SafetySupervisor or actual simulator runtime. This is the narrow, separately testable next dependency toward a full PC simulator.

TASK-001 is MERGED into main (PR #1); reuse its library and its accepted scenario result. **Never reimplement the JSON parser or M0 arithmetic**. Developer may propose an internal class/function structure within the output contract from `Design/158`.

## 2. Required reading (exact paths / source pin)

Read from Git snapshot `ca457f784975c2d0959b1baf988483fa042f5c67` and the new TASK-002 release docs, verifying paths/hashes before coding:

| Priority | File | Reason |
|---|---|---|
| 1 | `Design/07_AI_CODING_RULES.md` | Developer boundaries |
| 1 | `Design/10_SA_OPERATING_RULES.md` | SA / developer separation |
| 1 | `Design/11_HANDOFF_PR_WORKFLOW.md` | PR and isolated review |
| 1 | `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` | **Normative** 5ms eligibility and no intermediate dispatch |
| 1 | `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md` | Tick size and PC-only trust boundary |
| 1 | `Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md` | Validated inputs, duration and BOOT |
| 1 | `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` | Approved precedence |
| 1 | `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | Frozen v2 input constraints |
| 1 | `Design/157_TASK001_CLOSEOUT_AND_TASK002_RELEASE_BASELINE.md` | Merge closeout / exact baseline |
| 1 | `Design/158_G0A1_VIRTUAL_TICK_SCHEDULER_CONTRACT_DERIVED_R11.md` | This module's frozen-derived output boundary |
| 1 | `Design/159_TASK002_SCHEDULER_TEST_ORACLES_AND_REVIEW.md` | Acceptance test plan |
| 1 | `Design/fixtures/P214_TICK_BATCH_ORACLE_INDEX.json` | 14 design oracle recipes; **not PASS claims** |
| 2 | `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md` | Understand output cannot publish before trace commit (outside task) |
| 2 | `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py` | `AcceptedPreflight`, immutable scenario, no parser rewrite |
| 2 | `Source/host_preflight_m0/src/bb_host_preflight_m0/__init__.py` | Reusable public imports |
| 2 | `Source/host_preflight_m0/tests/conftest.py` | Existing fixtures/Test integration |
| 2 | `Design/fixtures/P210_MINIMAL_WIRE_V2.json` and `P210_NOMINAL_M0_WIRE_V2.json` | Base input examples |

**Pinned source blob checks:**

```text
Design/115...md                         e6d988d160773219811d28cdb346b5a4590a0fa0
Design/132...md                         2e154c314fbfdcfed8bc6daa00b72cdf349a6ccb
Design/contracts/G0A1_SCENARIO...json  1d10c76e34be70880a65252d89a6bca89839fea9
Source/.../bb_host_preflight_m0/wire.py 506aa23cbe5e01671f3f51c1f2fd64444d7f0578
```

Do not take untracked files or a different `main` as automatically authoritative. If these hashes changed from approved baseline, report `BLOCKED — DESIGN CLARIFICATION`.

## 3. Required behavior

1. Accept only a TASK-001 `AcceptedPreflight` result, produced by preflight of approved v2 bytes; reject direct raw JSON/dict or `RejectedPreflight` with trusted-caller exception; **not** a new `P_*` sidecar.
2. Fixed tick period **5000 microseconds**, `T_k=k*5000`, `k=0..duration_us/5000`, inclusive. Include `T=0`, and include the last scheduled tick at `duration_us`.
3. Tick `0`: exactly events with `event_at_us=0`. For `k>0`: eligible `(T_(k-1), T_k]`. Event at 4999 or 5000 belongs to 5000; event at 5001 belongs to 10000.
4. Yield **one batch every tick, including empty batches**. No timer-driven fabricated control/RF frame, state transition or held intent.
5. Preserve original `event_at_us`, `event_id`, type, payload and array order. Each input event appears once and only once. Do **not** collapse same-tick controls or resolve contradictory RF, RESET, ACK or catastrophe.
6. Batches and event collections read-only. Repeat same accepted input → same ordered batch sequence; no global state/time/RNG/device influence.
7. `O(ticks + events)` single-pass enumeration; no O(ticks×events) event rescans. Prefer lazy streaming; memory scales with active batch only (excluding already validated scenario).
8. No output actuation, no safety state machine, no trace/JCS hash, no host policy allowlist, no endpoint/network, no environment-dependent clock or plugin. The scheduler's existence **never grants runtime execution/ARM permission**.

## 4. Technical and directory constraints

- Create **only** `Source/host_virtual_ticks/**` for runtime, tests, scripts, package instructions and evidence. Read `Source/host_preflight_m0/**` and `Design/**` without editing them. Do not change root files, `Task/`, `ReviewPR/`, firmware or policy/schema.
- Use **Python 3.11+** and standard library for runtime. Reuse TASK-001 via local editable install/read-only dependency; pin/document dependency provenance. A test extra may include pinned pytest. No network or physical IO in runtime.
- Expose a documented pure callable such as `iter_virtual_ticks(accepted: AcceptedPreflight)`, with clear immutable `VirtualTickBatch` fields. Names can differ if the README and tests expose an equally simple stable API.
- Test scripts may use wall clock to measure *test duration*, but runtime scheduler must never sleep or read wall-clock time to decide a tick.
- Do not build a full simulator CLI or UI. If a schema/ABI change is required, **STOP**, report to SA rather than adjusting approved contracts.

## 5. Acceptance criteria (all required)

| ID | Observable check | Required evidence |
|---|---|---|
| AC-01 | Only `Source/host_virtual_ticks/**` written by Developer; no hardware/network/trace/FS writes in runtime. | Git diff + isolation/import scan |
| AC-02 | Exact tick count `duration_us/5000+1` for min/max cases, including empty ticks and T0. | Unit tests T01,T05,T11 |
| AC-03 | Boundary grouping `(prev,T]` with non-grid timestamps and final boundary; original time preserved. | T02,T03,T06 exact IDs/times |
| AC-04 | Full event count and original order preserved exactly once; no same-tick premature conflict/RF/catastrophe resolution. | T04,T07–T10 |
| AC-05 | Scheduler rejects raw dict/`RejectedPreflight` and emits no ticks or new diagnostic on invalid caller. | T12 negative test |
| AC-06 | Caller cannot mutate batches; accepted input remains unchanged; repeated enumerations match. | T13,T14 |
| AC-07 | O(ticks+events) behavior on max-duration and max 20000 input events; no per-tick rescanning or excessive copies. | Instrumented scalability tests (not timings alone) |
| AC-08 | Working API interoperates with merged TASK-001 0.1.0 and **all 14 oracle recipes** are executed with actual expected-versus-observed assertions. | Tests, versions and outputs |
| AC-09 | New package builds/installs/compiles and runs unit, integration, smoke on Windows Python 3.11+; no secrets. | Actual logs and commands |
| AC-10 | UAT instructions for Owner require at most three simple commands; no Developer PR until Owner UAT approval. | README and handoff report |

## 6. Minimum tests / smoke

Implement tests for **all** `P214-T01..T14` and additional max-events complexity case. Use `validate_wire` from TASK-001 to obtain accepted fixtures before scheduling, except the deliberate invalid-caller case. Test negative directly and no side effects. Record actual PASS/FAIL/SKIP; design fixtures are not already-passed runtime evidence.

Developer provides these **three final PowerShell commands** once the module exists, from `Source/host_virtual_ticks` (adjust for actual venv chosen, never omit commands):

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

A lightweight smoke should verify exactly T0 BOOT, at least one interior boundary, an empty tick, max tick-count sanity (if fast), and an invalid-caller rejection. **No hardware**.

## 7. Delivery workflow / cost control

1. Developer reads the task/specs and implements/tests on a private feature branch. No PR yet.
2. Developer returns concise `READY FOR OWNER UAT` plus file list, exact test results and **three runnable commands**. Only send long logs when something fails. No duplicate phase documents or self-written new Design/Task files.
3. Owner runs three commands directly in VS Code, handles Git stage/commit/push of SA-created docs and asks Developer to fix only real failures. Owner sends output if a warning/error arises.
4. **Only after Owner explicitly says “Tạo Pull Request TASK-002”** may Developer open PR; include TASK-002 AC mapping and actual evidence. Do not self-merge.
5. SA review in isolated `ReviewPR/pr-<id>` and advise Owner. Owner alone decides final merge; clean old task/worktree only after confirmed completion.

**Stop condition:** Any demand for ARM/FSM priority, real UART/RF/servo, trace hash, new schema fields, direct execution approval, test waiver, or changes outside allowed subtree ⇒ `BLOCKED — DESIGN CLARIFICATION` to SA. G0-B/G4 flight remain NO-GO.

## 8. Initial tracking

- TASK-001: merged, accepted and closed by `Design/157`.
- TASK-002: issued as an authorized design-derived software task; **implementation NOT STARTED, tests NOT RUN, PR NONE** at release time.
