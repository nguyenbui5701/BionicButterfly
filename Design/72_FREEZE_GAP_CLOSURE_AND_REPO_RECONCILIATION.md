# BionicButterfly — G0-A1 Gap Closure and Repository Reconciliation Procedure

> **Phase 2.4 review note (2026-11-12):** See the candidate corrective addendum at the end and `84–90` before treating older priority/approval text as normative. **Pending owner approval; not code or flight authorization.**

- **ID:** BB-G0A-GAP-072 | **Version:** 0.2 | **Date:** 2026-11-12
- **Author:** SA | **Status:** REVIEW PLAN / NOT COMPLETED
- **Scope:** reconcile actual owner `Design/` with the **proposal** 66–71 before any design approval. Do not treat a document present on `main` as automatically approved.

## 1. Required repository evidence before freeze

| Check | Exact evidence | Current disposition |
|---|---|---|
| Repo baseline | repository URL, branch, HEAD SHA, `Design/` tree path list | **UNVERIFIED remotely** in this session |
| Phase 2.0 files | sha256 and revision for each `48…55` on owner `main` | LOCAL ZIP COPY only; owner Git not compared |
| Phase 2.1 files | whether `56…65` exist on `main`, exact bytes and any edits | LOCAL ZIP COPY only; Git state UNKNOWN |
| Phase 2.2 proposal | compare `66…74` to any owner edits when integrating | new additive package; no prior paths overwritten |
| Approved design slice | explicit owner comment APPROVE G0-A1 referencing exact files, policy and commit | **NOT APPROVED** |
| Reference license/provenance | source-permission inventory for any imported snippet/CAD | OPEN, not required for purely original host code if no copying |

**Read-only check example for owner-controlled Windows project** (optional at review time; these are **not push commands**):

```powershell
# Run from BionicButterfly repository root, only if reviewing baseline
# git rev-parse HEAD
# git status --short
# git ls-tree -r --name-only HEAD Design
# git log -1 --format="%H %cI %s" -- Design
```

If the remote checkout is not available to SA, use an owner-provided file listing and exact commit SHA with hashes as provisional evidence; do not claim independent remote reconciliation unless source content was actually inspected. The clean status of the **reference** ESP-FLUTTER clone is unrelated to proof that BionicButterfly Design is synced.

## 2. Proposed source corrections after owner approval

Do not rewrite earlier approved files wholesale. At a later controlled revision, apply explicit amendments below as appropriate, preserving change history:

| Prior file | Clause requiring review | Proposed resolution now owned by | Test consequence |
|---|---|---|---|
| `51_G0A_PC_SIMULATOR_CONTRACT_CANDIDATE.md` | illustrative YAML and unspecified policy | `57`, `67`: JSON v1, SIM_ONLY complete proposal | P22-T01/17 |
| `57_CANONICAL_SIM_SCHEMAS_AND_ERRORS.md` | JCS/float wording not fully pinned | `69`: canonical JSON, bounded integer trace effort and separate float tolerance | P22-T01/19 |
| `58_DETERMINISTIC_SAFETY_FSM_SEMANTICS.md` | low/high timing, ACK and fault behavior TBD | `67–68`: explicit virtual qualification and no re-arm | P22-T02–14/23 |
| `59_VIRTUAL_TIME_EVENT_REPLAY_SPEC.md` | grouping and cross-schedule equivalence | `68–69`: single fixed tick in G0-A1; off-grid events folded atomically; cross-tick-size deferral | P22-T08/09/19 |
| `60_SIM_CONFIGURATION_PROFILE_GOVERNANCE.md` | optional mutable disarmed profile vs disk rollback | `70`: immutable config for entire run; writes denied, deferred persistent path | P22-T15 |
| `61_CORE_API_AND_SEQUENCE_DESIGN.md` | possible unspecified app services | `70`: preloaded host-only policy, no hardware/video/browser privilege | P22-T16/20 |
| `63_G0A_TEST_MATRIX_AND_COVERAGE.md` | G1B-15 optional, PC-A15 comparison | `71`: explicit test dispositions and narrow freeze scope | test ledger revised |
| `64_PHASE21_FREEZE_REVIEW_PACKET.md` | approval blocked by missing policy + remote baseline | `74`: review conditional and still blocked by exact Git proof | no false APPROVED |
| `49_CROSS_DOCUMENT_CONFLICT_REGISTER.md` | CF-04/08/10/11/13/16/17/18 | proposed host-specific fixes `66–71`; closure still depends on owner's actual file revisions | DF / G1B suites remain NOT RUN |

**IMPORTANT:** `P22-C01…12` are new internal issues and do not replace global `CF-01…18`. Safety/hardware blockers `CF-02/03/05/06/07/12/15` cannot be closed by host-only simulation.

## 3. Evidence checklist for owner review and SA PR review

1. Compare current `main` content to SHA manifest; record path-by-path `MATCH / EDITED / MISSING / SUPERSEDED / UNVERIFIABLE` with diff link and reviewer.
2. Re-read the *latest* `02`, `07`, `10`, `11`, `27–30`, `48–65` revisions for scope and safety consistency; do not assume older artifact ZIP is canonical.
3. Accept/revise policy proposal `67` **for PC only**, including units, boundaries, status TTL, max resource constraints and runnable approval mechanism.
4. Accept/revise same-tick semantics `68`, deterministic trace `69`, immutable run config `70`, and test oracles `71` **as a set**, because an isolated edit can change safety outcomes.
5. Explicitly list exclusions (hardware output, real RF, RC binding, flight contingency, physical wing forces and V2 autonomy).
6. Owner issues clear `APPROVE / REQUEST CHANGES / DEFER` for **G0-A1 only**, with exact version/commit and permitted next scope. “Tiếp tục”, adding files or pushing do not imply APPROVE.
7. If and only if later authorized, SA creates narrowly scoped `Task/` file pointing to approved Design commit. AI Developer works in `Source/`, includes executed test evidence, opens PR. SA reviews PR in `ReviewPR/`, does not mutate Developer branch.

## 4. Validation statuses — don't conflate

- **DOCUMENT_PACKAGE_VALIDATED**: archive paths, UTF-8, numbering, SHA-256 self-check and crossrefs checked. Does **not** prove runtime semantics.
- **DESIGN_REVIEW_READY**: coherent candidate, open issues classified and review packet complete; **still requires owner signoff**.
- **DESIGN_APPROVED**: owner explicitly accepts a scoped revision after baseline reconciliation.
- **IMPLEMENTATION_TESTED**: actual code built and tests executed, all evidence traceable.
- **FLIGHT_QUALIFIED**: a completely different and later G4 decision, requiring physical evidence.

Current Phase 2.2 may claim at most DOCUMENT_PACKAGE_VALIDATED after archive checks. It cannot claim source repo equality or test PASS.

## Phase 2.4 repository access change (rev 0.2)

**FRZ-01 repository access blocker is now resolved as of 2026-11-12:** GitHub connected repo `nguyenbui5701/BionicButterfly`, `main@16d5054ea951b2e52e90c7f81ea2767a7ba82b92` was accessed and `Design/75–83` blob hashes matched delivered local documents. See `88`. This does **not** approve semantics, policy values, test results or flight readiness. Source branch HEAD must be rechecked before changes are applied.
