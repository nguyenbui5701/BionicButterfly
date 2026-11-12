# BionicButterfly — Cross-Document Consistency & Conflict Register

- **Document ID:** BB-CONFLICT-049 · **Version:** 0.1 · **Date:** 2026-11-12
- **Status:** OPEN / awaiting comparison against actual owner Git revisions
- **Issue statuses:** `UNVERIFIED`, `OPEN`, `DRAFT RESOLUTION`, `CLOSED WITH EVIDENCE`. **No issue below is confirmed CLOSED** in this phase.

## 1. Active findings (verify first, fix at source)

| ID | Criticality / gate | Previously reported conflict or failure mode | Required source-of-truth rule / proposed resolution | Evidence of closure |
|---|---|---|---|---|
| **CF-01** | P0, G0-B/G4 | `19` had body `+Z UP`; `37` used `+Z DOWN`; 42 corrected by previous draft | Body right-handed **x forward, y right, z down**; inertial z up, explicitly documented rotation/force signs | inspect latest `19`, `37`, `42`, all fixtures/datasets for correct sign |
| **CF-02** | P0, G4 | Ground-safe stop/disarm may be incorrectly used as midair actuator power cut | Separate G2/G3 bench stop from **airframe-qualified in-flight contingency**; no universal ‘servos off’ policy | `27`, `25`, `39`, G3 evidence and signed G4 policy |
| **CF-03** | P0, G4 | Two independent servos do not prove lift, roll/pitch/yaw controllability or safe recovery | Retain manual pilot target, require `B∈R^(4×2)` measured local authority, passive/active-stability evidence | `37–41` + actual G3/G4 evidence |
| **CF-04** | P1, G0-A/G2 | Unconditional receiver `sequence` requirement conflicts with CRSF optional sequence | Counters exist only where actual protocol supplies them; require local monotonic receive time and validated RF health | `16`, `27`, `28` aligned; protocol bench capture |
| **CF-05** | P0, G2/G4 | UART-frame freshness may be falsely treated as proof of live RF control (receiver can hold channels) | Separate `uart_frame_valid` / frame age from `rf_health` and failsafe status; UNKNOWN not healthy | selected RX/TX firmware + unplug-RF and held-channel traces |
| **CF-06** | P1, G0-B | XIAO candidate D6/U0TXD can emit bootloader characters to receiver; D7 is UART RX | Record boot-time TX behavior, ensure CRSF parser ignores invalid frames and prevents auto-arm; final UART/console allocation board-tested | board boot traces and receiver interoperability test; Seeed pin-mux documentation |
| **CF-07** | P0, G0-B | XIAO `BAT` is not compatible with a 2S pack; 5V USB/external backfeed possible | Confirm pack/BEC topology and board-safe 5V input path, protections, servo brownout behavior | actual schematic/datasheets/bench test EE-T02/T04/T07 |
| **CF-08** | P1, G0-A | Legacy state name `GROUND_ARMED` can be mistaken for a physical ground sensor | Rename conceptually to `ARMED_IDLE`; actual airborne status `UNKNOWN` without validated sensing | align `27`, UI and logs |
| **CF-09** | P1, G0-A | Servo PWM carrier (e.g. 50 Hz) conflated with actual mechanical flap frequency | Define distinct `servo_pwm_hz`, `wing_flap_hz_requested`, `wing_flap_hz_measured`; no unqualified defaults | `23`, `28`, `33`, telemetry & tests |
| **CF-10** | P1, G0-A | Simulation planning example `T_CORE=5ms`, `T_LINK=500ms`, 50 Hz carrier could be promoted to flight parameters | all example values tagged `SIM_ONLY` and **never in airframe calibration** | config schema and negative acceptance tests |
| **CF-11** | P0, G0-A/G4 | Browser UI calibration/tuning conflicts with RC-only airborne owner | BENCH authenticated/disarmed or SIM only; no in-flight web arm/profile/OTA | `05`, `16`, `28`, `34`, tests PX-06/09 |
| **CF-12** | P1, G0-B/G4 | C0 70 g and C1 82 g are design *allocations*, not weighed aircraft | `mass_actual`, `cg_actual`, wing inertial properties must be measured for each revision | `20`, `44`, `47` weighed BOM, MX/RG tests |
| **CF-13** | P1, G0-A | `FLIGHT_TEST_APPROVED` may be modeled as user-selectable profile/mode | operation authorization separate from profile; no UI/config grants flight authority | `27`, `33`, `51`, tests PC-A and PX-12 |
| **CF-14** | P1, G0-A/G2 | ELRS ‘ARM using CH5’ behavior may be confused with 4.x alternative switch arming | per-version radio arming and MCU arming are **independent gates**; CH5 not universal | EdgeTX/ELRS revision, raw CH monitor and receiver trace |
| **CF-15** | P1, provenance | Reference firmware archive has paths whose Git tracked origin was not established | classify per-file as `REFERENCE_UNVERIFIED`, verify ignored/untracked and license | reference SHA/path/license manifest; no copied source |
| **CF-16** | P0, release | Design docs in chat/ZIP not necessarily equal latest owner's committed `Design/` | audit exact `HEAD`, differences, and approval statements before any freeze | signed baseline report with repository commit |
| **CF-17** | P1, G0-A | `ACTUATION_ACTIVE` sometimes read as ‘IN_FLIGHT’ | label as commanded actuator state only; physical flight is `UNKNOWN` absent validated sensor | state/UI contracts and tests |
| **CF-18** | P0, governance | SA instructed to commit locally, but current remote repository cannot be accessed from this session | provide additive artifact + SHA integrity record and disclose **no actual commit**; only commit when repo is accessible | `53`, owner verifies repository history |

## 2. Cross-document patch discipline

For each finding, capture: `ID`, original document/path+revision and exact paragraph, proposed replacement, affected tests, SA reviewer, owner approval, resulting commit. Never mass-replace technical terms by text substitution when changing semantics (e.g., Z-axis or failsafe). A correction to one document must be cross-checked against all dependent documents; a contradictory prior paragraph must be marked superseded or removed, not silently kept as a competing rule.

**Priority order:** P0 correctness/safety/source-of-truth → P1 interfaces and naming → P2 cosmetic wording. `CLOSED WITH EVIDENCE` requires versioned proof, not merely the presence of a new Markdown file.

## 3. Authoritative external reference checks

- XIAO pins, boot TX and strapping: https://wiki.seeedstudio.com/XIAO_ESP32C3_Pin_Multiplexing/ and https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/
- ESP32-C3 LEDC PWM low-speed mode/atomic updates: https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-reference/peripherals/ledc.html
- ExpressLRS 4.0 versus CH5 arming: https://www.expresslrs.org/quick-start/transmitters/tx-prep/ and https://www.expresslrs.org/software/switch-config/

A vendor's current documentation is authoritative only for the **matching hardware/firmware revision**; source-specific compatibility must still be measured.
