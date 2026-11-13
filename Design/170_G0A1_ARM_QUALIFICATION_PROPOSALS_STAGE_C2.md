# G0-A1 — Stage C2 ARM/DISARM Qualification Proposal Contract

- Contract: BB-P218-170 | **Derived internal mechanics only, not new safety policy** | `PC_SIM_ONLY`
- Exact baseline: `f2c9237bd4a1e2e077c15db6eb4c22ed2a250d5d`
- Normative references: `Design/115` §§2–4, `Design/116` policy parameters, `Design/117`, `Design/118`, `Design/141`, and Stage A/B/C1 `Design/161`,`164`,`167`.

## 1. Core rule: no self-authorized frame or state

Implement a **pure, immutable, one-tick proposal calculator** from real TASK-003 normalized facts, TASK-004 temporal facts and TASK-005 safety-priority assessment plus an **independently provided, explicitly hypothetical** guard verdict and a synthetic or previously committed qualification-window snapshot. A proposed LOW/HIGH milestone is **NOT** an accepted frame, committed state transition, committed timestamp, trace acknowledgement, `can_arm`, `output_allowed`, or an authorized command.

This deliberately separates *testing R1 timing mechanics* from *having an actual approved current RF + frame + policy decision*. TASK-006 is forbidden from deciding `rf_effective`, blindly treating `prior_*_within_timeout=True` as healthy, authenticating a caller by dataclass type, or creating a new runtime `E_*` code. A production FSM MUST NOT consume these test hypotheses as trusted input. No production health-arbiter adapter exists yet.

### Inputs (one tick)

```text
propose_arm_qualification(
  observations: NormalizedTickObservations,      # genuine TASK-003 (read-only)
  temporal: TemporalGuardFacts,                  # genuine TASK-004 same tick
  priority: SafetyPriorityAssessment,            # genuine TASK-005 same tick
  prior_window: PriorQualificationWindow,        # synthetic TEST fixture now; future trace-committed snapshot
  verdict: HypotheticalQualificationVerdict,    # synthetic TEST fixture now; future separately guarded R1 adjudication
) -> ArmQualificationProposal
```

`PriorQualificationWindow` is a frozen record:

```text
  last_committed_eval_at_us: int | None
  low_first_original_at_us: int | None
  low_qualified_committed_eval_at_us: int | None
  high_edge_original_at_us: int | None
  high_edge_committed_eval_at_us: int | None
```

- For T0, all fields `None`; at later ticks `last_committed_eval_at_us` is exact int on the 5,000us grid, `0 <= prior_commit < current_eval` (the future runner must commit **every** tick; a test synthetic prior is not real proof).
- `low_first_original_at_us` is the **first** accepted LOW original time of the uninterrupted series; if present, `0 <= low_first <= prior_commit`.
- `low_qualified_committed_eval_at_us` is set **only after a distinct later tick** containing a second accepted LOW with original separation `>=20,000us` was fully committed. It requires `low_first` and `0 <= qualified_eval <= prior_commit`, aligned to 5ms grid; it cannot be the current tick. This record **cannot itself prove** history was truly committed; that is future FSM/trace responsibility.
- `high_edge_original_at_us` and `high_edge_committed_eval_at_us` exist together, only for prior state `ARM_CHECK`. `0 <= edge_original <= edge_commit <= prior_commit`, edge_commit aligns to 5ms grid. Low fields are `None` after the proposed HIGH edge; prior state `DISARMED` may have only LOW fields. In other states the window must be empty. Contradictory snapshots reject as caller errors, not fabricated wire diagnostics.

`HypotheticalQualificationVerdict` is a frozen **non-authoritative** record with exact enum values:

```text
  health: PASS | FAIL | UNRESOLVED
  control: ADMITTED | ABSENT | DENIED | UNRESOLVED
```

