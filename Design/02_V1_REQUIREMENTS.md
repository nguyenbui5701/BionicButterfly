# BionicButterfly — V1 Requirements Specification

- **Document ID:** BB-REQ-001
- **Version:** 0.2
- **Date:** 2026-11-12
- **Owner:** Solution Architect
- **Status:** **PROPOSED — OWNER APPROVAL REQUIRED**
- **Applies to:** V1 **real, manually RC-controlled free-flying butterfly** as final product milestone; PC simulator and bench/restrained tests are mandatory prerequisite gates. This document itself is **not authorization to fly**.
- **Related documents:** `Design/12_FIRMWARE_SOURCE_AUDIT.md`, `Design/13_V1_ARCHITECTURE_PROPOSAL.md`, `Design/14_V1_VERIFICATION_PLAN.md`, `Design/15_V1_DECISION_REGISTER.md`, `Design/07_AI_CODING_RULES.md`

> **Important:** Numbers marked *TBD* require hardware measurement or owner decision. A default used only by the simulator is not an approved value for flying hardware. Evidence levels are `OBSERVED`, `DOCUMENTED`, `INFERRED`, `TESTED`, `DECIDED`; no flight performance is yet `TESTED`.

## 1. Product intent

Build a **real, manually controlled, butterfly-shaped flapping-wing aircraft**. Owner decision on **2026-11-12**: V1 target is powered free flight commanded by a **physical RC transmitter**, with demonstrable directional control and a controlled landing. **Self-directed/autonomous flight belongs to V2 after V1 succeeds.**

V1 development must prove, in order:

1. Safe state/control logic in a deterministic PC simulator.
2. Verified electrical limits, two-actuator wing mechanism and wired RC receiver on a restrained bench setup.
3. Measured structural, aerodynamic and steering feasibility for the actual airframe, including force/mass/energy budgets.
4. Controlled, approved free-flight trials demonstrating manual takeoff, steering, continued controlled flight and recovery/landing according to measurable criteria decided before flight.

A simulator or a flapping bench demonstrator is a **milestone**, not a complete V1. No flight attempt is authorized until G0–G3 pass, the flight-specific failure policy is approved, and G4 is explicitly authorized.

The target aesthetics (wing shape, LED patterns, exact scale) are informed by owner-provided videos `b1.mp4`–`b4.mp4`. Those videos **do not** establish a specific actuator, sensor, aerodynamics or reliable hover controller. The working hardware design is a **candidate**, not a reverse-engineered fact.

### In scope for V1

- **RC-first powered free flight**, manual pilot commands, and measured maneuverability as final V1 acceptance after the G4 flight-safety gate.
- Define and test a flight-specific contingency strategy (loss of link, low battery, structural malfunction), without treating midair motor/servo shutdown as intrinsically safe.

- Deterministic PC simulator for command validation, arming, fault injection and wing-angle traces.
- Modular firmware architecture targeting an ESP32-C3 **candidate board**, pending pin/power verification.
- Two independently driven servo outputs; selectable bounded waveform, frequency, amplitude and differential steering (bench evaluation only).
- One active command owner at a time, user-visible state, stop/disarm, telemetry/logging.
- Bench voltage monitoring and guarded calibration procedures after measured hardware envelope is known.
- Optional non-safety-critical LEDs and browser UI if they do not compromise control timing.

### Out of scope / unproven

- Automatic hover, positional hold, stabilization, IMU navigation, GPS autonomy, obstacle avoidance.
- Assertions that differential servo motion produces a reliable turn or that the vehicle can carry a specific payload.
- Flying directly from unreviewed upstream firmware or deploying a battery/servo design from an unverified BOM.
- Autonomy and GPS/IMU closed-loop self-flight as V1 acceptance; those are V2. Flight test site (indoor protected hall or outdoor calm area), limits and legal obligations remain TBD.

## 2. Stakeholders and role boundaries

