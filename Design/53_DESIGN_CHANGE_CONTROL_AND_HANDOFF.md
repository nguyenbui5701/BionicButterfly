# BionicButterfly — SA / Developer Design Change Control & Future PR Handoff

- **Document ID:** BB-WORKFLOW-053 · **Version:** 0.1 · **Date:** 2026-11-12
- **Status:** PROPOSED supplements `07_AI_CODING_RULES.md`, `10_SA_OPERATING_RULES.md`, `11_HANDOFF_PR_WORKFLOW.md`.
- **Owner preference:** keep working mainly in `Design/`; do not emit push instructions after each section; owner decides GitHub push timing.

## 1. Responsibilities / write boundaries

| Role | Allowed working area | Not allowed without explicit separate approval |
|---|---|---|
| **SA** | `Design/` documentation, design diffs, decision/acceptance records; `Task/` **only after design approval** | writing production firmware while Developer works, changing active Developer branch, asserting physical tests PASS |
| **AI Developer** | authorized `Source/` / test paths enumerated by a task; may propose Design issue via review comment | silently editing `Design/` approvals, changing safety/failsafe or BOM because code is convenient |
| **SA PR reviewer** | isolated `ReviewPR/` checkout/worktree using exact PR commit and task baseline | altering active Developer workspace/branch; auto-merge or deleting active unfinished work |
| **Owner** | approves scope, risk decisions, source freezes, when to push/publish | approvals should explicitly distinguish G0-A, G0-B and G4 |

## 2. Phase artifact and Git record rules

1. Every authored `Design/` revision has document ID, version, date, status, owner, prerequisites and change record.
2. **When actual local Git repo is accessible**, SA commits design file updates as a coherent reviewed change, records the resulting commit ID and tests/doc audit; only then may report “committed”. `git push` is owner-managed unless separately requested.
3. **When repo is not accessible**, SA supplies additive ZIP and manifest/checksums, clearly states no commit or direct file change occurred. This document follows this latter case.
4. Avoid writing older copies over newer owner-edited file revisions. For a conflict, compare the current HEAD content and propose a reversible patch with explicit source revision.
5. Freeze only exact scope and exact commit: a draft ZIP, an unmerged PR and a user saying “continue” do not constitute approval.

## 3. Future Task creation gate (currently CLOSED)

Only after owner approves a bounded design slice, issue a `Task/TASK-xxx.md` with:

```text
Task ID / objective / bounded output
Owner-approved Design slice + Git commit, exact file list to read
Allowed paths + files Developer may modify
Out-of-scope controls and safety-critical parameters
Required tests and PASS evidence
Known unresolved hardware/flight hazards and mandatory sim-only labels
Acceptance and review roles
PR branch/target and instructions to link artifacts
```

**No Task file is included or authorized by this Phase 2.0 package.** A PC-only task remains a possible *future* deliverable, not a default.

## 4. Future PR review isolation and resolution

- SA checks out exact PR head into `ReviewPR/<PR-id-or-commit>/`; do **not** checkout over the Developer's active working tree.
- Review against task and Design commit: correctness, interface, state invariants, test results, security/provenance and changed file scope.
- Post a PR comment with file/line, severity `BLOCKER / MAJOR / MINOR`, repro/test ID and required fix. No empty generic approval.
- **If BLOCKER/serious MAJOR:** mark not ready for merge; preserve that `ReviewPR` checkout + related task and append numbered remediation work in task as agreed.
- **If no serious unresolved comment:** after review and posting a clear nonblocking verdict, clean up only *that* isolated PR checkout and corresponding resolved Task file **as the owner's agreed workflow directs**. Never delete another person's active checkout; verify path ownership and whether untracked evidence needs preservation before removal.
- PR merge, GitHub publish and source push remain under owner's control unless explicit permission and access exist.

## 5. Change classification

| Change category | Mandatory review impact |
|---|---|
| C-DOC: typo/format with no semantics | doc version and author check |
| C-API: event/field/state contract change | requirement trace and PC-A test impact |
| C-RC: protocol/arm/mapping change | input contract, vendor revision, fail-safe and G2 test impact |
| C-EE: pin/voltage/servo/BEC change | electrical hazard analysis, measured rails, G2 gating |
| C-MECH: wing/motor/CG/CAD change | mass/inertia, calibration, G3 force/torque and stability review |
| C-FLIGHT: emergency response/test site/control gains | new G0-C/G4 approval; never inherited from bench |

No approved safety-related change is “minor” simply because it touches one line of source code.

## 6. Current Phase 2.0 handoff record

- `Task/`: **none created**.
- `ReviewPR/`: **not accessed**.
- Owner source repository: **not mounted**.
- Git commit/push: **not performed**.
- Delivered: proposed `Design/48–55` plus SHA-256 manifest in a ZIP for owner-controlled integration.
