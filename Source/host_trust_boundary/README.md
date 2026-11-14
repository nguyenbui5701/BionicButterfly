# TASK-010 — Host reference boundary (Stage E2)

PC_SIM_ONLY / TEST_ONLY reference comparison per Design/182 E2.1. The pure
`assess_reference_host_boundary(preflight, approved_policy_raw_bytes, claimed_host)`
consumes an exact TASK-001 result, immutable raw bytes and an independent synthetic
`ClaimedHostFingerprint`. Its frozen eight-field result always denies runtime
authorization and requires trusted host provisioning and the full FSM.

Matching policy content and all eleven test pins returns
`REFERENCE_MATCH_NO_AUTHORITY`; mismatches produce deterministic ordered reasons.
Genuine rejection wins without hashing the candidate policy or comparing the host.
Malformed types/header shapes raise TypeError/ValueError. The runtime does no I/O,
scenario reparse, event scan, output, clock, FSM, journal or trust provisioning.

The fixed test tuple is not a trusted allowlist. Exact Python classes, frozen data,
chat approval and digest equality cannot authenticate provenance or a binary.
The caller must run genuine TASK-001 `validate_wire` first; header checks cannot
distinguish an otherwise identical forged result. Rejected sidecars are genuine
TASK-001 dictionaries, inspected without mutation. Event semantics belong to
TASK-001 and are deliberately not revalidated here. Real runtime trust, ARM,
hardware and flight remain outside this task.

## Windows UAT

Open PowerShell in `Source/host_trust_boundary` (the task-local `.venv` is prepared).
Run these three commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Full verification, including nine independent read-only regressions, builds,
installation from pinned local wheels, wheel smoke and dependency checks:

```powershell
.\.venv\Scripts\python.exe scripts\verify.py
```

`evidence/summary.json` records actual results, AC-01…10, all 48 named oracle
results, N01…N18 counts, source/test/script/config hashes and installed dependencies.
`evidence/tests.xml`, `commands.json`, per-command logs and `environment.json`
provide reproducible details. `baseline.json` pins prerequisites, release hashes
and the pre-existing TASK-001 evidence edit, which this task preserves.
Failed verification attempts are retained under `evidence/history/`; development
failures use separate evidence filenames. Locale tests change the C locale and
English Windows locale; TZ environment variants are checked, but actual OS
timezone switching is NOT RUN on Windows without `tzset`.

N18 includes full verification operations recorded by the harness; its pytest
check alone does not claim that builds or regressions have run. After unchanged
Owner UAT, PR packaging compares hashes without repeating expensive verification.
PR creation requires explicit Owner authorization; Developer never merges.

## Recreate the development environment

Use Python 3.11+ to create `.venv`, then install the exact tool pins in the
`project.optional-dependencies.test` list in `pyproject.toml` (no unpinned tool
upgrades). Run `scripts/verify.py` with that environment. It builds TASK-001…009
from the frozen Git baseline into this task's `.cache`, installs their local
wheels and this editable package, and creates a separate wheel environment.
The runtime package depends only on `bb-host-preflight-m0==0.1.0`; the other
packages are verification prerequisites. No old task files are written.
