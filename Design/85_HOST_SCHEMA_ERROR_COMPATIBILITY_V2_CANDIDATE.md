# BionicButterfly — Phase 2.4 Schema & Error Contract Compatibility

- **ID:** BB-P24-SCHEMA-085 · **Version:** 0.1 · **Status:** PROPOSED; **no implementation and no backward-compatibility claim yet**.
- **Baseline:** `57`, `59`, `67`, `68`, `69`, `78`, `84` at Git main `16d5054…`.

## 1. Explicit contract version plan

Preserve the **scenario input schema v1** (JSON, integer microsecond times, `SIM_ONLY`, fixed `PC_SIM`, typed events, unique event IDs) unless an input field needs changing. Do **not** silently repurpose the legacy error enum `E_EVENT_ID_CONFLICT`, which conflated two different categories. Introduce **proposed result/error contract v2** with names below; this is a **candidate version change** requiring owner approval and tests before consumers rely on it.

| Concept | Layer | Candidate external code | Scope and behavior |
|---|---|---|---|
| duplicate `event_id` across scenario | **preflight** | `E_DUPLICATE_EVENT_ID` | reject whole scenario; core not called; no trace decisions |
| distinct valid SIM_CONTROL_FRAME bodies in same evaluation tick | **runtime batch** | `E_CONTROL_BATCH_CONFLICT` | deny entire control component; state resolution as `84`; no freshness refresh |
| same valid semantic body repeated with unique IDs | runtime batch | `R_DUPLICATE_SEMANTIC_OBSERVATION` | group IDs, apply one logical observation and one edge maximum |
| old `E_EVENT_ID_CONFLICT` | legacy `57` draft | **deprecated, not emitted by v2** | migration report maps old usage only with explicit context; if context missing ⇒ `AMBIGUOUS_LEGACY_ERROR` |

`v1` is a **draft** not an existing production wire contract; nevertheless its meaning must not be changed without a documented version migration. If owner prefers not to version, an alternative is an explicit, independently versioned `error_subcode` field; choose **one** versioning strategy before approval, not both dynamically.

## 2. Validation vs runtime event handling

**Preflight schema errors:** malformed/oversized UTF-8, unknown schema/type/field, missing required time, non-integer/negative/out-of-range `event_at_us`, duplicate globally unique ID, impossible declared context, unauthorized policy, resource quota failure *before execution*. Return `VALIDATION_REJECTED`, typed path/cause, zero core decisions and no active sink.

**Valid fault stimuli:** properly typed `SIM_RF_STATUS(LOST)`, `SIM_CONTROL_FRAME(uart_frame_status=INVALID)`, `SIM_CATASTROPHIC_FAULT`, simulated power problem, and valid `SIM_ACK_FAULT` rejected by state guards. These are scenario events; run must not be rejected merely for containing an intended fault.

**Semantic control equivalence:** compare canonical validated payload content, including arm, flap, steer and map revision, **excluding only** event ID and event timestamp. In one tick, multiple equivalent bodies are deduplicated to one event decision; for freshness adopt the **latest event_at_us** and list all causal IDs sorted. Multiple non-equivalent valid bodies yield conflict; invalid frames cannot be interpreted as valid arm/disarm. Contradictory RF status is treated separately and LOST dominates the tick.

## 3. Typed result and trace separation

```text
ScenarioValidationV1  = Accepted(Scenario, canonical_digest) | Rejected(error, path, ids)
ControlBatchV2        = {eval_at_us, accepted_control?, contradiction:boolean,
                         causal_event_ids_sorted, error_contract_version:2}
SafetyDecisionV2      = {state_before, state_after, owner, arm_gate, fault_latches,
                         reason_codes_sorted, rf_health, frame_age_us?,
                         output_allowed, virtual_effort_micro_left?, virtual_effort_micro_right?}
SimulationRunReportV2 = {run_status, assertion_result, evidence_complete,
                         normative_control_trace_digest?, partial_trace_digest?,
                         schema_version:1, result_contract_version:2,
                         policy_digest, scenario_digest, engine_revision,
                         replay_identity, execution_instance_id? [outside normative trace]}
```

`assertion_result` = `PASS|FAIL|INCONCLUSIVE|NOT_RUN` pertains to a *predeclared test oracle*, not to whether the simulated aircraft is safe or flying. `run_status` = `COMPLETED|VALIDATION_REJECTED|FAILED|FAILED_INCOMPLETE_EVIDENCE`. An expected injected fault may produce `run_status=COMPLETED` with `assertion_result=PASS` if trace shows exactly the expected contingency. No actual code has been run.

## 4. Explicit numeric and provenance rules

- Scenario times and event IDs use validated integer µs and input bounds from `67`; no wall-clock input to domain core.
- `virtual_left/right_micro_effort` integer in `[0,1_000_000]` when output enabled, else **null**; this is not servo pulse µs. Define the quantizer as `floor(clamp(value,0,1)*1_000_000 + 0.5)` for nonnegative finite virtual effort **before** canonical export; audit clipping reason. **This is a design candidate, not code.**
- Input canonicalization candidate RFC 8785/JCS; consider I-JSON restrictions (duplicate JSON keys invalid, Unicode handling, disallowed non-finite) as explicit acceptance tests. `json.dumps(sort_keys=True)` alone is inadequate.
- Output reasons, IDs, arrays have stable declared sorting. The contract must explicitly distinguish absent / null / UNKNOWN, not translate missing health to HEALTHY.
- Deterministic replay identity includes schema/error contract and approved engine revision; tests under differing versions are **comparisons**, not necessarily byte-equal replays.

## 5. Migration and freeze checklist

- [ ] Owner accepts `result_contract_version=2` or selects an alternative; no implicit approval by pushing files.
- [ ] Update `57`, `58`, `59`, `68`, `69`, `71`, `78`, `79` or add explicit supersession references to `84–87`.
- [ ] Define transition/validation semantics for old trace records with `E_EVENT_ID_CONFLICT`; ambiguous ones **must not** be relabeled PASS.
- [ ] Schema validator tests: duplicate ID vs same-tick conflicting frames vs equivalent frames, duplicate JSON property keys, unknown fields, type errors and resources.
- [ ] Zero physical adapters in host build and no runtime config/approval self-elevation.

**Current result:** compatibility candidate documented; **not approved**. No runtime claim.
