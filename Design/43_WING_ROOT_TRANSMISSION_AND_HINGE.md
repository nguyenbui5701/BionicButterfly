# BionicButterfly — Wing Root, Transmission, Hinge & Actuator Integration

- **ID:** BB-MECH-043 | **Rev:** 0.1 | **Owner:** Solution Architect | **Status:** PROPOSED / NOT VERIFIED
- **Inputs:** `17`, `19–21`, `37–42`; V1 manual RC, C0 first. Do not select a final actuator based on stall-torque marketing alone.

## 1. Mechanism options assessed

| Option | Load path / degrees of freedom | Expected benefit | Critical risk and proof needed | Current state |
|---|---|---|---|---|
| **A — servo output drives wing root** | Servo shaft → coupler → root; L/R independent | minimal parts, lower linkage backlash | servo output bearing takes wing bending/inertia; spline play; thermal duty; requires **vendor-approved reaction load** | CANDIDATE only |
| **B — servo horn + pushrod + supported wing pivot** | Servo → horn → pushrod → pivot arm, separate supported root | separate bending loads, geometry can tune mechanical advantage | added mass/friction, dead center, rod buckling, geometry nonlinearity/overconstraint | **Preferred CAD trade-study**, not proven |
| **C — twin crank motor transmission** | motor/gear/crank(s) → L/R wings | frequency/duty potentially favorable | much greater redesign, loss of independent wing parameters unless two drives/actuated differential | FALLBACK if A/B fail |

**Reason for preferring B for CAD comparison:** separation of radial/axial loads makes test instrumentation and replacement easier, but whether it is lighter or more efficient than A is unknown. Design both to compare **measured total mass, energy per cycle, stroke tracking, and failure behavior**.

## 2. Functional requirement of a wing root

A wing root shall: (i) transmit commanded stroke torque; (ii) react transverse/bending loads through a specified pivot/bearing structure; (iii) preserve the intended DOF (flap, optionally passive pitch); (iv) mechanically limit collision-causing overtravel independent of firmware; (v) allow inspection and replacement; and (vi) fail predictably on an unpowered bench (not a promised in-air safe landing).

Separate active **flap hinge** from optional passive **pitch hinge** and from flexible wing membrane torsion. They are not interchangeable. An over-constrained single hinge can prevent passive pitching, while an unrestrained pitch hinge can produce flutter or reversal outside the expected phase.

## 3. Parametric linkage kinematics: do not assume linear servo→wing mapping

For option B define: servo output center `S`, servo horn pin radius `r_s`, wing pivot `H`, wing crank pin radius `r_w`, pin-to-pin link length `L`, servo horn angle `theta_s`, wing root angle `theta_w`. Positions in **one planar projection** only if verified coplanar:

```
P_s(theta_s) = S + r_s * [cos(theta_s), sin(theta_s)]
P_w(theta_w) = H + r_w * [cos(theta_w), sin(theta_w)]
constraint: |P_s - P_w|^2 = L^2
```

The constraint can have multiple assembly branches and dead-center positions. In actual 3D geometry, use full coordinates/joint types and solve numerically across the proposed full stroke. At each pose log `theta_w(theta_s)` and sensitivity `d theta_w / d theta_s`; near singularity, mechanical advantage and force requirements can diverge. Soft limits may not protect if the linkage is assembled on the wrong branch.

**Firmware interface:** servo electrical command `[µs]` → measured servo shaft `[deg]` → calibrated wing root `[deg]`, potentially nonlinear and different L/R. Calibration map has mechanical revision, direction, fit residual and valid range. No arbitrary inversion based on 'left visually looks reversed'.

## 4. Inertial and torque scaling — illustrative calculation only

A per-side concept with a uniform slender radial wing of **5 g and 0.30 m** (purely hypothetical, not an actual manufactured wing) has:

`J_root ≈ m R² / 3 = 0.005×0.30²/3 = 1.5e−4 kg·m²`.

If physical flap angle is `theta_w(t) = A sin(2πft)` with an **assumed** amplitude `A=30°=0.524 rad`, `f=3 Hz`:

- `alpha_peak = A (2πf)² ≈ 186 rad/s²`.
- **Wing inertial torque alone**, with this simplified mass distribution, is approximately `J alpha_peak ≈ 0.028 N·m` at hinge (**not a servo torque rating**).

The real wing is not a slender uniform rod; servo-gear inertia, bending, elastic return, aerodynamic torque, transmission efficiency, losses and phase all change the load. Compute the required **servo** torque using the complete linkage Jacobian, validated by current, temperature, and actual waveform tracking. Never compare this `0.028 N·m` directly with datasheet *stall torque* to approve a flight drive.

## 5. Symmetry is a measured attribute

- Make left/right CAD mirrored, but maintain **separate** geometry, mass, center-of-mass and calibration records.
- Examine the servo-neutral and mechanical pitch phases at the same physical wing phase; optical recordings are needed to verify symmetry.
- Log `delta_f`, `delta_amplitude`, root-backlash, and drivetrain current under common command. A commanded zero steering differential does not guarantee zero yaw/roll moments.
- Test the entire coupled wing arrangement including passive rear lobes **without assuming** that four visible lobes = four actuators.

## 6. Mechanical fail modes and controls

| Failure / trigger | Detection | Design safeguard / stop criterion |
|---|---|---|
| Stroke hard-stop impact | high-speed video, noise, spikes in current | revise limit/sweep; no powered rig until all static clearances pass |
| Pushrod end binding/dead center | CAD sweep, manual movement unpowered | redesign pivot/horn geometry; reject kinematic singularity within qualified range |
| Wing-root looseness/backlash | indicator or video reference marks | record measured magnitude; rework if it changes repeatability or sign |
| Servo thermal overload | case temperature + current & speed sag | stop per actual part datasheet, identify load envelope; never invent a universal temp limit |
| Broken wing spar/membrane tear | pre/post close-up and crack inspection | discard damaged wing; do not patch then call it same revision without requalification |
| Linkage throws joint/horn | visual marks, captive retention inspection | fail review, add positive retention/compatible fastener method |
| Passive twist instability | phase-resolved video, force oscillation | change hinge stiffness/ribs; treat as new mechanical revision |
| Unpowered wing drops into wires | unpowered full-sweep gravity orientation | reroute, guard, or redesign; bench cut-power is not flight failsafe |

## 7. Proposed physical drawings / acceptance

- `A-001` root hinge bearing/pivot section; `A-002` servo mount envelope; `A-003` horn+pushrod option; `A-004` fore/rear wing coupling; `A-005` wiring motion-envelope.
- All drawings must show actual part revision, material, dimensions, fit requirements, assembly order and inspection features before release.
- Bench evidence: angle map at low/medium/high permitted commands; full slow unpowered sweep; high-frame-rate under load; servo rail current/sag; wing-root wear after cycles; repeatability on both sides. All **NOT RUN**.

Research: [Festo wing-root/rear-wing hinged arrangement](https://www.festo.com/PDF_Flip/corp/Festo_eMotionButterflies/en/index.htm), [mechanical review of hovering flappers](https://link.springer.com/article/10.1007/s42235-021-00118-4), [overview of flapping mechanisms](https://doi.org/10.3390/aerospace10060554).
