# BionicButterfly — Wing Structural Concept, Materials, Mass/CG/Inertia

- **ID:** BB-MECH-044 | **Rev:** 0.1 | **Owner:** SA | **Status:** PROPOSED / unverified geometry & materials
- **Scope:** baseline C0, optional C1 after C0 proof; aligns `20_PRELIMINARY_BOM_MASS_POWER.md` and `37_FLIGHT_DYNAMICS_MODEL_CONTRACT.md`.

## 1. Wing is a compliant aerodynamic structure, not a rigid decorative plate

The candidate wing assembly has a light leading-edge spar, selected radial ribs, a thin membrane, a root hinge, and optionally an inboard-connected rear lobe/pitch compliance. In real flapping-wing studies, passive deformation and hinge properties are material to aerodynamic performance; no membrane thickness, stiffness, fabric pattern or lift coefficient is assumed here. [Source: review of passive insect-inspired mechanisms](https://pmc.ncbi.nlm.nih.gov/articles/PMC12213000/).

Two geometry alternatives shall be maintained until a rig comparison:

| Wing option | Description | Measured comparison |
|---|---|---|
| `W-A` | joined front/rear planform per side with controlled flexible membrane and a stiff leading edge | mass, projected area, twist, left/right shape consistency, stroke response |
| `W-B` | split front/rear lobes with an independently specified **passive rear hinge** akin in principle to literature | added hinge mass/play, passive pitch phase, wing separation/clap effects, fatigue |

Do not assume `W-B` is more efficient or flyable. The Festo example used an overlapping split-wing concept with a rear wing also hinged to the torso, plus onboard sensors and external tracking: a relevant reference, not a transferable flight guarantee. [Festo brochure](https://www.festo.com/PDF_Flip/corp/Festo_eMotionButterflies/en/index.htm).

## 2. Material selection strategy (properties must come from actual batches)

| Feature | Candidate class | Advantage | Risk / critical test |
|---|---|---|---|
| Leading-edge spar | small-diameter carbon-fibre rod or compatible lightweight composite | high specific bending stiffness | brittle fracture/splintering; bond shear; RF antenna shielding; radius/thickness TBD |
| Rib/vein | thin composite rod, light strip or printable reinforcement | tune chord-wise vs span-wise deformation | extra inertia at wing tip, glue joints, repeatable left/right geometry |
| Membrane | thin polyester/Mylar-like film, lightweight flexible sheet | potentially low mass and replaceability | tear initiation, crease stability, adhesive compatibility, weather/temperature |
| Root pivot | supported miniature shaft/bushing or approved hinge | predictable rotational DOF and serviceability | radial load, backlash, fatigue, assembly misalignment |
| Passive hinge (if W-B) | material-flexure or small mechanical pin joint | avoid second active actuator for pitch | unmeasured stiffness, hysteresis, resonance, uncontrolled inversion |
| Body | lightweight printed polymer/composite or cut lightweight frame | prototype rapid iteration and access | anisotropy in prints, vibration cracks, fastener pull-out |

Neither a universal material thickness nor a fabrication method is selected. Sample coupons and joint specimens shall be inspected and characterized before final geometry release. Treat composite fragments and spinning/oscillating parts as guarded-test hazards.

## 3. Parametric wing area, mass and inertia definition

- Wing span per side `R_L/R_R`; define root and tip along the **actual hinge-to-tip distance**, not half visual image width.
- Station chord `c(r)` for `r in [0, R]`, and planform area `S = ∫ c(r) dr`; whether front/rear overlap area is counted once or separately MUST be stated. Maintain both flat-pattern area and projected area at each stroke phase; no silent mixing.
- Surface mass density `sigma_m` [kg/m²] and spar/rib distributed line masses `lambda_i(r)` [kg/m], including glue/LED/harness. `m_wing = ∫ sigma_m c(r)dr + sum ∫lambda_i dr + m_root`.
- Root rotational inertia `J_root = ∫ r² dm`; adding `Δm` at radius `r` increases `J` by approximately `ΔJ = Δm r²` around an axis perpendicular to radial distance.
- For airframe assembly `r_CG = Σ(m_i r_i)/Σm_i`; inertial tensor about CG uses parallel-axis theorem; retain both **calculated** and **measured** provenance and uncertainties.

## 4. Parametric mass ledger — C0/C1 is an estimate only

Use original `20` as budget, **not** as measured proof: C0=70 g target allocation, C1=82 g allocation including assumed +12 g for LED variant. Budget reserve was only 1.5 g for C0, so mass-margin risk is **HIGH**. A component may enter the BOM twice if someone counts wires inside both servo mass and harness: use a weighed BOM with disjoint accounting boundaries and explicit part IDs.

| Assembly | Mass source | CG measurement | Critical outboard inertia |
|---|---|---|---|
| two wings+membranes | weigh each finished L/R assembly | fixture with 3-point balance or measured local mass model | high |
| servos / pivots / linkage | weigh including horns, fasteners & cable | CAD measured location and balance validation | medium near root |
| body / rails / battery | weigh full equipped pack incl plug and retention | real battery at all permitted slider positions | low-to-medium |
| BEC, MCU, RX, antenna | weigh real harness as installed | measure locations, protect RF path | mostly near body |
| C1 LEDs, drivers, wiring | separately weigh and map radial location | full-wing after rework | potentially **very high** |

**CG adjustment policy:** sliding the battery changes the *body* CG only if actual battery retention is secure; it does not fix uneven wing mass/inertia or insufficient control authority. The reference CG allowed interval is TBD until measured trim/stability characteristics. Mark any ballast mass as an explicit penalty with design rationale.

## 5. Wing revision gates

| ID | Measurement required | What it means | Gate |
|---|---|---|---|
| `MW-01` | dimensioned flat pattern with L/R silhouette overlay | reproducible geometry, not aerodynamic sufficiency | G0-B |
| `MW-02` | wing masses + CG, radial mass distribution estimate | inertia and asymmetry reference | G0-B/G3 |
| `MW-03` | unpowered bending/twist video under controlled small load | structural compliance baseline; not flight loads | G0-B/G3 |
| `MW-04` | wing-root freeplay, hinge friction, phase lag | service limits and kinematic validity | G3 |
| `MW-05` | swept collision/deflection, wiring envelope | no interference in approved actuation envelope | G0-B/G3 |
| `MW-06` | per-revision cyclic durability vs thermal and load traces | reject damage before G4 | G3 |
| `MW-07` | measured force/moment sign/dispersion under controlled `u_c/u_d` | actual control effect from that wing geometry | G3 |
| `MW-08` | C1 reweigh, remeasure `J`, current, force and moments | C1 independently assessed | post-C0 |

No numeric pass thresholds fabricated here. Exact hard-stop, strength reserve, permitted elastic strain and fatigue-cycle target become release criteria after tests/vendor material data and owner review.

## 6. Fabrication notes and traceability

- Keep parametric left/right templates in source CAD and a reusable inspection outline with datum ticks. A hand-drawn or printed reference wing shape is NOT sufficiently specified without dimensions and material lot.
- Mark each wing `W-A-L-Rev` / `W-A-R-Rev`; photos before, during and after rig tests, including root joints and tears.
- Do not run a torn wing, a split carbon spar, or a wing with loose hinges. Every repair that changes geometry/mass gets a new revision and calibration.
- Optional LED wiring is a deliberate *structural and inertia redesign*, not a purely visual update.

**Exit:** approved wing-structure parameters + documented measurements and rig evidence; until then no fabrication production release or G4 authorization.
