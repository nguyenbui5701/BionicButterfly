# G0-A1 — Phase 2.12 Parser Diagnostic Acceptance Matrix

- **ID:** BB-P212-QA-154 · **Status:** SPECIFIED; no executable runtime test.
- **Machine oracle:** `fixtures/P212_PREFLIGHT_NEGATIVE_ORACLE_INDEX.json` lists P212-T01…26, the chosen issue code/path/stage and expected zero core ticks.

## 1. Test families and result invariants

| IDs | Family | Expected primary effect |
|---|---|---|
| T01–03 | raw transport | byte limit, strict UTF-8, BOM rejection; no scenario digest claim |
| T04–08 | strict lexical JSON | reject syntax, duplicate object key, depth, surrogate and nonfinite tokens |
| T09–16 | closed schema | missing/extra property, wire version, context, provenance, config, event tag, duration grid |
| T17–23 | cross-object semantics | global event ID, BOOT, order, range, UTF-8 byte count, prohibited control, micro precision |
| T24 | schema array capacity | frozen `maxItems=20000` enforced by `P_EVENT_COUNT` before a semantic pass |
| T25 | numeric typing | true cannot match integer event timestamp |
| T26 | positive in-band INVALID UART | accepted scenario, runtime must later apply `E_FRAME_INVALID`; **no preflight diagnostic** |

For T01–25 negative rows `run_status=VALIDATION_REJECTED`, `evaluated_tick_count=0`, `evidence_complete=false`, no full trace and no virtual output. T26 is **deliberately not a negative case**. Exact test construction notes, error paths and priority codes are in machine oracle file.

## 2. Reference JSON examples

- `P212_INVALID_DUPLICATE_KEY_RAW.json`: strict duplicate object member; expected pointer `/schema_version` and issue `P_JSON_DUPLICATE_KEY`.
- `P212_INVALID_DUPLICATE_EVENT_ID_WIRE_V2.json`: schema-valid but global event_id duplicate; expected `P_EVENT_ID_DUPLICATE`, pointer `/events/2/event_id`, frozen base `E_DUPLICATE_EVENT_ID`.
- `P212_POSITIVE_INBAND_UART_INVALID_V2.json`: frozen v2 schema-valid example of a deliberately injected UART INVALID observation. Accept **at preflight**, not a proof of runtime behavior.
- `P212_REFERENCE_REJECTION_DIAGNOSTICS.json`: authored expected sidecars for the two malformed examples; *not the output of a running parser*.

## 3. Evidence needed later from Developer

For each T01–26, capture actual input bytes or patch recipe, actual result, expected result, PASS/FAIL, interpreter/library versions, and scenario/core creation counters. Log actual vs expected JSON Pointer, sidecar schema validation and independent raw SHA-256. Run negative tests at multiple nested object depths, including non-ASCII identifier byte lengths, and include a corpus minimizing ambiguous overlapping errors. Build/review of the future module must not depend solely on authored fixtures.

## 4. Review of known non-parser cases

`E_CONTROL_BATCH_CONFLICT`, `E_FRAME_STALE`, `E_RF_NOT_HEALTHY`, ARM ACK precedence, R1 tick S1 and trace writer failure belong to later event/FSM/trace runtime modules. This phase deliberately **does not** call those cases PASS or reclassify them as parser errors. Hardware authority and flight G4 remain separate NO-GO.
