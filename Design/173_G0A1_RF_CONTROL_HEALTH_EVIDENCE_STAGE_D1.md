# G0-A1 Stage D1 — RF + Control Health Evidence (TASK-007)

- ID: BB-P219-173 · **Derived internal contract**; no new R1/R1.1 priority, schema, reason code or policy.
- Parent Git pin: `a47dc157453547125f5172b4ef165c3b522ff0c8` · Scope: **PC_SIM_ONLY** · External trust/flight: **NOT PROVIDED**.
- Normative hierarchy: `Design/115–118`, `141`; current source boundaries `161` (TASK-003), `164` (TASK-004), `167` (TASK-005), `170` (TASK-006).

## 1. Problem and explicit non-authority

The timestamp in TASK-004 `last_uncontested_healthy_rf_at_us` says **when a healthy observation was accepted previously**, not whether a later LOST/UNKNOWN observation has replaced that health status. A new current HEALTHY status can supersede a LOST committed in an earlier tick, but **same-tick HEALTHY+LOST is LOST** per R1/115. HEALTHY+UNKNOWN in a single tick is **not resolved by approved R1**: classify as `AMBIGUOUS_CURRENT`, never infer HEALTHY. The complete FSM alone will eventually commit an authorized effective status.

TASK-007 MUST NOT create a control authorization, a `HealthVerdict.PASS`, a `ControlVerdict.ADMITTED`, an accepted timestamp, a committed history, a state_after or a virtual/physical output. Its output is diagnostic **evidence classification only**. Even `SINGLE_CANDIDATE` means "one syntactically valid observation survived known negative filters"; it is **not a trusted frame** and cannot be handed to TASK-006 as an authoritative `ADMITTED` verdict. Do not implement a production adapter from TASK-007 to TASK-006 in this task.

### Pure API

```text
class PriorCommittedRFStatus:
    last_committed_eval_at_us: int | None
    last_rf_status: RFStatus | None        # HEALTHY | LOST | UNKNOWN | None
    last_rf_original_at_us: int | None

assess_health_evidence(
    observations: NormalizedTickObservations,        # genuine TASK-003
    temporal: TemporalGuardFacts,                    # genuine TASK-004
    priority: SafetyPriorityAssessment,              # genuine TASK-005
    prior_rf: PriorCommittedRFStatus,                 # separately sourced, TEST-SYNTHETIC in this task
) -> HealthEvidenceFacts
```

`PriorCommittedRFStatus` is **read-only** and cannot authenticate its own provenance. The independent future state owner must produce a genuine prior committed snapshot; TASK-007 tests use synthetic fixtures clearly labeled TEST_ONLY. No RF status field may be read from scenario JSON except approved `SIM_RF_STATUS` events already present in the wire schema. No new public fields or event types.

### Exactly eight immutable result fields

```text
HealthEvidenceFacts:
  tick_index: int
  eval_at_us: int
  pre_state: SafetyState
  rf_evidence: RFEvidenceKind
  latest_current_rf_original_at_us: int | None
  control_evidence: ControlEvidenceKind
  observed_control_candidate_original_at_us: int | None
  requires_full_fsm: bool                      # ALWAYS True
```

`RFEvidenceKind` exactly `MISSING, STALE_PRIOR, HEALTHY_CURRENT, HEALTHY_CARRIED, LOST_CURRENT, LOST_CARRIED, UNKNOWN_CURRENT, UNKNOWN_CARRIED, AMBIGUOUS_CURRENT`.

`ControlEvidenceKind` exactly `ABSENT, SINGLE_CANDIDATE, INVALID, CONFLICT, INVALID_AND_CONFLICT, BLOCKED_RF, BLOCKED_PRIORITY, DEFER_RF_AMBIGUOUS`.

Do not include `rf_effective`, `health=PASS`, `control=ADMITTED`, `can_arm`, `output_allowed`, `approved`, `reason_codes`, `accepted_control_at_us`, `accepted_rf_at_us`, `post_state`, `state_after`, output effort, trace record/ack or next prior snapshot. Enum values are internal evidence labels; none are approved public `E_*` runtime codes.

## 2. RF evidence classification (deterministic priority)

1. Inspect the whole current TASK-003 `rf_events` tuple once, using exact approved `rf_health` statuses and original `event_at_us`; `latest_current_rf_original_at_us` is the **max original timestamp of every current RF record** (regardless of status), or `None` for silence. Validate against TASK-003 boolean RF flags; do not infer source freshness from wall-clock time.
2. If any current **LOST** event, classify `LOST_CURRENT`, even if current HEALTHY/UNKNOWN also exists; this preserves R1 same-tick HEALTHY+LOST priority.
3. Otherwise if both current **HEALTHY and UNKNOWN**, classify `AMBIGUOUS_CURRENT`. **Do not rank** the two statuses; halt positive admission. Both input orders are treated identically.
4. Otherwise current UNKNOWN => `UNKNOWN_CURRENT`; current HEALTHY => `HEALTHY_CURRENT`.
5. On a tick with **no RF event**, use only the separately supplied prior RF status: HEALTHY + matching fresh TASK-004 prior-RF age `<=200000µs` => `HEALTHY_CARRIED`; HEALTHY with age `>200000µs` => `STALE_PRIOR`; LOST => `LOST_CARRIED`; UNKNOWN => `UNKNOWN_CARRIED`; missing prior status => `MISSING`. A past HEALTHY timestamp alone **never** overrides a later committed LOST/UNKNOWN status, even if that older healthy age is still fresh.
6. An observed current HEALTHY can supersede earlier committed LOST/UNKNOWN, **as an evidence observation** only; the future FSM must decide whether to accept and persist it. Its timestamp must not alter the prior snapshot or TASK-004 age outputs.
7. If prior status is HEALTHY, require the synthetic prior RF original timestamp to agree with TASK-004 prior RF accepted timestamp (`eval_at_us - temporal.prior_rf_age_us`), or reject the input; a forged inconsistent prior must not yield `HEALTHY_CARRIED`. For prior LOST/UNKNOWN, an older accepted-healthy timestamp may coexist, and cannot change the LOST/UNKNOWN classification. For prior missing status, prior RF accepted timestamp must be absent. This invariant is **specific to the declared D1 test snapshot pairing**, not a claim that arbitrary caller dataclasses are trusted.

