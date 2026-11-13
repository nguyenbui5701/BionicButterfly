# G0-A1 SafetySupervisor — Stage C1 Priority Kernel (TASK-005)

- Contract: BB-P217-167 · Derived implementation boundary · **no new R1 or R1.1 safety policy**.
- Verified merged `main`: `efe7fa3aff1beeb01af98b98a06593bd8e7af192`.
- Normative precedence: Design/115 (safety priority and states), 116 (PC-only SIM policy), 117 (error codes), 118 (commit-before-publish), 141 (R1 vs R1.1), 161 (batch facts), 164 (temporal facts).
- **IMPORTANT:** This is an *intermediate mandatory-priority assessment*, NOT a complete eight-state FSM, NOT a committed post-state decision and NOT an executable simulator.

## 1. Input and output data contract

A recommended pure function:

```text
assess_safety_priority(
    pre_state: SafetyState,                      # Enum, exactly one of the R1 eight states
    observations: NormalizedTickObservations,   # actual TASK-003 result
    temporal: TemporalGuardFacts,               # actual TASK-004 result on same tick
) -> SafetyPriorityAssessment
```

`SafetyState` contains exactly `BOOT`, `SELF_TEST`, `DISARMED`, `ARM_CHECK`, `ARMED_IDLE`, `ACTUATION_ACTIVE`, `CONTINGENCY`, `FAULT_LATCHED`. Developer may use `Enum[str]` or a closed immutable equivalent, **not** infer state from UI, scenario JSON or RF packets.

Output must be deeply immutable and contain only:

```text
SafetyPriorityAssessment:
    tick_index: int
    eval_at_us: int
    pre_state: SafetyState
    provisional_next_state: SafetyState | None     # ONLY a provisional R1 priority constraint, NOT committed
    priority_category: str | None               # internal evidence label, not an E_* runtime error
    blocks_control_qualification: bool          # negative factual gate; true never grants anything
    requires_full_fsm: bool                     # ALWAYS True until complete FSM + trace gate exist
```

Recommended stable internal `priority_category` values: `BOOT_INITIALIZATION`, `LATCH_PERSISTS`, `CATASTROPHIC_FAULT`, `CONTINGENCY_HOLD`, `ARMED_OBSERVED_HAZARD`, `ORDINARY_RESET`. When `provisional_next_state is None`, category must be `None` and later FSM must resolve all remaining safety transitions. These names are *internal assessment labels*, **not** additions to the public R1 `reason_codes` vocabulary. A provisional C1 constraint is not a published, committed transition. In particular, CONTINGENCY_HOLD can be superseded only by a later complete FSM that proves all approved ACK-recovery prerequisites.

No `state_after`, `accepted_control_at_us`, `rf_effective`, `can_arm`, `output_allowed`, `effort`, `reason_codes`, trace ID or commit acknowledgement may appear here. Never make an output permission inferred from `requires_full_fsm`.

## 2. Exact priority order / conditions for this slice

Process already-normalized full-batch facts before adjudication. All event flags are facts, not sequential callbacks. After validating matching tick indices/timestamps and mirrored flags between TASK-003 and TASK-004:

**A. Latch persistence (highest for a prior latched state):** If `pre_state==FAULT_LATCHED`, `provisional_next_state=FAULT_LATCHED`, category `LATCH_PERSISTS`, regardless of RESET, ACK, RF HEALTHY or simultaneous catastrophe. In-run latch never clears.

**B. Current catastrophe:** Otherwise if `observations.has_catastrophe`, require `FAULT_LATCHED`, category `CATASTROPHIC_FAULT`. This outranks RESET, ACK, LOW, RF, UART invalid and control conflict in any pre-state.

**C. Existing CONTINGENCY:** Otherwise if `pre_state==CONTINGENCY`, require `CONTINGENCY`, category `CONTINGENCY_HOLD`. This *C1 kernel* cannot approve ACK recovery: a future full FSM may supersede this provisional hold **only after** proving prior committed LOW qualification, all causes cleared, approved recoverable allowlist, no concurrent RESET/catastrophe. C1's hold is thus a safe interim hold, not a permanent new recovery ban.

**D. Unambiguous observed hazards in `ARM_CHECK`, `ARMED_IDLE`, `ACTUATION_ACTIVE`:** if `observations.has_invalid_control` OR `observations.has_distinct_valid_control_conflict` OR `observations.rf_has_lost` OR (`observations.rf_has_unknown` AND NOT `observations.rf_has_healthy`), then require `CONTINGENCY`, category `ARMED_OBSERVED_HAZARD`. Any simultaneous RESET is lower priority. `RF HEALTHY+LOST` resolves as hazardous LOST under Design/115. An `RF HEALTHY+UNKNOWN` mixture without LOST is deliberately **not resolved** in C1; no required state is assigned from it, and the later FSM is forbidden to treat this as an all-healthy pass without explicit R1-conformant resolution.

