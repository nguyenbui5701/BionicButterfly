# Bionic Butterfly — Electrical Hazards & Flight Safety Case (Draft)

- **ID:** BB-EE-SAFE-025 · **Version:** 0.1 · **Date:** 2026-11-12
- **Owner:** SA · **Status:** PROPOSED, NOT VERIFIED, FLIGHT NO-GO
- **References:** `16_RC_INTERFACE_CONTRACT.md`, `22_ELECTRICAL_POWER_ARCHITECTURE.md`, `23_PINOUT_AND_SIGNAL_CONTRACT.md`, `24_ELECTRICAL_BENCH_VERIFICATION.md`.

## 1. Risk treatment and scope

No arbitrary risk number is presented as a measured probability. This is a preliminary hazard inventory. Risk acceptance requires evidence of protection, scenario tests and owner approval. **No single firmware check is sufficient proof of hardware safety.** All listed hazards remain open until evidenced and closed in a revision-controlled record.

| Hazard ID | Scenario / effect | Minimum design controls proposed | How to verify | Gate |
|---|---|---|---|---|
| H-EE-01 | 2S pack voltage enters 1S BAT or 5V XIAO / RX / servo → damage/fire | regulator review, keyed connector, labeling, continuity check, charging isolation | EE-T01, T02 | G0 BLOCKER |
| H-EE-02 | Simultaneous servo current causes BEC sag / MCU reset → uncontrolled flap | independent suitable rails, transient budget, decoupling validated by measurement, safe boot behavior | EE-T03, T07, T11 | G2 BLOCKER |
| H-EE-03 | MCU GPIO floating or boot pulses drive wing unintentionally | safe default pin design, physical bench isolation, scope capture, gated interface if necessary | EE-T06 | G2 BLOCKER |
| H-EE-04 | RX sends invalid/held frames / stale data appears fresh | parser validation, independent receive age, RX status checks, RC-only ownership, recovery interlock | EE-T05, T09, T10 | G2/G3 BLOCKER |
| H-EE-05 | Flight link lost, firmware cuts both servo motors → sudden uncontrolled descent | **separate flight-specific contingency plan**, not a copied ground power-cut; controlled G3 review | EE-T13 + flight hazard analysis | G4 BLOCKER |
| H-EE-06 | Battery depletion, inaccurate ADC or voltage sag → actuator stall, brownout | sensing calibration, load testing, reserve operating envelope, no false battery-healthy status | EE-T08, T11, T12 | G3/G4 BLOCKER |
| H-EE-07 | USB and BEC back-feed each other → damaged rail | supported source selection and isolation, verify on board revision | EE-T04 | G2 BLOCKER |
| H-EE-08 | Servo 5V logic mismatch / RX UART electrical mismatch | verify high/low levels, 3.3V input tolerance, pulse characteristics against exact devices | EE-T05, T07 | G2 BLOCKER |
| H-EE-09 | LiPo short/overcurrent/charge error → heat/fire | genuine protected pack strategy, fit-for-purpose charger, fuse/protection, fire safe handling | EE-T02, inspection record | G0/G2 BLOCKER |
| H-EE-10 | LED C1 interferes with RC/ADC/PWM or adds wing inertia | separate LED load design, C1 requalify mass/current/EMI/force | EE-T14 plus MX mechanical tests | C1 BLOCKER |
| H-EE-11 | Manual pilot cannot control pitch/roll with two servos even if lifts | mechanics and aerodynamic stability tests, do not infer from waveform | MX-08, MC-10, G3 flight review | G4 BLOCKER |
| H-EE-12 | Servo power isolator cuts actuation mid-flight / brownout causes repeated arm | hardware/firmware separation, explicitly approve policy state by state | fault-injection simulation and restrained tests | G4 BLOCKER |

## 2. Failsafe decisions needing explicit approval

| Aircraft state | Bench test assumption | Flight implementation allowed? |
|---|---|---|
| `BOOT` / `DISARMED` | Actuator signal inactive or safe known parked state; physical bench protection | Requires boot electrical validation |
| `GROUND_ARMED` | Controlled activation under neutral command | Requires explicit pilot switch and interlock |
| `ACTIVE_FLAPPING` | Pilot commands bounded, monitored | Only after G3 proves sufficient lift and steering potential |
| `LOST_LINK` | **On bench:** stop/neutralize according to a reviewed test policy | **No generic immediate servo power cut or fixed failsafe flap command is approved in flight** |
| `LOW_BATTERY` | Warn / reject arming on ground if invalid or unsafe | Flight fallback depends on measured pack/actuator dynamics, site and energy reserve |
| `FAULT / REBOOT` | Prevent automatic arming on reboot | In-air behavior must be examined as a separate hazardous transient |

If measurements cannot establish a viable safe flight contingency, V1 must stay at G3. A mere switch to PWM neutral or holding last radio command has no proof of safety; both must be evaluated.

## 3. Approval and provenance

- **Owner-decided:** V1 RC manual free flight; V2 autonomy; pushing code to GitHub remains owner-controlled.
- **Not owner-decided:** exact 2S/1S topology, servo brands, board model, pin map, RC transmitter/receiver, numeric failsafe limits, pilot flight site, risk acceptance.
- **Source provenance:** upstream ESP-FLUTTER / S-DiY are references only; no assumption of permission to copy firmware or artwork. Audit ZIP may contain ignored/untracked local files that do not belong to confirmed upstream commit.
- **SA/Dev separation:** These documents stay within `Design/`. SA does not rewrite dev `Source/` during active AI coding; no `Task/` before relevant design decisions are approved.

**Current G0 / G1 / G2 / G3 / G4 status:** `NOT APPROVED / NOT RUN` — never treat a draft schematic as a flight-ready build.
