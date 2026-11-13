# G0-A1 — SafetySupervisor Stage A: Pure Tick Observation Normalizer

- ID: BB-P215-161 | Scope: `PC_SIM_ONLY` | Derived internal interface, **no new R1/R1.1 policy**
- Source main pin: `12b4ee1355d146080810d028843d24481f88af77`.
- Authority: approved `Design/115`, `116`, `117`, R1.1 `132`, `141`; input shape comes from merged TASK-002 `VirtualTickBatch`.

## Purpose and restrictions

Transform one complete already-scheduled immutable tick batch into an **informational read-only observation view** for a future SafetySupervisor. Do not transition FSM, resolve full runtime fault reason priority, update RF/pilot freshness, qualify LOW/HIGH, select authorized intent, run M0, generate trace/report, publish virtual output, or touch hardware/network/filesystem. A `VirtualTickBatch` type check is NOT trusted-host authorization.

### Required observable semantics

1. **Input:** exactly TASK-002 `VirtualTickBatch`, not raw dict/bytes/`RejectedPreflight`. Bad callers raise an ordinary API exception immediately; do not invent `P_*` or `E_*` wire error. Preserve the original event references and order.
2. **Causal IDs:** include *all* IDs for the tick, sorted by **unsigned UTF-8 bytes** without Unicode normalization. The sorted metadata is separate from the original source-event tuple.
3. **Valid controls:** group all `SIM_CONTROL_FRAME` with `uart_frame_status=VALID` by **exact decoded semantic body** `(arm_switch, flap_demand, steering_demand, map_revision)`. Same decoded values, different lexical decimal spellings or different timestamps = one group. Use exact accepted int/Decimal values; do not convert to binary float. Group order follows **first appearance** in the source batch. Each group records original member event references in input order, *sorted* member IDs, and **latest original event_at_us**, not evaluation tick time. A group is only a CANDIDATE; never an accepted or authorized pilot intent.
4. **Invalid controls:** preserve all typed `SIM_CONTROL_FRAME` with status `INVALID` and their IDs. Expose flags `has_invalid_control`, `has_distinct_valid_control_conflict` (more than one valid semantic group), and `has_duplicate_semantic_control` (a valid group has >=2 distinct member IDs). All flags can co-exist. **Scan every event; do not short-circuit.** Two different valid bodies in one tick are a conflict *fact*, not yet an emitted `E_CONTROL_BATCH_CONFLICT`; an INVALID is an observation, not a parser rejection. The later FSM must suppress accepted frame use if INVALID/conflicting VALID controls occur.
5. **RF observations:** keep every `SIM_RF_STATUS` event and timestamp in source order; expose independent presence flags `rf_has_healthy`, `rf_has_lost`, `rf_has_unknown`. A same-tick HEALTHY+LOST pair must remain visible so the future FSM can apply R1's LOST dominance. **Do not compute rf_effective, last_RF timestamp, freshness or choose an unsupported UNKNOWN+HEALTHY priority here.**
6. **Other events:** presence booleans `has_boot`, `has_reset`, `has_ack`, `has_catastrophe`; preserve every original event. Two distinct-ID ACKs set `has_ack` once without triggering two recoveries. Catastrophe+RESET+ACK is three preserved stimuli; no FSM priority computed.
7. **Empty batch:** all flags false, no groups, no RF, no causal IDs. Do not synthesize a control, RF refresh or timer-based action.
8. **Immutability/purity:** returned nested data is deeply immutable and deterministic, the source accepted scenario is unchanged. No parser re-run, scheduler re-run, clock/sleep/RNG, I/O, trace, M0, state transition or output callback.

## Required result information (Developer can choose immutable dataclasses or equivalent)

```
NormalizedTickObservations:
  tick_index: int
  eval_at_us: int
  source_events: tuple[original immutable event mappings, ...]  # source order, same references
  causal_event_ids: tuple[str, ...]                        # all, unsigned UTF-8 sorted
  valid_control_groups: tuple[ValidControlGroup, ...]       # first-seen group order
  invalid_control_event_ids: tuple[str, ...]                # unsigned UTF-8 sorted
  has_invalid_control: bool
  has_distinct_valid_control_conflict: bool
  has_duplicate_semantic_control: bool
  rf_events: tuple[original immutable RF event mappings, ...] # source order
  rf_has_healthy / rf_has_lost / rf_has_unknown: bool
  has_boot / has_reset / has_ack / has_catastrophe: bool

ValidControlGroup:
  semantic_control: immutable full VALID control body (exact accepted values)
  member_events: tuple[original immutable event references, ...]  # source order
  event_ids: tuple[str,...]                                 # UTF-8 sorted
  latest_original_at_us: int                                # max ORIGINAL time
```

Output MUST NOT include `state_after`, `reason_codes`, `rf_effective`, `accepted_frame_at_us`, `control_authorized`, `can_arm`, `output_allowed`, `left_micro_effort` or `right_micro_effort`, because these falsely imply decisions not yet made.

## Edge cases

- Same semantic content + different valid original IDs is one group but retains all IDs and all event references; duplicate `event_id` itself was already rejected by TASK-001 preflight.
- `0.1000000` and `1e-1` map to equal accepted values and one group; `0.100001` must create a second group. Negative zero is equivalent to zero after accepted-value normalization.
- Different VALID bodies and `INVALID` in the same tick set **both** conflict and invalid facts. Future state-priority logic decides consequences; no reason-code priority is selected here.
- `RF UNKNOWN` mixed with `HEALTHY` preserves both flags without inventing a rule. `LOST` dominates healthy only at the future effective-health stage, per R1.
- No prior-tick RF/control data is carried forward; Stage A is pure per-tick classification.

## Safety layering and future tasks

R1 order is immutable pre-state -> TASK-002 tick batch -> TASK-003 full-batch normalization -> future health and state decision -> tentative virtual command -> append committed trace -> publish. Later work is independently gated by owner-approved host policy/revisions, freshness and trace obligations. **No physical RF receiver, firmware, PWM, GPIO, servo or flight authorization.**
