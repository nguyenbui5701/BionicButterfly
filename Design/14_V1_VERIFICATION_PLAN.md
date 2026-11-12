# BionicButterfly — V1 Verification & Safety Gates

- **Document ID:** BB-VER-001
- **Version:** 0.5 | **Date:** 2026-11-12
- **Owner:** Solution Architect | **Status:** PROPOSED — NOT EXECUTED
- **Refs:** `02_V1_REQUIREMENTS.md`, `12_FIRMWARE_SOURCE_AUDIT.md`, `13_V1_ARCHITECTURE_PROPOSAL.md`

## 1. Meaning of results

- **NOT RUN** means proposed test only; no result may be represented as PASS.
- **PASS** requires artifacts: test log, configuration, test build/commit, source evidence, expected vs actual and reviewer.
- **FAIL / BLOCKED** requires defect ID and reproduction steps.
- Tests with virtual battery, servo and radio signals **do not establish** hardware or flight safety.

## 2. Verification gates

| Gate | Target and required output | Authorization |
|---|---|---|
| **G0 — Design review** | Requirements, architecture, command/state contracts, license/provenance list, hardware risk list and unresolved owner choices recorded | Owner approves bounded design scope |
| **G1 — PC simulation** | Deterministic command/state/motion tests below; CSV logs; fail/recover cases | No physical actuators |
| **G2 — Servo bench** | Wings disconnected; validated pin map; supply/inrush measurements; safe startup, limits, disarm and link-loss tested | Owner approves bench safety plan |
| **G3 — Restrained wings** | Mechanical guard, frame restraint, video/current/frequency/temperature/strain measurement; risk review | G2 passed and physical guard checked |
| **G4 — Flight experiment / V1 acceptance** | Owner-approved quantified powered free-flight scenario including manual takeoff, response to steering, controlled recovery/landing and traceable evidence | **Mandatory for V1 completion**, but requires separate explicit owner flight authorization after G0–G3 |

## 3. Simulator test matrix — planned, none executed

| Test | Maps to | Input / procedure | Expected result |
|---|---|---|---|
| **VT-01** | FR-001 | Boot, reboot, malformed persisted settings | DISARMED, outputs not enabled; no spurious arm |
| **VT-02** | FR-002 | Arm with non-neutral throttle, stale command, fault, no owner; then valid arm | All invalid arms rejected, valid arm accepted |
| **VT-03** | FR-003 | E-stop/disarm during max flapping, mode switch and command floods | Higher-priority stop wins, state and output match approved bench stop policy |
| **VT-04** | FR-004 | NaN, inf, wrong schema, invalid mode, out-of-range angles/throttle | Invalid command rejected; no servo/setpoint mutation |
| **VT-05** | FR-005 | Source A active, B sends conflicting arm/steering/profile; try switching source | B cannot control without explicit ownership transition |
| **VT-06** | FR-006 | Duplicate/reordered/stale sequence, noise-only edges, malformed PPM/ESP-NOW | No refresh of validated-frame age; control authority not extended by noise |
| **VT-07** | FR-007 | Simulated lost link across DISARMED, ARMED, ACTIVE and decorative mode; advance virtual clock past provisional 500 ms | State-specific BENCH fault/stop; no bypass from a mode preset; no automatic rearm |
| **VT-08** | FR-008 | Fault + fresh command; UI command with DISARMED; invalid owner + valid waveform | Central supervisor rejects unauthorized actuation across all sources |
| **VT-09** | FR-009 | Replay identical command with virtual scheduling at 1, 2, 5, 10 ms | Same trajectory for same timestamps within stated algorithm tolerance |
| **VT-10** | FR-010 | Boundary combinations: max frequency, steer, trim, amplitude, opposite limits; non-finite config | Always within configured/measured servo envelope; no missed limit path |
| **VT-11** | FR-011 | Voltage normal/low/critical/ADC-unavailable, with hysteresis parameters | Correct fault/warning transitions; no silent disabling of monitor |
| **VT-12** | FR-012 | Restore valid control or voltage after fault without acknowledgment; then acknowledge and rearm safely | Motion stays disabled until explicit recovery prerequisites are met |
| **VT-13** | FR-013 | Execute identical scenario twice with virtual clock and seed | Identical state/events/CSV fields/angle traces; replay can reproduce fault |
| **VT-14** | FR-014 | Compare telemetry against internal state in normal/fault cases | All fields correct; simulated flag obvious |
| **VT-15** | FR-015 | UI sends unauthorized arm and mode command during fault | Backend refuses even if UI control is bypassed; UI displays reason |
| **VT-16** | FR-016 | Simultaneous heavy LED/web workload and actuator control | No alteration of safety state; measured timing target TBD before bench acceptance |
| **VT-17** | FR-017 | Competing RC/bench/web input while ARM/IN_FLIGHT | Physical RC sole flight owner; browser command rejected and reported |
| **VT-18** | FR-018 | Exercise each transmitter channel, arm switch, throttle/steering mapping, reverse and trim with props/wings detached | Correct RC mapping, neutral arm condition, explicit switch behavior and failsafe indicators |
| **VT-19** | FR-019 | G4 approved staged powered-flight test with video/log and owner-approved pass/fail thresholds | Real pilot-commanded flight response and controlled recovery/landing; thresholds TBD until airframe measured |
| **VT-20** | FR-020 | Inject link timeout and critical battery conditions across bench/rig simulation and G3; analyze flight cases | Flight-specific response documented and shown nonhazardous enough to authorize G4; not bench-stop-by-default |
| **VT-21** | FR-021 | Weigh all-up airframe; record CG, motor/servo load and wing force evidence | Reviewed mass, power and structural feasibility; engineering uncertainties quantified before G4 |
| **VT-22** | FR-022 | Try web/UI calibration/config write while ARMED/ACTIVE, including replayed command | Rejected, logged; only validated disarmed configuration changes possible |
| **VT-23** | FR-023 | Complete test log including transmitter/receiver/battery/wing revision, firmware commit, video | G4 report repeatable, passes agreed flight metrics or records failure |

