# TASK-006 PR handoff

Owner confirmed UAT PASS and authorized this PR into main on 2026-11-13.
Ready for Solution Architect review; developer does not merge.
Branch: `feature/TASK-006`.
Baseline: `f2c9237bd4a1e2e077c15db6eb4c22ed2a250d5d` (merged PR #5), verified against origin/main.
Accepted implementation: `66be76cf8cedf32a90ee6de770bd362f3613edda`.
The handoff commit updates documentation/evidence and tracks original release
artifacts only. Runtime, tests, scripts and packaging config remain unchanged
from the owner-accepted implementation.

## Scope and frozen source

52 files: 46 under `Source/host_arm_qualification/**` plus six original approved
owner Design/Task release files, included on explicit owner instruction.
All five manifest-listed artifacts match original byte counts, SHA-256 and Git
blob SHA-1; the manifest itself is tracked byte-for-byte. No specification or
acceptance criterion was edited. AC-01 implementation scope stays within Source;
tracking approved release documents is separate from implementation changes.

TASK-001..005 modules remain unchanged. The pre-existing TASK-001 evidence
baseline.json working-tree edit is preserved byte-for-byte and excluded from
this PR. No schema, .github, ReviewPR, firmware or hardware changes.
[baseline.json](baseline.json) records 37 pinned paths, all five release hashes,
policy digest and the preserved external-edit hash. [files.json](files.json)
records final Source inventory SHA-256 over Git blob bytes, excluding itself.

Review Design/170 and Design/171, then runtime `src/bb_host_arm_qualification/qualification.py`,
`tests/` and `scripts/scenarios.py`. No R1 policy discrepancy identified for the
specified proposal mechanics; this developer evidence is not SA approval.

The API computes frozen LOW/HIGH/ARM/DISARM proposals from genuine upstream
records plus separate synthetic windows/verdicts. It preserves original times,
requires distinct prior ticks, uses exact Decimal comparisons, and rejects
contradictory verdicts. Nothing accepts a frame, commits a state/timestamp,
resolves effective RF or grants ARM/output authority. Every result has exactly
nine fields and requires_full_fsm=True. CONTINGENCY recovery remains deferred.

## Actual verification

Full verification rerun for PR preparation, Windows AMD64 / CPython 3.11.15:

| Check | Result |
|---|---|
| TASK-006 unit/integration, including all 32 P218 cases | 221 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| TASK-001 regression | 203 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| TASK-002 regression | 44 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| TASK-003 regression | 59 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| TASK-004 regression | 140 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| TASK-005 regression | 208 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| Development smoke | 16 PASS, 0 FAIL |
| Installed-wheel smoke | 16 PASS, 0 FAIL |
| Compile/build/install/both pip checks | PASS, all commands exit 0 |
| Provenance | 37 pinned paths + 5 release artifacts + policy/blob guards MATCH |

Total 875 tests PASS plus both smoke runs; no warnings, failures or skips in
this verification. All five prerequisite wheels are built from exact pinned Git
blobs in task-local cache, with installed runtime bytes matching baseline Git.
Installed TASK-006 matches source byte-for-byte. No runtime fix after UAT.
[commands.json](commands.json): exact commands/cwd/exits/logs.
[environment.json](environment.json): versions, JUnit counts, artifact hashes
and fresh isolated wheel environment. [REPORT.md](REPORT.md): full proof/limits.

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

## All 32 P218 oracle comparisons

Each PASS is verified against the actual JUnit testcase
`test_p218_real_pipeline[P218-Txx]`. The test constructs original wire bytes and
runs actual TASK-001 -> 002 -> 003 -> 004 -> 005 -> 006, comparing all nine values
and exact types. Synthetic pre-state, timestamp history, qualification window
and verdict stay outside JSON. Inputs remain unchanged; output is frozen and
repeat-deterministic. Every case expects requires_full_fsm=True and
`tick_index=eval_at_us/5000`.

The window tuple below is the exact expected four proposed fields in order:
LOW first original time, LOW qualified commit tick, HIGH edge original time,
HIGH edge commit tick (microseconds; None means absent).

| Oracle | Scenario | Eval us | Pre-state | Expected proposal | Expected window tuple | Actual |
|---|---|---|---|---|---|---|
| P218-T01 | low_first | 15000 | DISARMED | LOW_START | `(15000, None, None, None)` | PASS |
| P218-T02 | low_gap_19999 | 35000 | DISARMED | LOW_PENDING | `(15000, None, None, None)` | PASS |
| P218-T03 | low_gap_20000 | 35000 | DISARMED | LOW_QUALIFIED | `(15000, 35000, None, None)` | PASS |
| P218-T04 | low_gap_20001 | 40000 | DISARMED | LOW_QUALIFIED | `(15000, 40000, None, None)` | PASS |
| P218-T05 | equivalent_low_same_tick_not_two_samples | 35000 | DISARMED | LOW_START | `(35000, None, None, None)` | PASS |
| P218-T06 | empty_after_low_holds_only | 20000 | DISARMED | HOLD_WINDOW | `(15000, None, None, None)` | PASS |
| P218-T07 | high_with_no_qualified_low | 40000 | DISARMED | CLEAR_WINDOW | `(None, None, None, None)` | PASS |
| P218-T08 | high_with_unqualified_low | 40000 | DISARMED | CLEAR_WINDOW | `(None, None, None, None)` | PASS |
| P218-T09 | high_edge_after_prior_low_qualified | 40000 | DISARMED | HIGH_EDGE_ELIGIBLE | `(None, None, 40000, 40000)` | PASS |
| P218-T10 | high_non_neutral_flap | 40000 | DISARMED | CLEAR_WINDOW | `(None, None, None, None)` | PASS |
| P218-T11 | high_neutral_flap_and_steer_exact_limits | 40000 | DISARMED | HIGH_EDGE_ELIGIBLE | `(None, None, 40000, 40000)` | PASS |
| P218-T12 | high_non_neutral_steer | 40000 | DISARMED | CLEAR_WINDOW | `(None, None, None, None)` | PASS |
| P218-T13 | high_confirm_99999 | 140000 | ARM_CHECK | HIGH_PENDING | `(None, None, 40000, 40000)` | PASS |
| P218-T14 | high_confirm_100000 | 140000 | ARM_CHECK | HIGH_CONFIRMED | `(None, None, None, None)` | PASS |
| P218-T15 | high_confirm_100001 | 145000 | ARM_CHECK | HIGH_CONFIRMED | `(None, None, None, None)` | PASS |
| P218-T16 | empty_armcheck_does_not_confirm_timer | 140000 | ARM_CHECK | HOLD_WINDOW | `(None, None, 40000, 40000)` | PASS |
| P218-T17 | early_high_retains_original_edge | 50000 | ARM_CHECK | HIGH_PENDING | `(None, None, 40000, 40000)` | PASS |
| P218-T18 | armcheck_non_neutral_breaks_high_window | 140000 | ARM_CHECK | CLEAR_WINDOW | `(None, None, None, None)` | PASS |
| P218-T19 | armcheck_low_observed_disarm_no_reuse | 50000 | ARM_CHECK | LOW_DISARM_OBSERVED | `(None, None, None, None)` | PASS |
| P218-T20 | armed_idle_demand_equal_threshold | 145000 | ARMED_IDLE | NO_CHANGE | `(None, None, None, None)` | PASS |
| P218-T21 | armed_idle_demand_strictly_over | 145000 | ARMED_IDLE | DEMAND_OBSERVED | `(None, None, None, None)` | PASS |
| P218-T22 | armed_idle_low_disarm | 145000 | ARMED_IDLE | LOW_DISARM_OBSERVED | `(None, None, None, None)` | PASS |
| P218-T23 | active_low_disarm | 145000 | ACTUATION_ACTIVE | LOW_DISARM_OBSERVED | `(None, None, None, None)` | PASS |
| P218-T24 | active_high_not_a_fsm_transition | 145000 | ACTUATION_ACTIVE | NO_CHANGE | `(None, None, None, None)` | PASS |
| P218-T25 | invalid_plus_valid_low_blocks | 35000 | DISARMED | BLOCKED_CLEAR | `(None, None, None, None)` | PASS |
| P218-T26 | semantic_low_high_conflict_blocks | 35000 | DISARMED | BLOCKED_CLEAR | `(None, None, None, None)` | PASS |
| P218-T27 | rf_lost_low_blocks | 35000 | DISARMED | BLOCKED_CLEAR | `(None, None, None, None)` | PASS |
| P218-T28 | reset_and_low_blocks | 35000 | DISARMED | BLOCKED_CLEAR | `(None, None, None, None)` | PASS |
| P218-T29 | catastrophe_reset_high_blocks | 40000 | DISARMED | BLOCKED_CLEAR | `(None, None, None, None)` | PASS |
| P218-T30 | armed_stale_prior_prevents_positive | 205000 | ARMED_IDLE | BLOCKED_CLEAR | `(None, None, None, None)` | PASS |
| P218-T31 | unresolved_guard_cannot_use_high_qualified | 40000 | DISARMED | DEFER | `(15000, 35000, None, None)` | PASS |
| P218-T32 | contingency_ack_recovery_deferred | 50000 | CONTINGENCY | DEFER | `(None, None, None, None)` | PASS |

## Isolated reviewer setup

From `Source/host_arm_qualification`, use Python 3.11+ and all six local packages
from this pinned checkout, never public same-named substitutes. A fresh venv may
need network access for pinned test/build tooling.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install "../host_preflight_m0[test]" "../host_virtual_ticks[test]" "../host_batch_observations[test]" "../host_temporal_guard_facts[test]" "../host_safety_priority_kernel[test]" ".[test]"
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
foreach ($taskFolder in @('host_preflight_m0','host_virtual_ticks','host_batch_observations','host_temporal_guard_facts','host_safety_priority_kernel')) {
    Push-Location "../$taskFolder"
    try { ..\host_arm_qualification\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests }
    finally { Pop-Location }
}
.\.venv\Scripts\python.exe -m build --no-isolation
```

Aggregate `scripts/verify.py` additionally requires existing sibling regression
venvs. It builds new prerequisite artifacts from pinned Git and writes only
under TASK-006, avoiding old dist artifacts and prerequisite source modifications.

## Remaining limits

No actual health/frame arbiter, authenticated history/verdict source, full FSM,
accepted timestamps, host allowlist, ACK recovery, effective RF, trace-before-
publish, mixer/output/ACTIVE S1, simulator runner or hardware/flight authority.
Full P28-T08/T09/T13/T14/T26/T27 and P210-T02 system conformance NOT RUN / DEFERRED.
An admitted HIGH confirmation without a prior edge anchor is a caller error;
no positive proposal is fabricated from an incomplete snapshot. Constant-size
shape checks do not authenticate forged records or rescan all original events.

Effective OS timezone switching NOT RUN (Windows Python lacks tzset); two real
locales, two TZ environment values and Decimal precision variants passed.
SA review and owner merge decision remain pending.

## Complete PR file list (52)

- `Design/169_TASK005_CLOSEOUT_AND_TASK006_BASELINE.md`
- `Design/170_G0A1_ARM_QUALIFICATION_PROPOSALS_STAGE_C2.md`
- `Design/171_TASK006_ARM_QUALIFICATION_ORACLES_AND_REVIEW.md`
- `Design/P218_TASK006_RELEASE_MANIFEST.json`
- `Design/fixtures/P218_ARM_QUALIFICATION_ORACLE_INDEX.json`
- `Source/host_arm_qualification/.gitignore`
- `Source/host_arm_qualification/MANIFEST.in`
- `Source/host_arm_qualification/README.md`
- `Source/host_arm_qualification/evidence/PR_HANDOFF.md`
- `Source/host_arm_qualification/evidence/REPORT.md`
- `Source/host_arm_qualification/evidence/baseline.json`
- `Source/host_arm_qualification/evidence/build-task001.log`
- `Source/host_arm_qualification/evidence/build-task002.log`
- `Source/host_arm_qualification/evidence/build-task003.log`
- `Source/host_arm_qualification/evidence/build-task004.log`
- `Source/host_arm_qualification/evidence/build-task005.log`
- `Source/host_arm_qualification/evidence/build.log`
- `Source/host_arm_qualification/evidence/commands.json`
- `Source/host_arm_qualification/evidence/compile.log`
- `Source/host_arm_qualification/evidence/dependencies.log`
- `Source/host_arm_qualification/evidence/environment.json`
- `Source/host_arm_qualification/evidence/files.json`
- `Source/host_arm_qualification/evidence/install-prerequisites.log`
- `Source/host_arm_qualification/evidence/install.log`
- `Source/host_arm_qualification/evidence/smoke.log`
- `Source/host_arm_qualification/evidence/task001-regression.log`
- `Source/host_arm_qualification/evidence/task001-regression.xml`
- `Source/host_arm_qualification/evidence/task002-regression.log`
- `Source/host_arm_qualification/evidence/task002-regression.xml`
- `Source/host_arm_qualification/evidence/task003-regression.log`
- `Source/host_arm_qualification/evidence/task003-regression.xml`
- `Source/host_arm_qualification/evidence/task004-regression.log`
- `Source/host_arm_qualification/evidence/task004-regression.xml`
- `Source/host_arm_qualification/evidence/task005-regression.log`
- `Source/host_arm_qualification/evidence/task005-regression.xml`
- `Source/host_arm_qualification/evidence/tests.log`
- `Source/host_arm_qualification/evidence/tests.xml`
- `Source/host_arm_qualification/evidence/wheel-dependencies.log`
- `Source/host_arm_qualification/evidence/wheel-environment.log`
- `Source/host_arm_qualification/evidence/wheel-install.log`
- `Source/host_arm_qualification/evidence/wheel-smoke.log`
- `Source/host_arm_qualification/pyproject.toml`
- `Source/host_arm_qualification/scripts/__init__.py`
- `Source/host_arm_qualification/scripts/scenarios.py`
- `Source/host_arm_qualification/scripts/smoke.py`
- `Source/host_arm_qualification/scripts/verify.py`
- `Source/host_arm_qualification/src/bb_host_arm_qualification/__init__.py`
- `Source/host_arm_qualification/src/bb_host_arm_qualification/qualification.py`
- `Source/host_arm_qualification/tests/conftest.py`
- `Source/host_arm_qualification/tests/test_oracles.py`
- `Source/host_arm_qualification/tests/test_qualification.py`
- `Task/TASK-006_HOST_ARM_QUALIFICATION_PROPOSALS.md`
