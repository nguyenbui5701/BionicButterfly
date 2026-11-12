> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `115 (hazard before RESET and S1)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `2cc1f50a50437e7c820c74909e374237906e1ce3`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — Phase 2.4 G0-A1 Normative Safety & Atomic Event Semantics (Candidate)

- **ID:** BB-P24-NORM-084 · **Rev:** 0.1 · **Date:** 2026-11-12 · **Owner:** Solution Architect
- **Status:** **PROPOSED, UNSIGNED**; normative **only if explicitly approved for G0-A1 PC-only**.
- **Baseline:** Git `main` **`16d5054ea951b2e52e90c7f81ea2767a7ba82b92`**; previous candidate documents `57–61`, `67–71`, `76–83`.
- **Priority if approved:** for the narrow **PC_SIM-only** scope, this document supersedes conflicting interpretations of event ordering/arming/recovery in `57`, `58`, `59`, `68`, `78`. Numeric values continue to come from an independently owner-approved revision of `67`, not from sample JSON.
- **Not covered:** ESP32 drivers, real receiver, real servo PWM, free flight, physical in-air failsafe, G0-B, G4. V1 actual RC flight remains the product goal; V2 autopilot deferred.

## 1. Single observable transaction per evaluation tick

Scheduler is a **single fixed 5,000 µs candidate SIM_ONLY tick** at `T_k=k×step_us`. Its value is **not yet approved** and has no hardware timing authority. For `k>0`, eligible events have `T_(k-1) < event_at_us <= T_k`; for k=0, only `event_at_us=0` is eligible. Input event timestamps are never rounded or overwritten; `eval_at_us` is the time a **complete atomic batch** is committed. An event at time 4,999 µs is evaluated at 5,000 µs.

Preflight rejects invalid JSON, disallowed fields/contexts, duplicate global event IDs, invalid timestamps and unavailable approved policy **before creating an enabled virtual sink**. In-band syntactically valid `uart_frame_status=INVALID` is a **test observation**, not a malformed JSON error.

For every evaluation tick, take one immutable pre-state, compute a normalized batch (no intermediate state or actuation), apply the guards below, commit exactly **one post-state/decision**, compute at most one virtual output and append one normative trace decision. If trace append/quota fails, do **not** report run PASS, inhibit further virtual outputs and report partial evidence.

## 2. Canonical normalization order (intentionally resolves P23-F01/F02/F05/F06/F10)

1. **Identify all injected catastrophes, RESET, independent RF health updates, critical power events and config writes**, retaining their original event IDs and times. If `RF_LOST` and `RF_HEALTHY` appear **in the same tick**, `LOST` wins for this tick; a healthy event in a *later* tick can restore observed health but never auto-arm.
2. **Validate all SIM_CONTROL_FRAME observations together**, before interpreting *any* LOW as disarm or *any* HIGH as ARM. Two semantically distinct valid control payloads within one tick are an **entire control-batch conflict**; accepted-control component = none, no arm/disarm from it, and **no control timestamp refresh**. Two equivalent payloads with different unique IDs count as **one** logical frame; for timestamp semantics choose the latest `event_at_us` for freshness, but one batch counts as only one accepted observation/edge regardless of the number of original events. Preserve all causal IDs for audit.
3. A control frame in a tick with **catastrophic fault, RF LOST/UNKNOWN/expired, critical power fault or RESET** is **not eligible for new LOW qualification, ARM edge or arm-high confirmation**; a serial packet cannot override a failed upstream health gate. Do not count RF health events as RC control frames. Stale input alone cannot produce a trusted new switch observation.
4. Compute **hazard decision and one post-state** from pre-state + normalized batch. There is no instant in-tick output emitted by a momentary ARM that is later revoked in the same batch. Reject runtime unknown source, profile mutation and UI actuation independent of the physical sink (which does not exist).
5. Use event timestamps for minimum LOW/HIGH observation durations and freshness; use `eval_at_us` for commit ordering and trace. At a boundary, `age == timeout` is fresh; `age > timeout` is stale. Exact timestamp and tick separation are both required for distinct arm phases.

## 3. Priority table and explicit state outcome

The priority below decides **SIM virtual state only**. It does not specify how a real airborne robot should physically stop its wings.

| Priority | Effective condition | Result for this tick | Virtual outputs |
|---:|---|---|---|
| 1 | **catastrophic fault**, including same tick RESET | `FAULT_LATCHED`; RESET cannot clear this same-tick fault | inhibited |
| 2 | RESET *without active catastrophe* | if pre-state is `FAULT_LATCHED` remain latched and if pre-state is `CONTINGENCY` remain in contingency (**RESET is not a recovery shortcut**); otherwise revoke arm eligibility and move to `SELF_TEST`. In this narrow contract, only separately qualified ACK can clear a non-catastrophic contingency | inhibited |
| 3 | other critical hazard (RF LOST/UNKNOWN/stale, critical supply/scheduler), including **invalid control batch** if previously armed | if armed/ARM_CHECK/ACTIVE → `CONTINGENCY`; else remain `DISARMED` or latched fault; invalid batch cannot trigger trusted disarm | inhibited |
| 4 | accepted switch LOW with all qualification health guards valid | `DISARMED` from authorized idle/active; advance LOW qualification if already DISARMED; if in `CONTINGENCY`, advance candidate LOW qualification but **retain CONTINGENCY until separately qualified ACK**; if `FAULT_LATCHED`, retain fault latch | inhibited |
| 5 | eligible explicit ACK from `CONTINGENCY` in a **later tick** | requires previously committed qualified LOW, healthy RF/voltage, no active fault; `FAULT_LATCHED` is not ACK-clearable | inhibited |
| 6 | accepted neutral HIGH edge, then validated follow-up HIGH at boundary | `ARM_CHECK` then `ARMED_IDLE` on a **later** confirmed tick | inhibited |
| 7 | fresh accepted demand after already `ARMED_IDLE` | `ACTUATION_ACTIVE`; can request bounded virtual left/right | permitted only with all guards |
| 8 | config write, unowned/UI actuation or non-critical invalid request | deny action, preserve prior authorized state only if health remains qualified | never newly enabled |

**Conflict-specific outcome:** if `LOW+HIGH` arrive as distinct valid control frames in one tick: from `DISARMED` remain `DISARMED`; from `ARM_CHECK`, `ARMED_IDLE` or `ACTUATION_ACTIVE` → `CONTINGENCY`; from `FAULT_LATCHED` remain latched. All such cases have `E_CONTROL_BATCH_CONFLICT`; no frame age, LOW time, HIGH edge or active output advances. This supersedes the old priority #3 (LOW before conflict) in `68`.

**RESET+catastrophe:** record both causes; post-state `FAULT_LATCHED`. In this narrowly scoped G0-A1 proposal, a catastrophic latch is **terminal for the rest of the run**; neither ACK nor a later RESET may clear it. A new separate run can be created after test fixture corrections. This avoids inventing an unmodeled fault-clear stimulus. Any future in-run catastrophic recovery requires a **separately versioned design and tests**. This supersedes reset-first table row in `68`.

## 4. Arming protocol (distinct observations; PC_SIM only)

1. Boot at time zero → `SELF_TEST`, then successful preloaded-policy check → `DISARMED` on next evaluation tick. A high ARM switch held from boot **never** qualifies.
2. At least **two accepted LOW** control observations at distinct ticks, whose original timestamps differ by at least **20,000µs candidate** and whose RF/control health is valid at those ticks, create `low_qualified=true` at the *second* tick commit.
3. A **later tick** with accepted HIGH and neutral commands (`flap<=0.02`, `abs(steer)<=0.05`, **candidate SIM values**) creates a rising edge and `ARM_CHECK`. The HIGH timestamp is recorded. A LOW+HIGH in one tick never does so.
4. At least one **additional** eligible accepted HIGH frame at a later tick with `event_at_us >= high_edge_at_us + 100,000µs candidate`, continuous qualified health and neutral demand enters `ARMED_IDLE`. If high demand appears early or a fault occurs, cancel; an additional fresh LOW sequence is needed.
5. Only a subsequent accepted HIGH with `flap>0.05 candidate`, with no health/config fault, can enter `ACTUATION_ACTIVE`. It produces **dimensionless virtual effort**, not servo pulse/wing angle/lift. A confirming HIGH cannot also be the active-demand frame.
6. An accepted RESET outside `CONTINGENCY`/`FAULT_LATCHED` erases arm eligibility. RF restoration alone, ACK alone or a held HIGH after recovery **never** re-arms.

**ACK ordering:** ACK and the **final qualifying LOW** in one tick shall **not** clear a fault because the qualification was not committed in the previous snapshot. An ACK at a later tick may be accepted only with **previously committed** LOW qualification, independent healthy RF/voltage, no active fault and an allowed recovery reason. A catastrophic fault remains latched until the run ends; generic ACK and in-run RESET may not remove it. No in-run catastrophic-clear event is specified in scenario schema v1. These semantics are host design proposals, **not physical emergency procedures**.

## 5. Observability and fixed boundary

- `context = PC_SIM`, `owner = SIMULATOR`; simulator has no RF, PWM, GPIO, camera, IMU or LiPo hardware access. Scenario payload cannot set `FLIGHT_TEST_APPROVED`, enable device services or change policy trust.
- `airborne_state = UNKNOWN`, `measured_lift_N = null`, `measured_servo_angle = null` unless a separately approved non-G0A interface eventually supplies real instrumentation. Simulated command values are labeled **SIM_ONLY**.
- Scenario configuration and policy are immutable for the full run. `SIM_CONFIG_WRITE` is a denied runtime event even while disarmed.
- An injected `RESET` does not restart the simulation clock; it changes the virtual FSM and is traceable.
- Quantitative timing values in this document illustrate **candidate policy SIM_POLICY_CANDIDATE_22A**; only a signed decision referencing exact policy bytes can make it an approved G0-A1 baseline.

## 6. Test and decision traceability

- **P23-F01/02/04/05/06/10** → `85`, `86` with new `P24-T01…T24` cases.
- **P23-F03/07/08/09** → `85` schema compatibility and `87` replay/trust contract.
- **P23-F12** now **repository identity verified** at the SHA above; see `88`. This only closes repository *access/identity*, not the technical review.
- ADR D-067…D-074 remain pending owner approval; Phase24 D-075…D-082 refine them without silently asserting approval.

**This is a review-ready contract candidate, not a frozen executable policy.** Previous documents are historical context; approval requires reconciliation in `89` and an explicit owner decision.
