# BionicButterfly — Control Authority & System Identification Plan

- **Document ID:** BB-EXP-038 | **Revision:** 0.1 | **Date:** 2026-11-12
- **Status:** PROPOSED / ALL TESTS NOT RUN
- **Scope:** design of low-risk measurement steps to resolve force/moment controllability; this is **not permission to energize a flight-capable prototype**.
- **Prerequisites:** `18` mechanics, `22–25` power hazards, `27` supervisor, `31`, `37`; owner-approved G2/G3 safety fixture.

## 1. What is to be identified

At each approved operating condition `q=(wing geometry, CG, supply V, u_c, airspeed/orientation, flap frequency)` establish:

- Actual left/right stroke amplitude, phase, lag and flapping frequency vs commands, **not only ideal servo PWM**.
- Long-window mean force vector `F_B` and moments `M_B` *referenced to CG*, including uncertainty and sign.
- Empirical derivatives `\partial \bar F_z/\partial u_c`, `\partial \bar M_x/\partial u_d`, `\partial \bar M_y/\partial u_d`, `\partial \bar M_z/\partial u_d`, and off-diagonal coupling.
- Voltage sensitivity, hysteresis and whether differential command reduces total useful vertical force.
- Integrity: repeated-trial variation, sensor bias, structure fatigue, receiver delays; which results are not identifiable with the available rig.

Do not relabel a roll-moment change as yaw control or claim yaw based on asymmetrically moving wings.

## 2. Fixture concepts and instrumentation tiers

| Tier | Instrument arrangement | Evidence can support | Limitation |
|---|---|---|---|
| M0 | calibrated scale, mass/CG jig, high-speed phone recording, power/current monitor | mass, CG, wing motion, duty, thermal trend | not aerodynamic force/moment |
| M1 | rigid but vibration-characterized mount and **calibrated single-axis force sensor** | **one sensor-axis** force trend under defined orientation | no independent pitch/roll/yaw torque; sensor mount can bias data |
| M2 | load cell(s) with known separation/lever arms or **calibrated six-axis force–torque sensor** | torque components/force vector supported by actual calibration | no CFD surrogate, costs more; cross-axis errors require calibration |
| M3 | M2 plus synchronized calibrated optical motion tracking/IMU and permitted controlled-flow measurements | stronger dynamic identification and body motion correlations | not a substitute for free-flight G4 or in-air contingency qualification |

For a lever-arm fixture, compute moment from each independently measured force in its own direction, using **known geometry** and proper sign; never infer unmeasured torque axes. Check structural stiffness, resonance and sensor saturation. A cheap hanging load cell can be a **force proxy**, but is not by itself proof of lift or 3-axis control.

## 3. Controlled test-variable plan

| Variable | Approach | Why |
|---|---|---|
| Wing geometry | freeze an exact CAD/physical revision for each run block | avoid mixing elastic/area effects |
| Battery rail voltage | record under load; repeat at approved representative safe levels | servo force changes with power |
| Common drive `u_c` | sample low, medium and candidate high values **within a validated G2 envelope** | detect nonlinear force/power relationship |
| Differential drive `u_d` | test both positive and negative levels, including zero; hold actual `u_c` when feasible | distinguish sign, asymmetry, coupling |
| Servo strokes | record true angles/synchronization | output power ≠ commanded input |
| CG and frame tilt | freeze, then change **one measured variable at a time** | torque and vertical projection change |
| Wind/airspeed | record ambient; controlled-flow studies only if safe facility exists | force map may change with flight speed |

Every grid point must be limited by *measured mechanical/electrical limits*. None of the example words low/medium/high define a numeric command or authorize full-stroke power-up.

## 4. Force/moment derivative method

At fixed `u_c=u0` and operating condition, measure triplicate or preapproved count of corrected cycle means at `u_d=-d,0,+d`:

\[
 \widehat{\frac{\partial y}{\partial u_d}}(u_0)
 =\frac{\bar y(u_0,+d)-\bar y(u_0,-d)}{2d},
 \quad y=[F_z,M_x,M_y,M_z]^T.
\]

Similarly perturb common demand around the same operating condition and estimate `\partial y/\partial u_c`. `d` is a **future approved** perturbation small enough to avoid new saturation or collision, yet larger than sensor resolution. Test multiple `u_c` values to expose nonlinearity. Fit both direct and cross-axis effects; provide residuals and trial-to-trial variability. Partial derivatives are **local** and should be tagged with fixture version/voltage/ambient air.

