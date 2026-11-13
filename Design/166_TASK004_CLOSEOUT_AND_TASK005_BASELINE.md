# BionicButterfly Phase 2.17 — TASK-004 Closeout and TASK-005 Baseline

- Document: BB-P217-166 · SA-issued · 2026-11-13 · scope **G0-A1 PC_SIM_ONLY**.
- Repository: `nguyenbui5701/BionicButterfly`.
- GitHub PR #4: https://github.com/nguyenbui5701/BionicButterfly/pull/4; verified `merged=true` at `2026-11-13T15:49:48Z`.
- Tested PR head: `1bf8333518ad9078ceefff28fd1d01036e7bcf1e`; verified merge commit and new `main`: `efe7fa3aff1beeb01af98b98a06593bd8e7af192`.
- SA code review on PR #4: review ID `5894009495`; no BLOCKER/MAJOR from connected GitHub source review.

## Closeout

Owner accepted TASK-004 UAT and merged PR #4. Developer-submitted GitHub XML evidence: TASK-001=203, TASK-002=44, TASK-003=59, TASK-004=140 tests; each 0 failures/errors/skips, total 446. Development + installed-wheel smoke each 12/12. Independent SA runtime execution was **NOT RUN**. Merged TASK-004 is an immutable PC-only age/candidate evidence component; it does not accept an RF/control observation, ARM, execute a safety state transition, or publish output.

TASK-004 is **MERGED / CLOSED FOR ITS SPECIFIED STAGE B SCOPE**. Historic `Task/TASK-004...` may retain OPEN in Git; this closeout supersedes that *status* only. Do not mutate old signed/frozen designs or silently remove previous task history.

## Next authority and deliberately narrow Stage C1

TASK-005 adds a pure **high-priority SafetySupervisor adjudication kernel** that only identifies high-priority provisional safety transitions and block facts. It explicitly does **not** implement the eight-state FSM end-to-end. In particular, it cannot process LOW/HIGH arming windows, maintain accepted committed RF/control timestamps, complete SELF_TEST readiness, ACK recovery, choose active effort or publish trace/output. Those later milestones require a full state owner, host trust and a trace-before-publish integration.

Why split: authoritative Design/115 has a well-defined priority hierarchy, while final health acceptance has unresolved interactions between current uncommitted candidates, prior freshness, and host-trusted critical-fault inputs. Collapsing all three into this task would invite an accidental new safety policy. TASK-005 is limited to unambiguous high-priority cases; all ambiguous/remaining transitions are **DEFERRED, not approved**.

**Frozen controlling sources unchanged:** Design/115–118, Design/132–134, Design/141, Design/164 and the approved SIM policy domain digest `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. G0-B/G4 physical and flight remain NO-GO.

## Work ownership

SA authors `Design/166–168` + `Task/TASK-005` and oracle recipes; Owner copies them into the repository, checks status/commits/pushes, and runs UAT; Developer only writes `Source/host_safety_priority_kernel/**`, never changes Design/Task/ReviewPR, and waits for explicit Owner permission before creating PR. SA reviews the PR; Owner alone decides merge.
