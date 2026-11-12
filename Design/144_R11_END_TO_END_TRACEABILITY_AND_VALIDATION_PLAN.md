# G0-A1 — Phase 2.11 Contract Traceability & Validation Plan

- **Doc:** BB-P211-TRACE-144 · **Evidence state:** Static documented, executable simulator **NOT RUN**.

## 1. Requirements → normative design → oracles

| Requirement | Frozen rule | Linked tests (specified, NOT RUN) | Independent evidence required |
|---|---|---|---|
| Startup must not arm itself | `115` BOOT→SELF_TEST→DISARMED; v2 T0 BOOT only | P210-T01, P210-T02, P211-S03 | Observe actual state trace and null output |
| Explicit LOW/HIGH arm ritual | `115`, policy R1, `132` timestamp origin | P210-T09–T11, P210-T02 | T0/T+ timing and exact edge qualification |
| Fault wins over RESET | `115` priorities, `132` catastrophe | P210-T12, P211-S06 | Actual FAULT_LATCHED+null and no clear |
| Stale frame/RF cannot keep output | `115`, policy 200ms independent ages | P210-T09, P210-T13 | Stimulus with original timestamp at 200000/200001us |
| Strict PC-only input | `116`, `132`, v2 closed schema | P210-T03–T08,T18–T20,T32 | Reject before creating runner, zero tick, no hardware access |
| Deterministic M0 efforts | `133` and M0 pinned bytes | P210-T14–T17, P211-S10 | Compare independent integer arithmetic & clipping |
| One batch one published decision | `115`,`118`,`134` | P210-T21–T23,T26–T27 | No transient command and no partial output |
| Replay integrity & evidence | `118`, `134`, R1.1 trace schema | P210-T24–T31, P211-S11–S13 | Full-stream bytes, external digest, independent RFC8785 |
| Policy integrity | `116` and pinned digest | P210-T32, P211-R05 | Immutable allowlist and negative tampering tests |

## 2. Evidence hierarchy

- **Static audit PASS:** JSON Schema meta-syntax, example validation, duplicate-key parser proof-of-concept, exact Decimal M0 and authored trace hash. They demonstrate *documents and vectors are internally checkable*.
- **G1 test NOT RUN:** test harness executes future runtime and checks state/output/replay for all intended cases. Passing a preflight-rejection oracle does not mean a successful core run happened.
- **Hardware and G4 NO-GO:** no real RX/servo/power/wing test data or in-air recovery proof.

## 3. Additional release-test cases (do not invent current PASS)

1. `P211-R01` repeated nominal v2 scenario twice with identical policy+engine/scheduler revisions → identical normative trace and replay identity, differing *external* invocation ID allowed.
2. `P211-R02` Unicode supplementary codepoint and escaped key-edge RFC8785 independent canonicalization; rejects broken UTF-8/surrogates.
3. `P211-R03` scenario JSON bytes at and above 2MiB, trace bytes at 16MiB and a failed append before publication; no uncommitted virtual effort.
4. `P211-R04` multi-tick S1 held intent, no timestamp refresh; stale independently from RF vs control.
5. `P211-R05` tampered policy digest, writable host allowlist, physical IO adapter attempt rejected before runner.
6. `P211-R06` normal preflight invalid input → no full trace/digest, typed rejected result and zero evaluated ticks.

The machine-index `fixtures/P211_FREEZE_AUDIT_AND_FUTURE_CONFORMANCE.json` distinguishes 13 static checks from 6 executable tests **NOT RUN**. An actual G1 test report must cite commit, policy digest, executable revision and artifacts, not borrow PASS_STATIC.
