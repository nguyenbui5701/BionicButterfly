# TASK-003 PR handoff

Owner accepted UAT and explicitly authorized a PR into `main` on 2026-11-13.
Status: ready for Solution Architect review; no developer merge.
Branch: `feature/TASK-003-host-batch-observations`.
Baseline: `12b4ee1355d146080810d028843d24481f88af77` (merged PR #2).
Accepted implementation commit: `07467847d460d755b4719c69533f405ad6701d3d`.
The subsequent handoff commit changes documentation/evidence only and adds the
unchanged owner release artifacts. Runtime and test code remain as accepted.

## Scope and review entry points

The normalizer preserves every original event and timestamp in immutable tick
observations, groups exact int/Decimal controls, and exposes independent
invalid/conflict/duplicate, RF and lifecycle facts. It emits no FSM decision,
accepted intent, freshness result or output authority.

Implementation, tests and evidence: `Source/host_batch_observations/**` (34 files).
The six required Design/Task release files are included unchanged to make the
review checkout reproducible, consistent with the owner's instruction to track
necessary Design/Task documentation. Five artifacts match the release manifest's
byte counts, SHA-256 and Git blob SHA-1. This tracks approved release content;
no Design requirements or task acceptance criteria were edited. For AC-01,
review implementation scope separately from these original release documents.
The pre-existing TASK-001 evidence/baseline.json working-tree modification is
excluded from the PR and remains byte-identical.

Read Design/161 for the exact contract and Design/162 for the oracle/review gate.
The complete AC-01..10 evidence map is in [REPORT.md](REPORT.md).
Review `src/bb_host_batch_observations/normalizer.py`, then `tests/` and
`scripts/scenarios.py` for the real preflight -> scheduler -> normalizer chain.
All 18 P215 recipes run against raw schema-valid input bytes, preserving exact
decimal spellings and event reference identity.

## Actual verification

The entire local verification was rerun for this handoff on Windows AMD64,
CPython 3.11.15: 59 TASK-003 tests, 203 TASK-001 regressions and 44 TASK-002
regressions PASS; 0 failures/errors/skips. Development and installed-wheel smoke
each PASS 10/10. Compile, build wheel/sdist, install and both pip checks exit 0.
22 pinned files and 5 release artifacts MATCH. Installed prerequisite modules
match the Git baseline; installed normalizer matches source byte-for-byte.
Logs/exit codes: [commands.json](commands.json). Versions, test counts and built
artifact SHA-256: [environment.json](environment.json). Current tracked source
inventory hashes: [files.json](files.json), excluding the inventory itself.
Owner UAT acceptance is recorded from the owner's confirmation, independently
of these developer reruns. No unresolved test failure or runtime fix was needed.

Critical pinned Git blobs:

| File | Blob SHA-1 |
|---|---|
| Design/115 approved atomic safety contract | e6d988d160773219811d28cdb346b5a4590a0fa0 |
| Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json | 1d10c76e34be70880a65252d89a6bca89839fea9 |
| TASK-001 wire.py | 506aa23cbe5e01671f3f51c1f2fd64444d7f0578 |
| TASK-002 scheduler.py | 755e74b740f1a68eb6f095b6895d80cba3831928 |

## Reproduce in an isolated review checkout

From `Source/host_batch_observations`, use Python 3.11+ and install all three
packages from that same checkout (do not substitute public same-named packages).
Dependency download access is required for a fresh environment without cached
build/test tooling. The following uses a fresh review venv:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install "../host_preflight_m0[test]" "../host_virtual_ticks[test]" ".[test]"
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider ../host_preflight_m0/tests
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider ../host_virtual_ticks/tests
.\.venv\Scripts\python.exe -m build --no-isolation
```

The workspace-specific aggregate `scripts/verify.py` additionally requires the
sibling development venvs and locally built prerequisite wheels. The prepared
owner UAT environment and three UAT commands remain documented in README.md.

## Remaining limits

- PC_SIM_ONLY observations. FSM, ARM/ACK recovery, RF freshness/effective state,
  host trust allowlist, trace/replay and hardware/output/flight are outside scope.
- Effective OS timezone switching was NOT RUN (Windows Python has no tzset).
  Two real locales and two TZ environment values passed; runtime reads no clock.
- Caller shape guards do not authenticate forged objects; use real preflight and
  scheduler output. Required ID metadata sorting is O(N log N) worst case;
  classification/grouping event visits are instrumented O(N), without rescans.
- SA design/code review and the owner's merge decision remain pending.

## Complete PR file list (40)

- `Design/160_TASK002_MERGE_CLOSEOUT_AND_TASK003_BASELINE.md`
- `Design/161_G0A1_TICK_OBSERVATION_NORMALIZATION_CONTRACT.md`
- `Design/162_G0A1_TASK003_NORMALIZER_ORACLES_AND_REVIEW.md`
- `Design/P215_TASK003_RELEASE_MANIFEST.json`
- `Design/fixtures/P215_BATCH_NORMALIZER_ORACLE_INDEX.json`
- `Source/host_batch_observations/.gitignore`
- `Source/host_batch_observations/MANIFEST.in`
- `Source/host_batch_observations/README.md`
- `Source/host_batch_observations/evidence/PR_HANDOFF.md`
- `Source/host_batch_observations/evidence/REPORT.md`
- `Source/host_batch_observations/evidence/baseline.json`
- `Source/host_batch_observations/evidence/build.log`
- `Source/host_batch_observations/evidence/commands.json`
- `Source/host_batch_observations/evidence/compile.log`
- `Source/host_batch_observations/evidence/dependencies.log`
- `Source/host_batch_observations/evidence/environment.json`
- `Source/host_batch_observations/evidence/files.json`
- `Source/host_batch_observations/evidence/install.log`
- `Source/host_batch_observations/evidence/smoke.log`
- `Source/host_batch_observations/evidence/task001-regression.log`
- `Source/host_batch_observations/evidence/task001-regression.xml`
- `Source/host_batch_observations/evidence/task002-regression.log`
- `Source/host_batch_observations/evidence/task002-regression.xml`
- `Source/host_batch_observations/evidence/test-environment.log`
- `Source/host_batch_observations/evidence/tests.log`
- `Source/host_batch_observations/evidence/tests.xml`
- `Source/host_batch_observations/evidence/wheel-dependencies.log`
- `Source/host_batch_observations/evidence/wheel-install.log`
- `Source/host_batch_observations/evidence/wheel-smoke.log`
- `Source/host_batch_observations/pyproject.toml`
- `Source/host_batch_observations/scripts/__init__.py`
- `Source/host_batch_observations/scripts/scenarios.py`
- `Source/host_batch_observations/scripts/smoke.py`
- `Source/host_batch_observations/scripts/verify.py`
- `Source/host_batch_observations/src/bb_host_batch_observations/__init__.py`
- `Source/host_batch_observations/src/bb_host_batch_observations/normalizer.py`
- `Source/host_batch_observations/tests/conftest.py`
- `Source/host_batch_observations/tests/test_normalizer.py`
- `Source/host_batch_observations/tests/test_oracles.py`
- `Task/TASK-003_HOST_BATCH_OBSERVATION_NORMALIZER.md`
