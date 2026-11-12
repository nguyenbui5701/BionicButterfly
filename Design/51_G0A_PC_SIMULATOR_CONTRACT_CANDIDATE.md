# BionicButterfly — G0-A Host-only Simulator Contract Candidate

- **Document ID:** BB-G0A-051 · **Version:** 0.1 · **Date:** 2026-11-12
- **Status:** **DESIGN CANDIDATE, NOT OWNER-APPROVED, NOT A DEVELOPER TASK**
- **Goal:** design a deterministic, testable core **without** enabling physical actuators or claiming aerodynamic flight fidelity.
- **Dependencies:** owner-confirmed V1 RC-first intent; `02`,`16`,`27`,`28`,`29`,`30`,`32–36`,`37–41`; conflict list `49`.

## 1. Allowed and forbidden scope for eventual bounded G0-A1 approval

**Allowed design concepts:** typed validation, authority selection, arm-switch edge semantics, state transitions, simulated faults, virtual wing-command mixer with bounded outputs, virtual-time scheduler, simulated telemetry and event log, reproducible scenario replay.

**Explicitly excluded:** ESP32 GPIO setup, UART flashing, driving powered servos, calibration of real PWM pulse values, reading real LiPo rails, actual flight tests, internet-dependent control, closed-loop aircraft stabilization, dynamics predicted from unmeasured aerodynamic coefficients. Do not import reference firmware code without license/provenance approval.

The current document is a **specification**. No implementation source file, `Task/` file or PR is created by this phase.

## 2. Canonical abstractions (proposed)

```text
Clock { monotonic_us(): u64 }                         // injected, not wall clock
OperationContext = PC_SIM | BENCH_SERVO | RESTRAINED | FLIGHT_APPROVED
Authority = NONE | SIMULATOR | BENCH_LOCAL | RC_PRIMARY
RfHealth = HEALTHY | LOST | UNKNOWN
FrameValidity = VALID | INVALID
SafetyState = BOOT | SELF_TEST | DISARMED | ARM_CHECK | ARMED_IDLE |
              ACTUATION_ACTIVE | CONTINGENCY | FAULT_LATCHED
```

**Access rule:** In a **PC simulator build** `OperationContext` may only be `PC_SIM`; attempts to request other contexts are recorded and denied by policy. Merely selecting `FLIGHT_APPROVED` via config, profile name or UI cannot grant any authority. An actual hardware build would require a separately reviewed authorization mechanism and board-specific gating.

```text
ReceiverObservationV1 {
  schema_version; trusted_receive_time_us; source
  transport_frame_integrity; rf_health; failsafe_indicated
  normalized_flap_demand; normalized_steer_demand; arm_switch
  profile_id; map_revision; optional_transport_counter
}
SafetyDecisionV1 {
  time_us; state; owner; approved_context; fault_codes
  allow_virtual_motion; reason; recovery_interlock
}
VirtualWingCommandV1 {
  time_us; left_normalized; right_normalized
  was_limited; limit_reason; model_tag: SIM_ONLY
}
```

Unmeasured fields remain `UNKNOWN`/`null`, never converted to zero or HEALTHY. A protocol sequence is optional; a locally allocated event counter is for logging, not RF replay proof. In the simulator, RF health may be **injected as a separate test variable**, but must not be misrepresented as a hardware RF report.

## 3. Logical precedence and transitions

- **Cold boot/reset:** state `BOOT→SELF_TEST→DISARMED` when virtual config valid; otherwise `FAULT_LATCHED`. Output is **virtual** and inhibited; this is not evidence that a physical GPIO would be safe on boot.
- **Arming:** a prior observed DISARMED switch position then a fresh LOW→HIGH edge, neutral flap, valid map/profile, known healthy source and no blocking fault. For simulator-only tests a separately injected `RF_HEALTHY_SIM` tag may satisfy a simulated guard, not a real receiver's health.
- **Active:** only owned, validated input may change requests. Nonfinite, out-of-range, stale or wrong-owner data does not renew freshness or actuate.
- **Disarm priority:** the virtual state machine prioritizes pilot intent/fault and records denial reason; **in-air physical stop behavior is deliberately unspecified**.
- **Fault recovery:** restored healthy frames alone do not auto-rearm. Require explicit disarm/ack and new deliberate arm qualification.
- **State names:** `ARMED_IDLE` is a logical permission state; `ACTUATION_ACTIVE` is not proof the aircraft is physically airborne.

