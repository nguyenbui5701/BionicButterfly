# G0-A1 — R1.1 Design Vectors, Migration, and Integrity Claims

- **ID:** BB-P210-VEC-135 · **Status:** DESIGN REFERENCE / NO G1 TEST PASS

## 1. Files and exact expected results

| Input or vector | Purpose | Expected design result |
|---|---|---|
| `P210_MINIMAL_WIRE_V2.json` | BOOT at 0, D=5ms | two authored ticks, BOOT→SELF_TEST→DISARMED, both null outputs |
| `P210_NOMINAL_M0_WIRE_V2.json` | LOW 15/35ms, HIGH edge 40ms, HIGH confirm 140ms, demand 145ms | ACTIVE at 145ms with M0 `(250000,750000)` after guards, if trusted policy/engine and RF fresh |
| `P210_INVALID_UART_WIRE_V2.json` | typed in-band INVALID at 20ms | resets LOW qualification; later LOW at 35ms is first new LOW |
| `P210_RESET_CATA_WIRE_V2.json` | simultaneous RESET and catastrophe at 20ms | `FAULT_LATCHED` priority, null output; no in-run clear |
| `P210_ACK_SHAPE_ONLY_V2.json` | ACK is syntactically valid | ACK at DISARMED without prior fault is not permission to recover/arm |
| `P210_DUPLICATE_KEYS_INVALID.json` | duplicate root key in JSON token stream | preflight reject before core; despite parsers that silently overwrite |
| `P210_M0_GOLDEN_VECTORS.json` | 12 exact algebra vectors | no running hardware; requires independently implemented mixer comparison |

## 2. Hand-authored canonical mini-trace (design-only)

- `scenario_digest`: `b4cdadd91f838eef7c41866c8e16744dc4741353e9d7508239cbfae4bac874bf`
- `replay_identity`: `09a6d1290fbe150216652946078bfb20361d2bc2cc020872077ff3a5850b1b98`
- `control_trace_sha256`: `1cdaa68e016d4227d8623adf285a6d28ace9092bf1c45ef7a21b65638a4a10a3`
- `policy_digest`: `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`
- `trace_bytes`: 1433 (header + 2 tick lines + terminal, exactly one trailing LF per line).

The above is an *authored expected trace* with the explicit design-reference `engine_revision`; **not** evidence that any running simulator produced it. Only test its bytes, schema and hash calculation. For G1 acceptance use a distinct real engine revision bound in the trusted allowlist and compare its actual state/output against the oracle; its replay_identity and full digest will differ if the engine revision differs, which is expected by R1 `118`.

## 3. Compatibility policy

- v1 example files remain readable as historical sources and must not be treated as approved v2 runtime inputs; explicit opt-in conversion tool (future separately authorized) may add `schema_version=2` and approved `duration_us` after validation.
- No default injection of `SIM_RESET`/catastrophe/ACK, no guessing `config_id`, no lowering precision silently.
- v2 source JSON does not itself grant policy trust; a valid fixture can still be blocked by the independently provisioned allowlist.
- Different `run_id`, locale, time zone or file path cannot affect normative trace bytes. Input event array reordering can affect scenario_digest; the scenario byte/domain order is not semantically silently sorted by replay.

## 4. Explicit limits of this phase

JSON Schema examples, exact M0 calculations and authored JCS-compatible bytes were validated as **design artifacts**. No host runtime, RAF, serial, servo/wing, flight test, append failure injection or end-to-end G1 execution occurred. Test IDs remain NOT RUN.
