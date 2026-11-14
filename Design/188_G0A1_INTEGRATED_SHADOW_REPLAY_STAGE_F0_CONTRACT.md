# Stage F0 — Integrated PC Shadow Replay & Pilot-Input/Wing Preview

- ID **BB-P224-188**; baseline `ccb6babea26be805f752b80488a7232eff70aa06`; version F0.1; **PC_SIM_ONLY / TEST_ONLY / NO_OUTPUT**.
- Priority: deliver a genuinely runnable integrated G1 diagnostic demo, not a twelfth isolated checker. R1/1.1 contracts `115–118`, `132`, `134`, `141` remain normative; F0 is NOT a replacement for the full FSM, trusted runtime or canonical R1 trace.
- No new public R1 `E_*`/`P_*`, no real RC/UART, BLE/Wi-Fi, PWM/GPIO/servo, firmware, F4 flight or positive `PASS/ADMITTED`/execution authority.

## 1. Product the Owner can run

A deterministic **offline PC command-line demo** with test-provided wire-v2 scenario, frozen schema, policy bytes, E2 TEST_ONLY claim, E3 TEST_ONLY manifest + synthetic artifact bytes. It prints a legible timeline:

```text
T(ms)  RF evidence   Control candidate  E1 snapshot   Preview L/R (math only)  Output
0      MISSING       NONE               SELF_TEST     --                       INHIBITED
5      HEALTHY*      flap .40 steer .20 SELF_TEST     200000 / 600000          INHIBITED
10     LOST          ...                SELF_TEST     --                       INHIBITED
...    ...           ...                FAULT_LATCHED --                       INHIBITED
```

`HEALTHY*` means **observed but NOT committed/authorized**. `preview L/R` is arithmetic for illustration, never a physical PWM pulse, R1 `output_allowed` or an authorized virtual command. ARM switch may be printed as `REQUESTED_NOT_GRANTED`. There is **no animation callback/servo adapter**; printing preview is offline explanatory reporting only.

### 1.1 One integrated pipeline (real imported libraries; no mocks in positive integration)

```text
Scenario wire-v2 raw bytes ── TASK-001 genuine preflight ──┐
                                                            ├─ TASK-010 E2 reference check
Frozen policy raw bytes ────────────────────────────────────┤
TEST_ONLY synthetic E2 host claim ──────────────────────────┘
                                                            ↓
TEST_ONLY 16-field manifest + synthetic engine/scheduler ─ TASK-011 E3 intent
                                                            ↓
                   E2 matches TEST_ONLY reference AND E3 content-consistent?
                            │ no -> zero SHADOW ticks, blocked report
                            │ yes -> shadow diagnostic lane only (no operational authority)
                            ↓
 TASK-002 scheduler → TASK-003 normalized observation → TASK-004 temporal facts
                   → TASK-005 provisional priority → TASK-007 RF/control evidence
                   → TASK-008 diagnostic triage → TASK-009 E1 TEST_ONLY ledger
                            ↓
    offline shadow timeline + optional separately labeled M0 mathematical preview
                            ↓
              NO R1 trace/digest, NO authorized output, NO hardware
```

Never feed E2 `TEST_ONLY` revisions as E3 revisions: E2 and E3 have different intentionally synthetic reference strings. Use frozen **P222** E2 claim and **P223** E3 manifest/artifact fixtures in the CLI/test harness. Do not read user scenario and extract a host claim or manifest from its JSON. The pure runner takes all inputs separately; CLI loads Design fixtures read-only. Bad preflight -> E2 UPSTREAM_REJECTED, E3 UPSTREAM_NOT_ELIGIBLE; zero shadow ticks. E2 mismatch -> E3 UPSTREAM_NOT_ELIGIBLE; zero shadow ticks. E3 mismatch/malformed -> zero shadow ticks. An E3 positive is `INTENT_CONSISTENT_UNPROVISIONED` and **allows diagnostic observation only**.

## 2. Python API / exact authority constraints

Package `bb-host-integrated-shadow-replay` version `0.1.0` under `Source/host_integrated_shadow_replay/**`, Python >= 3.11. Public entry points:

```python
run_shadow_replay(
    scenario_raw: bytes,
    frozen_wire_v2_schema: dict,
    policy_raw: bytes,
    claimed_host: ClaimedHostFingerprint,
    intent_raw: bytes,
    engine_artifact: bytes,
    scheduler_artifact: bytes,
) -> ShadowReplayReport
```

- The `frozen_wire_v2_schema` is the **exact** TASK-001 schema; TASK-001 checks its fingerprint. The CLI may read it from Design; the pure runner performs no file or OS/env/network access.
- Only call imported genuine upstream APIs in documented order and use their immutable outputs, no copy/paste logic or new authority predicate. Never instantiate synthetic `AcceptedPreflight` or synthetic committed state to make positives pass. No untrusted receipt, callback, arbitrary initial snapshot, `is_authorized` flag, output sink, input plugin or serial adapter parameter.
- `ShadowReplayReport` (frozen/slotted) must expose `outcome`, `preflight_status`, `e2_outcome`, `e3_outcome`, `shadow_ticks`, `shadow_tick_count`, `blocked_at_tick`, `runtime_authorized=False`, `requires_full_fsm=True`, `actual_virtual_output=None`, `physical_output=None`, `canonical_control_trace_sha256=None`. `shadow_ticks` is a tuple of immutable `ShadowTick` summaries; cap at exactly `duration_us//5000+1` (max 12001). Tests assert exact field sets and types. No R1 run_status `COMPLETED` in this report.
- Closed `ShadowReplayOutcome`: `INPUT_REJECTED`, `REFERENCE_OR_INTENT_BLOCKED`, `SHADOW_DIAGNOSTICS_COMPLETE`, `BLOCKED_NEEDS_FULL_FSM`, `SHADOW_EVIDENCE_INCOMPLETE`. `INPUT_REJECTED` does **not** mean a successful R1 execution; shadow complete does **not** imply FSM complete.
- Each `ShadowTick` (frozen/slotted): `tick_index`, `eval_at_us`, `causal_event_ids`, `pre_state`, `test_state_after`, `rf_evidence`, `control_evidence`, `triage_reasons`, `e1_outcome`, `arm_switch_requested`, `preview_left_micro`, `preview_right_micro`, `preview_clip_tags`, `runtime_authorized=False`, `actual_virtual_output=None`, `physical_output=None`. No `output_allowed=True` or physical servo units anywhere. 
- `test_state_after` comes only from the E1 **acknowledged** snapshot, not C1 provisional next-state. For DEFER or missing ack, retain prior snapshot as the only observed prior and terminate with blocking result. E1 journal bytes stay test-only and must not become Design/118 canonical control trace or complete report SHA.

## 3. Exact per-tick history bridge (hard requirement)

1. Instantiate exactly one `TestOnlySnapshotLedger()` from BOOT genesis **inside** runner. Do not call private test seeding or forge any `OwnerSnapshot`.
2. For each `VirtualTickBatch` in TASK-002: read `prior = ledger.snapshot` once; form TASK-004 `PriorCommittedTimestampFacts(prior.last_eval_at_us, prior.last_accepted_control_at_us, prior.last_uncontested_healthy_rf_at_us)` and TASK-007 `PriorCommittedRFStatus(prior.last_eval_at_us, prior.last_rf_status, prior.last_rf_original_at_us)`; `priority.pre_state = prior.state`.
3. Compute TASK-003, TASK-004, TASK-005, TASK-007, TASK-008 with genuine typed outputs. Call E1 `commit_tick(...)` **once only** on each eligible chronological tick. Do not call TASK-006 hypothetical PASS/ADMITTED or repeat old event batches.
4. E1 COMMITTED_TEST_ONLY -> record snapshot state and continue; E1 DEFERRED_NEEDS_FULL_FSM -> stop at that tick; E1 FAILED_INCOMPLETE_EVIDENCE -> stop, no tentative preview/report row from failed tick, sticky failure not retried; never mark scenario R1 PASS or complete R1 trace.
5. Ensure committed prior RF/control historical timestamps remain unchanged in E1; do not self-promote current observations into prior accepted history. `SELF_TEST` hold is expected and explicitly shown as **UNRESOLVED_FULL_FSM**; do not falsely move into DISARMED/ARMED/ACTIVE.
6. For long scenarios record up to 12001 summaries, O(events + ticks), bounded memory and diagnostic JSONL quota; no per-tick full history copy. If unexpected typed-boundary mismatch occurs, surface a TEST_ONLY integration error and stop with no output; do not silently coerce an exception into successful demo.

