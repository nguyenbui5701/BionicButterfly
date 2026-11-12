# BionicButterfly — Phase 2.1 Deterministic Safety FSM Semantics

> **Phase 2.4 review note (2026-11-12):** See the candidate corrective addendum at the end and `84–90` before treating older priority/approval text as normative. **Pending owner approval; not code or flight authorization.**

- **ID:** BB-G0A-FSM-058 · **Rev:** 0.2 · **Date:** 2026-11-12
- **Status:** PROPOSED, SIM_ONLY; does **not** implement/authorize in-air failsafe.
- **Baseline:** conceptual FSM `27` and host-only interface `51`. This document disambiguates **host simulation** transitions, not hardware stop behavior.

## 1. State and context model

`BOOT → SELF_TEST → DISARMED → ARM_CHECK → ARMED_IDLE → ACTUATION_ACTIVE`; exceptions use `CONTINGENCY` or `FAULT_LATCHED`.

- `ARMED_IDLE`: authorization state only; not evidence aircraft rests on ground.
- `ACTUATION_ACTIVE`: virtual wing output requested; **not physical IN_FLIGHT**.
- `CONTINGENCY`: host-only logical response to a simulated safety event; **no physical PWM action specified**.
- `context=PC_SIM` is compile/composition-locked; any scenario requesting actual flight context is rejected before run.
- `owner=SIMULATOR` is injected scenario authority, **never** proof a real radio is healthy. Status `rf_health=HEALTHY` is explicitly **simulated**.

## 2. Canonical arming protocol

1. Every run starts with `arm_edge_eligible=false`, `arm_switch_seen_low=false`, `last_valid_control_frame_at=null`, `motion_allowed=false`.
2. After SELF_TEST passes and a valid SIM owner/map/config exists, a **separate accepted control frame** with `arm_switch=false`, `flap_demand` inside configured neutral window and healthy simulated RF may establish `arm_switch_seen_low=true`.
3. Only a subsequent distinct accepted frame with `arm_switch=true` creates a valid low→high edge. A continuous/high-after-boot value does not create an edge. An arm switch bounce is filtered by a configured SIM_ONLY qualification rule (value TBD by approval).
4. On that edge, enter ARM_CHECK iff no active warning classified as blocking, no config mismatch, flap neutral, steer within applicable arm-neutral rule, and input fresh. State and reason logged.
5. When the **approval-defined** qualifying interval and healthy frame expectations are satisfied, transition to ARMED_IDLE. If the guard fails, return to DISARMED and require a fresh valid low→high edge; never keep a stale pending arm request.
6. Only then can a *subsequent* accepted flap request allow ACTUATION_ACTIVE and produce virtual normalized L/R output. A same-tick arm edge and high throttle must not activate motion.
7. After fault/lost link/reset, restoring healthy frames does not reactivate. Disarmed acknowledgement, observed low and deliberate fresh edge are required before resumption.

**Unresolved before freeze:** exact `arm_qualification_us`, neutral window, debounce/recent-frame criteria and whether arm-switch LOW is sufficient acknowledgment after a simulated contingency. They must be resolved as SIM_ONLY values *prior to the G0-A1 owner approval*. No real-flight threshold can be inferred.

## 3. Deterministic transition/priority table (host-only)

| Current | Event/condition | State after atomic tick | Virtual output | Required trace |
|---|---|---|---|---|
| BOOT | initialized | SELF_TEST | disabled | boot and policy revision |
| SELF_TEST | valid SIM config | DISARMED | disabled | self-test accepted |
| SELF_TEST | invalid policy/config | FAULT_LATCHED | disabled | `E_PROFILE_INVALID` |
| DISARMED | held ARM high / unknown RF | DISARMED | disabled | `E_ARM_EDGE_ABSENT` / `E_RF_NOT_HEALTHY` |
| DISARMED | validated low→high and all guards | ARM_CHECK | disabled | guard snapshot |
| ARM_CHECK | stable qualification passed | ARMED_IDLE | disabled | qualified |
| ARM_CHECK | invalid/expired frame, reversed switch or fault | DISARMED or FAULT_LATCHED (per typed severity) | disabled | source and reason |
| ARMED_IDLE | subsequent accepted `flap_demand > active_threshold` | ACTUATION_ACTIVE | bounded, virtual | intent and envelope |
| ACTUATION_ACTIVE | accepted neutral demand | ARMED_IDLE | disabled/idle as simulated contract | motion transition reason |
| any armed | RF LOST/UNKNOWN, stale input, injected critical battery | CONTINGENCY | host virtual sink inhibited | injected source and fault; **no real in-air instruction** |
| any | injected catastrophic/invalid output fault | FAULT_LATCHED | disabled | latched fault code |
| CONTINGENCY / FAULT_LATCHED | RF healthy again alone | unchanged | disabled | recovery interlock |
| CONTINGENCY / FAULT_LATCHED | explicit safe reset + observed low + healthy guards | DISARMED | disabled | acknowledgment, no autoarm |

