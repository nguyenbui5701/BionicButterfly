# BionicButterfly — Phase 2.7 Verified Git Baseline & Architecture Review Scope

- **ID:** BB-P27-BASELINE-107 | **Rev:** 0.1 | **Date:** 2026-11-13
- **Owner:** Solution Architect (SA) | **Status:** EVIDENCE VERIFIED / OWNER DECISION PENDING
- **Review target:** https://github.com/nguyenbui5701/BionicButterfly/tree/main/Design

## 1. Exact remote snapshot actually inspected

| Item | Verified from connected GitHub source | Meaning |
|---|---|---|
| Branch | `main` | Source selection, not an approval |
| HEAD at review | `be85c3e28a2ba6891f2bd6199a58fe0ce564f305` | **Pin** for this review; recheck if HEAD advances |
| Repository visibility | public (earlier verification, same connected repo) | Not a safety claim |
| Phase 2.4 + 2.5 | `84–98` present | Old source-absence blocker closed |
| Phase 2.6 | `99–106` present, with `PHASE26_CONTENT_MANIFEST.json` | Source-publishing blocker also closed |
| GitHub `Design/` | 112 top-level entries in current listing | Includes documents, manifests and assets |
| Simulator implementation tests | none checked or executed by SA in this phase | No runtime PASS claim |

The following Phase 2.6 documents were **byte-equivalent by Git blob SHA** to the existing local snapshot: `99` through `106`. Their exact SHA values were checked against connected GitHub listing and local Git blob calculations; `108` includes a decision-level reading of them. Git blob SHA and manifest SHA-256 are **content identities**, not signatures granting approval.

| Source file | Blob SHA confirmed at HEAD |
|---|---|
| `99` | `f95ec37ffae71442388cadb733910855154f9005` |
| `100` | `70c1bb80e0a0ff5025d6c0fe3c0ee028afb4377c` |
| `101` | `7729ec0a4d39818b4d901b48099b069b351ee5c9` |
| `102` | `6e292c0a0736e47ea718d437a39bed427514f16e` |
| `103` | `68a7800fb4242282b6364a0ab8c30ce75700e97f` |
| `104` | `d4b339e8ad7e782b6181737e6abdc396d7632904` |
| `105` | `6e8166a51bd0166de163912aa5607fbd7d8e33e1` |
| `106` | `abd353f0f41104f9bb12d06217fc9f464471f460` |

## 2. Proven vs proposed vs untested

- **Verified externally:** remote HEAD, contents of published Phase 2.6 documents and their Git blob identities; closure of the old **source-not-present** finding for Phases 2.4–2.6.
- **Designed but UNSIGNED:** D-075…D-090; `100–103` safety/policy/trace contracts, inherited earlier drafts; PC_SIM_ONLY fixed test proposals.
- **Unrun:** PC-A, G1B, P22, P23, P24, P25, P26 and Phase 2.7 oracle executions. This phase evaluates document logic only.
- **Out of scope:** receiver signal from actual RF, servo/PWM, MCU pins, motor/wing tests, 6-DOF flight modeling fidelity, IMU attitude stabilization, site/legal/airworthiness, autonomous V2.

No source code, tests, CAD, prototype hardware or flight performance has been inspected/tested as part of Phase 2.7. Design freeze (G0-A1) is a **future owner decision**; no Developer handoff authorization is given merely by a document release.

## 3. SA review method and hierarchy

1. Treat `02` product requirements, `27–29` architecture/safety and `51` G0-A original scope as constraints, not canceled by a later simulator file.
2. Treat `84–87`, `93–95` as *historical candidate proposals*; `100–103` are the consolidated **current candidate** pending owner acceptance, NOT automatic normative supersession.
3. Use `108` to decide D-075–090; use `109–110` for precise semantic review; `111` for executable future oracle requirements; `112` for eventual source reconciliation; `113` as a decision packet.
4. Recheck branch HEAD, file hashes and any changed older sections before actual approval or copy-back. This ZIP only adds `107–113` and companion study assets.

## 4. Scope boundary to be preserved after any approval

`G0-A1` can authorize only the **design** of a deterministic, host-only, hardware-inert simulator core: strict scenario validation, independently authorized immutable SIM policy, virtual clock/event normalization, one safety decision per tick, bounded virtual commands, stable traces/replay and controlled rejection/reporting. It does **not** authorize live actuation, firmware flashing, G0-B electrical testing, G3 wing-force testing, or G4 free-flight. Physical V1 remains human-piloted RC; V2 self-flight is deferred.

**SA disposition:** baseline evidence VERIFIED; design review remains PENDING owner review.
