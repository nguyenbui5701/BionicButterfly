# BionicButterfly — CAD Datum, Assembly & Interface Contract

- **ID:** BB-CAD-042 | **Rev:** 0.1 | **Date:** 2026-11-12 | **Owner:** Solution Architect
- **Status:** PROPOSED / PARAMETRIC STUDY / NOT FOR FABRICATION
- **Scope:** C0 no-LED, M1 two independently driven left/right wing assemblies; physical manual-RC V1. C1 LED is a separate revision.
- **Prerequisites:** `19_MECHANICAL_CONCEPT_DESIGN.md`, `20_PRELIMINARY_BOM_MASS_POWER.md`, `37_FLIGHT_DYNAMICS_MODEL_CONTRACT.md`, `38_CONTROL_AUTHORITY_IDENTIFICATION_PLAN.md`, `41_CONTROL_ARCHITECTURE_TRADE_STUDY.md`.

## 1. One coordinate contract (resolves an actual conflict)

**Conflict MECH-001:** previous `19` said body `+Z UP` while `37` said body `+Z DOWN`. This revision adopts the **right-handed body frame B** from `37`:

- `+X_B`: toward the butterfly head (forward); `+Y_B`: toward the **right wing**; `+Z_B`: **downward**. `X_B × Y_B = Z_B`.
- Inertial `I` has `+Z_I` upward, as in `37`. The gravity vector in `B` points to positive `Z_B` when body level; do not swap body and inertial vectors without the attitude transform.
- `O_B`: body structural datum **at the intersection of the aircraft longitudinal centerplane and the proposed wing-root hinge axis reference**; this datum is fixed to the airframe and is NOT automatically the CG.
- `H_L/H_R`: physical wing root pivots measured from `O_B`; use full 3D signed coordinates `r_BH_L`, `r_BH_R`, not an unlabelled scalar distance.
- Measured/estimated CG `r_BCG` is distinct from CAD origin `O_B`. Every force/moment report names its reference point; convert as `M_at_CG = M_at_O - (r_CG - r_O) × F` with identical axis definitions.
- Define a distinct wing hinge angle `phi_L`, `phi_R` via **physical marker orientation and a measured zero**; do NOT equate raw servo electrical angle, horn angle or mirrored PWM with physical flap sign.
- Each rig sensor has its own coordinate frame `S` and a measured `R_BS`, lever-arm offset and calibrated polarity. Log conversions, not simply `F_z` without frame.

**Pass criterion:** CAD, pinout drawings, test-fixture drawings, labels and log schema explicitly show this convention and a sign-check procedure. The sign of pilot steering remains unapproved until measured.

## 2. Parametric CAD master register — no fictitious cut dimensions

All parameters below require revision control and units. Values in `study_range` are just concept envelopes. Never use study bounds as manufacturing drawings.

| Parameter | Unit | Meaning | Current source/status |
|---|---|---|---|
| `span_total` | mm | tip-to-tip extended planform span | study 500–700 mm; **UNSELECTED** |
| `root_L_B`, `root_R_B` | 3×mm | pivot axis origin in body frame | TBD from servo+hinge CAD |
| `hinge_axis_L_B`, `hinge_axis_R_B` | unit vectors | 3D pivot axis direction | TBD; match root fasteners and both CAD coordinate frames |
| `wing_halfspan_L/R` | mm | pivot to farthest tip | TBD, measured on assembly |
| `wing_area_L/R` | mm² | flat/projected reference area with convention | TBD; record exactly which planform is counted |
| `chord_root`, `chord_mid`, `chord_tip` | mm | wing shape control stations | TBD from independent SVG/parametric sketch |
| `theta_stroke_min/max` | deg | **measured** physical wing stroke relative to body datum | TBD based on fixture clearance and linkage sweep |
| `phi_passive_limit` | deg | allowed passive wing pitch/twist at hinge | TBD; if none, write `NONE` |
| `horn_radius_L/R` | mm | servo horn effective lever radius | part-specific TBD |
| `linkage_length_L/R` | mm | pin-to-pin distance including ball joints | option-specific TBD |
| `hinge_to_actuator_axis` | 3×mm | relative servo output / wing pivot centers | option-specific TBD |
| `min_clearance` | mm | clearance under static + worst dynamic/deflection envelope | **TBD AFTER MATERIAL/FAB METHOD** |
| `body_clearance_wire` | mm | wire-to-moving-part clearance under all poses | **TBD** |
| `battery_track_length` | mm | longitudinal adjustment range for measured CG | TBD after actual battery dimensions |
| `mount_pattern_*` | mm | attachment hole patterns by exact part revision | TBD, vendor drawing + measured part |
| `mass_each/CG_each` | g, 3×mm | weighed actual component incl connectors/harness | NOT MEASURED |
| `J_wing_root_L/R` | kg·m² | rotational inertia about each actual hinge | NOT MEASURED / can estimate with stated assumptions |

