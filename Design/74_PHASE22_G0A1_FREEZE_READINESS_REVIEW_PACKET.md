# BionicButterfly — Phase 2.2 G0-A1 Design Freeze Readiness Packet

- **ID:** BB-G0A-REVIEW-074 | **Rev:** 0.1 | **Date:** 2026-11-12
- **Author:** Solution Architect | **Verdict:** **CONDITIONAL REVIEW CANDIDATE — NOT FROZEN, NOT APPROVED**
- **Scope requested for possible future owner approval:** **PC simulator core only**. Real flying butterfly V1 and its RC transmitter are product goals, not outcomes proven by this package.

## 1. What this phase actually accomplished

| Area | Artifacts | SA assessment | Status |
|---|---|---|---|
| Local source baseline | `66` and manifest | Reviewed actual local Phase 2.0/2.1 artifacts; owner Git HEAD not independently fetched | PARTIAL / REPO UNVERIFIED |
| SIM numerical limits | `67` | Concrete SIM_ONLY candidate policy and boundary arithmetic | PROPOSED |
| FSM and atomic event semantics | `68` | Explicit low/high arm protocol, snapshot transitions and fault precedence | PROPOSED |
| Deterministic replay and evidence | `69` | JCS candidate, normalized virtual trace and equality scope | PROPOSED |
| Config and interface scope | `70` | Config immutable per run; no hardware I/O; persistence deferred | PROPOSED |
| Test acceptance oracles | `71` | 24 specific cases P22-T01…24; clear older test deferrals | SPECIFIED, NOT RUN |
| Cross-document fixes and governance | `72–73` | Correction targets, acceptance dependencies and ADR D-059…066 | PROPOSED |
| Package integrity | ZIP manifest/checks | May be called validated **after** local checks | DOCUMENTATION ONLY |

No `Source/` modifications, runtime execution, servo power-up, RC flight, test results or `Task/` issuance occurred in Phase 2.2.

## 2. G0-A1 scope boundary — exact inclusion and exclusion

**Potentially included after explicit owner design approval:** strict scenario JSON, single fixed virtual scheduler tick, validated simulated RF/control inputs, central authority/FSM, bounded normalized virtual wing requests, immutable SIM_ONLY policy, canonical read-only trace, offline replay and failure reporting. No app/browser UI is needed to meet first G0-A1.

**Excluded:** physical UART/PWM, ESP32, LiPo, servo, RF link pairing, true control gains, onboard IMU/stabilization, 6-DOF predictive flight, flight-specific E-stop/RC link contingency, full app UI, persistent profile editor, variable tick schedule equivalence, C0/C1 flight readiness, autonomous V2.

**Architectural guard:** an output `left_micro_effort=200000` means normalized virtual actuator demand 0.2, NOT 200000µs servo pulse and NOT lift. A host-only simulation cannot be relabeled a hardware flight controller by configuration.

## 3. Required approval conditions (all must be addressed)

| ID | Condition | Evidence / deliverable | Current |
|---|---|---|---|
| **FRZ-01** | Reconcile actual `main` SHA and versions of `48–65` | per-path SHA/diff and reviewed conflict resolutions `66/72` | **BLOCKED: remote unreadable in this session** |
| **FRZ-02** | Owner accepts G0-A1-only capability boundary | explicit scope approval for `56/66/70` | **PENDING** |
| **FRZ-03** | Owner accepts or modifies all SIM_ONLY numeric guard/resource values | approved `67` with revised tests if modified | **PENDING** |
| **FRZ-04** | Owner accepts state/tick/recovery semantics and no midair interpretation | approved `68` and relevant conflict dispositions | **PENDING** |
| **FRZ-05** | Serialization/replay and input format agreed | approved D-059/062/064, `69` test vectors | **PENDING** |
| **FRZ-06** | In-run profile persistence scope agreed | approved D-063/`70`, deferred CFG-05/G1B-15 recorded | **PENDING** |
| **FRZ-07** | Requirement/test coverage reviewed and exclusions documented | `52`, `63`, `71` with no critical unhandled scenario | **PENDING** |
| **FRZ-08** | Safety boundary explicitly prohibits physical I/O and unqualified airborne failsafe | review `58`, `62`, `66`, `68`, `70` | **PENDING** |
| **FRZ-09** | SA & owner approve exact Design freeze commit/revision | signed scoped decision ID and SHA after repository reconciliation | **PENDING** |
| **FRZ-10** | Separate decision whether to produce a Developer Task | explicit later user instruction, not inferred from this review | **NOT AUTHORIZED** |

## 4. SA disposition

- **Recommend:** retain G0-A1 as *narrowly scoped* host-only architecture. Candidate numeric values should be adopted **only** after owner review and incorporated into a recorded policy revision. Continue design reconciliation instead of choosing hardware values without measurement.
- **Do not recommend:** claiming full V1 architecture frozen, issuing firmware coding tasks based on unapproved parameters, treating virtual RF status as real control, configuring physical servo PWM from SIM_ONLY settings or treating missing `main` access as proof that the push failed.
- **Retain open:** Phase 2.0 physical issues `CF-02/03/05/06/07/12/15`, provenance and all measured flight dynamics. `G0-B=HOLD`, `G0-C/G4=NO-GO`.

## 5. Subsequent design activity (before any Developer task)

1. Reconcile `Design/` against exact owner Git commit and fix host-scope contradictions in the canonical source documents via controlled change review, **without overwriting unrelated owner edits**.
2. Present the policy and G0-A1 boundary for explicit owner approval or revisions.
3. If approved, prepare a signed design-freeze snapshot with baseline commit and approved schema/policy hashes; only then consider preparing a limited `Task/` if the owner separately requests it.
4. In parallel the SA can continue **G0-B candidate hardware risk/design** studies without implying physical authorization; there is no need to select unsafe component values to close a pure-simulator contract.

## 6. Decision form (no decision recorded yet)

```text
Review ID: G0A1-P22-____
Owner Git Design HEAD (exact): NOT VERIFIED
Phase 2.0 baseline content hashes: LOCAL MANIFEST ONLY
Phase 2.1 baseline content hashes: LOCAL MANIFEST ONLY
Phase 2.2 files and SHA manifest: attached
Bounded scope: PC_SIM_ONLY
Policy: SIM_POLICY_CANDIDATE_22A (DRAFT, not execution-approved)
Conflict disposition: P22-C01…12 reviewed?
Test design: PC-A01…20, G1B-01…24, P22-T01…24
Physical safety boundary: G2/G3/G4 out of scope
Owner decision: PENDING
SA reviewer:
Authorization to create Task/ later: NOT GIVEN
```

**Final status on 2026-11-12:** Phase 2.2 document package prepared; **G0-A1 DESIGN FREEZE NOT APPROVED**, G1 test execution **NOT RUN**, physical flight **NOT QUALIFIED**. Owner handles all GitHub pushing.
