> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `114 (owner approval and latest source baseline)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `48bfa34e31452aac9407d20daa5de3fa357c5b49`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — Phase 2.7 Owner G0-A1 Decision Packet

- **ID:** BB-P27-OWNER-113 | **Rev:** 0.1 | **Date:** 2026-11-13
- **SA recommendation:** **READY FOR OWNER DECISION ON CANDIDATE R1; NOT DESIGN-FROZEN**
- **Baseline:** `nguyenbui5701/BionicButterfly main@be85c3e28a2ba6891f2bd6199a58fe0ce564f305`
- **Approved scope today:** none newly granted. User-approved product goal remains manual RC free flight V1; V2 autonomy later.

## 1. Decision that is being presented

Approve, amend, or defer a **narrow** PC-only simulator architecture. The scope is host logic only: strict scenario JSON, independently approved immutable SIM policy, synthetic RF/control signals, atomic safety FSM decision per 5ms *candidate* tick, bounded dimensionless virtual wing commands, replayable trace and results, all with explicit no-hardware interface. The user is **not** asked to approve ESP32 firmware, hardware purchase, wing actuator tests, real airborne RC failsafe or autonomous V2.

## 2. One-page owner decision (currently unsigned)

| Choice | What it means | Consequence |
|---|---|---|
| **APPROVE CANDIDATE R1** | accept the exact scope and SA recommendations D-075…090, including numeric SIM policy in `102` and exact written semantic clarifications in `109/110` | SA can then reconcile older `Design/` docs under change control, pin revised contract & external digest. **No Task permission implied.** |
| **APPROVE WITH AMENDMENTS** | accept the scope but explicitly name changed ADRs (e.g., S2 instead of S1, altered recovery set, SELF_TEST RF gate) | SA revises the contract and affected test oracles, then returns for exact revision approval |
| **DEFER / REQUEST REWORK** | keep the current design candidate unapproved | SA addresses the specified gaps; source remains historical candidates |

**SA preference:** R1, because it provides deterministic, explicit semantics without crossing into hardware. But code must not start and Design must not be marked FROZEN until a decision with exact revision and proof of reconciliation is captured.

## 3. Decisions to accept together (not silently decided by SA)

| Package | Recommended choice | IDs |
|---|---|---|
| SAFETY | whole-tick conflict detection, active-hazard before RESET, terminal catastrophe, prior-snapshot ACK, LOW-break on invalid and recovery allowlist | D-075–077, D-083–087 |
| INPUT / POLICY | schema input v1, result/error v2, SIM numeric 22A, external owner-controlled policy approval | D-078, D-080, D-089–090 |
| REPLAY / EVIDENCE | deterministic replay identity, external nonrecursive full trace SHA, trace commit before virtual output | D-079, D-081, D-088 |
| BASELINE | current Git HEAD verified and no hardware/flight implication | D-082 plus `107` |

**Required explicit subchoice before approval:** exact recoverable voltage-warning enum and duplicate distinct-ID `SIM_ACK_FAULT` cardinality rule. SA suggests `VOLTAGE_WARNING_RECOVERABLE` only for documented noncritical, cured virtual warning; never class critical power under that type. Equivalent distinct-ID ACKs in one tick count once; repeated exact global IDs remain invalid scenario. These subchoices must be incorporated in result schema after owner acceptance, not left to Developer.

## 4. Conditional gate review status

| Area | Status on this phase | Why |
|---|---|---|
| Git source presence and contents | **VERIFIED** | current HEAD, docs `99–106`, matching blob IDs |
| Decision alternatives | **READY TO REVIEW** | `108–110`, exact options with trade-offs |
| Critical semantic reconciliation in older files | **NOT YET APPLIED** | requires an owner-selected contract, then controlled edit |
| G0-A1 owner decision | **PENDING** | no recorded explicit acceptance tied to revision |
| Trusted policy canonical digest/approval record | **NOT ISSUED** | policy format and decision not approved |
| G1 executable tests | **ALL NOT RUN** | no approved implementation task issued |
| G0-B / G3 / G4 physical readiness | **HOLD / NO-GO** | no flight/mechanical/electrical evidence |

## 5. Owner decision template (NOT signed / NOT an approval token)

```text
REVIEW ID: G0A1-P27-_________
Decision: APPROVE R1 / APPROVE WITH AMENDMENTS / DEFER
Reviewed repo: nguyenbui5701/BionicButterfly
Reviewed HEAD: be85c3e28a2ba6891f2bd6199a58fe0ce564f305
Proposed Design version: P27 / docs 107–113 (candidate)
Decision scope: PC_SIM_ONLY; no physical interfaces
D-075…D-090 outcome: __________
If amended, changed ADRs and required oracle modifications: __________
Exact accepted policy typed schema and numeric values: __________
Voltage warning enum; ACK duplicate cardinality: __________
Owner decision date/evidence: __________
SA review reference: __________
Reconciled prior docs Git commit: PENDING
Approved canonical policy SHA-256: PENDING
G0-A1 freeze status: NOT FROZEN until reconciliation & acceptance complete
Separate permission to create Developer Task/: NOT GIVEN
```

## 6. What SA does next depending on the owner's choice

- **APPROVE R1:** verify HEAD, prepare versioned `Design/` document reconciliation R1–R6 and audit updated oracles. Return exact re-reviewed commit and owner-approved typed policy digest for final freeze review. Do not invent a signature or auto-create Task.
- **AMEND:** update the particular contract and all impacted oracles, test coverage and ADR; present a new revision, not a patch without versioning.
- **DEFER:** keep P0 issues open and preserve historical baseline, continue only the requested changes.

**Final disposition:** Phase 2.7 is a **review packet**, not a flight design freeze, software acceptance report, or permission to actuate servos. No code or `Task/` was produced.
