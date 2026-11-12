# BionicButterfly — V1 Flapping-Wing Controllability & Flight Feasibility

- **Document ID:** BB-FLIGHT-031 | **Version:** 0.1 | **Date:** 2026-11-12
- **Status:** PROPOSED, analytical questions only; no aircraft measurements or flight authorization.
- **Target:** free flight under physical RC pilot. V1 may include *bounded stability assistance* only if owner explicitly approves; navigation/autonomous position control belongs to V2.

## 1. Critical distinction: flap motion, lift, trim and stable control

A servo following an angle sinusoid is an actuator demonstration, **not evidence of generated net upward force, useful moment or stable free flight**. A wing can be strong enough to lift a restrained rig yet have inadequate directional authority or unstable passive pitch/roll in the air.

For any all-up mass `m`, weight is `W=m×g` where `g≈9.81 m/s²`. A **necessary** level-flight condition in an appropriate coordinate/frame is sustained average vertical aerodynamic force `F_z,mean >= W`; realistic climbing, turning and disturbance recovery require reserve, but no arbitrary reserve number is approved. Bench thrust reading alone cannot capture flight velocity, body attitude and unsteady wing-body coupling.

If `m = 70 g` as a **design budget**, `W ≈ 0.687 N`, and if `m = 82 g`, `W ≈ 0.804 N`. These are theoretical gravity loads only, **not measured lift or success criteria**. C1 LED introduces inertia changes as well as extra grams.

## 2. How many independent controls exist?

For two wing drives, idealized commands can be decomposed into:

- Common mode: `(left + right)/2`, largely changes symmetric stroke demand / potential net aerodynamic load.
- Differential mode: `(left − right)/2`, can induce a roll/yaw/pitch couple depending on wing kinematics and aerodynamic interactions.

**Two independent actuator commands cannot generically command three independent rotational axes plus altitude at once.** Whether passive stability, coupling and pilot skill make this practical is an empirical aircraft-specific question. A butterfly-shaped planform, lightweight flexible wings, battery CG and linkage phase can affect stability strongly. Turning one side harder does **not** guarantee a controllable heading turn.

Potential routes if C0 fails control tests: revise linkage geometry / wing root angle, add passive stabilization (tail/dihedral/mass distribution), introduce another actuator, or consider a small IMU-based *attitude stabilization aid* **without** initiating V2 GPS/waypoint autonomy. Each route changes weight, cost and architecture; requires a design ADR and owner approval.

## 3. Phenomena to measure (not assume)

| Phenomenon | Experiment / evidence | Failure implication |
|---|---|---|
| Servo tracking under wing load | command angle vs high-speed wing angle; frequency, stroke, phase lag and power | if amplitude collapses at demanded rate, motor sizing/mechanism must change |
| Mean vertical force vs frequency and wing geometry | instrumented restrained rig force measurement over many flap cycles | if insufficient vs all-up weight, reduce mass or redesign aerodynamics |
| Moment response to differential stroke | multi-axis force/torque measurement if equipment permits; compare left/right configurations | direction mapping unknown; RC yaw may reverse or produce roll |
| CG and inertial properties | scale and balance fixture; measure x/y/z CG and left/right asymmetry; quantify wing mass distribution | trim changes, passive instability, actuator peak load |
| Power and heat | voltage/current transient, servo case temperature and load cycling | brownout or servo failure before flight duration |
| Fatigue and structural modes | inspect hinge, pushrod, wing root, delamination after restrained cycles | unstable/unsafe airframe even if static load passes |
| Pitch/roll behavior | guarded restraint and owner-approved controlled flight observations at G4; external tracking if feasible | two-drive manual control may not be sufficient |
| Pilot directional control | synchronized physical RC commands, external video, observable aircraft path | required V1 steering behavior not met |
| Link loss and low power | G3 fault exercises + flight hazard review before G4 | cannot publish usable emergency plan from bench alone |

## 4. Mechanical reference configuration and evidence tables

**C0**, no LEDs: estimate budget 70 g, two symmetric wing assemblies, servo/wing angles calibrated separately, battery on adjustable longitudinal mount. **C1**, LED: estimated 82 g and a fresh design verification cycle. Neither is an agreed flight-ready total weight. The `M1` two-servo concept is a **candidate**, not an accepted mechanical drawing.

Proposed experiment worksheet (fill with actual measurements):

