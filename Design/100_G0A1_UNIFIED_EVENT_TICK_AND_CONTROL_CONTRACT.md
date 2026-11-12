# BionicButterfly — G0-A1 Unified Tick, Input and Safety Contract (SA Candidate)

- **ID:** BB-P26-NORM-100 | **Revision:** 0.1 | **Date:** 2026-11-12
- **Status:** **SA RECOMMENDED CANDIDATE, NOT YET OWNER-APPROVED OR NORMATIVE**.
- **Baseline:** Git `main` reviewed at `b6628e567813396c36d670d17e18f75e5cc443d3`.
- **Potential effect if approved:** single consolidated PC-only interpretation for `57–59`, `67–71`, `78`, `84–85`, `93–95`. Supersession must be recorded in a future signed decision, not inferred merely from this filename.

## 1. Scope and trust partition

`ScenarioParser` checks strictly typed injected events; `ApprovedPolicyLoader` validates a digest against an independently provisioned owner approval; `VirtualScheduler` groups events; `SafetySupervisor` produces a post-state; `VirtualMixer/Envelope` produces dimensionless bounded commands; `TraceCommitter` gates the **host-visible virtual sink**. No real actuator, RF receiver, GPIO, UART, LED, camera, Wi-Fi/device HAL or inferred 6-DOF flight. Every event/input/output has provenance `SIM_ONLY` and `context=PC_SIM`.

A `SIM_CONTROL_FRAME(uart_frame_status=VALID)` is **not proof of RF HEALTHY**. Maintain separate RF health observation and pilot-frame freshness. Unknown or stale RF blocks new ARM and forces active virtual output inhibition. The JSON scenario cannot supply an alternative safety owner or policy approval flag.

## 2. Tick and timestamp semantics (one schedule only)

- Candidate `step_us=5000`; evaluation ticks `T_k=k×5000` from `T_0=0`. At k=0 only `event_at_us=0` is eligible; for k>0 eligible event times are `(T_{k-1},T_k]`. Preserve original event timestamps; they are never rounded for age calculations.
- One **immutable pre-snapshot** per tick. Gather the full eligible batch, normalize/validate, evaluate exactly once, compute tentative virtual output, persist exactly one committed decision record, then expose post-state/output. No intermediate states leak.
- Unknown/duplicate global event IDs, malformed JSON/invalid context or missing independently authorized policy fail at preflight **before virtual execution**; a syntactically valid in-band `uart_frame_status=INVALID` is instead a deliberate runtime observation.
- Duplicated **semantically equivalent** valid control frames with different IDs, same tick, are one logical observation; choose latest original timestamp for freshness, preserve all sorted original IDs. Different valid control bodies within the same tick are `E_CONTROL_BATCH_CONFLICT` **even if sender intended LOW then HIGH**. No accepted control, no low qualification, no arm edge or control freshness refresh from that batch.
- Within one tick, contradictory `SIM_RF_STATUS(HEALTHY/LOST)` yields **LOST**. A later tick with independently injected HEALTHY may recover the *observed RF state*, but never re-arm or ACK automatically.

## 3. Recommended priority order (explicit delta to old `84` RESET order)

| Rank | Batch outcome (pre-state considered) | Post-state / effect | Reason |
|---:|---|---|---|
| 1 | catastrophe present, even with RESET/ACK/LOW | `FAULT_LATCHED` terminal for this run; null virtual output | never clear same-tick catastrophic fault |
| 2 | pre-state already `FAULT_LATCHED` | remain `FAULT_LATCHED` under ALL events | latch is not in-run clearable |
| 3 | RF LOST/UNKNOWN/stale, critical voltage/scheduler hazard or contradictory valid control batch when pre-state in `ARM_CHECK`, `ARMED_IDLE`, `ACTUATION_ACTIVE` or `CONTINGENCY` | `CONTINGENCY`; null output; RESET same tick does NOT sidestep hazard | **P26 amendment:** hazard before ordinary RESET in active contexts |
| 4 | pre-state `CONTINGENCY`, not catastrophic | remain until eligible separate ACK; RESET and valid LOW alone do not exit | preserve fault recovery gate |
| 5 | ordinary RESET without higher hazard, from BOOT/DISARMED/ARM_CHECK/ARMED_IDLE/ACTIVE | `SELF_TEST`, clear arm/low/high/intent; output null | no latent high rearm |
| 6 | valid accepted LOW with qualified RF, no higher hazard | `DISARMED` from idle/active; LOW qualifications depend on state; null output | explicit disarm action is only trusted from coherent batch |
| 7 | eligible ACK with prior committed LOW qualification and healthy independent RF/power | `CONTINGENCY→DISARMED`; null output, clear previous arm edge; **new low qualification required for future ARM** | ACK never arms |
| 8 | eligible HIGH edge, confirmation, then later fresh HIGH-demand | `ARM_CHECK→ARMED_IDLE→ACTUATION_ACTIVE` across distinct ticks | never high arm from boot or timer alone |
| 9 | no new control frame and all freshness/power gates satisfied | state retained; **S1 last authorized intent hold** only in `ACTUATION_ACTIVE` | no virtual tick can refresh pilot-frame timestamp |
| 10 | denied UI/config mutation | state remains if otherwise healthy, log reason | no browser/SCENARIO control takeover |

