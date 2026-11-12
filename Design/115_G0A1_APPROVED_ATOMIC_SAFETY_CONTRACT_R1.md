# BionicButterfly — G0-A1 Approved Atomic Safety Contract R1

- **Document ID:** BB-G0A1-NORM-115 | **Revision:** R1 / 1.0 | **Owner decision:** `114` | **Date:** 2026-11-13
- **Normative scope:** **PC_SIM_ONLY.** This document is the controlling specification for host virtual safety semantics; older conflicting `57/58/68/84/100/101/109` clauses are retained as history via `119`.
- **Source baseline:** `3d9a4f28d521190d10579cab48d8b732817892c9`. Physical flight policy in `27` is a separate unvalidated candidate and **is not superseded** for hardware by this file.

## 1. Invariants and single ownership

- Only virtual owner `SIMULATOR` in `PC_SIM`. Scenario payloads, UI, scripts and injected events **cannot** change owner, policy authorization, physical context or sink type. No actual PWM/GPIO/UART/RF/IMU access.
- Virtual output is either a *pair* of integers `left_micro_effort`, `right_micro_effort` in `[0,1000000]`, or the pair `(null,null)`. An authorized `0` differs from inhibited `null`; **micro-effort is not servo pulse µs**.
- Non-null output implies post-state `ACTUATION_ACTIVE`, both independent freshness checks, no active hazard, policy match, and successfully committed trace for that tick. No transient callback may publish a tentative output.
- `AirborneEstimate` is always `UNKNOWN`; observed force, altitude, physical angle and actual flight safety cannot be inferred from virtual effort.

## 2. Virtual clock and deterministic batch

For `step_us=5000`, evaluation `T_k=k·step_us` including `T_0=0`. At k=0, events at time 0 are eligible; for k>0 use `(T_(k-1),T_k]`. Preserve original `event_at_us` for elapsed-time checks (never round it to tick time). Any malformed input, duplicate global `event_id`, wrong context or untrusted policy **rejects the whole scenario preflight**, with **zero core ticks**.

At each tick use exactly this order: (1) immutable pre-snapshot; (2) gather all eligible events; (3) typed validation and normalize the **entire** control and RF batch; (4) evaluate independent health, faults, and state priority once; (5) bound one tentative virtual command; (6) serialize+commit one complete decision record; (7) publish the single post-state/virtual command. Any append/serialization/quota failure aborts without publishing the new output, yields `FAILED_INCOMPLETE_EVIDENCE`, and cannot PASS a normal-success oracle.

Two valid equivalent control payloads in one tick with different unique IDs count once; preserve sorted original IDs and use latest original timestamp for accepted-frame age. Two valid **different** payloads yield `E_CONTROL_BATCH_CONFLICT`: ignore all control observations this tick, do not refresh timestamp or qualify LOW/HIGH. An in-band typed `uart_frame_status=INVALID` yields `E_FRAME_INVALID`, invalidates LOW window, cannot refresh and prevents a simultaneous valid control body from granting arm/disarm/demand. Contradictory RF HEALTHY/LOST in one tick resolves LOST; a later separate HEALTHY tick can change observed RF state but never auto-arm.

## 3. State machine and authority

States: `BOOT`, `SELF_TEST`, `DISARMED`, `ARM_CHECK`, `ARMED_IDLE`, `ACTUATION_ACTIVE`, `CONTINGENCY`, `FAULT_LATCHED`. Do **not** use `GROUND_ARMED` to imply ground detection; that term belongs to historical/physical context in `27`. FSM is pure virtual state in PC-only slice.

| Pre-state / event | Preconditions | Next | Output |
|---|---|---|---|
| BOOT at T0 | mandatory BOOT | SELF_TEST | null |
| SELF_TEST at later tick | approved policy and no power/scheduler critical | DISARMED; RF UNKNOWN permitted | null |
| SELF_TEST critical power/scheduler | unresolved critical cause | SELF_TEST | null |
| DISARMED: first valid LOW | coherent healthy RF + accepted frame | DISARMED; start LOW sample | null |
| DISARMED: second LOW | later tick; original timestamp separation ≥20,000µs; uninterrupted | DISARMED; LOW qualified at commit | null |
| DISARMED: HIGH edge | qualified LOW from **prior committed tick**; neutral and fresh RF/frame | ARM_CHECK | null |
| ARM_CHECK: confirming HIGH | later tick, original timestamp separation ≥100,000µs, neutral and continuously healthy | ARMED_IDLE | null |
| ARMED_IDLE: later HIGH demand | new accepted frame with `flap_demand>0.05`, all guards | ACTUATION_ACTIVE | bounded pair |
| ACTIVE: accepted valid HIGH demand | healthy and coherent | ACTIVE | bounded pair |
| ACTIVE: no new frame | S1 with most recent authorized input and both freshness gates still valid | ACTIVE; no timestamp update | last bounded intent |
| ACTIVE/IDLE: coherent accepted LOW | healthy, no higher hazard | DISARMED; old LOW not counted as new first LOW | null |
| ARM_CHECK/IDLE/ACTIVE: invalid batch, RF lost/stale or other critical cause | even with RESET | CONTINGENCY (or latch for catastrophe) | null |
| CONTINGENCY: fault recovery | approved recoverable reasons, all causes cleared; prior committed LOW qualification; separate ACK | DISARMED; clear qualification/arm edge | null |
| FAULT_LATCHED: any RESET/ACK/health change | no in-run clear | FAULT_LATCHED | null |

