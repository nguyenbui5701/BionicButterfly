# G0-B Parallel Readiness — bridge from PC simulator to real servo-only bench

- ID BB-P225-193 · status **DESIGN / NOT APPROVED TO ENERGIZE**. This is **not** a hardware build guide or shopping approval.
- Outcome intended after F1: put two *unloaded* servos on a physically safe bench only after a separate Owner G0-B acceptance decision and reviewed schematics. G3 restrained wings and G4 flight each require later independent approval.

## Required decisions (record `TBD` until measured/selected)

| Decision ID | Current reference (candidate only) | Required evidence and reviewer approval | Status |
|---|---|---|---|
| HB-01 MCU/board | XIAO ESP32-C3 or equivalent | exact vendor/model/revision, boot pin behavior, safe supply and PWM constraints | OPEN |
| HB-02 Left/right servos | 2× digital 4–6g-class candidate | exact datasheet, voltage, stall/peak current, rotation, speed, PWM rate, current under bench load | OPEN |
| HB-03 RC TX/RX | ELRS transmitter+receiver candidate; UART CRSF | exact firmware/version/CH5 ARM behavior, RF-loss reporting, voltage levels; disarmed tests | OPEN |
| HB-04 Power | battery 2S+BEC exploratory | reviewed regulator+connector+poles wiring, reverse-feed/USB isolation, independent servo supply, current limit and earth return plan | OPEN |
| HB-05 Physical inhibit | emergency disconnect and restraint | verified startup/reset/brownout pin waveforms, no unsolicited output, safe abort behavior without wings | OPEN |
| HB-06 Bench instrumentation | DC source DMM/current meter and timing capture | calibrated meter/scope or justified substitute, temperature measurement, documented safe envelope, trained operator | OPEN |
| HB-07 Firmware separation | host FSM core + ESP32 HAL candidate | no direct GUI to PWM; disarmed boot, source ownership, limits, watchdog and fail-closed reset design | OPEN |
| HB-08 Airframe M1 C0 | 2-servo wings 70g design allocation | CAD, measured mass/CG and servo envelope after G2; no lift/heading/flight assumption | OPEN |
| HB-09 G3 restraint | wing mount/load rig | separately verified protection, force/torque/current/temperature/wing kinematics/clearance, no free flight | OPEN |
| HB-10 G4 flight | not eligible | real dynamics/control, flight-specific link-loss and disarm policy, site/pilot compliance, signed hazard review | BLOCKED |

## Stage plan

**This release:** Developer may create an evidence-ready **offline checklist** (`evidence/hardware_ready_template.md`) inside TASK-013 source tree only; must not add real firmware, device library, PWM command generator, USB/serial/network code, or simulate verified G2 data. SA and Owner can make hardware purchasing choices outside TASK-013 after reviewing exact datasheets and budget; no need to postpone software integration.

**G0-B design review (separate Owner signoff):** approve exact HB01–HB07 values, physical test plan EE-T01…11, schematic/pinout, emergency inhibit and evidence capture. This authorizes a **future scope-limited servo-only bench implementation task**; it is not a permission to attach wings or fly. Battery/LiPo safety requires qualified wiring review and no direct 2S voltage to MCU/5V servo.

**G2 (later):** logic rails first, RF UART only when safe and selected, then left/right servo **without wings** under current-limited bench configuration; record voltage/current, scope traces, thermal and power/reset anomalies, negative test for held ARM at boot. Failures stop and require design change.

**G3 (later):** mechanical wing restraint and incremental tests after G2 and signed G3 gate; study force, moment, control authority, CG, rotor/servo thermal and repeatability. A servo moving on G2 is not evidence of wing lift or stable flight.

**G4:** aircraft-specific contingency qualification, pitch/roll/yaw authority, site/pilot review and regulatory compliance; PC_SIM policy cannot approve this.

**Owner decision block:** `G0-B_REVIEW_ID`, bill of materials + exact revisions, selected test instruments, measured G2 limits, safety-review outcome, `APPROVE_DESIGN_ONLY|REWORK|DEFER`, explicit exclusions and reviewer signature/link. Until filled in and approved, HB status remains OPEN.
