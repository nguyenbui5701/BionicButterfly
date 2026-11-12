# BionicButterfly — G0 Design Review and Freeze Readiness

- **Document ID:** BB-G0-030 | **Version:** 0.1 | **Date:** 2026-11-12
- **Owner:** Solution Architect | **Status:** DRAFT; current determination = **NOT READY FOR FULL V1 HARDWARE/FLIGHT FREEZE**.
- **Purpose:** capture exactly *what may be approved*, and prevent a partial design review from becoming implicit permission to build or fly.

## 1. What has actually been decided

| Decision | Status | Authority |
|---|---|---|
| V1 outcome: real butterfly RC-powered manually controlled free flight | OWNER-CONFIRMED 2026-11-12 | Owner message |
| V2 scope: autonomous flight only after V1 | OWNER-CONFIRMED 2026-11-12 | Owner message |
| GitHub push timing: owner handles as desired; no repetitive push instructions | OWNER-CONFIRMED 2026-11-12 | Owner message |
| ESP32-C3/XIAO, servo pair, ELRS/CRSF, 2S+BEC, current wing concept C0/C1 | **PROPOSED** | `03`, `16`, `19–25` |
| Source implementation method, role rules final approval, IMU/stability assistance | **OPEN** | `07`, `10`, `11`, `15` |
| Flight in-air safety response, actual airframe, BOM and numeric limits | **OPEN / G4 BLOCKERS** | `17–18`, `25`, `27`, `31` |

## 2. Tiered freeze — none is implied

| Design approval tier | Could authorize *after written owner approval* | Required evidence/constraints | Not allowed merely by tier |
|---|---|---|---|
| **G0-A: PC-only software design** | SA may issue a narrowly scoped simulation/core-firmware task (when owner says design approved) | FR/NFR interfaces, safety FSM and pure-core contracts reviewed; surrogate values explicitly SIM_ONLY; no hardware action | energizing servo, building airframe, G4 |
| **G0-B: electrical + mechanical bench design** | SA may issue G2/G3 hardware integration tasks *only after separate design approval* | exact BOM and revision, verified schematic and pinout, reviewed bench hazards/instrumentation, source license checks, defined stop rules | uncontrolled powered wings, free-flight authorization |
| **G0-C: flight-test case** | owner may authorize controlled G4 experiment after G1–G3 evidence, site/radio review and test plan signoff | actual flight-specific contingencies, pilot training, site rules/permissions, quantitative acceptance metrics, evidence capture, safety perimeter | assertions that it will fly, automatic V2 autonomy |

**Current status:** No G0 tier has yet been approved. Drafting a better design or uploading documents to GitHub does not count as approval. Per SA workflow, no `Task/` file now.

## 3. G0 review checklist with honest status

| Check | Status on 2026-11-12 | Closure proof needed |
|---|---|---|
| Scope, RC-first, autonomy deferred | CONFIRMED | owner message |
| All FR/NFR have traceable design/test IDs | DOCUMENTED, unreviewed | owner review `29` |
| Firmware input/safety/output abstraction | PROPOSED | approve `27` and `28` |
| Disarm, RF loss, low battery and recovery simulation policy | PROPOSED | approve G0-A semantics; G4 semantics remain open |
| Ownership of UI and dev workspaces | DRAFT | approve operational rule files `07`, `10`, `11` |
| Receiver/link failsafe semantics verified | NOT RUN | choose TX/RX, RF disconnect test and logs |
| Servo pulse, speed, torque and load | UNKNOWN | exact servo data and G2 measurements |
| Wing dynamics, moment and pitch/roll/yaw control | UNKNOWN | rig data and G3/G4 analysis |
| Source provenance and third-party licenses | OPEN | per-file inventory/licensing proof and Git-snapshot reconciliation |
| Electrical power path exact wiring | PROPOSED | schematic, regulator limits, USB protection and board revision |
| Numeric flight acceptance and experimental site | OPEN | site/pilot/conditions, thresholds, emergency procedure |
| Real G1/G2/G3 verification logs | NOT RUN | future actual artifacts |

## 4. Decision dependencies and architectural impact

| Missing input | Why it matters | Documents to revise when decided |
|---|---|---|
| Flight environment, available safe site and pilot constraints | determines test envelope/wind, ground protection, radio safety and G4 acceptance | `02`, `14`, `27`, `31` |
| Intended max span/weight/budget | affects wing loading, mass/balance, actuator selection | `03`, `17`, `19–21` |
| TX/RX exact model + channel mapping | determines baud/logic/failsafe semantics, RF health validity | `16`, `23`, `27`, `28` |
| Servo+linkage and wing concept | determines envelope, power and actual control authority | `17–23`, `28`, `31` |
| 1S vs 2S supply choice and protection | changes harness/BEC/CG and voltage thresholds | `20`, `22–25` |
| Whether passive stability is enough or V1 needs IMU assistance | V1 manual RC may need attitude damping; *assist* is not waypoint autonomy | `02`, `13`, `19`, `27`, `28`, `31` |
| How to handle link loss / midair E-stop | cannot safely assume lift removal = safe landing | `14`, `25`, `27`, `31` |
| Rules and license provenance approval | prevents ambiguous ownership and unauthorized reuse | `07`, `10`, `11`, `12`, `15` |

