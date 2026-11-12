# BionicButterfly — G0-A1 Replay, Commit Atomicity and Evidence Contract

- **ID:** BB-P26-TRACE-103 | **Rev:** 0.1 | **Status:** SA proposal / no implementation/test execution.
- **Intended reconciliation:** `69`, `80`, `87`, `94`; trust component `70`, API `78/85`.

## 1. Exact normative trace byte candidate

A successful (fully traceable) `SimulationRunReportV2` references a **single** canonical JSONL byte stream:

```text
JCS(header) + LF(0x0A)       exactly once
JCS(decision_tick_0) + LF    exactly once per executed/evaluated tick
JCS(decision_tick_1) + LF
...
JCS(terminal) + LF          exactly once, last
```

- Each record is a JSON object compatible with RFC 8785 JCS and the pinned domain schema; `UTF-8` without BOM, newline byte **LF only**, no trailing spaces or blank lines, no locale-dependent floats. Record field keys are canonicalized. Only schema-declared arrays with declared sorting are ordered; do not arbitrarily alphabetize semantic event sequences.
- `header`: `trace_format_version`, `result_contract_version`, `replay_identity`, `scenario_digest`, `policy_digest`, `engine_revision`, `scheduler_revision`, `tick_us`, `scope=PC_SIM_ONLY`.
- `decision`: one committed tick index and `eval_at_us`, `state_before`, `state_after`, `rf_health`, sorted causal IDs, sorted reason enums, last-accepted-frame age (or null), `output_allowed` and authorized integer virtual effort pair or null. No source wall clock.
- `terminal`: stable final `run_status` (`COMPLETED` / `FAILED` only for this *complete* stream), planned-vs-committed tick counts, stable error codes; **never `control_trace_sha256` or run UUID**. If terminal can't be written, no complete trace digest.
- `control_trace_sha256 = SHA256(exact UTF8 stream above)`, emitted **only in the external report after successful terminal append**. The report can also contain invocation metadata, which never affects deterministic trace hash.
- If validation fails before evaluation, report `VALIDATION_REJECTED`, **zero decisions, no canonical control trace** and no fake terminal tick. If partial append fails, report `FAILED_INCOMPLETE_EVIDENCE`, `control_trace_sha256=null`, optionally `partial_trace_sha256` for proven committed bytes, and `assertion_result` not PASS.

## 2. Non-recursive replay identity

`replay_identity = SHA256(JCS({"domain":"BIONICBUTTERFLY_G0A1_REPLAY_V1", "scenario_digest":..., "policy_digest":..., "engine_revision":..., "scheduler_revision":..., "result_contract_version":2, "trace_format_version":1}))`. Scenario and policy are independently validated JCS values; before owner approval all field names and versions here are candidates. Different `execution_instance_id`, wall time or UI theme may change the *human report only*, not normative digest.

Do not confuse `scenario_digest` (canonical semantic input identity), `replay_identity` (input+policy+engine/schedule identity), and `control_trace_sha256` (actual committed outcome bytes). A correct replay identity does not itself prove the engine behaved correctly: a test oracle must compare expected vs actual decisions.

## 3. Transaction ordering and failure model

At tick `T`:

1. Read immutable pre-state; take complete normalized batch; compute pure candidate state/output.
2. Validate result contract (types, bounds, non-finite, sorted IDs, no physical outputs); serialize candidate decision to a complete canonical record.
3. Check configured trace quota **before publication**; write/append whole record to host-controlled evidence sink and verify the declared write success criterion.
4. Only after (3) succeeds publish *one* virtual committed state/output to observers. Any error at (2) or (3): **no new active virtual output for that failed tick**, no PASS, halt with typed failure and partial evidence report. Do not expose a tentative post-state through another callback path.
5. Complete run only after the terminal record commits; then report external full-stream digest.

**Durability caveat:** user-level host append acknowledgment is not necessarily atomic fsync or crash-consistent persistent storage. The implementation contract must distinguish `appended_to_process_stream`, `durably_written_to_disk`, and `observer_visible`; G0-A1 requires a bounded *observational sequencing guarantee*, not an unproven OS crash guarantee. This is a host-only virtual safety design, not a physical actuator failsafe.

## 4. Typed run statuses and evidence outcome

| `run_status` | Core work performed? | Evidence | Allowed oracle result |
|---|---|---|---|
| `VALIDATION_REJECTED` | none | diagnostic only | rejection test may pass with test harness evidence, **no control-trace PASS** |
| `COMPLETED` | all scheduled ticks | header+all decisions+terminal and digest | PASS only if expected control test oracle agrees |
| `FAILED` | runtime failure but a terminal could be committed | complete trace if written and internally coherent | never PASS for a normal-success oracle |
| `FAILED_INCOMPLETE_EVIDENCE` | part attempted | no complete digest | never PASS; report partial bytes without fabricated completion |

`assertion_result=PASS` for a *predeclared expected rejection* tests only preflight behavior, not acceptance of a core run. An expected injected fault can be `run_status=COMPLETED` and test PASS if it is fully traced.

## 5. Scoping and secrets

Trace output excludes real pilot identity, card data, precise location, Wi-Fi secrets, hardware receiver pairing credentials and untrusted local paths. Software tests must verify an untrusted event cannot select GPIO/serial/PWM, network adapters, executable plugin, browser code or policy approval. Only externally approved immutable policy can execute in an isolated host virtual composition.

**Proposed test focus:** terminal self-hash injection, UI run UUID change, deliberate append failure before active output publication, partial transcript truncation and tampered record. `P25-T01/10–12`, `P26-T20–25`. All NOT RUN.
