# BionicButterfly — V1 Pilot Control Hazards and Human Factors Review

- **Document ID:** BB-RISK-036 | **Version:** 0.1 | **Date:** 2026-11-12
- **Status:** PROPOSED; preliminary qualitative hazards. No numeric reliability claim or flight authorization.
- **Reviewed boundary:** pilot -> TX model/mixes -> radio system -> RX -> MCU safety FSM -> wing actuators; ground UI may observe/prepare but **cannot fly**.

## 1. Risk vocabulary and disposition

Do not assign a misleading low/medium risk without evidence about likelihood or tested mitigations. The `Impact` column describes the *type* of possible harm, not a certified severity rating. `Flight blocker` requires an accepted test/report/owner signoff before G4. Hardware physical responses remain design questions until qualification.

| Hazard | Trigger | Potential consequence | Preventive design control | Required evidence / gate | Status |
|---|---|---|---|---|---|
| H-RC-01 | arm switch held at boot / TX reboot | surprise wing start, injury | explicit LOW observation then LOW→HIGH plus full guards | PX-01 G1/G2 | OPEN |
| H-RC-02 | wrong model selected, TX mix changed, throttle reversed | full input unexpectedly, wrong turn | mapping revision, CH monitor, model ID, end-point check | PX-02/03/18 G2 | OPEN |
| H-RC-03 | CH5 ELRS arm semantics differ across v3/v4 | arm state mismatch/disconnect risk | verify protocol/version/mode; independent firmware arm | PX-20 G2 | OPEN |
| H-RC-04 | receiver holds last channels while RF lost | uncontrolled sustained motion | independent RF health/receiver failsafe evidence | PX-07/08 G2/G3 | **G4 BLOCKER** |
| H-RC-05 | late/reordered serial data or UART noise | stale/throttled response | validated frames, monotonic age, reject malformed | PX-08/19 G1/G2 | OPEN |
| H-RC-06 | saturated left/right mixer or wrong sign | opposite/unexpected turn and loss of control | measured differential sign, bounded mixer, no unproven hover | PX-05/15 G3 | **G4 BLOCKER** |
| H-RC-07 | in-air disarm interpreted as servo power cut | loss of lift/impact | separate bench/in-air policy, flight-specific evidence | PX-16 + IT-06 G3/G4 review | **G4 BLOCKER** |
| H-RC-08 | critical battery, servo stall, brownout | reset/disarm or continued unintended motion | power architecture, reset supervision, instrumented load testing | EE-T + MX, PX-10 G2/G3 | **G4 BLOCKER** |
| H-RC-09 | UI/phone sends conflicting commands | wrong owner/profile | in-flight RC-exclusive authority; config immutability | PX-06/09 G1/G2 | OPEN |
| H-RC-10 | pilot thinks active flapping means airborne or hover | unsafe operation and false confidence | truthful labels, no false flight sensor, training script | UX-02/06 G1/G2 | OPEN |
| H-RC-11 | no independent pitch/roll authority, unstable CG | uncontrollable flight even with steering | mass/CG, moment response, stability assessment, redesign option | MX-07/08, PX-15 G3 | **G4 BLOCKER** |
| H-RC-12 | pilot loses orientation, can no longer see butterfly | wrong steering or uncontrolled excursion | restricted test site, observer, visible orientation/abort criteria | site review + G4 test plan | **G4 BLOCKER** |
| H-RC-13 | optional LED cable increases wing inertia or damages wing | stall, structural fatigue, loss of lift | C0 baseline first, requalify C1 mass/power | MX + EE tests C1 | OPEN for C1 |
| H-RC-14 | operator changes profile while armed | abrupt stroke/power jump | reject flight profile edits and switching until validated | PX-06/11 G1/G2 | OPEN |

## 2. Operational separation

`PC_SIM` verifies logic; `BENCH_SERVO_ONLY` verifies electronics without a flapping airframe; `RESTRAINED_AIRFRAME` verifies wings/forces behind physical protection; `FLIGHT_TEST_APPROVED` requires separate written authorization. A "flight" context flag is not an airborne sensor. In flight, hard physical hazards (fire/short) may justify a different response from ordinary lost-link, and **there is no single universally safe actuator-off rule**.

## 3. Minimum pilot/observer review before future G4 authorization

- Demonstrate understanding of arm switch, throttle/direction axes and radio channel monitor in safe bench setup.
- Understand transmitter-level arming vs vehicle software arming, and the consequences of choosing wrong model/mode.
- Demonstrate response to **simulated** RF loss, no-link, telemetry blackout and profile mismatch without touching moving airframe.
- Agree on site boundary, airspace/permissions, battery/fire and people/property separation, protective barriers where appropriate.
- Assign pilot vs safety observer; observer can request stop/abort, but must understand that in-air recovery is airframe-specific.
- Use evidence log with exact transmitter/receiver/airframe revisions and preapproved numeric criteria; no free flight if critical unknowns remain.

## 4. Required owner-level choices

Radio hardware, pilot control orientation, whether rate switching is needed at all for first flight, IMU stabilization assistance policy, specific link-loss and battery actions when airborne, and first safe flight location. Owner's "continue designing" does not approve the hazards or trial.
