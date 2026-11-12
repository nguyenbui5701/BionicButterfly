# Bionic Butterfly — Electrical Bench Verification (G0–G3)

- **ID:** BB-EE-TEST-024 · **Version:** 0.1 · **Date:** 2026-11-12
- **Status:** PLANNED / NONE EXECUTED · **Owner:** SA
- **References:** `14_V1_VERIFICATION_PLAN.md`, `18_MECHANICAL_EXPERIMENT_PLAN.md`, `22_ELECTRICAL_POWER_ARCHITECTURE.md`, `23_PINOUT_AND_SIGNAL_CONTRACT.md`, `25_ELECTRICAL_HAZARD_REVIEW.md`.

## 1. Instruments and preconditions

Prepare at minimum a current-limited bench supply, DMM, accurate scale, inspection light, thermal measurement, and a means to measure PWM and voltage transients (oscilloscope preferred). Arrange an insulated battery work surface, approved 2S balance charger and fire-safety practices appropriate to LiPo. Test RX and servo electronics **first without wings**. A personal flight battery should not be used for the first power-up of an unverified circuit; a current-limited laboratory supply is preferred.

**Important:** Even a current-limited power supply does not replace mechanical protection. Test only after a qualified person verifies regulator polarity, rated voltage and connectors. Keep people clear of the travel path. The test checklist is a design plan, **not an instruction to energize unreviewed hardware**.

## 2. Traceable tests (requirements for future acceptance)

| ID / gate | Stimulus or procedure | Evidence required | Proposed pass condition / stop criterion | Status |
|---|---|---|---|---|
| EE-T01 / G0 | Verify exact product datasheet + board/revision | Part inventory / pinout map | No conflicting voltage/interface information | NOT RUN |
| EE-T02 / G0 | Trace 2S, regulators, power path, polarity and USB | Reviewed schematic / continuity checklist | No path for 2S to unprotected MCU, RX or servo | NOT RUN |
| EE-T03 / G2 | Power logic-only with current limit and USB off | Supply V/I, boot log | Expected boot; safe disarmed startup; no heating/reset | NOT RUN |
| EE-T04 / G2 | Power MCU via supported path then connect USB as planned | Measured sources and reverse current | **No unapproved backfeed or unexpected powered nodes** | NOT RUN |
| EE-T05 / G2 | RX power-up, RC bind and UART level/protocol test | Scope/logic trace, valid-frame counters | Correct crossing, correct logic, no noise-triggered arm | NOT RUN |
| EE-T06 / G2 | Capture both PWM outputs over reset, brownout, boot | Scope trace | No unapproved pulse/actuation on startup or reset | NOT RUN |
| EE-T07 / G2 | Servo L then R then simultaneous without wings | I/V traces, servo pulse vs motion | Within actual voltage/current/temperature envelope, no reset | NOT RUN |
| EE-T08 / G2 | Battery sense 2S voltages across range on test supply | DMM vs ADC points / tolerance | Calibrated error limit **TBD before test**; invalid input detected | NOT RUN |
| EE-T09 / G2 | Unplug RX, corrupt frames, reboot TX/RX | logs / timestamps | Link state and freshness fail closed, no accidental rearm | NOT RUN |
| EE-T10 / G2 | Toggle arm / reverse channels / nonneutral throttle | command/state log | Arm rejected in invalid or ambiguous conditions | NOT RUN |
| EE-T11 / G2 | Brief controlled simulated load-step; no real servo jam | voltage dip / CPU reset count | Logic survives approved transient; no erroneous actuation | NOT RUN |
| EE-T12 / G3 | Restrained wings at incremental demands | I/V/temperature/vibration/strain and force | Stop on stall/binding/unstable rails; actual thresholds set from selected parts | NOT RUN |
| EE-T13 / G3 | Receiver link interruption while restrained | output/state/log/video | Observed response matches **bench** contingency; flight policy not assumed | NOT RUN |
| EE-T14 / G3 | Repeat C0 checks after C1 LED addition | current, rail noise, wing motion, RF diagnostics | No unexplained degradation; new revision reviewed | NOT RUN |
| EE-T15 / G0/G3 | Weigh complete electrical subsystem and locate CG | gram-level breakdown & CG | Updated C0/C1 budget, documented delta, no unsafe savings | NOT RUN |

**No numeric pass limits invented.** Exact currents, voltage tolerance, allowed reset count, UART baud, servo angles, thermal and electromagnetic disturbance thresholds require real selected parts, a datasheet review and an approved test plan before testing. A CPU reset causing uncontrolled motion is **automatic failure**, regardless of average voltage.

## 3. Test record template

```text
Electrical Test ID: EE-T__
Gate: G0 | G2 | G3
Status: NOT RUN | PASS | FAIL | BLOCKED
Date/time, owner, safety reviewer:
Airframe revision: C0 | C1
Reference design revision / Git commit:
Board + pin map revision, receiver, TX, servos, BEC, battery/bench PSU:
Instrument model + calibration:
Precondition and safety exclusion zone:
Input waveform / stimulus:
Expected behavior and agreed numeric limits:
Measured peak/avg values, brownout/reboots, servo behavior:
Evidence files (scope CSV, log, photo, video):
Deviation / corrective action:
Reviewer decision and owner approval:
```

## 4. Stop-work conditions

Stop the particular test and mark **FAIL/BLOCKED** for any uncommanded motion, unexpected reboot, high current, regulator heating, servo stall/binding, battery swelling/hot pack, cable damage, reversed polarity, unmanaged EMI, missing RC ownership or battery monitor failure. Investigate cause before retry; do not compensate by removing essential protection or silently relaxing constraints.

**G4 flight** remains separately approved under `14_V1_VERIFICATION_PLAN.md`. A G2/G3 electrical PASS does not prove controllable free flight.