**Measurement quality:** use calibration check before/after, clipped sample detection, predeclared averaging window and confidence intervals or an equivalent uncertainty model with systematic biases reported separately. For a preliminary *sign* classification, an interval that clearly excludes zero is stronger than a mean alone, but still cannot prove flight stability. If confidence interval overlaps zero or repeat sign reverses, mark `INCONCLUSIVE`, not PASS.

## 5. Test inventory — all results NOT RUN

| ID | Gate | Intended evidence | Design exit / hard stop |
|---|---|---|---|
| **CA-01** | G0 | frame & CG definitions, sensor calibration plan | no undefined axis/sign |
| **CA-02** | G2 | unloaded vs loaded servo angle response | abort if physical endpoint collision/current excess |
| **CA-03** | G2 | power waveform & brownout sensitivity | no unsafe transients; numerical limits TBD |
| **CA-04** | G2 | left/right wing synchronization at one verified safe input | quantify asymmetry; no assumption both servos identical |
| **CA-05** | G3 | force sensor calibration / tare / resonance | reject underresolved / clipped data |
| **CA-06** | G3 | mean `F_B` at multiple `u_c` | force proxy with units & uncertainty |
| **CA-07** | G3 | repeat `u_d=-d,0,+d` at fixed `u_c` | identify sign and cross-coupling |
| **CA-08** | G3 | measured `M_x` roll response | NOT MEASURABLE if no torque-capable fixture |
| **CA-09** | G3 | measured `M_y` pitch response | NOT MEASURABLE if no torque-capable fixture |
| **CA-10** | G3 | measured `M_z` yaw response | NOT MEASURABLE if no torque-capable fixture |
| **CA-11** | G3 | force loss under differential steering | identify lift–turn tradeoff |
| **CA-12** | G3 | rail voltage/power and thermal drift | repeat after safe dwell and cooling |
| **CA-13** | G3 | trial repeats, sensor/fixture hysteresis | characterize repeatability and sign uncertainty |
| **CA-14** | G3 | structural deformation/fatigue inspections | any crack/loose linkage blocks continuation |
| **CA-15** | G0/G3 | cross-review experimental fit & limitations | no G4 on invalid model or unreviewed data |

**No deliberate radio loss while airborne is part of these tests.** In-air contingencies remain a separate G4 hazard and approval blocker.

## 6. Sample dataset contract

`CA-xx` record must include: `timestamp_ns`, `test_id`, `gate`, `airframe_rev`, `mechanism_rev`, `sensor_rev`, `calibration_rev`, `command_profile_hash`, `software_commit`, `u_c_requested`, `u_d_requested`, `u_L_requested`, `u_R_requested`, `phi_L_measured`, `phi_R_measured`, `f_flap_measured_hz`, `sensor_force_raw_N[3]`, `sensor_moment_raw_Nm[3]` (use null if not measured), `force_body_N[3]` or null, `moment_body_Nm[3]` or null, `supply_V`, `supply_A`, `sample_clock`, `quality_flags`, `environment`, `operator`, `reviewer`.

Use null for physically unobservable data; do not fill with model predictions in raw sensor fields. Store original time series and calibration files; summaries contain evidence links and independently checkable calculations. Every test begins `NOT RUN`.

## 7. Predeclared decision rules (without fabricated numbers)

- At G3, **insufficient mean measured vertical aerodynamic contribution**, within uncertainty and tested conditions, triggers an aero/weight/actuation redesign discussion — **not an unsafe attempt to prove lift in free flight**.
- If a candidate steering derivative has wrong/unstable sign across the required operating region or simultaneously destroys needed vertical force, the initial two-axis pilot mixer is not approved for G4.
- If important moments cannot be measured with the available fixture, the steering claim remains **UNKNOWN** and G4 remains blocked; do not silently mark it passed.
- Numeric mass budget, required force reserve, actuator rate and control authority thresholds must be pre-approved **from calibrated capability and flight-test scope**, not inserted after observing a favorable run.
- Any overheating, cracking, unexpected actuation or unexplained RF/servo behavior is an immediate stop-and-review event under `18`, `24`, `25`.

## 8. Authority evidence worksheet

| Operating point | `dFz/duc` | `dMx/dud` | `dMy/dud` | `dMz/dud` | Steering sign | Confidence/bias | Judgement |
|---|---|---|---|---|---|---|---|
| Safe common drive A | TBD | TBD | TBD | TBD | UNKNOWN | UNKNOWN | NOT RUN |
| Safe common drive B | TBD | TBD | TBD | TBD | UNKNOWN | UNKNOWN | NOT RUN |
| Safe common drive C | TBD | TBD | TBD | TBD | UNKNOWN | UNKNOWN | NOT RUN |

No data have been measured; all results and judgements are placeholders.
