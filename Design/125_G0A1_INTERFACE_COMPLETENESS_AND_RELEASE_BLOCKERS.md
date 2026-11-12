# BionicButterfly — Phase 2.9 Contract Completeness Audit & Release Blockers

- **ID:** BB-P29-GAP-125 | **Pinned baseline:** `15803143960e3fc82a468d99e83474670237857f` | **Owner-approved R1 core:** retained unchanged
- **Severity meaning:** `P0-HANDOFF` blocks issuing an unambiguous *implementation task* for the affected module, not a retroactive revocation of the owner's R1 design selection. `P1` is an explicit risk/dependency not claimed closed.

## 1. Source-to-gap assessment

| ID | Priority | Verifiable finding | Why it matters | Disposition |
|---|---|---|---|---|
| **P29-F01** | **P0-HANDOFF** | `117` declares strict scenario v1; no exhaustive scenario/event machine schema in Phase2.8 `contracts/` | parser contracts could disagree | OPEN |
| **P29-F02** | **P0-HANDOFF** | `115/117` specify output bounds/quantization but **not unique L/R mixing** | deterministic outputs could differ | OPEN |
| **P29-F03** | **P0-HANDOFF** | `118` defines JSONL framing but **not closed header/tick/terminal schemas** | same semantics could hash differently | OPEN |
| **P29-F04** | P1-DESIGN | recoverable voltage warning is a reason, not a recognized new wire event | some fault vectors require defer | OPEN, explicitly constrained |
| **P29-F05** | P1-IMPLEMENTATION | trusted runtime allowlist not provisioned | no executable trusted host policy | EXPECTED G1 DEPENDENCY |
| **P29-F06** | P1-IMPLEMENTATION | no simulator test run | no functional PASS evidence | EXPECTED G1 DEPENDENCY |
| **P29-F07** | P1-CAPACITY | trace-byte bound not justified for 60s/5ms | quota could end nominal run | OPEN, no silent policy amendment |

## 2. What is **not** a blocker of the R1 approved core

- Legacy `57–113` different vocabulary and older proposed precedence: **controlled supersession** in `119`, merged Git files checked.
- `VOLTAGE_WARNING_RECOVERABLE` without a scenario v1 wire event: treat any unrepresentable voltage recovery fixture as **DEFERRED**, not a fabricated PASS.
- No real flight fail-safe/crosswind/mass/wing results: those block **physical gates**, not PC-only architecture selection.
- The policy digest and source records are accurately pinned, but neither constitutes a signed runtime release.

## 3. Precise missing artifacts before the first Developer parser/FSM/trace task

1. **Scenario input schema**: closed event inventory, per-event payload schema, `event_at_us` integer bounds, original timestamps, duplicate object keys, duplicate event IDs, required BOOT at T0, max nesting/bytes, and exact invalid-event injection.
2. **Virtual mixer**: signed steering convention, clamp/quantize order, expression of effort on HIGH demand and last-authorized S1 hold, null vs authorized zero; no physical wing-angle semantics.
3. **Trace schema**: versioned closed header/tick/terminal records; deterministic reason/source ID sorting, optional/null keys, terminal counts, exact error code set and canonicalization.
4. **Cross-check vectors**: at least one valid tiny scenario, one full arm/recovery scenario, one duplicate/conflict scenario and a byte-for-byte hash reference; all derived from chosen schema and mixer, not guessed by Developer.

## 4. SA recommendation / no silent amendment

Treat approved R1 as an **exact architecture snapshot**. Prepare an additive **R1 interface-completion candidate** rather than editing policy numbers or fault priorities under the R1 label. Approving such a completion is a separate documented decision, unless independent review conclusively proves it introduces no choice or observable semantic change. See `126` for candidate options and what is explicitly NOT approved.
