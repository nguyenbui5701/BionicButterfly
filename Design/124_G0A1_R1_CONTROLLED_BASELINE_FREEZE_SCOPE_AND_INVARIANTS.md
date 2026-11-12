# BionicButterfly — G0-A1 R1 Controlled Architecture Baseline

- **ID:** BB-P29-SCOPE-124 | **Role:** SA | **Evidence commit:** `15803143960e3fc82a468d99e83474670237857f`
- **Owner decision:** Approved R1 for G0-A1 host-only (see `114`); **not a new owner approval** of additional interface alternatives.
- **Decision vocabulary:** **BASELINE VERIFIED**, **R1 CORE RULES LOCKED**, **FULL INTERFACE READINESS ON HOLD**. These are deliberately distinct.

## 1. Locked contract domains

| Domain | Authority at pinned commit | Frozen behavior |
|---|---|---|
| Product/scope | `114` and owner statement | V1 target RC manually controlled real flight, but this slice *only* PC simulation |
| Host safety/authority | `115` | single SIMULATOR owner, immutable pre-snapshot, whole-tick conflict detection, catastrophe > RESET, previous-tick ACK, S1 hold within freshness limits |
| Numeric policy | `116` + canonical policy JSON | 5000us tick, 20000us LOW, 100000us HIGH, independent 200000us freshness, quotas; **virtual only** |
| Result/error contract | `117` | scenario v1 strict, result/errors v2, distinct conflict vs duplicate IDs, typed outcomes |
| Trace/replay | `118` | JCS JSONL header + tick records + terminal; no nested self-digest; hash external; append-before-virtual-publication |
| Historical authority mapping | `119` | prior proposals retained with front-of-file supersession notices; physical `27` NOT superseded |
| Verification expectations | `120` | documented P28-T01–T28 and inherited test IDs; all not executed |
| Delivery boundary | `122` | no physical HAL, no `Task/` issued by design-only artifacts |

## 2. What LOCKED means

At the exact commit above, selected safety behavior, policy values, result semantics and trace ordering have a verified, owner-selected definition. An SA/developer may not silently change these choices on the theory that an old `57–113` paragraph has priority. A necessary change requires an explicit design delta, impact analysis, version update and owner approval where it changes R1 meaning.

**Not implied by this baseline lock:** complete scenario/event wire grammar, numeric virtual mixing formula, exact trace record key/schema registry, executable test passage, installation of trust allowlist, firmware use, servo test or permission to fly.

## 3. Architecture invariants that MUST survive future wire/interface closure

1. No physical I/O, and no `PC_SIM` event payload that can choose hardware context/actuator adapter/owner.
2. Every virtual tick has one atomic state decision from a complete batch and immutable pre-state.
3. An invalid frame, contradictory control frames or bad RF never refresh trusted pilot input; catastrophic fault has precedence over RESET.
4. No ARM from boot HIGH, timer-only qualification, simultaneous ACK+last LOW, or unsafe restored RF.
5. Non-null effort pair may only be published after a complete trace-record append for that tick; `null` is NOT a PWM zero.
6. `control_trace_sha256` is external to its own hashed JSONL bytes; replay IDs exclude nondeterministic invocation metadata.
7. A test **NOT RUN** must never be described as passed, and no host simulation result proves actual aircraft control authority.

## 4. Freeze classification

**G0-A1 core/scope configuration baseline: VERIFIED / LOCKED at `15803143960e3fc82a468d99e83474670237857f`.**

**G0-A1 full interface-design gate: HOLD — see `125` P0 contract completions.** Do not represent this record as the release of an executable implementation task. This is a narrower, more auditable success than treating a ZIP or Git push as proof of deployable software.
