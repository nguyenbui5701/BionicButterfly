# G0-A1 — R1.1 Input & Parser Freeze Review

- **Doc:** BB-P211-IN-142 · **Decision:** R11-D01/D02/D05/D06 **approved** by owner, Git bytes verified.

## 1. Wire v2 acceptance contract

Top-level required exactly: `schema_version=2`, `scenario_id`, `context=PC_SIM`, `provenance=SIM_ONLY`, `config_id=sim-only-c0-v1`, `clock={start_us:0,step_us:5000}`, `duration_us`, `events`. Additional properties forbidden.

**Only six tags:** `BOOT`, `SIM_RF_STATUS`, `SIM_CONTROL_FRAME`, `SIM_RESET`, `SIM_ACK_FAULT`, `SIM_CATASTROPHIC_FAULT`. `SIM_CONTROL_FRAME` has two closed branches: `VALID` with flap/steer/arm_switch/map_revision, or `INVALID` with no other fields. `uart_frame_status=NONE` means absence, not wire input. Reset/ACK/catastrophe payloads are empty objects. Independent RF observation uses `rf_provenance=INJECTED_SIM`.

`duration_us∈[5000,60000000]` and divisible by 5000. Exactly one BOOT at T0 and first in array; no other event at T0. Event IDs unique across entire scenario; nondecreasing original integer `event_at_us≤duration_us`. Payload time is not rounded when checking LOW/HIGH/frame age. Pilot input represents exact decimal millionths; >6 decimal places rejected, exponent notation acceptable only when exact value is integral in 1e-6 units.

## 2. Parser-level rules outside schema

- Validate raw UTF-8 length (`max_input_bytes` 2MiB) BEFORE parsing. Deny BOM, invalid UTF-8, duplicate object keys at *any* depth, unpaired surrogates, excessive depth >16 and nonfinite numeric extensions.
- JSON number tokens must be read as exact decimal before converting to fixed-point integer. Boolean `true` cannot satisfy an integer field.
- Enforce identifier UTF-8 byte maxima: scenario_id ≤256, event_id ≤64; JSON Schema `maxLength` alone counts Unicode code points, not UTF-8 bytes.
- Unknown keys, version, context, sink/approval fields or unsupported volt-warning events lead to **VALIDATION_REJECTED before core ticks**. A syntactically valid in-band `INVALID` UART event remains a valid *scenario*, then causes a runtime fault per `115/117`.
- Strict array-level ordering and ID uniqueness cannot be fully expressed by Draft2020-12 JSON Schema; an independent semantic validation pass is mandatory.

## 3. Exact preflight outcome and residual detail

Common mandatory result is `VALIDATION_REJECTED`, `evaluated_tick_count=0`, no complete trace, no output; `E_DUPLICATE_EVENT_ID` is mandatory for repeated global IDs. The external report schema does not currently specify a **field for detailed validation subcode or JSON-path** for every other parser rejection. Do not add fields to frozen report schema or choose an unspecified new `E_*` enum silently. **P211-GAP-01**: SA must close the optional diagnostic envelope/issue-code taxonomy **before giving a full parser-report task**. Until then the frozen API still defines the top-level rejection response; do not misstate that all diagnostic detail is frozen.

## 4. Regression vectors and deliberate deferrals

| Scenario | Result at design/static level | Runtime test |
|---|---|---|
| `P210_MINIMAL_WIRE_V2.json` | schema-valid, BOOT-only two ticks reference | NOT RUN |
| `P210_NOMINAL_M0_WIRE_V2.json` | schema-valid, intended 145ms active oracle | NOT RUN |
| `P210_RESET_CATA_WIRE_V2.json` | schema-valid fault stimulus, catastrophe higher than RESET by R1 | NOT RUN |
| `P210_DUPLICATE_KEYS_INVALID.json` | strict parser must refuse before state creation | NOT RUN |
| v1 historical samples | not automatically promoted to approved v2 | DEFERRED |
| `SIM_VOLTAGE_WARNING_RECOVERED` | unsupported wire; not synthesized | DEFERRED |

**Conformance distinction:** `jsonschema.validate()` of examples and a hand-written check for event order are useful *static audit*, but not proof the future runtime implements these safeguards.