**E. Ordinary RESET:** Otherwise if `observations.has_reset`, require `SELF_TEST`, category `ORDINARY_RESET`, from all other pre-states (including DISARMED/SELF_TEST/armed states with no recognized higher hazard). RESET blocks same-tick LOW/HIGH/frame qualification. RESET does **not** clear CONTINGENCY or FAULT_LATCHED, because C/B/A took priority.

**F. BOOT:** Otherwise when `pre_state==BOOT`, require `SELF_TEST`, category `BOOT_INITIALIZATION`, strictly at tick 0 with `has_boot=True`. The strict accepted v2 wire contains BOOT at 0 only. A BOOT pre-state at a later tick, or non-BOOT pre-state at T0, is an invalid trusted-caller snapshot and raises ValueError before returning an assessment. Any catastrophe at tick 0 would be impossible under TASK-001 and is not a valid positive oracle.

**G. Otherwise:** leave `provisional_next_state=None`, category `None`, `requires_full_fsm=True`. This means **NO DECISION**, not “retain state”, “healthy”, “accepted”, “armed”, or “authorize output”. Examples: SELF_TEST completion needs independent host readiness; DISARMED LOW needs 20ms qualification; ARM_CHECK HIGH needs 100ms; ACTIVE hold needs full current RF and accepted-frame health; ACK recovery needs previous committed LOW. These will be later tasks.

### 2.1. What `blocks_control_qualification` means

This is a negative-only flag: `True` if any of the following is present in current batch or interim state decision: `has_catastrophe`, `has_reset`, `has_invalid_control`, `has_distinct_valid_control_conflict`, `rf_has_lost`, `rf_has_unknown`, or `pre_state in (CONTINGENCY,FAULT_LATCHED)` **or** `provisional_next_state in (SELF_TEST,CONTINGENCY,FAULT_LATCHED)`. An UNKNOWN+HEALTHY mixed tick is also blocked even if category is None. All other cases False does *not* mean a control may qualify: full FSM, policy, freshness and trace are still required.

Additionally, for `ARM_CHECK`, `ARMED_IDLE` or `ACTUATION_ACTIVE`, if either prior-committed control or RF timestamp is absent/stale (`prior_*_within_timeout=False`), set the block flag **True** without choosing an age-based state transition. This is a negative-only safeguard, not a replacement for the future FSM health-resolution rules; even a fresh current candidate cannot grant permission here.

`blocks_control_qualification` is not a runtime approved `output_allowed` field and cannot be used as its inverse. It never refreshes original timestamps. Critical power/scheduler signals are **not exposed as approved wire-v2 events** and are outside this stage; such cases must not silently be labeled healthy by a missing critical-fault input.

## 3. Boundary checks and purity

- Exact `SafetyState` value; no user JSON-derived owner or state. For T0, require BOOT and the first tick; for later ticks, reject BOOT as pre-state. The later state owner is responsible for providing a committed pre-snapshot.
- `type(observations) is NormalizedTickObservations`, `type(temporal) is TemporalGuardFacts`; match exact `tick_index`, `eval_at_us` and grid. Cross-check all common boolean facts: LOST, UNKNOWN, INVALID and VALID conflict. Reject malformed caller/mismatched shape rather than guessing a state. The check is **not cryptographic authentication** of a manually forged wrapper.
- No modification of original accepted preflight, scheduler, normalized observations, temporal facts or prior committed timestamp record. No local clock, IO, filesystem, network, device driver, policy loader, trace engine, mixer, return of committed state, actor, sink, runtime callback or process-global mutable memory.
- Pure O(1) flag-based decision once TASK-003 and TASK-004 data is provided; avoid scanning events or re-validating wire here.
- Distinguish **observed explicit hazard** from **age-based stale health**: C1 does not adjudicate stale age vs same-tick fresh current candidates. Do not synthesize `E_FRAME_STALE` or force CONTINGENCY merely by inspecting TASK-004 `prior_*_within_timeout` without a full R1 freshness-resolution layer. Any `None` result is strictly pending, including ACTIVE with both prior ages stale. This limits C1's safety claim; later tasks MUST close the gap before virtual output or full FSM is available.
- C1's provisional CONTINGENCY hold must NOT be mistaken for overriding future approved ACK clearance. Never claim P28-T08/T09/T13/T14/T26 full FSM or output PASS at this stage.

## 4. Mandatory hierarchy and prohibitions

Any new public scenario event type (voltage/scheduler), runtime `E_*` code, RF UNKNOWN+HEALTHY effective-health priority, approval bypass, arming rule, committed timestamp update, trace/report or hardware control requires new SA review and owner approval. R1/141 precedence wins over any convenience in this derived slice. TASK-005 never outputs a physical servo command or even an authorized dimensionless pair. G0-B/G4 remains NO-GO.
