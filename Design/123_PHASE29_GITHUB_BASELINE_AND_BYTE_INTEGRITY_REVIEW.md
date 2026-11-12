# BionicButterfly — Phase 2.9 Git Baseline / Byte-Level Verification

- **ID:** BB-P29-REPO-123 | **Date:** 2026-11-13 | **Role:** Solution Architect (SA)
- **Repository:** https://github.com/nguyenbui5701/BionicButterfly
- **Pinned `main` commit:** `15803143960e3fc82a468d99e83474670237857f` (`BionicButterfly Phase 28`)
- **Phase 2.8 patch base:** `3d9a4f28d521190d10579cab48d8b732817892c9` (`BionicButterfly Phase 27`)
- **Claim boundary:** **document bytes and source revisions verified**, NOT implementation or hardware-test evidence.

## 1. Verification results actually performed

| Check | Observed evidence | Result |
|---|---|---|
| GitHub `main` HEAD via linked repository | `15803143960e3fc82a468d99e83474670237857f`; commit message `BionicButterfly Phase 28` | PASS |
| Phase 2.8 additive files | `114–122`, policy contracts, fixture and diagram visible in GitHub `Design/` | PASS |
| Phase 2.8 manifest | `PHASE28_CONTENT_MANIFEST.json` Git blob `391ac735ca32bbc6384253527affbcefd31ce5c2` | PASS |
| 43 manifest entries | Each local file SHA-256 and byte size independently matched manifest; each Git blob matched exact GitHub listing | 43/43 PASS |
| 27 original-file guards | GitHub source-commit blobs vs `PHASE28_SOURCE_BLOB_GUARDS.json` | 27/27 PASS |
| 27 updated-file guards | GitHub merged-commit blobs vs same guard manifest | 27/27 PASS |
| Canonical SIM policy | SHA-256 `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10` of exactly 603 bytes without terminal newline | PASS |
| Policy schema | Draft 2020-12 JSON Schema validates canonical policy object | PASS |
| Runtime sim tests / hardware or flight tests | No code/runtime execution performed in this phase | **NOT RUN** |

The in-session GitHub file listings were checked at an **exact commit**, not an unspecified moving `main`. Full per-file identifiers are recorded in `contracts/P29_G0A1_BASELINE_ATTESTATION.json`. This is a SHA-256/Git blob audit; it does not assert that a ZIP's prose is a cryptographic owner signature.

## 2. Package arithmetic and scope

Phase 2.8 package: **9 new Markdown**, **27 prepend-annotated existing Markdown**, **1 existing-source guard JSON**, **1 Mermaid diagram**, **4 policy/approval JSON files**, **1 oracle index JSON**; its 43 files plus the standalone manifest give **44 verified Git blobs**. The owner committed this package on the new Phase 28 head. Other older `Design/` records are still historical; their different statuses do not override `115–118` for G0-A1.

We verified original and updated Git blobs against the guard manifest; a valid checksum match confirms byte identity, **not** that every old-body line has been semantically reconciled with every new line. Supersession remains explicitly scoped to G0-A1 by `119`.

## 3. Invariants of the frozen source snapshot

- Scope is `PC_SIM_ONLY`; no UART, PWM, GPIO, real receiver, LiPo, wing actuation or flight authority.
- Owner approved the **Candidate R1 architecture design**, per `114` and `contracts/G0A1_OWNER_APPROVAL_R1.record.json`; no assumption of approval for hardware/flight.
- Policy is the **exact canonical** `contracts/SIM_POLICY_22A_R1.canonical.json`; neither its human-readable copy nor `approved=true` from a scenario is a trust source.
- The reference Git commit is immutable as a **snapshot identifier**; the branch `main` will move when this Phase 2.9 report is later integrated. A new commit does not invalidate the old locked snapshot but is a new candidate for the next release baseline.

## 4. Checks not claimed

No full scenario v1 event-wire JSON Schema or mixer formula was present among the Phase 2.8 machine contracts (only **policy** JSON Schema). Exact per-record trace JSON Schemas are likewise absent. These are treated as readiness findings in `125`, **not** silently invented or represented as PASS.

No source code changes, executable tests, simulator runs, browser UI review or physical experiments are part of this phase.
