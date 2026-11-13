# G0-A1 — Pure Virtual Tick Batch Enumerator (TASK-002)

- **Document:** BB-P214-158 · **Type:** executable interpretation / implementation boundary derived from approved R1 + R1.1
- **Immutable source:** `ca457f784975c2d0959b1baf988483fa042f5c67` · **Owner-approved controls:** `115`, `116`, `132`, `141`.
- **New behavioral policy:** **NONE**. This document does not alter the R1 FSM, input schema, replay schema or host trust requirements.

## 1. Clock and window (normative excerpts of approved R1)

`step_us=5000`. For a fully preflight-accepted wire-v2 scenario, `duration_us` is an integer multiple of 5000 in `[5000,60000000]`. Enumerate tick indices `k=0..duration_us/5000`, inclusive:

- `eval_at_us(k) = k*5000` with **integer arithmetic only**.
- Tick 0 window: exactly `event_at_us=0` (v2 requires `BOOT` first, and no other T0 events).
- Tick `k>0` window: `(eval_at_us(k-1), eval_at_us(k)]` — **left-exclusive, right-inclusive**.
- Count of ticks for a complete, uninterrupted enumeration: `duration_us/5000 + 1` (at maximum 60s = 12001 ticks).
- Preserve each event's **original** `event_at_us` and `event_id`; eligibility at an upper tick does not rewrite event time for later freshness or qualification calculations.
- An empty event window still yields **one empty tick batch**. Do not fabricate a control frame/ACK/RF refresh or LOW/HIGH qualification event.

## 2. Pure interface and minimal record

SA approves an internal, pure *reference shape* (Developer may choose dataclass/NamedTuple or equivalent and document it) for each tick:

```text
VirtualTickBatch:
  tick_index: int                    # 0 through duration/step inclusive
  eval_at_us: int                    # exact integer microseconds
  events: immutable ordered sequence # references/immutable values from validated scenario
```

Recommended callable `iter_virtual_ticks(accepted: AcceptedPreflight) -> Iterator[VirtualTickBatch]`. It must require the **TASK-001 accepted-result boundary**, not raw dicts/unvalidated JSON; `RejectedPreflight` and wrong types cause a normal trusted-caller error without emitting any tick or diagnostic sidecar. Do not claim that possession of `AcceptedPreflight` cryptographically proves a trusted host allowlist or grants permission to execute a safety FSM.

Every accepted event must appear in **exactly one** batch, even when multiple events share one timestamp. Preserve the original array order inside a batch; **do not sort, de-duplicate, normalize, coalesce or change event semantics**. Derivable event ID summaries for later trace handling should be computed by future modules, not by rewriting the event batch. Each batch and its event collection must be immutable from the caller's viewpoint; the source accepted scenario stays unchanged.

`iter_virtual_ticks` is a **pure scheduling view**, not an event dispatcher. Consuming an iterator must never invoke `validate_wire` again, `mixM0`, real-time sleep, system clock, environment RNG, network APIs, SafetySupervisor, TraceCommitter or virtual output callbacks. A batch is not a committed tick decision. A complete trace must still be created later by the approved transaction rules in `118`.

## 3. Batch composition deliberately deferred to SafetySupervisor

- Same-tick **different valid control frames** remain separate; no `E_CONTROL_BATCH_CONFLICT` is produced here. That error belongs to the approved full-batch normalization/transition module.
- Same-tick equivalent control bodies with distinct event IDs remain separate; control-equivalence collapse happens later.
- RF HEALTHY+LOST remain separate; no RF priority resolution here.
- Catastrophic fault+RESET+ACK remain separate; catastrophe's higher priority is enforced later by FSM, not scheduler.
- In-band `SIM_CONTROL_FRAME INVALID` remains a valid **scheduled observation**, not a malformed-scenario rejection.
- An empty tick never implies a synthesized `SIM_CONTROL_FRAME`, RF observation, or privileged action. Any S1 held intent must be evaluated later, subject to R1 freshness and committed trace gate.

## 4. Boundary and implementation constraints

- Required complexity for a single traversal: `O(ticks + events)` (linear scan/two-pointer), no per-tick scanning of all events; memory bounded by active batch plus the preflight scenario already present. Avoid eager copying 12001 full event lists.
- Each tick contains a distinct immutable batch object; callers can iterate once per fresh invocation for deterministic equivalence. Developer must document whether the returned iterator itself is one-shot; do not expose an iterator with hidden mutable shared global state.
- No changes to the frozen wire schema or TASK-001 parser. If a valid accepted scenario violates a property assumed by the scheduler, raise a design issue to SA; do not silently filter or truncate it.
- Exception behavior for invalid trusted-call arguments is a library API error and does **not** add `P_*` codes or `SimulationRunReportV2` fields.
- This module does **not** decide whether a run terminates early after a fault. It enumerates a static complete clock plan; the later controlled runtime may stop consuming ticks after a committed terminal result.

## 5. Positive and negative examples

For duration=10000, events `BOOT@0`, `RF@1`, `RESET@4999`, `ACK@5000`, `RESET@5001`, `ACK@10000` produce:

| tick_index | eval_at_us | input event times |
|---:|---:|---|
| 0 | 0 | `[0]` |
| 1 | 5000 | `[1,4999,5000]` |
| 2 | 10000 | `[5001,10000]` |

This is batch eligibility only: `RESET`, `ACK` and `RF` have **no state effects** at TASK-002 boundary. In particular, the 4999µs event must retain 4999µs, not become 5000µs. At duration=60000000, there are exactly **12001** yielded ticks even with only one BOOT event.

## 6. Gate for delivery

See `Design/159_TASK002_SCHEDULER_TEST_ORACLES_AND_REVIEW.md` and `fixtures/P214_TICK_BATCH_ORACLE_INDEX.json`. These are **specified expected outcomes**, not tests that SA claims to have run on Developer's future code. Runtime remains PC_SIM_ONLY and non-actuating; physical/G0-B/G4 remain NO-GO.
