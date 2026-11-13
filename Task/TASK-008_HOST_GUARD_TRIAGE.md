# TASK-008 — HOST_GUARD_TRIAGE (SafetySupervisor Stage D2)

| Field | Value |
|---|---|
| Status | **OPEN — SA RELEASED / OWNER TO ASSIGN** |
| `main` baseline | `7c09bb5ab4d05d16bfa53439b5dab5b465ec8b05` (merged PR #7) |
| Scope | G0-A1 **PC_SIM_ONLY**, immutable fail-closed guard triage; **NO AUTHORITY** |
| Allowed Developer changes | `Source/host_guard_triage/**` only |
| Proposed branch | `feature/TASK-008-host-guard-triage` |
| PR policy | Only after owner UAT PASS + explicit permission; no automatic merge |

## Goal and rationale

TASK-007 classifies RF/control *diagnostic evidence*. Implement TASK-008 as a **pure, frozen, deterministic guard-triage report** using genuine TASK-003/004/005/007 records. Make risk/non-admissibility explicit and audit both prior control and RF ages for armed-state continuity. Keep the FUTURE trusted history/trace owner as an explicit boundary; this task is not that owner. Never treat `HEALTHY_CURRENT`, `HEALTHY_CARRIED`, `SINGLE_CANDIDATE`, a Python enum or a hash as authorized RF/control. No `PASS/ADMITTED` adapter to TASK-006.

## Mandatory reading, in order

1. Repository workflow: `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`.
2. Approved R1: `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md`, `116`, `117`, `118`; R1.1 hierarchy `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md`; frozen wire-v2 and SIM policy contract.
3. Earlier derived stage docs: `Design/161`, `164`, `167`, `170`, `173`; **read-only** SOURCE packages TASK-001…007, notably TASK-003/004/005/007 public APIs and frozen classes.
4. **New SA release:** `Design/175_TASK007_MERGE_CLOSEOUT_AND_TASK008_BASELINE.md`, **`Design/176_G0A1_GUARD_TRIAGE_STAGE_D2_CONTRACT.md`**, `Design/177_TASK008_GUARD_TRIAGE_ORACLES_AND_REVIEW.md`, `Design/fixtures/P220_GUARD_TRIAGE_ORACLE_INDEX.json`, `Design/P220_TASK008_RELEASE_MANIFEST.json`.
5. Verify parent Git HEAD `7c09bb5ab4d05d16bfa53439b5dab5b465ec8b05` and exact frozen blob/hash pins before coding. A discrepancy is **BLOCKED — DESIGN CLARIFICATION**, not a reason to alter approved R1 or guess.

## Implementation contract

- Implement Python 3.11+ `bb-host-guard-triage` 0.1.0 in new `Source/host_guard_triage/**`, public pure API `triage_guard_evidence(...)`, enums and **exact ten-field** `GuardTriageFacts`, as specified in Design/176.
- Enforce exact 5ms tick, 60s horizon, 200ms inclusive prior-age, independent RF and control status. Reuse **real existing** TASK-007 labels, reject contradictory upstream snapshots, and never re-parse or scan raw events/groups.
- RF lane: current healthy evidence only, carried healthy unverified, ambiguous, or not healthy. Control lane distinguishes absent, untrusted candidate, invalid/conflict, RF blocked/ambiguous and priority blocked. Armed continuity *prior stale* wins even with current healthy/control candidate; potential S1 remains **not authorized**.
- Frozen typed tuples, stable internal risk reason ordering (always end in `TRUST_NOT_PROVEN`), no output or state changes, no accepted timestamp updates. Never create an authority-bearing `health=PASS`, `control=ADMITTED`, `can_arm`, `rf_effective` or `output_allowed`.
- No code outside new task tree, no new wire events, no public E_* codes, no new policy or trace/allowlist/driver/firmware, no changes to TASK-006.

## Acceptance criteria AC-01…AC-10

| AC | Observable proof |
|---|---|
| AC-01 | Only task-local source/tests/scripts/evidence modified; upstream Source and frozen Design/policy unchanged; release doc files tracked unchanged only with explicit owner instruction. |
| AC-02 | All **36 P220-T01…T36** real TASK-001→002→003→004→005→007→008 oracles pass, exact ten fields and types, separate synthetic prior not in wire. |
| AC-03 | RF LOST dominates HEALTHY in same tick; HEALTHY+UNKNOWN remains ambiguous; old accepted HEALTHY never defeats carried LOST/UNKNOWN, regardless of original order. |
| AC-04 | RF 200000µs fresh / 200001µs stale and independent control age; no current frame candidate refreshes accepted prior time. |
| AC-05 | INVALID + VALID, conflict, duplicates and absence map to correct control lane and reason set; no accepted pilot intent from any diagnostic candidate. |
| AC-06 | RESET, catastrophe, latched and contingency have conservative priority; armed stale prior RF/control blocks continuity even with a current HEALTHY/VALID candidate; no S1 positive authority. |
| AC-07 | Wrong wrappers/enums, time grid, mirrors, malformed synthetic prior, forged or contradictory D1 evidence rejected; **18 negative families N01–N18**. |
| AC-08 | Frozen slotted ten-field record; internal ordered risk tuple; O(1) after TASK-007; deterministic; no upstream/event rescan, clocks, I/O, mixer, trace, state owner, output or hardware imports. |
| AC-09 | Real unit/integration, development + wheel smoke, compile/build/install/pip, exact pinned provenance, honest read-only TASK-001…007 regressions; compact JUnit/JSON with PASS/FAIL/ERROR/SKIP/warnings. |
| AC-10 | Three copy-paste PowerShell UAT commands + optional one-command aggregate verification, owner signs off; if unchanged no second complete regression just for PR packaging; Developer does not self-merge. |

## Required testing and handoff

Write `tests/test_oracles.py` mapping each P220 case to its genuine P219 recipe, keeping all synthetic pre-state/prior timestamps separate from wire JSON. Write independent negative tests for N01…N18; include exact armed continuity stale boundaries and S1 abstention. Test with previously merged packages installed **from local pinned source**, never same-named remote package substitutes. Regressions run in separate package cwd to prevent `scripts.scenarios` collisions. Provide a `scripts/verify.py` that verifies baseline and freeze hashes, performs build/install/pytest/regressions/dev+wheel smoke and records compact machine-readable evidence; avoid prose duplication of every case.

From `Source/host_guard_triage` after Developer prepares `.venv`, Owner uses:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
# Optional full final verification (Owner runs ONCE):
.\.venv\Scripts\python.exe scripts\verify.py
```

Developer reports READY FOR OWNER UAT with honest results and SHA of execution-affecting files. Owner runs final UAT once. Developer creates PR only after Owner explicit authorization; do not duplicate expensive work when tested bytes/dependencies unchanged. SA reviews the PR in isolation; Owner alone merges.

## STOP conditions

If the implementation would require host-allowlist provisioning, effective RF adjudication as authority, an actual trace-committed pre-state, `HypotheticalQualificationVerdict(PASS,ADMITTED)`, ACK recovery, SELF_TEST readiness, new wire critical-voltage/scheduler events, real PWM/RC/servo/flight or a policy revision, STOP and request SA change control. This task leaves those operations **NOT RUN / NO-GO**.

**TASK-008 status: Design only, implementation and UAT NOT RUN.**
