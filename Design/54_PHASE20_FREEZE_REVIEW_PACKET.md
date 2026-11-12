# BionicButterfly — Phase 2.0 Review Packet and Go/No-Go Decision Sheet

- **Document ID:** BB-G0PACK-054 · **Version:** 0.1 · **Date:** 2026-11-12
- **Status:** **DESIGN REVIEW PREPARED; NONE OF THE FREEZE SLICES APPROVED**
- **Scope:** V1 manually RC-piloted real flight; V2 autonomous only after successful V1.

## 1. SA executive recommendation

**Continue designing**, but do **not** approve full mechanical/electrical/flight design. There is a defensible path to **consider** a G0-A host-only design freeze once the latest owner repository and P0 document conflicts have been reconciled. G0-B and G4 still depend on unselected hardware, force/moment measurements and aircraft-specific contingency response.

| Gate | Decision today | Explicit rationale |
|---|---|---|
| **Phase 2.0 document packet** | **PREPARED LOCALLY / NOT COMMITTED** | new additive docs exist; owner Git revision unavailable |
| **G0-A1 pure PC core contract** | CANDIDATE, **NOT APPROVED** | `51` adequate to review, but latest `27/28` and requirements must be verified and accepted |
| **G0-A2 simulator UI** | DEFER until A1 scope accepted | ensure honest simulated labels, no hardware authority |
| **G0-B electrical bench** | HOLD | exact part selection, safe power path, GPIO/UART checks missing |
| **G0-B mechanical/rig** | HOLD | CAD part sizes, servo/load and guard measurements absent |
| **G0-C/G4 flight** | **NO-GO** | physical lift/control, flight-specific failsafe and site/approval missing |
| **V2 autonomy** | NOT IN SCOPE | owner deliberately deferred |

## 2. Outstanding P0 closure checklist

- [ ] `CF-01`: reconcile axis conventions and validate transforms across CAD, loads and control laws.
- [ ] `CF-02`: separate ground-safe stop and future in-air contingency; no implicit lift removal.
- [ ] `CF-03`: control authority/lift/stability measured before any G4 claim.
- [ ] `CF-05`: actual receiver RF-health behavior under radio loss established.
- [ ] `CF-07`: safe 2S/1S power topology and board/servo interface verified before energizing.
- [ ] `CF-11`: no browser takeover or armed calibration.
- [ ] `CF-16`: actual Git baseline and role rules reconciled.
- [ ] `CF-18`: no misleading “committed” statement without Git evidence.

For a narrowly approved PC-only slice, the *physical* blockers can remain `OPEN` if they are explicitly excluded and no physical outputs are possible. `CF-04`, `CF-08`, `CF-10`, `CF-11`, `CF-13`, `CF-16`, `CF-17` are **within** the PC-only contract and must be resolved before G0-A1 approval.

## 3. Stage selection matrix: do not mix authorization levels

| Owner decision text (example only) | Permitted next phase | Not implied |
|---|---|---|
| `CONTINUE DESIGN` | SA refines Design/ and documents decisions | code tasks, build, flight |
| `APPROVE G0-A1 CONTRACTS AT <commit>` | SA may propose a separate future PC-core task after scoped handoff decision | ESP32 firmware flashing / power-up |
| `APPROVE G0-B1 BENCH DESIGN AT <commit>` | after review, developer/tester may plan bench implementation/test tasks | G3 restrained wings or G4 flight |
| `APPROVE G0-C/G4 FLIGHT PLAN AT <commit>` | only after all measured prerequisites and explicit trial signoff | success is guaranteed or V2 autonomous scope |

**These are templates, NOT instructions for the owner to approve now.** The current request authorizes design continuation only.

## 4. Design package read order for future review

1. `48` identify source-of-truth limitations and inventory.
2. `49` resolve P0 contradictions against actual `Design/`.
3. `50` identify which approval slices are independent.
4. `51` consider strictly host-only contracts, *not code*.
5. `52` define test requirements and status/evidence.
6. `53` recheck SA/Dev role boundaries, commits and future PR workflow.
7. `55` review evidence demands and open owner choices.
8. Read the current owner versions of `02`, `14`, `15`, `16`, `19`, `27`, `28`, `30`, `37`, `42` before recording a final freeze decision.

## 5. Approval worksheet (unfilled)

```text
Review ID: P20-G0-____
Owner repository HEAD: UNKNOWN
Reviewed Design file revisions: UNKNOWN
Scope requested: G0-A1 / G0-A2 / G0-B1 / G0-B2 / G0-C
Conflicts closed (CF IDs + evidence): NONE CONFIRMED
Tests/design checks passed: NONE CONFIRMED
Remaining hazards/exclusions: LIST REQUIRED
Authoritative requirement and ADR revisions: UNKNOWN
SA recommendation: CONTINUE DESIGN
Owner explicit decision: PENDING
Owner decision date/reference: PENDING
Implementation task authorization: NONE
Hardware energization authorization: NONE
Flight authorization: NONE
```

The packet is a *review deliverable*, not proof that V1 can fly. It does not add developer work to `Task/`.
