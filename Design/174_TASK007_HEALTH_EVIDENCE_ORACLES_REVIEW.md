# TASK-007 — Stage D1 Health Evidence Oracle and SA Review Matrix

- ID: BB-P219-174 · Baseline `a47dc157453547125f5172b4ef165c3b522ff0c8` · Design reference only.
- Test recipe index: `Design/fixtures/P219_HEALTH_EVIDENCE_ORACLE_INDEX.json`, **36 cases P219-T01..T36**.
- **Status: ALL 36 SPECIFIED; NOT RUN against Developer code.** A static fixture-integrity check is not Python runtime proof.

## 1. Positive oracle construction

Use **real** TASK-001 raw wire v2 preflight → TASK-002 scheduler → TASK-003 normalizer → TASK-004 temporal facts → TASK-005 priority assessment. Derive legal wire-v2 bytes from pinned `Design/fixtures/P210_MINIMAL_WIRE_V2.json`: mandatory BOOT at zero, unique IDs, only approved event tags, no unauthorized fields; preserve decimal tokens exactly. For each case supply its `prior_timestamp_snapshot`, `prior_rf_snapshot` and `pre_state` as **separate synthetic TEST-ONLY objects**. Do not put them in scenario JSON, and do **not** call TASK-006 to obtain a real admitted guard token.

Assert exact eight fields and exact types for each `case.expected`, all enum value strings in the index, source-record identity, input preservation, `requires_full_fsm=True`, duplicate event semantics and repeat determinism. `HealthEvidenceFacts` is a diagnostic result **not** a trusted FSM decision.

## 2. Oracle families

| Cases | Required proof |
|---|---|
| T01–T03 | BOOT/none, current HEALTHY, multiple HEALTHY latest original time |
| T04–T11 | LOST dominance independent of order; UNKNOWN-only; HEALTHY+UNKNOWN unresolved; mixed LOST/UNKNOWN/HEALTHY |
| T12–T18 | RF silence with prior HEALTHY age=200000/200001; prior LOST or UNKNOWN supersedes earlier healthy; recovery observation in later tick; new LOST overrides still-fresh older healthy |
| T19–T24 | invalid-inband + valid; two distinct valid groups; candidate with current healthy, missing RF, fresh or stale prior healthy |
| T25–T30 | ambiguous current RF, LOST, RESET, catastrophe, silence with prior accepted control, armed stale accepted-frame age |
| T31–T36 | equivalent controls grouped, new RF healthy after stale prior, prior UNKNOWN stale, standalone UNKNOWN, INVALID+conflict, permanent latch blocks healthy control |

## 3. Required negatives and cross-checks

- Wrong input type, forged subclasses/enums, bool-as-int, out-of-range grid/timestamp, mutable RF record/payload, malformed `SIM_RF_STATUS`, inconsistent RF flags or mirrored control flags, current RF timestamp beyond tick window, T0 invalid prior history.
- Prior RF status/timestamp pair missing one side, prior timestamp later than last committed eval, last committed tick non-grid/future, prior HEALTHY mismatching TASK-004 last accepted healthy age, past LOST with fresh old healthy timestamp does **not** yield HEALTHY, prior `None` with non-None accepted healthy timestamp rejects.
- No reinterpretation of approval as authentication: injecting fake `approved=true`, health PASS or control ADMITTED in JSON must be rejected upstream. Do not add wire fields.
- Current HEALTHY+UNKNOWN retains ambiguity regardless order and earlier committed status; no positive candidate. Current LOST+HEALTHY resolves LOST regardless order. A subsequent genuine separate HEALTHY tick may be **observed evidence** but not automatically committed.
- Conflicting VALID frames and INVALID+VALID deny; equivalent duplicate controls produce one candidate, keep latest original timestamp. No C1 blockage may be inverted into permission.
- Pure O(N_RF) plus constant checks, no upstream re-parse, file I/O, timers, random, trace, mixer, output or hardware; reject malformed caller before returning. Frozen outputs/records and deterministic behavior under locale/TZ/Decimal precision.

## 4. UAT and PR proof: token-efficient

Developer must run relevant unit/integration tests while implementing and debugging, and supply 3 Windows UAT commands (pytest, smoke, pip check), one optional aggregate verifier, and one concise evidence manifest. **Owner** runs final full verification/regressions/smoke on the accepted code; store JUnit and record exact commit/source hash. Developer does not rerun all tests solely to regenerate a verbose PR report if unchanged. Any code/tests/dependency alteration after UAT requires new affected checks and Owner acceptance. Automated 36-case ID/results check instead of manually writing 36 PASS paragraphs.

SA must review source diff against `Design/115/141/173`, 36 oracle tests, verified hashes, uncertainty handling and no authorization leak. Existing TASK-001…006 tests must be **attempted and honestly reported**, not blindly assumed PASS (historic counts: 203/44/59/140/208/221). Stage D1 cannot certify full R1 FSM, S1, ACK recovery, trace, host allowlist or flight.
