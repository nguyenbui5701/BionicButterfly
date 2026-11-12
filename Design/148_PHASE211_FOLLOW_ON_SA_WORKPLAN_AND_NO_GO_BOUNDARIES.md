# BionicButterfly — SA Next Action Plan After Phase 2.11

- **Doc:** BB-P211-NEXT-148 · **Owner-selected milestone:** real V1 butterfly free flight with physical RC; autonomous V2 later.

## 1. Immediate SA actions in order

1. **Repository gate:** compare newly pushed Phase2.11 source and approval/index/manifest bytes against this package. If any SHA changed, run change control before declaring that commit equivalent.
2. **Handoff detailing:** close exact parse validation subcodes / path envelope only as a versioned clarification. Keep output result v2 and v2 scenario schema bytes frozen unless owner specifically approves a change.
3. **Task planning for first host-only module:** following owner authorization, issue a limited Developer handoff for schema+M0 logic with no serial device, PWM, hardware abstraction, UI control or aircraft physics.
4. **Review PR:** use `ReviewPR/` isolated checkout; verify semantic diffs and all failure-mode tests, plus evidence of never opening physical IO.
5. **Future G1:** expand test-run coverage only after a runnable implementation with trusted policy/engine revision, actual assertions and independently generated replay hashes.

## 2. Independent parallel design path to real V1 flight

Do not allow PC simulator progress to obscure the real airborne goal. Separate G0-B must eventually select receiver/transmitter/servo/BEC and verify datasheets, pin/boot behavior, mass/CG, root hinge dynamics and calibrated force/moment authority. G4 must decide airborne radio-loss/power/flight contingency on measured aircraft evidence. The 2-servo 4×2 effectiveness matrix is underactuated; passive stability may help but has **not been proven**. Nothing in R1.1 changes those blockers.

## 3. Out-of-scope and no-go

- No `Task/` file, firmware code, source integration or GitHub write in this phase.
- No bench servo action, wing restraint test or free flight authorized by PC-only documents.
- No claim that `P210-*` tests passed in implementation. The provided scripted static checks are not executable G1 flight controls.
- Do not create a V2 autonomous navigation requirement in the V1 PC simulator baseline.

## 4. Upcoming decision point

After Phase2.11 is on `main`, the next SA deliverable can be **Phase 2.12 — Scoped Developer Handoff and Parser-Diagnostic Closure**. That phase should avoid generating another broad stack of design documents; instead it closes the one diagnostic taxonomy gap and produces the **first deliberately small development task only if the owner asks for it**.
