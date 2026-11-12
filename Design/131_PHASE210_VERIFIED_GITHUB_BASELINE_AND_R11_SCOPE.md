# BionicButterfly — Phase 2.10 Git Baseline and Architecture Scope

- **ID:** BB-P210-BASE-131 · **Date:** 2026-11-13 · **Role:** Solution Architect (SA)
- **Baseline:** [`Design@21e6fa6debdc63868693cdbba900f83b1869f0e2`](https://github.com/nguyenbui5701/BionicButterfly/tree/21e6fa6debdc63868693cdbba900f83b1869f0e2/Design)
- **Git HEAD verification:** GitHub connection reported commit message `BionicButterfly Phase 29`; files `123–130` are present with the exact Git blob SHAs below.
- **Status:** DESIGN REVIEW / **R1.1 CANDIDATE, NOT OWNER-APPROVED**. Owner approval of R1 is preserved.

## 1. Read-only provenance checks

| Source document | Git blob SHA | Review role |
|---|---|---|
| `123` | `0721598b50c503bfc6b60954638e6aac2b317ab7` | previous source-integrity proof |
| `124` | `7a1a078b05eae5562289500d81cd773db5ee7588` | locked R1 scope |
| `125` | `838878a14857b32207cee1f6a0d8b32bcdc52d0d` | P29-F01–F07 finding baseline |
| `126` | `1ff46dc60abda7ea592dce6654635054abf58f2a` | interface change request |
| `127` | `f61d30ae5e1d35476f6c24804f4c4a5ca6e4f183` | regression oracle plan |
| `128` | `c6e995db26ab94f677f215a0cf50253591a7f7e3` | change governance |
| `129` | `7d6f6620d20940b69d03c346042421dc3fbd5f58` | SA HOLD verdict |
| `130` | `77896a548caf0f2c4ea15123c57323746df05cca` | developer handoff HOLD |

All 8 local source bytes recompute to the Git blob SHAs found on main. No change to `Source/`, `Task/` or remote repository was made.

## 2. Approval and freeze boundaries

- **Approved:** core R1 PC_SIM_ONLY `114–124` owner-decision domain and safety policy digest `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. The R1 numeric policy is immutable.
- **Open P0-HANDOFF:** P29-F01 exact wire event input; P29-F02 deterministic two-output mixer; P29-F03 closed trace record shapes.
- **New selection proposed:** R1.1 wire **schema version 2**, M0, fixed-point 6-place decimal input, typed trace record field set. These are observable choices not implied by approving R1; treat as separate owner decisions.
- **Outside:** physical ELRS/CRSF/UART, ESP32, servo pulse, wing forces, real failsafe, flight G4, cockpit UI, autonomous V2.
- **No runtime claim:** schemas and golden files are DESIGN artifacts, not tests of a running simulator or proof of hardware safety.

## 3. Documents introduced

`131–139` are additive; JSON schemas live in `Design/contracts/`, design vectors in `Design/fixtures/`. `131` is the baseline; `132/133/134` are normative **candidates**; `135–137` assess migration/verification; `138` is the explicit owner decision sheet; `139` records handoff readiness. Nothing in this package silently supersedes the approved R1.
