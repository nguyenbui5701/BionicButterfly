# TASK-011 — Offline provisioning intent inspection (Stage E3)

PC_SIM_ONLY / TEST_ONLY per Design/185. The pure public API is
`inspect_provisioning_intent(reference, intent_raw, policy_raw, engine_artifact, scheduler_artifact)`.
It accepts the exact TASK-010 `HostReferenceAssessment` and four immutable byte
arrays. It inspects a strict sixteen-field canonical ASCII proposal, checks the
frozen R1 policy digest and binds declared artifact digests to the independent
synthetic TEST_ONLY engine/scheduler bytes.

A match returns `INTENT_CONSISTENT_UNPROVISIONED`. The frozen nine-field result
always has `runtime_authorized=False`, `requires_owner_provisioning=True` and
`requires_full_fsm=True`, with three permanent missing-trust reasons. This is
content consistency only, never binary authentication, protected installation,
owner sign-off, runtime permission, ARM, FSM or output. No key, certificate,
trusted allowlist, signature verification or provisioning writer is created.

Exact E2 types, reason ordering, digest/outcome consistency and fixed flags are
validated; malformed wrappers raise TypeError/ValueError. Matching forged data
cannot be authenticated and still grants no authority. Real integration cases
use TASK-001 `validate_wire` followed by actual TASK-010 assessment. E3 itself
does not rerun either stage, inspect events or invoke the TASK-009 ledger.

E2 mismatch/rejection returns `UPSTREAM_NOT_ELIGIBLE` before E3 parsing/hashing.
Malformed/noncanonical manifest, including more than 4096 bytes (P223-T36),
returns `MALFORMED_INTENT` with no digests. Wrong Python types, policy above
1 MiB, or artifact sizes outside 1..1 MiB raise TypeError/ValueError before
parsing/hashing. Empty policy is allowed but mismatches. The manifest quota
is a raw-request failure, distinct from policy/artifact argument size errors.
The serializer validates the restricted ASCII/integer test domain only; it is
not a general RFC8785 implementation.

## Windows UAT

Open PowerShell in `Source/host_provisioning_intent`; the task-local `.venv`
is prepared. Run these three commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Full verification, including TASK-001 through TASK-010 read-only regressions:

```powershell
.\.venv\Scripts\python.exe scripts\verify.py
```

The harness builds frozen Git source copies in this task's `.cache`, installs
only pinned local prerequisite wheels, checks installed bytes, compiles, runs
tests and dev smoke, builds the package and installs it into a separate wheel
environment for smoke/dependency checks. Old source and evidence are not written.
Only `bb-host-trust-boundary==0.1.0` is a direct runtime dependency; the other
prior packages support integration/regression verification.

`evidence/summary.json` contains actual results, AC-01…10, 48 named P223 oracle
results, N01…N18 counts and hashes of code/test/script/configuration. Exact commands
and logs, JUnit, dependency versions and artifact hashes are in `commands.json`,
`tests.xml` and `environment.json`; `baseline.json` records frozen provenance and
the preserved pre-existing TASK-001 evidence edit. Development checks retain
their own JUnit; failed full attempts are archived before rerunning. N18's pytest
check alone does not claim full builds/regressions ran; the verification harness
records those separately.

Locale/TZ/Decimal determinism is tested. Actual OS timezone switching is NOT RUN
on Windows without `tzset`; hardware, flight and a full R1 runtime are NOT RUN.
Owner UAT and explicit authorization are required before any PR; no auto-merge.
After unchanged accepted UAT, PR packaging compares hashes without repeating
expensive full verification.

To recreate the development environment, create `.venv` with Python 3.11+,
install the exact tool versions under `project.optional-dependencies.test` in
`pyproject.toml`, then run `scripts/verify.py` using that environment. No unpinned
tool upgrades or changes to the frozen prerequisite tasks are required.
