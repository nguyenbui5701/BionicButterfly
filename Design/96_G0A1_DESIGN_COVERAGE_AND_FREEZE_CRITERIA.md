# BionicButterfly — G0-A1 Design Coverage and Freeze Criteria

- **ID:** BB-P25-COVER-096 | **Revision:** 0.1 | **Status:** PROPOSED acceptance checklist, NO CODE TESTS RUN.

## 1. Required distinction

**Design Freeze** confirms architecture semantics and approval references are internally consistent; it does **not** require completed implementation code, but MUST have complete reviewable test oracles. **Implementation Acceptance** later requires runnable tests and observed PASS on exact approved implementation. **Hardware/Flight Qualification** is a separate gate and does not follow from the first two.

| Topic | Design evidence | Design freeze gate | Runtime proof later |
|---|---|---|---|
| Scope and source separation | `02`, `56`, `78`, `84`, `87` | owner approves PC_SIM_ONLY exclusively | host dependency scan, hardware-port attack tests |
| Input wire schema/error version | `57`, `85` | input v1/result v2 decision recorded | parser/typed reject tests PC-A/P24 |
| ARM/DISARM/ACK/RESET | `58`, `68`, `84`, `95` | one complete transition matrix and owner-accepted P0/P1 resolution | deterministic state vectors |
| Time/freshness | `59`, `67`, `84`, `95` | exact no-event tick decision and boundary values accepted | virtual-time replay |
| Mixer/virtual sink | `28`, `39`, `78`, `85` | bounded, dimensionless outputs, null when inhibited | envelope/saturation tests |
| Config and trust | `70`, `87`, `93` | externally approved immutable policy provenance/digest | self-approval & mutation attacks |
| Trace/evidence | `69`, `80`, `87`, `94` | digest scope without recursion and committed tick contract | replay byte identity + failure injection |
| Tests | `63`, `71`, `79`, `86`, `95` | unique test IDs; every OPEN choice explicitly flagged | mandatory sets pass; no test inferred PASS |
| Review and owner authority | `30`, `89`, `97–98` | exact pushed Git SHA/digests and owner signoff | future task/PR and CI evidence |

## 2. Explicitly excluded from G0-A1

Real TX receiver/CRSF radio health, XIAO ESP32-C3 GPIO/UART, servo power/thermal limits, in-air RF loss, wing mechanics, 6-DOF calibrated aero, flight controller feedback, GPS/autonomy, LED payload. Simulation architecture can be frozen before these are measurable, **without** claiming they are solved.

## 3. Design-freeze blockers today

- **B1:** Phase24 revised contract absent on Git main at verified SHA (`P25-F01`).
- **B2:** D-075…D-082 not explicitly owner accepted; conflicting older tables not fully reconciled (`P25-F02`).
- **B3:** numeric SIM policy and trusted approval digest not owner accepted (`P25-F03`).
- **B4:** terminal hash/digest and no-event tick semantics incomplete (`P25-F04/05`).
- **B5:** owner has not approved a particular Phase25 reviewed revision nor a separate future implementation scope.

**Status:** G0-A1 NOT FROZEN. Once B1–B4 are closed in a new verified Git commit, owner can review *design freeze* separately. Code test PASS belongs to later execution, not a prerequisite to the design decision.