- `PASS` is only a **test assumption** that later R1 health/policy/map/RF/frame arbitration passed; it does *not* assert that such arbitration exists. `ADMITTED` is only a hypothetical result from that future arbiter, not a command from user JSON. Neither is a permission token or credential.
- `ADMITTED` requires `health=PASS`, a single uncontested current VALID control group, and exactly matching TASK-004 current control-candidate original timestamp. If priority says blocked, the assumption is contradictory and must be rejected, rather than silently accepting a frame.
- `ABSENT` means no current valid control candidate. `DENIED` means a candidate exists but was rejected by the hypothetical arbiter. `UNRESOLVED` means acceptance cannot yet be decided. Positive milestones are **never** returned for DENIED/UNRESOLVED.
- A `health=PASS` assumption contradicting `priority.blocks_control_qualification=True` is rejected. A `health=FAIL` or `UNRESOLVED` cannot have `control=ADMITTED`.
- At T0, no qualification. TEST helper may create synthetic verdicts; must never inject these fields into wire JSON or the real accepted scenario.

### Output (precisely nine fields, deeply immutable)

```text
ArmQualificationProposal:
  tick_index: int
  eval_at_us: int
  pre_state: SafetyState
  proposal_kind: ProposalKind                    # enum defined below
  proposed_low_first_original_at_us: int | None
  proposed_low_qualified_committed_eval_at_us: int | None
  proposed_high_edge_original_at_us: int | None
  proposed_high_edge_committed_eval_at_us: int | None
  requires_full_fsm: bool                        # ALWAYS True
```

`ProposalKind` is exactly one of: `DEFER`, `NO_CHANGE`, `HOLD_WINDOW`, `LOW_START`, `LOW_PENDING`, `LOW_QUALIFIED`, `HIGH_EDGE_ELIGIBLE`, `HIGH_PENDING`, `HIGH_CONFIRMED`, `DEMAND_OBSERVED`, `LOW_DISARM_OBSERVED`, `BLOCKED_CLEAR`, `CLEAR_WINDOW`.

**No** `post_state`, `state_after`, `can_arm`, `accepted_control_at_us`, `rf_effective`, reason codes, accepted history snapshot, output effort, trace record, callbacks, or commit. The four proposed-window fields are candidate values **only**: the future real FSM can discard them or atomically persist an independently validated decision. The result never mutates the input snapshot.

## 2. Ordered proposal rules

At each tick use only immutable upstream records. Validate exact type and matching tick/index/`pre_state` first; assert TASK-005 `requires_full_fsm=True`. TASK-005's `provisional_next_state` is **not** necessarily the full R1 next state.

1. If a mandatory prior latch/catastrophe/RESET/armed explicit hazard appears via priority (e.g. C1 provisional next state `FAULT_LATCHED`, `SELF_TEST`, or `CONTINGENCY` from armed state), propose `BLOCKED_CLEAR` with four `None` window fields. This **does not** commit state. For prior `CONTINGENCY` specifically, propose `DEFER` without a new window; **ACK-recovery LOW series is deferred to a separate task**, and C1's provisional hold cannot permanently override that R1 recovery.
2. If `priority.blocks_control_qualification` or `health=FAIL`: propose `BLOCKED_CLEAR`. A health failure invalidates LOW/HIGH continuity even on an empty tick. Do not authorize transitions.
3. If `health=UNRESOLVED` or `control=UNRESOLVED`: propose `DEFER`, preserving the *proposed* prior window for DISARMED/ARM_CHECK, but never qualifying from a new event. A full state owner must not commit it without resolved health continuity.
4. If `control=DENIED`: propose `CLEAR_WINDOW` (fail closed; denied/mismatched frame breaks continuity). If `control=ABSENT`, propose `HOLD_WINDOW` for an existing window, or `NO_CHANGE` otherwise. Silence is **not** a second LOW/HIGH; preservation requires the hypothetical `health=PASS` for this tick.
5. In `DISARMED` with admitted **LOW** (`arm_switch=False`): if no LOW series, `LOW_START` at **original** accepted time; if an unqualified series exists and this is a **later tick** with original separation `<20,000us`, `LOW_PENDING` (keep original first anchor); separation `>=20,000us` gives `LOW_QUALIFIED`, whose proposed qualification commit tick is **the current eval tick**, but eligibility for any HIGH edge requires a **later independently committed tick**. Already qualified LOW stays `HOLD_WINDOW` (no re-qualification timestamp refresh). No timer/empty tick qualifies LOW.
6. In `DISARMED` with admitted **HIGH** (`arm_switch=True`): it breaks the LOW series. Only when `low_qualified_committed_eval_at_us < current eval`, and frame is **neutral** (`flap_demand <=0.02` and `abs(steering_demand)<=0.05`, both exact accepted Decimal comparisons) propose `HIGH_EDGE_ELIGIBLE`, record **original** accepted timestamp and current eval as the *proposed* edge-commit tick, and clear LOW fields. Otherwise `CLEAR_WINDOW`. No demand/ARM permission.
7. In `ARM_CHECK`: admitted LOW -> `LOW_DISARM_OBSERVED`, clear windows; a HIGH must be neutral. For neutral HIGH at a **later tick** than committed high edge, original time difference `<100,000us` -> `HIGH_PENDING`, preserve original HIGH edge (do not shift start); `>=100,000us` -> `HIGH_CONFIRMED`, proposed windows cleared (future FSM may transition to ARMED_IDLE **only after independent guards/commit**). Non-neutral HIGH -> `CLEAR_WINDOW`. An empty tick cannot confirm HIGH; guard FAIL breaks continuity.
8. In `ARMED_IDLE`: admitted LOW -> `LOW_DISARM_OBSERVED`; admitted HIGH with exact `flap_demand >0.05` -> `DEMAND_OBSERVED`; else `NO_CHANGE`. In `ACTUATION_ACTIVE`, admitted LOW -> `LOW_DISARM_OBSERVED`; otherwise `NO_CHANGE`. None means a real output is allowed; ACTIVE S1 hold is **deferred**.
9. `BOOT`, `SELF_TEST`, `CONTINGENCY`, `FAULT_LATCHED`: no positive qualification proposals; return `DEFER` or mandatory `BLOCKED_CLEAR` as above. The separate ACK-recovery series in CONTINGENCY is not implemented by this task.

