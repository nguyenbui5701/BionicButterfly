# BionicButterfly — Phase 2.3 GitHub Public Baseline Check

> **Phase 2.4 review note (2026-11-12):** See the candidate corrective addendum at the end and `84–90` before treating older priority/approval text as normative. **Pending owner approval; not code or flight authorization.**

- **ID:** BB-P23-BASE-075 | **Rev:** 0.2 | **Date:** 2026-11-12
- **Role:** Solution Architect (SA) | **Status:** `REMOTE_UNVERIFIED`, not a claim that the repo is private or that the owner's push failed.
- **Declared repository:** `https://github.com/nguyenbui5701/BionicButterfly/tree/main/Design`
- **Scope:** `Design/` on branch `main`; do not modify `Source/` or `Task/`.

## 1. Attempted verification and honest conclusion

| Check channel | Observed outcome in this response | What it proves |
|---|---|---|
| GitHub HTML page | Direct page open returned cache miss / content unavailable | **Cannot verify** tree or commit; does NOT imply repository remains private |
| GitHub REST `contents/Design?ref=main` | Web reader could not access API endpoint | **Cannot verify** tree or file hashes |
| Exact public search `site:github.com/nguyenbui5701/BionicButterfly` | Results indexed other similarly named repositories, not target | No reliable positive confirmation or denial; recently public repo might not be indexed |
| Read-only `git ls-remote` in isolated container | DNS resolution of github.com failed | Local environment cannot validate remote Git HEAD |
| Connected GitHub provider | Suggested to user; **not established connected** | Access pending user's explicit connection if desired |

**No HEAD SHA, file list, latest push timestamp or remote content can be claimed as verified**. The user's statement that the repository is now public is accepted as a user-provided status, but is distinct from independent content retrieval. This is a real baseline blocker for full source reconciliation. Do not present a 3rd-party similarly named repo as the user's project.

## 2. Actual materials analyzed locally

Phase 2.0: `/mnt/data/BionicButterfly_Phase20_System_Design_Freeze/Design/` — files `48–55` + prior local manifest.

Phase 2.1: `/mnt/data/BionicButterfly_Phase21_Software_Architecture_Design/Design/` — files `56–65` + prior local manifest.

Phase 2.2: `/mnt/data/BionicButterfly_Phase22_Simulator_Policy_Freeze/Design/` — files `66–74` + prior local manifest.

These are **local artifacts from earlier work**, not a clone of the latest owner `main`. This Phase 2.3 package adds **only** `75–83`, so it avoids overwriting any older file on `main`. File `PHASE23_LOCAL_SNAPSHOT_ATTESTATION.json` includes SHA-256 of locally inspected inputs, allowing a future real Git tree to be compared exactly. It is NOT a remote Git attestation.

## 3. Required remote reconciliation before any G0-A1 freeze

1. Establish exact `main` full commit SHA and UTC timestamp using a trusted GitHub read or an owner-supplied read-only Git command result.
2. Enumerate `Design/48…74` exact paths and SHA-256 file bytes from that commit; compare with the local snapshot manifest. Record absent files, same-content files, and files edited after these packages.
3. Inspect actual `Design/` for numbered-file collisions `75…83` and any newer phase: if present, **do not overwrite**. Resolve numbering and content under a new SA ADR.
4. Reconcile host-scope conflicts `P22-C01…12`, new findings `P23-F01…` and older `CF-*` against the actual current source text; a later document number does not patch earlier prose automatically.
5. Request explicit owner approval of a **bounded** G0-A1 design baseline with that exact commit SHA and policy digest. Creating or pushing this ZIP is not approval.

### Read-only owner-side verification commands (optional, NOT push commands)

```powershell
# Run inside the root of the local BionicButterfly repository if you want to share evidence
# git rev-parse HEAD
# git status --short
# git ls-tree -r --name-only HEAD Design
# git log -1 --format="%H %cI %s" -- Design
```

No user action is needed to read this design package. For direct GitHub repository review in ChatGPT, a GitHub connector can be connected by the user; connection is an explicit user action.

## 4. Source-of-truth ordering

- **Scope and product intent:** owner messages (V1 manually RC-piloted real free flight, V2 autonomous later; owner-controlled push).
- **Design file content:** actual owner Git commit *when retrieved*, not a local ZIP assumption.
- **Proposed safety/API policy:** latest *unapproved* G0-A1 drafts (`56–74`), subject to higher-authority signed design decisions.
- **Hardware and airworthiness:** physical measurements and G2/G3/G4 approvals; never inferred from host simulator.

**SA disposition:** continue additive design review now; leave Git reconciliation `BLOCKED_BY_ACCESS`, not incorrectly `DONE` or `FAILED`.

## Phase 2.4 POST-VERIFICATION UPDATE (rev 0.2; supersedes historic access limitation)

**NEW OBSERVATION:** on 2026-11-12 the connected GitHub integration successfully read public `nguyenbui5701/BionicButterfly`, `main@16d5054ea951b2e52e90c7f81ea2767a7ba82b92`, including the entire top-level `Design/` listing and Phase23 file blobs. Therefore, the prior `REMOTE_UNVERIFIED` status in v0.1 is **closed for repository access**, not an indication that Git was actually private then. Full attestation `88_REPOSITORY_MAIN_BASELINE_AND_RECONCILIATION.md`. Older text is retained only as historical note of environment access at original drafting.
