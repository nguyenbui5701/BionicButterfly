# BionicButterfly — V1 Design Decision Register

- **Document ID:** BB-ADR-INDEX-001
- **Version:** 0.6 | **Date:** 2026-11-12
- **Owner:** Solution Architect | **Status:** PROPOSED — none of these decisions is automatically approved
- **Refs:** `02_V1_REQUIREMENTS.md`, `12_FIRMWARE_SOURCE_AUDIT.md`, `13_V1_ARCHITECTURE_PROPOSAL.md`

## 1. Proposed architecture decisions

| Decision | Recommendation | Reason / trade-off | State |
|---|---|---|---|
| **D-001 — Source foundation** | Independent modular firmware using upstream repositories as read-only engineering references | Reduces maintenance, safety-invariant and license/provenance risks, at cost of more initial work | PROPOSED |
| **D-002 — V1 milestone** | **Final V1 product: real RC-piloted powered free flight**; simulator/servo bench/restrained airframe remain prerequisite development gates | Owner clarified product goal; preserves safe development order | **OWNER-DECIDED scope**, 2026-11-12; technical feasibility not approved |
| **D-003 — Controller hardware** | ESP32-C3 **candidate**, not yet an approved PCB/pin map | Matches ESP-FLUTTER ideas and common toolchain, but part availability, GPIO and performance must be checked | PROPOSED |
| **D-004 — Command ownership** | One active trusted source; explicit arm and source handover; central Safety Supervisor | Avoids conflicting RC/web/ESP-NOW control (audit F-02, F-08) | PROPOSED |
| **D-005 — Input pathways** | **Physical RC primary in-flight** (owner decided); simulator first, Wi-Fi browser setup/bench only; protocol/hardware pending | Protects flight command ownership; avoids coupling safety to Wi-Fi | **OWNER-DECIDED RC-first intent**; implementation PROPOSED |
| **D-006 — Motion algorithms** | Monotonic-time waveform and differential setpoints constrained by per-servo measured envelopes | Audit F-06/F-09, dynamic reproducibility | PROPOSED |
| **D-007 — Loss of signal** | Strict bench fault/disarm policy including decorative states; flight policy separately designed | Audit F-03, F-05; wing shutdown midair not inherently safe | PROPOSED |
| **D-008 — Simulation fidelity** | Deterministic kinematics, state machine and safety fault injection; no unvalidated flight physics claims | Early confidence for software only | PROPOSED |
| **D-009 — LED & UI** | Secondary subsystem; must not block control/safety; optional for first bench demo | Keeps V1 testable and lowers timing risk | PROPOSED |
| **D-010 — Work partition** | SA edits `Design/` and later `Task/`; Developer owns `Source/`; PR checkout isolated under `ReviewPR/` | Mirrors role rules; avoids concurrent workspace collisions | PROPOSED; rules awaiting approval |

| **D-011 — Mechanical actuation feasibility** | Compare two independent servos first against M2/M3 and measure before selection | Closest to references and RC steering intent, but must demonstrate speed/torque/power/force | PROPOSED |
| **D-012 — LEDs** | Bare-airframe, no LEDs for first load/force experiments; add effects after baseline | Reduces wing inertia and isolates flight-critical performance | PROPOSED |
| **D-013 — Benchmarks vs specifications** | Keep literature weights, spans and rates as published *references*, not approved product requirements | Avoids assuming feasibility from other airframes | PROPOSED |
| **D-014 — IMU boundary** | Optional stabilization assistance may be considered for V1, but no waypoint autonomy | Distinguishes manual pilot assistance from V2 autonomous navigation | PROPOSED |

## 2. Open owner choices (fill when decided)

| Ref | Question | Suggested default | Owner decision |
|---|---|---|---|
| **O-01** | End goal: visual demonstration, or actual controlled free-flying butterfly? | V1 = flight by physical RC; V2 = autonomy | **DECIDED by owner 2026-11-12** |
| **O-02** | Preferred initial environment? | Indoor guarded bench | PENDING |
| **O-03** | Target wingspan/mass/cost and preferred wing material? | TBD by owner and CAD/force analysis | PENDING |
| **O-04** | Available servo, ESP32 model, battery, receiver? | TBD; no purchase recommendation yet | PENDING |
| **O-05** | Control preference for in-flight V1? | Physical RC is mandatory; bench simulation/config first | **DECIDED by owner 2026-11-12 (RC-first)** |
| **O-06** | Include LEDs in first hardware prototype? | Optional, after actuation passes bench tests | PENDING |
| **O-07** | Approve clean independent implementation; disallow copying upstream code/assets without license review? | Yes | PENDING |
| **O-08** | Approve `07_AI_CODING_RULES.md`, `10_SA_OPERATING_RULES.md`, `11_HANDOFF_PR_WORKFLOW.md` as project rules? | Yes after review | PENDING |