## 3. Critical timing/precedence examples

- LOW original @15,000µs, next @34,999µs => **19,999**: not qualified; @35,000µs => **20,000** qualifies. Do not round event timestamp to evaluation tick before subtracting.
- LOW second @35,000µs proposes qualification at eval @35,000µs. HIGH **cannot** use it in that same tick. Only a *prior-committed* qualification at @35,000µs may support HIGH edge @40,000µs.
- HIGH neutral edge original @40,000µs, confirming HIGH @139,999µs => **99,999** pending; @140,000µs => **100,000** confirmed. An empty tick @140,000µs cannot confirm HIGH.
- Neutral arm check uses `flap_demand <=0.02` and `|steering_demand| <=0.05`; equality allowed. Threshold to observe an ACTIVE-demand in ARMED_IDLE is strictly `flap_demand>0.05`; equality is insufficient.
- Valid frame + INVALID, two different VALID frames, RF LOST, RF UNKNOWN, catastrophe or RESET must not produce LOW/HIGH/ACTIVE-demand milestones despite apparently favorable synthetic verdicts. Use C1 priority blockers and reject contradictory `PASS/ADMITTED` assumptions. In particular **RESET cannot bypass stale/critical health priority in the full FSM**, which this stage does not implement.
- If a prior LOW series is broken, future rearming starts with a new LOW observation. DISARMING from ACTIVE/IDLE/ARM_CHECK does **not** treat that same LOW as first new qualifying LOW.
- Never claim `P28-T08/T09/T13/T14/T26` full state/output conformance PASS merely because these proposal mechanics pass.

## 4. Trust, complexity, regression, stop conditions

Strict exact Python types (`bool` is not `int`), 5000us grid, original source timestamp window, prior window invariants, `Decimal` exactness. The normalization layer must supply the one VALID group; TASK-006 does not re-parse wire or scan all source events. Complexity **O(1)** over already-normalized metadata and one group. No global memory, clock, IO, network, hardware, JCS trace, mapper/mixer, state commit, guard arbiter or virtual sink.

An operational adapter, source of trusted prior snapshot, host allowlist, frame/RF effective-health adjudicator, complete FSM and transaction publisher **do not exist in TASK-006**. A library with a public hypothetical verdict is **not an authorization boundary**. The next task must implement these pieces before any end-to-end simulator can be certified. Physical servo/RC/flight remain NO-GO.

If a Developer finds a policy/health ambiguity not covered by frozen R1, STOP and raise `BLOCKED — DESIGN CLARIFICATION`; never invent new E_ codes, RF UNKNOWN priority, wire fields, runtime trust or physical outputs.
