# BionicButterfly — V1 Hardware & Airframe Design (Draft)

- **Document ID:** BB-HW-001
- **Version:** 0.4 — 2026-11-12
- **Status:** PROPOSED — not approved for purchase, construction or flight
- **Owner:** SA
- **Owner-confirmed product goal:** V1 physically flies, piloted by a handheld RC transmitter; V2 autonomy follows after V1 acceptance.
- **Dependencies:** `02_V1_REQUIREMENTS.md`, `13_V1_ARCHITECTURE_PROPOSAL.md`, `14_V1_VERIFICATION_PLAN.md`, `16_RC_INTERFACE_CONTRACT.md`, `17_MECHANICAL_FLIGHT_FEASIBILITY.md`, `18_MECHANICAL_EXPERIMENT_PLAN.md`

## 1. Airframe architecture — candidate, not yet fixed

```text
RC Handheld Transmitter
          |
       RF LINK                 Airframe (all lightweight)
          v
      RC Receiver -- UART/receiver-specific interface --> ESP32-C3 candidate
                                                      |          |
                                                PWM L/R        status/LED (optional)
                                                 |   |
                                              Servo L  Servo R
                                                 |   |
                                               left/right wing linkage

Battery -> protected/distributed power -> servo rail + logic regulator
             |                           |
      voltage/current sensing      shared signal ground; filtered
```

- Wing count: two flapping sides, each with a commandable actuator **candidate** based on reference designs. Servo actuation **must be validated** for required flap rate and load; direct-drive, linkage or alternative actuator remains revisable if physics tests fail.
- Wing geometry, hinge and material: **TBD**; 3D prints or reference CAD are *research inputs*, not proven airworthy and not automatically licensed for reuse.
- Receiver protocol and board pins: **TBD**. UART-based ExpressLRS/CRSF is one candidate, not an approved BOM.
- No IMU/GPS navigation requirement in V1; optional telemetry sensors are subject to mass budget and flight safety case.

## 2. Measured design budget — template (do not substitute guessed numbers)

| Item | Quantity | Mass measured (g) | Power/current measurement | Source/evidence |
|---|---:|---:|---|---|
| Wing film / spar / hinges | 2 sides | TBD | n/a | actual sample |
| Actuator and linkage L/R | 2 | TBD | peak/average/stall TBD | datasheet + bench |
| Body/frame | 1 | TBD | n/a | scale |
| MCU, wiring, RX, connectors | set | TBD | peak and idle TBD | bench |
| Battery/regulator/protection | set | TBD | sag/thermal/runtime TBD | bench |
| LED/other optional load | optional | TBD | TBD | bench |
| **Total all-up mass & CG** | — | **TBD** | **TBD** | **weigh assembled airframe** |

**Physical feasibility:** Weight `W = m_total * g`. Before any flight claim, obtain lift/force evidence against weight and dynamic margins, verify actuator speed at load and linkage fatigue, and check that battery can supply peak current without brownouts. There is no validated lift margin, wing loading or flight duration yet. Mass budget must be revisited after each mechanical change.

## 3. Electrical & mechanical safety requirements

1. Use datasheet-compatible operating voltage and rated servo pulse frequency; avoid powering loaded servos directly from ESP32 IO or its onboard regulator without proven capacity.
2. Provide common signal ground and verified logic-level compatibility; use regulator/filter/protection as warranted by actual current/EMI measurements.
3. Hardware wake/reboot and firmware boot default to benign/disarmed behavior; verify no unexpected flap pulses with mechanism detached.
4. Separate actual servo-endpoint calibration from nominal 0°–180° conventions. Identify both hard stops and safe software endpoints for L/R with margin; check mechanism for binding at each phase.
5. Evaluate receiver RSSI/link validity and power warnings, but determine flight contingency from measured outcomes; immediately removing lift midair can be hazardous.
6. Retain positive mechanical guards and physical separation from people during bench and restrained testing. Confirm suitable flight location and applicable requirements before G4.
7. Battery chemistry/charger/connector selection and fire precautions require their own review before hardware energization.

## 4. RC controller candidate

Physical handheld radio with an intentional arm switch and dedicated throttle/steering channels; selection should verify receiver binding, compatible serial output, latency, fail status, range appropriate for approved test site, supply voltage, antenna placement, weight and mass budget. Wi-Fi/phone is not a fallback for flight-critical control.

Official sources to inspect when evaluating candidates:
- Espressif ESP32-C3 LEDC PWM documentation: https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-reference/peripherals/ledc.html
- ExpressLRS UART/CRSF wiring: https://www.expresslrs.org/quick-start/receivers/wiring-up/
- ExpressLRS receiver serial protocols: https://www.expresslrs.org/software/serial-protocols/

## 5. Mechanical/flight feasibility questions blocking final BOM

- Target wingspan, target all-up mass, chosen wing construction and actuator geometry? Owner preferences TBD.
- Servo speed/torque/current under *actual wing inertia and aerodynamic load*? Not measured.
- Evidence of aerodynamic lift, steering authority, trim and center of gravity? Not measured.
- Battery size/endurance/radio range and resulting mass trade-off? Not chosen.
- Indoor protected hall vs outdoor test location, local airspace and required permissions? Not chosen.
- RC receiver and transmitter model/availability? Not selected.

