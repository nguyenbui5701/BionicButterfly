# BionicButterfly — Phase 2.8 Architecture Freeze Readiness (SA Gate)

- **Document ID:** BB-P28-GATE-121 | **Date:** 2026-11-13 | **Source HEAD:** `3d9a4f28d521190d10579cab48d8b732817892c9`
- **Decision:** **R1 DESIGN SELECTION APPROVED. EXACT MERGED GIT DESIGN BASELINE NOT YET FREEZE-VERIFIED.**

## 1. Evidence and status

| Gate | Evidence | SA status |
|---|---|---|
| G0A1-01 Owner chose R1 | explicit current-conversation statement, record `114` | **APPROVED** for PC-only |
| G0A1-02 Repository identity | Git connector reads `main@3d9a4f28d521190d10579cab48d8b732817892c9` and `107–113` | **VERIFIED** at source ref |
| G0A1-03 Safety and authority | single controlling contract `115` plus source notices | **DESIGN-RECONCILED LOCALLY** |
| G0A1-04 Numeric policy and digest | exact canonical bytes, SHA `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10` | **DESIGN RECORD PREPARED** |
| G0A1-05 Input/results/replay | `117`, `118`, typed errors v2, external trace SHA | **DESIGN-RECONCILED LOCALLY** |
| G0A1-06 Conflicting previous candidates | source notices for 26 exact local copies; guard manifest | **PREPARED; NOT YET MERGED TO GIT** |
| G0A1-07 Test design coverage | `120`, inherited IDs; no runtime source | **SPECIFIED / ALL NOT RUN** |
| G0A1-08 Source revisioned freeze | future exact merge commit + review of all updated blob guards | **PENDING** |
| G0A1-09 Trusted runtime allowlist | outside untrusted scenario, bind to host build | **NOT PROVISIONED; IMPLEMENTATION WORK LATER** |
| G0A1-10 Developer work authorization | separate `Task/` decision | **NOT GIVEN** |
| G0A1-11 G0-B/G3/G4 | real hardware, safety, controllability evidence | **HOLD / NO-GO** |

## 2. No hidden P0 candidate-vs-approved conflict

Older docs remain in repo for audit and explicitly note R1 authority if applying this package. Unresolved physical questions in `27`, `31`, `37–47` do **not** block the narrow PC-only design but DO block any implication that the aircraft is safe to fly. Software implementation may discover new technical defects; design freeze does not preempt a new controlled ADR/revision.

## 3. Required final configuration-control actions

1. Owner integrates Phase2.8 package into `Design/`, with no conflicting unreviewed edits. Check expected file blob guard first.
2. SA retrieves the new Git HEAD, checks each new/updated file, policy byte hash, reference links and conflict notices, and records the post-integration SHA.
3. If unchanged, SA may recommend declaring **G0-A1 R1 DESIGN FROZEN** at that exact merged commit; if mismatches or P0 findings arise, mark **REVISE** instead. Owner retains approval authority for an amended R2.
4. Only a future explicit implementation handoff may lead to task files; no such task is included here.

## 4. Flight and physical NO-GO remain

The owner-approved product aim is a *real manual-RC flying butterfly*, but G0-A1 has no aircraft mass/CG/lift/control-authority validation, in-air loss-link actions, RC version mapping, actuator datasheets, rail load or venue/flight readiness evidence. Do not run free-flight tests based on this host-only gate.
