# G0-A1 — R1.1 Virtual Mixer M0 Exact Contract Candidate

- **ID:** BB-P210-MIX-133 · **Status:** **PENDING OWNER APPROVAL** · **Finding:** P29-F02
- **Machine-readable:** `contracts/G0A1_MIXER_M0_R11_CANDIDATE.json`; golden: `fixtures/P210_M0_GOLDEN_VECTORS.json`.

## 1. Selection and rationale

SA recommends **M0** from `126` over M1 for a pure host-only *abstract* two-output simulator: `L = clamp(flap - steer,0,1)`, `R = clamp(flap + steer,0,1)`. It directly represents common/differential commands but **does not claim positive steering causes a physical yaw/roll direction**; actual aircraft effectiveness requires measured aerodynamics, passive stability and separate G4 approval. `steer > 0` raises **right virtual effort relative to left**, a software sign convention only. No servo angle/PWM/beat frequency is implied.

## 2. Integer exact implementation equivalence

Pilot inputs in wire v2 are finite JSON numbers with at most 6 base-10 fractional places: `flap∈[0,1]`, `steer∈[-1,1]`. Convert *exact decimal token value*, not rounded binary64, to signed integers:

```
F = exact_integer(flap_demand * 1_000_000)
S = exact_integer(steering_demand * 1_000_000)
Lraw = F - S
Rraw = F + S
L = min(1_000_000, max(0, Lraw))
R = min(1_000_000, max(0, Rraw))
```

Thus both outputs are integers `left_micro_effort=L`, `right_micro_effort=R`. Under the six-decimal domain this is exactly equivalent to approved R1 `floor(clamp(x,0,1)*1e6+0.5)`; it avoids platform-dependent float half-ties. JSON `-0` normalizes to `0`. Exponents such as `1e-6` are allowed if the exact decimal value satisfies the scale rule. Do **not** round an input with >6 places; reject it in preflight. `0.0000005` is invalid, not rounded. This restriction is a *new R1.1 decision* to approve separately.

## 3. Clip tags and output gate

- For each unbounded side less than 0, add `<SIDE>_LOW`; greater than 1,000,000 add `<SIDE>_HIGH`. Equality is **not** clipping. Tags sorted by unsigned UTF-8 bytes: `LEFT_HIGH`, `LEFT_LOW`, `RIGHT_HIGH`, `RIGHT_LOW`.
- An allowed output of `(0,0)` is **not** the `(null,null)` inhibited pair. Calculate and expose L/R only if **post-state is ACTUATION_ACTIVE**, all independent R1 freshness and authority guards hold, and complete trace decision append was acknowledged.
- `input_mode=FRESH` if a new accepted and authorized frame established the active intent on this tick; `S1_HELD` if no new accepted frame and the previously authorized intent remains valid. **Never** re-quantize an already quantized output with a new sign convention or refresh timestamps on hold. Compute M0 from the held *input* each allowed tick, not from previous output bytes.
- No extra deadband is inserted; arm neutrality and active flap threshold belong to R1 FSM and are unaffected by M0. The M0 algebra for `flap=0` is a design vector, not evidence that ACTUATION_ACTIVE may emit zero on a LOW/DISARMED state.

## 4. Golden examples

| F | S | L | R | Clip tags |
|---:|---:|---:|---:|---|
| 0 | 0 | 0 | 0 | [] |
| 0.5 | +0.25 | 250000 | 750000 | [] |
| 0.5 | -0.25 | 750000 | 250000 | [] |
| 0.05 | +0.10 | 0 | 150000 | LEFT_LOW |
| 1 | +1 | 0 | 1000000 | RIGHT_HIGH |
| 1 | -1 | 1000000 | 0 | LEFT_HIGH |
| 0.999999 | +0.000002 | 999997 | 1000000 | RIGHT_HIGH |

R1 virtual actuator output still makes **no physical claim**. Do not interpret the numbers as servo pulse width measured in microseconds despite the `micro_effort` name.

## 5. Review tradeoff

M0 permits nonzero right effort when flap=0 and steer>0 in the *algebra*, so any physical reuse would be dangerous and is prohibited. M1 ties differential to common flap but changes user behavior; evaluate it only under a separate change request. SA recommends accepting M0 for PC-only validation *with independent signed virtual effort semantics*.
