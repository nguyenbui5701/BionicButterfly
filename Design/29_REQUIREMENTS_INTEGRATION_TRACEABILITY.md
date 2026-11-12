# BionicButterfly — V1 Requirements / Design / Test Traceability

- **Document ID:** BB-TRACE-029 | **Version:** 0.1 | **Date:** 2026-11-12
- **Status:** PROPOSED. All tests below: **NOT RUN**. A planned test is NOT evidence.
- **Canonical requirements:** `02_V1_REQUIREMENTS.md`. Canonical existing test specifications: `14_V1_VERIFICATION_PLAN.md` VT, `18_MECHANICAL_EXPERIMENT_PLAN.md` MX, `24_ELECTRICAL_BENCH_VERIFICATION.md` EE-T.

## 1. Functional requirement mapping (complete FR-001...FR-023)

| Requirement | Design artifact that constrains behavior | Verification / gate | Evidence status |
|---|---|---|---|
| FR-001 boot/disarm | `27` FSM; `23` GPIO startup | VT-01, EE-T06 / G1–G2 | NOT RUN |
| FR-002 explicit arm | `27`, `16` RC | VT-02, IT-01, EE-T10 / G1–G2 | NOT RUN |
| FR-003 stop priority | `27` stop policies | VT-03, IT-03, IT-06 / G1–G4 | NOT RUN; FLIGHT TBD |
| FR-004 normalized command | `28` typed interfaces | VT-04, EE-T05 / G1–G2 | NOT RUN |
| FR-005 single owner | `16`, `27`, `28` | VT-05, VT-17 / G1–G2 | NOT RUN |
| FR-006 freshness | `16`, `27`, `28` | VT-06, IT-02, EE-T09 / G1–G3 | NOT RUN |
| FR-007 link loss | `27`, `25` | VT-07, VT-20, IT-06 / G1–G4 | NOT RUN; FLIGHT TBD |
| FR-008 supervisor gate | `27`, `28` | VT-08, IT-03 / G1–G2 | NOT RUN |
| FR-009 time-based trajectories | `28` | VT-09, IT-04 / G1 | NOT RUN |
| FR-010 servo limits | `23`, `28`, `18` | VT-10, EE-T07, MX-03 / G1–G3 | NOT RUN |
| FR-011 power safety | `22`, `25`, `27` | VT-11, EE-T08/11 / G1–G3 | NOT RUN |
| FR-012 explicit fault recovery | `27` | VT-12, IT-01/03 / G1 | NOT RUN |
| FR-013 simulator | `28` | VT-13, IT-04 / G1 | NOT RUN |
| FR-014 telemetry | `28` observation only | VT-14 / G1 | NOT RUN |
| FR-015 bench UI | `05`, `26` INT-03 | VT-15, VT-17/22, IT-05 / G1 | NOT RUN |
| FR-016 optional LEDs | `20`, `28` | VT-16, EE-T14 / G1–G3 for C1 | NOT RUN |
| FR-017 RC only in flight | `16`, `27`, `28` | VT-17, IT-03/05 / G1–G3 | NOT RUN |
| FR-018 TX controls / channels | `16`, `23` | VT-18, EE-T05/10 / G1–G2 | NOT RUN |
| FR-019 true RC flight | `31`, `14` G4 | VT-19, IT-06, MX-10 / G4 | NOT RUN; G4 NO-GO |
| FR-020 flight contingencies | `25`, `27`, `31` | VT-20, IT-02/06, EE-T13 / G3–G4 | NOT RUN; G4 NO-GO |
| FR-021 mass/force/CG | `17–21`, `31` | VT-21, MX-01…10, EE-T15 / G2–G3 | NOT RUN |
| FR-022 no armed config | `16`, `28` | VT-22, IT-05 / G1–G2 | NOT RUN |
| FR-023 flight logs | `28`, `30` | VT-23, IT-06 / G4 | NOT RUN |

## 2. Nonfunctional mapping (complete NFR-001...NFR-011)

| Requirement | Design evidence | Test/review gate | Status |
|---|---|---|---|
| NFR-001 host-testable core | `28` dependency direction | core build + VT-01…13 / G1 | NOT RUN |
| NFR-002 central output policy | `27` INV-S01/04/05; `28` | property tests + code review / G1 | NOT RUN |
| NFR-003 trust boundary | `16`, `27` | unauthorized sources, held frame and lost RF tests / G1–G2 | NOT RUN |
| NFR-004 credentials | `28` config separation | secret scan and code review / G1 | NOT RUN |
| NFR-005 provenance | `12`, `26`, license register | per-file approval and source scan / G0 | OPEN |
| NFR-006 measured servo/wing/rails | `17–25`, `31` | EE-T/ MX evidence / G2–G3 | NOT RUN |
| NFR-007 in-air contingency | `25`, `27`, `31` | IT-06 + reviewed G4 hazard authorization | OPEN BLOCKER |
| NFR-008 build/config logs | `28` | versioned event replay / G1 | NOT RUN |
| NFR-009 UI/LED cannot block | `28` timing contract | VT-16 + timing instrumentation / G1–G2 | NOT RUN |
| NFR-010 actual RX protocol verified | `16`, `23`, `28` | EE-T05/09 + link interrupt / G2 | NOT RUN |
| NFR-011 G4 site and permissions | `30`, `31` | signed flight plan, site review, video | OPEN BLOCKER |

## 3. New integration test specifications (not replacing existing tests)

