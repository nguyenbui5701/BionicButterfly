> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `116 (exact policy)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `6e292c0a0736e47ea718d437a39bed427514f16e`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — G0-A1 SIM Policy, Parameter Boundary and Approval Proposal

- **ID:** BB-P26-POL-102 | **Rev:** 0.1 | **Status:** SA-recommended proposal; OWNER APPROVAL PENDING.
- **References:** `67`, `70`, `84`, `85`, `87`, `93`, `100–101`.

## 1. Numeric policy to review — values are simulation-only

The table below matches the *Phase 2.4 reviewed candidate* `SIM_POLICY_CANDIDATE_22A` in `Design/67...`, and retains its values. No hardware/aircraft timeout is inferred.

| Policy key | Candidate | Constraint / purpose |
|---|---:|---|
| `scheduler_step_us` | 5,000 µs | fixed for one G0-A1 engine revision; different step is NOT equivalent replay |
| `arm_low_observation_us` | 20,000 µs | 2 distinct accepted LOW frames separated >= this value |
| `arm_high_qualification_us` | 100,000 µs | distinct confirming HIGH after >= boundary |
| `frame_timeout_us` | 200,000 µs | inclusive boundary; > means stale |
| `rf_status_timeout_us` | 200,000 µs | independent RF health; UNKNOWN if stale HEALTHY |
| `neutral_flap_max` | 0.02 | inclusive neutral for ARM |
| `neutral_steer_abs_max` | 0.05 | inclusive neutral for ARM |
| `active_flap_threshold` | 0.05 | strict `>` required to enter ACTIVE |
| `max_scenario_duration_us` | 60,000,000 | scenario bound |
| `max_events` | 20,000 | scenario bound |
| `max_input_bytes` | 2,097,152 | UTF-8 bytes |
| `max_trace_bytes` | 16,777,216 | host trace bound |
| `max_json_nesting` | 16 | reject deeper |
| `max_event_id_utf8_bytes` | 64 | no control chars; nonempty |
| `max_generic_string_bytes` | 256 | default field bound; stricter for IDs |
| `context` / `owner` | `PC_SIM` / `SIMULATOR` | no physical hardware binding |
| `randomness_policy` | no stochastic core | deterministic by construction |

The virtual output uses integer `micro_effort` in `[0,1000000]` and `null` when not authorized; note the name **micro-effort is not a servo pulse width**. `0` as an authorized command differs from `null` as inhibition.

## 2. Remove ambiguous 'self-approval' semantics

The original `67` example contains `approved_for_host_execution: false` and `owner_approval_ref: null`. Treat this example as a **NON-EXECUTABLE ILLUSTRATION**; do **not** flip a field to true and treat that as authorization. The trusted policy authorization resides in an independently managed immutable host approval record, external to untrusted scenario JSON:

```text
TrustedSimApprovalRecord {
  decision_id, owner_acceptance_reference, reviewed_design_git_sha,
  policy_canonical_sha256, policy_format_rev, selected_contract_rev,
  allowed_scope: PC_SIM_ONLY, allowed_engine_contract_rev,
  effective_status: APPROVED, signed_or_immutable_host_provenance
}
```

A SHA-256 digest is a content fingerprint, not a signature or authorization by itself. The host may trust a prebuilt allowlist only if that allowlist itself is managed outside the scenario and bound to an explicit owner decision. A scenario cannot populate it, and changing policy bytes causes preflight rejection.

## 3. Canonicalization and split identity

A policy digest is computed over the approved **policy-specific typed fields only** (an explicitly versioned canonical record), not over a document with mutable approval dates, pasted Markdown or volatile reviewer prose. Schema and exact enum set must be approved and pinned before computing the *final* trusted digest. JCS RFC 8785 candidate with I-JSON compatible input: reject duplicate property names, non-finite values, unsupported Unicode representation. Do not invent a digest for unsigned policy by hashing a truncated table.

- `scenario_digest = SHA256(JCS(validated_scenario_object))`;
- `policy_digest = SHA256(JCS(policy_record with pinned schema))`;
- `replay_identity` binds scenario+policy+engine+event-scheduler+result-contract revision;
- `execution_instance_id` and wall-time are nonnormative, never part of deterministic trace bytes.

## 4. Approval conditions — owner is an explicit actor

`G0-A1` design approval requires owner acceptance of: scope; exact numerical candidate or amended values; state semantics `100–101`; S1 no-event rule or a selected alternative; result/error contract version; recoverable-cause allowlist; trace digest bytes; and all deferred tests. Record reviewed Git SHA and policy canonical digest **after** policy format is resolved. Publishing docs to GitHub is **not** an approval signature.

**Current status:** `SIM_POLICY_CANDIDATE_22A` is **UNAPPROVED**. No executable policy allowlist or code has been provisioned by SA. No physical failsafe/RC threshold selected.
