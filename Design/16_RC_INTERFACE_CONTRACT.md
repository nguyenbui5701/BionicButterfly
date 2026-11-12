# BionicButterfly — V1 RC Command & Safety Interface Contract (Draft)

- **Document ID:** BB-RC-001
- **Version:** 0.3 — 2026-11-12
- **Status:** PROPOSED, must be approved/bench tested before use
- **Architecture:** Physical RC transmitter is the sole in-flight command authority. No autopilot in V1.

## 1. Data flow / trust boundary

```text
handheld TX -- RF air link --> bound RX -- serial frames --> RX adapter
                                                           |
                                              framing/CRC/protocol checks
                                                           |
                                            channel normalization + age
                                                           |
                                            ownership/arming supervisor
                                                           |
                                             bounded wing motion planner
                                                           |
                                             bounded actuator driver
```

**Design rule:** Receiver binding/pairing controls the radio link, but protocol parsing, frame validity, system arming, link quality and local authority still require independent checks. A valid-looking frame from an unapproved local interface cannot become flight owner.

## 2. Candidate physical transport

- UART-based RC receiver output (e.g. ExpressLRS configured for CRSF) is a **candidate**, not a committed component. Confirm voltage, polarity/inversion, UART capability and pin map against the *exact board and receiver* datasheets. ExpressLRS describes CRSF UART control/telemetry wiring at https://www.expresslrs.org/quick-start/receivers/wiring-up/ .
- The input adapter may alternatively support a different *approved* RC protocol, but internal safety logic must not depend on it.
- Do not assume native frame sequence numbers, packet-level encryption, exact update rate or field meanings until receiver protocol implementation is verified.

## 3. Normalized interface (proposed)

```text
ControlCommandV1 {
  schema_version: 1,
  source_id: enum(RC_PRIMARY, BENCH_SIMULATOR),
  receiver_time_monotonic_ms: uint64,    // trusted local receive time
  throttle: float in [0,1],            // calibrated pilot demand
  steering: float in [-1,1],           // direction demand, not a guarantee of yaw
  arm_switch: bool,
  requested_profile: known enum,
  frame_valid: bool,                   // framing + CRC + range + configured mapping
  receiver_link_ok: bool,              // receiver's status, if available
  optional_frame_counter: uint32?,    // only if actual protocol provides it
}
```

Raw inputs are not accepted by motion planner. Missing, non-finite, implausible or malformed frames are rejected. Update `last_valid_frame_ms` **only** upon validated radio control frames. Unrecognized profile/channel map => deny ARM. Timeouts are determined by local receive age, not client-supplied timestamps.

## 4. States, ownership and conflicting commands

- Boot/power-cycle: `DISARMED` and hardware outputs gated.
- ARM: physical pilot intent + neutral throttle + healthy local power + validated recent receiver frames + agreed mechanical/calibration profile.
- ACTIVE_FLAPPING: in-flight radio controls throttle and steering only within constraints.
- Ground disarm: known safe actuation profile; **in-air emergency and link loss must use a separately approved flight-specific response**.
- Flight state: browser commands cannot change motion, arm status, active profile or servo endpoints. Firmware still owns the safety decision.
- Loss of link: receiver no-frame/explicit-failsafe flags handled; strategy, thresholds and transition timing **TBD** by radio bench measurements and G3 hazard review. Fixed 500 ms in existing simulation is only a placeholder, not a flight-safe number.
- Recovery: restored receiver packets must not create uncontrolled restart/command jumps. Pilot-initiated re-authorization policy must be approved before G4.

## 5. Logical outputs

```text
WingControlOutput {
  left_servo_cmd: measured-calibrated range,
  right_servo_cmd: measured-calibrated range,
  allow_output: derived exclusively from central supervisor,
  state: DISARMED | ARMED | ACTIVE_FLAPPING | FAULT | FLIGHT_CONTINGENCY,
  diagnostics: fault and decision metadata
}
```

Motion planner maps normalized pilot demands to time-based wing trajectory. Direction response, servo speed/frequency capability, saturation, aerodynamic effectiveness and trim are **unknown until tested**. Differential motion may not be sufficient for controllable flight; if the experiment proves this, SA revises architecture before any implementation change.

## 6. Verification coverage

