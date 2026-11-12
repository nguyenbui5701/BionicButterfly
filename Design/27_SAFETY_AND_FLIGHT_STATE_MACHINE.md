# BionicButterfly — V1 Safety State Machine & Contingency Policy

- **Document ID:** BB-SAFE-027 | **Version:** 0.1 | **Date:** 2026-11-12
- **Status:** PROPOSED — bench/airborne policies **NOT VALIDATED**, no flight authorization.
- **Purpose:** resolve `INT-01/05/08`; normative candidate for firmware safety reviews, not evidence of a safe aircraft.

## 1. Distinct concepts (must not be collapsed)

- **SystemState:** `BOOT`, `SELF_TEST`, `DISARMED`, `ARM_CHECK`, `GROUND_ARMED`, `ACTUATION_ACTIVE`, `CONTINGENCY`, `FAULT_LATCHED`.
- **OperationContext:** `PC_SIM`, `BENCH_SERVO_ONLY`, `RESTRAINED_AIRFRAME`, `FLIGHT_TEST_APPROVED`. This is an **explicit test configuration/authorization**, not a motion sensor.
- **AirborneEstimate:** `UNKNOWN` by default. Until an independently validated sensor/observer exists, software **must not infer actual flight** from throttle, RPM or servo PWM. UI must label uncertainty.
- **Authority:** `NONE`, `RC_PRIMARY`, `BENCH_LOCAL`, `SIMULATOR`; flight-test context permits RC only.
- **FaultCategory:** `WARNING`, `GROUND_INTERLOCK`, `FLIGHT_CONTINGENCY_REQUIRED`, `HARDWARE_DANGER`. A category is not an automatic physical response.

## 2. State transitions — events, guards and authoritative effects

| Current | Event | Guard / accepted evidence | Next | Effect |
|---|---|---|---|---|
| BOOT | MCU initialized | none | SELF_TEST | physical output held inhibited if hardware permits; record reset cause |
| SELF_TEST | all mandatory checks passed | valid immutable config, output startup trace, safe rails, no critical fault | DISARMED | no automatic arm |
| SELF_TEST | bad config, sensor or actuator fault | any blocking fault | FAULT_LATCHED | deny bench output; inform owner |
| DISARMED | explicit ARM switch edge | **fresh validated** RC or authorized bench owner; neutral throttle; voltage/limits healthy; approved context | ARM_CHECK | snapshot arming prerequisites, never arm based only on held switch level after reboot |
| ARM_CHECK | guard stable over defined qualification window | window TBD by testing; no stale frame, faults or source switch | GROUND_ARMED | enable only envelope-approved idle behavior |
| ARM_CHECK | timeout/mismatch/arm switch removed | any | DISARMED | reject and log reason |
| GROUND_ARMED | pilot command above qualified activation boundary | owned validated input; physical conditions approved | ACTUATION_ACTIVE | compute planned bounded wing motion |
| ACTUATION_ACTIVE | pilot demand reduces to idle | valid owner + agreed motion law | GROUND_ARMED | **name does not prove plane is on ground**; do not invoke an unvalidated airborne stop |
| any armed | link unhealthy, critical battery, actuator/scheduler fault | state and context-specific severity | CONTINGENCY | select **only a measured, approved** plan for this airframe/context; otherwise G4 NOT ALLOWED |
| BOOT/DISARMED/ARMED/ACTIVE | disarm/E-stop intention | always highest *command priority* | context-specific guarded state | ground/bench: verified stop; flight: policy must be airframe-specific; do not assert lift cut is safe |
| any | hardware danger (short/thermal/runaway) | hardware measurement/interlock | FAULT_LATCHED | hazard-specific emergency action, may trade flight safety against fire/physical injury; subject to hardware design |
| CONTINGENCY/FAULT_LATCHED | link restored/voltage recovers | health alone **insufficient** | unchanged | no automatic resumption |
| CONTINGENCY/FAULT_LATCHED | explicit reset / acknowledgment | disarmed, healthy, authorized and qualified | DISARMED | pilot re-arms deliberately; do not transition straight to ACTIVE |

`GROUND_ARMED` is a historical label inherited from project drafts. It means **armed idle** and is *not* proof the aircraft is on the ground. Future implementation should prefer `ARMED_IDLE` if owner approves renaming before code freeze.

## 3. Safety policy matrix

