# G0-A1 — Residual Findings, Risk Boundaries and R1.1 Change Control

- **Doc:** BB-P211-RISK-145 · **Status:** Approved *interface design* with open runtime and handoff prerequisites.

## 1. Closure of the three Phase 2.9 interface defects

| Finding | Before R1.1 | After owner approval at verified Git HEAD | Status |
|---|---|---|---|
| **P29-F01** input event grammar incomplete | RESET/ACK/catastrophe wire ambiguous | closed v2 schema + `132` chosen | **CLOSED_AS_DESIGN_DECISION**; runtime NOT RUN |
| **P29-F02** mixer not uniquely specified | multiple possible L/R transforms | exact integer M0 chosen; 12/12 static vectors match | **CLOSED_AS_DESIGN_DECISION**; runtime NOT RUN |
| **P29-F03** trace record shapes incomplete | different JSONL interpretations possible | closed header/tick/terminal/report schema chosen | **CLOSED_AS_DESIGN_DECISION**; runtime NOT RUN |

## 2. Remaining open risks (do not re-open closed decisions)

| ID | Level | Risk | Resolution gate |
|---|---|---|---|
| R11-GAP-01 | HANDOFF P0 for parser-report task | unspecified exact per-field parse issue-code taxonomy and diagnostic JSON path | SA addition/revision before implementing *full* diagnostic reporting |
| R11-GAP-02 | EXECUTION P0 | no installed immutable allowlist with vetted engine/scheduler revision | Must exist and be reviewed before any host runtime is trusted |
| R11-GAP-03 | EXECUTION P0 | authored ASCII JCS fixture not proof of Unicode/nonintegral canonicalization | Independent RFC8785 conformance before G1 PASS |
| R11-GAP-04 | EXECUTION P0 | trace quota, I/O failure, terminal handling not executed | Negative injection tests; no output on failure |
| R11-GAP-05 | TEST P1 | Unicode ID byte-length and bytewise ordering missing runtime checks | Add dedicated input/trace test vectors |
| R11-GAP-06 | DEFERRED | v1 migration, real voltage recovery wire, and unselected optional features | SA change request, never silent import |
| R11-GAP-07 | FLIGHT P0 | aerodynamic/control/power/in-air contingency unknown | G0-B/G4 remain separate NO-GO |

## 3. Change-impact policy

Change classes:

- **C0 — Editorial:** typography, links, contextual notes; preserve normative bytes and SHA, or issue an amended index if file bytes change.
- **C1 — Contract extension:** any allowed event tag, property, schema id, numeric precision, mixer sign, trace field, parser error code, result enum, policy value or failure behavior → **new contract revision + hash + approval + test oracle revision**.
- **C2 — Physical scope:** real receiver, PWM, servo, power, IMU or airborne policy → **not covered** by G0-A1 and must go through electrical/mechanical/flight safety review.

For an approved change, SA documents affected FR/NFR, interface, hazards, golden vectors, test IDs and Git SHA; owner approves before new normative bytes enter the freeze index. AI Developer cannot self-approve by editing a JSON field.

## 4. Ownership

Owner controls design decisions and Git push; SA owns contract reconciliation, safety/traceability and code-review gate; Developer may implement only scoped tasks after authorized handoff. PR review must use isolated `ReviewPR/` and document diffs/regression evidence. No unapproved physical test in this phase.
