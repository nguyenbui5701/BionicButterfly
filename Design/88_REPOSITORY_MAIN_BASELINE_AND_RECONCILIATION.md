# BionicButterfly — Phase 2.4 Verified GitHub Main Baseline & Reconciliation

- **ID:** BB-P24-REPO-088 · **Version:** 0.1 · **Checked:** 2026-11-12
- **Source:** connected GitHub repository **`nguyenbui5701/BionicButterfly`**, branch `main`.
- **Verified HEAD:** `16d5054ea951b2e52e90c7f81ea2767a7ba82b92` (commit message `BionicButterfly Phase 23`). Public repo and directory readable.
- **Source URLs:** https://github.com/nguyenbui5701/BionicButterfly/tree/main/Design ; https://github.com/nguyenbui5701/BionicButterfly/commit/16d5054ea951b2e52e90c7f81ea2767a7ba82b92

## 1. Observed inventory

GitHub contents endpoint returned **85 top-level items** in `Design/`: **79 `.md` documents** (files 01–83 with intentionally unused numbers 04,06,08,09), **5 JSON manifests**, and one `assets/` directory. Exactly `75–83` exist and have content blob SHAs matching the prior Phase23 local snapshot, which was checked using Git blob hashing. Key Phase 21–22 docs `57`, `58`, `67–71` were also verified equal to the local previously supplied files by SHA. This resolves the prior inability to access GitHub and establishes a verifiable source baseline, **not owner approval of safety contracts**.

### Confirmed Phase 2.3 blob identities

| Path (under `Design/`) | Observed Git blob SHA |
|---|---|
| 75_PHASE23_PUBLIC_REPO_BASELINE_STATUS.md | `a98f1292b63bd58149758e7e0676b95edd3a21c3` |
| 76_END_TO_END_HOST_CONTROL_PATH_REVIEW.md | `bc56c904e6acc837cc09041b382459e60f0a7c4f` |
| 77_SEMANTIC_CONFLICT_AND_HAZARD_REGISTER.md | `b179fd077baa799a0258af69d2a2ef006fba5bf2` |
| 78_HOST_API_NORMATIVE_FREEZE_CANDIDATE.md | `197b3af002976695b5546d2e40e1f1335d873729` |
| 79_PHASE23_E2E_TEST_ORACLES.md | `7e4543f4e25470edb9d511e07f9b7f98d6d73c4b` |
| 80_REPLAY_EVIDENCE_AND_RUN_ID_POLICY.md | `91811f3a53eab22e4d9fa8e74351cb245673f36e` |
| 81_DECISION_DEPENDENCY_AND_CORRECTION_PLAN.md | `b4012913b97c16db6dd9e34f14c0bb6af509ba6a` |
| 82_PHASE23_ADR_SUPPLEMENT.md | `0184edf461797923e4f2d800dced4e9d729b7837` |
| 83_PHASE23_G0A1_FREEZE_REVIEW_PACKET.md | `8bc59ff9ac68dd374d2325be25e9241d4a86c245` |

The `commit SHA` identifies an entire tree; individual Git blob SHA above identifies one file's content, **not SHA-256**. Phase 2.0–2.3 manifests provide a separate artifact-integrity ledger. Verify HEAD immediately again before applying any file replacements; **if branch moved, reconcile the new diff rather than applying stale files without review**.

## 2. Explicit disposition of older findings

| Finding | Current evaluation | Closing evidence required |
|---|---|---|
| `P23-F12` remote inaccessible | **CLOSED — repo accessible, exact SHA & Phase23 blob identity established** | already observed 2026-11-12; no owner action necessary for access alone |
| `P23-F01/02/04/05/06/10` conflicting priorities/schema/arm | **RESOLUTION PROPOSED** in `84–86` | versioned acceptance + updated source documents + tests |
| `P23-F03/07/08/09` replay/trust/trace failures | **RESOLUTION PROPOSED** in `85`, `87` | owner accepts format/trust and implements testable rules later |
| `P23-F11` SIM_ONLY policy sample authority | **REMAINS OPEN until policy approved** | explicit external approval ref/digest and safety limits |

Do not overwrite `75`/`83` history without a clear note that their original statement 'repo unavailable' was true **at document authoring time** and was superseded only after this new verification. Avoid rewriting history as if the older snapshot had actually been verified then.

## 3. Safe update plan (no Git write performed)

This Phase24 package includes proposed **revisioned addenda** to selected existing documents to steer readers toward the candidate normative contract. Files are rooted under `Design/` and are not automatically committed. Compare changes against the SHA inventory before replacing an already edited local file. No `Source/`, `Task/` or PR code modifications are part of this package.

After owner accepts the particular G0-A1 decisions and source patch set, SA may recommend recording an approved baseline commit and digest. **An uploaded ZIP or committed Design file is not implicit APPROVED status.**