## 5. Evidence and approval record templates

```text
Design review ID: G0-REV-____
Tier requested: G0-A / G0-B / G0-C
Document revision list: file, version, Git commit:
Approved scope / permitted tasks (if any):
Explicit exclusions:
Assumptions and measured inputs:
Open hazards and dispositions:
Pass/fail criteria and associated test IDs:
Reviewer (SA):
Decision (owner): APPROVED / REVISE / REJECT
Decision date / explicit message or issue link:
Next review trigger:
```

Never infer owner approval because the owner says “tiếp tục” (continue designing) or “push done”. That only authorizes further drafting in `Design/`.

## 6. Future SA → Developer handoff (not activated)

After a tier is explicitly approved, SA creates one bounded `Task/TASK-XXX.md` with: exact Design files/revisions, task scope/non-goals, code directories allowed, acceptance tests, no-go hazards, referenced Git commit, branch/PR target. Developer may comment on design defects but cannot unilaterally replace safety policies or amend `Design/`. SA checks PR via isolated `ReviewPR/` worktree and leaves a review comment. Follow the cleanup/retention policy in `11_HANDOFF_PR_WORKFLOW.md`. This section describes the future process, **not** an active task.

## 7. Final disposition

**Proceed with design only.** Flight demonstrator remains a goal, not a verified property. Hold off on component purchases, energizing unvalidated wings and all V1 flight claims until prerequisites are closed.

## 8. Pilot-control-specific Design Freeze requirements (v0.2)

`32–36` document a **candidate** two-axis Mode-2-style pilot mapping, radio/MCU arming separation, immutable profiles, pilot UX and risk matrix. For **G0-A PC-only** approval, owner must explicitly accept a bounded host-only logical interface with SIM_ONLY values; this does **not** choose a TX model or enable hardware. For **G0-B**, exact transmitter, RX, firmware, switch mode, arm intent channel, channel monitor traces, radio-loss behavior and servo/power calibration must be recorded and reviewed. For **G0-C/G4**, measured steering control authority, mass/stability, landing/recovery/site constraints and in-air link-loss/disarm/low-power policies are still blockers.

No prior decision was automatically approved by asking to continue. PX/UX test matrix results = NOT RUN. Source code remains untouched; no new `Task/` until scoped approval.

## 9. Phase 1.8 flight-dynamics review — current disposition

- **Analysis completed, validation not begun:** D0 geometry/weight/control-sensitivity *framework* (`37`) and experimental method (`38`) exist. No actual full-aircraft mass, force, torque or flight observations have been acquired.
- **Software-only readiness:** G0-A still requires **explicit owner acceptance** of a scoped simulation contract and verified safety/interface designs. D0 simulator must label air motion as hypothetical.
- **Hardware readiness:** G0-B not ready; specific servo/wing/BEC/receiver/sensor fixture are unapproved. Need calibrated `CA-01…15` in permitted G2/G3 contexts, applicable hardware portions only.
- **Flight readiness:** G0-C/G4 **NO-GO**. Two servo control authority, pitch/roll/yaw behavior, disarm/RF-loss, site, pilot procedures and numeric flight success criteria remain OPEN.
- **Decision table:** D-037…D-043 in `15`/`41`, all PROPOSED. S0 is an experimental candidate; S1/S2/S3/S4 require fresh owner decisions. A basic IMU stabilizer would not itself constitute V2 autonomy, but no such feature is approved.
- **Traceability:** see `29` §7, `14` §13, `38` CA-01…15 and `40` FA-01…12. **Every test status NOT RUN**.

**Next SA review item:** compare current power/servo/wing *physical bill of materials* against measurement feasibility, define reference CAD and instrumentation, and prepare a bounded G0-A design review proposal only when owner seeks approval. Do not create Developer tasks yet. Owner controls GitHub pushing and releases.

## 10. Phase 1.9 mechanical detailed design checkpoint

- **Resolved in draft only:** MECH-001 body-frame inconsistency is documented and `19` is corrected to match `37`; local owner's other documents must be checked for legacy +Z-up uses before sign-off.
- **New specifications:** `42`–`47` define parametric CAD, alternative load paths, wing material and inertia accounting, inspection and guarded fixture stages. Concept vector drawings are not production CAD.
- **G0-A PC-only:** unchanged (requires explicit owner review/acceptance; no coding task yet).
- **G0-B bench:** NOT READY: part-specific servo, hinge bearing ratings, minimum clearances, hard stops, BEC/pin spec, rig calibration and guard hazards unresolved.
- **G0-C/G4 flight:** NO-GO: physical force/moments/attitude controllability and in-air failsafe not demonstrated.
- **Unrun tests:** `MDR-01…12`, `MW-01…08`, `RG-01…10`; no physical evidence or flight claims.
- **Next decision:** owner may later approve a *bounded CAD-only concept* without approving part procurement, servo power or flight.
