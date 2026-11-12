> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `120 (oracles)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `d4b339e8ad7e782b6181737e6abdc396d7632904`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — Phase 2.6 Deterministic Test Oracles and Acceptance Vectors

- **ID:** BB-P26-TEST-104 | **Rev:** 0.1 | **State:** PLANNED; **ALL P26-T01…P26-T28 NOT RUN**.
- **Scope:** proposed host-only PC simulation, not flight hardware. Each vector must be executed only after owner approves a concrete immutable SIM policy & schema. No fixture/expected result here proves a runtime implementation.

## 1. Test fixture conventions

- Tick `step_us=5000`; valid BOOT at 0, `SELF_TEST` at 0, DISARMED at 5000 if no critical power/scheduler issue. Inject RF HEALTHY at 10,000; reference LOW at 15,000 and 35,000; HIGH neutral at 40,000; HIGH neutral confirmation at 140,000; HIGH flap 0.2 at 145,000.
- Original control frame `event_at_us` matters, not rounded evaluation time. An event at `139999` is evaluated at `140000` but fails the 100ms HIGH interval since edge 40000.
- Unless stated otherwise: no power fault, approved matching simulator profile and version (in a future *trusted host*, not the fixture itself), consistent mapping, finite inputs, RF healthy/fresh. All outputs are virtual dimensionless micro-effort when permitted.
- `assertion_result` is a result of an *actual test harness*, not a field the scenario can self-assert. Current written expectations are not executed outcomes.

## 2. Event/state oracles

| ID | Event sequence / mutation | SA-proposed expected state / reason / output |
|---|---|---|
| **P26-T01** | HEAD includes Phase24+25 docs | `P25-F01` source-presence finding CLOSED with commit/blob evidence; no design approval inferred |
| **P26-T02** | baseline sequence until HIGH at 40,000, HIGH at 140,000 and demand 145,000 | `DISARMED→ARM_CHECK→ARMED_IDLE→ACTUATION_ACTIVE`; output on 145,000 only (if policy trusted and healthy) |
| **P26-T03** | control LOW at 15,001 and 35,000 then HIGH at 40,000 | delta 19,999 insufficient, remain DISARMED |
| **P26-T04** | HIGH confirm at 139,999 after edge at 40,000 | original delta 99,999 insufficient, remains ARM_CHECK |
| **P26-T05** | duplicate valid LOW bodies with distinct IDs at same tick | one LOW observation only; no false 20ms series; causal IDs preserved |
| **P26-T06** | LOW+HIGH distinct valid bodies at one tick while DISARMED | `E_CONTROL_BATCH_CONFLICT`; remain DISARMED; no LOW qualification/time refresh |
| **P26-T07** | LOW+HIGH distinct bodies at one tick while ACTIVE | CONTINGENCY, null output; no accepted frame time refresh |
| **P26-T08** | RESET+catastrophe while ACTIVE | FAULT_LATCHED; terminal for run; no output |
| **P26-T09** | RESET+RF LOST while ACTIVE | CONTINGENCY, not SELF_TEST; null output (P26 proposed fix to prior rank order) |
| **P26-T10** | low window, RF LOST, RF HEALTHY then subsequent LOW at later tick | prior LOW window revoked; needs fresh two LOWs |
| **P26-T11** | low window, in-band INVALID frame, then LOW | invalid frame breaks qualification; no accepted time refresh |
| **P26-T12** | low window, accepted HIGH, then LOW | accepted HIGH invalidates previous LOW window; later LOW starts new series |
| **P26-T13** | DISARMED: empty tick, LOW window partially seen, RF remains healthy | no synthetic second LOW; qualification not granted |
| **P26-T14** | ARM_CHECK: no confirming HIGH at 100ms boundary | stay ARM_CHECK while fresh; never arm by elapsed time alone |
| **P26-T15** | ACTIVE: one empty tick with previous intent and RF both fresh | S1: stay ACTIVE, held bounded virtual intent, no control timestamp refresh |
| **P26-T16** | ACTIVE at exact `frame_age==200000`, RF healthy/fresh | S1: still eligible; at next tick `age>200000` => CONTINGENCY and null |
| **P26-T17** | ACTIVE at exact RF age==200000 and control fresh | HEALTHY remains effective; >200000 => UNKNOWN and CONTINGENCY |
| **P26-T18** | ACTIVE: no fresh serial but receiver reports HEALTHY repeatedly | control age still expires and enters CONTINGENCY; RF refresh alone cannot refresh pilot intent |
| **P26-T19** | ACTIVE: serial valid frames arrive while RF LOST | no new accepted intent and null output, even with fresh UART diagnostic timestamp |
| **P26-T20** | final qualifying LOW and ACK same tick while CONTINGENCY | ACK denied using pre-snapshot; remain CONTINGENCY |
| **P26-T21** | ACK next tick after qualified LOW, health restored, recoverable cause on allowlist | DISARMED, output null, consumes LOW qualification; never auto rearm |
| **P26-T22** | ACK after catastrophic FAULT_LATCHED | remain FAULT_LATCHED (new run needed) |
| **P26-T23** | SELF_TEST with RF UNKNOWN, valid policy | can become DISARMED; cannot arm without later healthy RF + LOW series |
| **P26-T24** | SELF_TEST + critical simulated power fault | remain SELF_TEST, no ready/arm; with catastrophe FAULT_LATCHED |
| **P26-T25** | ACTIVE would output but trace append/quota rejects candidate record | no newly exposed output, `FAILED_INCOMPLETE_EVIDENCE`, no complete digest |
| **P26-T26** | same scenario/policy/engine but different runtime UUID/walltime | same normative control bytes and digest |
| **P26-T27** | terminal includes digest or missing LF / modified decision byte | reject noncanonical / detect integrity mismatch; no certified matching full digest |
| **P26-T28** | same scenario has `approved_for_host_execution:true` but no independently approved digest | `VALIDATION_REJECTED`, zero core ticks, no hardware interface accessed |

## 3. Concrete JSON examples (not independently authorized)

`Design/fixtures/P26_ARM_NOMINAL_CANDIDATE.json` is a structurally illustrative sequence for T02; `P26_LOW_INTERRUPTED_INVALID_CANDIDATE.json` covers T11; `P26_CONTROL_BATCH_CONFLICT_CANDIDATE.json` covers T06. The fixture JSONs **do not include** trusted host approval and cannot be run merely because the input text is valid JSON. They intentionally use the source schema example from `57` and are not official JSON Schema proof.

## 4. Strong requirements for any future acceptance harness

- For every test: exact design Git SHA; SHA of approved policy bytes; engine+schema+result contract revision; normalized batch; **expected and actual per-tick state/output**; sorted reason codes; original vs evaluation event times; canonical trace digest or explicit `null`; independent reviewer.
- Include malformed JSON and duplicate IDs in separate **preflight rejection** tests; don't model an invalid JSON byte stream as an in-band serial fault.
- An SA-designed test vector is marked `SPECIFIED/NOT_RUN`. PASS comes only from a later actual executed implementation under independently approved inputs.
- No positive motion measurement, pitch/yaw/roll control, servo or free-flight assertion follows from this matrix.
