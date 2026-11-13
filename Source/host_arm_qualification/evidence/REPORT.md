# TASK-006 — READY FOR OWNER UAT

Date: 2026-11-13 (Asia/Saigon). Branch: `feature/TASK-006-host-arm-qualification`.
Pinned parent: `f2c9237bd4a1e2e077c15db6eb4c22ed2a250d5d` (merged PR #5).
Scope: Design/170 ARM Qualification Proposals Stage C2, PC_SIM_ONLY.
No staging, commit, push or PR. Owner UAT and SA review remain pending.

## Actual results

| Check | Actual result | Evidence |
|---|---|---|
| TASK-006 unit/integration, all 32 P218 oracles | **221 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [tests.log](tests.log), [tests.xml](tests.xml) |
| TASK-001 read-only regression | **203 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task001-regression.log](task001-regression.log) |
| TASK-002 read-only regression | **44 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task002-regression.log](task002-regression.log) |
| TASK-003 read-only regression | **59 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task003-regression.log](task003-regression.log) |
| TASK-004 read-only regression | **140 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task004-regression.log](task004-regression.log) |
| TASK-005 read-only regression | **208 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task005-regression.log](task005-regression.log) |
| Development smoke | **16 PASS, 0 FAIL** | [smoke.log](smoke.log) |
| Installed-wheel smoke | **16 PASS, 0 FAIL** | [wheel-smoke.log](wheel-smoke.log) |
| Compile, build wheel/sdist, install, both pip checks | **PASS**, all command exits 0 | [commands.json](commands.json) |
| Provenance | **37 pinned paths + 5 release artifacts + policy/blob guards MATCH** | [baseline.json](baseline.json) |

Total: **875 tests PASS**, plus both smoke runs. Windows AMD64 / CPython 3.11.15.
No failed tests/builds, errors, skips or warnings in the completed verification.
No runtime defect required a post-test fix. Exact versions, test counts, artifact
hashes and isolated installed-wheel environment: [environment.json](environment.json).

All five prerequisite wheels were built from exact baseline Git blobs in new
task-local cache directories, including manifest-required source/test/script/docs
inputs. No dependency package was fetched as a substitute for local source.
Installed prerequisite runtime bytes in both environments match baseline Git;
installed TASK-006 runtime matches source byte-for-byte. Owner `.venv` uses the
local prerequisite wheels and editable TASK-006. Read-only regressions run from
each prerequisite's own directory/interpreter, with `-B`, pytest cache disabled,
and JUnit files written only under TASK-006 evidence.

## Acceptance criteria

| AC | Result and executed proof |
|---|---|
| 01 | PASS: only new `Source/host_arm_qualification/**` files. AST import/call audit and side-effect/pipeline-rerun spies; prerequisite/frozen bytes unchanged. |
| 02 | PASS: all 32 real raw-wire preflight -> scheduler -> normalizer -> temporal -> priority -> qualification cases. Exact nine fields/types; synthetic state, timestamp history, windows and verdict never in wire JSON; unchanged input records and references. |
| 03 | PASS: 19999/20000/20001us LOW gaps, original timestamp anchors, duplicate same-tick group counted once, silence holds only, already-qualified LOW does not refresh qualification tick. |
| 04 | PASS: only prior committed LOW qualification supports HIGH; same/current commit rejected; flap 0.020000/2e-2 and steer +/-0.05 inclusive, 0.020001 and +/-0.050001 excluded, including Decimal precision 2. |
| 05 | PASS: 99999/100000/100001us HIGH gaps; later new frame/tick required; early HIGH retains original anchor; silence cannot confirm; nonneutral/failed health clears proposal continuity. |
| 06 | PASS: LOW disarm across ARM_CHECK/ARMED_IDLE/ACTIVE clears windows without LOW_START; ARMED_IDLE demand 0.049999/0.05/5e-2 vs 0.050001; ACTIVE HIGH returns NO_CHANGE without output. |
| 07 | PASS: FAIL/UNRESOLVED and current INVALID/conflict/LOST/UNKNOWN/RESET/catastrophe/stale armed ages cannot produce milestones; contradictory PASS/ADMITTED/ABSENT/DENIED assumptions reject. Interrupted LOW series restarts with a new anchor and needs another LOW. |
| 08 | PASS: closed enums and frozen exact nine-field output, prior window scalar/grid/state/pairing invariants, mirrored facts, exact upstream type rejection including subclasses. Poisoned events/members not read; identical runtime line counts for 1 vs 5000 real equivalent controls. Repeat determinism under locales/TZ values/Decimal contexts; no hidden window/history. |
| 09 | PASS: actual 203/44/59/140/208 regressions, build/install/compile, dev/wheel smoke, pip checks and pinned/installed source checks. No assumed PASS from design-only authorship. |
| 10 | PASS: prepared Windows `.venv`; three UAT commands below. No PR before explicit owner acceptance/permission; no self-merge. |

## Scope and remaining limits

- Runtime: `src/bb_host_arm_qualification/{__init__,qualification}.py`.
  Tests: `tests/{conftest,test_oracles,test_qualification}.py`.
  Helpers: `scripts/{__init__,scenarios,smoke,verify}.py`; packaging/README and
  evidence. [files.json](files.json) records complete task file hashes/scope.