## 4. Priority and edge cases

1. Catastrophic fault in current batch ⇒ `FAULT_LATCHED`; includes catastrophic + RESET + LOW + ACK same tick. A prior `FAULT_LATCHED` persists for entire run.
2. In `ARM_CHECK`, `ARMED_IDLE`, `ACTUATION_ACTIVE`, active RF LOST/UNKNOWN/stale, critical power/scheduler or invalid/contradictory control batch ⇒ `CONTINGENCY`; **ordinary RESET cannot bypass the active hazard**.
3. In `CONTINGENCY`, remain there until a qualified ACK or catastrophe; RESET cannot clear it and **RESET in the same tick blocks ACK/LOW qualification**. Any unresolved non-allowlisted cause bars recovery.
4. Else ordinary RESET ⇒ `SELF_TEST`, clear low/high/arm/held intent; a control frame in that same tick cannot arm, qualify LOW, or refresh accepted intent.
5. Else coherent accepted LOW (with healthy guards) revokes virtual active command and moves to DISARMED, or starts/advances LOW window when already DISARMED/CONTINGENCY; a HIGH **in the same tick** cannot be processed as a separate arm edge.
6. Else ACK in CONTINGENCY can clear only on **previous-tick** committed LOW-qualification and restored health, approved cause list, no active/reset fault. It consumes LOW qualification; a fresh two-LOW series is required to arm anew.
7. Else eligible HIGH edge/confirmation/demand, each requiring a distinct accepted frame/tick. No new control frame or a timer tick alone completes ARM_CHECK.
8. Else retain current state while all guards remain valid. Denied config/UI writes cannot mutate safety state but must be reported; a critical fault still takes precedence.

A qualifying LOW series is broken by accepted HIGH, RESET, RF nonhealthy, expired frame health, critical simulated power, in-band INVALID frame, semantic conflict, policy/map mismatch or authority violation. Empty ticks preserve a window only while all health remains fresh; they **do not** count as a second LOW or HIGH. At exact boundary ages `<=200,000µs` are fresh, strictly greater are stale. An accepted frame timestamp is distinct from raw UART diagnostic timestamp; UART-valid data with RF LOST never renews pilot authority.

## 5. Approved SIM-only recovery allowlist

`E_RF_NOT_HEALTHY`, `E_FRAME_STALE`, `E_CONTROL_BATCH_CONFLICT`, `E_FRAME_INVALID`, and `VOLTAGE_WARNING_RECOVERABLE` (noncritical, proven recovered simulated voltage warning) are eligible *causes* for ACK **only after all observed health is restored**. An explicitly emitted `SIM_CATASTROPHIC_FAULT`, `E_NUMERIC_INVALID`, a scheduler stall, generic `E_SIM_FAULT` with unknown subtype, unresolved critical supply or evidence-append failure is **not** ACK-clearable in-run.

`VOLTAGE_WARNING_RECOVERABLE` is a **reason/category enum**, not permission for the Developer to invent a new scenario v1 event. A voltage recovery test requiring an event not already in v1 must be **DEFERRED** and returned to SA as a schema revision request. Semantically equivalent valid distinct-ID ACK events in one tick count as one logical ACK; repeating the same global ID is preflight-invalid. ACK and the last LOW of qualification in the same tick cannot recover by snapshot ordering.

## 6. Observability and version impact

`P28` clarification: any noncritical warning event whose v1 wire representation is not fully defined must NOT be converted into a fabricated critical/healthy signal. The core rejects unsupported v1 inputs. Only owner-approved R2 may expand event types.

Refer to `117` for input v1/result-errors v2, `116` for exact frozen SIM numbers and independent approval, `118` for trace output, and `120` for negative/boundary oracle mapping. This is **approved design text**, not proof that software is implemented or passes tests. Real-airborne policy remains unresolved.
