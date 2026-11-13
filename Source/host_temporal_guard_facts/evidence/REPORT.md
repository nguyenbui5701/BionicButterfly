# TASK-004 — READY FOR OWNER UAT

Date: 2026-11-13 (Asia/Saigon). Branch:
`feature/TASK-004-host-temporal-guard-facts`.
Source pin: `ed106d22c52647090768ef60fb1e4c33384e9227` (merged PR #3).
Implementation: pure read-only temporal age and candidate facts, Design/164.
Owner confirmed UAT PASS and explicitly authorized the PR into main on 2026-11-13.
Accepted implementation commit: `fcca5d39903a0e773b68c49dd40dc115526bfb8a`.
SA review and owner merge decision remain pending. Developer does not merge.
See [PR handoff](PR_HANDOFF.md) for the complete PR file list and review instructions.

## Actual final results

Full verification rerun for the PR handoff; runtime, tests and scripts are
unchanged from the owner-accepted implementation.

| Check | Result | Evidence |
|---|---|---|
| TASK-004 unit/integration, including all 22 P216 oracles | **140 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [tests.log](tests.log), [tests.xml](tests.xml) |
| TASK-001 read-only regression | **203 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task001-regression.log](task001-regression.log) |
| TASK-002 read-only regression | **44 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task002-regression.log](task002-regression.log) |
| TASK-003 read-only regression | **59 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task003-regression.log](task003-regression.log) |
| Development smoke | **12 PASS, 0 FAIL** | [smoke.log](smoke.log) |
| Installed-wheel smoke | **12 PASS, 0 FAIL** | [wheel-smoke.log](wheel-smoke.log) |
| Compile, install, wheel/sdist build, both pip checks | **PASS**, final successful attempts exit 0 | [commands.json](commands.json) |
| Pinned source/Design and release provenance | **27 pinned files + 5 release artifacts MATCH**, policy SHA-256 MATCH | [baseline.json](baseline.json) |

Final total: **446 tests PASS**, plus both smoke runs. Windows AMD64,
CPython 3.11.15. Exact package versions, test counts and artifact SHA-256 are in
[environment.json](environment.json). The owner `.venv` uses the three local
prerequisite wheels and editable TASK-004. For this PR, a fresh `.cache/pr-wheel-env` installs all
four locally rebuilt wheels; prerequisite runtime bytes match the pinned Git tree, and
installed TASK-004 runtime bytes match source. No unresolved failing check.

## Errors found and resolved

- Initial dependency installation was blocked by sandbox networking:
  `WinError 10013`, fetching `setuptools==80.9.0` from PyPI. Retried using the
  permitted elevated installation, which installed the pinned tools successfully.
  No dependency versions or application behavior changed to bypass the failure.
- First TASK-003 regression invocation exited **4** during collection, with
  `ModuleNotFoundError: No module named 'bb_host_temporal_guard_facts'`.
  Its `from scripts.scenarios` resolved the TASK-004 helper because the runner
  used the TASK-004 working directory. Full original error is retained in
  [task003-regression-initial-failure.log](task003-regression-initial-failure.log).
  Fixed only TASK-004 `scripts/verify.py`: each prerequisite now runs with its
  own working directory and interpreter, `-B`, no pytest cache, and an absolute
  JUnit destination inside TASK-004. No prerequisite file was edited. The full
  final verification rerun passed, including all 59 TASK-003 regressions.

- PR packaging rerun encountered Windows artifact permissions: original TASK-004
  sdist replacement failed with `PermissionError: [WinError 5] Access is denied`;
  reading the old TASK-001 wheel then failed with `[Errno 13] Permission denied`.
  Full logs: [build-pr-initial-failure.log](build-pr-initial-failure.log) and
  [wheel-install-pr-initial-failure.log](wheel-install-pr-initial-failure.log).
  Built TASK-004 into `.cache/pr-dist`; rebuilt all three prerequisites from
  exact baseline Git blobs in `.cache/pr-source`, with wheels in `.cache/pr-deps`.
  Installed all four wheels into fresh `.cache/pr-wheel-env`: smoke 12/12 and
  pip check PASS; installed prerequisite bytes match Git and TASK-004 matches
  source. No runtime/test/script changes or permission changes were required.
  `commands.json` preserves both failed attempts and subsequent successful
  commands; artifact hashes and fresh environment location are in environment.json.

