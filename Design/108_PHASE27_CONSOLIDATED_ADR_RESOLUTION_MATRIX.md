> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `114 (owner disposition), 119 (register)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `110f479a597d366059354b4177f783d8572d0ecc`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — Consolidated G0-A1 Architecture Decision Matrix

- **ID:** BB-P27-ADR-108 | **Rev:** 0.1 | **Date:** 2026-11-13
- **Status:** **SA RECOMMENDATIONS — NONE APPROVED**
- **Scope:** candidate decisions D-075…D-090 (prior phases), pinned to Git HEAD in `107`.

## 1. How to read / avoid design-by-inference

All decisions below have two different fields: **SA recommendation** and **Owner disposition**. At publication, every Owner disposition is `PENDING`; uploading/pushing these documents is **not** an acceptance. Items `D-082` and P25-F01 contain already-verifiable *factual source checks*, but their architecture-policy portions are still recommendations. If even one P0 decision is amended, regenerate impacted test cases and update the owner review packet before freezing.

## 2. Unified decision register (single owner-facing view)

| ADR | SA recommended outcome | Why / trade-off | Proof before code acceptance | Owner disposition |
|---|---|---|---|---|
| **D-075** | **ADOPT** normalize full eligible control batch, reject contradictions before LOW/HIGH interpretation | prevents false DISARM/ARM from contradictory inputs; may reject rapid physical-like switch changes within same SIM tick | P26-T05…07, P27-T01/02 | PENDING |
| **D-076** | **ADOPT** catastrophe before RESET; active hazard before ordinary RESET | no RESET bypass of fault; a reset-on-loss stimulus becomes contingency | P26-T08/09, P27-T03 | PENDING |
| **D-077** | **ADOPT** previous-snapshot LOW qualification for ACK; FAULT_LATCHED cannot clear within a run | avoids one-tick recovery shortcut; requires deliberately separate LOW series after ACK | P26-T20…22, P27-T04/05 | PENDING |
| **D-078** | **ADOPT WITH EXPLICIT VERSIONS** input/scenario v1, result/error v2 | backwards-aware migration; result errors distinguish duplicate global event ID vs same-tick valid semantic conflict | P24/P26-T06, P27-T11 | PENDING |
| **D-079** | **ADOPT** replay ID from canonical scenario/policy/engine/scheduler/format; volatile run UUID excluded | deterministic evidence; requires exact byte spec and no self-hash | P26-T26/27, P27-T13 | PENDING |
| **D-080** | **ADOPT** externally provisioned immutable SIM policy allowlist/digest | scenario cannot authorize itself; added host provisioning governance | P26-T28, P27-T12 | PENDING |
| **D-081** | **ADOPT** trace commit then virtual output publication, incomplete evidence = no PASS | reduces false positives; intentionally introduces fail-closed behavior | P26-T25, P27-T14 | PENDING |
| **D-082** | **UPDATE FACTUAL BASELINE** to current Git HEAD, keep Git presence separate from approvals | earlier Phase23 baseline stale; current Phase26 files present | exact Git SHA + blob checks in `107` | PENDING (fact verified) |
| **D-083** | **ADOPT S1** keep last *authorized* input only while dual freshness gates valid | meaningful sparse-RC simulator; never fabricates new frame; real-flight hold-last still unresolved | P26-T15…19, P27-T07 | PENDING |
| **D-084** | **ADOPT** interrupt LOW on HIGH, invalid frame, semantic conflict, RF nonhealthy, RESET | no accidental qualification across unsafe observation | P26-T10…13, P27-T06 | PENDING |
| **D-085** | **ADOPT** active critical hazard prioritized over ordinary RESET; catastrophic latch absolute | fixes rank gap; no automatic in-run recovery | P26-T08/09, P27-T03 | PENDING |
| **D-086** | **ADOPT** SELF_TEST→DISARMED with RF UNKNOWN but no ARM; power/scheduler critical holds SELF_TEST | separates boot readiness from link qualification; risk of confusing display wording—must display RF UNKNOWN | P26-T23/24, P27-T10 | PENDING |
| **D-087** | **ADOPT WITH NARROW RECOVERY ALLOWLIST**: RF lost/stale, control conflict/invalid, recoverable virtual low-voltage warning after health restored; not catastrophic, scheduler stall or numeric/internal fault | lower risk vs generic ACK-clear; voltage-warning class must be typed precisely before implementation | P26-T20…22, P27-T08/09 | PENDING |
| **D-088** | **ADOPT** nonrecursive canonical JSONL trace, digest external, virtual sink after trace commit | records are replayable and don't contain their own SHA | P26-T25…27, P27-T13/14 | PENDING |
| **D-089** | **ADOPT ONLY AS SIM_POLICY_CANDIDATE_22A** numeric values, PC_SIM_ONLY, separate trusted approval | allows G1 design cases; numbers NOT for ESP32/flying robot | P26-T28; P27-T12/15 | PENDING |
| **D-090** | **ADOPT** source-document patch plan with explicit supersession, compatibility & evidence | avoids 2 competing priority tables being 'current'; source changes must be reviewed, not inferred | `105`, `112`; P27-T16 | PENDING |

**Recommended decision package R1:** accept all SA recommendations *as one internally versioned G0-A1 candidate*, subject to owner acceptance of the **exact text** and a controlled subsequent reconciliation of old docs. It is **not** a declaration that they are already approved; owner can AMEND or DEFER. Any amendment (e.g., S2 instead of S1) requires version bump, new affected oracles and impact review.

## 3. Key forks with a concrete fallback

| Issue | Recommended R1 | Alternative considered | Consequence of alternate |
|---|---|---|---|
| Empty tick in ACTIVE | S1 hold last authorized bounded SIM intent while both ages fresh | S2 output null until next frame | S2 better strict-input simplification but breaks P26 sparse-frame expectations; rewrite T15…19 and HMI tests |
| Catastrophe/RESET collision | catastrophe latches | RESET clears first | reject RESET-first: weakens safety invariants and inconsistent with inherited T08 |
| LOW recovery | prior committed qualification required | same-tick LOW+ACK allowed | not recommended: makes recovery depend on intra-tick ordering |
| RF UNKNOWN at SELF_TEST | can show DISARMED, cannot ARM | remain SELF_TEST until RF HEALTHY | valid simpler alternative; impacts state UX/P26-T23, not real hardware readiness |
| Result errors | separate v2 enum | reinterpret old v1 enum | reinterpretation rejected: would silently change historical test meanings |
| Trace evidence | nonrecursive terminal + digest external | terminal contains self-hash | self-hash rejected; unwell-defined fixed point |

## 4. Decision readiness vs test status

`DECISION-READY` means the alternatives and implications are written down; **it does not mean PASS**, developer permission, or safety approval. Architecture decision must be accepted first; code acceptance oracles execute after a scoped implementation is separately authorized. The only factual closure now is repo presence/hash matching, not test execution.
