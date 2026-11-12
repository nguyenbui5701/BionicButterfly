# BionicButterfly — Phase 2.0: System Design Baseline Audit

- **Document ID:** BB-BASELINE-048 · **Version:** 0.1 · **Date:** 2026-11-12
- **Author:** Solution Architect (SA)
- **Status:** **REVIEW DRAFT — BASELINE NOT VERIFIED AGAINST OWNER REPOSITORY**
- **Design goal:** V1 = real powered free flight under physical handheld RC; V2 = autonomous flight only afterward.
- **Stage:** Phase 2.0 / System Design Freeze Preparation. **No implementation or flight authorization.**

## 1. Why this audit is conditional

This package was drafted from the **document descriptions and revision history exchanged in the conversation**, a locally available `P1_Source_Audit.zip`, and current vendor technical docs. **The owner's current Windows `BionicButterfly/Design/` Git working tree and its actual HEAD commit were not mounted in this session**. Therefore:

- `01–47` below represent a **previously reported design inventory**, not files independently reopened at their latest committed revisions during this Phase.
- All issue statuses in `49` mean **needs local verification**, even when the issue was previously described as resolved.
- **No real Git commit or GitHub push was performed**. Do not assume document hashes, parent revisions or source-code state without a local check.
- This Phase 2.0 archive is **additive only**, containing `Design/48–55` and a content-integrity manifest. It deliberately does not overwrite `Design/01–47`, `Source/`, `Task/` or `ReviewPR/`.

The original source archive still visible in this session includes 26 entries spanning ESP-FLUTTER / S-DiY files. As reported in the previous audit, ZIP files may contain files not present in the tracked Git snapshot. This **does not establish** that those files belong to the reference commits.

## 2. Design-document inventory: reported history vs verification requirement

| Reported ID group | Intended authority / scope | Last reported phase | Actual latest Git revision checked now? |
|---|---|---|---|
| `01` + `12` | External source provenance / firmware audit | P1 static audit | **NO** |
| `02`, `03`, `05` | Requirements / hardware / pilot UX | requirements and later addenda | **NO** |
| `07`, `10`, `11` | AI Dev / SA role separation / PR process | project workflow | **NO** |
| `13–16` | system architecture / verification / decisions / RC contract | integration + pilot design updates | **NO** |
| `17–21` | mechanical feasibility / concept / BOM / review | mechanical concepts | **NO** |
| `22–25` | power / pinout / electrical tests / hazards | electrical design | **NO** |
| `26–31` | integrated system / safety FSM / modules / traceability / freeze / controllability | integration review | **NO** |
| `32–36` | physical RC pilot / calibration / ground UI / RC test / human hazards | pilot design | **NO** |
| `37–41` | 6DOF model / control-identification / manual strategy / acceptance / trade study | flight dynamics | **NO** |
| `42–47` | CAD datum / linkage / wing material / inspection / rig / mechanical gate | mechanical detailed design | **NO** |
| `48–55` | current Phase 2.0 review supplements | this package | **YES, locally generated only** |

**Caution:** Some older source files were updated in multiple Phase ZIPs. Latest *known-name* is not synonymous with latest *content revision*. In particular verify `02`, `14`, `15`, `19`, `27`, `28`, `30`, `37` before a Design Freeze decision.

## 3. Design source-of-truth policy (proposed)

- The authoritative Design is the **owner's Git repository at an explicitly recorded commit**, not the last chat ZIP, an untracked folder or a copied reference clone.
- Once reconciled, `Design/02_V1_REQUIREMENTS.md` is the requirement source; `15_V1_DECISION_REGISTER.md` the approved-choice index; `14_V1_VERIFICATION_PLAN.md` the G0–G4 gate index; `27/28` the safety and firmware contracts; `30` the tiered freeze authority. This Phase supplements them, never silently supersedes.
- If there are multiple differing revisions, compare and resolve conflicting passages; do not merge by blindly appending both incompatible statements.
- Each released requirement/ADR has unique ID, status, owner, revision and exact approval evidence; every implementation task will reference frozen revision and Git commit.
- `DRAFT`, `PROPOSED`, `OWNER-DECIDED`, `APPROVED FOR G0-A`, `APPROVED FOR G0-B`, `APPROVED FOR G4`, `SUPERSEDED` are distinct statuses; a user request to *continue designing* is **not** an approval of specifics.

## 4. Baseline provenance and read-only reconciliation procedure

Before claiming the freeze is verified, the SA must inspect the real repository **without altering Developer work**:

1. Record repository root, branch, `git rev-parse HEAD`, `git status --short`, and whether prior changes are committed. An empty `--short` does not reveal ignored files.
2. Enumerate `Design/` with exact paths, files and committed version; compare to this declared inventory. Avoid treating external `ESP-FLUTTER-reference` and `SDIY-reference` clones as local authoritative code.
3. Read `02`, `14`, `15`, `16`, `19`, `27`, `28`, `30`, `37`, `42` for conflicts `49` lists. Review git diffs of any updates after the last prior ZIP.
4. Verify all cited file paths exist and are linked correctly; check each document's status, linked requirement IDs and test IDs.
5. Reconcile missing parts with an explicit change record. Do not unilaterally overwrite owner edits in `Design/` from an older ZIP.
6. Run document-level checks `DF-01..DF-18` in `52` and attach an evidence packet to owner review.

No commands that push or merge to GitHub are included: the owner has explicitly reserved when to push.

## 5. Confirmed vs unconfirmed statements

**Confirmed by owner's previous messages:** final V1 is physical RC manual flight; V2 autonomy later; SA works predominantly in Design; SA hands Developer tasks only after Design approval; PR reviews use isolated `ReviewPR/`; owner controls timing of GitHub push.

**Not confirmed by documents alone:** two-servo viability, XIAO pin-level board compatibility, chosen ELRS radio revision, real mass/CG, safe in-air failsafe, actual hovering/turning capability, exact servo/calibration/profile limits, successful G1/G2/G3/G4 test, release-grade CAD, mechanical/flight legality for the future site.

## 6. Result for Phase 2.0

- Design work can proceed as **review/reconciliation**.
- A **bounded G0-A software/simulator design** can become a separate owner-approved slice after conflicts and contracts are explicitly accepted; this is not permission to code yet.
- G0-B bench hardware and G4 flight remain blocked on different evidence. There is no single global ‘V1 design approved’ flag.
- **Handoff status: NO `Task/` issued; no PR checkout or review; no Git commit performed in owner's repository.**
