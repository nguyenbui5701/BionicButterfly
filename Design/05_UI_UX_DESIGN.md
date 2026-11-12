# BionicButterfly — V1 Pilot Controls and Bench UI (Draft)

- **Document ID:** BB-UI-001
- **Version:** 0.1 — 2026-11-12
- **Status:** PROPOSED; owner has confirmed V1 manual RC flight, **not** exact control mapping.
- **Depends on:** `02_V1_REQUIREMENTS.md`, `16_RC_INTERFACE_CONTRACT.md`, `14_V1_VERIFICATION_PLAN.md`

## 1. Interaction surfaces and control authority

**Flight:** Physical RC transmitter is the sole live control owner once armed for flight. No internet/browser/phone dependency for commanding the airframe.

**On ground:** Local web/setup interface may configure calibration, select test profile and display telemetry **only while disarmed**. Simulator UI is educational/test-only and is never the authority for flight decisions.

| Surface | Intended user | Allowed | Disallowed |
|---|---|---|---|
| RC handheld | Pilot | Arm/disarm, throttle, steering, approved mode switch, deliberate emergency request | Unsafe profile edit while armed; bypass safety |
| Local configuration UI | Experimenter | Read firmware/state, upload *validated* profiles while disarmed, inspect logs, simulate faults (PC/bench only) | Claim flight safety, seize flight control, alter active limits while armed |
| PC simulator | SA/Developer/tester | Inject RC-like input/faults, plot wing commands, replay logs | Claim simulated wing angles prove flight capability |

## 2. Candidate handheld RC channel mapping — not fixed

| Physical control | Logical meaning | Safe default / rejection | Notes |
|---|---|---|---|
| Two-position arm switch | ARM/DISARM | Boot always disarmed; explicit neutral-to-arm transition | Avoid accidental stick-based arming |
| Throttle stick | Requested flap effort [0..1] | Must be within calibrated neutral zone before arming | Engineering model is NOT a guaranteed lift map |
| Roll/yaw stick | Directional steering [-1..1] | Center = neutral, movement mapped by measured wing response | Mapping/polarity/trim TBD |
| Optional mode switch | Approved flight profile | Unrecognized mode ignored/rejected | No automatic hover assumption |
| Dedicated emergency action (TBD) | Pilot-requested emergency response | Must use flight-tested policy, not blind stop | Evaluate risk before activation |

**Human factors:** Stick direction and wing response must be validated with the pilot before G4; use visible ARM indicator, a clear preflight checklist, deterministic arming cues, and a distinct ground disarm vs in-flight contingency distinction. Avoid reliance on multi-step phone navigation during flight.

## 3. Simulator & bench UI draft

```text
+------------------------------------------------------------+
| BIONIC BUTTERFLY / BENCH & SIMULATOR / NOT FOR FLIGHT       |
| STATE: DISARMED       RC: CONNECTED (SIM)     FAULT: NONE   |
| Owner: simulated_rc   Frame age: 18 ms       Battery: SIM  |
+------------------------------------------------------------+
| [Arm (gated)] [Disarm] [Reset fault (when safe)]            |
| Throttle  [-------|------] 0..100%                         |
| Steering  [-----|--------] -100..100%                      |
| Approved profile: [bench_sine_v1] (locked when ARMED)       |
+------------------------------------------------------------+
| Left wing angle     /\__ /\__       [plot vs virtual t] |
| Right wing angle    \__/ \__/       [plot vs virtual t] |
| Inputs and safety events | [export CSV] [replay]           |
+------------------------------------------------------------+
```

Status data must be visibly labeled `SIMULATED`, `BENCH MEASURED` or `UNAVAILABLE`; virtual link quality and virtual battery values must not masquerade as real telemetry. UI buttons are advisory; firmware rejects unsafe commands independently.

## 4. Test flows

1. Launch simulator, check DISARMED, confirm no actuator output.
2. Send invalid arm (throttle not neutral), show explicit denial reason.
3. Arm with valid RC ownership and neutral throttle; step input and observe left/right plots.
4. Inject link loss, malformed input, low voltage, and verify fault displays and enforced safety state.
5. Attempt forbidden config changes while armed; show blocked reason.
6. On physical bench, verify transmitter controls match labels and do not reverse unexpectedly.

## 5. Design decisions still required

- Exact transmitter model and ergonomic channel assignment.
- Whether V1 needs browser UI in the first build or can start RC/serial console first.
- Which safety indicators should be on airframe versus ground-side transmitter/log.
- Colors/visual layout of UI and optional LEDs. They are subordinate to mass/power/servo timing constraints.

**State:** UI only proposed; no Developer task until approved design and bounded implementation scope.

## 6. V1 Pilot Experience update — phase 1.7 (PROPOSED)

The companion documents `32_RC_PILOT_CONTROL_MAPPING.md`, `33_CONTROL_PROFILES_AND_CALIBRATION.md`, `34_PILOT_EXPERIENCE_AND_GROUND_UI.md`, `35_RC_CONTROL_VERIFICATION_MATRIX.md`, and `36_RC_PILOT_HAZARD_REVIEW.md` define a **proposed** Mode-2-style control layout, disarmed-only profile management, truthful RF/telemetry indicators, pilot checklists, and G1/G2/G3 verification. They supersede no earlier owner decision: **only** RC-first flight goal and deferred autonomy are confirmed.

Important UX clarifications:
- Radio-level ELRS arm state and firmware arm state are independent; no inference of safety from either one alone.
- CH1 steer / CH3 flap / CH5 arm / CH6 optional rate are a **candidate mapping for one explicit TX model**, not a universal EdgeTX channel order; v4 ELRS arming options require version-specific review.
- Display `UNKNOWN` when receiver RF health, physical wing position, battery or airborne state cannot be observed; show simulated/bench/flight data provenance prominently.
- First-flight profile changes, browser takeover and in-flight calibration are forbidden pending explicit evidence. The ground UI is not flight-critical and cannot certify safe flight.

**No UI implementation task created.** Refer to `35` test IDs PX-01…PX-20 and UX-01…UX-08; all NOT RUN.