| Field | Unit | Evidence source | Value |
|---|---|---|---|
| all-up mass C0 (charged battery, harness, RX antenna) | g | scale record + photo | TBD |
| left/right wing mass | g | scale | TBD/TBD |
| full airframe CG relative to wing root reference | mm x/y/z | CG fixture | TBD |
| servo model + measured link travel | model / deg | G2 servo measurement | TBD |
| servo electrical power and current peaks | W, A | G2/G3 power logs | TBD |
| flapping mechanical rate and stroke | Hz, degree | high-speed video | TBD |
| mean vertical force over N cycles | N | calibrated rig | TBD |
| direction-coupled moment under differential command | N·m | multidimensional rig or qualified method | TBD |
| roll/pitch stability evidence | mode-specific metrics | G3/G4 observation (not assumed) | TBD |
| radio loss response | response+latency | G3 and reviewed policy | TBD |
| V1 controlled free-flight outcome | video/log and criteria | G4 after approvals | NOT RUN |

## 5. Preliminary flight experiment protocol (design only)

1. Freeze exact C0 revision: all mass/CG/wing/servo/receiver/pin/battery/firmware/config versions. Prohibit structural or tuning changes without re-recording them.
2. Complete G1 simulation plus G2 electrical and G3 safeguarded wing-rig tests. Confirm no brownout, no unintended actuation, mechanical clearance, and measured force/deflection consistency.
3. SA/owner review: flight hazards including loss of lift, uncontrolled yaw/roll, dropped battery, hinge failure, RF loss, spectators/property; define site boundaries, recovery gear and pilot plan.
4. Define **quantified acceptance criteria before flight**: time aloft (if relevant), height/space boundaries, operator-commanded directional response, landing/recovery conditions, allowed weather/wind, log/video requirement; no post-hoc invented success metric.
5. G4 only after **separate explicit owner permission**, applicable site permissions and safety review. Record observed outcome with traceable evidence; if unstable/uncontrollable, stop further launches and revisit concept.

No specific unsupervised launch, tether release, emergency flight maneuver or automatic radio-loss motion is being recommended here.

## 6. Flight gate conclusion

**G4 = NO-GO** today because m, geometry, actuators, aerodynamic force/moments, RC link contingency, pilot/site setup and injury/property risk controls remain unverified. For V1 completion, a mere “it flapped” or “it briefly left the table” is inadequate: owner-defined evidence must show deliberate RC-controlled flight and recovery.

## 7. Source and analysis notes

- Engineering framework: Newtonian force balance and independent control-actuator reasoning, not claims of specific published robot performance.
- Official board/receiver constraints elsewhere: [Seeed XIAO](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/), [ExpressLRS Wiring](https://www.expresslrs.org/quick-start/receivers/wiring-up/), [Espressif LEDC](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-reference/peripherals/ledc.html).
- All analytical claims are conceptual until verified on the actual airframe. No reference 3D files or copyrighted designs are included.

## 8. Phase 1.8 Integration Addendum — measured control authority (2026-11-12)

- Canonical 6-DOF model maturity, axis definitions and `B ∈ R^(4×2)` **local** sensitivity: `37_FLIGHT_DYNAMICS_MODEL_CONTRACT.md`.
- Instrumentation plan, uncertainty, derivative signs, evidence `CA-01…CA-15`: `38_CONTROL_AUTHORITY_IDENTIFICATION_PLAN.md`.
- Candidate manual control S0 and optional passive/IMU/added-DOF branches: `39_V1_MANUAL_FLIGHT_CONTROL_STRATEGY.md`.
- Final free-flight acceptance requires `FA-01…FA-12`, not merely positive lift proxy: `40_FLIGHT_VALIDATION_AND_EVIDENCE_STANDARD.md`.
- Owner-gated alternatives and decision D-037…D-043: `41_CONTROL_ARCHITECTURE_TRADE_STUDY.md`.

**Refined risk statement:** underactuation (`rank(B) ≤ 2`) does *not* mathematically forbid flight with passive stability or coupled dynamics; it **does** forbid assuming four independent force/moment objectives can be set arbitrarily at a single trim point. The actual moment signs and recovery authority remain unknown. Positive average fixed-rig vertical force, even larger than assumed weight, is neither enough to certify flyability nor directional control. G4 remains **NO-GO**; no sensor/servo/airframe test has been conducted or authorized.
