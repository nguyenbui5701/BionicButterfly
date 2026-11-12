# BionicButterfly — Phase 2.6 GitHub Baseline and Finding Reconciliation

- **ID:** BB-P26-BASELINE-099 | **Revision:** 0.1 | **Date:** 2026-11-12
- **Role:** Solution Architect (SA) | **State:** SOURCE EVIDENCE VERIFIED / G0-A1 NOT APPROVED
- **Repository:** https://github.com/nguyenbui5701/BionicButterfly/tree/main/Design

## 1. Frozen review input — evidence, not design approval

| Item | GitHub-confirmed data |
|---|---|
| Default branch | `main` |
| Current reviewed HEAD | `b6628e567813396c36d670d17e18f75e5cc443d3` |
| Phase 2.4 commit | `012e3bc7fe6231e95a5c1c5dd4b83093931f5e91` — `BionicButterfly Phase 24` |
| Phase 2.5 HEAD | `b6628e567813396c36d670d17e18f75e5cc443d3` — `BionicButterfly Phase 25` |
| Design directory | 102 top-level items, including Markdown, JSON manifests and `assets/` |
| P24 design docs | `84–90` present |
| P25 design docs | `91–98` present |
| Manifest evidence | `PHASE24_CONTENT_MANIFEST.json`, `PHASE25_CONTENT_MANIFEST.json` present |

The GitHub repository/branch/contents listing and commit list were read by connected GitHub tools in this SA review. A Git blob SHA is a content identity for that file, *not* an approval signature. Six critical docs (`84`, `85`, `87`, `93`, `94`, `95`) were locally byte-compared against the HEAD's Git blob IDs; all six matched. No change to repository was made.

## 2. Correct P25-F01, do not carry outdated issue forward

Previous `93` and `96` recorded **P25-F01** as a P0 blocker because Phase 2.4 was missing from `main` at an earlier reviewed commit. At this newer HEAD, the narrow factual predicate has changed: **Phase 2.4 and Phase 2.5 are present**.

- New disposition: `P25-F01 = CLOSED (SOURCE PRESENCE VERIFIED)` with evidence commit `main` HEAD above, contents listing, blob SHAs. The historical statement in `93` remains a correct *past observation*, not a current problem.
- Do **not** conclude all Phase 2.4 semantic decisions are approved: the docs still say **PROPOSED / UNSIGNED**. Git merge/push is content publication, not the owner's explicit G0-A1 design-freeze decision.
- If HEAD changes, repeat SHA check before any formal approval. A subsequent document's presence alone is insufficient evidence its semantic conflicts are resolved.

## 3. Evidence pins for the semantic review

| Document | Verified Git blob SHA at HEAD | Why reviewed |
|---|---|---|
| `57` input and errors | `833ccfcc0d976cee9504d080b1e12461e9b5c51d` | legacy input/result v1 wording; v2 proposal |
| `67` numerical SIM policy | `06a26f9d355fd4a3728d07f9d87e4653d00648fa` | 5ms/ARM/timeout boundary; not owner-approved |
| `68` atomic event contract | `4240405e6fde9a7fd87dce4e179e25e65341bc54` | historical priority vs P24 |
| `84` candidate FSM | `2cc1f50a50437e7c820c74909e374237906e1ce3` | same-tick/ARM/ACK candidate |
| `85` error compatibility | `8ee215206449c45d17627f530dbe2c5f5ddd6666` | result/error v2 distinction |
| `87` policy/replay trust | `debc8f0633f740d5c97c54b1eebf82dd4f92cb63` | approval and trace digest |
| `93` defect register | `3dd826459412cbbadb62022944f5d68f4881c028` | P25-F01…F12 source findings |
| `94` trace repair | `d5ea99889c906c14b63012648347fb585ea7f6a9` | non-recursive hash and append gate |
| `95` no-event tests | `a4f8e33d9af424bcfd0f5a49997909936adc1eb8` | S1/S2 choice and LOW interruption |
| `98` owner review packet | `21715e87e872f78beb6bbd608a53ab15ce894ed3` | review authority and remaining signoff |

Additional file SHAs and documentation update targets: `Design/105_G0A1_SOURCE_PATCH_MAP_AND_TRACEABILITY.md`. The phase 2.6 ZIP consists of **new documents only**; it does not silently overwrite prior accepted or proposed files.

## 4. Review boundary

- Confirmed product: V1 manually controlled by a real RC transmitter, true powered free flight as eventual goal; V2 autonomous flight deferred.
- G0-A1 reviewed subsystem: **host PC-only deterministic logic simulator**. It uses injected RF status and a virtual motion sink, no real serial/PWM/wing/current/IMU, no airworthiness claim.
- Source code/tests have **not** been run. The document checker that builds this artifact is an artifact integrity check, not a simulator execution or physical test.
- **Decision:** P25-F01 may be recorded CLOSED; P25-F02…F12 remain proposals/pending evidence as specified in `104–106`. No GitHub code write, `Source/` edit, `Task/` issue or owner approval is implied.
