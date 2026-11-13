# TASK-009 TEST_ONLY snapshot commit gate (Stage E1)

Python 3.11+, `bb-host-snapshot-commit-gate` 0.1.0. Baseline:
`e61f97e388662a48a13ccb6b308954436cbb87ec`. Design/179 controls this slice.

`TestOnlySnapshotLedger()` starts at frozen genesis. `commit_tick` consumes
genuine TASK-003/004/005/007/008 results, validates them against ledger history,
prepares an eligible negative/administrative snapshot, serializes one closed
ASCII internal record and swaps the snapshot only after private full-append ack.
Deferred ticks do not append or advance. Serialization/quota/append/no-ack
failures keep the previous snapshot and permanently reject further ticks.
Snapshot and five-field result views are immutable; no journal or receipt can
be supplied to the public ledger API. `_testing._seed_for_test` is private,
TEST_ONLY fixture setup, never an application restore or provenance credential.

No accepted RF/control timestamp/status is newly created or refreshed. No
PASS/ADMITTED, ARM, output, full FSM, readiness, ACK recovery, host allowlist,
trusted runtime or real R1 canonical trace is implemented. Journal bytes are
`BB_E1_TEST_JOURNAL_V1`, not Design/118/134 header/tick/terminal records. No
fsync/crash consistency or physical/flight safety claim. Python privacy and
frozen dataclasses do not authenticate callers or defend hostile introspection.

From `BionicButterfly/Source/host_snapshot_commit_gate`, after developer setup:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Full verification (once for final owner acceptance):

```powershell
.\.venv\Scripts\python.exe scripts\verify.py
```

Verifier uses this venv's pinned test/build tools and builds all previous package
wheels from exact local Git source. It runs TASK-001..008 regressions read-only,
each in its own cwd; fresh wheel install/smoke and provenance checks write only
under this task. All artifacts/caches and the prepared venv stay task-local.

`evidence/summary.json` records code/test/script/config SHA, environment, AC
mapping and all 48 named oracle results; `tests.xml` has per-test JUnit;
`commands.json`, `environment.json`, `baseline.json` preserve commands/exits,
artifact hashes and immutable baseline. Expected fault-oracle PASS does not
mean a failed/deferred ledger is a successful R1 run.

Owner UAT and explicit PR permission pending. No PR. After accepted UAT, do not
repeat full regression merely for unchanged PR packaging; execution-affecting
changes require appropriate retesting and renewed owner acceptance.
