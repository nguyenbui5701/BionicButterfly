# BionicButterfly — V1 System Architecture Proposal

- **Document ID:** DESIGN-P1-003
- **Version:** 0.1
- **Date:** 2026-11-12
- **Owner:** Solution Architect
- **Status:** PROPOSED / **OWNER REVIEW REQUIRED** — no implementation authorization
- **Evidence basis:** `Design/12_FIRMWARE_SOURCE_AUDIT.md` and four demonstration videos previously provided by owner (mechanical performance still to be measured).

## 1. Goals and boundaries

**Candidate V1 target:** A controllable, twin-servo flapping-wing butterfly **bench prototype** with a virtual simulator, manual throttle/turn, emergency disarm, status telemetry and optional LED effect. Advance to tethered and then free-flight trials only after measured hardware + safety gates. LED, battery size and specific radio hardware remain choices, not fixed requirements.

**Explicitly outside V1 until proven:** automatic hover/position hold, IMU-based attitude stabilization, GPS navigation, fully autonomous flight, obstacle avoidance, guaranteed outdoor wind resistance and flight-ready certification.

## 2. Proposed logical architecture (separable modules)

```text
           Phone browser UI                     RC receiver
            (optional)                            (primary candidate)
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
| `ControlCommand` | `source_id`, `sequence`, `timestamp_ms`, `throttle [0..1]`, `steering [-1..1]`, `requested_mode` | Reject stale/replayed/invalid values; one current controlling source; arming requires explicit safe sequence |
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
- **In-flight behavior:** Must be evaluated separately; sudden servo stop can remove lift. **No generic “stop = safe landing” claim.** Flight-specific fallback/landing behavior requires experiments and a risk review.
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

**G4 — Controlled flight:** Only after previous gates pass and owner explicitly approves controlled site, equipment, mitigation and acceptance tests.

**Not a schedule:** Gate labels are sequence/permission constraints, not estimated delivery dates.

## 8. Decisions requested from owner

1. Priority: decorative flapping/LED demo first, or controlled free-flight as first major milestone?
2. Intended conditions: indoors or outdoors; wingspan/maximum weight constraints?
3. Control: phone Wi-Fi as prototype control or proper RC as flight-primary?
4. Hardware: own available ESP32 board/servos/RC receiver and battery details?
5. Code strategy: confirm **clean-room-inspired implementation** (use ideas, not copied third-party files) for future sharing/commercial freedom.
6. Are SA/Developer rule files `07`, `10`, `11` approved as the operational governance baseline?

Until recorded decisions and G0 approval, all material in this document remains a design proposal. SA will not publish a dev task or modify `Source/`.
