# BionicButterfly — V1 Pilot Experience, Bench UI and Preflight Interaction Design

- **Document ID:** BB-UX-034 | **Version:** 0.1 | **Date:** 2026-11-12
- **Status:** PROPOSED, not an approved flight procedure.
- **Target experience:** pilot uses a physical RC transmitter for ALL active flight inputs; phone/browser is a separate disarmed maintenance/test tool.

## 1. Pilot journey (UX tasks)

1. **Prepare off-line:** select the correct named TX model and physically inspect airframe/wing locks/battery/CG. Site and pilot permissions separately approved.
2. **Confirm disarmed state:** ARM physically low, throttle minimum, steering neutral; do not trust a screen icon alone. Flight-authorized airframe profile must match exact machine.
3. **Power on / self-test:** aircraft reports DISARMED, servo output inhibited, receiver/radio link and power health checked; held-high ARM never auto-arms.
4. **Verify command axes on the bench:** move a single control at a time with wings/actuators made safe; confirm decoded CH, signs, endpoints and metadata.
5. **Request ARM:** deliberate low→high edge only after all guards; failed ARM yields explicit reason and no motion. Radio-level armed indication and firmware armed state must both be understood.
6. **Pilot controls:** a single fixed flight-qualified profile; physically move throttle/steer. Other radio controls cannot unexpectedly activate calibration/LED/OTA.
7. **End flight:** controlled recovery/landing in G4 scenario using flight-specific approved process; in-air disarm consequences unresolved and **must not be trialed without approval**.
8. **Power down/log:** disarm on ground, verify no actuation, capture flight/build/config revision, inspect mechanics, preserve event log.

## 2. Ground UI access rules

| UI mode | Inputs exposed | Allowed actions | Prohibited actions |
|---|---|---|---|
| `PC_SIM` | simulated RX, voltage, faults, clock | replay, virtual arm/disarm, virtual waveforms, export CSV | claim measured force/flight |
| `BENCH_DISARMED` | measured device state, mapping proof | inspect status, read config, run *authorized* calibration via gated staged workflow | command servo without approved hardware context; upload arbitrary flight policy |
| `BENCH_ACTIVE` | read-only health | observe, log, invoke qualified bench stop | profile write, OTA, switch command owner |
| `FLIGHT_TEST_APPROVED` | optional radio/telemetry only, data if available | **read-only** status (no dependency for flight) | browser arm, throttle, steering, calibration, failsafe override |

If no reliable telemetry exists, display **UNAVAILABLE** rather than fabricated zeros. `airborne_status=UNKNOWN` unless a sensor/observer has been validated; `ACTUATION_ACTIVE` alone is not proof of airborne state. Explicitly distinguish `SIMULATED`, `MEASURED ON BENCH` and `MEASURED IN FLIGHT` tags.

## 3. Core informational screen — wireframe (not flight control)

```
┌─────────────────────────────────────────────────────────────┐
│ BIONIC BUTTERFLY   [SIM / BENCH / FLIGHT READ-ONLY]          │
│ System: DISARMED  Link: UNKNOWN  Owner: NONE                 │
│ Profile: NO FLIGHT PROFILE APPROVED                          │
├─────────────────────────────────────────────────────────────┤
│ CH monitor: STEER [ - - ● - - ]  FLAP [●---------] ARM:LOW    │
│ RX: frames age=...  RF link=UNKNOWN  Failsafe=UNKNOWN         │
│ Power: UNAVAILABLE       Output: INHIBITED                    │
│ Left cmd: --   Right cmd: --  Servo feedback: UNAVAILABLE     │
├─────────────────────────────────────────────────────────────┤
│ [Simulator scenarios] [Mapping checker] [Read-only logs]     │
│ [Calibration] DISABLED (wrong context / missing approval)    │
│ ERROR / DENIAL: exact reason, timestamp, policy revision     │
└─────────────────────────────────────────────────────────────┘
```

The UI should never display a green "SAFE TO FLY" label based only on software state. Use `G4 NOT AUTHORIZED`, `BENCH TEST ONLY`, and `OWNER APPROVAL PENDING` when those are facts. The actual controller hand feel is validated with pilot on bench, not from visual mockups.

## 4. Feedback and alarm hierarchy

| Priority | Situation | UX reaction | Control behavior |
|---|---|---|---|
| P0 | unexpected actuation, severe hardware hazard | distinct physical stop procedure, unmistakable critical label on available telemetry | hardware/context-specific; no promise of safe flight from UI |
| P1 | RF LOST/UNKNOWN, failsafe, critical power | clear source/status and last-confirmed time; store event | supervisor contingency (flight policy TBD) |
| P2 | ARM rejected, wrong model/map/profile, non-neutral input | short reason code + exact prerequisite; visible rejected transition | remain DISARMED |
| P3 | profile/rate request declined, calibration locked | nonblocking explanation; do not change flight output | retain current approved state |
| P4 | cosmetic LED/theme | optional | always preempted by control/telemetry priorities |

No assumption that a ground screen has connectivity during flight. If radio offers voice/haptic alarms, configure them only after exact model verification and bench test; do not rely on them as sole evidence of a failed link.

## 5. Preflight checklist UX — **DRAFT, NOT AUTHORIZATION**

| ID | Check and observable evidence | Expected disposition |
|---|---|---|
| PF-01 | matching TX model, RX identity, firmware/switch mode, mapping revision | any mismatch → NO-GO |
| PF-02 | mechanical inspection: wing structure, symmetry, fasteners, linkages, CG | damage/unknown CG → NO-GO |
| PF-03 | correct battery/connector/rail, no abnormal heat, power evidence | invalid power measurement → NO-GO |
| PF-04 | approved airframe profile and measured servo envelopes | missing report → NO-GO |
| PF-05 | firmware cold boot observed DISARMED, outputs inhibited | unexplained motion → NO-GO |
| PF-06 | CH monitor: throttle/direction/arm sign, neutral and bounds verified, without dangerous wing motion | reversed/unstable channel → NO-GO |
| PF-07 | receiver link state and physically tested loss/recovery behavior | UNKNOWN/unproven → NO-GO |
| PF-08 | G4 flight-only contingency policy signed; human/premise/weather hazards assessed | unresolved → NO-GO |
| PF-09 | physical pilot and observer agree on abort and boundary procedure | unclear roles → NO-GO |
| PF-10 | G0–G3 evidence attached; exact configuration revision recorded | missing evidence → NO-GO |

The checklist is a *design requirement*, not an instruction to initiate flight now. Site/legal safety review and measurable G4 acceptance are independent required gates.

## 6. Pilot ergonomics decisions (open)

- Left-handed/right-handed control preference, spring-return throttle or non-return slider, physical arm switch location and tactile distinctness.
- Whether the transmitter provides a reliable telemetry alert and if audio cues can be heard in the flight location.
- What pilot calls *left* or *right* from head-on/back-facing butterfly; clearly define body-forward coordinate axes and verify actual moment on G3 rig.
- If passive stability or a third independent degree of control is required, redesign V1 controls; do not overload a stick to falsely imply attitude hold.

## 7. Usability acceptance and evidence (no tests run)

Proposed `UX-01…UX-08` are specified in `35_RC_CONTROL_VERIFICATION_MATRIX.md`. User/pilot needs to interpret ARM/owner/link state without a web page, and distinguish lack-of-response from wrong mapping. Record observer notes and repeatable video in safe bench configurations. G4 remains NO-GO.
