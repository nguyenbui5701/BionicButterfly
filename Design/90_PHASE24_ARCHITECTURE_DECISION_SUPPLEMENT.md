# BionicButterfly — Phase 2.4 Architecture Decision Supplement

- **ID:** BB-P24-ADR-090 · **Version:** 0.1 · **2026-11-12** · **Status:** ALL **PROPOSED**, no owner signoff.
- **Reference:** D-067…D-074 in `82`, Phase23 findings in `77`, candidate solutions `84–89`.

| Decision | Proposal | Why / rejected ambiguity | Status |
|---|---|---|---|
| **D-075** | Normalize **all valid control frames for tick** before accepting any switch LOW/HIGH; conflicting batch is denied and if armed enters SIM contingency | prevents disarm from rejected LOW while contradictory HIGH exists | PROPOSED |
| **D-076** | Catastrophic fault dominates same-tick RESET; RESET revokes arm but does not erase active fault | deterministic latch safety | PROPOSED |
| **D-077** | Recovery ACK uses prior committed LOW qualification; final LOW+ACK same tick insufficient; catastrophic latch is terminal within G0-A1 run; in-run recovery requires a future versioned contract | no same-tick recovery shortcut | PROPOSED |
| **D-078** | Retain input scenario schema v1; propose **separate result/error contract v2** for `E_DUPLICATE_EVENT_ID` vs `E_CONTROL_BATCH_CONFLICT` | do not reinterpret v1 name in place | PROPOSED |
| **D-079** | Canonical replay digest excludes volatile execution ID and visualization, identifies exact contract/policy/engine/schedule | deterministic cross-run evidence | PROPOSED |
| **D-080** | External trusted policy approval digest and immutable configuration; input JSON cannot grant itself authority | scenarios are untrusted data | PROPOSED |
| **D-081** | Incomplete trace/quota errors explicitly fail without PASS and inhibit virtual sink; complete vs partial SHA separated | no silent successful-result fabrication | PROPOSED |
| **D-082** | Git `main@16d5054…` is **verified** baseline; exact HEAD and blob SHA must be checked before overwrite; physical G4 stays NO-GO | closes repo access blocker without confusing with safety approval | PROPOSED (repo access verified) |

**Decision status is not inferred from an owner request to continue or from files appearing on GitHub.** Any approved freeze must contain the exact policy digest and scope. `Task/` creation is a separate later owner decision. No changes to `Source/` are made in this phase.