| Condition | PC_SIM | G2 servo-only bench | G3 restrained wings | G4 flight (UNAPPROVED) |
|---|---|---|---|---|
| BOOT/invalid config | output disabled | prevalidated hardware inhibit | prevalidated hardware inhibit | must pass hardware startup signoff |
| Arm with non-neutral throttle | deny | deny | deny | deny |
| Malformed/old RF data | reject, age source correctly | reject + test fault | reject + test fault | qualification and contingency needed |
| Radio loss | simulate bench fault | verified ground-safe stop | rig hazard/stop plan | **TBD**: cannot assume instant wing cut, hold-last, or fixed flap is safe |
| Low/critical battery | inject warning/fault | measured threshold and bench stop | sag/overload response | **TBD**: energy reserve, glide/recovery evidence needed |
| Explicit disarm/E-stop | test command priority | validated hardware-safe termination | approved rig-safe response | **TBD**: pilot emergency maneuver and catastrophic-hardware protections must be assessed separately |
| Return of valid frames | no auto-arm | no auto-arm | no auto-arm | no uncontrolled auto-restart; flight-specific recovery to be reviewed |
| UI/Web config change while armed | reject | reject | reject | reject |

**No G4 output policy is supplied as ready-to-flash defaults.** Before owner approval the design must give a tested exact action, trigger, timeout, threshold, and evidence for each contingency. Generic `failsafe = servos off` is unacceptable.

## 4. Truth and freshness checks

- **Local monotonic timestamp** set on receipt of a *fully verified* RC control frame; not user/network timestamps, not number of edges, not UART bytes. Track separate `last_valid_frame_at`, `last_rf_health_at`, `last_pilot_intent_at` if each is available.
- **RF health state is independent:** `HEALTHY`, `LOST`, `UNKNOWN`. If receiver reports frozen channels but sends serial frames, do not treat serial frame freshness as confirmed pilot intent. Validate exact selected RX firmware behavior with controlled RF disconnect.
- **CRSF RC frame sequence:** do **not** assume one. If no counter, derive event ordering locally and use age + status + independent receiver failsafe information. Sequence anti-replay applies only to paths that actually carry authenticated counters.
- **Unknown failsafe state blocks arm**. In-flight response to transition to UNKNOWN cannot be specified without physical test; this remains a G4 blocker.
- **Timeout:** 500 ms in existing simulator is **not** approved for flight. Timeouts must be linked to measured update period, receiver firmware, maximum transient frame loss and authorized contingency evidence.
- **Time wrap and resets:** evaluate elapsed time via monotonic-safe arithmetic, verify wrap/reboot; a reboot revokes arm authority and must not produce uncontrolled servo pulses.

## 5. Decision table for competing requests

Priority in *logical decisions*: catastrophic hardware fault (specific policy) / explicit disarm intent / safety supervisor fault > valid armed RC command > bench-calibration request > UI effects. **Priority is not equivalent to physically removing actuator power.** When armed for flight, non-RC sources cannot acquire ownership or rewrite configuration; stale packets cannot change arm status. No remote web E-stop is claimed to be a flight-safety channel.

## 6. Invariants and test requirements

- INV-S01: `state != ACTUATION_ACTIVE` shall not cause *unapproved* wing motion.
- INV-S02: `ARM_CHECK` requires deliberate pilot switch transition following boot; held ARM on power-up must not arm.
- INV-S03: `DISARMED` + fault recovery never transitions straight to flapping.
- INV-S04: malformed/stale/unowned command never changes physical setpoints or resets valid-frame age.
- INV-S05: all actuator commands pass bounds and slew limits from a **measured** airframe profile.
- INV-S06: config writes are rejected atomically when armed; firmware refuses unsupported profiles.
- INV-S07: all faults/contingencies carry event reason, timestamps, operation context, source and build/config identifiers.
- INV-S08: no flight contingency is enabled merely because ground bench tests passed.

**Proposed integration tests:** `IT-01` arm held at boot and reset; `IT-02` serial frames present while RF link absent; `IT-03` stale/fault overlap with UI; `IT-04` alternate simulated clocks and wrap; `IT-05` reject in-flight config writes; `IT-06` airframe-specific contingency evidence review (G3/G4). See `29`.

## 7. Unresolved approvals

Pilot control switch semantics, chosen receiver's RF-loss reporting, ground vs flight hardware emergency policy, arm qualification interval, allowable link-gap latency, physical stop distances, and reboot behavior require exact hardware + tests and signed approval before flight. Zero of these are assumed passed.

## 8. Human RC interaction and radio-level arming (v0.2 — PROPOSED)

The `ARM_INTENT` physical switch is a deliberate **vehicle** arming request; ELRS RF armed mode is a separate radio-layer state. **Neither authorizes output without supervisor guards.** After boot, MCU reset, transmitter model switch or lost-link recovery, a held HIGH is insufficient; the MCU must first observe DISARMED LOW and then a new valid LOW→HIGH edge and qualification. The mapping/version must match `32` and the active profile `33`. Wrong CH assignment, invalid rate code, stale serial or UNKNOWN RF health blocks **new ARM**. Armed profile/rate editing remains disabled before G4 qualification.

`ARMED_IDLE` should replace legacy `GROUND_ARMED` in future code freeze; it is not an airborne sensor. Explicit disarm has highest logical priority, but physical reaction during free flight remains **UNQUALIFIED**: do not map it to a blind power cut. See `34–36`, PX-01/04/07/08/16/20. No flight-test policy activated by this document.
