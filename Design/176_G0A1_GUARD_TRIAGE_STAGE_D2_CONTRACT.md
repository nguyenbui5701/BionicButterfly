# G0-A1 Stage D2 — Fail-Closed RF/Control Guard Triage (TASK-008)

- ID: BB-P220-176 · **Derived internal contract**, **no new policy / reason codes / wire events**.
- Exact baseline: `7c09bb5ab4d05d16bfa53439b5dab5b465ec8b05` · Scope: **PC_SIM_ONLY**.
- Authority: `Design/115–118`, `141`; previous task contracts `161`, `164`, `167`, `170`, `173`.
- Stage D2 is NOT the R1 SafetySupervisor, a trusted host allowlist, a frame admission source, an RF-effective-status authority, or a trace-committed state owner.

## 1. Safety invariant and implementation goal

Stage D1 gives categorical **evidence**. Stage D2 must produce a **negative-only/potential-only** report combining independent RF evidence, control evidence, the TASK-004 original timestamp ages and TASK-005 provisional fault priority. Its purpose is to prevent a later FSM implementer from accidentally equating *recent healthy RF* with *pilot authority* or using an in-tick candidate to erase an expired previously committed frame. Stage D2 DOES NOT produce a `HealthVerdict.PASS`, `ControlVerdict.ADMITTED`, `rf_effective`, `can_arm`, `output_allowed`, `state_after`, qualified windows, updated committed timestamp or trace ack.

**Important historical continuity distinction:** `prior_control_within_timeout=True` merely means *the last previously accepted control timestamp is at most 200000µs old*, not that a current candidate is accepted. `HEALTHY_CURRENT` does not undo a stale **prior** control age in an armed-state continuity check. `HEALTHY_CARRIED` only means an unverified claimed committed HEALTHY status with fresh arithmetic age. A previous LOST remains LOST until a future trusted commit verifies a distinct later HEALTHY; never replace it using an older fresh healthy timestamp.

Inputs (read-only, exact types):

```python
triage_guard_evidence(
    observations: NormalizedTickObservations,    # genuine TASK-003
    temporal: TemporalGuardFacts,                # genuine TASK-004
    priority: SafetyPriorityAssessment,          # genuine TASK-005
    health: HealthEvidenceFacts,                  # genuine TASK-007
) -> GuardTriageFacts
```

TASK-006 proposals are deliberately **not** an input; its hypothetical verdicts are not trusted. No extra `approved`, `trusted=True`, simulated app token or externally supplied health override is allowed. Input type checking is necessary but never sufficient to authenticate provenance. The caller and future state owner remain responsible for providing actual upstream results and the prior trace-confirmed snapshot, not arbitrary constructed lookalikes.

## 2. Exact immutable result (10 fields)

```text
GuardTriageFacts:
  tick_index: int
  eval_at_us: int
  pre_state: SafetyState
  rf_lane: RFGuardLane
  control_lane: ControlGuardLane
  armed_continuity_lane: ArmedContinuityLane
  current_rf_candidate_original_at_us: int | None
  current_control_candidate_original_at_us: int | None
  unresolved_reasons: tuple[GuardReason, ...]  # exact order; internal only
  requires_full_fsm: bool                      # ALWAYS True
```

All objects are frozen/slotted; no mutable nested collections, no generated output permission. Three CLOSED enums:

- `RFGuardLane`: `CURRENT_HEALTHY_UNCOMMITTED`, `CARRIED_HEALTHY_UNVERIFIED`, `AMBIGUOUS`, `NOT_HEALTHY`.
- `ControlGuardLane`: `NO_CANDIDATE`, `UNTRUSTED_CANDIDATE`, `INVALID_OR_CONFLICT`, `RF_BLOCKED`, `RF_AMBIGUOUS`, `PRIORITY_BLOCKED`.
- `ArmedContinuityLane`: `NOT_ARMED`, `PRIOR_STALE_OR_MISSING`, `HAZARD_OR_UNRESOLVED`, `POTENTIAL_S1_UNVERIFIED`.

`GuardReason`, internal diagnostic values only (never emitted as public `E_*`):

```text
PRIORITY_BLOCKED
RF_AMBIGUOUS
RF_NOT_HEALTHY
CONTROL_INVALID
CONTROL_CONFLICT
NO_UNCONTESTED_CONTROL
ARMED_PRIOR_RF_STALE_OR_MISSING
ARMED_PRIOR_CONTROL_STALE_OR_MISSING
TRUST_NOT_PROVEN
```

