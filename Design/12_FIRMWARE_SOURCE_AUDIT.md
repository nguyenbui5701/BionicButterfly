# BionicButterfly — P1 Firmware Source Audit

- **Document ID:** DESIGN-P1-002
- **Revision:** 1.0 — 2026-11-12
- **Owner:** Solution Architect
- **Status:** DRAFT / SECURITY & SAFETY FINDINGS — **NOT APPROVED FOR FLIGHT OR IMPLEMENTATION**
- **Inputs:** `P1_Source_Audit.zip` (SHA-256 `3245e30e38d33b06b0fa65f56dd78d9b55a2578508f691783bbf618969946c45`)
- **Reference HEAD as reported by project owner (not independently verified against archive content):**
  - ESP-FLUTTER: `b1e508f87be7105096661946c209f32db541a5d5`
  - S-DiY: `0ca29a0d14574b94e144325e0bbe1cf80a25fb5e`
- **Method:** Read uploaded source code and build/config documentation; static review only. **No PlatformIO/Arduino compilation, hardware measurement, RC-link test, CAD verification or flight test conducted.**

## 1. Executive assessment

**Recommendation:** Continue with a clean, independent `BionicButterfly` design; treat both repositories as **read-only technical references**, not an approved flight-ready base. ESP-FLUTTER offers more useful input/profile/UI patterns, while S-DiY offers a compact servo mixer and mechanical build concept. There are **safety-critical blockers** to resolve before driving a free-flying airframe.

The supplied archive contains 26 entries: ESP32 firmware (`src/`, `include/`, `platformio.ini`, context file) and S-DiY firmware (`firmware/`, `lib/`, manual/diff). It **does not contain** the S-DiY STL files, wiring diagrams or original video footage. Conclusions about mechanical geometry, center of mass, wing lift and real flight performance remain **UNVERIFIED**.

**Provenance discrepancy requiring immediate check:** Archive contains `src/hardware_config.h`, `src/hover_bias.cpp`, `src/led_control.cpp`, but those three files **were not in the owner's earlier `git ls-files` list** for ESP-FLUTTER. The local files might be untracked/ignored, or the working tree might differ from the recorded HEAD. Do **not** assume the uploaded snapshot is a clean copy of that commit. Request `git status --short`, `git ls-files --others --exclude-standard`, and `git check-ignore -v` for these paths.

## 2. Architecture and signal flow observed

### A. ESP-FLUTTER (ESP32/PlatformIO)

`src/main.cpp:24-49`:

```text
setup(): hardware config -> wing/servo init -> LED init -> wireless/Web UI init
loop():  updateWingMotion -> updateLedControl -> updateWiFiControl -> delay(1)

Phone/HTTP/WebSocket --\
ESP-NOW receiver ------+--> protocol-specific parsing/mapping -> arm/profile/safety checks
ELRS/CRSF UART --------/                                     |
                                         throttle / steering / trim / waveform
                                                             |
                                   wing_motion (phase from micros(), Hz, amplitude)
                                                             |
                                            left/right servo pulse commands
Battery ADC -> warning/cutoff (cutoff optionally enabled); LED and telemetry paths
```

- `src/config.h:16,40-52`, `platformio.ini:14-42`: XIAO ESP32-C3 selected by default. S3 and DevKit mapping listed as experimental in the code.
- `src/wifi_control.cpp:2369-2381,2383-2463,2677-2842`: normalized throttle/steering and channel mapping; multiple input channels converge toward actuator setters.
- `src/wing_motion.cpp:398-426,446-475,649-731`: phase integrates using `micros()` delta time, with triangle/sine waveform and a **default direct differential-amplitude mixer** (`config.h:138-151`). Final servo angles are clamped, but mechanical headroom is not guaranteed by a measured actuator envelope.
- `src/flight_mode.h:3-7`, `src/flight_mode.cpp:38-42`: `DISARMED`, `ARMED`, `PERCH`; defaults to disarmed after Wi-Fi control initialization.
- `src/flight_profile.cpp:16-23`: `CRUISE`, `SPORT`, `HOVER` are parameter presets. `src/hover_bias.cpp:80-116` uses a supplied **device** tilt parameter, not a measured onboard attitude loop. There is **no validated autonomous hover/position hold** in the supplied code.
- `src/wifi_control.cpp:4173-4226`: command-age watchdog of **500 ms**, with explicit exception for `PERCH`.
- `src/wifi_control.cpp:668-691`: optional voltage-cutoff path; default `batteryFailsafeEnabled = false` (`wifi_control.cpp:97-99`).
- `src/wifi_control.cpp:3520-3573,4166-4170,4281-4455`: Wi-Fi AP, HTTP endpoints and WebSocket command/control.

### B. S-DiY (Arduino Nano/PPM)