| Role | Main responsibility |
|---|---|
| Project owner | Approves V1 scope, hardware constraints, architecture, risk acceptance and design freeze |
| SA | Maintains `Design/`, traces requirements to evidence, records decisions, audits implementation in isolated PR checkout |
| AI Developer | Implements **only** `Task/TASK-*.md` derived from approved design; changes `Source/` and runs prescribed tests |
| Tester/experimenter | Produces reproducible simulator and restrained-bench evidence, records equipment and safety precautions |

A draft/proposed requirement shall **not** be silently promoted to implementation scope. SA must not write implementation code on the Developer's branch.

## 3. Functional requirements

Acceptance criteria below describe desired behavior; test IDs are defined in `14_V1_VERIFICATION_PLAN.md`.

| ID | Priority | Requirement | Verification / measurable acceptance |
|---|---|---|---|
| **FR-001** | Must | On boot/restart, enter `DISARMED` and keep unintended flap commands from reaching actuators. | VT-01: simulator boot and restart always report `DISARMED`, `output_enabled=false`; bench startup separately checked with wings disconnected. |
| **FR-002** | Must | Arming requires explicit user action, valid current controller ownership, no active blocking fault and neutral throttle. | VT-02: failed prerequisites never arm; valid sequence arms once. |
| **FR-003** | Must | Explicit disarm/E-stop command has priority over mode/profile changes. | VT-03: stop returns to guarded bench output policy by next control evaluation; no automatic re-arm. |
| **FR-004** | Must | Normalize all incoming inputs to a versioned `ControlCommand` before affecting state or actuator output. | VT-04: malformed/out-of-range/nonfinite fields rejected; no direct adapter-to-servo calls. |
| **FR-005** | Must | Exactly one source owns motion control; source switching requires explicit reauthorization or safe disarm/re-arm. | VT-05: non-owner packets cannot change motion, arm status or configuration. |
| **FR-006** | Must | Detect stale commands by age of **validated frames**, not mere radio edges; reject replay/duplicate sequence numbers where protocol supports them. | VT-06: stale, duplicate, malformed and wrong-source input is rejected; loss of valid frames triggers fault policy. |
| **FR-007** | Must | Define a link-loss timeout and apply a consistent **bench-specific** failsafe, including decorative/perch-like states. | VT-07: default simulator `T_LINK=500 ms` is **provisional**; after threshold, motion is disallowed/controlled to approved bench-safe condition; flight response is separately unresolved. |
| **FR-008** | Must | The central safety supervisor is the only path authorizing output. | VT-08: combinations of invalid input, unarmed state, fault and out-of-envelope motion never produce an enabled unsafe command. |
| **FR-009** | Must | Produce bounded left/right servo trajectories from monotonic elapsed time, not loop iteration count. | VT-09: different simulator scheduler steps produce equivalent trajectory at the same virtual timestamps within a documented numeric tolerance (initial proposal: `1e-3 degree` for identical inputs). |
| **FR-010** | Must | Enforce separately calibrated left/right mechanical soft limits, and limit setpoint slew/refresh based on measured servo capabilities. | VT-10: no command exits measured bounds even at max throttle+steering+trim. Hardware values **TBD**, not assumed to be 0°–180°. |
| **FR-011** | Must | Make battery/power critical events visible and feed them through the supervisor. | VT-11: simulated low/invalid voltage produces defined fault/notification. Physical cutoff/flight response remains **TBD** until measurement. |
| **FR-012** | Must | Require disarm + deliberate fault acknowledgment + restored healthy conditions before recovery. | VT-12: restoring radio or voltage does not automatically restart flapping. |
| **FR-013** | Must | Provide deterministic PC simulation using virtual time, controllable input/fault injection and CSV/event logs. | VT-13: reproducible scenario replay produces identical state/event trace and bounded angle output; CSV includes timestamps, state, source, fault and two angles. |
| **FR-014** | Should | Expose state, input age, mode, commanded angles, faults and measured/simulated voltage in telemetry. | VT-14: displayed telemetry agrees with internal state; labels distinguish simulated from measured values. |
| **FR-015** | Should | Provide a basic manual UI: arm/disarm (when permitted), throttle, differential steering, waveform/mode, status and fault banner. | VT-15: unsafe/disallowed actions disabled and rejected on backend; UI is never the sole safety enforcement. |
| **FR-016** | Could | Drive optional LEDs independently of control timing, with a fault/armed status indication. | VT-16: LED effects cannot alter servo commands, arming, fault state or miss control deadlines in bench measurement. |
| **FR-017** | Must | Primary V1 in-flight operator uses a physical RC transmitter/receiver; Wi-Fi/browser cannot seize control during flight. | VT-17: RC active-owner mapping tests; unauthenticated/secondary interface cannot affect in-flight motion. |
| **FR-018** | Must | Pilot can command flapping power and directional steering via deliberately defined RC controls, with explicit arm/disarm switch logic. | VT-18: calibrated channel map and left/right setpoint response; transmitter failsafe tested on bench. |
| **FR-019** | Must | Demonstrate a repeatable free-flight scenario under approved G4 trial conditions, including observable pilot-commanded directional change and controlled recovery/landing. | VT-19: owner-approved numeric flight criteria + synchronized video/log; outcome remains NOT TESTED until real flight. |
| **FR-020** | Must | Provide flight-specific link-loss and critical-battery contingencies validated as far as practicable on restrained rig before G4. | VT-20: risk review; injected faults; no automatic assumption that disabling wing motion equals safe landing. |
| **FR-021** | Must | Produce mass budget, center-of-gravity measurement, actuator torque/speed/load tests, structural inspection and aerodynamic thrust/lift evidence before G4. | VT-21: measurements documented, engineering feasibility reviewed; no guessed flight-ready rating. |
| **FR-022** | Must | Do not allow browser tuning, calibration or OTA changes to servo envelope or flight profile during powered flight. | VT-22: no configuration change while armed; changes require safe disarmed state, validation and recorded revision. |
| **FR-023** | Should | Log flight-test equipment/config, battery, pilot inputs, vehicle response and outcome, with telemetry optional where weight allows. | VT-23: test report traceable to exact configuration and observed events. |

