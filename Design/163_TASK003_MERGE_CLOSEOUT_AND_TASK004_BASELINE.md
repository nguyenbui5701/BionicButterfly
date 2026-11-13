# BionicButterfly — TASK-003 Merge Closeout and TASK-004 Baseline

- Document: BB-P216-163 | Role: Solution Architect | Date: 2026-11-13
- Repository: `nguyenbui5701/BionicButterfly` | source: `main` commit `ed106d22c52647090768ef60fb1e4c33384e9227`.
- PR #3: https://github.com/nguyenbui5701/BionicButterfly/pull/3 — GitHub confirmed `merged=true` at `2026-11-13T12:14:23Z`.
- Merge commit: `ed106d22c52647090768ef60fb1e4c33384e9227` | reviewed PR head: `2cb7b2ec172247b85123394d1af698c8da3e6bb8`.

## TASK-003 closeout

**CLOSED / MERGED** for its **PC-only, pure full-tick observation-normalizer** scope. Owner indicated TASK-003 UAT was completed before PR. Developer-submitted and SA-reviewed JUnit evidence showed TASK-003 **59/59 PASS**, TASK-001 regression **203/203 PASS**, TASK-002 regression **44/44 PASS**, and smoke **10 PASS / 0 FAIL**. SA review ID `5890780869` found no BLOCKER/MAJOR in PR #3. SA did **not** independently run the tests in a separate worktree, and did **not** approve a physical flight gate. The `main` merge is verified by GitHub; existing historical Task records should be preserved in Git history even if cleaned from active Task folder by the Owner later.

## TASK-004 decision

**Implement only pure temporal health *facts* (Stage B)** after TASK-003, before a full SafetySupervisor. Required: exact 200,000µs independent age checks for previously committed accepted-control and uncontradicted healthy-RF timestamps, plus *uncommitted* current-tick candidate timestamp facts. Do **not** implement state transitions, RF effective-state winner, control authority refresh, ARM qualification, hazard cause priority, output or trace transaction.

The most important R1 rule is that **new raw UART VALID while RF LOST/UNKNOWN must not refresh accepted pilot authority**, and **a timed tick cannot manufacture a new accepted frame**. Therefore TASK-004 must **not update a stored snapshot** from current observations. The future separately authorized SafetySupervisor will own acceptance and commit after the entire tick batch is resolved. Never conflate timestamp freshness with RF health, an ARM permission, or output authorization.

## Authority and scope

- R1 approved `Design/115`, `116`, `117` govern state/authority and numeric timeouts; R1.1 hierarchy `141` keeps frozen wire-v2 and event semantics.
- Fixed evaluation ticks are from TASK-002; current observations are from TASK-003; both are **read-only**.
- No scenario/user-provided approval, no host policy/engine allowlist, no new wire schema/`E_*` codes, no real receivers, UART, PWM, GPIO, servo or flight. G0-B and G4 remain **NO-GO**.
- Source baseline for Developer: **exact** `ed106d22c52647090768ef60fb1e4c33384e9227`. Do not use movable `main` as a substitute for pinned review evidence.
- Owner manages unzip/docs Git commit/push and final UAT. Developer only edits `Source/host_temporal_guard_facts/**`; PR only on Owner's explicit instruction. SA reviews an isolated `ReviewPR/pr-<n>` checkout and never merges on the Owner's behalf.
