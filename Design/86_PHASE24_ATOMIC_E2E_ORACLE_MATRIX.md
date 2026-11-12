# BionicButterfly — Phase 2.4 End-to-End Atomic Test Oracles

- **ID:** BB-P24-TEST-086 · **Version:** 0.1 · **Status:** ALL NOT RUN / design test specifications only.
- **Baseline:** `84` normative candidate, `85` result contract v2 proposal, `67` candidate SIM_ONLY parameters, `71` and `79` earlier oracle suites.

## 1. Canonical host fixture (not approved hardware data)

- `context=PC_SIM`, virtual 5,000 µs ticks, `BOOT` at 0, `SELF_TEST->DISARMED` at 5,000, new valid `SIM_RF_STATUS(HEALTHY)` at 10,000.
- Candidate LOW at 15,000 and 35,000 qualifies on 35,000 if both accepted and RF remains fresh; HIGH neutral at 40,000 starts ARM_CHECK; confirming HIGH neutral at 140,000 reaches ARMED_IDLE; a separate HIGH with `flap=0.2` at 145,000 can enter ACTUATION_ACTIVE if all other guards hold. This is **not a proven simulator run**.
- Body `arm_switch` is independent from RF status; `NORMAL` vs `UNKNOWN` health and all timeouts have the semantics specified in `84` and `67`. All outputs are virtual, not actual servos.
- Treat values 5ms,20ms,100ms,200ms as **SIM_ONLY candidate** numbers. No G0-A1 approval is implied.

## 2. New P24-T01...T24 cases

| ID | Stimulus / boundary | Expected design oracle | Related finding |
|---|---|---|---|
| **P24-T01** | duplicate global `event_id`, even with identical payload | reject whole scenario preflight: `E_DUPLICATE_EVENT_ID`, no core tick | F04 |
| **P24-T02** | two distinct valid LOW and HIGH control bodies in one tick while DISARMED | `E_CONTROL_BATCH_CONFLICT`, remain DISARMED, no low qualification/edge | F01/F04 |
| **P24-T03** | LOW and HIGH distinct in one tick while ACTUATION_ACTIVE | CONTINGENCY, virtual output disabled, no trusted LOW | F01 |
| **P24-T04** | identical control bodies with different IDs same tick | one logical observation/edge maximum; all causal IDs logged | F04 |
| **P24-T05** | RESET and catastrophe in same tick | FAULT_LATCHED; RESET cannot remove fault | F02 |
| **P24-T06** | RESET from healthy ARM_CHECK with no catastrophe | self-test re-entry; all arm eligibility revoked, virtual output inhibited | F02 |
| **P24-T07** | RF LOST and HEALTHY in same tick with LOW frame | LOST wins; no LOW qualification or arm edge | F05 |
| **P24-T08** | distinct later RF HEALTHY after previously LOST | health updates in later tick, but no automatic ARM or fault ACK | F05 |
| **P24-T09** | final qualifying LOW and ACK in same tick | ACK denied; requires previously committed low-qualified snapshot | F06 |
| **P24-T10** | while CONTINGENCY send LOW, then RESET (denied), then later ACK with prior committed LOW and healthy RF+power | LOW and RESET alone retain CONTINGENCY; only qualified later ACK clears to DISARMED; no auto-ARM | F06 |
| **P24-T11** | catastrophic latch then ACK or later RESET in same run | stay FAULT_LATCHED; both denied; a separate new run is needed | F02/F06 |
| **P24-T12** | LOW frame at 15,001 and LOW at 35,000 | delta 19,999µs => insufficient; remain not qualified | F10 |
| **P24-T13** | LOW at 15,000 and 35,000, HIGH at 40,000 | separate ticks and delta=20,000 => edge eligible after all guards | F10 |
| **P24-T14** | HIGH edge at 40,000, confirming HIGH at 139,999 | qualification window not met despite eval rounding; remain ARM_CHECK | F10 |
| **P24-T15** | HIGH edge at 40,000, confirming HIGH at 140,000 | reaches ARMED_IDLE if continuous health/neutral; no output this tick | F10 |
| **P24-T16** | high flap during ARM_CHECK | cancel qualification; never queue motion for later auto-start | FR-002 |
| **P24-T17** | valid UART control frames continue while RF is UNKNOWN | do not qualify new ARM, serial freshness != RF health | F05 |
| **P24-T18** | same scenario/policy/engine/tick but different volatile execution ID/wall time | same canonical control trace digest; external execution metadata may differ | F03/F07 |
| **P24-T19** | visual interpolation/GUI theme differences only | normative control digest unchanged | F07 |
| **P24-T20** | JSON object field ordering changes under JCS-valid input | same canonical scenario digest and trace for same contract | F03 |
| **P24-T21** | scenario with `approved_for_host_execution=true` but unapproved policy digest | preflight rejected: scenario cannot self-approve | F08/F11 |
| **P24-T22** | trace quota/append fails after prior committed decisions | run FAILED_INCOMPLETE_EVIDENCE; partial trace identified, no complete digest or PASS | F09 |
| **P24-T23** | input `FLIGHT` context or physical PWM field in PC_ONLY | preflight E_CONTEXT_DENIED/unknown-field reject, no device I/O | scope |
| **P24-T24** | G1B test replays same logical events with different scheduler step | no byte-equivalence claim; unsupported schedule rejected or deferred research | F10 |

## 3. Additional invariant/property tests (existing IDs not replaced)

`INV-P24-01`: no enabled virtual output on malformed/unapproved input. `INV-P24-02`: one committed state/output at most per tick. `INV-P24-03`: rejected control never refreshes pilot-frame age. `INV-P24-04`: any catastrophe latches even with RESET in same tick. `INV-P24-05`: no automatic rearm after reset/ACK/RF restore. `INV-P24-06`: host build has no reachable physical I/O. `INV-P24-07`: normalization independent of presentation order; causal event IDs sorted. `INV-P24-08`: two executions with equal stable replay identity have byte-equal normative traces under the same pinned engine and scheduler. `INV-P24-09`: incomplete trace prevents PASS. `INV-P24-10`: physical sensor/airborne fields always `UNKNOWN`/null in G0-A1.

## 4. Evidence requirements when testing eventually occurs

Each executable test needs: design main commit, exact contract/policy digests, engine version, scheduler step, canonical scenario bytes/hash, expected and actual **state per tick**, typed errors, virtual-effort integer outputs, full normative control trace and digest, external execution instance ID, report status, pass/fail, reviewer and any incomplete evidence flag. A test suite name without a runnable test is NOT a PASS.

**G0-A1 acceptance (future):** owner-approved baseline + implemented host-only runner + all mandatory PC-A/G1B/P22/P23/P24 tests tested; failures re-open design. It is not approval for G2 bench, G3 mechanics or G4 actual free flight.
