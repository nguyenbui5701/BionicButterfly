# Bionic Butterfly — Candidate Pinout & Control Signal Contract V1

- **ID:** BB-IO-023 · **Version:** 0.1 · **Date:** 2026-11-12
- **Status:** PROPOSED; logical assignment, **NOT a certified schematic**.
- **Candidate board only:** Seeed Studio XIAO ESP32-C3 (not generic ESP32-C3). GPIO assignment must be revisited if board changes.
- **Dependencies:** `16_RC_INTERFACE_CONTRACT.md`, `22_ELECTRICAL_POWER_ARCHITECTURE.md`.

## 1. Proposed XIAO pin reservation (subject to proof)

| Connection | XIAO silkscreen | ESP32-C3 GPIO | Direction | Design rationale & checks |
|---|---|---|---|---|
| CRSF UART from RX | `D7 / RX` | GPIO20 | **MCU input** | Receiver `TX` → D7; requires measured 3.3V-safe signal level; no receiver 5V UART signal into GPIO |
| CRSF UART toward RX (telemetry) | `D6 / TX` | GPIO21 | **MCU output** | D6 → receiver `RX`; check boot messages/UART0 ownership and receiver tolerance of 3.3V-high |
| Left servo signal | `D4 / SDA` | GPIO6 | **MCU output** | PWM generator candidate; run unloaded boot-glitch and timing tests |
| Right servo signal | `D5 / SCL` | GPIO7 | **MCU output** | PWM generator candidate; ensure no conflicting I2C allocation |
| Battery sense | `D1 / A1` | GPIO3 (ADC1_CH3) | **ADC input** | 2S divider + filter, calibrated; never connect pack voltage directly |
| Optional local safety/status input | `D2 / A2` | GPIO4 | input | Bench switch/status only after pull/default state review; may remain unused |
| Optional LED data **C1 only** | `D10 / MOSI` | GPIO10 | output | Verify waveform and 3.3V compatibility; **not permitted to impact flight loop** |
| Reserved | `D0 / A0` | GPIO2 | — | **Strapping pin**, avoid on first prototype |
| Reserved | `D8 / SCK` | GPIO8 | — | **Strapping pin**, avoid on first prototype |
| Reserved | `D9 / MISO` | GPIO9 | — | **BOOT/strapping pin**, avoid on first prototype |
| Spare | `D3 / A3` | GPIO5 | TBD | ADC2 sampling caveat; use as digital if necessary and qualified |

This is a **functional allocation only**, not authorization to solder wires. USB debug/upload, oscillator startup, pin boot state, external pull resistors and board revision must be tested before electrical freeze. The XIAO exposes other functions on pins; if a future IMU/LED/actuator circuit requires them, perform a formal pin-map change.

## 2. RC receiver wiring — logical cross-over

```text
[RC RX candidate]                           [XIAO ESP32-C3 candidate]
receiver TX / T ---- [level compatibility verified] ---> D7 / GPIO20 (MCU RX)
receiver RX / R <--- [level compatibility verified] ---- D6 / GPIO21 (MCU TX)
receiver GND ------------------------------------------- GND
receiver VCC <----------- regulated receiver-rated supply (not GPIO 3V3 by assumption)
```

The physical **CRSF UART protocol** carries control and optionally telemetry; use an actual ExpressLRS transmitter and receiver pair and check configured output mode. Do not assume RSSI/LQ is present in every frame. Freshness clock must update only after a **fully valid receiver control frame** (not noise or a telemetry frame). Receiver and MCU may reboot independently. The UART must not be shared with a diagnostic serial console without a proven allocation. **Do not select the final baud rate, channel map, arm-switch polarity or timeout from a guess.**

## 3. Servo interface contract

| Contract | Rule |
|---|---|
| `servo_left_cmd` / `servo_right_cmd` | One centralized safety supervisor owns valid outputs; never raw radio/UI pass-through |
| PWM physical timing | Exact servo datasheet controls pulse min/max, frequency and whether 3.3V logic is valid. **50 Hz** is only a common reference starting point, **not a model-independent requirement** |
| Mechanical calibration | Measure safe endpoints, direction and neutral on each side **with wings detached** and physical stop clearance |
| Power | `V_SERVO` regulated **separately** from MCU GPIO, with common signal ground |
| Boot/disarm | No uncommanded flap before and after MCU startup/reset; scope high-Z/floating behavior; no in-air arbitrary power disable |
| Loss of command | Defer to V1 RC safety contract (`16_RC_INTERFACE_CONTRACT.md`); flight policy requires experiments and owner approval |

## 4. Battery sense math and data contract

`V_ADC = V_BAT * R_BOTTOM / (R_TOP + R_BOTTOM)`.

**Illustrative only:** `R_TOP=47kΩ`, `R_BOTTOM=22kΩ`, `V_BAT_MAX=8.4V` yields `V_ADC≈2.678V`; resistor tolerances and spikes require separate limits and filtering.

Normalized telemetry field proposal:

```text
BatterySampleV1 {
  measured_v: float,           // ADC-calibrated pack voltage, not state-of-charge
  calibration_id: string,
  sample_age_ms: uint32,
  quality: VALID | STALE | OPEN_OR_SHORT | UNCALIBRATED,
  scope: PACK_VOLTAGE_ONLY
}
```

Do not label a voltage sample as percentage remaining unless a separately validated SoC estimator exists. Bad/unknown ADC quality must never be treated as healthy. Circuit must be assessed for USB-powered bench scenario with battery sense attached and MCU not powered through battery — possible backfeed paths are blocking review items.

## 5. Control authority (unchanged from V1 design)

- `DISARMED` after power-up. Explicit physical radio arm, validated channel map, receiver age and supply required.
- **No** web or PC command may own actuators while airborne.
- Simulator input may be allowed in a clearly isolated PC or grounded bench mode, not silently swapped into real in-flight command authority.
- In-flight failure transition, reconnection and brownout behavior remain **TBD after tests**; no automatic re-arm on link recovery.
- Never interpret a numeric throttle command as guaranteed thrust: aerodynamic mapping must be measured under wing load.

## 6. Acceptance evidence for pin-map freeze

1. Board pin-silkscreen and revision photo, vendor datasheet revision and exact RX/servo model list.
2. Scope capture of all candidate GPIOs at boot/reset and with receiver powered independently.
3. UART loopback/control frames **with no attached wings**, verified level and direction.
4. PWM frequency/duty/pulse oscilloscope capture and actual servo calibration (no load).
5. USB/BEC power backfeed and hot-plug analysis; receiver power-loss/reboot test.
6. Battery divider sweep/calibration, overvoltage margin and analog noisy-load behavior.
7. Reviewed pin matrix signed by SA and owner **before** implementation/PCB fabrication.

**Status:** All seven evidence items **NOT RUN**, pin map **NOT APPROVED**.

## Official sources

- XIAO pins, power and strapping: https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/
- ESP32-C3 strapping GPIOs and UART: https://documentation.espressif.com/esp32-c3_datasheet_en.html
- Receiver TX/RX crossover: https://www.expresslrs.org/quick-start/receivers/wiring-up/
