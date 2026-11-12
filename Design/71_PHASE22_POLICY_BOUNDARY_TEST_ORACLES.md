# BionicButterfly — Phase 2.2 Boundary Test Oracles & Acceptance Vectors

> **Phase 2.4 review note (2026-11-12):** See the candidate corrective addendum at the end and `84–90` before treating older priority/approval text as normative. **Pending owner approval; not code or flight authorization.**

- **ID:** BB-G0A-TEST-071 | **Revision:** 0.2 | **Date:** 2026-11-12
- **Status:** TEST DESIGN, ALL **NOT RUN**. No simulation code or hardware tests executed.
- **Depends on:** `52` PC-A01–20, `63` G1B-01–24, `58–59`, `67–70`. New test prefix `P22-T` does not renumber older test IDs.

## 1. Common fixture assumptions (unapproved)

Tests below assume **only** `SIM_POLICY_CANDIDATE_22A` from `67` is hypothetically accepted: tick=5,000µs, low observation=20,000µs, high qualification=100,000µs, valid-frame and RF status timeouts=200,000µs, neutral flap<=0.02, neutral steer<=0.05, active flap>0.05. If the owner changes a number, **all boundary vectors must be regenerated and versioned**. No code was executed to produce the expected values.

### Known-good *logic* timeline (not proof of flight or simulator PASS)

| Event time | Stimulus | Expected state at next eligible eval | Output |
|---:|---|---|---|
| 0 | BOOT | SELF_TEST | disabled |
| 5,000 | preloaded config validated | DISARMED | disabled |
| 10,000 | `SIM_RF_STATUS(HEALTHY)` | DISARMED | disabled |
| 15,000 | valid control LOW, flap=0, steer=0 | DISARMED; low candidate starts | disabled |
| 35,000 | second valid control LOW, flap=0 | DISARMED; low qualified | disabled |
| 40,000 | distinct valid control HIGH, flap=0, steer=0 | ARM_CHECK | disabled |
| 140,000 | confirming valid control HIGH, neutral | ARMED_IDLE if RF/frames healthy | disabled |
| 145,000 | valid control HIGH, flap=0.2, steer=0 | ACTUATION_ACTIVE | bounded virtual-only command |
| 150,000 | `SIM_RF_STATUS(LOST)` | CONTINGENCY | inhibited virtual-only |
| 160,000 | `SIM_RF_STATUS(HEALTHY)` + valid HIGH | CONTINGENCY remains; no auto-rearm | inhibited |

This is a **design oracle**, not a result of running code. In this fixture, RF HEALTHY age at 140,000 is 130,000µs, within 200,000. At 145,000 the accepted frame is new, and at 150,000 LOST dominates even though the previously valid control frame is fresh.

## 2. New exact and negative tests

