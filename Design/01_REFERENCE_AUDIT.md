# BionicButterfly — P1 Reference Audit (Preliminary)

- **Document ID:** DESIGN-P1-001
- **Revision:** 0.2 — Draft
- **Date:** 2026-11-12
- **Owner:** Solution Architect
- **Status:** RESEARCH / NOT APPROVED FOR IMPLEMENTATION

## 1. Purpose

Assess two external bionic-butterfly repositories as *references*, not as an automatically approved codebase. Identify reusable concepts, risks, requirements that remain open, and the evidence required before design freeze. AI Code must not start implementation from this draft.

## 2. Reference repositories

### R1 — ESP-FLUTTER

- URL: https://github.com/maximagination1/ESP-FLUTTER
- Published description: XIAO ESP32-C3, two digital servos, controllable flapping-wing flight, optional LED wings, web joystick and RC transmitter.
- Reported features: ESP-NOW and CRSF/ExpressLRS inputs; configurable flapping frequency, amplitude, waveform, trims, differential-amplitude steering, flight profiles, arming, voltage monitoring, battery cutoff, LED effects, settings persistence.
- **Important constraint:** README says the current fixed-amplitude test mode uses throttle for flapping frequency. The named `Hover` profile is not automatic stabilization or position hold.
- **License:** PolyForm Noncommercial License 1.0.0. No commercial reuse of the firmware without appropriate permission.
- **Audit level:** README inspected. File inventory and local HEAD supplied by owner, but actual implementation contents and build have **not** been independently audited.

### R2 — S-DiY bionic-butterfly, corrected v1.1

- URL: https://github.com/25sidhx/bionic-butterfly
- Published description: Arduino Nano/ATmega328P, two servos, PPM RC receiver, 3D-print STL parts, wiring diagram and build manual.
- `README.md` states v1.1 includes an edge-based RC-link watchdog: no PPM pulse for more than 100 ms triggers a move toward neutral, plus improvements to clipping and flap-speed calculation. These are upstream claims, not verified on hardware by this project.
- The build manual includes example pin mapping (Nano D2 PPM, D4/D5 servos, D6 LED), BOM, 3D-print/assembly steps. **Do not treat power-supply choices in the upstream manual as validated for our hardware.**
- **Documentation discrepancy:** `BUILD_MANUAL.txt` describes some v1.0 build-kit material while README advertises corrected v1.1 firmware. Confirm the local file/version before basing design on it.
- **License:** Do not assume reuse rights until the repository's license and any third-party components are verified.
- **Audit level:** README/build manual inspected. File inventory and local HEAD supplied by owner, but actual firmware and STL contents not independently validated.

## 3. Comparison

| Attribute | ESP-FLUTTER | S-DiY | Preliminary direction |
|---|---|---|---|
| MCU | XIAO ESP32-C3 | Arduino Nano | ESP32 candidate; verify power, weight and real-time behavior |
| Wing actuation | Two servos | Two servos | Compare mechanical travel, mass, stroke/frequency |
| RC control | ESP-NOW or CRSF; phone web UI | PPM | Design a control-input adapter boundary |
| LED | Wing effects | Basic LED | Feature optional pending mass/power budget |
| CAD / fabrication | External project files/BOM linked | STL parts included | Inspect source availability and license |
| Safety | Arming, battery monitoring/cutoff (reported) | Link-loss watchdog (reported) | Define fail-safe independent of upstream assumptions |
| Simulation | Not established | Not established | Provide separate bench/virtual test plan |

## 4. Proposed system boundary (UNAPPROVED)

```text
Phone Web UI / RC Transmitter
             |
      Input Adapters
             |
  Command Validation & Arming
             |
  Safety Supervisor (link-loss, undervoltage, limits)
             |
  Flap Profile + Differential Steering
             |
      Servo Output Drivers
             |
       Left/Right Wings

Battery/Sensors ---> Safety Supervisor
User Settings ---> Validated Configuration
LED controller <--- Safe Operating State
```

This is an architectural hypothesis for review, **not** a verified circuit or flight controller.

## 5. Requirements to confirm with project owner

1. Primary goal: demonstrable controlled flight, or stationary flapping/ornamental motion first?
2. Control mode for V1: phone Wi-Fi, dedicated RC, or both?
3. Prototype cost ceiling and locally available fabrication tools (3D printer, soldering, instruments)?
4. Target wingspan/mass/flight duration, acceptable flight environment, and LED priority?
5. Intended distribution: private research, open source, or future commercial product? This affects licensing.

## 6. Source audit checklist — pending