**Priority ordering within one atomic evaluation:** `BOOT/RESET` > `CRITICAL HARDWARE SIM FAULT` > `EXPLICIT DISARM` > `RF/INPUT/POWER FAULT` > `CONFIG/PROFILE DENIAL` > `ARM QUALIFICATION` > `NORMAL DEMAND`. A disarm action is logically dominant, but the *physical* emergency response is **not specified**. If contradictory same-owner frames arrive at identical timestamps, report conflict, deny motion and leave the old virtual output **inhibited** for that atomic step.

## 4. Input temporal properties

- Only fully validated `SIM_CONTROL_FRAME` advances `last_valid_control_frame_at`; metadata or `SIM_RF_STATUS` updates `last_rf_health_at` independently and cannot revive a stale pilot command.
- Simulator `ARM` qualification requires both independent **current injected RF health** and current validated control-frame freshness (plus config). `UNKNOWN` never means healthy.
- A host-only RF-loss event while active triggers the simulated contingency/inhibit policy by design. This is an artifact of the **virtual sink** and shall **never** be copied as servo-power-off hardware policy.
- Multiple events at one timestamp are *batched*; the scheduler must evaluate one safety decision after normalizing the whole batch, not expose intermediate actuations based on parse order.
- If a later event timestamp is lower than the latest committed virtual time, the scenario is rejected; seek/rewind is a new run, not stateful backward time.
- Recovery requires a fresh switch sequence, not merely a timeout expiration or stable high level.

## 5. Safety invariant proof obligations

| Invariant | Host-only required property | Related PC-A cases |
|---|---|---|
| FSM-01 | from BOOT/RESET no enabled virtual output without full arm protocol | PC-A01/02/04 |
| FSM-02 | duplicate high state alone never generates two arm edges | PC-A01/04 |
| FSM-03 | invalid or stale input does not refresh control age, alter output or source ownership | PC-A06/09 |
| FSM-04 | RF LOST/UNKNOWN blocks new arm even with fresh serial frames | PC-A07/08/17 |
| FSM-05 | non-finite, over-bound or unknown profile prevents enabled motion | PC-A10/11 |
| FSM-06 | disarm/fault priority is independent of same-timestamp input presentation order | PC-A18 |
| FSM-07 | config writes attempted while armed are denied without modifying active config | PC-A12/13 |
| FSM-08 | fault recovery and link restoration never auto-arm | PC-A17/18 |
| FSM-09 | actual airborne/wing angle/force measurements stay unknown | PC-A19/20 |

## 6. Important non-proofs

This FSM can prove **logical** authorization and deterministic virtual output. It cannot prove physical GPIO boot levels, receiver RF health, servo tracking, lift, flight control, hardware disarm safety or airborne recovery. Those remain G0-B/G2/G3/G4 obligations under `14`, `25`, `31`, `40`, `49`.

## Phase 2.4 FSM candidate precedence addendum (rev 0.2)

This earlier design is preserved historically. **Candidate authoritative semantics**, pending owner approval, are in `84_G0A1_NORMATIVE_SAFETY_AND_EVENT_SEMANTICS.md`: control conflict classification precedes any LOW/HIGH acceptance, same-tick catastrophic fault dominates RESET, and ACK requires a previously committed low-qualified snapshot. No real flight policy is specified. Existing G1 test cases remain NOT RUN.
