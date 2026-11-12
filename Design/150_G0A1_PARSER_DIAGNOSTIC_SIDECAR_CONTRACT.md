# G0-A1 — Deterministic Parser Diagnostic Sidecar v1 (Candidate)

- **ID:** BB-P212-DIAG-150 · **Status:** PROPOSED, not part of frozen R1.1 bytes.
- **Machine schema:** `contracts/G0A1_PREFLIGHT_DIAGNOSTIC_V1_CANDIDATE.schema.json`.
- **Issue registry:** `contracts/G0A1_PREFLIGHT_ISSUE_REGISTRY_V1_CANDIDATE.json`.

## 1. Architectural separation

`parse(raw_bytes)` returns either `ACCEPTED + immutable typed scenario`, or `REJECTED + exactly one typed *external* diagnostic`. The rejected branch creates **zero core ticks**, no virtual output, no canonical complete trace. Existing R1.1 `SimulationRunReportV2` remains byte-for-byte unchanged; an eventual host wrapper may independently emit its pre-existing `run_status=VALIDATION_REJECTED` report. This sidecar is not embedded in JSONL, cannot introduce new `reason_codes` and cannot affect replay/engine digest.

*Do not confuse* the new `P_*` **preflight issue codes** with frozen `E_*`/`R_*` runtime codes. The map `frozen_base_error_code` uses only previously defined `E_DUPLICATE_EVENT_ID` and `E_CONTEXT_DENIED`, where applicable; otherwise it is JSON `null` and does not claim an unknown `E_*` code exists.

## 2. Exact rejected response shape

```json
{
  "diagnostic_format_version": 1,
  "scope": "PC_SIM_ONLY",
  "run_status": "VALIDATION_REJECTED",
  "evaluated_tick_count": 0,
  "evidence_complete": false,
  "raw_input_sha256": "<64 lowercase hex characters>",
  "primary_issue": {
    "code": "P_JSON_DUPLICATE_KEY",
    "stage": "LEX",
    "json_pointer": "/schema_version",
    "frozen_base_error_code": null
  }
}
```

`raw_input_sha256` hashes the **original input byte stream**, even when it contains invalid UTF-8; it is for diagnostics only and is *not* the scenario_digest or trace hash. `json_pointer` is RFC 6901-like: empty string is root; `/` segments escape `~` as `~0` and `/` as `~1`. If the input is undecodable or has no meaningful syntax tree, use `""` rather than invent a path. For a missing schema property, point to the expected missing member (`/duration_us`); for duplicate keys, point to the second occurrence in its parent path, without accepting last-wins parsing.

## 3. Invariants

- Exactly **one** primary issue returned for rejected input, selected using `151` and machine registry; no ambiguous multiple diagnostics with inconsistent ordering.
- `P_*` codes are diagnostic-only. No C++/Python exception string may substitute for a stable issue code.
- The diagnostic object has `additionalProperties=false`; it must not leak raw scenario bytes, secrets, local filenames, absolute paths or wall-time.
- No sidecar is produced for a valid scenario that contains a legal in-band `SIM_CONTROL_FRAME` with `uart_frame_status=INVALID`: its runtime fault is `E_FRAME_INVALID` per R1.1, not a parser failure.
- Unsupported v1 input receives a typed rejection, **not** an automatic migration to v2.
- Denied physical context (`FLIGHT_TEST_APPROVED`) is always an input error; this design does not enable real hardware.

## 4. Compatibility and versioning

The frozen external report schema has `additionalProperties=false`; therefore attaching a `diagnostics` field to it would **break R1.1**. The sidecar is a separate optional product of validator preflight (a new artifact schema), not a field addition. The owner must approve this supplemental diagnostic contract before Developer treats it as a normative acceptance requirement. **R1.1 schema, M0 and trace SHA remain unchanged.**
