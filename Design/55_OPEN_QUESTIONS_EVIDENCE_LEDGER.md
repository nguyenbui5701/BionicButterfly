# BionicButterfly — Open Technical Questions & Evidence Ledger (Phase 2.0)

- **Document ID:** BB-OPEN-055 · **Version:** 0.1 · **Date:** 2026-11-12
- **Status:** PENDING/NOT MEASURED; use this as a planning list, not a substitute for owner decisions.

## 1. Unanswered questions sorted by when they block

| ID | Question/data needed | Earliest slice affected | Who can supply | Status |
|---|---|---|---|---|
| **OPEN-01** | Actual current `Design/` commit and changed files vs last Phase ZIP | G0-A1 | Owner repository access + SA | UNVERIFIED |
| **OPEN-02** | Latest versions of `27/28` state/data contracts agree with `02` | G0-A1 | SA review | UNVERIFIED |
| **OPEN-03** | Sim-only interval, arm/ack edge semantics and test framework acceptance | G0-A1 | Owner+SA | PENDING |
| **OPEN-04** | Named TX/RX, EdgeTX/ELRS versions and channel map/switch mode | G0-B1/G2 | Owner/bench tester | UNKNOWN |
| **OPEN-05** | Can receiver distinguish RF lost/held controls independently of serial age? | G2/G4 | chosen RX + hardware test | NOT RUN |
| **OPEN-06** | Exact MCU board revision and safe boot TX, ADC, PWM, power path | G0-B1/G2 | Electrical review and bench | UNKNOWN |
| **OPEN-07** | Servo part numbers and continuous loaded response (not only stall torque) | G0-B1/G2 | Component datasheets + tests | NOT RUN |
| **OPEN-08** | 1S/2S choice, BEC peak current and rail isolation | G0-B1/G2 | Electrical review and bench | UNKNOWN |
| **OPEN-09** | Actual C0 mass (battery/harness included), CG and wing inertia | G0-B2/G3 | Scales/CAD/physical inspection | NOT MEASURED |
| **OPEN-10** | Source CAD and toleranced hinge, spar, horn, pushrod, fasteners | G0-B2/G3 | Mechanical design | NOT RELEASED |
| **OPEN-11** | Rig sensor/calibration/force-moment uncertainty and guarding | G3 | Rig/testing plan | NOT BUILT |
| **OPEN-12** | Mean vertical force and derivative of moments wrt common/differential | G3 | Instrumented hardware | NOT MEASURED |
| **OPEN-13** | Pitch/roll/yaw recoverability with two servo inputs | G3/G4 | Mechanical/control study | UNKNOWN |
| **OPEN-14** | Is IMU assistance needed within manual V1 and permitted by owner? | pre-G4 architectural decision | Owner+SA | NOT DECIDED |
| **OPEN-15** | In-air RF-loss, low battery and disarm response for **actual aircraft** | G0-C/G4 | Risk review and qualified evidence | BLOCKER |
| **OPEN-16** | Intended first test environment, safety observer, radio range and local permissions | G0-C/G4 | Owner/site reviewer | NOT DECIDED |
| **OPEN-17** | Numerical V1 success criteria: repeatability, steering, recovery, envelope | G0-C/G4 | Owner after G3 data | NOT DECIDED |
| **OPEN-18** | Third-party source/CAD/images legal reuse permissions | before copying any files | SA/owner | UNVERIFIED |
| **OPEN-19** | C1 LED change to wing inertia, power, EMI and attitude response | after C0 demonstrated | Tester/SA | DEFERRED |
| **OPEN-20** | Full lifecycle of clean-room build, PR review, commit and deletion workflow | before Developer handoff | SA+owner | WORKFLOW DRAFT |

## 2. Evidence hierarchy and no fabricated progress

`OWNER-DECIDED` (explicit scope) != `DOCUMENTED` (design proposal) != `MEASURED` (instrumented run) != `VERIFIED PASS` (approved metric + reproducible evidence) != `AUTHORIZED` (separate act approved).

- A screenshot of waveform simulation is **not** evidence of actual wing angle, aerodynamic lift, controllability or electrical safety.
- A video of an upstream robot is **not** an acceptance test of our airframe.
- A table of desired masses, servo current limits or timestamps is **not** a measurement.
- A clean `git status --short` does not prove ignored files belong to a reference commit; `Design/` version status requires its own examination.
- `G1 PASS` cannot authorize G2, G3 or G4 without independent corresponding design and safety reviews.

## 3. Data acquisition priorities

**First, no hardware required:** OPEN-01/02/03/18/20, conflict CF-01/04/08/10/11/13/16/17, requirement IDs and document revision audit. **Then exact hardware:** OPEN-04/06/07/08/10 before powered bench. **Then real measurements:** OPEN-05/09/11/12/13 and flight safety case. **Eventually:** OPEN-15/16/17 plus recorded owner go/no-go decision.

There is no need to buy a device or authorize a test merely to finish this *design-only* phase.
