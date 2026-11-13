# TASK-005 PR handoff

Owner accepted UAT PASS and authorized the TASK-005 PR into main on 2026-11-13.
Status: ready for Solution Architect review; developer does not merge.
Branch: `feature/TASK-005-host-safety-priority-kernel`.
Baseline: `efe7fa3aff1beeb01af98b98a06593bd8e7af192` (merged PR #4), verified against origin/main.
Accepted implementation: `e2db969ada53b3fb747e577eb9e072abd5fd0eb5`.
The handoff commit updates documentation/evidence and tracks approved release
artifacts; runtime, tests, scripts and packaging config remain unchanged from UAT.

## Scope and contract review

49 files: 43 under `Source/host_safety_priority_kernel/**` and six original owner
Design/Task release artifacts. Owner explicitly requested committing the needed
Design/Task documents. All five manifest-listed files match exact byte counts,
SHA-256 and Git blob SHA-1; the manifest itself is unchanged. This is release
tracking, not a specification/acceptance-criteria edit. AC-01 implementation
scope remains entirely inside the allowed Source subtree.

The known pre-existing TASK-001 evidence/baseline.json working-tree edit was
reported to the owner before PR creation, excluded from the commit, and verified
byte-identical. No other out-of-scope source change was found. No prerequisite
code, schema, firmware, .github or ReviewPR content changes.

Read Design/167 (normative C1 boundary), Design/168 (test/review), then runtime
`src/bb_host_safety_priority_kernel/priority.py`, `tests/` and `scripts/scenarios.py`.
Review against R1/115 and the R1.1 hierarchy/141 found no priority/authority
conflict in this defined slice; this is developer evidence, not SA approval.

| Priority | Implemented behavior |
|---|---|
| A | Prior FAULT_LATCHED persists, including simultaneous catastrophe |
| B | Current catastrophe forces provisional FAULT_LATCHED before RESET/ACK/hazards |
| C | Prior CONTINGENCY holds provisionally; full ACK recovery deferred |
| D | Armed explicit LOST, standalone UNKNOWN, INVALID or conflict forces provisional CONTINGENCY before RESET |
| E | Ordinary RESET forces provisional SELF_TEST |
| F | Valid initial BOOT at T0 forces provisional SELF_TEST |
| G | Every remaining case DEFER: None next-state/category, never safe-retain or authority |

HEALTHY+UNKNOWN without LOST is blocked without inventing effective RF priority.
Missing/stale prior ages in armed states only block qualification, not force an
age-based transition. Negative block=False never permits control/output;
requires_full_fsm is always True. Exactly seven output fields, no reason codes,
accepted timestamp update, trace, M0, full FSM or execution authority.

## Verification and AC-01..10

Full verification rerun for this PR: 208 TASK-005 tests (all 22 P217 oracles),
203 TASK-001, 44 TASK-002, 59 TASK-003 and 140 TASK-004 regressions PASS.
Total **654 PASS, 0 FAIL, 0 ERROR, 0 SKIP**. Dev and installed-wheel smoke each
**12 PASS, 0 FAIL**. Build/install/compile and both pip checks exit 0. Windows
AMD64, CPython 3.11.15. 31 pinned paths + 5 release artifacts + policy digest MATCH.
Installed prerequisite runtime bytes match pinned Git; installed TASK-005 matches
source. No runtime fix was required after accepted UAT.

| AC | Result | Evidence |
|---|---|---|
| 01 | PASS | Source-only implementation diff; import/call audit and side-effect spies; unchanged release artifacts tracked separately |
| 02 | PASS | 22 real-pipeline oracles; exact seven fields/types; synthetic pre-state/history excluded from wire JSON |
| 03 | PASS | Prior latch and catastrophe dominance across all valid later states, with simultaneous competing stimuli |
| 04 | PASS | All three armed states crossed with explicit hazards; RESET loses priority |
| 05 | PASS | Provisional CONTINGENCY hold with RESET/ACK/healthy/LOW; no recovery decision |
| 06 | PASS | Ordinary RESET, valid T0 BOOT, rejected invalid BOOT/pre-state/tick combinations |
| 07 | PASS | DEFER for unresolved freshness, mixed RF, readiness/arming; no state retention or output permission implied |
| 08 | PASS | Frozen exact shape, mirrored flags, wrong caller rejection; zero event/group reads; constant work, deterministic repeat |
| 09 | PASS | Actual four regression suites, build/install, smoke, pip, installed-byte and provenance verification |
| 10 | PASS | Three UAT commands delivered; owner UAT accepted and explicit PR permission received; no self-merge |

[REPORT.md](REPORT.md) has the detailed AC test mapping and limitations.
[commands.json](commands.json) records every command, cwd and exit code;
[environment.json](environment.json) records versions/counts/artifact hashes;
[baseline.json](baseline.json) records all pinned hashes; [files.json](files.json)
records final Source inventory Git blob SHA-256, excluding itself.

The prerequisite wheel build copies omit tests/scripts and TASK-001 DEPENDENCIES.md,
so their manifests emitted 18 warnings; all are retained in build-task001..004.log.
These warnings did not affect installed runtime bytes. TASK-005 packaging and all
pytest suites emitted no warnings. No failed test/build attempt remains.

## P217 oracle-by-oracle comparison

Each PASS below is checked against the actual JUnit testcase
`test_p217_real_pipeline[P217-Txx]`, not inferred from design authoring status.
Each case asserts exact expected values/types for all seven fields, including
current tick index/time and separately supplied enum pre-state. Expected next
state/category/block/full-FSM values and actual assertion results follow.

| Oracle | Scenario | Expected provisional next state | Expected category | Expected block | Expected requires_full_fsm | Actual |
|---|---|---|---|---|---|---|
| P217-T01 | boot_to_self_test | SELF_TEST | BOOT_INITIALIZATION | True | True | PASS |
| P217-T02 | latched_permanent_reset_ack_healthy | FAULT_LATCHED | LATCH_PERSISTS | True | True | PASS |
| P217-T03 | catastrophe_over_reset_control | FAULT_LATCHED | CATASTROPHIC_FAULT | True | True | PASS |
| P217-T04 | catastrophe_over_contingency_ack | FAULT_LATCHED | CATASTROPHIC_FAULT | True | True | PASS |
| P217-T05 | active_lost_reset | CONTINGENCY | ARMED_OBSERVED_HAZARD | True | True | PASS |
| P217-T06 | armed_idle_invalid_and_valid | CONTINGENCY | ARMED_OBSERVED_HAZARD | True | True | PASS |
| P217-T07 | armcheck_control_conflict | CONTINGENCY | ARMED_OBSERVED_HAZARD | True | True | PASS |
| P217-T08 | active_unknown_only | CONTINGENCY | ARMED_OBSERVED_HAZARD | True | True | PASS |
| P217-T09 | active_healthy_unknown_ambiguous | DEFER | None | True | True | PASS |
| P217-T10 | active_healthy_lost | CONTINGENCY | ARMED_OBSERVED_HAZARD | True | True | PASS |
| P217-T11 | contingency_reset_ack_holds | CONTINGENCY | CONTINGENCY_HOLD | True | True | PASS |
| P217-T12 | contingency_healthy_ack_hold_pending | CONTINGENCY | CONTINGENCY_HOLD | True | True | PASS |
| P217-T13 | disarmed_reset | SELF_TEST | ORDINARY_RESET | True | True | PASS |
| P217-T14 | active_reset_no_current_hazard | SELF_TEST | ORDINARY_RESET | True | True | PASS |
| P217-T15 | selftest_reset | SELF_TEST | ORDINARY_RESET | True | True | PASS |
| P217-T16 | disarmed_low_deferred | DEFER | None | False | True | PASS |
| P217-T17 | selftest_empty_deferred | DEFER | None | False | True | PASS |
| P217-T18 | active_stale_prior_deferred | DEFER | None | True | True | PASS |
| P217-T19 | active_current_valid_stale_history_deferred | DEFER | None | True | True | PASS |
| P217-T20 | armcheck_catastrophe_ack | FAULT_LATCHED | CATASTROPHIC_FAULT | True | True | PASS |
| P217-T21 | disarmed_invalid_reset | SELF_TEST | ORDINARY_RESET | True | True | PASS |
| P217-T22 | healthy_active_no_immediate_hazard_deferred | DEFER | None | False | True | PASS |

## Isolated review reproduction

From `Source/host_safety_priority_kernel`, prepare Python 3.11+ and the exact
local prerequisite packages from this checkout, never public same-named substitutes.
Fresh environments need access to pinned build/test dependencies.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install "../host_preflight_m0[test]" "../host_virtual_ticks[test]" "../host_batch_observations[test]" "../host_temporal_guard_facts[test]" ".[test]"
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
foreach ($taskFolder in @('host_preflight_m0', 'host_virtual_ticks', 'host_batch_observations', 'host_temporal_guard_facts')) {
    Push-Location "../$taskFolder"
    try { ..\host_safety_priority_kernel\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests }
    finally { Pop-Location }
}
.\.venv\Scripts\python.exe -m build --no-isolation
```

Aggregate `scripts/verify.py` additionally expects existing sibling regression
venvs. It builds prerequisite wheels from pinned Git blobs and fresh artifacts
under the TASK-005 cache to avoid changing prerequisite trees or old dist files.

## Remaining limitations

Full FSM, LOW/HIGH qualification, SELF_TEST authority, current/prior health
arbitration, critical power/scheduler signals, accepted timestamp owner, complete
ACK recovery, host allowlist, trace-before-publish, M0/output and hardware/flight
remain NOT RUN / DEFERRED. Full P28-T08/T09/T13/T14/T26 conformance is not claimed.
Shape checks do not authenticate forged records or inspect every nested event;
genuine upstream objects and an independently trusted pre-state owner are required.
Effective OS timezone switching NOT RUN (Windows Python lacks tzset); two actual
locales and two TZ environment values passed. SA review and owner merge decision
remain pending.

## Complete PR file list (49)

- `Design/166_TASK004_CLOSEOUT_AND_TASK005_BASELINE.md`
- `Design/167_G0A1_SAFETY_PRIORITY_KERNEL_STAGE_C1_CONTRACT.md`
- `Design/168_TASK005_PRIORITY_KERNEL_ORACLES_AND_REVIEW.md`
- `Design/P217_TASK005_RELEASE_MANIFEST.json`
- `Design/fixtures/P217_SAFETY_PRIORITY_ORACLE_INDEX.json`
- `Source/host_safety_priority_kernel/.gitignore`
- `Source/host_safety_priority_kernel/MANIFEST.in`
- `Source/host_safety_priority_kernel/README.md`
- `Source/host_safety_priority_kernel/evidence/PR_HANDOFF.md`
- `Source/host_safety_priority_kernel/evidence/REPORT.md`
- `Source/host_safety_priority_kernel/evidence/baseline.json`
- `Source/host_safety_priority_kernel/evidence/build-task001.log`
- `Source/host_safety_priority_kernel/evidence/build-task002.log`
- `Source/host_safety_priority_kernel/evidence/build-task003.log`
- `Source/host_safety_priority_kernel/evidence/build-task004.log`
- `Source/host_safety_priority_kernel/evidence/build.log`
- `Source/host_safety_priority_kernel/evidence/commands.json`
- `Source/host_safety_priority_kernel/evidence/compile.log`
- `Source/host_safety_priority_kernel/evidence/dependencies.log`
- `Source/host_safety_priority_kernel/evidence/environment.json`
- `Source/host_safety_priority_kernel/evidence/files.json`
- `Source/host_safety_priority_kernel/evidence/install-prerequisites.log`
- `Source/host_safety_priority_kernel/evidence/install.log`
- `Source/host_safety_priority_kernel/evidence/smoke.log`
- `Source/host_safety_priority_kernel/evidence/task001-regression.log`
- `Source/host_safety_priority_kernel/evidence/task001-regression.xml`
- `Source/host_safety_priority_kernel/evidence/task002-regression.log`
- `Source/host_safety_priority_kernel/evidence/task002-regression.xml`
- `Source/host_safety_priority_kernel/evidence/task003-regression.log`
- `Source/host_safety_priority_kernel/evidence/task003-regression.xml`
- `Source/host_safety_priority_kernel/evidence/task004-regression.log`
- `Source/host_safety_priority_kernel/evidence/task004-regression.xml`
- `Source/host_safety_priority_kernel/evidence/tests.log`
- `Source/host_safety_priority_kernel/evidence/tests.xml`
- `Source/host_safety_priority_kernel/evidence/wheel-dependencies.log`
- `Source/host_safety_priority_kernel/evidence/wheel-environment.log`
- `Source/host_safety_priority_kernel/evidence/wheel-install.log`
- `Source/host_safety_priority_kernel/evidence/wheel-smoke.log`
- `Source/host_safety_priority_kernel/pyproject.toml`
- `Source/host_safety_priority_kernel/scripts/__init__.py`
- `Source/host_safety_priority_kernel/scripts/scenarios.py`
- `Source/host_safety_priority_kernel/scripts/smoke.py`
- `Source/host_safety_priority_kernel/scripts/verify.py`
- `Source/host_safety_priority_kernel/src/bb_host_safety_priority_kernel/__init__.py`
- `Source/host_safety_priority_kernel/src/bb_host_safety_priority_kernel/priority.py`
- `Source/host_safety_priority_kernel/tests/conftest.py`
- `Source/host_safety_priority_kernel/tests/test_oracles.py`
- `Source/host_safety_priority_kernel/tests/test_priority.py`
- `Task/TASK-005_HOST_SAFETY_PRIORITY_KERNEL.md`

Source diff whitespace checks pass. The original owner Task specification has
a trailing space at line 33; the full-diff check reports it. It is preserved
unchanged to retain the release manifest byte/hash match, not silently edited.
