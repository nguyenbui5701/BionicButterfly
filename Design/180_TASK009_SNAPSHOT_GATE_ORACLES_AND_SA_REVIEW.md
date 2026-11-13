# TASK-009 Stage E1 — Test Oracle and SA Review Plan

- ID BB-P221-180; parent `e61f97e388662a48a13ccb6b308954436cbb87ec`; scope **PC_SIM_ONLY / TEST_ONLY**.
- Machine fixture `Design/fixtures/P221_SNAPSHOT_GATE_ORACLE_INDEX.json`, **48 named design cases P221-T01…T48**.
- Static fixture QA may PASS; TASK-009 implementation, isolated SA tests and real-flight tests **NOT RUN** at release.

## Positive scenarios and required test construction

- P221-T01…T36: one-to-one mapping to existing P219 RF/control recipes. Rebuild **real** TASK-001 preflight→TASK-002 tick→TASK-003 normalization→TASK-004 temporal→TASK-005 priority→TASK-007 evidence→TASK-008 triage, then TASK-009 test-only ledger. Synthetic pre-state/prior accepted timestamps/prior RF status must stay outside scenario JSON. Do not use TASK-006 hypothetical verdict or invent a production owner seed.
- P221-T37…T40: create additional *legal wire-v2* batches for ACTUATION_ACTIVE RF LOST, ARMED_IDLE INVALID, ARM_CHECK conflict and ACTIVE stale+RESET, with matching separately seeded test-only prior histories. Verify negative priority CONTINGENCY and no new accepted timestamps.
- P221-T41…T44: armed current healthy, ACTIVE S1 potential, armed RESET without fully resolved health, and HEALTHY+UNKNOWN ambiguous. **Must DEFER**; no journal append or snapshot advance, even if a C1 provisional result proposes SELF_TEST.
- P221-T45…T48: deterministic test-only journal before-append error, short write, after-write-before-ack error, and quota denial. Every such case is `FAILED_INCOMPLETE_EVIDENCE`; no acknowledged snapshot update, no output and no retry in same ledger. A partial/orphan internal record is not a completed R1 trace.

**Independent transaction proof:** verify valid two-tick DISARMED sequence commits 0→1 in order, stale duplicate tick is rejected, skipped ticks are rejected, snapshot returned before append-ack is identical to prior, previous frozen snapshots are not mutated, source record bytes deterministic for identical inputs and journal full-append count matches. On failure the prior snapshot remains readable and unchanged but ledger is terminal and cannot accept further ticks.

## Additional mandatory negatives

1. Invalid exact types including `bool` as `int`, float/Nan/negative ticks, mismatched grid, classes or SafetyState/RFStatus enums, mutable/intentionally forged snapshot, and non-consecutive tick.
2. Snapshot accepted original timestamps beyond previous committed eval; missing/unpaired status/at; carried LOST with older healthy accepted timestamp remains LOST; illegal HIGH window in DISARMED or LOW window in ARM_CHECK; invalid held intent (>1,000,000 or non-null in E1).
3. Input objects from TASK-003/004/005/007/008 must all be read-only, on same tick and same state, with mandatory `requires_full_fsm` flags. No output or timestamp refresh from new frame/RF even when both look HEALTHY and SINGLE_CANDIDATE.
4. Never honor a public `receipt`, caller-provided append result, `approved`, `health=PASS`, `control=ADMITTED` or arbitrary restored snapshot; test journal owned privately by ledger.
5. Inject serialization error, full record quota failure, append exception, short write and post-write/no-ack; no snapshot publication or terminal full-trace SHA in any of them; terminal failure sticky.
6. Inspect source to confirm no filesystem/network/clock/RNG/threads/physical SDK, no policy loader, mixer/virtual output or external callback. Internal journal is not full JCS/R1 trace, not authentication and not fsync/crash durability.
7. **No actual R1 full state oracles** (LOW/HIGH authorization, full ACK recovery, S1 hold, multi-tick scenario completion) may be marked PASS merely because Stage E1 internal commits pass.

## Developer → Owner UAT → PR → SA gate

Developer must run targeted tests during coding, implement exact 48 fixtures and adversarial negatives, package/wheel/dev-smoke, report real run counts and errors. The Owner runs the final `pytest`, `smoke.py`, `pip check` and optional one-command `verify.py` (read-only regressions TASK-001…008). Capture JUnit and compact evidence. No need for Codex to re-run every suite solely to package PR if source/test/dependencies and UAT evidence bytes remain unchanged; any execution-affecting modification needs reapproval. SA reviews full source and failure-injection tests against Design/115/118/179 and commit SHA/hash. Only Owner decides merge. Hardware remains NO-GO.