**State-independent health handling:** in `SELF_TEST` a healthy policy/config check may complete to `DISARMED` even if RF is UNKNOWN, but **cannot ARM**; when disarmed, RF LOST preserves `DISARMED` with reason and null output. If a critical hazard occurs during SELF_TEST (other than catastrophes), do not signal 'ready to ARM'; remain in `SELF_TEST` or exit DISARMED **under a uniquely specified guard**: SA selects **remain SELF_TEST until non-catastrophic power/scheduler hazard cleared**, but RF UNKNOWN alone may transition DISARMED. The exact `SELF_TEST` guard status shall be logged.

## 4. Freshness model — avoids UART hold-last pitfall

- `last_raw_serial_valid_at_us`: observation time for diagnostics only; may update on schema-valid serial even if RF health bad, but **never** grants authority by itself.
- `last_accepted_pilot_intent_at_us`: timestamp of most recent coherent, valid control under an independently healthy & fresh RF state and applicable mapping; this alone supplies the 'held' intent for virtual actuation.
- `last_rf_status_at_us` plus provenance and state, independent of serial. On expiry of HEALTHY (age > policy `rf_status_timeout_us`), effective state becomes UNKNOWN; explicit LOST remains LOST until later accepted HEALTHY in a separate tick. Status UNKNOWN blocks new ARM and active output.
- Freshness is inclusive at the exact boundary: `T_k - last_accepted_pilot_intent_at_us <= frame_timeout_us`; similarly for healthy RF. At strictly greater timeout, active/arming state enters `CONTINGENCY` with output null.
- A control packet in the same tick as RESET, RF nonhealthy, catastrophe, critical power, or semantic conflict is **not accepted** as pilot intent and never renews this freshness. A valid packet while DISARMED + healthy RF may be accepted for LOW qualification without granting output.

## 5. No-event tick, S1 recommended for PC_SIM only

`S1` = when pre-state is `ACTUATION_ACTIVE`, no new accepted control in this tick, and both accepted pilot intent and independent healthy RF are still fresh, preserve last **authorized** dimensionless intent, re-run guards and envelope, and log a no-new-frame tick. **Never fabricate an accepted frame, LOW observation, HIGH confirmation or a refreshed timestamp.** The output is `null` upon fault, stale control, unqualified RF, config mismatch or exiting active state. The rule is only a virtual simulator policy: it does not decide real-flight RF failsafe.

In `ARM_CHECK`, an empty tick never completes qualification by timer. Explicit later valid HIGH confirmation is mandatory. In `DISARMED`, empty tick cannot qualify LOW. A frame invalid in-band is not 'no-event': it generates an explicit rejection/diagnostic; **SA recommends that it invalidate an in-progress LOW qualification window**, and if already armed it enters CONTINGENCY (same safety purpose as conflicting frames), pending owner decision. The invalid frame is never assigned `last_accepted_pilot_intent_at_us`.

## 6. Transaction status and sink boundary

`decision` is computed in memory then validated/serialized/trace-appended before any new virtual sink visibility. Failure to commit the decision (quota, append, format) produces `FAILED_INCOMPLETE_EVIDENCE`, refuses to expose that tick, inhibits future virtual output and does not report PASS. If committed, apply state/output only once; external log durability guarantee is NOT implied beyond the host's declared append contract. Strictly no physical side-effect guarantee is claimed.

Reference state matrix with tick examples: `101_G0A1_ARM_RECOVERY_AND_NO_EVENT_TRANSITION_MATRIX.md`; trace format: `103_G0A1_REPLAY_TRACE_AND_TRUST_BOUNDARY.md`. All values remain **candidate SIM_ONLY** until the owner signs `106`.