## 3. Control evidence classification

`observed_control_candidate_original_at_us` must equal the TASK-004 `observed_uncontested_valid_control_at_us` exactly, including when blocked by RF or priority. Keep it for audit: **candidate != accepted**.

Apply these ordered diagnostics (they do not replace Design/115's FSM hazard priority):

1. Both `has_invalid_control` and `has_distinct_valid_control_conflict` => `INVALID_AND_CONFLICT`; INVALID only => `INVALID`; distinct VALID conflict only => `CONFLICT`.
2. No uncontested VALID candidate => `ABSENT`. Silence never refreshes accepted frame age.
3. If RESET, catastrophe or pre-state `CONTINGENCY`/`FAULT_LATCHED` exists => `BLOCKED_PRIORITY`; do not promote candidate.
4. If RF evidence is `AMBIGUOUS_CURRENT` => `DEFER_RF_AMBIGUOUS`; unresolved HEALTHY+UNKNOWN cannot qualify.
5. If RF evidence is NOT one of `HEALTHY_CURRENT`, `HEALTHY_CARRIED` => `BLOCKED_RF`.
6. If TASK-005 `blocks_control_qualification=True` from any other factor (including armed-state stale prior frame or prior RF age), => `BLOCKED_PRIORITY`. Even a new in-tick RF HEALTHY/control candidate does not override a stale prior-accepted frame in an armed pre-state at Stage D1. The complete R1 FSM decides remediation.
7. Otherwise => `SINGLE_CANDIDATE`, explicitly **non-authoritative**, subject to separate trusted host/policy/map readiness and full FSM/trace transaction.

No new acceptance of duplicates: equivalent VALID bodies from unique IDs produce one source candidate with latest original timestamp (TASK-003). Distinct VALID groups deny all, no winner selection. Any in-band INVALID denies all, including simultaneous VALID. A syntactically valid control with nonhealthy RF never renews pilot authority.

## 4. Input invariants and fail closed

- Exact Python types, not `isinstance` permissiveness: `bool` is not integer time; reject wrong wrappers/subclasses, mutable structures, fake enums, non-finite/out-of-domain times and mismatched tick/index. `eval_at_us=tick_index*5000`, `0<=tick_index<=12000`.
- `prior_rf.last_committed_eval_at_us` must be `None` only at T0; at later ticks, exact integer grid multiple `5000`, `0<=last_commit<current_tick`; `(status, original_time)` must be jointly present or absent, with `0<=last_rf_original_at_us<=last_commit`. When T0 all prior fields must be `None`.
- For current RF events, enforce immutable mappingproxy shape and approved type/payload, original timestamp in the current tick interval `(T-5000,T]` (T0 only BOOT); no unjustified rescue by later current control.
- Match TASK-003 and TASK-004 RF/INVALID/conflict boolean mirrors; match TASK-003/004/005 tick and TASK-005 pre-state/negative qualification blocker. Caller may not inject `priority.blocks_control_qualification=False` if the approved C1 formula requires true. Earlier modules own normalized group content; do not deeply rescan every source event or rerun the pipeline. Reject contradictory field shapes/flags using TypeError/ValueError before making a result.
- Pure O(number of current RF records), O(1) other work, constant extra memory; frozen/slotted values, no retained state. No filesystem, wallclock, network, random, task-local global state/cache, code execution, policy loader, JCS, M0, VirtualSink, physical driver or trace write.
- This module **does not verify a trusted host allowlist**, prior status authenticity, currently critical power/scheduler condition, or R1 SELF_TEST readiness. It cannot create a real `HealthVerdict.PASS`, nor can it resolve R1 ACK recovery. If approved semantics remain ambiguous or newly contradictory, STOP and escalate to SA; R2/owner approval required for a policy change.

## 5. Release and safety gates

PC_SIM_ONLY; G0-B/G4 physical hardware/flight remain **NO-GO**. All full FSM, replay/trace and authorization oracles remain **NOT RUN**. A future module needs an actual policy/engine allowlist, trace-committed history owner and dedicated full R1 health adjudication; until then, `SINGLE_CANDIDATE` and `HEALTHY_CARRIED` may **not** grant ARM, ACTIVE, held S1 output or ACK recovery.
