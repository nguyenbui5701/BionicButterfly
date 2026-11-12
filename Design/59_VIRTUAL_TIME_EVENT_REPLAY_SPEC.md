# BionicButterfly — G0-A1 Virtual Time, Event Ordering & Replay

- **ID:** BB-G0A-TIME-059 · **Rev:** 0.1 · **Date:** 2026-11-12
- **Status:** PROPOSED / HOST-ONLY / NOT EXECUTED
- **Related:** `51` host candidate, `52` PC-A suite, `56–58`, `60–64`.

## 1. Time domains and why they matter

**Host-controlled virtual monotonic time** is the only authority for core calculations. Never read a wall clock or sleep from `SafetySupervisor`/`MotionPlanner`. All exposed time fields are integer **microseconds** from run start. Separate:

- `event_at_us`: when external simulated stimulus is defined to occur;
- `eval_at_us`: at which scheduled supervisor decision evaluates all pending events;
- `last_valid_frame_at_us`: last accepted full control frame; invalid/telemetry-only frame never updates;
- `last_rf_status_at_us`: last independently injected simulated RF status;
- `phase_time_us`: elapsed time used for virtual wing phase calculation;
- `trace_index`: per-run increasing integer *logging order* only, not RF transport sequence.

Input frames at `event_at_us` need not coincide with an evaluation tick. On each evaluation, consume all eligible events in a deterministic batch, then issue **one** decision for that evaluation time. Unused carrier timing is a virtual visualization concept, not an ESP32 PWM specification.

## 2. Scheduler candidate and explicit ordering

1. **Preflight parse and validation**: check schema version, max scenario duration/event count, unique event IDs, monotonic timestamps or documented sorting rule, valid event types/payloads and SIM_ONLY context. Reject entire malformed input before any core state transition; return typed error and an evidence record.
2. **Canonical time order**: sort events by `(event_at_us, priority_class, canonical_event_id)` for stable audit, but **do not apply safety effects one by one**. Group all events scheduled up to the current eval time and evaluate one atomically consistent batch.
3. **Conflict detection**: if same source delivers two contradictory `SIM_CONTROL_FRAME` updates at identical event time (e.g. arm HIGH and LOW), reject that source’s conflicting control updates for the batch and flag `E_EVENT_ID_CONFLICT`. Duplicate identical IDs are rejected at parse; repeated identical semantic frames with distinct IDs must not generate duplicate edges.
4. **Fault precedence**: `RESET`, injected catastrophic fault, explicit DISARM, independent RF/other fault, config changes, arm qualification, then normal demand. Priority is defined in `58`. Multiple faults are reported in a stable sorted list.
5. **Single state commit**: evaluate from snapshot after batch normalization; publish at most one core safety state and one bounded virtual output per `eval_at_us`. Do not permit intermediate 'ARM then move then fault' within a single tick.
6. **Output trace**: write canonical decision and virtual output with run/config hashes, event IDs, fault codes and `SIM_ONLY` provenance, then advance to next tick. No viewer callback may inject an output between commits.

**Design choice pending:** if the owner prefers processing event-time microsteps rather than fixed periodic evaluation, that is a *different scheduler contract* and requires explicit ADR/test changes. Phase 2.1 recommends periodic event batching with documented quantization, not silently mixing both.

## 3. Virtual phase and precision

Proposed normalized virtual wing oscillator (only when permitted):

\[
\phi(t + \Delta t) = \operatorname{wrap}_{2\pi}\!\big(\phi(t) + 2\pi f_{sim}(t)\Delta t\big)
\]

Here `f_sim` is a **SIM_ONLY visualization frequency**, not physically measured stroke frequency or servo PWM carrier. `Delta t` is converted from integer microseconds to seconds once. A long tick gap is handled as elapsed time in one deterministic calculation or a *declared* scheduler fault; it must **not** silently create fake N wing cycles. On RESET, reset phase explicitly and log it. Avoid floating accumulation tied to loop iteration count; optionally compute phase from elapsed run time between documented profile changes, within an approved numeric tolerance.

The numbers `T_CORE=5000 us`, `PWM=20000 us`, `link_timeout=500000 us` in previous docs are **examples tagged SIM_ONLY**, **not normative**. Numeric tests use a `SimPolicy` that must be approved before design freeze and encoded in scenario trace. It is valid to test many time parameter values without treating any as physical limits.

## 4. Deterministic replay definition

Two runs are *logically equal* only when all of the following are equal: `schema version`, `scenario canonical bytes`, `configuration canonical bytes`, `core implementation revision`, `virtual clock schedule`, `explicit random seed` (if any) and `replay engine version`. Compare canonical decision/state/output records, excluding display-only wall timestamps, path separators and incidental UI render order. Avoid byte-identity assertions on platform-native floating serialization unless a canonical representation is actually defined; for numeric values either use an approved quantization format **or** a predeclared absolute/relative float tolerance. Event ids, reasons, ownership and states should match **exactly**.

**No external network fetches, host wall clock or non-seeded randomness may affect the replayed core.** Scenario parse order must not change same-time priority semantics.

## 5. Resource and error envelope

- Set **approved** maximum event count, total duration, event payload length, queue capacity, trace memory/disk quota and CPU budget before G0-A1. These are currently `TBD`; do not infer 'unbounded means safe'.
- Malformed JSON, recursion/depth abuse, duplicate IDs, invalid float encodings, timestamp overflows, too-large payloads and unsupported event types fail closed without virtual output.
- Trace storage failure: simulator returns `FAILED_INCOMPLETE_EVIDENCE` and does not print `PASS`. If failure occurs mid-run, the core halts with virtual outputs inhibited; report partial trace provenance.
- Event input stream closure is not automatically a valid radio failsafe test. The scenario must explicitly model `SIM_RF_STATUS`/timeouts so the final state is explainable.
- Long pause, evaluation overrun and clock-reset tests can be intentionally injected but they do not transfer timing requirements to ESP32 hardware.

## 6. Replay acceptance and test obligations

| ID | Host test proposal | Expected logical result |
|---|---|---|
| `TIME-01` | same scenario, config, seed, tick schedule twice | identical state/reason/event ID trace; numeric values within declared precision |
| `TIME-02` | permute presentation order of different event types at identical timestamps | same final state and virtual output due to atomic batch |
| `TIME-03` | two contradictory frames from same source in one timestamp | deny conflict; no inadvertent arm/flap |
| `TIME-04` | invalid timestamp / negative / fractional / overflow | scenario rejected before any motion |
| `TIME-05` | skip ticks, one large pause, wrap/reboot scenario | explicit fault or documented elapsed-time result; never autoarm |
| `TIME-06` | burst over queue limit / trace write failure | typed failure, no false PASS |
| `TIME-07` | RF LOST and ARM HIGH same tick | fault dominates, no enabled motion |
| `TIME-08` | same physical event time but different valid tick partitions | comparable states at common evaluation instants according to approved quantization contract |

All are **NOT RUN**. `PC-A14/15/18` in `52` cover a subset; the new tests strengthen definitions without claiming physical real-time performance.