## 4. Virtual-time and motion contracts

- Virtual time must be strictly monotonic under normal run; tests can inject wrap/reboot/reordering to validate fail-closed behavior. Do not use wall time or timer sleeps to calculate motion phase.
- Example testing periods (`5ms` supervisor, `20ms` nominal servo carrier, `500ms` provisional link loss) are **SIM_ONLY** numbers taken from earlier design hypotheses. The exact harness must keep them configurable and **must not export them into a flight profile**.
- A normalized mixer may be defined as `u_c=(u_L+u_R)/2`, `u_d=(u_R-u_L)/2`. Pilot flap/steer map to requested normalized output with clipping and event reasons. There is **no requirement** to predict actual `Fz`, `Mx`, `My`, `Mz` or altitude at G0-A.
- Mode profile IDs may define wave-shape preferences only within virtual envelopes; simulation does not select servo pulse widths, electrical speed, CG or safe flight frequency.

## 5. Virtual scenario file (illustrative data shape)

```yaml
schema_version: 1
scenario_id: "sim_only_arm_linkloss_001"
context: "PC_SIM"
model_tag: "SIM_ONLY"
clock: {start_us: 0, step_us: 5000}
configuration: {revision: "sim-model-v1", no_physical_outputs: true}
events:
  - {at_us: 0, type: "BOOT"}
  - {at_us: 10000, type: "SWITCH_LOW"}
  - {at_us: 20000, type: "VALID_SIM_FRAME", rf_health: "HEALTHY"}
  - {at_us: 30000, type: "SWITCH_HIGH", flap: 0.0, steer: 0.0}
  - {at_us: 50000, type: "FLAP_REQUEST", flap: 0.2, steer: 0.0}
  - {at_us: 100000, type: "RF_HEALTH", rf_health: "LOST"}
expected:
  - "no implicit autoarm on boot"
  - "fault/contingency event recorded after injected RF loss"
  - "no automatic rearm on later RF recovery"
```

This YAML is **an illustration, not validated production schema or physical control instruction**. Event timing and RF-loss transition must be explicitly agreed; a simulated short trace cannot infer a safe in-air response.

## 6. Host-only invariant registry (proposed)

| Invariant | Must hold in every virtual run | Tests |
|---|---|---|
| `SIM-INV-01` | boot, restart and invalid configuration do not auto-arm | PC-A01/02 |
| `SIM-INV-02` | arming requires deliberate switch edge after known disarmed observation | PC-A03/04 |
| `SIM-INV-03` | exactly one validated command owner may affect virtual motion | PC-A05/06 |
| `SIM-INV-04` | unknown RF health, stale or malformed frames do not satisfy new arming | PC-A07–09 |
| `SIM-INV-05` | outputs always finite and within declared **virtual** envelope | PC-A10/11 |
| `SIM-INV-06` | no config/profile/write/OTA mutation while armed | PC-A12/13 |
| `SIM-INV-07` | replay is deterministic under fixed virtual time and input | PC-A14/15 |
| `SIM-INV-08` | switching simulated context to hardware/flight denied | PC-A16 |
| `SIM-INV-09` | loss/recovery event never resumes armed activity without requalification | PC-A17/18 |
| `SIM-INV-10` | physical force, measured servo wing angle or real airborne state never fabricated | PC-A19/20 |

All are **expected properties, NOT TESTED**. Add measurable pass/fail definitions to `52` and gain owner approval *before* implementation tasks.

## 7. Approvals to request later

- Choice of stable API shape, virtual scenario format, finite and timeout policies, state naming, logging fields, and sim-only default values.
- Agreement that `G0-A1` is a **narrow design freeze** and excludes hardware/airworthiness verification.
- Explicit owner choice whether to *begin coding later*; approving this concept alone does not create a task.