- [x] Record exact local Git commit SHA for each reference (`git rev-parse HEAD`), **as reported by owner**.
- [x] Enumerate tracked project files (`git ls-files`), **as reported by owner**; entrypoints/config candidates identified by filename only.
- [ ] Read source file contents to verify actual entrypoints, pin definitions, configs and dependencies.
- [ ] Read firmware's initialization, control loop, flapping waveform and servo output logic.
- [ ] Verify RC packet timeout, disarm, input range validation and recovery behavior.
- [ ] Verify battery monitoring assumptions, voltage calibration and cutoff behavior.
- [ ] Examine servo travel endpoints and reversal, actuator saturation and control authority.
- [ ] Identify timing model (control-loop period, PWM/servo refresh, jitter).
- [ ] Confirm build instructions and dependencies in isolated development environment.
- [ ] Inspect mechanical CAD/STL for fit, symmetry, loads, center of mass and mounting.
- [ ] Inspect electrical power/current/regulator details before connecting batteries or servos.
- [ ] Check all top-level and embedded third-party licenses before code reuse.
- [ ] Cross-map key motions and features against b1–b4 video frames; distinguish observation from inference.

## 7. Risk register (initial)

| Risk | Severity | Mitigation before build |
|---|---|---|
| Link loss / runaway wing motion | High | Positive arming, timeout-to-neutral, bench tests |
| Servo stall, current spikes, brownouts | High | Measure/size supply, test with current limit, common ground |
| LiPo misuse / undervoltage | High | Appropriate battery protection and safe charging/handling |
| Wing mechanical damage / injury | Medium | Guards, free-space bench testing, emergency disarm |
| Inaccurate 'hover' assumptions | Medium | Treat flight modes as waveform presets until measured |
| Unlicensed third-party code or models | High | Maintain a license and provenance register |
| Apparent flight success lacking reproducible metrics | Medium | Define measurable tests and logging |

## 8. Phase gate before implementation

P1 ends only when the local source audit, mechanical/power feasibility, target requirements, license constraints, and source/video evidence are documented. SA will prepare final requirements/architecture/control/UI docs for review. **No `Task/TASK-*.md` is issued before design approval.**

## 9. Sources

- ESP-FLUTTER README: https://github.com/maximagination1/ESP-FLUTTER
- S-DiY README: https://github.com/25sidhx/bionic-butterfly
- S-DiY BUILD_MANUAL: https://github.com/25sidhx/bionic-butterfly/blob/main/BUILD_MANUAL.txt

## 10. Local reference snapshot supplied by project owner (2026-11-12)

These snapshots identify the *versions to audit*. Their SHA and tracked path listings were copied from the owner's terminal output; the SA has not read these local files and **does not yet claim source-level verification**.

| Reference | `git rev-parse HEAD` | Candidate files to read next |
|---|---|---|
| ESP-FLUTTER | `b1e508f87be7105096661946c209f32db541a5d5` | `ESP-FLUTTER/PROJECT_CONTEXT.md.txt`, `ESP-FLUTTER/platformio.ini`, `ESP-FLUTTER/src/main.cpp`, `config.h`, `hardware_config.cpp`, `wing_motion.*`, `flight_mode.*`, `flight_profile.*`, `wifi_control.*`, `hover_bias.h`, `led_control.h`, `ESP-FLUTTER/include/esp_flutter_espnow_packet.h` |
| S-DiY | `0ca29a0d14574b94e144325e0bbe1cf80a25fb5e` | `README.md`, `BUILD_MANUAL.txt`, `firmware/firmware.ino`, `lib/PPMReader/src/PPMReader.*`, `v11_diff.txt`, `schematics/circuit-original.jpeg`, `docs/wing-design-original.jpeg`, `print/*.STL`, `print/PRINT_PROFILE.txt` |

### Next evidence required

- **Control pipeline (ESP-FLUTTER):** inspect `main.cpp` → input receiving (Wi-Fi/ESP-NOW/RC) → validated commands → `flight_mode`/`flight_profile` → `wing_motion` → servo outputs; verify actual calls instead of assuming filename roles.
- **Actuators and power:** inspect `config.h` and `hardware_config.cpp` plus circuit; verify pin mapping, servo range, power and battery/undervoltage assumptions.
- **S-DiY RC safety:** inspect `.ino`, `PPMReader` and `v11_diff.txt` to assess link-loss behavior, actuator neutral and version-specific differences.
- **Hardware and fabrication:** inspect STL/wing images for mechanical assumptions; no dimensions or strength claim until measured.
- **Build/reproducibility:** check `platformio.ini`, library versions and compile results in an isolated workspace; reference clones remain read-only.
- **Video mapping:** compare b1–b4 observations to a *candidate* feature only; no automatic equivalence with either upstream repo.

**Current P1 gate:** Inventory received ✅; actual source contents, build, hardware, licensing and design approval ⏳. No implementation task should be issued yet.

## 11. Changelog

- 2026-11-12 (v0.1): Initial preliminary reference assessment from public repository documentation.
- 2026-11-12 (v0.2): Pinned owner-provided reference SHAs and exact candidate files; updated checklist and next audit priorities. Local implementation, hardware and video-motion audits remain pending.