## 6. Hardware validation gates

- **G0:** approved BOM candidate, pin map, design mass/power/CG budgets, mechanical plan, risk controls.
- **G1:** simulator only; no physical motion.
- **G2:** electronics and free servos; calibrated current-limited bench tests with *wings removed*.
- **G3:** fully restrained mechanism, lift/force and loads/temperature/link fail data captured.
- **G4:** separate flight review/authorization, controlled site, pilot, video/log; free-flight test required for V1 completion.

**Status as of 2026-11-12:** measurements NOT RUN; no parts selected or purchased by SA; not approved for flight.


## 7. Mechanical feasibility update (v0.2, 2026-11-12)

- V1's next design decision is **candidate M1: two independent servos**, not approved final drive. Alternatives M2 (one motor + crank and dedicated steering) and M3 (two geared motors) remain in `17_MECHANICAL_FLIGHT_FEASIBILITY.md`.
- Published butterfly flying robots emphasize **very low all-up mass**, thin compliant wings, independent wing control and CG. The Festo eMotionButterflies example (50 cm, 32 g, ~1–2 Hz) also uses IMU and **external indoor camera positioning**; it is not proof of manual-only RC flight with our intended build. See original source: https://www.festo.com/PDF_Flip/corp/Festo_eMotionButterflies/en/index.htm
- **No purchase BOM yet.** Before selecting servos/regulator/airframe: mass and CG, `f_actual` under load, amplitude, transient current, voltage stability, wing force/moment and controllability must be reviewed against the mechanical experiment protocol `18_MECHANICAL_EXPERIMENT_PLAN.md`.
- The 7805/AMS1117 concept mentioned in the S-DiY build manual must **not be assumed sufficient** for fast actuating servos: linear regulators dissipate approximately `(Vin - Vout) × I` in heat; actual regulator thermal/current limits require engineering review. Never power a wing servo from an unverified MCU rail.
- Use a **bare-airframe/no-LED** mechanical test configuration first, because placing LED/wiring on wings changes inertial load. The eventual illuminated demo may have a different mass/CG and must be retested.
- Attitude assistance from an IMU, if eventually needed, is distinct from waypoint-based autonomous flight. It must be separately evaluated and owner-approved as an optional V1 stabilization aid; V2 autonomy remains out of scope.

**Verification status:** NOT RUN; dimensions, wing area, target mass, servo ratings, voltage and thrust/lift/moments all remain TBD.

## 8. Bố trí concept M1/C0 và ngân sách (v0.3, 2026-11-12)

- Sơ đồ top/side view chỉnh sửa được và hệ trục: [`19_MECHANICAL_CONCEPT_DESIGN.md`](19_MECHANICAL_CONCEPT_DESIGN.md). Đây là mô hình bố trí, không phải CAD đủ kích thước để đặt in 3D.
- Ngân sách phân bổ C0 **70 g**, C1 **82 g** chỉ là *kịch bản dự toán* (chưa cân), không phải tiêu chí bay được: [`20_PRELIMINARY_BOM_MASS_POWER.md`](20_PRELIMINARY_BOM_MASS_POWER.md).
- M1 hai servo có thể chưa đủ điều khiển pitch/roll khi bay tự do: gate MC-10 trong [`21_MECHANICAL_CONCEPT_REVIEW.md`](21_MECHANICAL_CONCEPT_REVIEW.md) là điểm chặn G4.
- Phương án điện bắt buộc kiểm chứng 2S→BEC theo rail servo và logic; không cấp 2S trực tiếp vào servo không-HV hay BAT (1S) của XIAO.
- C0 không LED luôn đi trước C1. Sau khi chuyển sang C1 phải cân, đo nguồn, đo quán tính/tần số/lực và review lại.

**Trạng thái:** vẫn PROPOSED / chưa được phép mua hoặc thử bay.

## 9. Electrical detailed design overlay (v0.4 — PROPOSED)

- Read [`22_ELECTRICAL_POWER_ARCHITECTURE.md`](22_ELECTRICAL_POWER_ARCHITECTURE.md) for 2S→regulated servo/logic supply candidate, USB power-path isolation, battery sensing and limits.
- Read [`23_PINOUT_AND_SIGNAL_CONTRACT.md`](23_PINOUT_AND_SIGNAL_CONTRACT.md) for **XIAO-specific candidate** D6/D7 UART, D4/D5 PWM, D1 ADC1 and reserved boot strapping pins. This is *not* the final soldering schematic.
- Read [`24_ELECTRICAL_BENCH_VERIFICATION.md`](24_ELECTRICAL_BENCH_VERIFICATION.md) and [`25_ELECTRICAL_HAZARD_REVIEW.md`](25_ELECTRICAL_HAZARD_REVIEW.md) before approving G2/G3/G4 electrical activities.
- C0 70g/C1 82g mass scenarios are unchanged but must be updated after real regulator/receiver/wiring weights are measured. Source, receiver and servo choices remain NOT APPROVED.

*Changelog v0.4: electrical concept handoff added; no physical readiness claim.*
