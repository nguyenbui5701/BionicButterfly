# G0-A1 — Temporal Guard Facts (TASK-004, Stage B)

- Document ID: BB-P216-164 | Status: SA-released **derived internal contract**, not a new R1 policy.
- Git baseline: `ed106d22c52647090768ef60fb1e4c33384e9227` | PC scope: `PC_SIM_ONLY`.
- Controlling approved requirements: `Design/115` sec. 2/4, `Design/116` sec. 1/2, `Design/117` sec. 2, `Design/141`; merged TASK-003 `NormalizedTickObservations` is the current-tick input.

## 1. Boundary and why this is intentionally not the FSM

TASK-004 **observes** a *single tick* and computes independent ages of two **prior-committed timestamp facts**, and also identifies **uncommitted current-tick candidates**. TASK-004 **does not decide** if RF is effectively HEALTHY, if an input is accepted, whether a guard authorizes ARM/ACTIVE, or whether a recovery is permitted. Any use of its outputs as direct actuator/output permission violates this contract. No internal mutable memory/history is kept; no output adapter or file/trace writer.

### Explicit input

Recommended pure function:

```text
evaluate_temporal_guard_facts(
    observations: NormalizedTickObservations,
    prior: PriorCommittedTimestampFacts
) -> TemporalGuardFacts
```

`PriorCommittedTimestampFacts` is an immutable *read-only input view* populated by a future **separately trusted, trace-committed** state machine (or constructed as a clearly labeled synthetic test fixture):

```text
  last_committed_eval_at_us: int | None
  last_accepted_control_at_us: int | None
  last_uncontested_healthy_rf_at_us: int | None
```

A `None` prior snapshot is represented by all three fields `None` at T0. When `observations.tick_index>0`, the previous committed evaluation time must be an integer on the **5,000µs grid**, `0 <= last_committed_eval_at_us < observations.eval_at_us`; both optional last-observation original timestamps must be exact `int` (not bool), nonnegative and `<= last_committed_eval_at_us`. At tick index 0, all three are `None`. These invariants describe a valid committed *prior state*, not a claim that arbitrary caller objects are trustworthy. Reject malformed types/time relationships as trusted-caller errors (TypeError or ValueError), **not** new `P_*`/`E_*` codes. Direct user JSON must never instantiate an authorized history or bypass a future host allowlist.

### Exact age semantics

For each independent prior timestamp `s` in the snapshot, at evaluation time `T = observations.eval_at_us`, compute:

```text
age_us = T - s                    # exact integer difference, if s exists
within_timeout = (age_us <= 200000)  # equality fresh; 200001 stale
```

If `s` is `None`, `age_us=None`, `within_timeout=False`. Do not use `time.time`, wall clock, monotonic OS clocks, `sleep` or round original event times to 5ms. Positive ages are not inferred from `eval_at_us` alone. Both intervals are **independent**: a fresh RF record never refreshes `last_accepted_control_at_us` and a valid control record never refreshes `last_uncontested_healthy_rf_at_us`. Even if both `within_timeout` flags are true, that alone grants **NO control permission** (current LOST/UNKNOWN, fault or insufficient ARM conditions still inhibit later runtime).

### Uncommitted current-tick candidate facts

Compute, separately from prior ages:

- `observed_uncontested_healthy_rf_at_us`: latest **original** timestamp among current RF HEALTHY observations **only if** RF observations exist and **every** current RF observation is HEALTHY. If there is *any* LOST or UNKNOWN alongside HEALTHY, or no RF event, this candidate is `None`. This is a conservative evidence filter, **not** a newly invented RF effective-state priority (UNKNOWN+HEALTHY remains unaccepted); the future FSM will apply the approved R1 priority rules.
- `observed_uncontested_valid_control_at_us`: `latest_original_at_us` of the single `valid_control_groups[0]` **only if** exactly one VALID group exists and **no injected INVALID** or distinct-VALID conflict exists. Otherwise `None`. This is a *visible control candidate*, not an **accepted** frame. An accompanying RESET, catastrophe, nonhealthy RF or other guard can still block any acceptance; this function must neither suppress the raw observation nor permit authorization.
- `has_rf_lost_observation`, `has_rf_unknown_observation`, `has_invalid_control_observation`, `has_valid_control_conflict`: simply mirror TASK-003 current-tick facts. Crucial: a fresh **prior** RF timestamp and **current** LOST may coexist; callers must not treat the age result as live RF health.
- For candidate fields, retain **original source timestamps**, never `eval_at_us` substitutions. No control candidate may be created from an empty tick or an INVALID frame. No RF candidate may be created from silence.

Do **not** update or return a refreshed committed timestamp snapshot. Do **not** choose a winning control from a conflict, record `accepted_frame_at_us`, evaluate arm-neutrality, health-transition priority, RESET/ACK, or fault state. The future R1 state owner must verify all hazards before it can decide **whether** to accept an observation and persist accepted timestamps.

## 2. Output shape

The immutable result must expose **only** these defined items (names may adapt to Python style but semantic fields and absence of authority are required):

```text
TemporalGuardFacts:
  tick_index: int
  eval_at_us: int
  prior_control_age_us: int | None
  prior_rf_age_us: int | None
  prior_control_within_timeout: bool
  prior_rf_within_timeout: bool
  observed_uncontested_valid_control_at_us: int | None
  observed_uncontested_healthy_rf_at_us: int | None
  has_rf_lost_observation: bool
  has_rf_unknown_observation: bool
  has_invalid_control_observation: bool
  has_valid_control_conflict: bool
```

Output is deeply immutable and deterministic. It must **not** contain state transition, boolean `can_arm`, `rf_effective`, `control_accepted`, approved guard, `output_allowed`, mixer results, trace record, fault reason list, policy digest authorization, refreshed snapshot or any execution authority.

## 3. Critical separation and examples

- Current VALID control @4999µs, no valid committed accepted-control timestamp: prior control age remains `None` / not fresh; observed candidate may be 4999. An ACCEPTED frame still does **not** exist until a future decision is committed.
- Previously healthy RF @5000µs, evaluating at 205000µs: prior RF age 200000 and `prior_rf_within_timeout=True`. If current LOST is also observed, that boolean remains an arithmetic fact **but cannot imply current RF health**. Runtime fault precedence belongs to the future SafetySupervisor.
- Prior accepted control @4999µs, eval 205000µs: age 200001 ⇒ stale. A current VALID candidate does not erase this stale history.
- Current RF HEALTHY at 4999µs and UNKNOWN at 5000µs: **no uncontested healthy RF candidate**, no decision on an R1 `rf_effective` field.
- RESET+VALID control in one tick: current control may remain an *observed candidate fact*, but RESET will later block accepting it per approved R1 priority. Do not add `can_arm` or accepted intent here.

## 4. Implementation/security boundaries

- Accept only exact TASK-003 `NormalizedTickObservations` and declared immutable prior snapshot; do not pull live data or trust user-supplied `approved=true`.
- No mutation of observations, prior or original data. Pure function, `O(number of RF observations)` scan plus O(1) age math; reuse TASK-003 groups/flags. No per-tick history cache, network, physical IO, `mixM0`, `SafetySupervisor` implementation, policy loader, JCS trace or file writes.
- Freeze only this **internal data contract**, derived from 115/116, without modifying approved source/policy bytes. If a Developer finds ambiguous true RF status resolution (particularly UNKNOWN+HEALTHY), do not invent a status precedence; notify SA and keep this task at uncommitted candidate-evidence level.
- G0-A1 simulator engine still not runnable or authorized by this task; G0-B/G4 hardware/flight remain NO-GO.
