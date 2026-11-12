# BionicButterfly — Detailed Mechanical Review Gate & Decision Record

- **ID:** BB-MECH-GATE-047 | **Rev:** 0.1 | **Owner:** SA | **Status:** PROPOSED / REVIEW NOT APPROVED
- **Goal:** define what a meaningful 'mechanical design complete' statement can mean and identify blocked evidence before flight design freeze.

## 1. Summary — what is supported today

- Supported by literature: articulated wing-root mechanism, light spars/membranes, passive deformation and a separate rear-wing hinge are **valid design directions** in other aircraft.
- Supported by user: target V1 is physical free flight by manual RC, V2 self-flight later. User decides Git pushes.
- Supported by our documents: proposed component breakdown, master reference frames, parametric CAD definitions, alternative transmissions, mass/CG equations, rig and test plan.
- **Not supported:** final hinge dimensions, material thicknesses, validated servo speed/torque, wing loads, stable yaw/pitch/roll control, flight failsafe, safety to fly, final BOM or cost.

## 2. Gate checklist — status explicit

| Gate | Review item | Evidence required | Current disposition |
|---|---|---|---|
| `MDR-01` G0 | master body and sensor coordinates consistent | corrected `19`, `37`, new `42`; sign tests planned | **DRAFT RESOLUTION** |
| `MDR-02` G0 | alternatives A vs B both modeled for sweep and weight | `43` with actual actuator envelope and 3D constraints | PROPOSED / NO CAD |
| `MDR-03` G0 | structural root pivot and reaction load path | dimensioned pivot concept; load-path drawing | NOT READY |
| `MDR-04` G0 | wing variant W-A / W-B definitions, no unlicensed CAD copying | `44`, material revision and drawing release policy | PROPOSED |
| `MDR-05` G0 | C0 total target mass / allowance and per-wing inertia risk | weighted BOM assumptions vs verified measured parts | 70g ONLY ESTIMATE |
| `MDR-06` G0 | CG/antenna/power harness dynamic clearances | `42`,`44`; sweep + physical verification | NOT RUN |
| `MDR-07` G0-B | native parametric CAD, STEP, assemblies & manufacturing tolerances | actual part models and measured interfaces, inspection drawings | NOT READY |
| `MDR-08` G0-B | free servo and guarded rig test infrastructure | `46`, risk review, load/calibration chain | NOT BUILT |
| `MDR-09` G2 | servo motion/current/temp/brownout and limits | G2/MX/RG records, actual datasheets | NOT RUN |
| `MDR-10` G3 | wing trajectory, fatigue, force/moment, control authority | G3/MX/RG/CA records w/ uncertainty | NOT RUN |
| `MDR-11` G4 | recovery, yaw/pitch/roll stability, response to RF loss and power | aircraft-specific G4 safety case & test review | **BLOCKER** |
| `MDR-12` C1 | LEDs requalification | wing inertia, power and force remeasured | DEFER until C0 evidence |

**No model-specific flight success, build readiness or selection of active two-servo mechanism is claimed.**

## 3. Proposals to owner — not automatic approvals

| Decision ID | Pending proposal | Alternatives / uncertainty |
|---|---|---|
| D-044 | adopt body coordinate frame B: forward/right/**down** and datum O_B per `42`; resolve conflict MECH-001 | require systematic correction of older documents not overwritten by current package |
| D-045 | evaluate mechanism B (servo horn/pushrod + supported pivot) vs A direct-drive as a pair of CAD studies | weight, backlash, torque and servo bearing rating not yet measured |
| D-046 | make W-A joined wing and W-B split passive rear-wing separate research variants | no assumption split wing always increases performance |
| D-047 | support C0 geometry/mass property ledger with actual assembled full-harness measurements | 70g target is not a pass criterion and reserve is slim |
| D-048 | use staged R0–R3 restrained fixture; never equate one-axis force with 6-axis force/moment | exact sensor, rig enclosure, budget and sample rate open |
| D-049 | CAD and inspection are under engineering change control; C1 LED is a new qualification | owner can prioritize C0 only until feasible |
| D-050 | physical geometry and rig gates do not authorize G4 flight or hardware procurement | G4 safety case and measured control authority remain unresolved |

## 4. Cross-document correction protocol

**MECH-001 frame mismatch:** Old `19` has `+Z up`; `37` has `+Z down`. This package includes an edited `19` and `42`. However, if the owner's local `19` has changed since the previous ZIP, review diff rather than overwriting it. Any other `Design/` document with legacy `Z-up` must be evaluated explicitly: coordinate sign conversions are a semantic change, not just a spelling update.

**MASS-001 low reserve:** `20` estimates 70 g C0 with just 1.5 g reserve. Add a new measured BOM ledger before choosing CAD sizes; do not hide overruns by subtracting wing structural retention or safety mass.

**CTRL-001 flight authority open:** `37` states B in R^(4×2) for two instantaneous controls. That does not prohibit an underactuated flyable airframe, but does preclude claiming independent four-axis force/moment control. Do not make a completed hardware drawing a substitute for a controllability test.

**LIC-001 provenance:** Some upstream reference source may not have commercial reuse rights. Use original CAD and record origin/license of every imported component geometry.

## 5. Integration sequence — design only

1. Consolidate current `Design/` files in owner's Git tree; compare before overwriting later revisions.
2. Review `42` coordinate datum and `43` A/B transmission alternatives.
3. Approve a **narrow G0 design concept** if desired; this is not G0-B CAD release or G4 flight.
4. Gather *measured* part envelopes, provisional manufacturing process and test-rig budget.
5. Define parametric CAD with released fit/clearance numbers only after actual interface data and review.
6. Review electrical and pilot safety impact of any change; update `15`, `20`, `22–25`, `30`, `37–41` as appropriate.
7. Only after owner approves an explicit design scope could SA create a bounded `Task/` for AI Code. No task now.

## 6. Mechanical change review template

```text
Design review: MDR-____
Documents and revisions (plus Git commit if available):
Scope: parametric CAD-only / bench-fixture-only / hardware / flight
A/B mechanism considered:
W-A/W-B wing concept considered:
Measured mass and CG values: UNMEASURED | ...
Evidence: source, instrument, status PASS/FAIL/NOT_RUN
Outstanding hazards / mitigation:
Technical SA recommendation:
Owner explicit decision (APPROVE / REWORK / DEFER):
Next review trigger:
```

**As of 2026-11-12, all physical tests remain NOT RUN and all D-044…D-050 remain PROPOSED.**
