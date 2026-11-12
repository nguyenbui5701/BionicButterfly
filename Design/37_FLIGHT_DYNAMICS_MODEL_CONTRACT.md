# BionicButterfly — Flight Dynamics Model & Assumptions Contract

- **Document ID:** BB-DYN-037 | **Revision:** 0.1 | **Date:** 2026-11-12
- **Author/owner:** Solution Architect | **Status:** PROPOSED / MODEL UNIDENTIFIED
- **Product goal:** V1 actual RC-controlled free flight. V2 autonomous navigation explicitly excluded.
- **Cross-links:** `02`, `17`, `19`, `27`, `28`, `31–36`, `38–41`.

## 1. Design question and validity boundary

We must determine whether the two independent left/right wing actuators provide sufficient **average force**, **attitude behavior**, **directional authority**, and **pilot-recoverable response**. This contract describes a *model hierarchy*, **not an aircraft that has been built or validated**. The conceptual simulations do not establish stable free flight or qualify any flight-control gain.

Research context, not plug-in numerical parameters:
- **USTButterfly**: independent left/right servo drives, published climbing-flight observation; the exact wing, servo and mass differ from ours ([IEEE, DOI:10.1109/TIE.2023.3260355](https://doi.org/10.1109/TIE.2023.3260355)).
- **COLIBRI**: pitch/roll actively stabilized by wing-root control, yaw passively stable for its *own* airframe ([SAGE 2017](https://journals.sagepub.com/doi/full/10.1177/1756829317695563)).
- **2025 motor-driven flapper**: measured all three moment components but experimentally demonstrated roll/pitch feedback hover of about six seconds **without successful yaw control** ([Biomimetics 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12563709/)).
- The above do **not** prove that our two servo outputs can stabilize four independent flight variables.

## 2. Coordinate frames and observables

Choose conventions once and print them on fixtures and every dataset. **Candidate (must be confirmed with hardware drawing):** body frame `B`: x forward toward head, y right wing, z downward; right-hand rule for moments. Inertial frame `I`: z points upward. Positive right/left pilot steering is *logical intent*, not the same thing as positive body-yaw moment. Sensor's native frame must be transformed into `B` using a measured calibration transform `T_B_sensor`.

| State or quantity | Symbol, units | Required provenance |
|---|---|---|
| Body position, velocity | `p_I` m, `v_I` m/s | external tracker/video **only if measured**; `UNKNOWN` otherwise |
| Body attitude and angular velocity | `R_IB`, `omega_B` rad/s | IMU/optical tracker if installed and calibrated |
| Left/right flap command | `u_L`, `u_R` dimensionless normalized requested drive | post-supervisor AND pre-HAL request, tagged as *commanded* |
| Wing angles and wing stroke rate | `phi_L,phi_R` rad; `f_L,f_R` Hz | high-speed video/angle sensing, tagged *measured* |
| Mean aerodynamic body force & torque | `F_B` N, `M_B` N·m | instrumented rig with tare and dynamic-bias limits |
| CG and body inertia | `r_CG` m, `J_B` kg·m² | weighing/balancing/inertial estimation, revision-specific |
| Supply voltage/current and servo temperature | V, A, °C | sampled instruments, synchronized timestamps |

Do **not** label a wing-command sine wave as a measured wing trajectory; do **not** label load-cell `F_z` as aircraft vertical force until frame projection, mounting loads, inertial artifacts and calibration are addressed.

## 3. Governing 6-DOF equations (conceptual)

For a rigid-body *cycle-averaged* approximation, before accounting for flexible-wing vibration explicitly:

\[
 m\dot{v}_I = R_{IB}\,\bar{F}_B + m\,g_I + F_{external,I},
 \qquad \dot{p}_I=v_I
\]

\[
 J_B\dot{\omega}_B + \omega_B\times(J_B\omega_B)=\bar{M}_B + M_{external,B},
 \qquad \dot{R}_{IB}=R_{IB}[\omega_B]_\times
\]

- `R_IB`: rotation from body to inertial. `g_I` points downward. `F_B` includes *aerodynamic* contributions (thrust/lift definitions depend on orientation and velocity), **not gravity again**.
- Cycle average `\bar{F},\bar{M}` depends on stroke variables, wing flexibility, body attitude/rate, relative wind `v_air`, and geometry. It is not a constant linear mapping; e.g. `\bar{F}_B = f_F(x,u_L,u_R;\theta)`.
- If the aircraft changes attitude significantly during a stroke, a cycle-averaged model can miss dynamics. The *wing-resolved* model is a later option once data warrants it; do not use unvalidated CFD as a substitute for measured force.
- Static laboratory vertical-force reading is **not** a direct in-air lift estimate during turning/translating flight.

### 3.1 Necessary force budget, *not sufficient proof of flight*

Gravity reference `g=9.81 m/s²`:

| Scenario | **Design-budget mass** | Gravity force | Meaning |
|---|---:|---:|---|
| C0, no LED | 70 g | 0.6867 N | hypothetical threshold for a body vertical force component in steady level-flight |
| C1, LED | 82 g | 0.8044 N | same gravity arithmetic; LED changes inertia & servo load too |

**No numeric thrust margin is approved.** At an assumed nearly-level quasi-steady condition with no other vertical supports, mean inertial vertical force must balance weight. Such a balance alone cannot establish climb, stability, yaw control, safety or duration. The true hardware mass will replace 70/82 g before accepting any measurement-based comparison.

## 4. Inputs, authority and local sensitivity

Define the control variables using *measured actuator motion* where possible:

\[
 u_c=(u_L+u_R)/2,\quad u_d=(u_R-u_L)/2,\quad
 u_L=u_c-u_d,\quad u_R=u_c+u_d.
\]

A candidate local empirical map at a fixed operating condition `x0, uc0, ud0`:

\[
 \Delta y\approx B(x_0,u_0)\,\begin{bmatrix}\Delta u_c\\\Delta u_d\end{bmatrix},\qquad
 y=\begin{bmatrix}\bar F_{z} & \bar M_x & \bar M_y & \bar M_z\end{bmatrix}^{T},\quad
 B\in\mathbb{R}^{4\times2}.
\]

`rank(B) <= 2`: **two instantaneous independent command dimensions cannot arbitrarily set four independent force/moment objectives**. But a system with passive restoring dynamics, fixed aerodynamic coupling, changing flight speed, and skilled/manual feedback **can sometimes be flyable despite underactuation**. Rank alone cannot prove impossibility or success. This is why each moment sign, coupling and dynamic response must be measured.

**Critical:** the sign of `\partial M_z/\partial u_d` (or heading response) is **UNKNOWN** until tested. Do not configure transmitter reversal based on visual left/right wing motion alone. `B` also changes with common flap level, battery voltage, speed and body orientation; a one-point `B` is not a universal flight model.

## 5. Aerodynamic vs inertial observations

Six-axis load-cell outputs contain fixture dynamics and wing inertial reaction as well as aerodynamic loads. Required experimental mitigations:

1. Zero/tare the mounted rig; record sensor axes, sensor-to-CG lever arm and sensor bandwidth.
2. Sample time histories across *many* wing cycles, not just a single peak reading; store raw and filtered traces.
3. Run controlled zero-flap, fixed-wing and mechanical-background baselines as *diagnostics*; **do not assume simple subtraction isolates aerodynamics** when modifying the wings changes inertial loading.
4. Inspect frequency spectra and measurement resonance; reject trials where rig vibration or sensor clipping dominates.
5. Use a time-synchronized motion record and phase marking; report mean, cycle variance and systematic bias range. Document airflow (stationary/forward flow), orientation and nearby surfaces.
6. Repeat tests after any mechanical revision. Treat measured mean force from a restraining fixture as a force proxy with stated uncertainty, not a guaranteed free-flight net force.

## 6. Model maturity levels

| Level | Input available | Outputs we may claim | What cannot be claimed |
|---|---|---|---|
| **D0 geometry-only** | assumed mass, wing shape, two control scalars | gravity budget, kinematics envelope, hypotheses | lift, speed, stable flight |
| **D1 wing-actuation bench** | G2 measured servo angles, speed, current | actuator tracking and repeatability | actual aerodynamic force or turning |
| **D2 restrained instrumented rig** | G3 synchronized force/moment + actual motion | local force/moment trends and uncertainty | validated free-flight stability |
| **D3 qualified dynamics** | D2 plus approved limited-flight observation and instrumentation | locally validated dynamics and manual response within measured envelope | V2 autonomous capability or operation outside envelope |

At present **D0 only** (analytical concepts; even actual mass is unmeasured). No `D1–D3` results exist. SIM may contain `SIM_ASSUMED` parameters, but they must never silently flow into `FLIGHT_APPROVED` profiles.

## 7. Simulation schema (interface only; NO code task)

```yaml
model_revision: "D0-PROPOSED"
frame_convention: "B_x_forward_y_right_z_down; I_z_up"
mode: "KINEMATIC_ONLY"                 # D0; not truthful as 6DOF prediction
mass_kg: null                         # measured required for D2+
center_of_gravity_m: null
inertia_kg_m2: null
control_matrix: null                  # 4x2 measured, frame/trim dependent
parameter_status: "UNMEASURED"
validated_envelope: null
experiment_ids: []
provenance: "concept-design-only"
```

A separate `D1/D2` dataset can populate measured values **only after human review**. Separate a *visual preview simulator* from any physically predictive 6DOF simulator in UI labels and outputs.

## 8. Measurable exit conditions

- **D0 exit:** units/frame/signal definitions, source evidence plan, input limitations and failure modes peer-reviewed.
- **D1 exit:** repeatable measured linkage/stroke/current at multiple command points with bounded uncertainty and no unacceptable mechanical/power issues.
- **D2 exit:** reproducible body-frame load/moment responses and credible measurement uncertainty for both `u_c`, `u_d`; characterize saturation/cross-coupling. If authority cannot be measured reliably, stay at D1.
- **D3 exit:** separate G4 authorization; qualified real-flight evidence needed. Neither D2 nor a high modeled lift number authorizes flight.

**All numerical acceptance thresholds remain TBD**, to be approved *before* running acceptance experiments. See `38` and `40`.
