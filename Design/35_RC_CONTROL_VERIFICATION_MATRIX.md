# BionicButterfly — V1 RC Control Mapping & Pilot UX Verification Matrix

- **Document ID:** BB-TEST-035 | **Version:** 0.1 | **Date:** 2026-11-12
- **Status:** TEST DESIGN ONLY; **all results NOT RUN**. This table neither approves hardware power-up nor authorizes flight.
- **Cross refs:** `14_V1_VERIFICATION_PLAN.md`, `16`, `27–29`, `32–34`, `36`.

## 1. Acceptance rules and test taxonomy

`PX` = pilot-control and UX test; `G1` = deterministic host simulation; `G2` = approved servo-only bench (wing mechanism disengaged); `G3` = separately authorized restrained wing/airframe test; `G4` = future airframe-specific free-flight experiment. No G1/G2 PASS can substitute for G4 evidence. Each PX test must save expected and actual raw input, normalized intent, supervisor state, actuator *command* (if applicable), timing and mapping/profile revisions. `PASS` requires comparison against approved criteria; no numeric timing or air-response thresholds have yet been approved.

## 2. Detailed cases

| ID | Gate | Stimulus / boundary | Expected behavior / acceptance | Trace to requirement |
|---|---|---|---|---|
| **PX-01** | G1,G2 | boot with ARM high, then toggle; radio reboot/rebind | no autoarm until legitimate LOW observation + LOW→HIGH edge, other guards pass | FR-001/002, VT-01/02, IT-01 |
| **PX-02** | G1,G2 | move each physical TX axis separately; vary TX default AETR/TAER | only configured logical CH changes; unused axes do not affect actuation | FR-004/018, VT-18 |
| **PX-03** | G1,G2 | reverse throttle/steering endpoints and center; abnormal calibration | configured sign/bounds exactly; inverted/mismatched map blocks ARM | FR-004/018, VT-04/18 |
| **PX-04** | G1,G2 | arm high with nonneutral throttle/steer, bad profile or low voltage | explicit denial reason, no flapping, no stale arm | FR-002/011, VT-02/11 |
| **PX-05** | G1,G2 | servo disconnected or safe bench; throttle and steering sweeps incl saturation | bounded left/right requests, no implicit yaw/altitude claim; log saturation | FR-009/010/018, VT-09/10/18 |
| **PX-06** | G1,G2 | move mode/rate while armed, unknown switch position, browser profile write | reject unapproved in-flight change and preserve active profile | FR-005/022, VT-17/22, IT-05 |
| **PX-07** | G1,G2 | fresh serial frames with RF transmitter OFF, receiver hold-last | RF health separate from serial freshness; new ARM denied, contingency event | FR-006/007/020, VT-06/07/20, IT-02 |
| **PX-08** | G1,G2 | loss/return of RX RF, UART pull, receiver reset, serial invalid | no accidental rearm, invalid frames cannot renew pilot intent; recovery guarded | FR-006/012/020, VT-06/12/20 |
| **PX-09** | G1 | conflicting command owner (web + RC + simulator), rapid malformed requests | exactly one owner; RC flight authority not preempted | FR-005/008/017, VT-05/08/17 |
| **PX-10** | G1,G2 | injected scheduler pause, low battery and RF lost in same tick | deterministic priority; event reason + context logged; physical policy qualified separately | FR-003/011/020, VT-03/11/20 |
| **PX-11** | G1,G2 | config version mismatch, CRC corruption, power loss during write | reject / roll back; never arm using generic fallback profile | FR-001/010/022, VT-01/10/22 |
| **PX-12** | G1,G2 | attempt to invoke flight-only context with SIM or bench profile | denied; operation context independent from profile | FR-008/019/022, VT-08/19/22 |
| **PX-13** | G1 | telemetry disconnected, radio unknown, sensor unavailable | UI shows UNAVAILABLE/UNKNOWN, not green healthy status | FR-014/015, VT-14/15 |
| **PX-14** | G1,G2 | LEDs/web/log CPU overload and RX burst | measured control deadline/timing, no bypass; failure reported; thresholds to qualify | FR-016, VT-16 |
| **PX-15** | G2,G3 | calibrated steering signs/wing asymmetry under load with force/moment rig | quantify direction and moment; if insufficient, stop design-freeze progression | FR-018/021, VT-18/21, MX-07/08 |
| **PX-16** | G3/G4 review only | in-flight disarm intent, lost RF, critical battery scenarios | owner-approved exact airframe policy required **before** any G4 attempt | FR-003/019/020, VT-19/20, IT-06 |
| **PX-17** | G1,G2 | switch bounce, noisy centering, channel changes at profile boundary | no repeated arm edge; no unsafe discontinuity or profile activation | FR-002/004/009, VT-02/04/09 |
| **PX-18** | G1,G2 | compare transmitter CH monitor values with UART decoded channels | exact configured mapping and firmware versions recorded | FR-018, NFR-010, VT-18 |
| **PX-19** | G1 | virtual clock wrap, long sleep, stale status and receiver reconnect | no bypass of age/health rules, no spontaneous arming | FR-006/009, VT-06/09, IT-04 |
| **PX-20** | G1,G2 | optional TX arm mode v3 vs v4; CH5/mode mismatch | wrong mode detected and disarmed; radio-level arm not equal MCU arm | FR-002/018, VT-02/18 |

