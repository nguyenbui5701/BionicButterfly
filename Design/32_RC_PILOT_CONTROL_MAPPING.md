# BionicButterfly — V1 Handheld RC Pilot Control Mapping

- **Document ID:** BB-RC-032 | **Version:** 0.1 | **Date:** 2026-11-12
- **Status:** **PROPOSED / NOT HARDWARE-VALIDATED**; SA owner; no physical flight authorization.
- **Scope:** V1 powered free flight with pilot-held radio; V2 autonomy excluded. Target board/receiver/radio and airframe are not selected.
- **Related:** `02_V1_REQUIREMENTS.md` FR-002, FR-005–008, FR-017–020, FR-022; `05_UI_UX_DESIGN.md`, `16_RC_INTERFACE_CONTRACT.md`, `27_SAFETY_AND_FLIGHT_STATE_MACHINE.md`, `28_FIRMWARE_MODULE_AND_TIMING_CONTRACT.md`, `33`, `34`, `35`.

## 1. Operator intent vs aircraft behavior

**Pilot control is NOT an attitude controller.** Until restrained testing establishes otherwise, our 2-servo design accepts only: (a) requested *common wing motion intensity* and (b) requested *left/right differential*. Neither maps to guaranteed thrust, altitude, yaw, heading, pitch, roll or hover. Direction sign must be measured on the exact airframe. An unused right-stick axis must not silently enable a nonexistent pitch actuator. Any later IMU-assisted attitude stabilization requires a separate design review; it is not autonomous V2 by itself.

```
Physical TX controls -> EdgeTX Inputs/Mixes/Outputs -> ELRS RF transport
                   -> receiver CRSF/UART (or approved alternative)
                   -> integrity and RF/link evidence -> explicit channel map
                   -> normalization, range, freshness -> pilot intent
                   -> AuthorityManager + SafetySupervisor -> planner/limits/HAL
```

## 2. Candidate *logical* handheld layout (Mode 2 style, not approved)

```
 [LEFT GIMBAL]                            [RIGHT GIMBAL]
   up/down: FLAP DEMAND                     left/right: STEER DEMAND
   left/right: UNASSIGNED                  up/down: UNASSIGNED

 [SW-ARM] deliberate 2-position physical switch (DISARM / REQUEST ARM)
 [SW-RATE] optional LOW / NORMAL profile selector (read-only in flight until proven)
 [SW-EXTRA] reserved; no flight E-stop output until flight-specific policy approved
```

Mode 2 names only describe a human-interface **proposal**; actual radios use configurable channel order. Never infer EdgeTX AETR/TAER based solely on stick label. The user can choose a different ergonomic layout after G1 simulator validation, but an approved mapping revision is mandatory.

## 3. Canonical candidate channel-to-function map

| Logical slot | Candidate air-link channel | Input on TX | Semantics | Guard | State |
|---|---|---|---|---|---|
| `STEER` | CH1 | Right stick horizontal | signed `[-1,+1]`; center requested neutral | center/calibration + direction sign must be tested on rig | PROPOSED |
| `RESERVED_PITCH` | CH2 | Right stick vertical | no effect; ignored/reported if moved | no hidden surface/control axis | RESERVED |
| `FLAP_DEMAND` | CH3 | Left stick vertical | `[0,1]`; minimum is safe **arming neutral**, not confirmed physical wing stop | min-endpoint calibration and deadband TBD | PROPOSED |
| `RESERVED_YAW` | CH4 | Left stick horizontal | no effect | do not pretend yaw control | RESERVED |
| `ARM_INTENT` | CH5 (AUX1) | 2-position switch | low = disarm, high = request arm | radio-specific arming mechanism and firmware arming **both** verified | PROPOSED |
| `RATE_SELECTOR` | CH6 (AUX2) | optional switch | selectable *pre-qualified* rate/profile ID | disarmed-only for V1 until safe in-flight transitions demonstrated | PROPOSED |
| `SPARE` | CH7+ | optional | no actuator authority | deny unknown or spoofed codes | RESERVED |

**Not an assertion about the receiver.** For ELRS v3/default-style arming, CH5/AUX1 has special radio-link semantics; ELRS v4 adds an alternative "Arm using Switch" configuration. A chosen TX/RX/ELRS mode must be documented and tested, including CH5 behavior; for a v4 configuration where RF arm uses a separate switch, the firmware must STILL receive a verified explicit arm-intent channel. Never infer it from RF connection alone. Sources: https://www.expresslrs.org/software/switch-config/ and https://www.expresslrs.org/quick-start/transmitters/tx-prep/ .

## 4. Mapping config is explicit and versioned

