# BionicButterfly — Phase 2.12 Git Baseline & Scope Guard

- **ID:** BB-P212-BASE-149 · **Date:** 2026-11-13 · **Role:** Solution Architect · **Status:** DESIGN ADDENDUM / REVIEW CANDIDATE.
- **Repository:** [`nguyenbui5701/BionicButterfly`](https://github.com/nguyenbui5701/BionicButterfly) / `main`.
- **Pinned Git HEAD verified by GitHub connector:** `443d388f29e3a41774d18c7f717783680a47ea3f` (`BionicButterfly Phase 2.11`).
- **Previously frozen R1.1 reference:** `479f65b1f0f077c0a3a75384dbc6b51b8a24e492`, plus Phase 2.11 Git version-specific review on HEAD.

## 1. Verified facts, not assumptions

1. Design files `140–148` are on `main`, the Phase 2.11 frozen index and approval record exist in `Design/contracts/`.
2. R1.1 **wire v2 / M0 / trace** and R1 safety FSM/policy were owner-approved; implementation and G1 runtime tests remain **NOT RUN**.
3. File `142` explicitly calls out the missing exact parse diagnostic taxonomy (P211-GAP-01); `146` marks full parser-report handoff as HOLD for that reason.
4. Phase 2.12 is an **add-only documentation/contract clarification candidate**, no modification to any frozen contract. All relevant source SHA values are recorded in `contracts/P212_SOURCE_PIN_AND_NO_OVERWRITE.json`; verify them when integrating.

## 2. Bounded scope

**Inside:** define one reproducible primary issue per rejected raw input, JSON Pointer location, compatibility with the unchanged R1.1 external report, and acceptance criteria for the first isolated validator/mixer package.

**Outside:** `Source/`, `Task/`, firmware, RC hardware, real serial/USB/PWM, servo/wing physics, flight contingencies, cockpit UI, autonomous V2, engine allowlist implementation. No claim of an executable G1 result.

**Decision status:** existing R1.1 is already approved; the *new optional diagnostic sidecar v1* is **SA RECOMMENDED / OWNER REVIEW REQUIRED**. Adding it must not be interpreted as an automatic rewrite of frozen `117`, `132`, `134` or machine schemas. Git push only adds documents; it is not a new safety/flight authorization.

## 3. Required checks after owner push

- Verify the exact new source commit and all SHA-256 manifest entries.
- Compare all original Git blob values against pinned source; reject unexpected modifications (append to `Design/` only).
- Owner accepts or amends the new diagnostic sidecar contract **before** any task requires detailed parser diagnostics; R1.1 stays frozen regardless.
- No `Task/*.md` is issued by this phase: a later explicit owner handoff request selects the first scoped development job.
