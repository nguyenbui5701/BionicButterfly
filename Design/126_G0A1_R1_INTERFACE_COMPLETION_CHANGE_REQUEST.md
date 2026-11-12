# BionicButterfly — R1 Interface Completion Change Request (SA Proposal, NOT APPROVED)

- **ID:** BB-P29-CR-126 | **Class:** additive interface specification, candidate **R1.1** for review
- **Base:** R1 `115–118`, exact Git `15803143960e3fc82a468d99e83474670237857f`
- **Status:** **PROPOSED / NO AUTOMATIC OWNER APPROVAL / DO NOT IMPLEMENT AS NORMATIVE YET**

## 1. CR-01 — Formal scenario wire grammar

Create a strict JSON Schema (Draft 2020-12) for scenario-v1 domain with no unknown fields and an exhaustive event registry, with illustrative, non-binding examples from `104`: `SIM_RF_STATUS`, `SIM_CONTROL_FRAME`, and the acknowledged `SIM_ACK_FAULT`; specify BOOT encoding unambiguously rather than assuming the state name is the JSON `type` discriminator. In existing docs, some events are named `BOOT` and others prefixed `SIM_`; this is exactly why an explicit tagged union is needed.

**R1 invariants:** `schema_version=1`, `context=PC_SIM`, `provenance=SIM_ONLY`, global event ID uniqueness, strict event microsecond time, `SIM_CONTROL_FRAME` with `uart_frame_status=INVALID` as a valid typed injected diagnostic, no arbitrary physical context or owner. Decide whether `SIM_CATASTROPHIC_FAULT`, RESET, scheduler/power stimuli have v1 wire representations by examining all historical fixtures and owner-reviewed expectations. **Do not invent their payload shape to make tests pass.**

Proposed contract must give validation precedence: malformed JSON/duplicate keys/unknown event type/duplicate IDs -> preflight rejection with zero core ticks; valid injected diagnostic INVALID -> runtime event with typed refusal.

## 2. CR-02 — Deterministic virtual mixer

R1 only fixes `left/right_micro_effort ∈ [0,1,000,000]`, null gate, and quantizer. Two potential virtual-only choices are shown for decision, neither is an approved flight model:

| Option | Conceptual dimensionless transformation | Effect | Status |
|---|---|---|---|
| **M0** | `L=clamp(flap - steer,0,1)`, `R=clamp(flap + steer,0,1)` before R1 quantizer | Common+differential steering, clips on extreme values | **SA candidate**, not approved |
| M1 | `L=clamp(flap*(1-steer),0,1)`, `R=clamp(flap*(1+steer),0,1)` | steering authority tied to flap effort | Alternative, not approved |

The actual `steering_demand` admissible domain and sign convention must be explicitly validated against `57`/`32` (some candidate schemas may use signed steering), as must normalization, neutral thresholds, clipping reasons and quantization. The relation to measured lift/roll/yaw is **unknown**. The eventual approved formula must include exact results for `flap=0`, `flap=0.5, steer=±0.25`, saturation and S1-held ticks.

**SA preliminary preference:** M0 is more directly traceable to the common/differential two-servo abstraction (`37/39`); do not present as proven feasible or physically safe. Selecting M0 vs M1 is an **observable behavioral decision**, requiring owner review/approval of the new interface version.

## 3. CR-03 — Closed trace record types

Adopt a tagged union with separately declared header, tick and terminal record schemas, each `additionalProperties=false`, explicit version numbers, `null` versus omitted fields and fixed record membership. The JSONL framing and digest algorithm from `118` are **unchanged**. A candidate required field set:

- Header: `record_type`, `trace_format_version`, `result_contract_version`, `replay_identity`, `scenario_digest`, `policy_digest`, `engine_revision`, `scheduler_revision`, `scheduler_step_us`, `scope`.
- Tick: `record_type`, `tick_index`, `eval_at_us`, `state_before`, `state_after`, `rf_effective`, `accepted_frame_age_us`, `causal_event_ids`, `reason_codes`, `output_allowed`, `left_micro_effort`, `right_micro_effort`.
- Terminal: `record_type`, `run_status`, `evaluated_tick_count`, `fault_codes`, `evidence_complete` (no trace hash or wall time).

These are **suggested** fields only. Canonical reason sorting must use an exact comparator; same-tick duplicate semantically equivalent observations preserve sorted causal IDs. `event_at_us` and `eval_at_us` must not be conflated. Freeze reference JCS vectors (including non-ASCII inputs and float edges) before claiming deterministic replay.

## 4. CR-04 — Test/approval process

R1.1 cannot change R1 fault priority, independent RF/frame freshness, 5ms policy values, no in-run catastrophic clear, ACK-before/after-LOW semantics, `SIM_ONLY` isolation or external trace digest. Supply a diff and explicit owner decision for any observable behavior newly selected. Test vectors in `127` remain NOT RUN until code exists.

After review, publish one authoritative interface supplement with ID/version, SHA/digest, and formally supersede only the affected part of `117` / `118`; never append different inferred wire grammars into the old docs silently.
