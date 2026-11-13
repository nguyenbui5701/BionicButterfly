# TASK-004 PR handoff

Owner confirmed UAT PASS and authorized the TASK-004 PR into main on 2026-11-13.
Ready for Solution Architect review; developer does not merge.
Branch: `feature/TASK-004-host-temporal-guard-facts`.
Baseline: `ed106d22c52647090768ef60fb1e4c33384e9227` (merged PR #3).
Accepted implementation: `fcca5d39903a0e773b68c49dd40dc115526bfb8a`.
The subsequent handoff commit updates documentation/evidence and tracks original
release artifacts only. Runtime, tests and scripts remain unchanged from UAT.

## Scope and provenance

48 files: 42 under `Source/host_temporal_guard_facts/**` and six original owner
Design/Task release files. The owner explicitly requested tracking required
Design/Task documents. All five manifest-listed artifacts match byte counts,
SHA-256 and Git blob SHA-1; the manifest itself is tracked without alteration.
No specification or acceptance criterion was edited. For AC-01, implementation
scope remains the allowed Source subtree; release-document inclusion is separate.
The pre-existing `Source/host_preflight_m0/evidence/baseline.json` local edit is
excluded and remains byte-identical. No prerequisite code, firmware, schema,
.github or ReviewPR modification.

The function exposes twelve immutable facts: two independent exact ages and
inclusive 200000us timeout booleans, uncommitted current control/RF timestamps,
and four independent hazard flags. New candidates never refresh prior history.
No FSM decision, effective RF status, accepted intent or output permission exists.

Review Design/164 and Design/165, then runtime `src/bb_host_temporal_guard_facts/temporal.py`
and `tests/`. The complete AC-01..10 evidence map is in [REPORT.md](REPORT.md).
[baseline.json](baseline.json) records all 27 pinned paths, five release hashes
and exact approved policy SHA-256. [files.json](files.json) records the final
Source inventory hashes over Git blob bytes, excluding itself.

## Actual verification

Full verification rerun for this handoff, Windows AMD64 / CPython 3.11.15:

| Check | Actual result |
|---|---|
| TASK-004 unit/integration, all 22 P216 recipes | 140 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| TASK-001 regression | 203 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| TASK-002 regression | 44 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| TASK-003 regression | 59 PASS, 0 FAIL, 0 ERROR, 0 SKIP |
| Development smoke | 12 PASS, 0 FAIL |
| Installed-wheel smoke | 12 PASS, 0 FAIL |
| Compile, build wheel/sdist, install, both pip checks | PASS, exit 0 |
| Provenance | 27 pinned files + 5 release artifacts + policy digest MATCH |

Commands, working directories and exit codes: [commands.json](commands.json).
Versions, JUnit counts and artifact hashes: [environment.json](environment.json).
All prerequisite installed runtime bytes match baseline Git; the installed
TASK-004 runtime matches source byte-for-byte. No unresolved failure remains.
PR packaging initially hit Windows permissions on old dist artifacts (sdist
replacement and prerequisite wheel read). The recorded retries built TASK-004
into `.cache/pr-dist`, rebuilt prerequisite wheels from exact baseline Git
blobs under `.cache/pr-source` / `.cache/pr-deps`, and installed into fresh
`.cache/pr-wheel-env`. Final build/install, 12/12 wheel smoke, pip and installed
source checks PASS. Both initial error logs and every command exit code remain
in evidence. No runtime/test/script changes were needed.

The historical TASK-003 collection failure and its task-local runner fix remain
recorded in REPORT.md and the original failure log, separate from passing reruns.

## Reproduce in an isolated review checkout

From `Source/host_temporal_guard_facts`, use Python 3.11+ and all four local
packages from the pinned review checkout. A new venv may need network access to
fetch the pinned test/build tools. Do not substitute public same-named packages.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install "../host_preflight_m0[test]" "../host_virtual_ticks[test]" "../host_batch_observations[test]" ".[test]"
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
foreach ($taskFolder in @('host_preflight_m0', 'host_virtual_ticks', 'host_batch_observations')) {
    Push-Location "../$taskFolder"
    try { ..\host_temporal_guard_facts\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests }
    finally { Pop-Location }
}
.\.venv\Scripts\python.exe -m build --no-isolation
```

Each regression runs from its own package directory so `scripts.scenarios`
resolves correctly. If existing dist artifacts are inaccessible, use fresh build output directories
and rebuild local prerequisite wheels from baseline sources as recorded in
commands.json. The workspace aggregate `scripts/verify.py` additionally
requires sibling dev venvs and local prerequisite wheels; prepare these first
in a fresh isolated review checkout. Owner UAT uses README's three commands.

## Remaining limits

- PC_SIM_ONLY facts; no FSM/ARM qualification, accepted timestamp commit,
  effective RF priority, host trust allowlist, trace, output or hardware/flight.
  Full P28-T13/T14/T26 state/output conformance remains NOT RUN at Stage B.
- Caller shape checks do not authenticate forged objects or rescan all original
  events/groups. Actual TASK-003 output and independently trusted history required.
- Effective OS timezone switching NOT RUN (Windows Python lacks tzset). Two real
  locales and two TZ environment values passed; runtime reads no clock.
- SA review and owner merge decision remain pending.

## Complete PR file list (48)

- `Design/163_TASK003_MERGE_CLOSEOUT_AND_TASK004_BASELINE.md`
- `Design/164_G0A1_TEMPORAL_GUARD_FACTS_CONTRACT.md`
- `Design/165_TASK004_TEMPORAL_GUARD_TEST_AND_REVIEW.md`
- `Design/P216_TASK004_RELEASE_MANIFEST.json`
- `Design/fixtures/P216_TEMPORAL_GUARD_ORACLE_INDEX.json`
- `Source/host_temporal_guard_facts/.gitignore`
- `Source/host_temporal_guard_facts/MANIFEST.in`
- `Source/host_temporal_guard_facts/README.md`
- `Source/host_temporal_guard_facts/evidence/PR_HANDOFF.md`
- `Source/host_temporal_guard_facts/evidence/REPORT.md`
- `Source/host_temporal_guard_facts/evidence/baseline.json`
- `Source/host_temporal_guard_facts/evidence/build-pr-initial-failure.log`
- `Source/host_temporal_guard_facts/evidence/build.log`
- `Source/host_temporal_guard_facts/evidence/commands.json`
- `Source/host_temporal_guard_facts/evidence/compile.log`
- `Source/host_temporal_guard_facts/evidence/dependencies.log`
- `Source/host_temporal_guard_facts/evidence/environment.json`
- `Source/host_temporal_guard_facts/evidence/files.json`
- `Source/host_temporal_guard_facts/evidence/install.log`
- `Source/host_temporal_guard_facts/evidence/pr-build-host_batch_observations.log`
- `Source/host_temporal_guard_facts/evidence/pr-build-host_preflight_m0.log`
- `Source/host_temporal_guard_facts/evidence/pr-build-host_virtual_ticks.log`
- `Source/host_temporal_guard_facts/evidence/smoke.log`
- `Source/host_temporal_guard_facts/evidence/task001-regression.log`
- `Source/host_temporal_guard_facts/evidence/task001-regression.xml`
- `Source/host_temporal_guard_facts/evidence/task002-regression.log`
- `Source/host_temporal_guard_facts/evidence/task002-regression.xml`
- `Source/host_temporal_guard_facts/evidence/task003-regression-initial-failure.log`
- `Source/host_temporal_guard_facts/evidence/task003-regression.log`
- `Source/host_temporal_guard_facts/evidence/task003-regression.xml`
- `Source/host_temporal_guard_facts/evidence/tests.log`
- `Source/host_temporal_guard_facts/evidence/tests.xml`
- `Source/host_temporal_guard_facts/evidence/wheel-dependencies.log`
- `Source/host_temporal_guard_facts/evidence/wheel-environment.log`
- `Source/host_temporal_guard_facts/evidence/wheel-install-pr-initial-failure.log`
- `Source/host_temporal_guard_facts/evidence/wheel-install.log`
- `Source/host_temporal_guard_facts/evidence/wheel-smoke.log`
- `Source/host_temporal_guard_facts/pyproject.toml`
- `Source/host_temporal_guard_facts/scripts/__init__.py`
- `Source/host_temporal_guard_facts/scripts/scenarios.py`
- `Source/host_temporal_guard_facts/scripts/smoke.py`
- `Source/host_temporal_guard_facts/scripts/verify.py`
- `Source/host_temporal_guard_facts/src/bb_host_temporal_guard_facts/__init__.py`
- `Source/host_temporal_guard_facts/src/bb_host_temporal_guard_facts/temporal.py`
- `Source/host_temporal_guard_facts/tests/conftest.py`
- `Source/host_temporal_guard_facts/tests/test_oracles.py`
- `Source/host_temporal_guard_facts/tests/test_temporal.py`
- `Task/TASK-004_HOST_TEMPORAL_GUARD_FACTS.md`