`firmware/firmware.ino:64-154,157-200`:

```text
PPM input D2 -> sample 8 channels -> steer/elev/throttle/trim/switches
           -> choose glide/perch/sine flap -> servo mixer -> clamp [5°,175°]
           -> left/right Servo on D4/D5; LED D6

RC edge-age >100 ms -> processFailsafe() -> damp flap offset toward 0
```

- `firmware/firmware.ino:157-169`: sine phase increment is **radians per loop**, not actual frequency in Hz; real frequency depends on executed loop period (including `delay(4)` at line 153).
- `firmware/firmware.ino:115-141`: mixed servo commands approximately `L=90+flap+steer+elev+trim`, `R=90-flap+steer-elev-trim` with 5–175 degree clamping.
- `BUILD_MANUAL.txt:37-52,74-87`: 2S battery, regulator, two hobby servos and PPM receiver are **upstream BOM guidance**, not validated electrical requirements for this project. In particular, supply must be selected by measured stall/transient current, dissipation and wiring, not by copying a 7805/AMS1117 recommendation.

## 3. Findings register — evidence and disposition

| ID | Severity | Finding and code evidence | Consequence / required action |
|---|---|---|---|
| **F-01** | **BLOCKER** | S-DiY `PPMReader` registers `attachInterrupt(..., isr, RISING)` in its constructor (`lib/PPMReader/src/PPMReader.cpp:24-40`); `firmware.ino:74-77` registers **another** ISR on the same D2 interrupt. AVR `attachInterrupt` registers a single callback per interrupt source; the second callback ordinarily replaces the first. The firmware comment claiming both are allowed is not a valid guarantee. | Likely RC channel decoder loses its ISR while the edge watchdog still ticks. **Do not flash/fly as-is**. Design one signal-decoding path that also timestamps validated frames; verify with a PPM signal generator and telemetry. |
| **F-02** | **BLOCKER** | ESP-FLUTTER ESP-NOW packet callback ignores sender MAC (`wifi_control.cpp:3268-3297`), checks only plain magic/version/size then queues controls; `updateEspNowReceiver()` can apply packet mode/config updates even when the selected protocol is not ESP-NOW (`3311-3324`, `2473-2554`). | Nearby radio sender potentially can change arm/profile/config without transmitter authorization. Define peer allowlist/pairing, authenticated commands where practical, protocol isolation, and command validation; test spoof/replay behavior. No claim made about remote Internet access. |
| **F-03** | **MAJOR** | The 500 ms input timeout skips `PERCH` (`wifi_control.cpp:4207-4226`) intentionally to retain decorative flapping. | Link-loss does not universally stop moving wings. Define per-state failsafe for **bench/ground** versus **flight**, and test each. Centering or stopping midair may itself cause loss of lift; do not presume it is a safe landing strategy. |
| **F-04** | **MAJOR** | Low-voltage servo cutoff exists but is disabled by default (`wifi_control.cpp:97-99,668-691`), with thresholds editable by UI (`3655-3683`). | Battery warning is not hard protection. Define monitored battery chemistry and voltage/current policy; measure with load and add an explicit supervisor. Avoid sudden flight-power cuts without safety analysis. |
| **F-05** | **MAJOR** | S-DiY edge watchdog treats **any** rising pulse as link alive (`firmware.ino:53-61,95-102`); `latestValidChannelValue()` preserves last valid values (`PPMReader.cpp:87-95`). | Electrical noise or malformed frames can mask stale control. Require frame validity, timestamped channel set, receiver failsafe flags (when available), and conservative recovery criteria. |
| **F-06** | **MAJOR** | ESP-FLUTTER defaults `DIRECT_FLAP_MODE=1` and `FIXED_AMPLITUDE_TEST_MODE=1` (`config.h:138-151,188-190`); the direct mixer scales travel and clips final servo angles (`wing_motion.cpp:649-674`) with nominal 0°–180° limits (`config.h:214-216`). | Potential endpoint clipping, torque spikes, stroke distortion and steering authority loss if real mechanical range is narrower. Safe envelope must be measured on restrained servo/wing test rig; never infer from code constants. |
| **F-07** | **MAJOR** | No onboard IMU stabilization logic established; `HOVER` is a preset (`flight_profile.cpp:16-23`) and `hover_bias.cpp:80-116` processes incoming device tilt. | Do **not** advertise hovering, attitude stabilization, obstacle avoidance or autonomous flight in V1 without sensor/control verification. |
| **F-08** | **MAJOR** | Hard-coded AP password `12345678` (`wifi_control.cpp:27-28`); HTTP control/configuration handlers are registered without visible per-request authentication (`3520-3573,4133-4164`); WebSocket commands at `4281-4455` rely on AP access. | Unwanted control by any connected local client. Replace defaults, define authenticated command paths and explicit arming ownership before flight tests. |
| **F-09** | **MEDIUM** | S-DiY `safeFlapAmp` is updated **after** `updateCurrentOffsetSine(throttle)` (`firmware.ino:124-136,157-169`), so current tick uses prior cap; output clipping still occurs (`195-199`). | Claim “always has headroom” is not guaranteed. Compute safe amplitude before waveform/mix; test worst-case simultaneous stick inputs. |
| **F-10** | **MEDIUM** | `wifi_control.cpp` is ~4,467 lines and embeds web UI within a firmware module; HTTP/WS/RC paths duplicate parts of the control mixing (`2383-2463,3375-3518,4281-4455`). | Harder to test invariants, maintain protocols and centralize safety. Propose thin adapters feeding a single command validator/controller. |
| **F-11** | **MEDIUM** | ESP startup servo neutralization happens before radio/flight-mode initialization (`main.cpp:32-35`, `wing_motion.cpp:352-395,826-859`). | Motor can move on power-up before user establishes intent. V1 bench procedure must isolate wings and validate startup pose; define boot state and output enable. |
| **F-12** | **MEDIUM / LEGAL** | S-DiY `firmware.ino:1-7` states `ALL RIGHTS RESERVED`; vendored `PPMReader.cpp:1-18` states GPLv3-or-later. ESP-FLUTTER has separately stated noncommercial terms in reference documentation, but license files were not included in this ZIP. | Do not transplant source, STL or webpage assets into a public/commercial repo until author/asset licensing is reviewed. Ideas/interfaces can inform a clean implementation; record provenance. |
| **F-13** | **INFO / TRACEABILITY** | S-DiY `BUILD_MANUAL.txt:15-20` mentions prebuilt `.hex` outputs not present in supplied archive. Three ESP files do not match previous `git ls-files` inventory (section 1). | Reproducible build not proven. Confirm clean checkout, source status and platform toolchains; record compiler/library versions/build logs before further decisions. |