| ID | Input condition | Predeclared acceptance oracle | Traceability |
|---|---|---|---|
| **P22-T01** | legal JSON + BOOT 0 + safe approved fixture, repeated two runs | states/reasons/event orders same with same engine and policy digest | G1B-01/19, TIME-01 |
| **P22-T02** | ARM high at boot, repeated HIGH at 15k/35k/140k, no prior LOW | never reaches ARM_CHECK/ARMED_IDLE; `E_ARM_EDGE_ABSENT` | PC-A01, G1B-02 |
| **P22-T03** | LOW frame at 15k, HIGH at 20k (less than 20k LOW qualification) | no arm, reason for unqualified LOW | PC-A04, G1B-03 |
| **P22-T04** | LOW at 15k and 35k, HIGH 40k, qualifying high 140k | ARM_CHECK at 40k; ARMED_IDLE at 140k if all other guards valid | G1B-03 |
| **P22-T05** | HIGH confirmation at 135k (95k elapsed), no later confirmation | remain ARM_CHECK; no timer-only auto-arm | G1B-03, TIME-07 |
| **P22-T06** | ARM edge flap=0.020000 vs 0.020001 | first may pass flap-neutral guard, second denied | PC-A03, G1B-04 |
| **P22-T07** | ARMED_IDLE, flap=0.050000 vs 0.050001 | at 0.05 virtual output inhibited; above threshold enters ACTUATION_ACTIVE | PC-A10, G1B-17 |
| **P22-T08** | LOW and HIGH with distinct payloads inside same 5ms tick | `E_EVENT_ID_CONFLICT`, no arm/virtual output, no freshness refresh | G1B-07, TIME-03 |
| **P22-T09** | identical control payload repeated with distinct event IDs in one tick | idempotent logical update, no duplicate switch edge | G1B-23 |
| **P22-T10** | ARM + RF LOST + injected critical fault + edit at same tick | fault dominates; no enabled output or policy mutation, stable sorted reasons | PC-A18, G1B-08, TIME-07 |
| **P22-T11** | age of last valid control frame exactly 200000 vs 200001µs at a selected eval time | exactly boundary remains fresh; exceeding threshold is stale/contingency | PC-A07/09, G1B-06 |
| **P22-T12** | RF HEALTHY status age exactly 200000 vs 200001µs; fresh UART continues | valid at boundary; beyond ⇒ RF UNKNOWN, new ARM blocked | G1B-05, P22-C07 |
| **P22-T13** | RF lost at 150k, fresh UART continues; HEALTHY restored 160k with held HIGH | CONTINGENCY remains until explicit ACK, low qualification and new edge | PC-A17, G1B-16 |
| **P22-T14** | RESET while active, control HIGH continues | reset edge eligibility, no autoarm, virtual output inhibited | PC-A02, TIME-05 |
| **P22-T15** | `SIM_CONFIG_WRITE` while DISARMED, then while armed | both denied in G0-A1, immutable policy digest; new run needed for change | PC-A12, CFG-04 (narrowed) |
| **P22-T16** | scenario asks `FLIGHT_TEST_APPROVED`, physical servo pulse or real RX authority | `E_CONTEXT_DENIED`, invalid preflight, zero actual output | PC-A16, G1B-13 |
| **P22-T17** | malformed schema, duplicate JSON keys, NaN, fraction timestamp, unknown type | validation rejected before run; zero core transitions | G1B-11, TIME-04 |
| **P22-T18** | event count, input size, JSON depth or trace export exceeds quota | bounded typed failure; no fake PASS | G1B-12/20, TIME-06 |
| **P22-T19** | identical event set permuted within **same** tick but different display/file ordering | same canonical state, reasons and virtual output; intermediate actuation never published | G1B-09, TIME-02 |
| **P22-T20** | trace sink fails mid-run | result `FAILED_INCOMPLETE_EVIDENCE`, partial trace labeled, virtual sink inhibited | G1B-20 |
| **P22-T21** | physical wing sensor/lift/airborne fields absent | null/UNKNOWN and `SIM_ONLY` label, never fake measured values | PC-A19/20, G1B-18 |
| **P22-T22** | RF status update only, with expired control frame | does not refresh pilot intent; no new ARM | PC-A07/08, P22-C07 |
| **P22-T23** | critical fault cleared but ACK sent while arm still HIGH | ACK denied; CONTINGENCY/FAULT_LATCHED remains; no output | G1B-16 |
| **P22-T24** | long virtual pause with expired RF/frame but future high-control packet | no phantom phases, no autoarm; stale state reached before any new actuation | G1B-10, TIME-05 |

**Tick-alignment caution:** Cases P22-T11/T12 with age=200001µs must use a fixture with an appropriate original event time (for example 4,999µs before a tick) so that a 5,000µs-aligned evaluation can actually observe 200,001µs. Tests cannot assume arbitrary evaluation at a non-tick time.

## 3. Deferred older cases: no false PASS

| Existing test | Phase 2.2 disposition | Reason |
|---|---|---|
| `CFG-05`, `G1B-15` | DEFERRED | persistent config writes/rollback excluded by immutable-in-run G0-A1 |
| `PC-A15`, `TIME-08` (different tick partitions) | DEFERRED | first host freeze fixes `scheduler_step_us=5000`; changing discretization is a separate behavior contract |
| Device-specific RF/CRSF and power G2 cases | NOT RUN / OUT OF SCOPE | physical receiver and electrical components not yet chosen |
| Lift/moment/stability and G4 failsafe cases | NOT RUN / OUT OF SCOPE | simulator cannot certify physical flight |

## 4. Implementation evidence bar (only after separate approval)

Each future test must record the exact Design commit, accepted `SimPolicy` digest, scenario canonical SHA, engine/build revision, expected-vs-observed categorical state and timestamps, output tolerance, canonical trace SHA, pass/fail/error details and independent reviewer. At design stage each row above remains **NOT RUN**; checked document consistency is a different claim.

**Minimum G0-A1 *design* review:** test oracles mutually consistent with `67–70`, no unapproved physical capability, source conflicts recorded, owner approval exact revision. **Minimum G1 *implementation* verification:** executed PC-A and G1B cases in approved scope plus P22-T cases with actual logs, no safety-critical failure. No such evidence exists now.

## Phase 2.4 test-oracle supplement (rev 0.2)

This test table is preserved. Test cases previously interpreted using old `68` priority must instead use **candidate** `84–86`: conflict before trusted LOW, catastrophe before RESET, ACK after a prior qualifying LOW commit, and distinct preflight duplicate-ID vs runtime control contradiction (proposed error-result contract v2). `P24-T01…T24` add boundary coverage; all tests remain NOT RUN.
