> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `120 (oracles)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `5cc449119735c8807e9237dc433a766d8a356b5c`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — Phase 2.7 Closure Test Oracles & Review Gates

- **ID:** BB-P27-TEST-111 | **Rev:** 0.1 | **Status:** DESIGN TEST CASES / ALL NOT RUN
- **Scope:** PC_SIM_ONLY; no existing software implementation executed or certified.

## 1. Independent G0-A1 design review vs G1 implementation acceptance

A **G0-A1 architecture decision** requires an accepted versioned contract, exact owner-selected policy and scope, reconciled conflicting documents, an evidence plan and approved oracles. It does **not** require claiming a PASS from unimplemented tests. A subsequent **G1 software implementation acceptance** may require actual execution of these tests (under separately authorized Developer work). No G0-A1 document authorizes hardware testing or flight.

## 2. New Phase27 closure vectors (review fixtures, not executed)

| ID | Scenario / review target | Expected result if recommended R1 accepted | Design source |
|---|---|---|---|
| **P27-T01** | DISARMED, same-tick accepted LOW and HIGH different bodies | `E_CONTROL_BATCH_CONFLICT`; no LOW/HIGH progress, output null | `100`, `109` |
| **P27-T02** | DISARMED, duplicate distinct-ID equivalent LOW bodies | one logical LOW, preserve sorted source IDs, no 20ms qualification | `100`, `101` |
| **P27-T03** | ACTIVE, RF LOST + ordinary RESET in one eligible batch | CONTINGENCY, output null; catastrophic+RESET yields FAULT_LATCHED | `100`, `109` |
| **P27-T04** | CONTINGENCY, qualifying LOW #2 + ACK same tick | ACK denied; CONTINGENCY; prior-snapshot rule | `101`, `109` |
| **P27-T05** | CONTINGENCY, ACK later tick with healthy RF + prior qualified LOW + all causes allowlisted | DISARMED, no implicit rearm, consume previous LOW | `101`, `109` |
| **P27-T06** | LOW at 15,000; in-band INVALID at 25,000; LOW at 35,000 | invalid breaks window, later LOW is first observation | `101` |
| **P27-T07** | ACTIVE with empty tick, both RF and input ages <= timeout | S1 bounded prior **authorized** intent, no timestamp refresh | `100`, `101` |
| **P27-T08** | CONTINGENCY includes RF loss + later unresolved scheduler fault; ACK after RF restored | deny ACK until **all** causes recovered/allowlisted; never auto-clear scheduler fault | `101`, `109` |
| **P27-T09** | FAULT_LATCHED, valid ACK and RESET | stays latched, virtual output null | `100`, `101` |
| **P27-T10** | SELF_TEST with RF UNKNOWN but no critical power/scheduler issue | DISARMED with RF UNKNOWN, still refuses new ARM | `101`, `109` |
| **P27-T11** | duplicate event ID at scenario validation vs valid same-tick distinct bodies | typed distinct preflight vs runtime conflict; no ambiguous alias | `85`, `110` |
| **P27-T12** | scenario flag says approved, no external digest allowlist / altered policy byte | preflight `VALIDATION_REJECTED`, zero core ticks | `102`, `110` |
| **P27-T13** | same canonical scenario/policy/engine, different invocation UUID and wall time | identical canonical trace bytes/digest and replay identity | `103`, `110` |
| **P27-T14** | failure appending active tick or terminal | never expose uncommitted active output; incomplete evidence has null complete digest | `103`, `110` |
| **P27-T15** | proposed 5ms step vs different step, identical scenario | different scheduler revision/replay identity; do not assert trace equality across schedules | `102`, `110` |
| **P27-T16** | old `58/68/84` priority tables disagree with approved selected contract after future reconciliation | resolved with explicit supersession anchors and unique canonical revision; NO simultaneous 'current' rules | `105`, `112` |

## 3. Inherited test coverage — count and purpose

| Family | Quantity specified | Coverage intent | Current status |
|---|---:|---|---|
| PC-A | 20 | initial deterministic PC-only core | NOT RUN |
| G1B | 24 | schema, interface, FSM, replay | NOT RUN |
| P22-T | 24 | policy and boundary cases | NOT RUN |
| P23-T | 20 | end-to-end architecture oracles | NOT RUN |
| P24-T | 24 | atomic priority and trust | NOT RUN |
| P25-T | 16 | missing-event, terminal trace | NOT RUN |
| P26-T | 28 | consolidated safety/state/replay | NOT RUN |
| **P27-T** | **16** | decision-closure collisions and governance | **NOT RUN** |

These are *specified test-case inventories*, not 172 proven independent tests. Old and new cases may overlap semantically. A later implementation harness should deduplicate by behavior while preserving original IDs for traceability; do **not** treat duplicate test names as extra evidence or silently discard coverage.

## 4. Exit criteria and severity

| Criterion | Must be true to mark G0-A1 design READY_FOR_OWNER_APPROVAL | Currently |
|---|---|---|
| G01 verified source | exact Git HEAD, 99–106 presence, blob evidence | **YES** at review HEAD |
| G02 scope | PC_SIM_ONLY chosen, no HAL/physical effects | **CANDIDATE / UNSIGNED** |
| G03 semantic policy | D-075…090 decided, own/override precedence unambiguous | **PENDING** |
| G04 numeric policy | versioned exact values + limits accepted | **PENDING** |
| G05 trust/trace | independent approval record, defined bytes/format/error version | **PENDING** |
| G06 historical docs | explicit supersession/patch integration, old tables demoted | **PENDING** |
| G07 test oracle architecture | coverage reviewed, statuses remain NOT RUN before implementation | **SPECIFIED / REVIEW PENDING** |
| G08 owner review | explicit APPROVE/AMEND/DEFER with commit/ref and review evidence | **PENDING** |
| G09 code task | separate downstream authorization required | **NOT GIVEN** |

A defect of type P0 (inconsistent critical safety decision, policy self-approval, trace hash self-reference, ambiguous recovery permissions) blocks G0-A1 design freeze. Noncritical editorial issues may be tracked separately if they cannot change code behavior and the owner explicitly accepts the deferral.

## 5. Review evidence record (currently empty)

```text
Review case: P27-T__
Expected state/reason/output from D-075...090: __
Accepted policy revision/digest: NOT APPROVED
Source HEAD under evaluation: be85c3e28a2ba6891f2bd6199a58fe0ce564f305
Design reviewer and decision: PENDING
Actual executable result (if any): NOT RUN
Failure / discrepancy owner approval: NONE
```
