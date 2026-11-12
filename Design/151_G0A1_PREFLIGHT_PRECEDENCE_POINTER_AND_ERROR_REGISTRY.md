# G0-A1 — Parser Preflight Stages, Error Precedence & Path Contract

- **ID:** BB-P212-ERR-151 · **Status:** proposed normative clarification for future isolated parser module; no runtime tested.

## 1. Deterministic rejection ladder

| Stage | Order | Action | Primary issue |
|---|---|---|---|
| RAW | 1 | Check input bytes <=2,097,152 before decoding | `P_INPUT_TOO_LARGE` |
| RAW | 2 | Strict UTF-8 decode; reject overlong encodings/invalid sequences | `P_UTF8_INVALID` |
| RAW | 3 | Deny UTF-8 BOM (not stripped) | `P_UTF8_BOM` |
| LEX | 4 | Tokenize strict JSON; require duplicate-member detection at every depth; reject unpaired surrogate, nonfinite extensions, >16 nesting | One `P_JSON_*` from first offending raw-byte token |
| SCHEMA | 5 | Validate against *unchanged* R1.1 wire-v2 schema; reject missing, extras, type, enum, const, range, unknown tag and >20,000 events | One `P_SCHEMA_*` or specialized tag/context/version/count code |
| SEMANTIC | 6 | Global duplicate event IDs (before timestamp-order checks) | `P_EVENT_ID_DUPLICATE` → frozen base `E_DUPLICATE_EVENT_ID` |
| SEMANTIC | 7 | BOOT exactly first and T0; no other T0 events | `P_BOOT_SEQUENCE` |
| SEMANTIC | 8 | Nondecreasing original `event_at_us` | `P_EVENT_TIMESTAMP_ORDER` |
| SEMANTIC | 9 | Each original time within `duration_us` | `P_EVENT_TIMESTAMP_RANGE` |
| SEMANTIC | 10 | UTF-8 identifier byte lengths, control chars, exact Decimal micro scaling | First failing category in registry order |

### JSON Schema error reporting

JSON Schema validators can differ in the *order and shape* of `oneOf`/`const` diagnostic messages. Do **not** expose backend error order as the public issue. Instead classify a failed schema by the exact failing field and stable rules:

1. Verify the closed top-level object shape; specialized `schema_version`, `context`, `provenance`, `config_id`, `duration_us` and `events` count codes precede generic enum/range.
2. For each event, inspect its `type` before validating its payload branch; unsupported type ⇒ `P_EVENT_TYPE` at `/events/N/type`. When type is valid, inspect payload against that branch only.
3. For independent violations within one stage, traverse object properties in **UTF-8 byte lexicographic order of decoded key strings**, arrays by ascending integer index; report the first path. Within the same path, use `required → additionalProperties → type → const/enum → numeric/string/array bounds` to break ties. Different implementations must produce the same issue by these rules.
4. This rule selects one issue from a set of *actual* violations; it never skips a higher-priority RAW/LEX violation to disclose a later SCHEMA issue. Syntactic JSON offsets are counted in raw bytes, not Unicode codepoints.

## 2. JSON Pointer examples

| Failure | Chosen pointer | Why |
|---|---|---|
| Missing root `duration_us` | `/duration_us` | Name of missing member |
| Unknown `approved` root property | `/approved` | Unauthorized property |
| Duplicate `event_id` at third event | `/events/2/event_id` | Second occurrence in event array |
| Wrong pilot decimal in third event | `/events/2/payload/flap_demand` | Concrete member location |
| Byte overflow or invalid UTF-8 | `""` | No trusted JSON tree |
| Unknown tagged event at index 4 | `/events/4/type` | Tagged-union discriminant |

## 3. Data-integrity caution

The approved R1.1 wire schema validates object structure, but it cannot alone enforce global ID uniqueness, raw byte limits, exact decimal token scaling and original-time order. Preflight must run all passes; **never** let schema success alone create a runner. Number tokens are exact base-ten values; for example `1e-6` may be accepted where `0.0000005` must be rejected (nonintegral micro units).

## 4. Unsupported or deferred interfaces

`SIM_VOLTAGE_WARNING_RECOVERED`, live RC input, firmware voltage/current events and any autonomous V2 event remain prohibited. A failing v1 scenario must not be silently translated to v2. Host allowlist / engine revision trust validation is a separate host capability gate and is **not** a parser issue taxonomy; this Phase 2.12 does not certify host run permission.