**Requirement precedence:** critical fault / E-stop > disarm > ownership and input validity > actuator bounds > motion/mode > UI/LED. This is a **proposed architectural rule** pending owner approval.

## 4. Quality and safety requirements

| ID | Priority | Requirement / objective | Evidence needed |
|---|---|---|---|
| **NFR-001** | Must | Pure safety/state/motion algorithms must be testable on desktop without ESP32 SDK or hardware. | Host-side tests compile and pass (VT-01–13). |
| **NFR-002** | Must | Every output command passes the same central state/limit gate, irrespective of Wi-Fi, RC or simulator input. | Code review + fault injection matrix. |
| **NFR-003** | Must | Radio/remote control trust boundary explicitly documented; commands from unpaired/unapproved peers never gain control. | Adversarial input tests on simulator and, later, bench; pairing/security approach TBD. |
| **NFR-004** | Must | No embedded default hard-coded production Wi-Fi credential and no plaintext secret committed. | Configuration/secret scan and review. |
| **NFR-005** | Must | Reference clones and third-party assets remain read-only; provenance and license assessed before copying any code, CAD, STL or images. | Source manifest + license approval record. |
| **NFR-006** | Must | Measured mechanical servo limits, load current/stall risk, supply behavior, wing mass/CG and emergency procedure exist before connecting wing mechanism. | Approved bench checklist + measurements G2/G3. |
| **NFR-007** | Must | A flight-specific loss-of-link strategy is developed and approved before attempting free flight; abruptly stopping wings is **not** presumed to be a safe landing. | Dedicated hazard analysis and G4 authorization. |
| **NFR-008** | Should | Firmware identifies build version, config revision and command/safety events in its log. | Repeatable reproduction of a reported issue. |
| **NFR-009** | Should | Safety priority must not depend on UI network connectivity or LED animation. | Timing and fault tests. |
| **NFR-010** | Must | RC link and transmitter mode/switch mapping must be explicitly proven on the chosen hardware; no RC protocol, UART pin, frequency or failsafe is assumed from upstream examples. | Read-only receiver datasheet + physical bench capture/validation. |
| **NFR-011** | Must | Flight acceptance needs reproducible measurements and a flight site/hazard plan, including people/property separation and applicable local permissions. | G4 signed checklist + video and logs. |