`unresolved_reasons` is sorted in **exact above enum order**, without duplicates. `TRUST_NOT_PROVEN` must ALWAYS be last even when all evidence looks favorable. A reason's presence is not a public runtime fault or definitive state transition.

## 3. Deterministic mapping of already-validated facts

Check all upstream tick and pre-state matches before assessing. Use only TASK-007 RF/control evidence labels plus TASK-003 flags and TASK-004 prior ages; **do not rerun/parse or reinterpret a raw event batch**.

**RF lane:**

| TASK-007 rf_evidence | RF lane |
|---|---|
| `HEALTHY_CURRENT` | `CURRENT_HEALTHY_UNCOMMITTED` |
| `HEALTHY_CARRIED` | `CARRIED_HEALTHY_UNVERIFIED` |
| `AMBIGUOUS_CURRENT` | `AMBIGUOUS` |
| All others: LOST CURRENT/CARRIED, UNKNOWN CURRENT/CARRIED, STALE_PRIOR, MISSING | `NOT_HEALTHY` |

Current RF candidate is **exactly** `temporal.observed_uncontested_healthy_rf_at_us` (not TASK-007 latest RF time when LOST/UNKNOWN exists). It may be non-null only for a HEALTHY_CURRENT all-healthy batch. A `None` candidate is not proof of unhealthy if it is carried healthy. A current RF candidate cannot refresh the previously committed RF time or status.

**Control lane:**

| TASK-007 control_evidence | Control lane |
|---|---|
| `ABSENT` | `NO_CANDIDATE` |
| `SINGLE_CANDIDATE` | `UNTRUSTED_CANDIDATE` |
| `INVALID`, `CONFLICT`, `INVALID_AND_CONFLICT` | `INVALID_OR_CONFLICT` |
| `BLOCKED_RF` | `RF_BLOCKED` |
| `DEFER_RF_AMBIGUOUS` | `RF_AMBIGUOUS` |
| `BLOCKED_PRIORITY` | `PRIORITY_BLOCKED` |

Current control candidate is **exactly** `temporal.observed_uncontested_valid_control_at_us`. A `SINGLE_CANDIDATE` NEVER means admitted, including when RF is fresh; a `NO_CANDIDATE` must never refresh an accepted timestamp. Contradictory facts (for example `SINGLE_CANDIDATE` with RF NOT_HEALTHY, priority blocker TRUE, or a missing current candidate) raise ordinary TypeError/ValueError rather than quietly returning a positive label.

**Armed-state prior continuity:** only for `ARM_CHECK`, `ARMED_IDLE`, `ACTUATION_ACTIVE`. In that group, check in this order:

1. If **either** prior-committed control or prior-committed RF timestamp is absent or age `>200000µs`, `PRIOR_STALE_OR_MISSING` — *even if the same tick has a fresh current healthy/control candidate*. This is fail-closed triage, not a final full R1 stale-state transition; the future arbiter may evaluate current acceptance according to R1 before committing the FSM.
2. Else if RF lane `NOT_HEALTHY` or `AMBIGUOUS`, or TASK-005 `blocks_control_qualification=True`, or priority has provisional fault/reset state, `HAZARD_OR_UNRESOLVED`.
3. Otherwise `POTENTIAL_S1_UNVERIFIED`, regardless of current frame presence; this is **not** permission for ACTIVE S1 hold, because the prior authorized intent, policy/host approval, effective current RF and trace-before-publish are unproven.
4. In `BOOT`, `SELF_TEST`, `DISARMED`, `CONTINGENCY`, `FAULT_LATCHED`, use `NOT_ARMED` always.

At 200000µs equality `prior_*_within_timeout=True`; at 200001µs False. Never replace an expired prior with current observation for step 1. No wallclock/timezone, float age rounding or mutation.

**Ordered `unresolved_reasons`:**

