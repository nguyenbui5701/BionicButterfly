# G0-A1 — R1.1 Candidate Closed Scenario Wire v2

- **ID:** BB-P210-WIRE-132 · **Candidate revision:** R1.1 · **Owner approval:** PENDING
- **Machine-readable artifact:** `contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` (JSON Schema Draft 2020-12).
- **Finding addressed:** P29-F01. **No changes** to R1 policy numbers, safety priorities or physical scope.

## 1. Why version 2 is mandatory

The examples in `57` and `P26_*` fully show only `BOOT`, `SIM_RF_STATUS` and `SIM_CONTROL_FRAME`. R1 FSM also discusses RESET, `SIM_ACK_FAULT` and `SIM_CATASTROPHIC_FAULT`, but does not freeze all wire payloads. Adding these directly to input v1 would silently extend the previously approved syntax. **Candidate v2 explicitly requests approval of a new wire version**, retaining v1 input as history. `G0A1_SCENARIO_WIRE_V1_HISTORICAL_SUBSET.schema.json` checks only the unambiguous old three-event illustrated subset; **it is not** an assertion that all legitimate old R1 fixtures are covered or approved for runtime.

## 2. Exact object grammar

Required top-level keys: `schema_version=2`, `scenario_id`, `context=PC_SIM`, `provenance=SIM_ONLY`, `config_id=sim-only-c0-v1`, `clock={start_us:0,step_us:5000}`, **new required `duration_us`** and `events`. Unknown properties at every level are forbidden. `duration_us` is a multiple of 5,000 µs in `[5000,60000000]`; exactly one `BOOT` at timestamp 0, **first** in the array; all other events must have timestamps in `[0,duration_us]` and be nondecreasing in array order. Additional at T0 may be present but cannot change boot's one-tick precedence; to minimize ambiguity, v2 SA proposal disallows non-BOOT events at T0. There are `duration_us/5000+1` scheduled ticks on an ordinary complete run (including T0). `scenario_id` max 256 UTF-8 bytes; `event_id` nonempty max 64 UTF-8 bytes, globally unique; opaque IDs are **not normalized** by Unicode.

All events use exactly `{event_id:string,event_at_us:int,type:string,payload:object}`. The *complete proposed enum* is:

| Wire `type` | Exact payload | Interpretation | R1 claim |
|---|---|---|---|
| `BOOT` | `{}` | T0 only, one per scenario | existing |
| `SIM_RF_STATUS` | `{rf_health: HEALTHY\|LOST\|UNKNOWN, rf_provenance: INJECTED_SIM}` | independent simulated RF observation | existing |
| `SIM_CONTROL_FRAME` | `{uart_frame_status: VALID, flap_demand, steering_demand, arm_switch: bool, map_revision: sim-map-v1}` | complete valid control observation | existing |
| `SIM_CONTROL_FRAME` | `{uart_frame_status: INVALID}` | deliberately injected in-band invalid UART; a **valid scenario event** | existing |
| `SIM_RESET` | `{}` | software RESET stimulus; safety rank still per `115` | **new wire choice** |
| `SIM_ACK_FAULT` | `{}` | ACK; cannot clear without prior committed LOW + recovered conditions | previously named, now given closed payload |
| `SIM_CATASTROPHIC_FAULT` | `{}` | latch catastrophe; reason `E_SIM_FAULT` + `R_CATASTROPHIC_LATCH` | previously named, now given closed payload |

`uart_frame_status=NONE` is a **logical absence of frame**, not a v2 wire event. Unknown types such as `SIM_VOLTAGE_WARNING_RECOVERED` are rejected preflight; `VOLTAGE_WARNING_RECOVERABLE` stays a reason enum, so related recovery tests remain **DEFERRED** until a later owner-reviewed schema. Physical context, BLE/Wi-Fi, PWM and RC receiver data are not permitted.

## 3. Exact parser acceptance procedure (JSON Schema alone is insufficient)

1. Enforce approved `max_input_bytes=2097152` on raw UTF-8 before parsing. Reject BOM/invalid UTF-8; prohibit duplicate object keys at **every nesting level** using a token-preserving strict parser; prohibit unpaired Unicode surrogates, NaN, ±Infinity and excessive JSON depth >16.
2. Parse numeric tokens as exact base-10 values (not lossy binary64 first). JSON booleans never satisfy integer fields. Validate JSON Schema Draft 2020-12 closed union; reject unknown property/type. Limit all free-form string values to approved max 256 UTF-8 bytes, event IDs to 64 bytes. Reject C0/C1 control chars in identifier tokens.
3. Validate semantic cross-field constraints the schema cannot express: `BOOT` single first T0 event; no other T0 event; nondecreasing `event_at_us`; event time <= duration; global exact `event_id` uniqueness; map revision bound to approved `sim-map-v1`; all numeric pilot values finite with at most 6 base-10 fractional decimal places (equivalently `n*1,000,000` exactly integral). Zero duration not supported in this candidate.
4. Validate `config_id`, policy digest, engine/scheduler revisions against independent host-side approval (per `116`); never accept scenario `approved`, custom sink/owner or role key. Construct virtual runner only after complete preflight success.
5. All malformed scenarios ⇒ `VALIDATION_REJECTED`, zero core ticks/no canonical full trace. Duplicate ID ⇒ `E_DUPLICATE_EVENT_ID`. For other parse failures use the typed error registry from `117` plus deterministic validation issue path; the missing *exact* preflight parse code mapping is a minor follow-on decision for G1 runtime errors, not permission to silently accept input.

## 4. Important separations

- Different **valid** payloads within the same evaluation tick remain legal scenario input. They cause a runtime `E_CONTROL_BATCH_CONFLICT`, **not** a preflight parse rejection. Same-tick RF HEALTHY + LOST resolves LOST by R1 priority.
- An `INVALID` UART observation is a valid typed event; it breaks LOW and denies control authority, never refreshes accepted-frame timestamp.
- `event_at_us` is not rounded to `eval_at_us`; original timestamps determine freshness and 20ms/100ms arm windows.
- Adding `duration_us`, narrowing pilot precision to 6 decimals, fixed map revision and wire event vocabulary is an observable **new candidate policy**; approval must explicitly reference this document and the schema SHA before treating R1.1 as normative.

## 5. Migration examples

- `fixtures/P26_ARM_NOMINAL_CANDIDATE.json` → v2: set `schema_version=2`, add `duration_us` (>= last event, multiple of 5000), keep existing BOOT/RF/valid controls; see `fixtures/P210_NOMINAL_M0_WIRE_V2.json`.
- `SIM_ACK_FAULT` and `SIM_RESET` should not be auto-invented when loading older JSON. A v1 script lacking a clear mapping to v2 must be rejected and migrated explicitly.
- No automatic schema-version coercion and no `approved=true` migration.
