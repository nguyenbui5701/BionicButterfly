# TASK-003 — READY FOR OWNER UAT

Date: 2026-11-13 (Asia/Saigon). Branch: `feature/TASK-003-host-batch-observations`.
Baseline: `12b4ee1355d146080810d028843d24481f88af77` (merged PR #2).
No commit, push or Pull Request created for TASK-003. Owner UAT and SA review pending.

## Actual results

| Check | Result | Evidence |
|---|---|---|
| TASK-003 unit/integration, all 18 P215 oracles | **59 PASS, 0 FAIL, 0 SKIP**, 2.02 s | [tests.log](tests.log), [tests.xml](tests.xml) |
| Read-only TASK-001 regression | **203 PASS, 0 FAIL, 0 SKIP**, 4.36 s | [task001-regression.log](task001-regression.log) |
| Read-only TASK-002 regression | **44 PASS, 0 FAIL, 0 SKIP**, 1.63 s | [task002-regression.log](task002-regression.log) |
| Development smoke | **10 PASS, 0 FAIL** | [smoke.log](smoke.log) |
| Installed-wheel smoke | **10 PASS, 0 FAIL** | [wheel-smoke.log](wheel-smoke.log) |
| Build/install/compile/pip check | All exit 0 | [commands.json](commands.json) |
| Provenance | **22 pinned files + 5 release artifacts MATCH** | [baseline.json](baseline.json) |

All executed tests passed without failures or warnings. CPython 3.11.15, Windows
AMD64; pinned tooling and distribution hashes are recorded in
[environment.json](environment.json). The prepared `.venv` contains version 0.1.0
for owner UAT. A separate `.test-env` installed the built wheel and passed smoke.
Both prerequisite packages' installed runtime files match the pinned Git source;
the installed normalizer matches source byte-for-byte.

## Acceptance map

| AC | Executed proof |
|---|---|
| 01 | AST import/call audit and forbidden-call spies PASS. All new developer source/test/evidence files are within `Source/host_batch_observations/**`; final scope audit recorded in files.json. |
| 02 | P215-T01..T18 all execute raw recipe bytes through TASK-001 preflight and TASK-002 scheduling, then assert exact normalized IDs, semantic bodies, flags, original timestamps, group order and references. |
| 03 | T05/T15/T16 and Unicode test assert separate source order vs unsigned UTF-8 ID sorting; composed/decomposed IDs retained independently. All source tuples/member mapping references are preserved. |
| 04 | T03..T06/T15/T17 plus exact spelling/zero/exponent cases, low Decimal context precision and distinct arm/flap/steer fields. Latest original time is asserted independently of eval time. |
| 05 | T07..T09 and INVALID-first/last tests retain every observation. INVALID, conflict and duplicate-semantic flags can all be true; later RF/catastrophe remain visible. |
| 06 | T10..T12 and combined HEALTHY/LOST/UNKNOWN test retain source-order RF mappings and timestamps; exact output field checks prohibit rf_effective or freshness outputs. |
| 07 | T01/T13/T14 and mixed lifecycle test preserve all stimuli, including repeated ACK, without selecting priority or transitions. |
| 08 | T02/T18 and repeated empty/full calls prove no fabricated or carried-over observation. |
| 09 | Deep mutation attempts fail; repeated output matches across two Windows locales, TZ environment values and Decimal context precision=2. Eight wrong caller types and eleven malformed-wrapper cases fail before result construction. Two instrumented large cases verify one classification visit per event and bounded executed lines. |
| 10 | 59 current tests, 203+44 prerequisite regressions, development/wheel smoke, build/compile/install and pip check all PASS. Three UAT commands below are ready in the prepared environment. |

Large-case details: a legal 20000-event scenario includes BOOT plus a 19999-event
target batch (2000 controls in 1000 groups, 17999 RESET observations). A second
case contains 6000 distinct control groups. Both raw inputs are below 2MiB and
pass real preflight. Tests instrument `_inspect_event` and executed runtime lines:
one visit per source event, line bound `100*(events+groups)`, all members retained.
This is linear event classification; required ID metadata sorting separately has
worst-case O(N log N) comparisons. No per-group source rescan occurs.

## Files, boundaries and remaining limitations

- Runtime: `src/bb_host_batch_observations/{__init__,normalizer}.py`.
- Tests: `tests/{conftest,test_oracles,test_normalizer}.py`.
- Verification: `scripts/{__init__,scenarios,smoke,verify}.py`.
- Packaging/docs: `.gitignore`, `MANIFEST.in`, `pyproject.toml`, `README.md`.
- Evidence: this report, logs, XML, pinned hashes, versions and [file inventory](files.json).

Design/Task and both prerequisite source trees were read only. The pre-existing
`Source/host_preflight_m0/evidence/baseline.json` working-tree change remains
byte-identical (SHA-256 in environment evidence). Owner release docs remain
untracked as found. No ReviewPR, firmware, schema or policy content was changed.

No known failing check remains. Effective OS timezone switching is **NOT RUN**
on Windows Python without `tzset`; two actual locales and two TZ environment
values passed. Runtime imports no clock, locale, environment or device APIs.

This result is an observation view only. There is no FSM, freshness, ARM/ACK
decision, effective RF resolution, intent acceptance, M0, trace/replay, trusted
host allowlist, hardware access or output/flight authority. Type/shape guards do
not authenticate a manually forged wrapper; supported inputs come from the real
preflight/scheduler chain. Full policy validation remains at the approved layers.

## Owner UAT: three commands

Open PowerShell at `BionicButterfly/Source/host_batch_observations`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Expected: **59 passed**, **Smoke: 10 PASS, 0 FAIL**, **No broken requirements found**.
PR: **NOT CREATED — WAITING FOR OWNER**.
