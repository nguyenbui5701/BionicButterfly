# BionicButterfly — Controlled Architecture Reconciliation Plan & Handoff Boundaries

- **ID:** BB-P27-CHANGE-112 | **Rev:** 0.1 | **Status:** CHANGE PLAN ONLY / NOT APPLIED
- **Git baseline:** `main@be85c3e28a2ba6891f2bd6199a58fe0ce564f305`.

## 1. Why no silent overwrites now

The repository contains multiple candidate rules from Phases 2.1–2.6. Older `58/68/84` priority or arming tables and the newer `100/101` proposal cannot all be considered the sole normative source simultaneously. A real design freeze requires a **file-by-file controlled reconciliation AFTER the owner has selected the semantic rules**. A new document numbered above `100` does not by itself rewrite older files; a Git push alone is not a normative endorsement.

## 2. Proposed edit batches after a later explicit owner decision

| Batch | Source files to reconcile | Required change | Re-review proof |
|---|---|---|---|
| R1 Safety FSM | `27`, `58`, `68`, `84`, `100`, `101` | one accepted PC-only priority, LOW/ACK/RESET/no-event contract; label older tables historical/superseded by exact accepted ID; do not overwrite physical flight policy | diff + selected ADRs + P26/P27 tests |
| R2 Schema and errors | `57`, `61`, `78`, `85` | input v1, result/errors v2, unique duplicate-ID vs runtime conflict semantics | schema examples + P27-T11 |
| R3 SIM policy governance | `67`, `70`, `87`, `102` | exact policy values and immutable external approval record; remove implication that a JSON boolean grants permission | digest calculation from approved typed bytes + P27-T12 |
| R4 Replay | `59`, `69`, `80`, `94`, `103` | complete trace header/ticks/terminal, external digest, run identity, failure behavior | byte-level conformance plan + P27-T13/14 |
| R5 Tests and gates | `63`, `71`, `79`, `86`, `95`, `104`, `111`; review `96`, `98`, `106` | coherent expected results and requirements coverage; explicitly separate design signoff and executable PASS | reviewed test index, critical safety cases |
| R6 Decision/register and traceability | `15`, `29`, `30`, `73`, `82`, `90`, `105`, `106`, `108`, `113` | record APPROVED/AMENDED/DEFERRED per ADR and exact HEAD; older proposal labels retained historically | signed decision + change log + Git diff |

R1–R6 refer to **future reviewed Design edits**, not code generation tasks. Preserve old text as historical where safe; include a clear supersession section with exact paragraph/table identifiers and avoid duplicating contradictory 'normative' requirements.

## 3. Safe Git reconciliation procedure — SA governance, not commands to push

- Check `main` HEAD again and capture original Git blob SHA for every target. If it has moved, perform a fresh semantic/diff review; don't overwrite someone else's newer edits.
- Create a bounded change set containing only reviewed `Design/` documents; explicitly enumerate which behavioral interpretations changed, why, and their oracle IDs.
- Evaluate markdown link paths, duplicate ADR IDs, scope labels `PC_SIM_ONLY`, and old per-file status lines. All semantic changes must be reviewed by SA and owner.
- Compute a new manifest/sha list and a distinct approved contract revision only after signed acceptance; do not invent an approval record in a candidate artifact.
- If requested in the future, review a Developer PR by checking out in isolated `ReviewPR/` and comparing with the approved Design revision.

## 4. Potential Development handoff boundaries (NOT a `Task/`)

If and **only if** owner approves G0-A1 and *later explicitly requests work allocation*, implementation can be divided into: strict JSON v1 input validation; trusted immutable SIM policy loader; deterministic virtual-clock batching; conflict-normalization and owner/safety FSM; virtual mixer/envelope; canonical trace/replay; security-negative and deterministic test harness. Each would cite exact revised Design file and acceptance IDs. Developer cannot resolve an unselected safety behavior by intuition. Physical UART/CRSF/servo and in-flight failsafe belong to a separate future authorization, not this slice.

## 5. Exact completion definition

**Design Closure:** selected ADR dispositions + an accepted revisioned normative contract, resolved P0 findings, reviewed change/diff evidence, approved SIM-only policy bytes/digest and owner decision. **Development Handoff Ready:** design closure plus separately approved scope/task plan and defined test harness; **not** equivalent to execution or code completion. **Flight Ready:** separate G0-B/G3/G4 evidence, never inferred from host simulation.

No repository edits, `Task/` creation or source implementation are performed in Phase 2.7.
