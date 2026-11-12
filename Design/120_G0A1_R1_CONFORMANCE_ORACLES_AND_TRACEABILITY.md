# BionicButterfly — G0-A1 Approved R1 Design Conformance Oracle Matrix

- **Document ID:** BB-P28-TEST-120 | **Revision:** R1 / 1.0 | **Status:** **DESIGN CASES ONLY; ALL NOT RUN**
- **Expected contract:** `115` FSM; `116` policy; `117` schema/error; `118` replay; `114` approved scope.

## 1. New review vectors

| ID | Review condition | Expected contract result | Executed |
|---|---|---|---|
| `P28-T01` | Duplicate event_id at disjoint timestamps | VALIDATION_REJECTED, zero ticks; E_DUPLICATE_EVENT_ID | NOT RUN |
| `P28-T02` | Two different valid control bodies same tick (LOW and HIGH) | E_CONTROL_BATCH_CONFLICT; no accepted LOW/HIGH or age refresh | NOT RUN |
| `P28-T03` | Different IDs, same semantic payload same tick | one observation; IDs sorted; latest original timestamp | NOT RUN |
| `P28-T04` | Valid LOW + typed invalid UART in same tick | no qualifying LOW; E_FRAME_INVALID | NOT RUN |
| `P28-T05` | Same-tick healthy and lost | LOST effective; no arm or active output | NOT RUN |
| `P28-T06` | ACTIVE + RF LOST + RESET | CONTINGENCY, null output | NOT RUN |
| `P28-T07` | ACTIVE + catastrophe + RESET | FAULT_LATCHED, cannot clear in-run | NOT RUN |
| `P28-T08` | CONTINGENCY + second LOW completing window + ACK | deny ACK this tick; remain CONTINGENCY | NOT RUN |
| `P28-T09` | CONTINGENCY + committed LOW + eligible ACK, all sources restored | DISARMED, LOW consumed, no rearm | NOT RUN |
| `P28-T10` | Two distinct IDs equivalent ACK same tick | one logical ACK; no double recovery | NOT RUN |
| `P28-T11` | LOW at 15ms; invalid at 25ms; LOW at 35ms | new LOW is first; window not completed | NOT RUN |
| `P28-T12` | HIGH first at 40ms; confirm 139999us or 140000us | 139999 no qualification; 140000 yes with healthy preconditions | NOT RUN |
| `P28-T13` | ACTIVE, no new control, both ages <=200ms | held authorized effort; no timestamp refresh | NOT RUN |
| `P28-T14` | ACTIVE, no new control, age >200ms | CONTINGENCY and (null,null) | NOT RUN |
| `P28-T15` | SELF_TEST, policy approved and no critical health issue, RF unknown | DISARMED but no ARM | NOT RUN |
| `P28-T16` | Unrecognized voltage recovery event type in input v1 | VALIDATION_REJECTED; do not invent event schema | NOT RUN |
| `P28-T17` | CONTINGENCY with scheduler stalled, ACK after RF healthy | no ACK-clear | NOT RUN |
| `P28-T18` | Scenario includes approved=true and false trusted allowlist | preflight rejection, no sink | NOT RUN |
| `P28-T19` | terminal contains control_trace_sha256 | nonconforming complete trace; reject | NOT RUN |
| `P28-T20` | ACTIVE tick append fails before publish | no new output, FAILED_INCOMPLETE_EVIDENCE, complete SHA null | NOT RUN |
| `P28-T21` | same scenario/policy/engine/schedule, different execution-instance UUID | same normative trace bytes and digest | NOT RUN |
| `P28-T22` | one byte changed in canonical approved policy | mismatched digest rejected at preflight | NOT RUN |
| `P28-T23` | SIM JSON asks real servo PWM/FLIGHT_TEST_APPROVED | preflight E_CONTEXT_DENIED; no hardware adapter | NOT RUN |
| `P28-T24` | E_EVENT_ID_CONFLICT ambiguous legacy result | no silent alias to v2; report AMBIGUOUS_LEGACY_ERROR | NOT RUN |
| `P28-T25` | compare head and prepended notices against blob guards | all sources match or freeze BLOCKED | NOT RUN |
| `P28-T26` | frame or RF age equals 200000 vs 200001µs | exact boundary allowed; +1 fails if active | NOT RUN |
| `P28-T27` | ARM_CHECK 100ms timer tick but no confirming HIGH frame | does not reach ARMED_IDLE | NOT RUN |
| `P28-T28` | normal complete run expected fault injection and full terminal | can report COMPLETED; PASS only if oracle matches | NOT RUN |

The machine-readable companion is `fixtures/P28_R1_ORACLE_INDEX.json`. Values are specifications, not executable fixture results. If an implementation doesn't support a modeled voltage warning event under input v1, the test must **reject unrecognized v1 input**, not fabricate a recovered voltage waveform.

## 2. Inherited coverage and de-duplication

Existing PC-A (20), G1B (24), P22 (24), P23 (20), P24 (24), P25 (16), P26 (28), P27 (16) and P28 (28) are **documented test-case inventories**, not independent executed PASS counts. The eventual test suite may consolidate duplicate scenarios but MUST preserve original IDs in a traceability matrix. Design-review approval means the expected semantics are accepted; **not one executable case here has been run**.

## 3. Mandatory negative tests at first implementation review

Preflight duplicates, unauthorized policy bypass, mixed UART-valid/RF-lost, in-band INVALID, nested invalid or unknown JSON fields, RF and control freshness boundaries, reset+critical power, catastrophe latch, same-tick ACK+last LOW, stale held output, trace append failure, digest self-reference, concurrent duplicate equivalent ACK and physical adapter denial. `P28-T01–T28` are controlling where prior proposal expectations disagree.

## 4. Gates are not conflated

- **G0-A1 design freeze:** owner-approved contract + source reconciled to an exact Git commit + SHA guards/digest and no unresolved P0 contradictions.
- **G1 software acceptance:** implementation separately authorized, host-only integration tests executed and PASS against frozen revision; evidence complete.
- **G0-B/G3/G4 physical progression:** independent electrical/mechanical/flight evidence, flight-specific contingencies and owner go/no-go. No simulator PASS can establish physical controllability.