- Design/Task release files remain unchanged and owner-managed/untracked as
  found. Existing TASK-001 evidence edit retains its recorded SHA-256. No edits
  to upstream source, schema, .github, ReviewPR, firmware or hardware. No Git
  staging, commit, push, PR or merge performed for TASK-006.
- No R1 policy conflict identified for the stated proposal mechanics. This is
  developer implementation evidence, not SA approval or safety certification.
  Hypothetical PASS/ADMITTED inputs are not an arbiter, trust token, real frame
  acceptance or permission. Even positive milestones always require full FSM.
- Prior-window checks reject impossible qualification chronology and same/future
  commit claims. An admitted HIGH in ARM_CHECK without an edge anchor rejects as
  a caller error; no confirmation is fabricated. A public record cannot prove
  actual committed history. Genuine TASK-003/004/005 outputs are required; nested
  source events remain upstream responsibilities and are not rescanned.
- CONTINGENCY ACK recovery is deferred with no new window. Proposed windows may
  be discarded; nothing commits state, accepted-control history or trace. No full
  FSM, effective RF/current-health arbiter, host allowlist, LOW/HIGH state owner,
  output/ACTIVE S1 hold, mixer, simulator runner, physical actuator/RC or flight.
  Full P28-T08/T09/T13/T14/T26/T27 and P210-T02 conformance is **NOT RUN / DEFERRED**;
  hardware G0-B/G4 remain NO-GO.
- Effective OS timezone switching is **NOT RUN** (Windows Python lacks tzset).
  Actual locales C/English_United States.1252, TZ environment values UTC0/ICT-7,
  and Decimal contexts passed. Runtime reads no clock/locale/environment.
- Aggregate verification requires prepared sibling regression venvs and the
  pinned build/test tooling in TASK-006 `.venv`. Fresh reviewer environments must
  prepare these prerequisites; owner UAT uses the already-prepared environment.

## Owner UAT: three PowerShell commands

Run from `BionicButterfly/Source/host_arm_qualification`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Expected: **221 passed**, **Smoke: 16 PASS, 0 FAIL**,
**No broken requirements found**. PR: **NOT CREATED — WAITING FOR OWNER**.

## All 32 oracle results

Each PASS is verified against the actual JUnit testcase, which compares all nine
fields and exact types, not just the proposal kind shown here.

| Oracle | Scenario | Expected proposal | Actual |
|---|---|---|---|
| P218-T01 | low_first | LOW_START | PASS |
| P218-T02 | low_gap_19999 | LOW_PENDING | PASS |
| P218-T03 | low_gap_20000 | LOW_QUALIFIED | PASS |
| P218-T04 | low_gap_20001 | LOW_QUALIFIED | PASS |
| P218-T05 | equivalent_low_same_tick_not_two_samples | LOW_START | PASS |
| P218-T06 | empty_after_low_holds_only | HOLD_WINDOW | PASS |
| P218-T07 | high_with_no_qualified_low | CLEAR_WINDOW | PASS |
| P218-T08 | high_with_unqualified_low | CLEAR_WINDOW | PASS |
| P218-T09 | high_edge_after_prior_low_qualified | HIGH_EDGE_ELIGIBLE | PASS |
| P218-T10 | high_non_neutral_flap | CLEAR_WINDOW | PASS |
| P218-T11 | high_neutral_flap_and_steer_exact_limits | HIGH_EDGE_ELIGIBLE | PASS |
| P218-T12 | high_non_neutral_steer | CLEAR_WINDOW | PASS |
| P218-T13 | high_confirm_99999 | HIGH_PENDING | PASS |
| P218-T14 | high_confirm_100000 | HIGH_CONFIRMED | PASS |
| P218-T15 | high_confirm_100001 | HIGH_CONFIRMED | PASS |
| P218-T16 | empty_armcheck_does_not_confirm_timer | HOLD_WINDOW | PASS |
| P218-T17 | early_high_retains_original_edge | HIGH_PENDING | PASS |
| P218-T18 | armcheck_non_neutral_breaks_high_window | CLEAR_WINDOW | PASS |
| P218-T19 | armcheck_low_observed_disarm_no_reuse | LOW_DISARM_OBSERVED | PASS |
| P218-T20 | armed_idle_demand_equal_threshold | NO_CHANGE | PASS |
| P218-T21 | armed_idle_demand_strictly_over | DEMAND_OBSERVED | PASS |
| P218-T22 | armed_idle_low_disarm | LOW_DISARM_OBSERVED | PASS |
| P218-T23 | active_low_disarm | LOW_DISARM_OBSERVED | PASS |
| P218-T24 | active_high_not_a_fsm_transition | NO_CHANGE | PASS |
| P218-T25 | invalid_plus_valid_low_blocks | BLOCKED_CLEAR | PASS |
| P218-T26 | semantic_low_high_conflict_blocks | BLOCKED_CLEAR | PASS |
| P218-T27 | rf_lost_low_blocks | BLOCKED_CLEAR | PASS |
| P218-T28 | reset_and_low_blocks | BLOCKED_CLEAR | PASS |
| P218-T29 | catastrophe_reset_high_blocks | BLOCKED_CLEAR | PASS |
| P218-T30 | armed_stale_prior_prevents_positive | BLOCKED_CLEAR | PASS |
| P218-T31 | unresolved_guard_cannot_use_high_qualified | DEFER | PASS |
| P218-T32 | contingency_ack_recovery_deferred | DEFER | PASS |