**Severity convention:** BLOCKER = must resolve or exclude the code path before prototype flight; MAJOR = requires approved design/tests before hardware operation; MEDIUM = engineering risk to track; INFO = incomplete evidence. These are **static review findings**, not measured failure rates.

## 4. Reference usage decision (SA recommendation — NOT YET APPROVED)

| Aspect | Prefer borrowing as concept | Do not copy without further work |
|---|---|---|
| ESP-FLUTTER | Input adapters; flight profiles; wing waveform generation using elapsed time; status telemetry; configurable trim | Its open AP/control commands, unverified amplitude test configuration, radio authority paths and monolithic web UI |
| S-DiY | Lightweight airframe approach; two-servo mirrored kinematics; switchable motion modes; STL layout as an **inspection reference** | Current ISR/watchdog implementation, unchecked power supply recommendations, unverified mechanical limits; code/STL licensing rights |
| Our V1 | Simulator/bench-first clean implementation, safe arming and command arbitration, physics-informed calibration | Claims of autonomous hover or safe free-flight before test evidence |

## 5. Required evidence before approving V1 design

1. **Provenance:** On Windows run:

   ```powershell
   git -C ..\ESP-FLUTTER-reference status --short
   git -C ..\ESP-FLUTTER-reference ls-files --others --exclude-standard
   git -C ..\ESP-FLUTTER-reference check-ignore -v ESP-FLUTTER/src/hardware_config.h ESP-FLUTTER/src/hover_bias.cpp ESP-FLUTTER/src/led_control.cpp
   ```

   `check-ignore` may return no matches; that is normal. Preserve the output; do not run `git clean` or modify the reference tree.
2. **Reproducibility:** Build both original source trees in a disposable environment; record board profile, tool versions, build output. Do not infer build status from upstream manual.
3. **RC validity:** Bench test missing/silent/stale/malformed control, disarmed startup, return of signal, malformed ESP-NOW and protocol switching. Servo outputs disconnected from full airframe for initial tests.
4. **Hardware:** Obtain actual schematics/CAD/STL and actuator data; measure servo current at startup/stall, travel limits, mass, center of gravity, wing frequency vs. power.
5. **Product target:** Owner approves intended use (indoor/outdoor, demonstration versus controlled flight), weight/size budget, RC versus phone role, desired LED and safety constraints.
6. **IP review:** Verify authoritative license and ownership for each imported source and asset; decide whether any reuse is legally permitted. This audit does not give legal clearance.

## 6. Next design files / gates

- `Design/13_V1_ARCHITECTURE_PROPOSAL.md`: candidate design to review, not a dev task.
- `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`: remain role-boundary rules (proposed until approved).
- **No `Task/TASK-001.md` yet**: deliver a coding task only after owner approves the relevant design revision.