## 4. Bench test checklist (design only — no energized hardware authorization)

- [ ] Obtain actual servo part numbers, max pulse range, stall current, torque, operating voltage and thermal specification.
- [ ] Measure source/regulator capacity at transient current; include reverse polarity/short protection as appropriate.
- [ ] Verify common ground, signal level and board GPIO suitability; document exact wiring schematic.
- [ ] Start with wings **disconnected**, protective physical constraints and a suitable current-limited supply.
- [ ] Verify power-on has no unexpected actuator movement; calibration only via deliberate operation.
- [ ] Confirm E-stop, stale link, unplugged receiver, malformed packets and reconnect are handled in each state.
- [ ] Identify mechanical travel limits with safety margin, record approved values per wing (do not assume 0°–180°).
- [ ] Log voltage under actuation and load; never rely on unspecified voltage cutoff to make flight safe.
- [ ] Stop if overheating, stall, brownout, structural bending or unexpected motion is observed.

## 5. Traceable test evidence template

```text
Test ID: VT-__ / Gate: G_
Result: NOT RUN | PASS | FAIL | BLOCKED
Environment: PC / bench / restrained
Build commit + config revision:
Hardware and supply (if any):
Procedure:
Expected:
Actual:
Log/video/CSV path:
Defect or deviation:
Reviewer and date:
```

## 6. Stop conditions

Any uncontrolled flap on boot, missing explicit disarm, unauthorized radio control, unstable power rail, suspected servo stall, mechanical contact, or unknown state requires **immediate stop of the bench experiment** and corrective design review. The recommended ground stop (disable/neutral) is **not** an approved free-flight recovery strategy.

## 7. Approval record

- V1 manual RC powered free-flight goal: OWNER CONFIRMED 2026-11-12; detailed plan approval: PENDING
- G0: NOT STARTED | G1: NOT RUN | G2–G4: NOT AUTHORIZED
- No `Task/` deliverable created before owner approves the relevant design revision.

## 8. Flight-acceptance definition (owner intent confirmed; numeric values TBD)

V1 may be declared COMPLETE only if G0–G3 have passed and the separately authorized G4 tests demonstrate all of the following in a controlled, recorded environment:

1. Physical RC transmitter controls start/arming and sustained powered flapping on the actual airframe.
2. Aircraft achieves real free-flight (not only suspended or pulled by tether) and responds predictably to a deliberate manual steering input.
3. Pilot can terminate/recover the flight in the pre-approved manner without unacceptable uncontrolled excursion or injury hazard.
4. A defined number of repeat trials, duration, steering response tolerance and acceptable landing condition are met; **all numeric thresholds TBD by measurements and separate owner design approval**, not invented here.
5. Link-loss, low-battery, site constraints and emergency procedures have been risk-reviewed and demonstrated insofar as possible before flight.

Results are **NOT RUN**; do not assert simulator/bench PASS implies free-flight capability. Autonomy is excluded from this acceptance criterion and deferred to V2.

*Changelog 2026-11-12 v0.2: added VT-17–VT-23 and reclassified G4 as V1 acceptance gate (still separately authorized).* 


## 9. Mechanics/force experiment traceability (v0.3)

Before declaring G3 complete or evaluating G4 authorization, consult `18_MECHANICAL_EXPERIMENT_PLAN.md` for:

| New ID | Existing coverage | Required additional evidence |
|---|---|---|
| MX-01…MX-02 | VT-21 | mass, CG and measured wing geometry |
| MX-03…MX-04 | VT-10, VT-11, VT-18 | real servo angle/pulse bounds, power transients and MCU resets |
| MX-05…MX-06 | VT-21 | actual flap frequency/amplitude under wing loading and early structural durability |
| MX-07…MX-08 | VT-19, VT-21 | calibrated force/moment and steering effect, with uncertainty |
| MX-09 | VT-20 | real receiver/power fault responses while restrained |
| MX-10 | VT-19, VT-23 | flight acceptance evidence, **only after separately authorized G4** |

