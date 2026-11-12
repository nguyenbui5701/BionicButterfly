# BionicButterfly — DFM, Assembly Plan & Mechanical Inspection

- **ID:** BB-MECH-045 | **Rev:** 0.1 | **Status:** PROPOSED / NOT A BUILD INSTRUCTION
- **Scope:** C0 mechanical prototype planning. No final part dimensions, servo or adhesive specification has been approved.

## 1. Design-for-assembly rules

1. Every L/R component has an **unambiguous orientation marker**; mirrored parts are identified by part number and mechanical datum.
2. Mount servo and supported wing root so they can be removed **without destroying wings or depowering harness by cutting**.
3. Non-redundant wing retention and pin/horn attachments require positive capture and a visual inspection feature; adhesive-only retention is a hazard pending joint tests.
4. Provide service access to receiver, battery connector, power isolation, and debug port, without placing hands in moving sweep.
5. No exposed sharp rod or unsupported composite fibre in areas handled by the operator; inspect cut ends and apply safe treatment appropriate to material.
6. Final rig mount must not change airframe assembly mass/CG used for the actual flight calculation; fixture-only hardware clearly tagged and removable. If flight configuration changes mounting points or fasteners, recalculate and weigh.
7. Any wing-revision swap invalidates old servo calibration/force-map evidence until rechecked.

## 2. Pre-production drawing and tolerance readiness

**Do not use a global ±0.1 mm tolerance.** Before dimensioning a released part, each interface needs a reasoned tolerance type:

| Interface | Governing need | Release evidence |
|---|---|---|
| servo mount | vendor dimensions + connector/wire exit + access | actual board/servo revision and measured sample |
| hinge journal/bushing | running fit, wear, bearing reaction | calculated fit and trial fit based on process/material |
| horn or spline fit | positive fastener and axial retention | vendor-approved coupling and under-load verification |
| left/right root alignment | suppress unintended steering bias | measured angular alignment error + rig impact |
| wing film/bond | retained mass and no buckling/peel | coupon trials and inspection rubric |
| battery holder | secure under intended motion/impact; no cell puncture | fit, retention and electrical isolation study |
| harness | strain relief & safe minimum bend | video/wiring envelope across stroke |

3D-print anisotropy, heat distortion, hole shrinkage and bonding compatibility are process-specific. 3D printing is **one candidate**, not a universal design guarantee. Include print orientation, material and rework history with part ID if selected.

## 3. Prototype assembly traveler — records, not permission to energize

| Step | Required observation | Pass/hold rationale |
|---|---|---|
| Q-01 | parts inventory with vendor/lot/revision and weight | missing/unknown provenance = HOLD |
| Q-02 | body frame on `O_B`, compare left/right hinge axis positions | unmeasured alignment = HOLD |
| Q-03 | dry-fit pivots and linkages without power | full manual sweep, no binding or snap-through = required |
| Q-04 | attach separately weighed wings and check membrane/rib joints | no cracks, tears, peeling = required |
| Q-05 | route restrained harness/antenna outside dynamic envelope | zero rubbing in worst plausible pose |
| Q-06 | install battery dummy of equal measured geometry/mass before live pack | stability/retention test without energy |
| Q-07 | calculate and measure assembled mass/CG | record full revision incl cables and connectors |
| Q-08 | inspect all retainers and access to power disconnect | positive retention and accessible bench stop |
| Q-09 | independent second-person visual inspection of mechanical hazards | sign off before any bench power tests |
| Q-10 | controlled G2/G3 tests only after electrical + fixture gates | no G4 bypass; record outcomes |

## 4. Mechanical quality attributes

- `PLAY`: hinge deadband and servo-command vs physical-wing response (explicit measurement method, units, limit later).
- `SYMM`: L/R stroke and mass alignment within measurement uncertainty and an approved envelope, not merely visual similarity.
- `WEAR`: any crack, bond peel, detached rib, loose screw, gear strip or temperature-related deformation yields HOLD and rework.
- `HARNESS`: no tensile load on solder/power leads as wing moves; no unapproved route through a hinge.
- `MASS`: total measured C0 and per-part subtotal reconcile; current 70 g design budget and 1.5 g reserve only estimates.
- `TRACE`: physical assembly ID, test rig revision, instrument calibration, BOM and source revisions in the test manifest.

## 5. Change classification

| Change | Review impact |
|---|---|
| edit wing membrane/rib/hinge/servo/horn | invalidate stroke calibration; rerun mechanical and force/authority measurements |
| move battery or BEC/MCU | recalculate and measure CG, inertia; check wire paths and antenna clearances |
| re-print same drawing in different material/orientation | NEW material/process revision: re-qualify strength/fit |
| add LEDs, root LED wire or tip mass | NEW C1; reweigh/retest inertia, power, force, motion and controllability |
| merely change label or textual drawing note | document revision, no physical test claim |

## 6. Evidence form

```text
Assembly ID / revision:
CAD release/hash (if any):
Component BOM with measured masses:
Wing L/R mass and measured root angular play:
Measured O_B->CG position (mm), method, instrument uncertainty:
A/B linkage selected (both cannot be installed simultaneously):
Unpowered full-sweep collision check: PASS / FAIL / NOT RUN
Harness clearance: PASS / FAIL / NOT RUN
Photographic evidence and instrument IDs:
Inspector + date:
Decision: REJECT / REWORK / READY FOR CONTROLLED BENCH REVIEW
```

**Owner gate:** completing a form or 3D printing parts does not approve flight. See `46`, `47`, `30`.
