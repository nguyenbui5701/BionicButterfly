> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `117 (API typed contract), 115 (atomic tick)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `197b3af002976695b5546d2e40e1f1335d873729`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — G0-A1 Host-only API Normative Contract Candidate

- **ID:** BB-P23-API-078 | **Rev:** 0.1 | **Date:** 2026-11-12 | **Status:** DRAFT / not production code / not approved
- **Hierarchy:** this file proposes narrow refinements to `57`, `58`, `61`, `67–70` and **cannot retroactively rewrite the owner's Git tree**.

## 1. Interface groups (architecture only)

| Interface | Input | Output | Invariant |
|---|---|---|---|
| `validateScenario` | UTF-8 bytes; pinned schema v1 | `ValidationResult` with typed issues OR immutable scenario | no hardware access, no state change |
| `loadApprovedSimPolicy` | independently trusted approved digest + policy bytes | immutable `SimPolicySnapshot` or reject | scenario cannot approve a policy |
| `schedule` | typed events, canonical fixed tick, monotonic virtual clock | stable eligible batch | no event after current evaluation exposed |
| `normalizeBatch` | entire eligible batch | classified events + semantic conflicts + reasons | no intermediate output or mutable control side effects |
| `evaluate` | immutable pre-snapshot, normalized batch, immutable policy | one `SafetyDecision` + new snapshot | deterministic, no hidden clock/state source |
| `mixAndBound` | approved intent from safety decision | bounded virtual L/R, clip reasons | no physical pulse/angle semantics |
| `appendTrace` | one post-state decision | canonical control trace item | append failure forces non-PASS run result |
| `completeRun` | canonical control trace & failure status | terminal report + digest | status/result logic independent of display/UI |

Each interface has a **total outcome**: typed success or typed refusal/failure, not an uncaught exception that could leave a virtual output enabled. The future implementation must not accept arbitrary callback-provided `SafetyDecision` or `ActuatorOutput` bypassing `evaluate`.

## 2. Candidate transaction contract

At evaluation tick `T`:

1. Fetch eligible events by true original timestamps, retain causal event IDs, group without output side effects.
2. Fail scenario before run for parse errors/duplicate IDs; runtime field `uart_frame_status=INVALID` may be a deliberately valid test event and does **not** refresh.
3. Detect **semantic contradiction** among valid control frames in this tick before any arm/disarm classification; semantic duplicates with different unique IDs count once.
4. Observe RESET, catastrophic fault, link/power safety hazards, disarm, ACK, ARM candidate, demand under a **single explicit priority contract**. **Open proposal:** catastrophic fault cannot be cleared by simultaneous RESET. Invalid control batch cannot produce a trusted DISARM or ARM transition; if armed, it causes virtual CONTINGENCY/inhibit.
5. Apply state transition using pre-state and qualified event summaries, then compute at most one virtual actuator decision from post-state. No output may be emitted from transient state transitions.
6. Append one canonical decision per evaluation tick, including exact sorted reasons; if append fails, mark run `FAILED_INCOMPLETE_EVIDENCE`, inhibit sink, no PASS.
7. If run is complete, write terminal summary and replay digest; if not, disclose partial result. `run_id` definition must exclude volatile identifiers from deterministic replay digest.

**Open design question:** `RESET` with catastrophic fault should latch catastrophic fault at this same tick; this proposal is listed as **P23-F02**, not yet approved. Do not implement it as a hidden semantic change.

## 3. Candidate typed error distinctions

- `E_DUPLICATE_EVENT_ID`: invalid whole scenario at validation; no core run.
- `E_CONTROL_BATCH_CONFLICT`: two distinct control bodies in one eval tick; reject control component, preserve fault trace.
- `E_EVENT_ID_CONFLICT`: **legacy** early-draft name; resolution requires schema versioning/ADR; no alias silently selected.
- `E_RF_NOT_HEALTHY`, `E_FRAME_STALE`, `E_ARM_PRECONDITION`, `E_ARM_EDGE_ABSENT`, `E_CONFIG_LOCKED`, `E_CONTEXT_DENIED`, `E_INPUT_OVERFLOW`, `E_NUMERIC_INVALID`, `E_SIM_FAULT`: reuse existing semantics, but only when backed by exact error registry.

If enum changes cannot be approved without breaking v1, retain a single old error code but add a separate, explicit subcode in a **new versioned contract**. Developers must not guess migration behavior.

## 4. Typed information, not magic defaults

```text
RunRequestV1: { scenario_bytes, approved_policy_ref }  // no physical context field
InputValidation: { status, code, path, causal_event_ids } 
SimPolicy: { immutable approved policy values, digest, external approval_ref, schema_rev }
Batch: { eval_at_us, event_ids_sorted, control_conflict, fault_flags, accepted_control? }
Decision: { state_before, state_after, owner, rf_health, frame_age_us?, output_allowed,
            reason_codes_sorted, left_micro_effort?, right_micro_effort?, policy_digest }
Report: { run_status, test_assertion_status?, normative_control_trace_digest?,
          scenario_digest, policy_digest, engine_revision, partial_evidence, claim_scope }
```

`physical_airborne_state=UNKNOWN` always; absence of physical sensors is a declared model limit, not a missing field to fill with zero.

## 5. Policy approval / trust boundary

`approved_for_host_execution` in local candidate JSON is **not sufficient**. The host application should only run with an immutable policy whose SHA-256 digest appears in an independently provisioned owner-approved allowlist for that exact design revision (or equivalent signed immutable build manifest). User-generated scenarios cannot update this allowlist, switch the sink, load plugins, or toggle source privileges. Exact trust provisioning is a future G0-A1 implementation design issue and must be tested with a tampered-policy vector.

**No physical I/O:** even test fixtures claiming `RC_PRIMARY` are represented as injected simulation data and cannot open serial devices, PWM output or camera/IMU hardware.

## 6. Output/tracing contract

Use integer `left/right_micro_effort ∈ [0,1000000]`, null when inhibited. Input floating `flap_demand`/`steering_demand` remain finite, range checked, canonicalized as declared in `69`; no hidden float->servo PWM conversion. A replay ID built from canonical scenario/policy, engine and schedule identity is deterministic. Any wall-time, operator metadata, local file path or UI preferences are stored **outside normative trace bytes**.

**Version control:** this is a proposed new contract revision and must be reconciled against old 57/58/61/68/69 before approval. No compiled runtime or automated acceptance test exists yet.
