# TASK-014 parallel decision packet — physical G0-B and future trusted PC runtime

- BB-P226-197 — **DRAFT DESIGN FOR OWNER REVIEW; no approval granted here**.
- Keep two strictly separate gates: **SC-G1** authentic PC_SIM virtual-only execution; **HB-G0B** physical servo-only bench design. An OWNER_FULL_UAT PASS of TASK-014 approves code review only, not either safety gate.

## Security gate SC-G1: not provisioned

Before **future** authorized `output_allowed=true` virtual commands, Owner must approve a written trust architecture with: fixed runtime binary/version ID and protected install, immutable allowlist with frozen R1 policy digest `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`, approved engine/scheduler revisions, signer/trust-root generation and storage out of scenario/CLI, attestation measurement and rollback/revocation strategy, process boundaries, explicit virtual-only sink identification, failure-injection and append-before-publish receipt verification, and auditable operator roles. SHA-256/policy content, E2/E3 TEST_ONLY consistency, CI, GUI toggles or signed-looking JSON are **NOT TRUST**. Developer must not fabricate keys, positive attestation or a test credential that becomes deployable.

Open decisions: `SCG1-01 owner signoff`, `SCG1-02 signer/root management`, `SCG1-03 signed executable identity`, `SCG1-04 protected install/roll back`, `SCG1-05 receipts/storage crash behavior`, `SCG1-06 virtual sink isolation`, `SCG1-07 failure/quota and audit criteria`. Mark all **OPEN**; future task requires separate approved Design and owner decision.

## Hardware gate HB-G0B: design only, no power on

Carry forward the open HB01–HB10 in Design/193 without inventing measured data:

| Gate | Required concrete owner choice / evidence | Now |
|---|---|---|
| HB01 board | manufacturer, exact MCU board/revision, logic voltage, boot/strap pins | TBD |
| HB02 servos | exact two models, digital/analog drive, supply voltage/current/stall, torque, stroke | TBD |
| HB03 TX/RX | actual ELRS model/revision/firmware, UART levels, channel map, RF-loss semantics | TBD |
| HB04 wiring/power | reviewed schematic, BEC current capacity, servo/logic supply isolation, ground and battery protection | TBD |
| HB05 inhibit | physical disconnect, safe power-up/reset/brownout, independent power cut | TBD |
| HB06 measurement | current-limited DC supply, DMM and oscilloscope/logic analyzer or proven alternative, thermal probe | TBD |
| HB07 firmware | host/core↔HAL design boundary; PWM limits and watchdog/failsafe contract | TBD |
| HB08 mechanics | measured mass/CG, geometry/clearance, unload servo test jig | TBD |
| HB09 G3 wings | separately reviewed restraint, structural, force/moment and power tests | NO-GO |
| HB10 G4 flight | aircraft-specific stability/control/flight failsafe and local compliance | NO-GO |

**Next owner actions:** Record exact possessed/purchasable part numbers, datasheets, battery/BEC/servo wiring draft, bench schematic and proposed test instruments. SA can then produce a reviewed G0-B decision without changing any TASK-014 software requirement. Only a separately signed HB-G0B **APPROVE DESIGN ONLY** permits scheduling G2 servo-only power-up; G3 wing loading and G4 free flight require later gates. Do not directly connect LiPo 2S to servo logic/MCU without a verified regulator design.

## Planned owner decision record (leave unfilled)

`decision_id: TBD`  `date: TBD`  `reviewed_board/servo/receiver_revisions: TBD`  `wiring_schematic_sha256: TBD`  `bench_hazard_review: TBD`  `SC-G1: HOLD|DESIGN_ONLY`  `HB-G0B: HOLD|APPROVE_DESIGN_ONLY`  `owner_signoff: TBD`