## Acceptance map

| AC | Executed proof |
|---|---|
| 01 | Only new TASK-004 subtree files. AST import/call allowlist and forbidden IO/clock/RNG/M0/upstream-rerun spies PASS. Original unrelated TASK-001 evidence edit preserved. |
| 02 | All P216-T01..T22 build real wire-v2 bytes, execute actual TASK-001 -> TASK-002 -> TASK-003 -> TASK-004. Exact twelve-field values and types compared, including None vs int vs bool. Prior fixtures are separate synthetic objects, absent from wire JSON. |
| 03 | T03..T11 and six 60s-final-tick tests cover independent 199999/200000/200001 ages; zero timestamp is not absence; old commit may skip ticks. No float or grid rounding. |
| 04 | T12..T16 plus all RF status orderings retain hazards and reject mixed candidate promotion; 5000 RF events scanned exactly once each. Last bad RF timestamp rejects before return. |
| 05 | T17..T20; exact decimal-equivalent duplicate group uses latest original 4999us; INVALID/conflict suppress candidate; RESET/catastrophe/ACK/nonhealthy RF do not invent acceptance or suppress raw control candidates. |
| 06 | T21/T22, new RF with stale history, later empty tick and repeated invocation prove ages stay independent and unrefreshed, with no internal history. |
| 07 | Every oracle checks input/prior/source preservation and frozen records; wrong types/subclasses, bool/float/negative/future times, missing/equal/future/non-grid commits, mutable envelopes/RF payloads and T0 violations reject. Repeat determinism under two locales, two TZ env values and Decimal precision 2. |
| 08 | Exact twelve-field output and three-field prior contract, frozen slots, no extra authority/history fields. All timestamps and ages exact integers/None. |
| 09 | Actual 203/44/59 regressions, packaging, both smoke runs, pip checks and installed source comparisons PASS; initial harness failure retained and explained above. |
| 10 | Prepared Windows `.venv`; README and commands below. No PR before owner authorization. |

Complexity proof: the evaluator inspects only outer shapes/flags, one sole
control group's metadata, two prior timestamps and the RF events. With 5000
RF events, the timestamp helper is called 5000 times. With 1000 distinct control
groups and no RF, fewer than 300 runtime Python line events execute. No source
or group rescan, normalization rerun or per-tick history is involved.

## Scope and limitations

- All implementation, tests, packaging and evidence live under
  `Source/host_temporal_guard_facts/**`; see [file inventory](files.json).
  The six required owner Design/Task release files are tracked unchanged in the
  PR, as explicitly requested. Manifest-listed bytes and hashes are verified. Existing TASK-001
  evidence change retains its baseline SHA-256. No .github, ReviewPR, firmware,
  prerequisite code or schema edits. The unrelated TASK-001 evidence edit is
  excluded from the PR. Implementation writes remain in the allowed subtree;
  release-document tracking does not change the specifications.
- This is PC_SIM_ONLY arithmetic and uncommitted observation evidence. No FSM,
  ARM qualification, accepted-frame update, effective RF selection, trace
  transaction, host allowlist, output adapter or hardware/flight test was run.
  Full P28-T13/T14/T26 state/output conformance is **NOT RUN** by Stage B.
- Types/consumed-field checks do not authenticate manually forged records or
  rescan every original event/group. The genuine TASK-003 output boundary is
  required; trust in history must be independently provisioned by a future owner.
- Effective OS timezone switching is **NOT RUN** because Windows Python lacks
  `tzset`. Actual locales C/English_United States.1252 and TZ environment values
  UTC0/ICT-7 passed. Runtime imports no clock, environment or locale APIs.
- Aggregate verification assumes prepared sibling dev environments/local wheels.
  Fresh reviewer checkouts must prepare them first, using the pinned source.

## Owner UAT: three PowerShell commands

Working directory: `BionicButterfly/Source/host_temporal_guard_facts`.

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Expected: **140 passed**, **Smoke: 12 PASS, 0 FAIL**,
**No broken requirements found**. PR: **NOT CREATED — WAITING FOR OWNER**.
