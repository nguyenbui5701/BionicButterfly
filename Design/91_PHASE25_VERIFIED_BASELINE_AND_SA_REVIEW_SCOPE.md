# BionicButterfly — Phase 2.5 Verified Baseline & SA Review Scope

- **Document:** BB-P25-BASE-091 | **Revision:** 0.1 | **Date:** 2026-11-12
- **Role:** Solution Architect | **Disposition:** VERIFICATION OF BASELINE ONLY; DESIGN NOT FROZEN

## 1. Sources distinguished by authority and actual access

| Category | Source and proof | Status |
|---|---|---|
| Repository GitHub | `nguyenbui5701/BionicButterfly` public, default branch `main`, retrieved using GitHub connector on 2026-11-12 | VERIFIED REMOTELY |
| `main` HEAD | `16d5054ea951b2e52e90c7f81ea2767a7ba82b92` | VERIFIED REMOTELY in Phase 2.5 |
| Design 01–83 | GitHub `Design/` directory index, including README-like numbering gaps 04/06/08/09 and 4 manifests; 85 direct items at directory root | VERIFIED directory names, not that all contents were personally audited |
| Phase 2.3 source of truth | `75–83` on that Git tree; `78` and `83` content retrieved for this review | VERIFIED selected contents |
| Phase 2.4 normative candidates | Locally delivered ZIP `BionicButterfly_Phase24_Architecture_Conflict_Resolution.zip`: `84–90`, 13 proposed revisions and manifest | LOCAL CANDIDATE, NOT ON MAIN |
| Phase 2.5 files `91–98` | Additive SA review files bundled separately; not in Git | LOCAL DELIVERABLE |

**Important:** Git blob SHA identifies file content, not the same thing as SHA-256. The ZIP manifest records SHA-256 of the deliverable; Git commit identifies a tree. No repository write or code task occurred.

## 2. Reproducible baseline verification protocol before any future freeze

1. Read repository visibility, default branch, HEAD SHA, `Design/` tree from GitHub, and log retrieval date.
2. Enumerate all `84–90` files and the Phase24 edited 13-file set. If absent, **do not** claim that G0-A1 freeze is based on Phase24 in `main`.
3. Before using revised `57/58/59/61/67/68/69/70/71/72/75/77/83`, compare each current blob SHA with the `source_git_blob_sha` recorded in Phase24 manifest. If mismatch, review that diff manually; never overwrite a newer user edit blindly.
4. After any new user push, capture a fresh HEAD and digest the *exact* revision of `84–90`, `67` policy and this Phase25 packet. Pin references in approval record.
5. A commit containing a candidate means **published**, not **approved**. Approval must reference the specific commit and scope separately.

## 3. Source relationship

`57/58/59/61/67–71/78/80` are historical candidates. `84–87` are proposed semantic corrections, not currently effective normative contracts. `88–90` propose repository, readiness and ADR governance. This Phase25 package evaluates their readiness, **not** a new third competing state machine.

## 4. Changes prohibited during this SA phase

No `Source/` implementation, no `Task/` issuance, no PR, no owner Git push, no board/servo energization, no flight approval. Only design review documents and candidate corrections, clearly marked PROPOSED.

## 5. Direct GitHub links verified

- Repository: https://github.com/nguyenbui5701/BionicButterfly
- Design: https://github.com/nguyenbui5701/BionicButterfly/tree/main/Design
- Commit: https://github.com/nguyenbui5701/BionicButterfly/commit/16d5054ea951b2e52e90c7f81ea2767a7ba82b92
- Candidate documents from Phase 2.4 are local, NOT claimed as Git links.
