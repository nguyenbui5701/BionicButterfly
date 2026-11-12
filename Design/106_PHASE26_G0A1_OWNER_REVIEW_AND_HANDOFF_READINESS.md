# BionicButterfly — Phase 2.6 SA Review Decision Sheet and Handoff Readiness

- **ID:** BB-P26-GATE-106 | **Version:** 0.1 | **Status:** REVIEW PACKAGE PREPARED / UNSIGNED.
- **Git baseline:** `b6628e567813396c36d670d17e18f75e5cc443d3` (`BionicButterfly Phase 25`).
- **Purpose:** bring owner a finite set of proposed G0-A1 decisions, not keep adding unspecified feature scope.

## 1. Executive SA judgement

**Source-presence blocker P25-F01 is closed.** The code-independent host-only contract has meaningful candidate resolution across `100–103`, but **G0-A1 is not yet design-frozen**. The core priority, input policy, empty-tick semantics, error v2, fault recovery allowlist, exact hash/trace bytes and external policy authorization need an explicit owner selection on a revision. The project has **no executed simulator tests and no qualified physical flight evidence**.

| Gate | Current evidence | Decision |
|---|---|---|
| repo and P24/P25 source presence | GitHub connected, HEAD/SHAs verified | SOURCE VERIFIED |
| safety FSM candidate | `100/101` coherent draft after P25 findings | AWAIT OWNER APPROVAL |
| numeric SIM policy | `102`, unchanged 22A numeric proposal | AWAIT OWNER APPROVAL |
| recovery cause allowlist | `101` proposes recoverable subset | AWAIT OWNER APPROVAL |
| trace/replay format | `103`, draws from `94` | AWAIT OWNER APPROVAL |
| test oracle inventory | `104`, P26-T01…28; inherited PC-A/G1B/P22/P23/P24/P25 | SPECIFIED, NOT RUN |
| G0-A1 design freeze | no owner signature tied to exact approved policy + git ref | **HOLD** |
| G0-B/G3/G4 | real electrical/mechanical/flight dependencies unsatisfied | **HOLD / NO-GO** |

## 2. Explicit proposed decisions (not approved by continuing)

| ADR | SA recommendation | Owner choices | Condition |
|---|---|---|---|
| **D-083** | adopt fixed S1 on no-new-frame tick with dual freshness guards | approve S1 / adopt S2 / revise | `100`, P26-T15…19 |
| **D-084** | break LOW qualification on in-band INVALID, conflicting control, lost/unknown RF, RESET, HIGH | approve / amend | `101`, T10…13 |
| **D-085** | active critical hazard precedes ordinary RESET; catastrophic remains absolute latch | approve / amend | `100`, T08–09 |
| **D-086** | SELF_TEST may go DISARMED with RF UNKNOWN but cannot arm; critical power issue holds SELF_TEST | approve / amend | `101`, T23–24 |
| **D-087** | adopt proposed recoverable fault allowlist; no scheduler/internal numeric recovery without fresh run | approve / revise allowlist | `101`, T20–22 |
| **D-088** | adopt nonrecursive JSONL digest/external report, trace-commit-before-virtual-output contract | approve / amend | `103`, T25–27 |
| **D-089** | approve scope `PC_SIM_ONLY`, numeric `SIM_POLICY_CANDIDATE_22A` and independent trusted allowlist | approve exact version / amend | `102`, T28 |
| **D-090** | accept versioned input v1/result v2 & patch/traceability map; only then reconcile older docs | approve / amend | `105`, T06, T25 |

D-075…D-082 and previous decisions remain their historical PROPOSED status until explicitly accepted/amended, even if this review endorses a consistent consolidated alternative. Do not equate a Git push with implicit acceptance.

## 3. Suggested owner review record — intentionally empty

```text
Review ID:                  G0A1-P26-____________________
Reviewed Git repository:    nguyenbui5701/BionicButterfly
Reviewed HEAD SHA:          b6628e567813396c36d670d17e18f75e5cc443d3
Scope accepted:             PC_SIM_ONLY? APPROVE / AMEND / DEFER
Accepted normative documents/revisions: ______________________
D-083..D-090 disposition:   ________________________________
Recoverable cause allowlist version: ________________________
Accepted policy canonical bytes + SHA-256: __________________
Independent trusted owner approval ref: _____________________
Result schema/trace format versions: ________________________
Reconciled older doc versions/commit: ________________________
Acceptance test design IDs reviewed:  PC-A/G1B/P22/P23/P24/P25/P26
Owner decision:             APPROVE G0-A1 / REQUEST REWORK / DEFER
Owner decision evidence/date: __________________________________
Separate authorization to create Task/: NOT GIVEN
```

## 4. Potential Developer handoff — **NOT A TASK**

Only after approval, a later SA task plan could split work into: strict parser/validation, immutable policy loader, virtual scheduler and event normalization, safety FSM, virtual envelope sink, trace/replay writer and isolated host testing. Each task must cite exact Design revision and acceptance oracles. Do **not** ask Developer to choose missing safety semantics; ambiguous cases return to SA. Do not implement an ESP32 actuator driver or flight failsafe in this slice.

## 5. Final SA recommendation

**Continue design closure**, present D-083..D-090 plus inherited D-075..D-082 for explicit owner review, then prepare a controlled source-document reconciliation. Do not declare G0-A1 frozen solely because this ZIP exists. No `Task/`, no `Source/`, no Git commits/pushes performed by SA. V1 human-piloted physical flight and V2 deferred autonomy remain unchanged.
