# TASK-002 — OWNER ACCEPTED / READY FOR SA REVIEW

Date: 2026-11-13 (Asia/Saigon). Branch: `feature/TASK-002-host-virtual-ticks`.
Baseline: `ca457f784975c2d0959b1baf988483fa042f5c67` (merged TASK-001).
Owner UAT confirmed: 44 pytest PASS, smoke 8 PASS / 0 FAIL, pip check PASS.
The owner authorized tracking the required release documents, pushing TASK-002
and creating a PR into main. Merge is not authorized.

Pre-PR recheck: **44 PASS, 0 FAIL, 0 SKIP** in 1.56 s, both development and
installed-wheel smoke **8/8 PASS**, pip check PASS. See
[pr-verification.log](pr-verification.log). All 29 files in the original delivery
inventory matched before handoff updates; runtime/tests have not changed since UAT.

## Actual final results

| Check | Result | Log |
|---|---|---|
| TASK-002 unit/integration, all 14 P214 recipes | **44 PASS, 0 FAIL, 0 SKIP**, 1.61 s | [tests.log](tests.log), [tests.xml](tests.xml) |
| TASK-001 regression, read-only source | **203 PASS, 0 FAIL, 0 SKIP**, 4.14 s | [task001-regression.log](task001-regression.log) |
| Development smoke | **8 PASS, 0 FAIL** | [smoke.log](smoke.log) |
| Installed-wheel smoke | **8 PASS, 0 FAIL** | [wheel-smoke.log](wheel-smoke.log) |
| Build/install/compile/dependency checks | All exit 0 | [commands.json](commands.json) |
| Baseline and release checks | **20 pinned files + 5 release artifacts MATCH** | [baseline.json](baseline.json) |

CPython 3.11.15 on Windows AMD64. Version 0.1.0 is installed in `.venv` for UAT;
the independent wheel installation in `.test-env` also passed smoke. Installed
TASK-001 runtime files were compared byte-for-byte with the pinned Git tree;
installed scheduler files match source. Versions and build hashes are in
[environment.json](environment.json).

One initial test failed: T08 compared exact `Decimal('0.2')` to Python float
`0.2`. The assertion now derives exact Decimal values from the serialized input
before comparing the full event payload, preserving the frozen oracle and exact
numeric semantics. Runtime code and Design were unchanged by this fix. Original
failure: [initial-test-failure.log](initial-test-failure.log). The complete suite,
build and smoke checks passed after the fix; no outstanding failure remains.

## Acceptance evidence

| AC | Executed evidence |
|---|---|
| 01 | Runtime AST import/call audit and parser/mixer/IO call spies PASS; all new writes under `Source/host_virtual_ticks/**`. |
| 02 | P214-T01/T05/T11 assert exact ticks, indices, empty batches and inclusive final tick; 12001 batches at maximum duration. |
| 03 | P214-T02/T03/T06 and six boundary cases assert exact IDs/times, including 4999/5000/5001 and final duration. |
| 04 | P214-T04/T07..T10 assert full original events and reference identity; additional equal-control/nonlexical-ID test preserves duplicates and order. |
| 05 | P214-T12 and seven wrong-type cases raise at call time with zero emitted ticks; no sidecar. T12's count=2 is asserted for its valid recipe control, while its explicit invalid-caller assertions require zero output. |
| 06 | P214-T13 mutation attempts fail; source event identities/values preserved; T14 repeats sequence 10 times per locale/TZ configuration. One-shot independent iterators also tested. |
| 07 | Instrumented sparse/spread/dense-final cases: 12001 batches, each source event visited exactly once (2 or 20000 events); first consumption builds only T0 with one lookahead. Executed runtime line visits bounded by `30*(ticks+events)`, not timing alone. Early stop constructs no future batches. |
| 08 | All 14 machine recipes run through TASK-001 preflight; six frozen positive fixtures and dependency version checks PASS. |
| 09 | Editable/wheel install, compile, full tests, smoke, wheel/sdist build, pip check all PASS on Windows Python 3.11.15. |
| 10 | Prepared environment and exactly three UAT commands below; no PR until owner instruction. |

## Files and boundaries

Runtime: `src/bb_host_virtual_ticks/{__init__,scheduler}.py`.
Tests: `tests/{conftest,test_oracles,test_scheduler}.py`.
Tools: `scripts/{smoke,verify}.py`.
Package/docs: `pyproject.toml`, `MANIFEST.in`, `.gitignore`, `README.md`.
Evidence: this report, provenance, environment, command logs, testcase XML and
[file inventory](files.json).

Design/Task contents and TASK-001 source were read only. The pre-existing modification to
`Source/host_preflight_m0/evidence/baseline.json` was preserved byte-for-byte;
its SHA-256 is recorded in environment evidence and the change is excluded from
this PR. Per the owner's latest instruction, the six required release files
(Design 157/158/159, P214 manifest, P214 oracle and TASK-002) are now included in
the PR without content edits. All five manifest entries match their exact bytes
and Git blobs. No ReviewPR/firmware/schema/policy content changes occurred.

Runtime implements enumeration only, with no FSM, conflict/RF resolution, M0,
trace/replay, hardware or execution authorization. No output or flight claim.
Two actual Windows locales and two TZ environment values passed determinism.
Effective OS timezone switching is **NOT RUN** on Windows Python without tzset;
the runtime does not import any clock, locale or environment API.

## Three owner UAT commands

Open PowerShell at `BionicButterfly/Source/host_virtual_ticks`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Expected: **44 passed**, **Smoke: 8 PASS, 0 FAIL**, and **No broken requirements found**.
Owner UAT is accepted. PR creation is authorized; SA review remains pending.
See GitHub for the PR state. Developer does not self-approve or merge.
