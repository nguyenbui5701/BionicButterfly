# BionicButterfly — G0-A1 Source-Document Patch Map and Traceability

- **ID:** BB-P26-PATCH-105 | **Revision:** 0.1 | **Status:** PRE-APPROVAL CHANGE PROPOSAL / NOT COMMITTED
- **Pinned Git baseline:** `b6628e567813396c36d670d17e18f75e5cc443d3`.

## 1. Important boundary: 'candidate consolidated' is not a silent retroactive replacement

`100–103` are **proposed** canonical contracts. Existing `57–98` may still contain different historic/candidate language. Without a documented owner acceptance and a reviewed modification to those files, they remain past proposals. This file is a **change map**, not a license to overwrite user modifications or hide incompatible behavior under a vague 'superseded' label.

## 2. File-level corrective changes after owner accepts contract (all PENDING)

| Existing Design file | Frozen-at-HEAD reference | Specific reconciliation proposed | Test proof |
|---|---|---|---|
| `57` input/errors | repo blob `833ccfcc…` | input v1, separate result/error v2; split duplicated event ID vs valid same-tick conflict; distinguish frame INVALID stimulus | P24-T01…04, P26-T06/11 |
| `58` safety FSM | repo blob `841f3d4a…` | single tick full-batch evaluation, arm/ack/RESET priority consistent with `100–101` | P26-T08/09/20/21 |
| `59` clock/replay | repo blob `ea58f382…` | scheduler eligible time, retain original timestamps; empty tick S1 and no new qualification | P26-T14…18 |
| `67` numeric policy | repo blob `06a26f9d…` | keep candidate numbers, remove self-approval interpretation, pin approved bytes externally | P26-T28 |
| `68` precedence | repo blob `4240405e…` | semantic conflict before DISARM, catastrophic before RESET, active hazard before RESET | P26-T06…09 |
| `69` serialization | repo blob `47de847c…` | trace header+committed decisions+terminal (without digest), LF bytes; digest external | P26-T25…27 |
| `70` trust | repo blob `68f35f8b…` | independently provisioned approval/allowlist; immutable per run | P26-T28 |
| `71` old oracle | repo blob `195dcac1…` | update error/result v2 and mandatory/deferred references; keep historical evidence | test suite cross-reference |
| `78` host API | Phase23 candidate | align accepted-intent vs raw-serial timestamps; one virtual sink commit per tick | P26-T18/19/25 |
| `80` replay ID | Phase23 candidate | stable replay identity separate execution UUID and full control trace digest | P26-T26/27 |
| `84` primary FSM | repo blob `2cc1f50a…` | amend priority RESET vs active critical hazard, empty tick and invalid LOW break; clarify SELF_TEST | P26-T09/11/15/24 |
| `85` compatibility | repo blob `8ee21520…` | retain result/error v2 candidate and typed failure semantics; no old alias conflation | P26-T06/25 |
| `86` tests | Phase24 source | inherit existing tests and append distinct Phase26 vectors, do not silently change outcomes | `104` |
| `87` trust/trace | repo blob `debc8f06…` | explicitly adopt non-self-referential terminal and commit-before-output ordering | P26-T25…28 |
| `93` finding register | repo blob `3dd82645…` | close P25-F01 on new verified commit, update remaining proposed-vs-approved state | `99` and `106` |
| `94` targeted trace | repo blob `d5ea9988…` | accept/adjust explicit bytes & append contract as canonical proposal | P26-T25…27 |
| `95` edge tests | repo blob `a4f8e33d…` | decide S1 and LOW invalid interruption, ACK allowlist | P26-T11/15/20 |
| `96` gate conditions | Phase25 source | mark historical B1 fixed; B2–B5 still pending; no runtime PASS claim | `106` |
| `98` owner decision | Phase25 source | replace old baseline/push blocker; bind to current HEAD and future approved policy digest | `106` |

This patch map **does not include modified copies** of these earlier files. The SA recommends selecting a **single** canonical section for the approved contract and recording explicit override anchors/versions; do not copy contradictory legacy tables forward as parallel normative rules.

## 3. Finding closure trace

| Existing finding | New evidence or recommendation | Closure status |
|---|---|---|
| P25-F01 | Git HEAD read, P24/P25 present, selected local bytes match blob SHA | **CLOSED — SOURCE VERIFIED** |
| P25-F02 | atomic priority consolidated in `100/101`; D-075…82 still unsigned | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F03 | `102` separates trusted authorization from flag | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F04 | `103` removes terminal self-hash | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F05 | select S1 candidate, `100/101` | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F06 | interrupted LOW invalidates, in-band INVALID candidate decision | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F07 | explicit SELF_TEST guard and RF UNKNOWN treatment | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F08 | normalize batch/casual IDs with stable semantics | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F09 | append-before-virtual-output contract | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F10 | preserve PC_SIM-only and no physical HAL | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F11 | typed result/error v2 migration map | PROPOSED RESOLUTION, OWNER PENDING |
| P25-F12 | unique `P26-T01…28` plus inherited test matrix | PROPOSED RESOLUTION, OWNER PENDING |

**Terminology:** 'Resolved in a draft' is not 'closed under approved baseline'. Only the source-presence question F01 has new objective closure evidence now. At most it is possible to say the remaining findings have proposed dispositions.

## 4. Freeze readiness checks before Task/ is ever created

- Check reviewed git HEAD has not moved. If it has, rebase design discussion on new contents without guessing.
- Owner explicitly accepts contract and exact SIM policy, affected docs and test oracle set; choose `APPROVE`/`AMEND`/`DEFER` and record it in `106`.
- If approved, update legacy documents through reviewed Git edits using expected blob SHA and preserve historical audit trail; do not merge unapproved design candidate as if already authoritative.
- Design freeze is not code test PASS. Only a subsequent **separate** request from owner can authorize any Developer `Task/`, and hardware/flight gates require independent signoff.