Owner confirmation can be recorded through explicit user message (as for D-002 and O-01/O-05); no user message has yet approved the complete hardware, architecture, budget, interface or V1 acceptance numbers. **An unanswered item is not approval.**

## 2A. Workflow preference — owner decision 2026-11-12

- SA may prepare/update files under `Design/` and preserve versioned drafts.
- **Do not include repetitive push instructions after every design deliverable.** Owner decides when to push GitHub; no automatic push/merge without a separate explicit request.
- Local commits remain the intended change-history safeguard, if a local repo is available; if only chat artifacts are available, SA must state that no commit occurred and provide files to place in the repo.
- This workflow preference **does not** approve any technical design not explicitly confirmed.

## 3. Source provenance follow-up (nonblocking for requirements drafting)

User reported `git -C ..\ESP-FLUTTER-reference status --short` produced **no output** on 2026-11-12. This means the working tree has no reported modified tracked files or visible nonignored untracked files, but it **does not establish that all files in the uploaded ZIP are tracked at the stated commit**. In particular `hardware_config.h`, `hover_bias.cpp`, `led_control.cpp` appeared in the archive while absent from `git ls-files` provided earlier.

Read-only Windows commands for later verification, from the `BionicButterfly` project root:

```powershell
git -C ..\ESP-FLUTTER-reference ls-files --stage -- ESP-FLUTTER/src/hardware_config.h ESP-FLUTTER/src/hover_bias.cpp ESP-FLUTTER/src/led_control.cpp
git -C ..\ESP-FLUTTER-reference check-ignore -v -- ESP-FLUTTER/src/hardware_config.h ESP-FLUTTER/src/hover_bias.cpp ESP-FLUTTER/src/led_control.cpp
git -C ..\ESP-FLUTTER-reference ls-files --others --ignored --exclude-standard -- ESP-FLUTTER/src/
```

An empty `check-ignore` output can also be normal. Do not modify or clean the reference clone; do not conflate an audit ZIP with a verified commit snapshot.

## 4. Design freeze checklist

- [ ] Requirements and target milestone agreed by owner.
- [ ] Safety/state machine, source authority, failure behavior agreed for chosen milestone.
- [ ] Bench-only numeric safety envelope or explicit plan to calibrate without wings agreed.
- [ ] Mechanical/electrical constraints collected for eventual hardware task.
- [ ] Reference license and imported-content policy recorded.
- [ ] Test plan and acceptance criteria accepted.
- [ ] Rules of responsibility approved.
- [ ] Specific revision/commit IDs recorded; only then may SA issue scoped implementation tasks.

## 5. Change control

When a decision is approved, append `APPROVED` with date/approval link, update dependent requirements/architecture/tests, commit, and link that exact commit from each subsequent task. To change an approved decision, record the old status as `SUPERSEDED`, add a new decision/revision and seek reapproval. Do not silently rewrite the meaning of past task acceptance criteria.

*Changelog 2026-11-12 v0.2: record RC-controlled free-flight as V1 and autonomy as V2; honor owner-managed GitHub push.*


## 6. Mechanical feasibility evidence and decisions (v0.3)

- `17_MECHANICAL_FLIGHT_FEASIBILITY.md` reviews M1/M2/M3, literature benchmarks and unmeasured physical quantities.
- `18_MECHANICAL_EXPERIMENT_PLAN.md` defines MX-01…MX-10 and G2/G3/G4 evidence and stop conditions.
- Decisions D-011…D-014 remain **PROPOSED**; none overrides owner-confirmed V1 manual RC free-flight scope.
- No mass/span/servo/LED/IMU purchase or pilot-safety claim is approved by this update.

*Changelog 2026-11-12 v0.3: mechanical trade-offs, quantitative evidence plan, preserve owner-managed push.*

## 7. Mechanical Concept Design (v0.4 — PROPOSED)

