# BionicButterfly — Diagnostic Sidecar v1 Approval & First Task Release Record

- **Document ID:** BB-P213-DEC-156
- **Version:** 1.0
- **Date:** 2026-11-13 (Asia/Ho_Chi_Minh)
- **Status:** **OWNER-APPROVED SCOPE / SA TASK RELEASED** (chat approval, not a GitHub commit)
- **Owner decision:** “Tôi phê duyệt Diagnostic Sidecar v1 và cho phép SA tạo task đầu tiên cho AI Developer.”
- **Repository:** `https://github.com/nguyenbui5701/BionicButterfly`
- **Verified source commit:** `f378ec294a4a05887b03a9431696994dc22c0a4f` (`BionicButterfly Phase 2.12`).

## 1. Meaning of the approval

The owner explicitly approved the **Diagnostic Sidecar v1** specified by the *exact existing file contents* of `Design/150` and `Design/151`, plus the paired machine artifacts below. The owner separately authorized the SA to **issue the first Developer task**. This is a design approval and task-release authorization, **not** implementation completion or permission to merge code.

The diagnostic extension is **additive** to the already owner-approved R1.1 G0-A1 host-only design. Existing R1.1 scenario schema v2, safety FSM R1, M0, canonical trace and external report bytes are not modified. Diagnostic `P_*` codes exist outside the frozen runtime `E_*` / `R_*` namespace and do not enter the control trace or the closed report.

### Pinning of approved diagnostic documents

| Role | Exact repository path | Git blob SHA-1 at source commit |
|---|---|---|
| Diagnostic contract | `Design/150_G0A1_PARSER_DIAGNOSTIC_SIDECAR_CONTRACT.md` | `b96beba505a4db94c16e1c0f2b0f8ec65fd740f9` |
| Preflight precedence and pointer rules | `Design/151_G0A1_PREFLIGHT_PRECEDENCE_POINTER_AND_ERROR_REGISTRY.md` | `d1ba14b4d8cf31926353fb72fb20c29c148a9a40` |
| Closed sidecar JSON Schema | `Design/contracts/G0A1_PREFLIGHT_DIAGNOSTIC_V1_CANDIDATE.schema.json` | `d41091455e112cbcede1c7c0ce391c91827bfb41` |
| 27-code issue registry | `Design/contracts/G0A1_PREFLIGHT_ISSUE_REGISTRY_V1_CANDIDATE.json` | `ed7cb5305bf40996a006ac853d7b1990de4eaa70` |
| 26 test-oracle definitions | `Design/fixtures/P212_PREFLIGHT_NEGATIVE_ORACLE_INDEX.json` | `41b5536d37042cb68e71f0c37c40e0b08272617f` |

Historical filenames with `_CANDIDATE` **remain unchanged** to preserve hashes and provenance; they are approved for the narrow scope above, by this explicit owner decision. This does **not** approve other draft/candidate proposals not named here.

### Previously approved frozen R1.1 foundation (unchanged)

- `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` and `Design/contracts/G0A1_R11_FROZEN_DESIGN_BASELINE_PHASE211.json` define precedence.
- `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` — blob `1d10c76e34be70880a65252d89a6bca89839fea9`.
- `Design/contracts/G0A1_MIXER_M0_R11_CANDIDATE.json` — blob `dfde74e76b1bd7eb44088e6d49d06dd1a46cc759`.
- `Design/fixtures/P210_M0_GOLDEN_VECTORS.json` — blob `165aee1347a619c6f2514e522bf0e4fc4b518a6c`.
- `SIM_POLICY_22A_R1.canonical.json` frozen **content SHA-256:** `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`.

## 2. Released work

**SA issues exactly one task:** `Task/TASK-001_HOST_PREFLIGHT_M0.md` (OPEN). The Developer is authorized to implement and test the **pure host-only input preflight/diagnostic plus M0 math** in an isolated package after reading the approved contracts. This task does not authorize a full simulator runner, hardware I/O, a PR merge, or any extra code beyond its allowlist.

The first implementation's Python tooling is a **task-local host development choice**, not a change to approved physical firmware language/platform. Tooling or path changes must be declared by Developer as an SA clarification before changing outside the permitted subtree.

## 3. Release-gate and authority boundaries

- **G0-A1:** selected design contracts approved; runtime implementation/conformance tests **NOT RUN** until Developer delivers evidence.
- **G0-B:** real circuit/power/servos/rig not approved by this decision.
- **G0-C/G4:** free flight and airborne contingency **NO-GO**.
- **V1 product:** ultimately manually RC-piloted *real* flight; this host module proves neither aerodynamic feasibility nor flight control authority. V2 autonomy remains outside scope.
- **Owner manages push/merge.** This record and task are locally created deliverables; merely receiving a ZIP does **not** mean they were committed to the user's repository.
- **Review workflow:** Developer creates task branch/PR; SA reviews in isolated `ReviewPR/pr-<number>/` per `Design/11_HANDOFF_PR_WORKFLOW.md`; cleanup/Task closure only after owner confirms accepted/merged.

## 4. Approval versus evidence

Approval establishes *what to build*, not a `PASS` claim. The P212 oracle rows and M0 golden values remain **design expectations** until executable tests have been run by Developer and reviewed by SA. Code review findings must cite actual diff lines and test evidence.

## 5. Change control

If there is a contradiction between `150/151` and a pinned approved machine schema/registry, stop only the affected behavior and raise `BLOCKED — DESIGN CLARIFICATION` with exact fields and paths; do not quietly edit the frozen files or create unsupported codes. Any further contract revision requires a new SA addendum and owner decision.
