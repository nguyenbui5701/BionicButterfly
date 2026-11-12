# BionicButterfly — Phase 2.1 Architecture Decision Supplement

- **ID:** BB-ADR-065 · **Rev:** 0.1 · **Date:** 2026-11-12
- **Status:** PROPOSED. Append-only proposal to be reconciled into canonical `15_V1_DECISION_REGISTER.md` after exact owner Git baseline review.
- **Purpose:** avoid overwriting a possibly newer owner-edited decision register while still giving unambiguous traceability.

| ID | Subject | Proposed choice | Alternatives | Affected design/test | State |
|---|---|---|---|---|---|
| D-051 | Host capability boundary | only VirtualActuatorSink, PC_SIM context in host build | runtime physical-driver flags (rejected as unsafe) | 56,61,62; G1B-13 | PROPOSED |
| D-052 | Scenario/schema | strict UTF-8 JSON v1, typed provenance | YAML sample of 51 (legacy illustrative) | 57,60; G1B-11/22 | PROPOSED |
| D-053 | Same-time events | atomic batch + safety precedence + conflict rejection | parse-order mutation/event microsteps | 58–59,61; G1B-07–09 | PROPOSED |
| D-054 | SIM fault vs flight fault | virtual sink can inhibit on SIM link loss; not copied to physical in-air policy | generic servo-power-off (rejected for flight) | 58,61; G1B-06/16 | PROPOSED |
| D-055 | Policy/config mutation | immutable during arming/active/fault states; validated disarmed update only | online hot-swap (rejected) | 60; G1B-14/15 | PROPOSED |
| D-056 | Deterministic replay | virtual time, canonical traces, resource bounds | wall-clock timing in core (rejected) | 59,63; TIME and G1B | PROPOSED |
| D-057 | UI role | read-only observer/scenario author, no actuator bypass | direct GUI-to-output control (rejected) | 56,61,62; G1B-21 | PROPOSED |
| D-058 | Review baseline | exact owner main SHA + conflict review + explicit owner G0-A1 approval | treating pushed file list as freeze proof (rejected) | 64,49,53; DF-01/18 | PROPOSED |

**Precedence:** Canonical decisions in owner Git `15` remain authoritative until the owner explicitly accepts an amendment. If IDs `D-051…058` already exist in that file, treat as **collision**: reconcile or renumber rather than duplicate. No physical/electrical/flight decision is changed here.