| Decision | Proposal | State / owner approval |
|---|---|---|
| **D-015** | Dựng concept M1/C0, 2 servo đối xứng, bố trí pin dịch dọc để cân CG; CAD cuối cần thông số thực | PROPOSED, not owner-approved |
| **D-016** | Sử dụng 70 g C0 như ngân sách phân bổ phân tích và 82 g C1 như kịch bản LED, không phải airworthy limits | PROPOSED, not owner-approved |
| **D-017** | C1 LED sau C0 và phải thử lại toàn bộ cơ khí/điện/điều khiển liên quan | PROPOSED, not owner-approved |
| **D-018** | Nguồn LiPo 2S + rail servo/logic đúng datasheet như hướng nghiên cứu, chưa khóa BEC/pin | PROPOSED, not owner-approved |

Refs: `19_MECHANICAL_CONCEPT_DESIGN.md`, `20_PRELIMINARY_BOM_MASS_POWER.md`, `21_MECHANICAL_CONCEPT_REVIEW.md` và `assets/19_CONCEPT_M1_*_VIEW.svg`. Không task phát triển trước Design Freeze.

## 8. Electrical architecture decisions (v0.5 — PROPOSED)

| Decision | Proposal | Rationale | Approval status |
|---|---|---|---|
| **D-019** | Compare **2S regulated buck** with a **1S boost / rated low-voltage servo** variant after load data; use 2S only as exploratory baseline | Avoid assuming that low regulator input current implies lowest flight mass | PROPOSED |
| **D-020** | Separate regulated servo and MCU/RX power branches, common ground, protected external board input/USB isolation | Servo transients may brownout MCU; 2S must not touch XIAO BAT/5V directly | PROPOSED |
| **D-021** | Candidate XIAO D6/D7 UART, D4/D5 PWM, D1 ADC1, avoid D0/D8/D9 boot strapping pins for first prototype | Pin map aligns with board reference and reserves safe interfaces | PROPOSED |
| **D-022** | Flight RC-loss/low-battery response must be established from G3 evidence; not a blanket servo-power-off rule | Cutting lift midair may be hazardous | PROPOSED |

**Open owner decisions (electrical):** board variant; TX/RX exact models; servo model; 1S/2S pack and weight; budget; acceptable test site; approval of electrical safety plan and power-path topology. No exact part or wire path is approved by this draft.

**SA boundary:** no `Task/` assignment until owner approves a *bounded* design scope and associated G0 plan. Owner controls GitHub pushes; documents are prepared for manual application.

*Changelog v0.5 — electrical power, pinout and hazard decisions appended.*

## 9. Software / safety integration decisions (v0.6 — ALL PROPOSED)

| ID | Recommendation | Reason | State |
|---|---|---|---|
| **D-023** | One central safety supervisor and separately tested typed adapters, planner and HAL | Prevent ISR/UI paths from bypassing output policy | PROPOSED |
| **D-024** | Receiver serial-frame freshness and actual RF health are separate observations; CRSF sequence is optional, not invented | Prevent held-channel failsafe from looking like valid pilot intent | PROPOSED |
| **D-025** | Distinguish `ACTUATION_ACTIVE` from actual airborne observation; operation context comes from approved setup | No proof of being airborne without validated sensor | PROPOSED |
| **D-026** | G2/G3 bench stop and G4 in-air contingency are distinct policies | Powering off both wings mid-air is not by itself a safe landing plan | PROPOSED — G4 BLOCKER |
| **D-027** | RC exclusively owns V1 flight; browser configuration works only in disarmed/authorized bench contexts | Prevent in-flight takeover and unsafe tuning | PROPOSED; RC-first intent owner confirmed |
| **D-028** | Two-servo M1 must prove controllability and passive stability, or revise mechanics/assist strategy | Independent command count does not prove pitch/roll/yaw control | PROPOSED — G4 BLOCKER |
| **D-029** | Distinguish G0-A PC-only design approval from G0-B hardware and G0-C flight approvals | Permit bounded future development without implying hardware or flight authorization | PROPOSED |

**Owner scope is still the only confirmed technical product choice.** None of D-023…D-029 has been accepted simply by requesting more design. New traceability and approval artifacts: `26` integration findings, `27` safety FSM, `28` module/timing contract, `29` requirement/test matrix, `30` freeze checklist, `31` flight controllability analysis.

*Changelog v0.6: cross-document integration decisions and no-go conditions; no developer task created.*

## 10. Pilot controller and calibration decisions (v0.7 — PROPOSED, not owner-approved)

