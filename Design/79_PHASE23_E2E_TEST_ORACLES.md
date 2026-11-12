# BionicButterfly — Phase 2.3 End-to-End Design Test Oracles

- **ID:** BB-P23-TEST-079 | **Rev:** 0.1 | **Date:** 2026-11-12
- **Status:** **ALL NOT RUN**. Test cases here are design criteria, not an executed simulator or hardware measurement.
- **Inputs:** `PC-A01…20` (`52`), `G1B-01…24` (`63`), `P22-T01…24` (`71`) plus findings `77`.

## 1. Hypothetical base fixture (not an approved runnable config)

Use `SIM_POLICY_CANDIDATE_22A` from `67`: `scheduler_step_us=5000`, low 20000µs (two distinct ticks), high qualification 100000µs, separate RF/frame TTL 200000µs, flap neutral<=0.02, active flap>0.05. Set `approved_for_host_execution=false` in illustrative JSON; **do not toggle it to claim owner approval**. To implement actual tests in a future approved environment, the owner must accept the policy and its trusted digest, and the developer must create separately authorized test fixtures.

## 2. Proposed test oracles

| ID | Stimulus / expected distinct case | Required expected result | Covers |
|---|---|---|---|
| **P23-T01** | two JSON events share same `event_id` anywhere in scenario | whole preflight `VALIDATION_REJECTED`, zero decisions, no virtual output; proposed `E_DUPLICATE_EVENT_ID` | F04 |
| **P23-T02** | unknown `physical_pwm_hz`, `FLIGHT_TEST_APPROVED`, or vendor servo field in scenario | schema/context denied before runtime; no permissive ignore | F08, host isolation |
| **P23-T03** | supplied policy changes `approved_for_host_execution` to true but digest absent from trusted approval set | rejected despite boolean; no run/armed state | F08/F11 |
| **P23-T04** | one frame arrives at 4999µs, evaluation 5000µs | original event timestamp retained for age; exactly one atomic decision at tick | F10 |
| **P23-T05** | already armed, valid LOW and contradictory valid HIGH in same tick | **proposal** runtime control-batch conflict, post-state CONTINGENCY/inhibited, no LOW-based trust, no refreshed frame time | F01/F04 |
| **P23-T06** | DISARMED, valid LOW/HIGH in same tick | conflict denied; no LOW qualification and no HIGH edge | F01/F05 |
| **P23-T07** | RESET and catastrophic injected fault same tick | **proposal** FAULT_LATCHED with virtual sink inhibited; no false SELF_TEST recovery | F02 |
| **P23-T08** | RF LOST and HEALTHY and LOW control in same tick while DISARMED | LOST dominates; LOW does not qualify; no ARM | F05 |
| **P23-T09** | fault latched, final qualifying LOW frame and ACK in same tick | **proposal** ACK denied until a subsequent tick with prior committed qualified LOW and healthy guards | F06 |
| **P23-T10** | LOW at 15001µs and 35000µs, HIGH at 40000µs | difference 19999µs: not qualified, no ARM, even though eval ticks differ | F10 |
| **P23-T11** | replay same canonical event set/build/schedule twice but supply differing volatile execution metadata | canonical **control trace** digest same; metadata excluded, execution IDs may differ | F03/F07 |
| **P23-T12** | trace sink fails immediately after last committed virtual decision | `FAILED_INCOMPLETE_EVIDENCE`, no PASS, exact partial trace declared; virtual sink logically inhibited thereafter | F09/F07 |
| **P23-T13** | two semantically identical valid control frames, unique IDs, within one tick | deduplicated logically; a single virtual decision and no double arm edge | `68`, P22-T09 |
| **P23-T14** | semantic conflict followed by valid control in next tick | stale/fault state not secretly refreshed by rejected frames; recovery follows explicit FSM guards | F01, F05 |
| **P23-T15** | no RF status but valid control frames continue | RF UNKNOWN, no new ARM; no fabricated link health | F05; existing P22-T12/22 |
| **P23-T16** | complete nominal sequence 0/5k/10k/15k/35k/40k/140k/145k/150k | expected states as `71`; output only after eligible active demand, virtual contingency on RF loss | complete E2E path |
| **P23-T17** | two scenarios with identical canonical content but differently ordered JSON object fields | same scenario digest under RFC8785 and same normative replay if inputs semantically identical | `69` JCS |
| **P23-T18** | visual-only metadata/commentary differs; normative events identical | `normative_control_trace_digest` same; visual artifact digest may differ | F07 |
| **P23-T19** | run completes in SIM_ONLY and physical sensor fields absent | measured_lift, wing_angle, physical_airborne stay null/UNKNOWN; no claim of flight readiness | boundary |
| **P23-T20** | change scheduler step from 5000 to 2500us in scenario | deny unsupported schedule or mark a separate deferred research contract; do not expect identical hash | `67`,`69`, deferred cross-schedule |

**All oracles are conditional on acceptance of the proposed conflict resolutions**, including F01 and F02. Until then, such rows are `DESIGN_DISPUTED`, NOT RUN, rather than a confirmed normative implementation requirement.

## 3. Coverage rules for later G1 execution

A G1 run must preserve: exact owner-approved Design commit, engine version, canonical scenario/policy SHA, run ID semantics, test ID, expected/actual state, ordered causal event IDs, typed reasons, virtual output and terminal summary with PASS/FAIL/INCONCLUSIVE. A test expecting a simulated `CONTINGENCY` may *pass its assertion* while the scenario run records a fault. Both results are independent.

Older tests **not superseded**: `PC-A01…20`, `G1B-01…24`, `P22-T01…24`. Explicitly deferred: persisted profile crash test G1B-15/CFG-05 and cross-tick-size equivalence PC-A15/TIME-08. No G2 electrical, G3 mechanical or G4 flight evidence is included.

## 4. Test acceptance levels

- `SPECIFIED` means test text exists.
- `APPROVED` means owner accepts exact input policy + expected output semantics, not that software passes.
- `NOT_RUN` means no executable behavior has been observed.
- `PASS` requires independent actual implementation results and evidence after a separately approved task.
- `FAILED` or `INCONCLUSIVE` must remain visible; never fabricate a green dashboard from authored Markdown.