## 5. Interface contracts (draft)

- `ControlCommand`: `{schema_version, source_id, sequence, receiver_time_ms, throttle[0..1], steering[-1..1], mode_request, arm_request}`. Timestamp must be assigned/validated at a trusted ingress; raw sender clocks are not inherently authoritative. Finite values only. Anti-replay policy per protocol.
- `SafetyState`: `{state, active_owner, command_age_ms, fault_code, reason, output_permission}`. Only supervisor may determine `output_permission`.
- `WingSetpoint`: `{t_ms, left_deg, right_deg}` bounded by calibrated limits and disabled when no permission.
- `TelemetryFrame`: `{t_ms, simulated, build_id, source, state, command_age_ms, mode, left_deg, right_deg, supply_v, fault_code}`; no control side effects.
- **No direct UI/network callback may call the physical servo driver.** All paths go through validation → supervisor → motion planner → envelope check → driver.

## 6. Open decisions and requirement dependencies

The following need owner approval or hardware data before becoming an implementable hardware contract:

1. **Primary outcome — OWNER DECIDED 2026-11-12:** V1 = real free flight under manual physical RC control. Bench-first remains required as a **development sequence**, not the final V1 objective. V2 = autonomous flight, only after V1 success.
2. **Environment:** indoor/outdoor tests; max wingspan, target mass and budget — **TBD**.
3. **Input transport — OWNER DECIDED intent:** physical RC transmitter is mandatory in-flight. Receiver technology (e.g. UART CRSF from a suitable receiver), binding/trust, pin mapping, and protocol details remain PROPOSED/TBD; browser/Wi-Fi is bench/config only.
4. **Available hardware:** ESP32-C3 model, two servo part numbers, receiver, battery chemistry/cell count, regulator, wing material — **TBD**.
5. **User experience:** optional LED in first demonstrator; browser panel vs RC-first setup — **TBD**.
6. **Licensing:** new original source only unless explicit per-file legal approval to reuse third-party works (**recommended**).
7. **Numeric limits:** physical servo travel, frequency, amplitude, dynamic slew, power and low-voltage thresholds **TBD**; simulator values shall be labeled hypothetical.

See `15_V1_DECISION_REGISTER.md` for proposal IDs. **No Task file should be opened solely based on this PROPOSED document.**

## 7. Traceability

| Rationale | Requirement references | Source |
|---|---|---|
| ISR collision/invalid PPM link data | FR-004, FR-006, NFR-002 | `12_FIRMWARE_SOURCE_AUDIT.md` F-01, F-05 |
| Untrusted ESP-NOW/AP control | FR-004–006, NFR-003/004 | F-02, F-08 |
| PERCH bypass and battery protection | FR-003, FR-007, FR-011/012, NFR-007 | F-03, F-04 |
| Servo endpoints/startup | FR-001/008/009/010, NFR-006 | F-06, F-09, F-11 |
| No validated hover | In-scope/out-of-scope and honest telemetry | F-07 |
| Monolithic upstream software | FR-013, NFR-001/002 | F-10 |
| Third-party rights and snapshot mismatch | NFR-005 | F-12, F-13 |

## 8. Approval record

- Owner decision on V1 goal and RC-first/V2 autonomy: **CONFIRMED in user message, 2026-11-12**; full requirements/architecture approval: **PENDING**
- Date / approval source (GitHub issue, PR or explicit owner confirmation): **PENDING**
- Approved revision/commit: **PENDING**
- Next step after approval: SA freezes relevant decisions, resolves missing values for target scope, then creates targeted `Task/TASK-XXX.md`.

## Changelog

- 2026-11-12 v0.1: Initial V1 requirements from static audit and architecture proposal; no hardware assertions.

- 2026-11-12 v0.2: Owner confirms **real manual RC free flight is the V1 goal**; flight acceptance and flight-specific safety requirements added. Full design approval still pending.
