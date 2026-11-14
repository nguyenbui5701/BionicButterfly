# TASK-012 DEV CHECK ? READY FOR OWNER FULL UAT

BLOCKED resolved by SA Design/187 v1.1; no contract changes by Developer.
24/24 explicit baseline Git blob pins and raw bytes MATCH. The TASK-011 intent.py
blob is eceb4fe38b34ece781c8a6099d395e98d7a75298.
9/9 release artifact hashes MATCH; manifest separately pinned; frozen R1 policy
SHA-256 d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10 MATCH.
444 baseline files match their pinned Git blobs.

ACTUALLY RUN: 111 TASK-012 tests PASS, 0 failures/errors/skips; 20/20 authored P224
oracles PASS. Development smoke 4 PASS/0 FAIL; installed-wheel smoke 4 PASS/0 FAIL.
All four actual console/JSONL demos, source/sdist/wheel build, install, installed
source comparison and pip check exit 0. No outstanding test failures or warnings.

NOT RUN: TASK-001?011 regression suites, OWNER FULL UAT, complete R1 FSM, hardware
or flight. Owner acceptance is pending. No PR created or merged.

Source version: bb-host-integrated-shadow-replay 0.1.0 in task-local Windows .venv.
Branch: feature/TASK-012-integrated-pc-shadow-replay.
Baseline HEAD: ccb6babea26be805f752b80488a7232eff70aa06 (implementation uncommitted).
Execution-affecting source fingerprint: 987f7ac1999a58fc23bcd0312e2e00aa7f6ffd52aaae5edf11d31f83d806666b.

60-second test: 12001 ticks / 20000 events; 17.446 seconds measured,
22832840 bytes peak Python allocations (tracemalloc), 6504724 diagnostic bytes.
Process peak memory NOT MEASURED. These are observations, not performance guarantees.

Scope: only Source/host_integrated_shadow_replay changed by Developer. Existing
Source/host_preflight_m0/evidence/baseline.json modification was preserved with
SHA-256 e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d.
Owner-supplied Design/Task release files were read without modification.

Evidence: dev/summary.json (AC-01?12, oracles, exact source hashes), dev/commands.json,
dev/tests.xml, dev/environment.json, dev/*.log and dev/demo-*.jsonl. Early targeted
JUnit results are retained as development-*.xml; the final complete DEV result is
111 tests. See ../README.md for the five Owner commands and all four demos.

PC_SIM_ONLY / NO_OUTPUT / NOT A FLIGHT TEST. SELF_TEST stays UNRESOLVED_FULL_FSM.
Synthetic E2/E3 references grant no authority. Preview uses actual M0 arithmetic;
no ARM grant, accepted control/RF history, actual virtual output, servo or runtime
trust. The offline JSONL is not normative R1 trace/JCS; replacement is atomic but
not a claim of durability across power loss.

## Actual console excerpts (one per preset)

### pilot

```text
   10 | HEALTHY* | rf-h-10@10000:SIM_RF_STATUS; frame-high-10@10000:F=0.4 S=0.2 | SELF_TEST / COMMITTED_TEST_ONLY | REQUESTED_NOT_GRANTED | 200000/600000 | INHIBITED
      control=SINGLE_CANDIDATE; reasons=TRUST_NOT_PROVEN
```

### hazard

```text
   25 | HEALTHY* | rf-h-25@25000:SIM_RF_STATUS; reset-25@25000:SIM_RESET | FAULT_LATCHED / COMMITTED_TEST_ONLY | NONE | -- | INHIBITED
      control=ABSENT; reasons=PRIORITY_BLOCKED,NO_UNCONTESTED_CONTROL,TRUST_NOT_PROVEN
```

### conflict

```text
    5 | HEALTHY* | rf-h-5@5000:SIM_RF_STATUS; frame-a-5@5000:F=0.2 S=0.0; frame-b-5@5000:F=0.5 S=0.3 | SELF_TEST / COMMITTED_TEST_ONLY | NONE | -- | INHIBITED
      control=CONFLICT; reasons=CONTROL_CONFLICT,NO_UNCONTESTED_CONTROL,TRUST_NOT_PROVEN
```

### minimal

```text
    5 | MISSING | NONE | SELF_TEST / COMMITTED_TEST_ONLY | NONE | -- | INHIBITED
      control=ABSENT; reasons=RF_NOT_HEALTHY,NO_UNCONTESTED_CONTROL,TRUST_NOT_PROVEN
```

