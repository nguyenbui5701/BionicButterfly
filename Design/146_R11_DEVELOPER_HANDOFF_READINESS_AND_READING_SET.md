# G0-A1 — R1.1 Developer Handoff Readiness Boundaries (NOT A TASK)

- **Doc:** BB-P211-HANDOFF-146 · **Owner-approved interface choices; no implementation executed.**

## 1. What can be handed off without ambiguity *after an explicit Task issuance*

**Potential scoped first work package (not created now):** pure host-side scenario JSON v2 validation, schema binding and exact integer M0, as **isolated deterministic functions**, with rejection before state creation and no OS/device adapters. This can be evaluated independently of the full safety FSM. It must not claim full G0-A1 end-to-end conformance merely from unit tests.

**Later packages:** immutable policy/engine revision trust binding; virtual event queue + normalized full batch + R1 FSM; append-before-publish trace; integrated replay and negative tests; UI only after core design/verification. Actual module/file layout is a Developer design choice *only within* pinned interfaces; unexpected design changes must be raised to SA.

## 2. Mandatory reading set

| Type | Exact references |
|---|---|
| SA process/rules | `07_AI_CODING_RULES.md`, `10_SA_OPERATING_RULES.md`, `11_HANDOFF_PR_WORKFLOW.md` |
| Scope & safety | `02_V1_REQUIREMENTS.md`, `115`, `116`, `117`, `118`, `124` |
| Owner decisions | `114`, `138`, `140`, `141`, approval JSON |
| R1.1 interface | `132`, `133`, `134` and five machine contract JSONs in frozen index |
| Test design | `120`, `127`, `136`, `144` and golden fixtures |
| Change control / review | `119`, `128`, `145`, `147` |

All referenced files must come from **the pinned Git commit**; new Phase2.11 docs should be integrated and HEAD rechecked before issuing a task. Filename `CANDIDATE` is historical; exact pinned hash + decision record grants design authority, not filename spelling.

## 3. Handoff gates

| Gate | Status | Required next evidence |
|---|---|---|
| H0 scope and owner interface decisions | PASS_DESIGN | Verified Git SHA + explicit owner approval |
| H1 scenario wire/schema and M0 | PASS_STATIC_DESIGN | Machine schema and 12 golden values verified |
| H2 trace byte contract | PASS_STATIC_DESIGN | Closed schema and reference SHA verified |
| H3 full parser diagnostic code registry | **HOLD_FOR_FULL_PARSER_TASK** | Exact approved error category-to-issue mapping |
| H4 trusted host run environment | **NOT INSTALLED** | Bind policy/engine/scheduler revisions in immutable host allowlist |
| H5 runnable G1 conformance | **NOT RUN** | Engine commit, fixture execution, logs, negative tests |
| H6 real hardware / flight | **NO-GO** | Completely separate G0-B/G4 |

## 4. Preconditions for future Task creation

- Separate owner signal to issue a development task after this Phase2.11 baseline has been pushed/confirmed.
- Every task names permitted module scope, excluded physical integrations, exact Git SHA, baseline schema hashes and test acceptance IDs.
- Developer cannot edit normative policy, widen schema, change mixer, add firmware IO or set `approved=true` in a file to bypass the review.
- SA reviews PR only in isolated `ReviewPR/`, never writes directly to production branch without owner authorization.

This is a **handoff-readiness assessment**, not a `Task/*.md` or developer implementation request.