| ID | Candidate design decision | Reason / verification | Status |
|---|---|---|---|
| **D-030** | Mode-2-style two-axis interface: left vertical `FLAP_DEMAND`, right horizontal `STEER`; other stick axes unused for V1 until aerodynamics measured | No fictional pitch/roll/yaw guarantees; PX-02/15 | PROPOSED |
| **D-031** | Deliberate physical 2-position firmware arm intent; candidate CH5/AUX1 plus **independent** MCU ARM gate | ELRS v3/v4 switch modes vary; PX-01/20 | PROPOSED |
| **D-032** | Channel map identified by TX model, ELRS/RX version, selected mode and calibration revision | Prevent mistaken channel order and reverse control; PX-03/18 | PROPOSED |
| **D-033** | First powered flight uses one fixed, qualified profile; rate switching, trims, browser calibration locked when armed | Avoid sudden energy/phase/motion changes; PX-06/11 | PROPOSED |
| **D-034** | Distinct SIM / BENCH / RESTRAINED / FLIGHT configuration profiles; context authorization cannot be granted by profile name | Prevent SIM envelope from being treated as airworthy; PX-12 | PROPOSED |
| **D-035** | Flight UI is read-only/non-critical; pilot uses physical RC; unknown link/airborne state truthfully indicated | RC sole owner; UX-02/04, PX-13 | PROPOSED |
| **D-036** | In-air disarm, RF-loss and low-battery policy remains unresolved; block G4 | Cutting flapping may remove lift; PX-16 and risk H-RC-07 | **PROPOSED / G4 BLOCKER** |

New draft documentation: `32–36`. Owner still needs to decide TX/RX model, exact pilot layout, first-flight profile strategy, physical site and allowed stabilization aid. Owner's instruction to keep designing is **not** final design approval. No Developer task and no automatic GitHub push.

## 11. Flight dynamics and control-authority decisions (v0.8 — PROPOSED)

| ID | Proposal | Reason / proof | State |
|---|---|---|---|
| **D-037** | Models are labeled D0–D3; do not claim free-flight fidelity at D0 | `37`; no identified aerodynamic coefficients | PROPOSED |
| **D-038** | Calibrate local force/moment effectiveness and uncertainty before freezing steering sign or profile | `38`, tests CA-05…13 | PROPOSED |
| **D-039** | S0 two-servo manual differential remains an **experimental option**, not selected airworthy controller | `39`; authority currently UNKNOWN | PROPOSED |
| **D-040** | Optional bounded IMU stabilization may be evaluated for manually piloted V1 only after explicit approval | user deferred autonomy V2; S2 ≠ route autonomy | PROPOSED |
| **D-041** | Redesign passive geometry/actuation if measured authority insufficient | `41` trade study | PROPOSED |
| **D-042** | G4 needs qualified directional/attitude/recovery evidence as well as net force | `40` FA-01…12, prior flight blockers | PROPOSED / G4 BLOCKER |
| **D-043** | LED configuration C1 gets independent aero-inertial and power qualification | wing-inertia and power changes beyond mass | PROPOSED |

These decisions are **not implied approvals** from 'tiếp tục'. V1 manual RC and V2 autonomous-after-V1 remain the only confirmed product scope. No `Task/`, no automatic GitHub push. References: `37_FLIGHT_DYNAMICS_MODEL_CONTRACT.md` to `41_CONTROL_ARCHITECTURE_TRADE_STUDY.md`.

## 12. Detailed mechanical architecture (v0.9 — PROPOSED)

| ID | Proposal | Rationale / files | State |
|---|---|---|---|
| **D-044** | Adopt body frame +X forward, +Y right, +Z **down** for all 3D mechanical/aero/load data | Resolve conflicting `19` and `37`; see `42`, `47` | PROPOSED |
| **D-045** | Model A direct servo wing drive and B separate supported pivot with servo linkage; compare mass/loads before choosing | `43` | PROPOSED |
| **D-046** | Keep W-A membrane+veins and W-B split rear lobe as distinct wing concepts | `44`; Festo reference does not prove our design | PROPOSED |
| **D-047** | Require revised measured C0 mass/CG/inertia ledger instead of relying on 70 g allocation | `20`, `44` | PROPOSED |
| **D-048** | Approve only staged R0–R3 rig *design process*, not powered experiments | `46`; actual guard, sensor and power approval pending | PROPOSED |
| **D-049** | Release dimensioned CAD under part/fit/change management and requalify C1 independently | `42`, `45`, `47` | PROPOSED |
| **D-050** | Mechanical design completion alone is NOT flight authorization | `30`, `47`; G4 blockers remain | PROPOSED / G4 BLOCKER |

**No change in owner-approved scope:** V1 manual RC free flight, V2 autonomy later; owner manages Git pushes. No `Task/` has been authorized.