```text
RcChannelMapV1 {
  schema_version: 1
  tx_model_id: string                 // human-verified model identity; not crypto identity
  tx_firmware_version: string
  rf_system_and_version: string       // e.g. specific ELRS version and switch mode
  rx_model_and_firmware: string
  transport_protocol: string          // verified on real board
  channels: { steer: index, throttle: index, arm: index, optional_rate: index? }
  per_axis: { min_raw, center_or_low_raw, max_raw, reversed, deadband, invalid_zone }
  arm_values: { disarmed_class, armed_class }
  mapping_revision: string
  calibration_evidence_id: string
}
```

All numeric raw thresholds and reversal flags are TBD and require measured transmitter channel monitor + decoded receiver bench samples. Config must reject duplicate conflicting channel assignments (e.g. `ARM_INTENT` sharing `FLAP_DEMAND`) or missing mandatory values. In flight, config is immutable and only the active approved mapping revision can be used. A mismatched TX model/receiver/map invalidates arming.

## 5. Arm/disarm semantics — safety critical

1. **Power-on:** outputs inhibited; radio ARM high at boot is *not* an arm request.
2. **Recognition:** require verified link status, known config and valid channel samples. Observe a genuine DISARMED position after startup/reset (not inferred from a held high).
3. **Explicit edge:** only a verified low-to-high transition may request ARM. Qualification requires measured arm-stability interval, throttle-minimum, steering-neutral (proposal), safe power/actuator state and appropriate operation context.
4. **Armed idle:** `ARMED_IDLE`/legacy `GROUND_ARMED` means authorized idle, **not proof aircraft rests on ground**. Qualified demand initiates wing actuation.
5. **Disarm:** highest pilot command priority in supervisor, but the *physical in-flight actuator response* is unresolved. Bench-safe stop and airborne contingency are separate policies.
6. **Link recovery, model swap, reset:** never auto re-arm or re-apply stale non-neutral demand; require a deliberate full disarm/arm sequence when safe and explicitly approved.

**Dual arming:** ELRS transmitter-level arm logic can influence link behavior; firmware local arming is an independent gate. Either being "armed" alone is insufficient permission to actuate.

## 6. Input shaping and mixing — trial-only models

- `flap_demand = clamp01(calibrated_low_to_high(raw))`. A zero command is *pilot intention*, not a guaranteed servo pulse/stop policy.
- `steer_demand = clip(calibrated_signed_center(raw), -1,+1)`. Deadband, expo and output direction remain **hardware-calibrated design parameters**, not radio defaults.
- At planner level use a bounded conceptual differential: `left_effort = common(u) + d(u,s)`, `right_effort = common(u) - d(u,s)` then pass per-side mechanical envelope, slew limits and saturation. `d(0,s)` should not accidentally start flapping from zero request (candidate invariant; actual linkage tests needed).
- Under saturation, prefer coherent common/differential reduction rather than independently clipping one side, because hard clipping can invert the intended turn. The exact mixer and priority require G1 simulation and G3 moment evidence.
- Rates/flight curves, trim, servo endpoints and frequency must not be freely tuned from radio midair. A flight-validated selected profile may eventually exist, but none is approved now.
- Profile request from an unknown switch state/invalid channel cannot arm or alter active outputs.

## 7. RF health is NOT frame freshness

Track distinct `serial_frame_integrity`, `last_valid_serial_frame_at`, `rf_link` (`HEALTHY/LOST/UNKNOWN`), `failsafe_indicated` (`TRUE/FALSE/UNKNOWN`), and optional receiver link statistics with actual provenance. A receiver might stream held values when TX RF is lost. Therefore **fresh UART frames alone never establish fresh pilot control**. New arming requires independently verified RF health; `UNKNOWN` is a blocker, not healthy by default. Numeric timeouts are G2-measured, never imported from a demo firmware's 500 ms placeholder.

## 8. Control configuration/owner decision gates

| ID | Owner/SA must decide | Current proposal | Blocker? |
|---|---|---|---|
| MAP-01 | specific radio/TX/receiver/firmware | ELRS CRSF UART candidate | blocks G0-B exact wiring and G2 |
| MAP-02 | stick layout | Mode-2-style left throttle, right steering | blocks mapping freeze |
| MAP-03 | explicit arm mechanism | dedicated switch, verified CH5 default, plus local gate | blocks G2 arm testing |
| MAP-04 | whether rate switch works in flight | **disable in-flight profile change by default** | blocks rate switching, not G1 |
| MAP-05 | response to in-air disarm/critical link | **UNRESOLVED: G4 NO-GO** | blocks G4 |
| MAP-06 | controlled steering sign/magnitude | measure on rig and then low-risk trials | blocks G4 |

**Design status:** no flight channel map is approved; no servo arm/pulse/timing default in this file is ready to flash.
