# BionicButterfly — Phase 2.9 Design Oracles & Regression Plan

- **ID:** BB-P29-TEST-127 | **Status:** all design-only; **NOT RUN**
- **Baseline:** R1 `115–120` at `15803143960e3fc82a468d99e83474670237857f`.

## 1. Additional test-oracle specifications

| ID | Negative/edge scenario | Required result / reason | Gate |
|---|---|---|---|
| P29-T01 | Scenario with extra event payload key | strict preflight rejection under proposed closed schema; no tick | R1.1 interface closure |
| P29-T02 | Duplicate JSON key in scenario envelope | parse rejection before JSON Schema; no trace | R1.1 parser |
| P29-T03 | Duplicate global event ID with semantically identical data | preflight `E_DUPLICATE_EVENT_ID` despite equivalent meaning | R1.1 parser |
| P29-T04 | In-band valid-schema INVALID UART and simultaneously valid control | runtime `E_FRAME_INVALID`; no accepted frame/ARM | R1 invariant |
| P29-T05 | Two implementations of same proposed mixer with flap .5, steer .25 | exact same integer pair (pending approved formula) | R1.1 mixer |
| P29-T06 | Saturating positive/negative steer inputs | exact clip causes + bounded pair, not physical servo µs | R1.1 mixer |
| P29-T07 | ACTIVE S1 held input, no new frame, both freshness checks valid | same authorized effort according to frozen mixer; timestamp not refreshed | R1 invariant + R1.1 mixer |
| P29-T08 | Same header/ticks/terminal serialized twice with different property insertion orders | byte-identical JCS JSONL and SHA | R1.1 trace |
| P29-T09 | Terminal record includes its own complete SHA | reject as nonconforming, no recursive digest | R1 invariant |
| P29-T10 | Same normative inputs with different invocation UUID/wall time | same complete trace SHA and replay identity | R1 invariant |
| P29-T11 | Unrecognized wire event named for voltage warning | preflight rejection or declared DEFER; do not auto-invent v1 | R1 invariant |
| P29-T12 | 60-second 5ms run at worst-case record sizes vs 16MiB quota | deterministic bound/fail-incomplete (no silent quota expansion) | capacity review |

## 2. Inherited mandatory conformance IDs

`PC-A`, `G1B`, `P22-T`, `P23-T`, `P24-T`, `P25-T`, `P26-T`, `P27-T`, `P28-T` remain **specification inventories**, not passed tests. Before future G1 software acceptance, generate a traceability matrix that retains each historical ID even if cases are deduplicated in an executable harness. Current review establishes only **design coverage**.

## 3. PASS semantics — different gates

- **Document audit PASS:** Git blob, source guard, canonical policy hash, JSON syntax/schema validation; no simulator execution.
- **Design Freeze REVIEW/PASS:** owner-approved R1 exact snapshot, no P0 safety semantic contradictions, **plus** full interface contract gates independently closed if requesting a developer-ready handoff.
- **G1 software PASS:** tested executable against frozen revision, controlled hardware isolation, deterministic output oracle match, complete evidence, negative tests. This is **NOT RUN** here.
- **G4 flight PASS:** cannot be inferred from any of the above; requires independent aircraft, venue, pilot and flight-specific safety evidence.