## 4. Mathematical wing-intent preview — separate from output authority

- A preview is **optional** and **only** shown when current tick has exactly one genuine valid control group, no INVALID/conflict, exactly uncontested `HEALTHY_CURRENT` RF evidence, no reset/catastrophe, priority not blocking, triage control lane `UNTRUSTED_CANDIDATE` and E1 has acknowledged this tick. If any condition missing, pair must be `(None, None)` and tags empty. Do not preview from carried/uncommitted unknown RF or stale history.
- Convert TASK-001 validated `int | decimal.Decimal` numeric demands to exact integer micro units (multiply exactly by 1,000,000, no binary float). Call **TASK-001 `mix_m0(flap_micro, steer_micro)`**. Output goes into `preview_*` **only**, with label `MATH_PREVIEW_UNTRUSTED`, never into `OwnerSnapshot`, E1 journal, normative trace, output_allowed, callback or drivers. Never change `no output` merely because preview exists.
- Print `arm_switch_requested` as observed boolean request, **NOT** state transition/approval. Test cases MUST show arm HIGH while state stays `SELF_TEST`, and RF LOST suppresses preview.
- If the full condition set conflicts with behavior of frozen D2/C1 gates, **omit preview and file SA clarification**; do not edit upstream or relax gate. No preview may imply servo position, PWM pulse width, flap Hz or measured force.

## 5. Reporting: honest offline diagnostics, not R1 trace

- CLI `python scripts/demo.py --case pilot|hazard|conflict|minimal` reads ONLY the pinned Design files, prints summary/timeline to console and optionally saves `--jsonl <path>` **OFFLINE**, marked `BB_F0_SHADOW_DIAGNOSTIC_V1`. Its file IO is a CLI adapter, not pure runtime; no user-supplied executable/plugin, network path, serial device or dynamic import.
- Every JSONL record has `diagnostic_record_type='shadow_header'|'shadow_tick'|'shadow_terminal'` (not R1 `record_type`), `authority='NONE'`, `physical_output=null`, `actual_virtual_output=null`. Use stable ASCII diagnostic serialization with LF (not claimed general JCS), bounded output <=16 MiB. A failed write leaves no falsely successful file; use temporary file+atomic replace or a write-failure flag and cleanup. Only successful full offline report may carry test-only `shadow_report_sha256` in separate CLI metadata, **never** `control_trace_sha256`.
- Default 4 demo presets exercise real BOOT, frame demand, STEER, ARM request denial, RF LOST, INVALID/conflict, RESET and catastrophe. Where event schema only has six event types, do NOT invent a hardware PWM/RC event or a new wire-v2 field. Raw scenario JSON and approval/manifest live in **separate files**.
- UI may be terminal ASCII/Unicode, not an interactive hardware controller. `run_shadow_replay` must NOT open/exec/import files from scenario-provided paths.

## 6. Explicit exclusions and truthful milestone

Stage F0 is the **first runnable, multi-module integrated observation/demo**, NOT G1 full FSM completion. It cannot pass tests claiming `ACTUATION_ACTIVE`, qualified arming, accepted health timestamps, R1 canonical trace or authorized virtual/physical outputs. Do not replace frozen E1/E2/E3 with naive `if manifest matches: allow output`. No generated PWM, CH-to-servo physical mapping, real ESC/servo, RF receiver, firmware, flight. The NEXT milestone after F0 is a separately owner-approved full R1 FSM + canonical control trace/virtual-only publish, and concurrently G0-B schematic/BOM/bench approval; do not create more standalone trust check tasks.