- VT-04 malformed/invalid frames; VT-05 ownership; VT-06 freshness; VT-17 RC-only flight authority; VT-18 mapping and arm switch; VT-20 failsafe; VT-22 armed config write denial.
- Test disconnected RX, RX reboot, stale held channel values, mistaken channel reversal, UART electrical mismatch, interference, low battery, brownout and recovery.
- Before G4 obtain measured update period and approved timeout/flight fallback; record chosen protocol version and physical test evidence.

## 7. Explicit open items / owner approval

1. Physical RC transmitter + receiver model.
2. Channel map and safety switch choices.
3. Choice of grounded bench vs actual in-air link-loss and battery contingency.
4. Maximum RC command age and acceptable loss/latency (from measured data).
5. RF/site plan and pilot test protocol.

**State:** all specific numeric settings, wiring and flight contingency are NOT APPROVED.

## 8. Physical interface overlay (v0.2 — PROPOSED)

- Candidate XIAO D7(GPIO20) receiver-to-MCU RX; D6(GPIO21) MCU-to-receiver TX; check actual UART assignment, receiver logic level and boot-time logging before approval. See [`23_PINOUT_AND_SIGNAL_CONTRACT.md`](23_PINOUT_AND_SIGNAL_CONTRACT.md).
- RC receiver remains sole in-flight owner. Electrical validity, fresh frames, explicit failsafe status and measured link loss are **separate** checks.
- Do not use servo power isolation as a default in-air link-loss response. See [`25_ELECTRICAL_HAZARD_REVIEW.md`](25_ELECTRICAL_HAZARD_REVIEW.md).

*Changelog v0.2: referenced electrical pin map and flight-vs-bench stop distinction. No numeric failsafe accepted.*

## 9. Canonical receiver health and safety integration (v0.3 — PROPOSED)

- Separate **valid UART control frame** from **confirmed healthy RF link**. A UART packet may arrive while the receiver is holding previous pilot channels or independently reporting failsafe. Neither an updating timestamp nor a stable RC value alone proves RF health. Exact behavior must be measured with the selected receiver firmware.
- `optional_frame_counter` remains truly optional. CRSF standard channel frames are **not assumed** to provide a trustworthy per-frame sequence; an internal monotonic event ID is a log counter, **not** a transport anti-replay proof.
- Revise conceptual output to carry independent `rf_link ∈ {HEALTHY,LOST,UNKNOWN}`, `failsafe_indicated ∈ {TRUE,FALSE,UNKNOWN}` and verified local `ingress_at_monotonic_us`. UNKNOWN blocks **new arming**; airborne contingency remains unresolved until qualified.
- Treat browser calibration as **DISARMED bench only**; no browser-initiated flight takeover, arm, OTA or servo envelope changes.
- Source/receiver health and in-air contingency are specified in `27_SAFETY_AND_FLIGHT_STATE_MACHINE.md`; common types and scheduling in `28_FIRMWARE_MODULE_AND_TIMING_CONTRACT.md`; scenarios IT-01/02/05/06 in `29_REQUIREMENTS_INTEGRATION_TRACEABILITY.md`.

*Changelog v0.3: RF/serial freshness split; prohibit assumed RC sequence; clarify bench/web role.*

## 10. Pilot intent and channel adapter refinement (v0.4 — PROPOSED)

`32_RC_PILOT_CONTROL_MAPPING.md` is the current **candidate** channel assignment: CH1 steering, CH3 flap, CH5 explicit arm-intent, CH6 optional (disarmed-only) rate selection. CH2/CH4 are unassigned rather than fictitious attitude-control channels. Every physical TX/EdgeTX mix/ELRS switch mode must be verified using actual model/channel monitor; raw protocol numbers cannot be assumed from the handheld's labeling.

The physical radio's arming state does not replace firmware `ARM_CHECK`. A channel map must carry TX model, ELRS/RX firmware version and switch mode, measured min/center/max/reversal, checksum, profile ID and evidence. No arm without observed disarmed switch position after boot then a fresh valid edge, healthy RF evidence and power/calibration guards. Disarmed-only profile changes are the V1 default. Unknown RF status denies new arm; no in-air fallback is approved.

Official references: https://www.expresslrs.org/software/switch-config/ ; https://www.expresslrs.org/quick-start/transmitters/tx-prep/ ; https://manual.edgetx.org/color-radios/model-settings . Tests `PX-01...PX-20` in `35` supplement VT/IT matrices; all remain NOT RUN.