A numeric dimension may enter **CAD-PROVISIONAL** only with a source (`measured part`, `chosen geometry assumption`, `bench measurement`) and owner. **CAD-RELEASED** is a separate decision after checks in `47`.

## 3. CAD document and assembly breakdown

```text
BB_C0_ASM                         [top assembly, revision & BOM]
├── BB_BDY_DATUM                  [axes, root planes, battery rail, antenna corridor]
├── BB_FUSELAGE                   [body frame / accessible fasteners / safety mounts]
├── BB_ACTUATOR_L                 [exact servo envelope, output shaft & connector]
├── BB_ACTUATOR_R                 [mirrored in CAD, electrically calibrated independently]
├── BB_ROOT_HINGE_L               [separate pivot reaction path]
├── BB_ROOT_HINGE_R
├── BB_TRANSMISSION_L             [A direct / B horn-link; do not co-install]
├── BB_TRANSMISSION_R
├── BB_WING_FRONT_L / _R         [structural membrane/ribs/leading-edge]
├── BB_WING_REAR_L / _R          [optional passively coupled; not presumed]
├── BB_BATTERY_TRAY               [securing, retention and CG adjustment]
├── BB_MCU_RX_POWER               [service clearance, vibration isolation as tested]
├── BB_WIRING_ANTENNA             [harness route and bend envelope]
└── BB_TEST_INTERFACE             [dedicated fixture connection outside motion volume]
```

- Keep one master datum for both free-airframe and test-rig mount; preserve the **mass and geometry impact** of test interfaces and any removable ballast.
- Assembly mates: exactly one prescribed rotational DOF per actively driven wing root; remaining unintended DOFs constrained. A floating rear-wing hinge is defined independently and checked for excessive free play.
- Avoid overconstraints: do not ask servo spline/output shaft to carry large unsupported bending moments. Propose a **separate bearing/pivot reaction path** for the wing root and a torque-transmitting horn/linkage, subject to weight budget.
- Use modular replaceable wings and servo mounts for calibration, not permanent glue that prevents inspection; define fastening/vibration-retention plan after materials are chosen.
- A wire or antenna route that intersects a moving sweep is a CAD hard clash even if it looks clear when wings are neutral.

## 4. Three kinds of geometry envelope

1. `NOMINAL`: CAD position at neutral commanded stroke.
2. `KINEMATIC`: full synchronized/asynchronized left/right stroke, including worst intended phase and steering differential; test each proposed waveform on both sides independently.
3. `DEFLECTED`: `KINEMATIC` + structural deflection, root play, tolerance stack-up, and wiring movement **as measured/estimated**. Reject a purported 'clear' design based only on `NOMINAL`.

Collision list: leading edges vs body; rear vs front wing overlap; horns vs skin/frame; pushrods at dead center; opposing left/right cilia/rods; power harness; battery latch; receiver antenna; test fixture. Label `CLEAR`, `CONTACT`, `UNKNOWN`; unknown is not pass.

## 5. CAD output requirements and versioning

- Source in an editable **native parametric CAD format**; neutral STEP for exchange plus SVG/PDF 2D drawing **only when dimensions approved**. Do not claim the SVG concept in `assets/` is a solid CAD model.
- For every release: bill of materials, named datum, assembly exploded view, pose envelope snapshots, mass model and measured correction table, manufacturing process, tolerances and inspection points.
- CAD model IDs `MECH-C0-rXX`; printed/cut component IDs and revision mark physically present when practical. C1 is not a cosmetic increment of C0; its wing inertia must be re-established.
- No external STL/wing CAD copied into released drawings until reuse rights and attribution are reviewed. Reference only upstream data with provenance.

## 6. Exit and interfaces

**For G0 concept review:** accept frame contract, component breakdown, exact distinction between assumed and measured dimensions, configuration tree and collision-check plan. **Do not yet authorize fabrication**.

**For G0-B bench design:** exact servo/battery/receiver variants, mechanical load path, CAD release package, fixtures, measurable limits and signed hazard review. **No G4 implication.**

References: [Festo design brochure](https://www.festo.com/PDF_Flip/corp/Festo_eMotionButterflies/en/index.htm), [review of FWMAV fabrication](https://pmc.ncbi.nlm.nih.gov/articles/PMC6412266/), [flapping-wing mechanisms review](https://doi.org/10.3390/aerospace10060554).
