# G0-A1 — R1.1 Compatibility & Change Impact Review (Phase 2.12)

- **ID:** BB-P212-COMPAT-152 · **SA Status:** APPROVAL OF EXISTING R1.1 PRESERVED, NEW DIAGNOSTIC CANDIDATE PENDING.

## 1. Change categories

| Item | R1.1 version | Phase 2.12 operation | Changes frozen bytes? |
|---|---|---|---|
| Scenario wire schema | `contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | reference only | **No** |
| Exact integer M0 | `133` / machine JSON | reference only | **No** |
| FSM + SIM numeric policy | `115` / `116` | reference only | **No** |
| Trace/header/tick/terminal | `134` / machine JSON | reference only | **No** |
| External report schema v2 | existing closed schema | separate sidecar instead of adding a field | **No** |
| Parser rejection details | Previously unspecified beyond broad run status | new diagnostic sidecar + `P_*` registry | **New reviewable contract** |

## 2. Scenario validation versus runtime refusal

- *Invalid raw UTF-8, malformed JSON, duplicate keys or repeated global event ID:* PRE-FLIGHT REJECTION; zero tick count; no full canonical trace.
- *Schema-valid `SIM_CONTROL_FRAME INVALID` event:* PRE-FLIGHT ACCEPTANCE; then runtime `E_FRAME_INVALID` and safety policy decide the state/trace.
- *Schema-valid multiple distinct VALID controls within one tick:* PRE-FLIGHT ACCEPTANCE; then `E_CONTROL_BATCH_CONFLICT` at runtime. Do **not** reject valid scenario solely because controls conflict semantically within one evaluation tick.
- *`context=FLIGHT_TEST_APPROVED` or `provenance=REAL_RF`:* PRE-FLIGHT REJECTION; never use physical hardware adapters.
- *Valid scenario but unapproved engine/policy:* HOST TRUST FAILURE; no core action; not a parser diagnostic. A future separate approved host report contract must define how that failure is externally represented, without contaminating parser V1.

## 3. Risk register

| Finding | Risk if omitted | SA mitigation | Status |
|---|---|---|---|
| R11-GAP-01 exact issue taxonomy | Different implementations return incompatible errors | `150–151`, sidecar schema/registry and cases | SPECIFIED / OWNER APPROVAL PENDING |
| R11-GAP-02 host trust allowlist | Scenario self authorizes execution | independent immutable allowlist | NOT IMPLEMENTED |
| R11-GAP-03 Unicode/JCS cross-runtime | Replay diverges by runtime | independent canonicalization verification | NOT RUN |
| R11-GAP-04 append/truncation/quotas | Virtual output with incomplete evidence | failure-injection tests after implementation | NOT RUN |
| R11-GAP-05 unicode IDs | Byte-count and order bugs | exact UTF-8 pointer/ID tests | SPECIFIED / NOT RUN |
| R11-GAP-07 hardware/in-air response | Unsafe extrapolation from simulator to flight | G0-B/G4 continue NO-GO | BLOCKED |

## 4. Version governance

The candidate diagnostic extension is a **separate namespace and artifact**. If an owner accepts it, pin its exact SHA-256/Git SHA and add a decision record. If amended, publish a new version; do not silently edit `117/132/134`, mutate the R1.1 frozen machine index or relabel past oracle outcomes PASS. Developers may raise ambiguity to SA; they may not invent `E_*` codes or alter output formats.
