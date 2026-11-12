# BionicButterfly — Phase 2.3 Proposed Architecture Decisions

- **ID:** BB-P23-ADR-082 | **Rev:** 0.1 | **Date:** 2026-11-12
- **Status:** **ALL PROPOSED**; no owner design freeze approval inferred from 'continue'.

| Decision | Candidate design | Alternatives / caution | Review source | Approval |
|---|---|---|---|---|
| **D-067** | Validate semantic same-tick control conflict **before** accepting disarm/arm candidates; armed conflict → virtual CONTINGENCY; no refreshed frame age | Applying LOW from rejected batch creates bypass | F01/F05, P23-T05/06/08 | PENDING |
| **D-068** | Catastrophic injected fault dominates RESET in same tick; no reset-based latch clearing | Earlier 68 priority #1 RESET risks hiding fault | F02, P23-T07 | PENDING |
| **D-069** | Deterministic replay identity and normative control trace digest separate from volatile execution metadata/visuals | Full raw file SHA depends on run_id/time if nondeterministic | F03/F07, P23-T11/18 | PENDING |
| **D-070** | Distinguish duplicate event-ID preflight rejection from runtime conflicting controls by versioned enum/subcode | Cannot silently change schema v1 error meaning | F04, P23-T01/05 | PENDING |
| **D-071** | Fault ACK requires LOW qualification already committed at previous tick, healthy guards and explicit event; no same-tick shortcut | Reduces ambiguity in recovery edge | F06, P23-T09 | PENDING |
| **D-072** | SIM policy approval via immutable external digest allowlist/record, never self-asserted input boolean | Prevent scenario elevating its own privileges | F08/F11, P23-T03 | PENDING |
| **D-073** | Incomplete or quota-broken trace → typed failed/incomplete status, virtual output inhibited; never PASS | May affect rerun/recovery semantics | F09, P23-T12 | PENDING |
| **D-074** | Source event timestamps and evaluation time are distinct and logged; no unqualified cross-tick-size replay equivalence | Age/arm boundary tested with off-grid events | F10, P23-T04/10/20 | PENDING |

**Scope preserved:** V1 real manually piloted RC free flight; V2 autonomous only after V1. This ADR concerns *PC simulator design only*; it does not authorize field testing, hardware source or flight failsafe policy.
