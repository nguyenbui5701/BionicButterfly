# BionicButterfly — Phase 2.2 Architecture Decision Supplement

- **ID:** BB-ADR-073 | **Version:** 0.1 | **Date:** 2026-11-12
- **Owner:** Solution Architect | **Status:** **ALL PROPOSED, NONE OWNER-APPROVED**
- **Purpose:** append decision candidates without overwriting the owner's canonical `15_V1_DECISION_REGISTER.md` before exact Git baseline review.

| ID | Decision proposal | Alternatives rejected/deferred | Primary dependencies | Approval status |
|---|---|---|---|---|
| **D-059** | Strict UTF-8 JSON v1 with schema, event types, no duplicate keys; YAML sample legacy only | YAML as executable canonical input deferred | `57`, `66`, `67`, `69` | PROPOSED |
| **D-060** | Fixed 5ms evaluation tick; batch all eligible events, single atomic state/output commit; conflicting control input denied | event-by-event actuator emission rejected | `58–59`, `67–68`, P22-T08/19 | PROPOSED |
| **D-061** | Adopt or revise complete `SIM_POLICY_CANDIDATE_22A`, with separate RF and serial freshness, low/high ARM qualification and resource quotas **SIM_ONLY** | missing/fallback numeric safety defaults rejected | `67`, `68`, `71` | PROPOSED |
| **D-062** | RFC8785 JCS candidate for canonical JSON input/config, integer micro-effort export and declared same-engine identity | byte-identical cross-platform floats rejected | `57`, `59`, `69`, P22-T01/19 | PROPOSED |
| **D-063** | Immutable preloaded profile/config throughout each G0-A1 run; edits require new run. Disk-persistent config mutation deferred | DISARMED in-run writes not selected for first host scope | `60`, `70`, `71` P22-T15 | PROPOSED |
| **D-064** | Freeze one scheduler step for G0-A1; cross-scheduler-step equivalence and persistent writes remain **DEFERRED**, not PASS | mixing variable tick intervals with strict byte identity rejected | `59`, `63`, `69`, `71` | PROPOSED |
| **D-065** | Host-only virtual sink and no real hardware/RF/flight context by composition; virtual contingency never specifies in-air actuator cutoff | runtime hardware-mode switches and reused flight failsafe rejected | `56`, `58`, `66`, `68`, `70` | PROPOSED |
| **D-066** | G0-A1 freeze requires exact owner Git Design revision, conflict signoffs, tests planned and separate owner approval; Developer `Task/` still requires subsequent authorization | push as approval, status CLEAN as approval rejected | `64`, `66`, `72`, `74` | PROPOSED |

## Consistency rules

- D-059…D-066 **refine** D-051…D-058 in `65`; they do not silently change the historical proposals in the actual Git tree. Final accepted decisions should be copied/linked into `15` with their approval source once the owner approves a specific revision.
- If D-060 changes, revise D-061/062/064 and the test oracles at the same time. If D-063 expands to persistent storage, re-enable CFG-05/G1B-15 and revise failure semantics before implementation.
- No decision authorizes selection of servo pulse frequency, pinout, RF failsafe, aerodynamic control gain, physical lift limit, emergency power cut or autonomous flight.
- **Owner-approved scope remains** V1 manual real RC flight; V2 autonomy only after V1. This supplement only addresses the host-only engineering prerequisite.

## Decision record to capture in future review

```text
Decision ID:
Proposal revision / exact file hash:
Options considered:
Risks / required tests:
Owner decision: APPROVED | REVISE | DEFER
Approval date & link:
Affected documents and design commit:
Effective G0 tier:
Developer task authorized separately? NO unless explicitly requested
```
