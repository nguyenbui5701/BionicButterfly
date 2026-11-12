# BionicButterfly — Phase 2.3 Semantic Conflict & Hazard Register

> **Phase 2.4 review note (2026-11-12):** See the candidate corrective addendum at the end and `84–90` before treating older priority/approval text as normative. **Pending owner approval; not code or flight authorization.**

- **ID:** BB-P23-CONFLICT-077 | **Rev:** 0.2 | **Date:** 2026-11-12
- **Basis:** actual locally available Phase 2.0–2.2 Markdown snapshots, **NOT verified GitHub `main`**.
- **Status:** all items REVIEW-OPEN unless explicitly recorded as a proposal. Severity: `B` blocks G0-A1, `M` requires resolution before G1, `L` design clarification.

| ID | Sev | Actual source tension / ambiguity | Proposed SA resolution | Test & owner effect |
|---|---|---|---|---|
| **P23-F01** | **B** | `68` priority #3 treats accepted switch LOW/disarm as authoritative, while normalizer #4 says **all distinct control frames in a tick** are denied if conflicting; LOW+HIGH same tick could disarm despite the whole control component being invalid. | Normalize conflict **before** applying disarm priority. Invalid same-tick control frames may never authorize state transition or refresh freshness. If already armed, conflict causes simulated CONTINGENCY/output inhibition; if DISARMED remain. An independent trusted `RESET`/fault may still take priority. | P23-T05/06, D-067; owner acceptance required |
| **P23-F02** | **B** | `68` priority #1 RESET outranks catastrophic fault #2; if RESET and fault arrive same tick, a dangerous candidate could go through SELF_TEST without latching catastrophe. | RESET means **arm eligibility revocation and virtual output inhibition**. When simultaneous catastrophic fault is present, proposed post-state is `FAULT_LATCHED`, with reset observed as denied/pending; never let RESET erase a same-tick fault. Clarify distinction between explicit fault-clear recovery and any reset event. | P23-T07, D-068 |
| **P23-F03** | **M** | `69` includes `run_id` in trace header while requiring same-scenario same-build identical whole-file trace SHA. A nondeterministic run_id or wall-time metadata makes whole-file hashes differ. | Split `deterministic_replay_id` (content-derived) from optional `execution_instance_id` (outside canonical replay hash). Hash normative trace without wall time / nondeterministic metadata, or explicitly set deterministic run_id; specify one exact scheme. | P23-T11, D-069 |
| **P23-F04** | **M** | `57` registry `E_EVENT_ID_CONFLICT` conflates duplicate global event IDs (preflight reject) and contradictory valid control frames within one evaluation tick (runtime denied batch). | Distinguish typed `E_DUPLICATE_EVENT_ID` (hard preflight reject) vs `E_CONTROL_BATCH_CONFLICT` (runtime); old code retained only as legacy alias in report migration. No silent enum change under schema v1. | P23-T01/05, D-070 |
| **P23-F05** | **M** | `68` states last LOW qualification and current RF freshness, but simultaneous LOST and HEALTHY in a tick plus a LOW control frame is not fully specified for whether LOW observation accrues during fault. | Faulted/unknown-RF batch cannot advance LOW qualification or arm-high edge. Apply all fault evaluations before qualifying candidate controls. | P23-T08, D-067 |
| **P23-F06** | **M** | `68` says a new `SIM_ACK_FAULT` plus LOW qualification may recover; exact ACK event-time when low is qualified **in the same tick** vs a later tick is ambiguous. | Require distinct *already committed* qualified LOW snapshot before ACK decision; ACK same tick as its final LOW does not clear latch. Clear only on later evaluation with healthy accepted frame and independently qualified LOW. | P23-T09, D-071 |
| **P23-F07** | **M** | `69` refers to `same trace SHA` while trace can include optional `VISUAL_ONLY` records and differing presentation metadata. | Define normative `control_trace` separate from non-normative `visual_trace`; only normative control data contributes to replay digest. Document if optional visual artifacts are produced and their digests separately. | P23-T11/12, D-069 |
| **P23-F08** | **M** | `70` has approval fields but no explicit trust anchor/allowlist identity. A user-supplied JSON with `approved_for_host_execution=true` could be misinterpreted as authorization. | Design explicitly states **scenario and supplied policy booleans are not authority**. Host allowlist of approved `policy_digest` and matching signed owner decision is provisioned outside scenario input; no runtime on/off flag elevates privileges. | P23-T03, D-072 |
| **P23-F09** | **M** | `67` max input bytes 2MiB, trace 16MiB, event 20k, but hard handling if export exceeds quota after decisions not fully specified. | Terminate with `FAILED_INCOMPLETE_EVIDENCE`, count prior decisions, mark partial outputs, keep virtual actuation inhibited; future implementer cannot discard failure and claim PASS. | P23-T12, D-073 |
| **P23-F10** | **M** | `67/68` use original `event_at_us` for arm edge and sample age, while events are applied at later eval ticks; a much earlier high frame in a tick could qualify an edge if timing isn’t interpreted consistently. | Specify source timestamp for age and `eval_at_us` for atomic commit, and require LOW and HIGH in different ticks with the measured separation; arm qualification must have a distinct later confirming accepted frame. | P23-T04/10, D-074 |
| **P23-F11** | **L** | `67` uses a proposed numeric policy that is execution-disabled, while `71` sample oracles presume hypothetical authorization. | Keep every vector explicitly *hypothetical*. Freeze approval must change authorization via owner-gated baseline, not by user-modifying the example `approved_for_host_execution` field. | Documentation signoff; P23-T03 |
| **P23-F12** | **B** | User's public GitHub repository `main` cannot currently be read by the available environment, so exact SHA/collision/version status is unknown. | Maintain `FRZ-01=BLOCKED`; complete direct GitHub access or obtain a read-only directory SHA inventory **before asserting Design Freeze**. | `75`, `82`, D-066; no false claim |

## 2. Risk classification and path to closure

- **B = freeze gate blocker**: P23-F01/F02/F12 require exact reviewed semantics or verified repository identity.
- **M = implementability blocker**: P23-F03…F10 must be accepted as one versioned contract, with tests updated; no developer may choose an implementation-specific tie-breaker ad hoc.
- **L = documentation**: F11 still requires a clear banner at the top of all sample oracles.
- Physical G0-B/G0-C findings from previous phases are **not closed**, particularly lack of measured pitch/roll/yaw authority and the in-flight fail-safe strategy.

## 3. Decision format

```text
Finding ID:
Observed source path and exact revision:
Owner Git commit (when verified):
Chosen resolution / rejected alternatives:
Affected schemas, tests and ADR IDs:
SA review:
Owner approval (APPROVE / REVISE / DEFER):
Status: OPEN / PROPOSED_RESOLVED / CLOSED_AFTER_COMMIT
```

**SA recommendation:** approve neither a new `E_*` enum nor a reset priority change by silently overwriting old docs. These are **proposed corrections** requiring a versioned freeze review and canonical source updates before tasking a Developer.

## Phase 2.4 finding disposition update (rev 0.2)

**P23-F12 CLOSED FOR ACCESS/IDENTITY:** public repository `main@16d5054ea951b2e52e90c7f81ea2767a7ba82b92` verified; matching Phase23 blobs documented in `88`. This corrects the earlier historical repo-access blocker. Other P23-F01…F11 stay **PROPOSED RESOLVED / NOT OWNER-APPROVED** with normative candidate `84`, error migration `85`, tests `86`, and replay/trust `87`. No old blocker is silently marked PASS by document creation.
