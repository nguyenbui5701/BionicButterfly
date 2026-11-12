# BionicButterfly — V1 System Design Integration Review

- **Document ID:** BB-INT-026 | **Revision:** 0.1 | **Date:** 2026-11-12
- **Owner:** Solution Architect | **Status:** PROPOSED / review findings OPEN
- **Scope:** V1 = powered free flight under a **physical RC transmitter**. V2 autonomy is excluded. C0 (no LED) is the initial feasibility airframe; C1 (LED) requires independent requalification.
- **Reviewed baseline:** Requirements `02`, hardware `03`, UI `05`, reference firmware audit `12`, architecture `13`, verification `14`, decisions `15`, RC `16`, mechanics `17–21`, electrical `22–25`. These are the previously shared *document revisions*, not an asserted Git commit.

## 1. Integration verdict

**G0 DESIGN NOT FROZEN; NO G2/G3/G4 FLIGHT AUTHORIZATION.** The logical architecture is coherent enough to define further pure-software design, but airworthiness, control authority, measured component limits and in-air contingency behavior remain unproven. No physical flight outcome has been observed for our proposed airframe.

Confirmed owner decisions only: V1 physically flies and is piloted by handheld RC; V2 autonomy later; owner chooses when to push GitHub. These are *scope/workflow* decisions, not approval of technical implementation or a procurement list.

## 2. Cross-document findings — no silent acceptance

| ID | Severity | Finding / conflicting assumption | Required resolution | Related evidence |
|---|---|---|---|---|
| **INT-01** | **BLOCKER for G4** | FR-003, FR-007 and G1 bench stop terminology can be misconstrued as safe in-flight wing disable. | Separate ground-stop policy and **unapproved** in-air link-loss/critical-battery response; test and sign off on airframe-specific contingency. | `27`, `25` H-EE-05/12, VT-03/07/20 |
| **INT-02** | **BLOCKER for G4** | Two-servo common/differential controls do not prove independent pitch/roll/yaw authority or recoverability. | Measure force/moment/stability, verify pilot-turning and landing response; revise actuation or add stabilization if necessary (without assuming autonomy). | `31`, MX-08, FR-019/021 |
| **INT-03** | MAJOR | Browser UI FR-015 could be interpreted as an arm/motion source in free flight despite RC-only FR-017. | Restrict browser to **simulator, setup and explicitly enabled grounded bench**; firmware rejects web arm, trims and changes while flight control is active/armed. | `05`, `16`, `28`, VT-17/22 |
| **INT-04** | MAJOR | Architecture `13` lists a required command `sequence`; RC contract `16` correctly says sequence is optional when actual protocol supplies one. | Specify per-adapter anti-replay; **no invented CRSF frame sequence**. Use local receipt timestamp + valid frame age + radio/receiver health evidence. | `16`, `28`, VT-06 |
| **INT-05** | MAJOR | A stream of valid serial frames does not necessarily prove the upstream RF link remains healthy: receiver firmware can hold prior channel values or indicate failsafe separately. | Treat `rf_health` and `serial_frame_freshness` as separate states. If receiver reports neither reliably, deny G4 until tested. | `27`, `28`, EE-T09 |
| **INT-06** | MAJOR | C0 70 g / C1 82 g budget figures risk being read as proven flight weight limits. | Mark **ESTIMATE**, retain measured mass, CG, moment of inertia and force records. No lift guarantee from a bench force reading. | `20`, `31`, FR-021 |
| **INT-07** | MAJOR | Generic 2S / BEC and XIAO pin map may be mistaken for approved circuit. | Freeze by exact board + receiver + servo + regulator part/revision; verify protection, logic levels, servo current, USB backfeed and startup PWM. | `22–25`, EE-T01–11 |
| **INT-08** | MAJOR | Flight state is not observable from throttle or wing PWM alone when there is no validated altitude/attitude sensing. | Avoid claiming `IN_FLIGHT` as measured. Model **pilot/rig context** separately from actual airborne status; flight policy selection must not depend on an unverified inference. | `27`, FR-014/023 |
| **INT-09** | MEDIUM | “HOVER”, “PERCH” and autonomous-sounding names in reference firmware may be conflated with stability or safety modes. | Use bounded **waveform profiles**; no V1 automatic hover/position hold claim. | `12` F-07, `28` |
| **INT-10** | MEDIUM | Different documents refer to servo “angle” without distinguishing calibrated linkage command from actual measured wing flap angle. | Define units/frames: servo pulse µs, servo command deg, **measured wing angle deg**; never infer one from the other without calibration. | `23`, `28`, `31` |
| **INT-11** | MEDIUM | Optional LED C1 can add outboard inertia, rail noise and timing load. | Re-qualify C1 separately; never treat LED as a cosmetic change alone. | `20`, `24`, EE-T14 |
| **INT-12** | TRACEABILITY | Three upstream ESP-FLUTTER files in archive were absent from owner's `git ls-files` even though `status --short` was blank. | Verify whether ignored/untracked or different provenance; keep findings using them qualified. | `12` F-13, `15` §3 |
| **INT-13** | WORKFLOW | No approved design revision or owner's authorization to issue `Task/` yet. | Finish bounded G0 review and record explicit owner approval. Do not let developer fill safety-critical TBDs by guessing. | `07`, `10`, `11`, `30` |