**No MX tests have been run.** Load-cell force is an important screening metric but not a standalone substitute for free-flight proof, since rig constraint and inflow differ from actual flight.

*Changelog 2026-11-12 v0.3: MX traceability, no change to G0–G4 or owner approval policy.*

## 10. Electrical verification expansion (v0.4, PLANNED ONLY)

- `24_ELECTRICAL_BENCH_VERIFICATION.md`: EE-T01…EE-T15 augment G0/G2/G3. They do not rename or replace VT-01…VT-23 or MX-01…MX-10.
- `25_ELECTRICAL_HAZARD_REVIEW.md`: H-EE-01…H-EE-12 are **open** hazard findings. Electrical G2/G3 tests are not deemed PASS until their approved numeric limits and dated instrument evidence are supplied.
- G4 remains a separate flight-approval gate: free-flight failsafe and power recovery cannot be inferred from bench cutoff or a simulation.

*Changelog v0.4: electrical test traceability added; all tests still NOT RUN.*

## 11. Integration-safety additional test coverage (v0.5 — NOT RUN)

`29_REQUIREMENTS_INTEGRATION_TRACEABILITY.md` defines **IT-01…IT-06** and maps them across FR-001…FR-023 and NFR-001…NFR-011. These tests strengthen, not supersede, `VT-01…VT-23`, `MX-01…MX-10`, `EE-T01…EE-T15`. Core new cases: arm-held across boot/reset, UART-valid but RF-unhealthy, simultaneous faults/source conflicts, clock wrap, disallowed armed web reconfiguration, and airborne-contingency evidence review.

**Gate caution:** G1 passing a contingency simulation does not certify a G4 flight response. G4 remains expressly prohibited until separate flight-policy and site authorizations with G3 measured data. No test from this section has been executed.

*Changelog v0.5: integrate IT-01…IT-06 and prohibit G1→G4 inference.*

## 12. Pilot RC control and human-interface verification extension (v0.6 — PLANNED, NOT RUN)

`35_RC_CONTROL_VERIFICATION_MATRIX.md` defines detailed **PX-01–PX-20** and **UX-01–UX-08** tests supplementing existing VT/IT, not replacing them. The highest-risk examples are:

- PX-01/PX-20: radio and MCU arming stay independent; no arm if high at boot, mismatched CH5/ELRS mode, failed low→high edge or model swap.
- PX-02/03/18: verify the *actual* TX Inputs/Mixes/Outputs, channel monitor and serial-decoded mapping; never assume AETR/TAER or direction sign.
- PX-07/08: receiver can send serial frames while radio RF unhealthy; reject arming and log state appropriately.
- PX-05/15: no flight steering claim without measured left/right effort and restrained force/moment result.
- PX-06/11/12: in-flight profile and calibration changes rejected; profile does not bypass context.
- PX-16: flight-specific loss-of-link/disarm/low battery action is **still a G4 BLOCKER**.

Every result begins `NOT RUN`. Pilot UX results require safe configuration plus pilot observation notes; no test result is inferred from documents or video.

## 13. Phase 1.8 — Flight dynamics / control authority verification overlay (NOT RUN)

`37` defines the model and its assumptions, `38` defines the measurable `CA-01…CA-15` control-authority experiments, `39` defines the candidate mixer and fallback strategies, and `40` defines `FA-01…FA-12` final acceptance evidence. `41` records how this evidence affects the mechanical/control concept choice.

| Gate | Phase 1.8 acceptance intent | Present state |
|---|---|---|
| G0-A | approved input/frame/model-maturity semantics; clear labeling of assumed vs measured | PROPOSED; owner not yet approved |
| G1 | mixer sign/saturation tests, deterministic state and data-label propagation; kinematic simulator cannot predict flight | NOT RUN |
| G2 | actual wing/servo tracking/current/temperature, no-wing safe startup and validated envelope (`CA-02…04`) | NOT RUN; separate approval required |
| G3 | calibrated force/moment measurements and sign with uncertainty; cross-coupling, mechanical fatigue (`CA-05…15`) | NOT RUN; fixture and authorization needed |
| G4 | owner-approved `FA-01…12` with actual intentional RC-controlled free flight and recovery | **NO-GO** |

**Stop rule:** if important moment components cannot be measured reliably, classify their controllability `UNKNOWN`, not `PASS`. Only predeclared mass/force/moment/response and safety thresholds can be used for final stage decisions. A single vertical-load proxy or one simulated trajectory is not a flight result. Flight link-loss/disarm policy is still unresolved and **must not** be inferred from bench stop behavior.
