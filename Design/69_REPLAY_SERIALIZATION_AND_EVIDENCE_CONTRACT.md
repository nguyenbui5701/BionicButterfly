> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `118 (JCS JSONL, external digest)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `47de847c7742d90c3b3d5272058115885092e996`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — Deterministic Replay, Canonical Serialization & Evidence

> **Phase 2.4 review note (2026-11-12):** See the candidate corrective addendum at the end and `84–90` before treating older priority/approval text as normative. **Pending owner approval; not code or flight authorization.**

- **ID:** BB-G0A-TRACE-069 | **Revision:** 0.2 | **Date:** 2026-11-12
- **Status:** SA PROPOSED; no replay engine or runtime test executed. **PC_SIM ONLY.**
- **Parent:** `57` schema, `59` virtual time, `63` test matrix; refined by `66–68`, tested by design in `71`.

## 1. What must be stable

| Layer | Normative equality within **same engine/build** | Across different engines/builds |
|---|---|---|
| Parse/validation result | exact typed errors and source locations | exact error classification; display text may vary |
| State, owner, reason, event ID, decision timestamp | exact equality | exact equality with same policy/schema |
| Input/config identity | canonical UTF-8 JSON bytes, `SHA-256` | same canonicalization implementation/profile |
| Virtual normalized left/right effort | exact **integer micro-effort** in exported trace if same implementation | mathematical outputs within approved `1e-6` normalized absolute tolerance **only when comparable**, no claim of identical bytes |
| Waveform phase/floating intermediate | not serialized as unrestricted machine floats; log quantized controlled observable | tolerance/phase normalization declared per contract; no unqualified byte identity |
| Binary/trace container | canonical JSON Lines (JSONL) using one canonical object per line | physical file byte hash may differ if implementation/revision differs |
| Test outcome | exact typed PASS/FAIL/INCONCLUSIVE/NOT_RUN | no blanket cross-platform PASS without controlled environment |

This resolves the apparent inconsistency between `PC-A14` byte-identical normalized event trace and `PC-A15` numeric tolerance: **PC-A14 tests same engine, same config, same schedule**, while **PC-A15 is an explicit cross-schedule research test (DEFERRED for G0-A1)**. Do not require different tick partitions to be byte-identical when the evaluation times themselves differ.

## 2. Input and configuration canonicalization

- Interchange is strict UTF-8 **JSON** only, object fields exactly as defined in versioned schemas. Reject duplicate JSON keys, unknown fields, excessive nesting, noninteger timestamps, negative times, nonfinite numeric values and out-of-range normalized values.
- **Candidate canonicalization**: RFC 8785 / JSON Canonicalization Scheme (JCS), with safe integer limits, Unicode normalization policy **none** (preserve literal Unicode values), stable object-key sorting and ECMAScript-compatible finite JSON number formatting. This must be implemented with a proven compatible library or tested reference vectors; a generic `sort_keys` call is **not** accepted as JCS proof.
- `schema_version` must be 1; unknown versions are hard failures. `event_id` unique and nonempty; only known enum fields accepted. Timestamps are integers well below the 2^53 precision boundary by the 60s cap.
- For future safety-critical fixed-point fields, review whether to replace floating control literals with integer millionths in `ScenarioV2`. Do not silently reinterpret v1 field names or units.
- The normalized `ScenarioV1` and `SimPolicyV1` produce separate SHA-256 digests. A record of hashes must include the canonicalization contract revision and source file SHA so replay can be audited independently.

## 3. Proposed output representation

- `TraceRecordV1` is a JSON object on one LF-terminated line. Each line is separately JCS canonicalized. The trace file includes header, one or more event/decision records and a **terminal summary** (or an explicitly labeled truncated partial trace on failure).
- Required header: `run_id`, `scope=PC_SIM_ONLY`, `scenario_digest`, `policy_digest`, `schema_revision`, `contract_revision`, `engine_revision`, `tick_step_us`, `test_mode`, `virtual_output_units=micro_effort`.
- Required decision: `eval_at_us`, `state_before`, `state_after`, `owner`, `serial_frame_age_us|null`, `rf_health`, `rf_status_age_us|null`, `arm_edge_status`, sorted `reason_codes`, sorted `causal_event_ids`, `output_allowed`, `left_micro_effort|null`, `right_micro_effort|null`, `profile_revision`, `fault_latched`.
- **Micro-effort** is an integer from `0` to `1,000,000` corresponding to requested normalized virtual effort [0,1]. The mapping uses `round-half-even` at 1e-6 resolution after validating finite numerical output and envelope bounds; do not serialize as servo degrees or PWM microseconds.
- When `output_allowed=false`, record `left_micro_effort=null`, `right_micro_effort=null` rather than pretending the real wing is at physical zero. No `measured_lift`, `measured_wing_angle`, actual location or `airborne=true` values are populated. The provenance `SIM_ONLY` is explicit in every report.
- Optional visualization phase may be logged in a separate `VISUAL_ONLY` record with declared float tolerance; it is **not** an acceptance datum for real physics.
- Names and values from future physical log adapters are prohibited in host-only composition. No hardware serial port, radio binding, RF transmitter or ESP32 PWM can be selected by JSON or runtime flag.

## 4. Hash, run ID and failure outcomes

Recommended digest input is a **length-prefixed** ordered bundle to avoid ambiguous concatenation of strings: `(schema_version, canonical_scenario_bytes, canonical_policy_bytes, engine_revision, scheduler_contract_revision)`; encode each with an explicit byte length. `run_id` may be derived from this digest plus an optional explicit test case identifier; wall-clock date must not affect replay identity.

| Event | Required report and consequence |
|---|---|
| Invalid input before run | `VALIDATION_REJECTED`, zero decisions, no enabled output; typed error and no fake core trace |
| Fault during run | `FAILED` or `EXPECTED_FAULT` determined by predeclared test oracle; still record fault and reason |
| Trace write fails / 16MiB quota reached | `FAILED_INCOMPLETE_EVIDENCE`, sink logically inhibited and partial trace flagged; never PASS |
| Same scenario and policy replayed twice in same engine | exact categorical state/reason/owner and integer micro-effort trace; same canonical trace SHA if same engine revision |
| Different platform/engine version | compare state/reason exactly, quantized outputs per declared absolute tolerance, and explicitly note differences; don't claim same hash |

An intentional test that expects a simulated fault is allowed to PASS its **test assertion**, but **SimulationRunReport** still describes what happened (`CONTINGENCY`, faults etc.); don't conflate test status with aircraft safety.

## 5. Example record (illustrative, not executed)

```json
{"eval_at_us":145000,"scope":"PC_SIM_ONLY","state_before":"ARMED_IDLE","state_after":"ACTUATION_ACTIVE","owner":"SIMULATOR","rf_health":"HEALTHY","arm_edge_status":"QUALIFIED","output_allowed":true,"left_micro_effort":200000,"right_micro_effort":200000,"reason_codes":[],"causal_event_ids":["e100"],"profile_revision":"sim-only-c0-v1","fault_latched":false}
```

A complete implementation must also include the remaining fields specified above, so this line is an **explanatory subset**, not a conformant real trace. Its `200000` virtual efforts are not physical servo PWM, actual flap angle or aerodynamic thrust.

## 6. External standard reference and limitations

- IETF RFC 8785 JSON Canonicalization Scheme: https://www.rfc-editor.org/rfc/rfc8785 .
- SHA-256 digest convention: NIST FIPS 180-4. This proposal does not claim cryptographic authentication of a user or security proof; hashes identify exact bytes for audit only.

**Owner review:** D-062 and D-064 must be explicitly decided before design freeze, with canonicalization test vectors added to the approved test acceptance. No real code or validation tests exist yet.

## Phase 2.4 canonical replay proposal (rev 0.2)

`87_TRUST_REPLAY_AND_EVIDENCE_FREEZE_CANDIDATE.md` refines earlier replay terminology: separate stable `replay_identity` from volatile `execution_instance_id` (excluded from normative bytes); canonical control JSONL includes JCS objects + LF and stable integer micro-effort, but not visual-only metadata. `control_trace_sha256` exists only for a **complete** normative trace; a partial trace is explicitly labeled and can never claim PASS. See `85` result-contract version and `86` P24-T18..22. Unapproved candidate.
