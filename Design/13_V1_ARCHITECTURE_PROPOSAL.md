# BionicButterfly — V1 System Architecture Proposal

- **Document ID:** DESIGN-P1-003
- **Version:** 0.3
- **Date:** 2026-11-12
- **Owner:** Solution Architect
- **Status:** PROPOSED / **OWNER REVIEW REQUIRED** — no implementation authorization
- **Evidence basis:** `Design/12_FIRMWARE_SOURCE_AUDIT.md` and four demonstration videos previously provided by owner (mechanical performance still to be measured).

## 1. Goals and boundaries

**Owner-confirmed V1 product goal:** A butterfly-shaped robot capable of **real, pilot-controlled powered flight using a physical RC transmitter**. Simulation, separated-actuator bench and restrained-wing trials are mandatory engineering phases, **not the V1 final acceptance**. The design shall make manual takeoff/steering/landing measurable; actual flight feasibility has not yet been proven. V2 is autonomous flight only after V1 is completed. LED, battery, exact RC hardware and wing size remain TBD.

**Explicitly outside V1 until proven:** automatic hover/position hold, IMU-based attitude stabilization, GPS navigation, fully autonomous flight, obstacle avoidance, guaranteed outdoor wind resistance and flight-ready certification.

## 2. Proposed logical architecture (separable modules)

```text
       Setup/bench browser UI                Physical RC receiver
          (not in flight)                     (primary in flight)
                 |                                      |
          Web/API adapter                         RC adapter
                 \                                      /
                  \------ Normalized ControlCommand --/
                                         |
                            Input Validation / Freshness
                                         |
                         Arming + Command Ownership FSM
                                         |
                  +---------------- Safety Supervisor ----------------+
                  |             |                 |                   |
             Battery health   Link timeout   Servo envelope     E-stop / faults
                  +----------------------+--------------------------+
                                         |
                              Motion / Profile Planner
                       (time-based flap, differential steering)
                                         |
                              Actuator Output Layer
                                         |
                              Left servo + Right servo
                                         |
                              Butterfly wing mechanism

                  Telemetry / Logging  <--- command + safety + actuator
                  LED effects          <--- read-only safety/armed status

              PC simulator: substitutes input, hardware and dynamics
```

**Safety invariant:** Nothing from UI or a radio packet may drive servos until a single validated, owned, fresh command is allowed by the safety supervisor and arming state. All actuator outputs pass through the same physical-limit enforcement, regardless of protocol/profile.

## 3. Interface contracts (draft)

| Interface | Proposed fields | Validation / ownership |
|---|---|---|
| `ControlCommand` | `source_id`, `trusted_ingress_monotonic_us`, `throttle [0..1]`, `steering [-1..1]`, `requested_profile`, `RF_link_health`, `optional_transport_sequence` | Reject malformed/stale/invalid values; anti-replay only where a protocol actually exposes a trustworthy counter; do not assume CRSF control frames have sequence numbers; one current controlling source; explicit arm edge |
| `MotionCommand` | `flap_hz`, `amplitude_deg`, `left_right_bias_deg`, `waveform`, `profile_id` | Bounded by approved actuator envelope and measured frequency/current constraints |
| `SafetyStatus` | `state`, `last_valid_control_age_ms`, `battery_v`, `fault_code`, `armed`, `stop_reason` | Generated internally; UI must not override fault conditions |
| `ActuatorCommand` | `left_angle_deg`, `right_angle_deg`, `output_enabled` | Mechanical soft limits, slew and servo pulse limits checked immediately before output |
| `Telemetry` | mode/profile, input freshness, servo commands, battery, faults, build version | No effect on actuator/safety state |

## 4. Proposed state machine

```text
BOOT -> SELF_TEST -> DISARMED
                    | [valid owner + neutral throttle + explicit arm]
                    v
                   ARMED -> ACTIVE_FLAPPING
                    |          |
                    +--- Disarm / invalid input / link loss / critical fault --+
                                                                              |
                                                                          SAFE_FAULT
                                                                              |
                                                      owner acknowledge + checks -> DISARMED
```

- **Ground/bench behavior:** If input fails, immediately prevent new flap commands and use a pre-approved neutral/disable policy that does not hit mechanical stops.
- **In-flight behavior (V1 requirement):** Define pilot-selectable emergency response and an aircraft-specific radio-loss/battery-critical response prior to G4. A sudden servo stop can remove lift; **no generic “stop = safe landing” claim**. Loss-of-link logic may differ from grounded bench behavior and must be validated on the restrained airframe and risk-reviewed.
- `PERCH` should be a deliberate state; whether link-loss can sustain motion is an explicit, testable policy decision. Do not silently bypass watchdog.

## 5. Configuration and responsibilities

- Single immutable/validated configuration at boot plus explicitly authorized parameters when disarmed. Pin map, servo pulse range, wing travel and power limits belong to a board/airframe profile, not ad hoc UI adjustments during flight.
- Flight planner uses measured delta-time (`micros` or high-resolution timer), not loop-count-based phase increments; sensors/RC input do not directly write to servo drivers.
- LED output is low priority and must not compromise actuator control or electrical noise margin.
- Software modules should permit host-side compilation for pure math, state machine and simulated telemetry; embedded-specific adapters isolated.
- Use a separate PC simulator first: deterministic virtual time; left/right angle plot; command source, arm/disarm, loss of signal, battery/fault injection; CSV log export. **This is kinematic/control simulation, not an aerodynamically validated flight simulator** until force/dynamics data are available.

