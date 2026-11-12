# BionicButterfly — G0-A1 Defect & Closure Register (SA Review)

- **ID:** BB-P25-ISSUE-093 | **Version:** 0.1 | **Status:** REVIEW FINDINGS, ALL OPEN / owner has not approved resolution.
- **Scoping:** Defect means a missing/ambiguous *design contract*, not a claimed software bug: no implementation currently exists.

| ID | Severity for G0-A1 design freeze | Evidence in draft | Required design disposition | Exit evidence |
|---|---|---|---|---|
| P25-F01 | **P0** | Phase24 `84–90` and 13 updated docs not on verified main | integrate and recheck exact candidate files or approve alternative based only on Git main | a new commit read back, current blob SHAs/digests reconciled |
| P25-F02 | **P0** | `84` candidate and older `58/68` conflicting historical priority interpretations | explicitly accept/supersede old sections by unique versioned normative reference | owner decision on D-075–077; no competing current tables |
| P25-F03 | **P0** | `67` sample has `approved_for_host_execution:false`; `87` says externally authorized policy can run | make sample flag NON-AUTHORITATIVE or remove it from approved record; trust host-signed/allowlisted digest, not scenario | exact policy bytes + independent approval record + tamper negative oracle |
| P25-F04 | **P0** | `87` says hash full JSONL including terminal, but terminal may be assumed to include `control_trace_sha256` | prohibit self-referential hash and define explicit terminal exclusion plus location of returned digest | byte-format revision + test `P25-T01` |
| P25-F05 | **P1** | `84` active state on a tick with **no** control frame but still-fresh last frame unspecified | decide whether hold last command until timeout, zero demand, or require one control per tick; state/output semantics explicit | tick-by-tick table + tests `T02–T04` |
| P25-F06 | **P1** | low qualification only mentions two LOW observations, not whether intervening HIGH/invalid/unknown events invalidate the candidate | reset LOW qualification on any valid HIGH, RESET, health loss; invalid frames do not qualify; clarify continuous health | transition matrix `95` tests `T05–T07` |
| P25-F07 | **P1** | `84` SELF_TEST passes on next tick, but exact priority and consequence of a fault at SELF_TEST boundary incomplete | define preflight fatal rejection vs injected fault vs self-test and whether initial `RF UNKNOWN` permits DISARMED but blocks ARM | `95` test `T08–T09` |
| P25-F08 | **P1** | `84` same-tick event eligibility uses timestamps; `85` equivalent bodies select latest timestamp; need exact deterministic ordering of noncontrol causes | define stable event type/order and causal ID sorting, one immutable batch per tick | permutation tests and canonical trace comparison |
| P25-F09 | **P1** | trace append failure may occur after virtual sink computation; claim one decision per tick needs transaction semantics | stage decision+normative log before exposing virtual output, fail closed on log quota/error | design sequence and `P25-T10` oracle |
| P25-F10 | **P1** | candidate numeric policy `67` includes flight-looking names and hardware-negative values | policy and fixtures remain `PC_SIM` `SIM_ONLY`, assert no physical HAL, no PWM or in-air action configured | negative scope test + static dependency audit |
| P25-F11 | **P2** | tests reuse old error name in historical documentation | versioned migration report, not a one-name alias | compatibility table and repeatable test IDs |
| P25-F12 | **P2** | mandatory test inventory spans PC-A/G1B/P22/P23/P24 and now P25 | define precise mandatory-vs-deferred set, remove duplicate oracle confusion | `96` coverage mapping with gating |

**P0 = blocks owner-ready normative G0-A1 freeze recommendation.** P1 means detailed behavior must be resolved before any implementation-task handoff. P2 is documentary/harness governance. Hardware G4 NO-GO remains independent.

## Proposed closure ownership

SA writes/reviews contract & evidence; owner explicitly accepts policy/scope/semantics. Future Developer implements only if **separately authorized** and provides actual test evidence. No P25 finding is closed by merely creating this document.
