# G0-A1 — R1.1 Closed Trace JSONL Record Contract Candidate

- **ID:** BB-P210-TRACE-134 · **Status:** **PENDING OWNER APPROVAL** · **Finding:** P29-F03
- **Machine-readable:** `contracts/G0A1_TRACE_RECORDS_R11_CANDIDATE.schema.json`, `contracts/G0A1_EXTERNAL_REPORT_R11_CANDIDATE.schema.json`.

## 1. Byte stream: preserve approved R1 framing

Keep exactly `JCS(header)+LF`, then one `JCS(tick)+LF` for every evaluated tick, then `JCS(terminal)+LF` for a **complete run**. UTF-8, no BOM, no blank lines, no extra spaces, no partial record. `trace_format_version=1`, `result_contract_version=2` remain the owner-approved R1 values. The R1.1 schema **closes currently unassigned fields** and adds `scenario_wire_schema_version=2` and `mixer_revision=G0A1_M0_R11` to the header. `control_trace_sha256` is **external**, never part of hashed JSONL bytes. `run_id` and wall time are external only.

Header REQUIRED exact keys: `record_type, trace_format_version, result_contract_version, scenario_wire_schema_version, replay_identity, scenario_digest, policy_digest, engine_revision, scheduler_revision, scheduler_step_us, scope, mixer_revision`. Additional properties false. `engine_revision` must change if semantics change; scheduler revision must reflect the 5ms schedule.

Tick REQUIRED exact keys: `record_type, tick_index, eval_at_us, state_before, state_after, rf_effective, accepted_frame_age_us, causal_event_ids, reason_codes, output_allowed, requested_flap_micro, requested_steer_micro, input_mode, mixer_clip_tags, left_micro_effort, right_micro_effort`. Each field is always present; no omitted-vs-null ambiguity. `accepted_frame_age_us=null` if no previously accepted frame (or no age is meaningful), otherwise nonnegative **original** age. If `output_allowed=false`, request and output effort fields **all null**, `input_mode=NONE`, clips empty. If true, state_after ACTIVE, pair ints and request ints, mode FRESH or S1_HELD. No scenario may supply trace objects as input.

Terminal REQUIRED exact keys: `record_type, run_status, evaluated_tick_count, fault_codes, evidence_complete`. `run_status=COMPLETED|FAILED`, complete terminal has `evidence_complete=true`. No self-hash, wall-time, invocation UUID, or PASS claim in trace.

`external_report` fields and all complete/incomplete digest constraints are separately closed in its schema. A report may say `assertion_result=NOT_RUN` alongside an authored design trace; it may say PASS **only after executing a real implementation oracle**. `VALIDATION_REJECTED` has zero ticks and no complete trace; `FAILED_INCOMPLETE_EVIDENCE` has null complete hash and possible partial digest.

## 2. Determinism and record-order checks outside JSON Schema

- Exactly one header first and one terminal last, no records after terminal, no extra/omitted ticks. Tick index is `0..N-1`; `eval_at_us=index*5000` strictly; initial pre-state BOOT, pre-state at tick k equals prior committed post-state; `evaluated_tick_count=N`. A normal run with `duration_us=D` has `N = D/5000+1`; a runtime failure may terminate earlier with FAILED and a complete terminal.
- `causal_event_ids` are unique strings ordered lexicographically by **unsigned UTF-8 encoded bytes**, not locale. No Unicode normalization; compare exact JSON-decoded scalar string. Include all events observed for this tick (including rejected in-band diagnostics); no round-off from original event timestamps.
- `reason_codes`, `fault_codes` and `mixer_clip_tags` use ASCII enum sets in the machine schema; canonical ascending bytewise ordering; duplicates forbidden. No implicit reason insertion by UI. New reason values require version review.
- `replay_identity` retains the exact R1 hash domain and key set from `118`: domain `BIONICBUTTERFLY_G0A1_REPLAY_V1`, SHA scenario canonical object, trusted policy SHA, engine & scheduler revisions, result version 2 and trace version 1. R1.1 scenario v2 changes the input digest naturally, and the engine revision must identify M0 so no unmarked semantic collision occurs.
- All types/bytes checked BEFORE publish; emit virtual post-state/output only after one full append acceptance. If quota/serialization/append fails, no output of that tick is shown; `FAILED_INCOMPLETE_EVIDENCE`, complete digest null; do not pretend the partial trace has a terminal.

## 3. Canonical reference and limitations

`fixtures/P210_MINIMAL_DESIGN_TRACE.jsonl` and `fixtures/P210_MINIMAL_DESIGN_EXTERNAL_REPORT.json` are **hand-authored design reference vectors**, not output of an executable simulator. Their SHA-256 and replay identity are calculated over ASCII-only strings, integer JSON values and null/bool, for which the supplied serializer bytes are JCS-equivalent. A future implementation MUST use an independently tested RFC 8785 implementation for general Unicode and floating values; Python `json.dumps(sort_keys=True)` is **not** declared a general RFC 8785 serializer.

JSON Schema validates a record's keys/types but does **not** establish whole-stream order, hash correctness, state continuity, enum semantic precedence or buffer commit ordering. G1 acceptance needs a validator/harness that independently compares all of these. `fixtures/P210_MINIMAL_VECTOR_ATTESTATION.json` states the expected design digest and marks `runtime_executed=false`.

## 4. Decision needing owner signoff

The exact trace record field set, candidate reason-code vocabulary, integer request fields and header `scenario_wire_schema_version`/`mixer_revision` are new observable interface choices. If the owner rejects them, rewrite schema and reference hashes; **do not** publish an unapproved stream under R1 authority.