## 6. Architectural trade-off to be approved

| Choice | Advantages | Risks | Recommendation |
|---|---|---|---|
| Clone/adapt ESP-FLUTTER firmware | Fast demo and established UI concepts | License constraints; monolithic code; safety/provenance gaps | **Reference only** until authorization and tests |
| Port S-DiY Nano code | Very small code and inexpensive board | ISR blocker; little telemetry; hard to extend; license uncertainty | **Do not use as foundation** |
| Clean modular firmware on ESP32-C3 | Better interface boundaries, testability, RC/web capability | More work before first demo | **Preferred V1 architecture**, pending owner approval |

## 7. Proposed verification gates

**G0 — Static/design:** Review and approve requirements, hardware schematic, mass/power budget, state machine, licenses and source provenance.

**G1 — PC only:** Deterministic tests of motion output bounds; stale/replayed packet rejection; command arbitration; arming transitions; fault recovery; timeout; battery fault injection. No hardware needed.

**G2 — Hardware bench (wings disconnected):** Servo center/limits and calibration, supply transient tests, emergency stop, RC loss and reconnect, startup behavior, battery measurements.

**G3 — Restrained airframe:** Measure flap frequency/current/temperature/structural integrity with guards, inspect asymmetry, coupling and vibration; evaluate flight-specific failsafe.

**G4 — Controlled flight (V1 product acceptance gate):** Only after previous gates pass and owner explicitly approves controlled site, equipment, mitigation, flight-specific failsafe and numeric pass/fail criteria. Manual powered flight including commanded steering and controlled recovery/landing is the target, not a claim of achieved performance.

**Not a schedule:** Gate labels are sequence/permission constraints, not estimated delivery dates.

## 8. Decisions requested from owner

1. **RESOLVED 2026-11-12:** V1 is real manually RC-controlled flight; V2 is autonomy later.
2. **OPEN:** Intended conditions: indoors or outdoors; wingspan/maximum weight constraints?
3. **RESOLVED at intent level:** Physical RC transmitter is the V1 flight-primary. Receiver, protocol, failover and channel map remain OPEN.
4. Hardware: own available ESP32 board/servos/RC receiver and battery details?
5. Code strategy: confirm **clean-room-inspired implementation** (use ideas, not copied third-party files) for future sharing/commercial freedom.
6. Are SA/Developer rule files `07`, `10`, `11` approved as the operational governance baseline?

Until recorded decisions and G0 approval, all material in this document remains a design proposal. SA will not publish a dev task or modify `Source/`.

## 9. Architectural impacts of owner decision (2026-11-12)

- **Flight-critical input path:** RC receiver → validated RC adapter → control authority/arming → safety supervisor → motion planner → servo driver. Browser remains setup/bench-only; no Wi-Fi requirement for flight.
- **Mass and power:** each additional module/LED competes directly with wing loading and energy budget. See `03_HARDWARE_DESIGN.md`.
- **Control semantics:** pilot command ≠ guaranteed heading response. Actuator steering map must be established by G3/G4 experiments. See `16_RC_INTERFACE_CONTRACT.md`.
- **Ground vs flight safety:** safety supervisor applies explicitly different policies where justified by flight hazard review; no untested in-air hard stop assumption.
- **V1 release:** requires G4 observed flight outcome; G1–G3 alone cannot close V1.

*Changelog 2026-11-12 v0.2: RC/manual free flight promoted from later experiment to V1 final objective by owner decision.*

## 10. Integration refinement (v0.3 — 2026-11-12; PROPOSED)

This section supersedes any ambiguous interpretation elsewhere that `sequence` must exist in every RC input, that a browser can command in-flight actuators, or that disarm implies sudden mid-air power removal. Canonical contracts: `26_SYSTEM_INTEGRATION_REVIEW.md`, `27_SAFETY_AND_FLIGHT_STATE_MACHINE.md`, `28_FIRMWARE_MODULE_AND_TIMING_CONTRACT.md`.

- **Source of truth:** RC UART decoder → local timestamp/validated frame → *separately validated receiver RF health* → authority/arming → context-aware supervisor → motion planner → calibrated servo envelope → actuator hardware abstraction. No direct web/ISR-to-servo path.
- **Flight owner:** physical RC only. Browser/UI may operate only in simulator or authorized grounded bench setup and cannot alter config or safety limits while armed.
- **Status naming:** `ACTUATION_ACTIVE` means a command requests flapping, not `IN_FLIGHT`. Actual airborne status is unknown without validated observation. The current `GROUND_ARMED` term is a legacy software label and must not be used as a flight sensor.
- **Output timing:** 5 ms logical control / 20 ms PWM are **candidate engineering hypotheses** for testing, not confirmed servo timings. Hardware timer behavior, power and input sampling must be validated on the selected board.
- **Flight-critical unknowns:** aerodynamic yaw/pitch/roll controllability, measured lift reserve, in-air loss-of-link/battery contingency and site safety remain **G4 NO-GO** blockers, even if simulator passes.
- **Approval:** Architecture and all referenced new files remain PROPOSED. Do not issue coding tasks until a bounded G0 approval is explicitly recorded as described in `30_G0_DESIGN_FREEZE_READINESS.md`.

*Changelog v0.3: cross-document interface alignment, clarified RC frame counters, UI authority and unknown airborne status.*
