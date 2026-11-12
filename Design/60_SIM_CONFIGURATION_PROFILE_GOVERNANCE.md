# BionicButterfly — G0-A1 SIM Configuration, Profile & Mutation Policy

- **ID:** BB-G0A-CFG-060 · **Rev:** 0.1 · **Date:** 2026-11-12
- **Status:** PROPOSED; no real airframe calibration or approved flight profile.
- **Refs:** `16`, `27`, `28`, `33`, `49`, `51`, `56–59`, `61–64`.

## 1. Three layers with distinct authority

| Layer | Example values | Immutable scope rule | Who can change it |
|---|---|---|---|
| **Build composition** | `HOST_ONLY`, `PC_SIM`, `VirtualActuatorSink` | cannot be raised to BENCH/FLIGHT by file, UI or environment variable | future build review, not runtime config |
| **SimPolicyV1** | arm qualification, input-age rule, virtual envelope, fault priority revision | SIM_ONLY numbers; may never be relabeled physical safe limits | authorized design/version change while DISARMED |
| **ScenarioV1** | sequence of simulated RC frames, injected faults, virtual clock steps | untrusted input; no permission to override policy or build type | local scenario author/tester |

A **flight hardware profile** shall not be loadable by the G0-A1 host. `FLIGHT_APPROVED` is neither a user-settable enum in a scenario nor a profile name that grants privileges.

## 2. Proposed configuration record

```json
{
  "schema_version": 1,
  "profile_id": "sim-only-c0-v1",
  "model_tag": "SIM_ONLY",
  "allowed_context": "PC_SIM",
  "board_id": null,
  "physical_servo_limits": null,
  "real_failsafe_policy": null,
  "channel_map_revision": "sim-map-v1",
  "neutral_flap_max": null,
  "neutral_steer_abs_max": null,
  "arm_qualification_us": null,
  "frame_timeout_us": null,
  "virtual_left_range": [0, 1],
  "virtual_right_range": [0, 1],
  "sim_waveform_id": "virtual-sine-v1",
  "policy_revision": "G0A-draft-v1",
  "approved_for_host_execution": false
}
```

`null` placeholders mean the record is **not executable as an approved test profile**. Approval of G0-A1 must populate SIM_ONLY policies (not physical values) with a reviewer and committed revision. If an implementation receives this draft record unchanged, it must refuse arming, not pick vendor defaults.

## 3. Arm qualification and conflict rules

- Fix raw-to-normalized channel maps and switch semantics as **simulated assumptions**. Do not reuse CH5 as immutable truth across real ELRS firmware; actual radio mapping remains G2 evidence.
- Neutral windows, arm hold duration, frame freshness timeout and virtual output thresholds are *safety-critical model parameters* that must be set prior to G0-A1 approval, with test cases around all boundaries.
- A profile update while `ARM_CHECK`, `ARMED_IDLE`, `ACTUATION_ACTIVE`, `CONTINGENCY` or `FAULT_LATCHED` is rejected. Only healthy **DISARMED** and explicit local authorization may accept an update. No runtime hot-swapping sources, arm logic, context or virtual envelope.
- Sim scenario input may request a profile switch for next run, but cannot change the active approved profile inside an armed run. If an event claims config update at same timestamp as fault/ARM, the atomic batch priority and pre-state locking rule must deny any mutation that risks bypassing ARM guards.

## 4. Durable/atomic revision update rules

1. Read/validate candidate `schema_version`, profile hash and `SIM_ONLY` tag.
2. Validate allowed enum values, cross-field invariants (min ≤ max, neutral inside envelope, timeout > 0, no duplicate channel assignments), reasonable bounded numeric values and explicit documented units.
3. Ensure state is stable DISARMED, not a same-timestamp ARM transition; deny if active/unsafe event competing.
4. Commit in one auditable atomic operation or refuse. On crash/interruption, previous approved config remains intact; invalid partial records must not load on next BOOT.
5. Increment revision and log *before/after digest*; replay identity pins to the specific digest. Config write attempts from a viewer/scenario without authority are always rejected.

**Note:** This is a future design contract. No persistent storage or file-based implementation has been created.

## 5. Calibration authority and separation

- Simulation plots commanded left/right **virtual** values only; measured servo angle and physical wing position are `UNAVAILABLE`.
- An actual servo calibration record belongs to G0-B/G2 and must identify board revision, servo ID, wing linkage, safe pulse limits and measured evidence; G0-A1 cannot invent these fields.
- Source changes to wing/mass/CG/servo, IMU or real in-air failsafe need a new non-host design review. No simulated output success can automatically validate them.

## 6. Invariants and negative cases

| ID | Input | Required result |
|---|---|---|
| `CFG-01` | profile tagged `FLIGHT_APPROVED` | reject unsupported context |
| `CFG-02` | `SIM_ONLY` with `real_failsafe_policy` populated | reject physical-policy field |
| `CFG-03` | missing arm qualification or age threshold | deny arming and report config incomplete |
| `CFG-04` | attempted mutation while armed | reject atomically; previous digest remains |
| `CFG-05` | crash while committing simulated profile | old committed config or new complete config; no partial fallback |
| `CFG-06` | duplicate channel index or endpoint reversal unexpectedly | invalid mapping denies ARM |
| `CFG-07` | config update + ARM in same event time | reject update and ARM unless stable pre-state policy explicitly qualifies; never bypass checks |
| `CFG-08` | unknown extra actuator/control field | reject rather than expand control surface |

All tests **NOT RUN**; owner may later choose a narrower, purely in-memory policy for first host-only scope, provided revision/replay and no-mutation properties remain satisfied.