## 3. Pilot comprehension and observational checks

| ID | Safe evaluation | Pass condition (to approve after pilot trial) |
|---|---|---|
| **UX-01** | ask pilot to identify disarmed state and output gate from radio + optional display | pilot can state physical arming status accurately; no confusion |
| **UX-02** | show `UNKNOWN` vs `LOST` and stale vs fresh serial in simulator | pilot/observer do not treat unknown RF as ready to fly |
| **UX-03** | prompt "turn left" at safe G3 rig while watching body-forward diagram | correct stick and observed differential direction recorded; no assumption of yaw |
| **UX-04** | disable network while keeping simulated RC | UI loss cannot affect active radio authority or control timing |
| **UX-05** | request config write while armed in PC_SIM | UI shows refusal; backend independently enforces same |
| **UX-06** | pilot narrates manual recovery process | can explain why bench stop differs from in-air contingency (still unapproved) |
| **UX-07** | incorrect model/profile selected on radio in disarmed bench setup | warning is comprehensible; ARM blocked |
| **UX-08** | review inspection/checklist with pilot and observer | all items understood; unresolved flight blockers called out explicitly |

## 4. Evidence record template

```text
PX / UX ID:                  Result: NOT RUN / PASS / FAIL / BLOCKED
Gate:                        context: PC_SIM / BENCH_SERVO_ONLY / RESTRAINED / G4
Date, test operator, reviewer:
Code Git commit:             config hash:              airframe version:
TX model + EdgeTX version:   ELRS TX/RX versions + switch mode:
RX model + CRSF transport:   channel-map revision:
Battery/servo/wing if used:  instrument and calibration version:
Starting state and hazards:  controls moved / receiver events:
Observed input/channel trace and RF health:
Expected vs actual safety state, left/right output (commanded vs measured):
Timing/evidence file links (CSV, UART capture, video, scope):
Defects/flight safety impact:             Signoff / next gate:
```

## 5. Exit / fail rules

- G1 mapping design: PX-01–14,17–20 and UX-02/04/05 can be completed in simulator, but actual radio/receiver versions still require G2.
- G2: no unexplained startup PWM, no unrecognized RF-health behavior, no channel sign reversal, power/servo limits recorded; any fault blocks G3 until reviewed.
- G3: force/moment sign, robustness, thermal and physically restrained link contingencies measured; unresolved controllability or emergency strategy blocks G4.
- G4: **no tests executed or authorized**. Any test needing an in-air loss-of-link event must be risk-approved and must not be casually performed as a "failsafe demo".