| ID | Stimulus | Acceptance rule (logical, not airborne validation) | Gate |
|---|---|---|---|
| **IT-01** | Hold transmitter ARM switch high across cold boot, brownout/reset, recovery, then toggle deliberately | Never auto-arm; explicit safe switch edge and qualified inputs required | G1 / G2 |
| **IT-02** | Valid UART frames continue while RF TX is off or receiver reports failsafe; stale channel value held | RF health != valid serial frame; no successful new arm, age/contingency recorded | G1 / G2 / G3 |
| **IT-03** | Same instant: UI arm, disarm switch, malformed radio frame, critical voltage | Supervisor records deterministic priority and rejects unauthorized actuation; no bypass path | G1 |
| **IT-04** | Reorder virtual updates, simulate elapsed time wrap and long pause, compare same timestamp trajectory | Same intended waveform/state within documented numerical tolerance; no time-wrap spontaneous arm | G1 |
| **IT-05** | Write config/OTA/servo endpoint via web while physical RC owns, even with valid credentials | Rejected atomically, event logged, previous approved config intact | G1 / G2 |
| **IT-06** | Replay link loss, battery critical and pilot E-stop at multiple G3 operating points; review policy for G4 | G3 data recorded; **does not pass G4** until signed airframe-specific hazard review and measured controlled-flight evidence | G3 + G4 approval |

## 4. Evidence standard and stage exit criteria

Every future test record must contain test ID; requirement IDs; procedure; date; exact code Git commit; board/receiver/servo/wing/battery revision; config hash; test context (SIM / G2 / G3 / G4); measured input; expected and actual; pass/fail; full logs; video/oscilloscope where needed; hazards/defects; reviewer; signoff link. A simulation trace cannot be relabeled hardware evidence.

**G0:** design documents consistent, unresolved safety dependencies explicitly blocked, license/provenance recorded; owner approves bounded scope. **G1:** pure logic + timing simulation passes. **G2:** approved electrical bench tests. **G3:** approved restrained wing tests with instrumented force/power, safety case. **G4:** specifically authorized controlled RC free-flight experiment with numerical acceptance and evidence. G0 approval does not automatically approve any G2–G4 activity.

## 5. Coverage caveats

- `VT-19` and `VT-23` define final product acceptance, not evidence of achieved flight.
- If selected TX/RX has no trustworthy link-loss indication, resolve before G4 instead of forging `rf_link=HEALTHY` from UART freshness alone.
- Numeric safety/time/force gates await exact hardware measurements; this document does not invent them.

## 6. RC Pilot control and UX traceability overlay (v0.2; tests NOT RUN)

| Existing requirement | New design | New tests | Remaining uncertainty |
|---|---|---|---|
| FR-001, FR-002, FR-012 | `32` arm, `33` profile, `27` state | PX-01,04,08,11,17,20 | exact RX firmware and arm window |
| FR-003, FR-007, FR-020 | `32` link, `36` hazards, `27` policy | PX-07,08,10,16,19 | **G4 in-air response unqualified** |
| FR-004, FR-005, FR-006 | `32` map, `28` adapter/authority | PX-02,03,07,09,18,19 | actual channel ordering and RF health |
| FR-008, FR-009, FR-010 | `33` calibration/mixer; `28` envelope | PX-05,11,12,15 | actuator limits and aerodynamic moment |
| FR-011, FR-021 | `36` power/load hazards; `33` CAL-01…05 | PX-10,15,16 | load, CG, power and real stability |
| FR-013, FR-014, FR-015 | `34` pilot UI, `35` UX tests | PX-13, UX-01…08 | actual human observations |
| FR-016, FR-017, FR-022 | `34` ownership; `33` immutable profiles | PX-06,09,12,14 | timing/flight electronics |
| FR-018, FR-019, FR-023 | `32`, `34`, `35`, `36` | PX-02,03,15,18,20; PX-16 review | **G4 acceptance/site open** |
| NFR-001, NFR-002, NFR-003 | `32`, `33`, `35` | PX-01–14,17–20 G1 | G2 actual radio evidence pending |
| NFR-006, NFR-007, NFR-010, NFR-011 | `33`, `35`, `36` | PX-07/15/16/18/20; UX-06/08 | G2/G3/G4 signoffs missing |

All requirements keep their original IDs; this overlay adds test detail, not silent scope expansion or proof of passing tests.

## 7. Flight dynamics/controllability overlay (v0.3 — all evidence NOT RUN)

| Requirement | New design specification | Verification/evidence | Remaining blocker |
|---|---|---|---|
| FR-004, FR-009, FR-010 | `37` command vs physical motion; `39` bounded mixer | CA-02/04/07/11, VT-09/10 | servo actual response unmeasured |
| FR-011, FR-021 | `37` actual mass/CG/force, `38` rig calibration | CA-01/03/05/06/12/14; FA-01…03 | hardware and aero data absent |
| FR-018, FR-019 | `37` local 4x2 control map; `39` pilot intent and control | CA-07…11/13; FA-04/05/08/09/11 | directional authority unknown |
| FR-003, FR-007, FR-020 | `39–40` in-air control/contingency bounded by `27` | FA-06/07/10/12; IT-06 | **flight policy G4 NO-GO** |
| FR-013/014/023 | `37` model maturity, `38` raw evidence, `40` qualified logs | CA-15; FA-12 | no flight evidence, model D0 |
| FR-016 | `41` C1 separate qualification | CA-02…14 after C1 build | LED aero/power effect unknown |
| NFR-001/002/008 | `37–39` typed data & honest SIM status | G1 replay/mixer and provenance review | not implemented/tested |
| NFR-006/007/011 | `38–41` controlled authority and flight gates | G2/G3 + G4 FA-01…12 | no hardware verification, permissions or flight plan |

**No new FR/NFR IDs introduced.** These map existing scope to additional future observations. A planned `CA/FA` test is not a PASS. Do not issue G2–G4 task or declare design frozen on the strength of these documents.
