# BionicButterfly — TASK-001 Merge Closeout & TASK-002 Release Baseline

- **Document:** BB-P214-157 · **Date:** 2026-11-13 · **Role:** Solution Architect
- **Verified GitHub repository:** `nguyenbui5701/BionicButterfly`
- **Verified main:** `ca457f784975c2d0959b1baf988483fa042f5c67`
- **PR #1:** `https://github.com/nguyenbui5701/BionicButterfly/pull/1` — `merged=true`, merged 2026-11-13T09:20:10Z.
- **Task-001 PR head:** `4390a26514e6bab1870a1f3e94f14ced09eba69a`.
- **Safety scope:** G0-A1 `PC_SIM_ONLY`. Hardware bench/air flight G0-B/G4 remain NO-GO.

## 1. Evidence-supported TASK-001 closeout

The owner performed a final acceptance check at PR head `4390a265`: `scripts/verify_baseline.py` reported **32 exact Git blobs and 2 release artifacts MATCH**, `pytest -q` reported **203 passed / 2 warnings**, and `scripts/smoke.py` reported **6 PASS / 0 FAIL**. Two warnings were `PytestCacheWarning`, WinError 5 writing the optional `.pytest_cache`; they were not test failures. SA independently inspected GitHub PR source, test evidence and contracts, resolved finding `BB-PR-001`, and posted final review comment ID `5888668836`. SA did not run those tests inside an isolated local checkout; evidence is **owner-executed and GitHub-reviewed**, not SA-independent runtime certification.

**Decision:** TASK-001 is **CLOSED / MERGED / OWNER-ACCEPTED** for its limited pure host library. This is not G0-A1 complete simulator readiness and not a hardware clearance.

**Task hygiene:** `Task/TASK-001_HOST_PREFLIGHT_M0.md` remains in Git `main` with historic `OPEN` text. Its authority is superseded **for status only** by this closeout record. The owner may remove that task file from the active `Task/` folder in a later controlled documentation commit; Git history retains the task. **Do not mutate the old task to falsify past status** and do not remove it without checking uncommitted work. Until cleaned up, Developer must execute only the *explicitly assigned* TASK-002.

## 2. Immutable release source for TASK-002

- Parent main commit: `ca457f784975c2d0959b1baf988483fa042f5c67`. This is the only confirmed source baseline for the initial TASK-002 release; compare actual branch content before coding.
- TASK-001 reusable API: `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py` exposes `AcceptedPreflight`, `RejectedPreflight`, `validate_wire`; accepted `scenario` is deeply immutable (`MappingProxyType`, tuples, exact integers/Decimal).
- `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` controls tick intervals and batch semantics; `Design/132_...` supplies validated wire-v2 clock/duration/events constraints; `Design/141_...` records approved precedence.
- **No new owner decision** is required to implement the *already-approved pure tick grouping algorithm*. A new interface format is internal implementation detail only, not a new public scenario/trace contract or G0-A1 runtime approval.

## 3. Scope discipline

TASK-002 shall implement a pure virtual tick **enumerator and unnormalized event batches only**. It may not perform RF status resolution, validate a new wire version, determine ARM/FAULT, aggregate conflicting control frames, compute output M0, authorize simulation, write trace/hash, talk to devices, or create IO adapters. Independently trusted host allowlist, SafetySupervisor and TraceCommitter are future tasks, not implicit outcomes of schedule enumeration.

## 4. Owner → Developer handoff

The owner can unzip this package into the repository and choose when to commit/push the new docs and task. Developer reads `Task/TASK-002_VIRTUAL_TICK_SCHEDULER.md` and confirms a pinned baseline. The owner continues to run copy-paste smoke commands and perform UAT. Developer handles coding/debugging/tests and **does not open a PR until the owner explicitly instructs it**. SA reviews PR in a separate `ReviewPR/pr-<number>` worktree.
