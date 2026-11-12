> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `117 (input/result-error v2), 115 (tick/health)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `833ccfcc0d976cee9504d080b1e12461e9b5c51d`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — Phase 2.1 Canonical SIM Schemas, Units & Errors

> **Phase 2.4 review note (2026-11-12):** See the candidate corrective addendum at the end and `84–90` before treating older priority/approval text as normative. **Pending owner approval; not code or flight authorization.**

- **ID:** BB-G0A-DATA-057 · **Rev:** 0.2 · **Date:** 2026-11-12
- **Status:** PROPOSED, NOT PRODUCTION SCHEMA / G0-A1 DESIGN ONLY
- **Related:** `16`, `27–28`, `32–33`, `49`, `51`, `56`, `58–64`.

## 1. Authoritative type and value conventions

- External scenario representation: **UTF-8 JSON**, schema version integer `1`. Avoid YAML parser ambiguity, implicit timestamps and hidden defaults in the *candidate frozen contract*. The YAML snippet in `51` is **illustrative legacy**, superseded for the eventual G0-A1 review if the owner approves this JSON decision.
- Time: `event_at_us` and `clock_us` are nonnegative integer microseconds from scenario start. Use a monotonic clock. A simulation restart is an explicit new run with a new run ID; do not model clock wrap as a silent backward jump.
- Units: `flap_demand ∈ [0,1]`, `steering_demand ∈ [-1,1]`, `left_virtual/right_virtual ∈ [0,1]`. These are *dimensionless requested effort*, not servo angle, electrical PWM, lift, RPM, throttle percentage or actual motion.
- Numeric values: any NaN/±Infinity, invalid type, nonintegral timestamp, overflow, negative timestamp or out-of-range channel is rejected **without implicit clamp at ingress**. Normalized mixer output may be bounded by a separately logged envelope gate.
- Radio: `rf_health = HEALTHY | LOST | UNKNOWN` and `rf_provenance = INJECTED_SIM`; `uart_frame_status = VALID | INVALID | NONE`. A valid simulated UART frame is not proof of actual physical RF health.
- Actuator/flight observability: `measured_wing_angle_deg`, `measured_airspeed`, `measured_lift_N`, `airborne_status` are absent or `null`/`UNKNOWN` **by design** in host only. Cannot be silently synthesized.
- Revision identifiers are opaque *nonempty* strings; reject unknown or mixed revision references. For trace equality, canonical JSON sorts object keys and uses integer times and fixed decimal representation for finite numbers.

## 2. Candidate wire/message schemas (structural design, not implementation)

```json
{
  "schema_version": 1,
  "scenario_id": "sim_loss_after_arm_v1",
  "context": "PC_SIM",
  "provenance": "SIM_ONLY",
  "config_id": "sim-only-c0-v1",
  "clock": { "start_us": 0, "step_us": 5000 },
  "events": [
    { "event_id": "e001", "event_at_us": 0, "type": "BOOT", "payload": {} },
    { "event_id": "e002", "event_at_us": 5000, "type": "SIM_RF_STATUS", "payload": { "rf_health": "HEALTHY", "rf_provenance": "INJECTED_SIM" } },
    { "event_id": "e003", "event_at_us": 10000, "type": "SIM_CONTROL_FRAME", "payload": { "uart_frame_status": "VALID", "flap_demand": 0, "steering_demand": 0, "arm_switch": false, "map_revision": "sim-map-v1" } },
    { "event_id": "e004", "event_at_us": 15000, "type": "SIM_CONTROL_FRAME", "payload": { "uart_frame_status": "VALID", "flap_demand": 0, "steering_demand": 0, "arm_switch": true, "map_revision": "sim-map-v1" } },
    { "event_id": "e005", "event_at_us": 20000, "type": "SIM_CONTROL_FRAME", "payload": { "uart_frame_status": "VALID", "flap_demand": 0.2, "steering_demand": 0, "arm_switch": true, "map_revision": "sim-map-v1" } },
    { "event_id": "e006", "event_at_us": 25000, "type": "SIM_RF_STATUS", "payload": { "rf_health": "LOST", "rf_provenance": "INJECTED_SIM" } }
  ]
}
```

**Important:** This is a **schema illustration**. Arming requires a *configuration-dependent* qualification window and a verified transition; the events at 15000/20000 µs do not guarantee that the system became `ACTUATION_ACTIVE`. The host must log an explicit DENIED/PENDING/ACCEPTED decision. A simulated RF-loss transition may inhibit **virtual** output; it does not specify physical servo action.

### 2.1 Logical observations

```text
SimControlObservationV1 {
  event_id: nonempty string;
  source: SIMULATOR;                   // never RC_PRIMARY in host composition
  scenario_provenance: SIM_ONLY;
  event_at_us: u64;
  uart_frame_status: VALID|INVALID|NONE;
  rf_health: HEALTHY|LOST|UNKNOWN;     // current injected SIM state, independent of UART
  rf_provenance: INJECTED_SIM;
  failsafe_indicated: TRUE|FALSE|UNKNOWN;
  flap_demand?: finite float in [0,1];
  steering_demand?: finite float in [-1,1];
  arm_switch?: bool;
  map_revision?: string;
  optional_transport_seq?: u64;       // not required and never forged for CRSF
}
```

`last_valid_control_frame_us` is updated only on an accepted valid full control frame **from a recognized candidate simulation source during DISARMED/ARM_CHECK, or from the current authorized simulation source when armed**. This distinction permits first-time arming while the initial owner is `NONE`. RF-health-only events, invalid/malformed control frames, telemetry, unknown sources and redundant UI status do not advance that timestamp. Authority can only be granted by the separate supervisor guard; updating the candidate frame timestamp alone never grants ownership. RF link health is a separate observation and may be `UNKNOWN` while serial messages continue. An injected healthy RF status can qualify **only simulated** arming.

### 2.2 Decision and trace

```text
SafetyDecisionV1 {
  eval_at_us: u64;
  state: BOOT|SELF_TEST|DISARMED|ARM_CHECK|ARMED_IDLE|
         ACTUATION_ACTIVE|CONTINGENCY|FAULT_LATCHED;
  owner: NONE|SIMULATOR;
  context: PC_SIM;                 // fixed by host composition, not user payload
  virtual_motion_allowed: bool;
  fault_codes: sorted list<ErrorCode>;
  reason_codes: sorted list<ReasonCode>;
  physical_airborne_state: UNKNOWN;
  policy_revision: string;
}
VirtualWingCommandV1 {
  eval_at_us: u64;
  requested_flap: finite float;
  requested_steer: finite float;
  left_virtual: finite float in [0,1];
  right_virtual: finite float in [0,1];
  limiting_reason?: ReasonCode;
  command_provenance: SIM_ONLY;
}
TraceEventV1 {
  run_id: string; event_index: u64; eval_at_us: u64; type: known enum;
  event_id?: string; source: SIMULATOR|SYSTEM;
  state_before: SafetyState; state_after: SafetyState;
  reason_codes: sorted list; virtual_outputs?: VirtualWingCommandV1;
  config_digest: string; input_digest: string;
}
```

## 3. Typed reason and error registry

| Code | Kind | When emitted | Required response |
|---|---|---|---|
| `E_SCHEMA_VERSION` | input reject | unknown schema | reject scenario / no motion |
| `E_CONTEXT_DENIED` | security | BENCH, RESTRAINED or FLIGHT context requested | deny request, immutable host PC_SIM |
| `E_BAD_EVENT_TIME` | input reject | negative/noninteger/overflow/backward time | reject scenario or specific event before execution |
| `E_EVENT_ID_CONFLICT` | input reject | duplicate ID or same-owner contradictory frames at one timestamp | reject conflicting batch, no owner change |
| `E_FRAME_INVALID` | input reject | bad finite/range/schema or invalid frame status | reject, no freshness refresh |
| `E_RF_NOT_HEALTHY` | arm denial | LOST or UNKNOWN RF, or invalid provenance | no new ARM |
| `E_FRAME_STALE` | safety | age exceeds configured SIM_ONLY threshold | revoke fresh intent; host contingency if armed |
| `E_ARM_EDGE_ABSENT` | arm denial | arm held high at startup/recovery | remain DISARMED |
| `E_ARM_PRECONDITION` | arm denial | throttle/steer/config not qualified | remain DISARMED, show specific failing field |
| `E_OWNER_DENIED` | security | source mismatch or UI tries to take over | reject without motion |
| `E_CONFIG_LOCKED` | mutation denial | profile/config update while armed | atomic deny, no modification |
| `E_PROFILE_INVALID` | config | corrupted or non-SIM profile | deny arm/output; error recorded |
| `E_NUMERIC_INVALID` | output safety | nonfinite result or invalid envelope | fault/latch virtual output disabled |
| `E_INPUT_OVERFLOW` | resource | queue/trace/budget exceeded | terminate failed simulation with deny result |
| `E_CONFLICT_PRIORITY` | informational | simultaneous disarm, fault and arm request | deterministic fault/disarm priority |
| `E_SIM_FAULT` | simulation | injected brownout/scheduler fault | host contingency / latch as specified by `58` |

Reason codes must be stable machine-readable enums. Error strings can be localized in a UI but **do not form the API contract**. Reject unknown event types and additional actuator-target fields in scenario input, not merely ignore them.

## 4. Versioning, privacy, evidence

- Semantic change to arming, ordering, scope, normalization or enum meaning ⇒ **schema/contract revision with migration and test update**; do not silently reinterpret version 1.
- Store no Wi-Fi credentials, actual radio binding secrets, personal pilot names or precise location in canonical trace examples. A future hardware log security policy is separate.
- Hash the **canonical input and config**; a display screenshot or a claimed PASS cannot replace a replayable event trace. `64` specifies freeze evidence.
- This is a draft schema. A formal machine-readable JSON Schema should only be included in a future approved implementation task, not forged as already validated software.

## Phase 2.4 authoritative-candidate error compatibility addendum (rev 0.2)

**Historical clarification:** v0.1 `E_EVENT_ID_CONFLICT` in §3 conflates two separate errors. **If/when owner approves** the new `85_HOST_SCHEMA_ERROR_COMPATIBILITY_V2_CANDIDATE.md`, keep scenario input schema v1 but choose result/error contract **v2**, with `E_DUPLICATE_EVENT_ID` for global preflight duplication and `E_CONTROL_BATCH_CONFLICT` for distinct same-tick valid controls. No code/consumer has been migrated. Prior `E_EVENT_ID_CONFLICT` remains historical until that decision. For same-tick atomic rules use `84`; cases `86`.
