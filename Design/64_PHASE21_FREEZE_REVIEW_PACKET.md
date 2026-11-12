# BionicButterfly — Phase 2.1 G0-A1 Freeze Review Packet

- **ID:** BB-G0A-REVIEW-064 · **Rev:** 0.1 · **Date:** 2026-11-12
- **Status:** **DESIGN PACKAGE PREPARED, NOT FROZEN, NOT OWNER APPROVED**
- **Purpose:** summarize a *bounded* PC-simulator design, flag unresolved assumptions and prepare for an eventual explicit approval rather than pretend that physical V1 design has been released.

## 1. Current factual baseline

- Owner confirms `Design/` files through Phase 2.0 have been pushed to `main` and gives GitHub URL. Public web retrieval and raw/API URL attempts **did not return the repository contents in this session** (cache/access limitation; repository may be private but that is not established). **Do not claim a reviewed SHA or remote commit.**
- This Phase 2.1 ZIP **adds** `Design/56–64` without replacing owner `Design/01–55`; contents are locally generated and verified against the *locally available Phase 2.0 packet*, not the remote HEAD.
- Owner-confirmed scope: real RC-piloted free flight is the product V1; autonomous flight V2. GitHub pushing remains owner-managed; no SA access to the owner's Windows local repository.
- Physical uncertainty persists: actual airframe mass, wing force/moment, two-servo controllability, in-air failsafe, power and RC hardware all unverified.

## 2. Decision recommendation

| Scope | Review result | Rationale |
|---|---|---|
| Phase 2.1 doc deliverable | **PREPARED / local validation only** | new additive contracts and test design exist |
| G0-A1 host-only core/API design freeze | **REVIEW CANDIDATE — NOT APPROVED** | remote HEAD not reconciled; SIM policy numeric parameters and approved canonical serialization not settled |
| G0-A2 UI application build | **DEFER** | first accept host-only core bounds and event schema; UI is noncritical |
| G0-B electrical/servo/CAD | **HOLD** | exact hardware and instrumented test proof absent |
| G0-C/G4 free flight | **NO-GO** | actual force, control/recovery and flight risk case unproven |
| V2 autonomy | **OUT OF SCOPE** | deliberately deferred by owner |

## 3. Candidate owner decisions (not implicitly approved)

| Decision | Proposal | Required closure |
|---|---|---|
| `D-051` | host-only core has no physical hardware drivers | dependency audit and owner acceptance |
| `D-052` | strict JSON input, typed records with provenance | schema field list and unknown-data semantics approved |
| `D-053` | atomic same-time event evaluation + conflict rejection | tick semantics and replay acceptance approved |
| `D-054` | SIM contingency never becomes physical in-air policy | review `58` with `27`, `49` CF-02 |
| `D-055` | SIM_ONLY policy immutable while armed | decide profile revision and persistence approach |
| `D-056` | virtual scheduler/replay with bounded budgets and trace integrity | approve exact precision, max duration/size and resource controls |
| `D-057` | UI read-only with no actuator authority | reviewed API/security boundary |
| `D-058` | freeze requires exact Git baseline + signoff | actual HEAD and conflict closure evidence |

## 4. Required closure before G0-A1 can be approved

1. Verify exact `main` commit and owner changes to `Design/02,05,16,27,28,29,30,32–36,48–55`; do not overwrite later edits. Record hashes and changes for the approved subset.
2. Address **host-scope** conflicts CF-04, CF-08, CF-10, CF-11, CF-13, CF-16, CF-17, CF-18 from `49` with actual document paragraph/revision evidence; physical blockers CF-02/03/05/07 remain explicitly excluded from host freeze, **not closed**.
3. Choose exact `SimPolicy` numbers **for simulation only**: arm qualification, neutral windows, valid-frame age, virtual envelope, scheduler step, event limits, replay precision and log format. Record rationale and boundary tests.
4. Resolve whether core replay uses fixed evaluation ticks and atomic batches as recommended here; if alternative event-driven microsteps are preferred, revise `59`, `58` and `63` together.
5. Record owner decision `APPROVE / REWORK / DEFER` for the *bounded host slice* and cite a Git commit; approval does not create a task unless explicitly instructed.

## 5. Explicit 'not implemented' / nonclaims

- No `Source/`, `Task/`, ESP32 binaries, UI application or test harness was created by Phase 2.1.
- No G1 PC-A or G1B simulation test has run; only static validation of this new document package may be asserted after checking.
- No source or CAD from third-party repositories was copied; references are contextual only.
- No attempt to drive servo, energize LiPo, open a physical RF link or fly the robot was made.
- Phase 2.1 does not override signed owner decisions, nor does “continue” mean automatic approval.

## 6. Review record template

```text
PHASE21-G0A-REVIEW-ID:
Owner main SHA (verified, exact):
Design subset file/revision/hash list:
Host-only conflict IDs and source paragraphs:
SimPolicy version and exact SIM_ONLY numbers:
Scheduling and JSON schema decision:
Test scope PC-A01–20, G1B-01–24, TIME/CFG/SEC:
Safety exclusions (hardware, servo, flight):
Reviewer and date:
Owner decision (APPROVE/REWORK/DEFER):
Task authorization (separate yes/no):
```

## 7. Next bounded SA design topic

If this G0-A1 concept remains pending, next SA review can consolidate `49` document conflicts against the real Git snapshot and produce a precise proposal for SIM_ONLY policy constants. If the owner later approves G0-A1 and separately requests Developer work, a limited `Task/` may be issued, explicitly forbidding physical I/O. No GitHub push command is emitted here.