1. `PRIORITY_BLOCKED` iff current RESET or catastrophe, restricted prior `CONTINGENCY/FAULT_LATCHED`, or TASK-005 provisional next state in `SELF_TEST/CONTINGENCY/FAULT_LATCHED` (covers T0 BOOT). This is diagnostic; especially a C1 provisional ordinary RESET must NOT outrank unadjudicated stale armed hazards at future FSM commit.
2. `RF_AMBIGUOUS` if RF lane `AMBIGUOUS`, else `RF_NOT_HEALTHY` if lane `NOT_HEALTHY`.
3. `CONTROL_INVALID` iff TASK-003 has_invalid_control.
4. `CONTROL_CONFLICT` iff TASK-003 has_distinct_valid_control_conflict.
5. `NO_UNCONTESTED_CONTROL` iff TASK-004 observed current control candidate is None (absence includes invalid/conflict).
6. `ARMED_PRIOR_RF_STALE_OR_MISSING` iff prior state is armed and TASK-004 prior RF freshness False.
7. `ARMED_PRIOR_CONTROL_STALE_OR_MISSING` iff prior state is armed and TASK-004 prior control freshness False.
8. `TRUST_NOT_PROVEN` ALWAYS. Preserve exact order; no other enum names or new runtime error codes.

## 4. Validation, negative tests, and trust boundaries

- Reject wrong exact Python types (including bool-as-int, subclassed dataclasses and fake enum lookalikes), invalid grid/time, inconsistent TASK-003 flags, mismatched TASK-004 mirrors/ages and TASK-005 C1 priority. Reject forged TASK-007 label combinations: HEALTHY_CURRENT requires no LOST/UNKNOWN and an exact current uncontested-healthy timestamp; CARRIED_HEALTHY requires no current RF and prior RF freshness True; AMBIGUOUS requires current HEALTHY+UNKNOWN and no LOST; SINGLE_CANDIDATE requires an uncontested VALID control candidate, unblocked C1 and healthy RF evidence. Both TASK-007 and D2 are non-authenticating; these checks catch inconsistent call shape, not forged valid-lookalike provenance.
- TASK-007 itself owns current RF event scanning, its immutable payload and original timestamp validation; TASK-008 must **not rescan raw RF/control/source events**. Cross-check fixed record shapes/flags only: O(1) after upstream classification, irrespective of 1 vs 5000 current RF events or duplicate equivalent controls. No recalc of TASK-007, TASK-005, TASK-004 or any raw-wire parser.
- Never call TASK-006 with fabricated `HypotheticalQualificationVerdict(PASS, ADMITTED)`; never construct committed snapshots or a `GuardVerdict.PASS`. Never write `Source/host_arm_qualification` or any previously merged Source. Never emit `can_arm`, `control_accepted`, `rf_effective`, `output_allowed`, state_after, effort, trace, reason_codes, engine allowlist or hardware command.
- Runtime only stdlib + pinned local read-only TASK-003/004/005/007 packages (TASK-001/002/006 are test/build prerequisites). Python >=3.11; no network/FS/clock/RNG/threads/plugins/global mutable state/policy loading, callbacks or physical device SDK. Deterministic immutable output.
- Critical power/scheduler fault signals are not approved wire-v2 events. TASK-008 must **not** invent a new event type, no S1 authorization, no ACK clearance, no SELF_TEST readiness decision, no state commit/trace publication, no physical safety assertion.
- If an R1/R1.1 conflict or unsupported RF UNKNOWN+HEALTHY precedence arises, keep `AMBIGUOUS` and raise `BLOCKED — DESIGN CLARIFICATION`; new policy/schema needs explicit Owner/SA approval.

## 5. Future state-owner integration contract — NOT IMPLEMENTED HERE

Before any full-FSM positive decision is published, a **separate** module must consume a *trusted, previously trace-committed, immutable* snapshot containing at least prior FSM state, accepted-control original time, accepted healthy-RF original time, latest committed RF status and its original time, LOW/HIGH qualification history and last authorized intent. The future owner must verify policy/engine/scheduler allowlist independently of input JSON and commit one trace decision before publication. A standalone frozen dataclass, a Git hash, Stage D1/D2's diagnostic labels or `requires_full_fsm=True` are not sufficient authentication.

Keep this dependency explicit as a future task/gate; do **not** implement owner persistence or automatic promotion of D2 candidates in TASK-008. The complete R1 arbiter must resolve stale+RESET priority, UNKNOWN+HEALTHY ambiguity under approved policy, same-tick priority, carry behavior, and ACK recovery before authorizing a committed FSM transition. Do not certify P28 full-system oracles from these partial modules.

**G0-A1 PC_SIM_ONLY. G0-B/G4 physical receiver/servo/flight: NO-GO.**
