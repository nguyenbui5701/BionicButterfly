# BionicButterfly — Phase 2.0 Design Consistency & G0-A Verification Plan

- **Document ID:** BB-VERIFY-052 · **Version:** 0.1 · **Date:** 2026-11-12
- **Status:** PLAN ONLY — **all DF and PC-A tests NOT RUN**.
- **Scope:** document inspection and future deterministic host tests. **Does not replace** `14` G0–G4, `29` FR/NFR traceability, `35` RC UX, `38` control authority or `46` rig tests.

## 1. Documentation checks DF-01…DF-18

| Test | Check | Pass criterion for eventual design freeze | Current |
|---|---|---|---|
| DF-01 | latest owner Git baseline | exact clean or reconciled repo commit + changed-file list recorded | NOT RUN |
| DF-02 | Design file inventory | all declared paths from the design inventory accessible; numbering gaps documented (do not assume every number exists) | NOT RUN |
| DF-03 | V1/V2 scope | no document requires autonomy before RC manually controlled V1 | NOT RUN |
| DF-04 | frame agreement | body axes and moment signs consistent in `19`,`37`,`42` and fixture | NOT RUN |
| DF-05 | requirement ID integrity | FR-001..023 and NFR-001..011 unique/traceable in `02`,`29` | NOT RUN |
| DF-06 | ADR registry | decisions D-001..050 traced; new supplement never claims approval | NOT RUN |
| DF-07 | state terminology | `ARMED_IDLE` not falsely labelled physical ground; airborne UNKNOWN | NOT RUN |
| DF-08 | RC protocol contract | no assumed CRSF frame sequence; RF health distinct from UART freshness | NOT RUN |
| DF-09 | link-loss/disarm | bench and flight policies separated; no preapproved in-air shutdown | NOT RUN |
| DF-10 | physical outputs | no direct UI/ISR → PWM; supervisor and envelope gate mandatory | NOT RUN |
| DF-11 | example numbers | 70/82g, 5/20/500ms, PWM ranges marked study/sim, not certified | NOT RUN |
| DF-12 | electrical interfaces | no 2S direct XIAO BAT/5V; USB/BEC backfeed and boot TX handled | NOT RUN |
| DF-13 | radio arm modes | ELRS v4/CH5 implications documented and model-specific | NOT RUN |
| DF-14 | simulator boundary | no airplane lift/stability claims based on waveform simulation | NOT RUN |
| DF-15 | reference licenses | upstream source/cad/assets imported only with proven rights | NOT RUN |
| DF-16 | test evidence | G1/G2/G3/G4 statuses separated; no PASS invented from documentation | NOT RUN |
| DF-17 | workspaces and commit policy | SA only Design/Task once approved; Dev source; PR isolated; owner push timing | NOT RUN |
| DF-18 | versioned approval | every freeze requires owner decision, exact revisions and linked hazards | NOT RUN |

A document check is **not a software test** and cannot demonstrate actuator electrical safety or flyability.

## 2. Future host-only test cases PC-A01…PC-A20 (design specification)

| Test ID | Input scenario | Observable acceptance criterion | Status |
|---|---|---|---|
| PC-A01 | cold boot with ARM held high | no virtual output enabled; no autoarm | NOT RUN |
| PC-A02 | reset after active state | state not active/armed until explicit reauthorization | NOT RUN |
| PC-A03 | valid owner plus throttle nonneutral at arm | deny with specific reason | NOT RUN |
| PC-A04 | low→high arm edge after valid qualifications | exactly one request recognized; no repeated edge from held high | NOT RUN |
| PC-A05 | conflicting RC/bench/simulator owner inputs | active authorized owner only changes virtual output | NOT RUN |
| PC-A06 | rapid source switching and stale owner | denial and event reason; no unauthorized output | NOT RUN |
| PC-A07 | UART control packets fresh but RF status LOST | deny new arm and record distinct statuses | NOT RUN |
| PC-A08 | UART packets fresh but RF UNKNOWN | new arm denied; UNKNOWN displayed, never coerced healthy | NOT RUN |
| PC-A09 | NaN/Infinity/out-of-range or invalid schema | reject without refreshing valid-control age or output | NOT RUN |
| PC-A10 | extreme flap+steer demand | finite normalized L/R and explicit saturation reason | NOT RUN |
| PC-A11 | virtual limits/NaN in profile | invalid profile blocks output; never generic flight defaults | NOT RUN |
| PC-A12 | profile/servo envelope write while armed | rejected atomically, previous config unchanged | NOT RUN |
| PC-A13 | bench UI attempts flight takeover / OTA | denied and logged | NOT RUN |
| PC-A14 | scenario replay with identical seed, virtual clock | byte-identical normalized event trace, barring explicitly excluded nondeterminism | NOT RUN |
| PC-A15 | different scheduler partitions, same physical timestamps | same phase/state within predeclared floating-point tolerance | NOT RUN |
| PC-A16 | set `FLIGHT_APPROVED` or `BENCH` context in host-only build | rejected even if profile name matches; simulated outputs only | NOT RUN |
| PC-A17 | RF loss then recovery with ARM still high | no automatic restart | NOT RUN |
| PC-A18 | brownout/fault and valid frame simultaneously | deterministic priority, latched fault and recovery guard | NOT RUN |
| PC-A19 | telemetry with no physical wing sensor | measured angle/airborne state `UNKNOWN` or null | NOT RUN |
| PC-A20 | proposed simulator ‘hover’ profile without validated aero data | no claim of real hovering / lift / stability in UI or report | NOT RUN |

**Quantitative threshold rule:** any predeclared numeric test limit must be approved *before execution*. In this host-only slice, state/ownership tests can use exact equality; numerical phase comparison needs documented float tolerance and time sampling scheme. No invented hardware current/latency/servo tolerances.

## 3. Evidence record and completion bar

```yaml
review_id: "PHASE20-DF-___"
status: "NOT_RUN"
repository_commit: null
reviewed_file_versions: []
scoped_approval: null
requirement_ids: []
conflict_ids: []
expected: null
actual: null
evidence_paths: []
reviewer: null
owner_decision: null
```

- **Design checkpoint pass:** DF-01…18 documented with evidence and owner disposition; no P0 design conflict left unresolved inside the slice requested for approval.
- **Future G0-A1 approval:** explicitly frozen `51` plus schema/state/context decisions and negotiated host test acceptance; **not a permission to fly**.
- **G1 implementation PASS:** would require actual tests/trace evidence on code built to approved requirements, not these Markdown specs.
- **G2/G3/G4:** separate authorizations and measured hardware/flight evidence; remain NOT RUN/NO-GO.
