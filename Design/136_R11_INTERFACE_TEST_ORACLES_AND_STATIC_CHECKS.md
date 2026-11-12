# G0-A1 — Phase 2.10 R1.1 Interface Test Matrix

- **ID:** BB-P210-TEST-136 · **Status:** all tests below are **SPECIFIED / NOT RUN as simulator tests**.
- **Prerequisites:** owner accepts R1.1 decisions; future executable is pinned to approved Git and policy digest.

| Test ID | Setup / input | Expected behavior | Layer |
|---|---|---|---|
| P210-T01 | `P210_MINIMAL_WIRE_V2.json` schema + semantic preflight | ACCEPT; 2 design ticks, not real run | input |
| P210-T02 | `P210_NOMINAL_M0_WIRE_V2.json` | ACCEPT input, ACTIVE at 145ms under R1 guards; `(250000,750000)` | input/FSM/mix |
| P210-T03 | duplicate JSON key (raw text fixture) | VALIDATION_REJECTED, zero core ticks | parser |
| P210-T04 | duplicate global event ID at different times | E_DUPLICATE_EVENT_ID, zero core ticks | parser |
| P210-T05 | extra event or payload property | reject, zero ticks | schema |
| P210-T06 | unrecognized `SIM_VOLTAGE_WARNING_RECOVERED` | reject, no invented v1/v2 semantics | schema |
| P210-T07 | typed UART INVALID observation | ACCEPT input; runtime E_FRAME_INVALID, no age refresh | runtime |
| P210-T08 | valid LOW and HIGH distinct bodies in same 5ms tick | ACCEPT input; runtime batch conflict, neither accepted | runtime |
| P210-T09 | frame age 200000µs vs 200001µs | eligible boundary vs stale/CONTINGENCY | runtime |
| P210-T10 | two LOWs 19999us apart | no qualification even if evaluated 20ms apart | FSM |
| P210-T11 | ACK + final qualifying LOW same tick | no ACK-clear; need prior committed LOW | FSM |
| P210-T12 | RESET + catastrophe same tick | FAULT_LATCHED, no in-run clear | FSM |
| P210-T13 | ACTIVE no new frame, both sources fresh | M0 from held input S1; timestamps unchanged | FSM/mix |
| P210-T14 | M0 flap .5 steer +.25 | L=250000 R=750000, no tags | mix |
| P210-T15 | M0 flap .5 steer -.25 | L=750000 R=250000, no tags | mix |
| P210-T16 | M0 flap 1 steer +1 | L=0 R=1000000, RIGHT_HIGH only | mix |
| P210-T17 | M0 raw output equal boundary | zero clip tags for equality | mix |
| P210-T18 | flap 0.0000005 | strict **reject precision**, never input rounding | parser |
| P210-T19 | flap `1e-6` | ACCEPT exact Decimal scale, mixer result deterministic | parser/mix |
| P210-T20 | malformed Unicode surrogate / invalid UTF-8 | reject before runner | parser |
| P210-T21 | two equivalent distinct-ID control events in same tick | one semantic observation, sorted causal IDs | runtime/trace |
| P210-T22 | per-record trace schema | schema validation for header/tick/terminal; unknown key rejected | trace |
| P210-T23 | two ticks with discontinuous state/index | reject whole-stream sequence, schema-only insufficient | trace |
| P210-T24 | reserialize same authored ASCII-only trace | identical bytes and SHA in `P210_MINIMAL_VECTOR_ATTESTATION` | trace bytes |
| P210-T25 | terminal includes self SHA | schema reject, no recursive digest | trace |
| P210-T26 | output_allowed=false with only one effort null | schema reject, no partial virtual command | trace |
| P210-T27 | quota or append fails before active tick publication | output not exposed, report FAILED_INCOMPLETE_EVIDENCE, complete SHA null | trace transaction |
| P210-T28 | same inputs/policy/engine/revision, different invocation UUID | same canonical normative trace bytes | replay |
| P210-T29 | unsigned UTF-8 byte lexical order IDs including multibyte | stable comparator, no locale/unicode normalization | trace |
| P210-T30 | external report `run_status=VALIDATION_REJECTED` with full trace digest | reject inconsistent report | report |
| P210-T31 | 60s run with max long causal IDs/reasons vs 16MiB trace quota | fail incomplete deterministically when needed; never silent policy increase | capacity |
| P210-T32 | scenario tries `context=FLIGHT_TEST_APPROVED` or `approved=true` | deny, zero core ticks, no physical adapter | trust |

**Design checks actually performed in this phase:** JSON Schema `check_schema` and fixture validation, deterministic M0 example calculations, typed record validation, byte hash of authored reference trace, file SHA manifest and ZIP CRC. These are **not simulator G1 test runs**. No prior historical test ID is silently removed: retain PC-A, G1B, P22–P29 inventories and link equivalent cases when eventually building a G1 harness.