## 3. Boundary and responsibility review

**Pilot path:** TX radio → bound RX → electrical UART → protocol decoder/receiver health → validated pilot demand → source/arming supervisor → motion planner → envelope gate → actuator IO → airframe. No UI callback or RF interrupt may bypass the central gate.

**Configuration path:** grounded + DISARMED + authenticated local bench context → schema and range validation → versioned configuration → atomic commit with audit log. Do not write trim, profile or safety limits while armed. **Config transport unavailable or compromised must not revoke RC control or corrupt a valid currently active state.**

**Observation path:** state, command and measurements → read-only structured event log → local debug/optional UI. Observed source voltage is not equivalent to an accurate remaining-capacity estimate.

**Bench vs flight:** G1 software simulator and G2/G3 physical bench are progressively distinct; their safe-stop semantics are not transferable to G4 without review. Flight approval includes site, trained pilot, emergency response, exclusion zone and appropriate local permissions.

## 4. Engineering invariants for V1

1. **Single actuation authority:** one approved pilot source; flight control = RC only.
2. **Default deny:** after any boot/restart/unknown config, no automatic armed output.
3. **Validated provenance:** malformed/unknown/stale sources never refresh control authority.
4. **Separation:** decoder, safety supervisor, planner, servo driver, UI have distinct interfaces and tests.
5. **Measured limits:** no physical servo pulse/angle/slew/amplitude beyond the tested per-airframe envelope.
6. **No flight “safe-stop” fiction:** response to loss of control depends on measured aircraft; G4 is blocked until a contingency is justified.
7. **Engineering reproducibility:** each test has board/airframe/config revision, source commit, conditions, expected/actual, artifacts and reviewer.
8. **V1 honest scope:** no position hold, GPS/autonomy or “hover” label without demonstrated corresponding behavior.

## 5. Next review package

- `27_SAFETY_AND_FLIGHT_STATE_MACHINE.md` — approved-state proposal and hazard-aware transitions.
- `28_FIRMWARE_MODULE_AND_TIMING_CONTRACT.md` — software boundaries, scheduling and data definitions.
- `29_REQUIREMENTS_INTEGRATION_TRACEABILITY.md` — all FR/NFR mapped; evidence still NOT RUN.
- `30_G0_DESIGN_FREEZE_READINESS.md` — controlled approval checklist and implementation boundaries.
- `31_FLIGHT_CONTROL_FEASIBILITY_RISK.md` — physics/control authority questions before G4.

**Disposition:** advance design; **do not authorize purchasing, servo operation or flight** on this document alone.
