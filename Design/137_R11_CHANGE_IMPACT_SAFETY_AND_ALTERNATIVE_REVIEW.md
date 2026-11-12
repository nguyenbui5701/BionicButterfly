# G0-A1 — R1.1 Change Impact, Alternatives and Safety Separation

- **ID:** BB-P210-CHANGE-137 · **Status:** candidate behavioral changes, review required.

## 1. Change classification from approved R1

| Decision | R1 locked scope preserved | New externally visible R1.1 choice | Impact / approval |
|---|---|---|---|
| R11-D01 | host PC_SIM_ONLY, no physical adapter | exact scenario v2 wire grammar | major wire-version change: owner APPROVE/AMEND/DEFER |
| R11-D02 | R1 ingress finite ranges | at most 6 base-10 decimal places, exact integer scale | rejects some previously acceptable values; owner decision |
| R11-D03 | requested dimensionless L/R bounded, R1 quantizer | M0 common/differential, sign convention | new virtual behavior; owner decision |
| R11-D04 | approved R1 replay hash framing/version | exact closed header/tick/terminal and run report schema | produces new control bytes; owner decision |
| R11-D05 | R1 state and priority unchanged | v2 SIM_RESET / ACK / catastrophe wire representation | no new safety logic; typed input surface expands; owner decision |
| R11-D06 | R1 immutable trusted policy | fixed `config_id`, approved map `sim-map-v1` binding | narrows input; owner decision |

## 2. Alternative analysis

- **M1**: `L=clamp(F*(1-S),0,1)` and `R=clamp(F*(1+S),0,1)` ties steering to flap effort. It is attractive for physical intuition but requires multiplication rounding rules and differs from M0 at zero flap; not selected for this candidate.
- **Unrestricted binary64**: closer to original permissive input numbers but harder to certify same quantization near half-ties across languages. Six-decimal fixed point sacrifices precision to maximize exact trace replay. This precision decision **must not be slipped into R1** as a parser default.
- **Keep unversioned v1 wire**: risks undetected incompatible RESET/catastrophe vocabulary, so rejected for candidate closure.
- **More event types for voltage/scheduler faults**: **deferred**; code must not invent simulator power safety behavior to satisfy test vectors. R1 scheduler stall stays a non-recoverable internal failure/hazard test until a later explicit schema approved by owner.

## 3. Safety and security review

- Not a physical flight controller. Positive `steer` is a **virtual channel sign**; actual aerodynamic roll/yaw authority is **unmeasured**. No implication two servos can independently control all attitude axes.
- Strictly no UART, radio link bind, PWM, actuator plugin, web arm authority, hardware panic mapping or flight fail-safe policy.
- A typed `SIM_RF_STATUS(HEALTHY)` is injected virtual data and does not assert RF link actually exists; cannot by itself arm. Control invalid or RF LOST still outranks demands as in R1.
- R1 allowlist based on immutable trusted policy SHA `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10` is distinct from schema/fixture content hash. Approval file is not an executable credential.
- Parser resource budget inherited unchanged: max 2MiB raw input, 20k events, 16 levels JSON, event ID max 64 bytes; trace quota 16MiB. A 60s run may exceed trace quota and must fail incomplete honestly.

## 4. Git and ADR control

Do not rewrite `115–118` or any other approved R1 doc inside this phase. Add candidate spec `131–139`, obtain exact owner approval on `R11-D01..D06`, and only in a later reviewed update add an explicit supersession/canonical revision notice to affected R1 docs. The freeze baseline is the exact commit plus per-file blob SHA, not a verbal “done” claim.
