# BionicButterfly — Phase 2.10 Owner R1.1 Decision Packet (UNSIGNED)

- **ID:** BB-P210-OWNER-138 · **Decision authority:** project owner · **SA recommendation:** **APPROVE R1.1 interface candidate with PC-only scope**, subject to review.
- **Status:** ALL SIX NEW DECISIONS PENDING. Owner's previous approval **only** covers R1, not the new wire/mixer/trace choices.

## 1. One-page decision table

| ID | Proposed decision | SA recommendation | Owner disposition |
|---|---|---|---|
| R11-D01 | v2 closed wire schema; exact `duration_us`, 6 event tags incl. SIM_RESET/ACK/catastrophe | APPROVE | PENDING |
| R11-D02 | six decimal places maximum, exact 1e6 scale pilot input | APPROVE | PENDING |
| R11-D03 | M0 (`L=F-S`, `R=F+S`) with virtual-only positive steer raises R relative L | APPROVE | PENDING |
| R11-D04 | closed JSONL record shapes and separate complete external digest | APPROVE | PENDING |
| R11-D05 | fixed new stimuli payloads `{}`; `NONE` not a wire type; no invented voltage event | APPROVE | PENDING |
| R11-D06 | host config mapping fixed to `sim-only-c0-v1` and `sim-map-v1` in v2 | APPROVE | PENDING |

## 2. Approval boundaries

Selecting APPROVE accepts the **six design choices** (and machine schema/mixer references) solely for a host PC simulator, without changing the R1 safety state machine, fault precedence, policy numerics, or permission model. It does not approve G1 implementation results, physical RC/PWM, servo and flight operations, autonomous V2 or any G0-B/G4 gate.

Approving v2 **does not** mean old v1 fixtures are validated as runtime cases. They need an explicit reviewed migration. `SIM_VOLTAGE_WARNING_RECOVERED` is intentionally excluded.

## 3. Review record to fill after owner response

```
Design base commit: 21e6fa6debdc63868693cdbba900f83b1869f0e2
New Phase 2.10 Git commit: PENDING
Decision: APPROVE | AMEND | DEFER   (none selected)
R11-D01..D06: PENDING
Machine schema SHA256s: see PHASE210_CONTENT_MANIFEST.json after package verification
SA: recommendation only; not owner approval
Owner explicit acknowledgement: NOT YET GIVEN
Actual simulator tests: NOT RUN
Physical flight: NO-GO
```

## 4. Next step if approved

After integrating the package, SA will verify Git file/blob hashes, register the owner's exact decision, reconcile the source index and only then reassess **full G0-A1 Design Freeze / Developer handoff readiness**. Issuing a `Task/` remains a separate owner-directed step. Do not mistake a Markdown decision sheet or a Git push for implicit signing.
