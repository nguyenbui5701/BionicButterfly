# TASK-008 guard triage (Stage D2)

`bb-host-guard-triage` 0.1.0, Python 3.11+, PC_SIM_ONLY.
`triage_guard_evidence(observations, temporal, priority, health)` consumes genuine
TASK-003/004/005/007 records and returns exactly ten frozen/slotted fields.
The result reports RF/control lanes, independent armed prior continuity and a
fixed-order tuple of internal reasons, always ending with `TRUST_NOT_PROVEN`.
It never authenticates a caller, accepts a frame/timestamp, supplies PASS/ADMITTED
to TASK-006, grants ARM/S1/output, commits FSM state or publishes trace.

Baseline: `7c09bb5ab4d05d16bfa53439b5dab5b465ec8b05`.
Contract: Design/176; P220 has 36 real-pipeline oracles and 18 negative families.
The future trusted state/history owner, policy/engine allowlist and complete R1
arbiter/trace transaction are separate gates, NOT IMPLEMENTED here. Prior input
history in tests remains TEST_ONLY and outside scenario wire JSON.
Runtime checks only fixed metadata: no RF/source/member/group rescans, upstream
reruns, IO, clocks, RNG, retained history or hardware. O(1) after D1.

From `BionicButterfly/Source/host_guard_triage`, after developer venv setup:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Full verification (run once for final owner acceptance):

```powershell
.\.venv\Scripts\python.exe scripts\verify.py
```

Verifier requires Git, the pinned checkout/owner release and this venv with the
exact tooling in `pyproject.toml` test extra. Prerequisite packages are built
from local pinned Git source, never substituted with remote same-named packages.
TASK-001..007 tests run read-only in separate package cwd using this venv.
Build caches, wheel venv and all new evidence stay inside this task subtree.

Evidence: `evidence/summary.json` (revision, AC/36 oracle/18-family results),
`tests.xml` (per-case JUnit), `commands.json` (commands/exits/logs),
`environment.json` and `baseline.json` (frozen source/release hashes).
Git HEAD alone does not identify uncommitted work; the verification source SHA
includes every runtime/test/script file and packaging config.

Owner UAT/approval pending; PR NOT CREATED. After acceptance, do not repeat full
regressions merely for PR packaging if code/tests/dependencies/evidence are
unchanged. Execution-affecting changes need relevant tests and renewed UAT.
Full FSM/trace/authorization/SELF_TEST/ACK/hardware/flight remain NOT RUN.
