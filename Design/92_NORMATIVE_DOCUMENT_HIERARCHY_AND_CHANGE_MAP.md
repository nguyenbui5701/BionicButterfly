# BionicButterfly — Normative Document Hierarchy & Change Map

- **ID:** BB-P25-HIER-092 | **Version:** 0.1 | **Status:** PROPOSED / OWNER APPROVAL REQUIRED.
- **Purpose:** avoid ambiguity from overlapping sections in 57–87; do not automatically designate newest file authoritative.

## 1. Proposed precedence **only if owner explicitly accepts G0-A1**

| Concern | Primary approved contract candidate | Other documents | Mandatory reconciliation before freeze |
|---|---|---|---|
| Product V1/RC & V2 boundary | `02`, `16`, `27` | `31–41` | preserve actual V1 flight goal, no promotion of PC_SIM to flight readiness |
| Host-only logical architecture | `56`, `78` with clarifications `84–85` | `51`, `61` | one public host API entrypoint and no physical HAL paths |
| State transitions, conflicting input, reset/ACK | `84` | `58`, `68`, `78` | replace/supersede contradictory existing tables with exact section pointer and version; old text remains historical |
| Event names/typed errors | `85` result v2, input v1 | `57`, `71`, `79` | version migration and explicit source of errors; no mixed enum meanings |
| Virtual scheduler/time | `84` + `67` for **candidate values** | `59`, `68` | clarify per-tick freshness, equal boundary and low/high qualification |
| Config/policy authorization | `87`, `70` | `67` example policy JSON | remove misleading approval field from authoritative policy OR document it as ignored display-only; digest must bind trusted bytes |
| Replay canonicalization/hash | `87` + Phase25 correction `94` | `69`, `80` | remove circular terminal trace digest; pin JCS/JSONL canonical rules |
| Acceptance tests | `63`, `71`, `79`, `86`, Phase25 `95` | `52` | mark all design-only; reconcile contradictions before asserting oracle coverage |
| Design approval and handoff | `89`, Phase25 `97–98` | `30`, `54`, `64`, `74`, `83` | approval of design != authority to create code task, and never flight authorization |

**Until approval, the above is an SA recommendation, NOT a binding override.** Publication order or filename number does not itself grant authority.

## 2. Necessary type governance

`scenario_input_version=1` does not equal `result_contract_version=2`. Declare `policy_contract_version`, `scheduler_contract_version`, `canonical_trace_format_version`, and `engine_revision` independently. A producer/consumer checks the complete version tuple, rejecting incompatible combinations, rather than silently mapping error names.

## 3. Conflict closure checklist for files already on GitHub

- [ ] `57` has an authoritative note *and* a single unambiguous error registry; old `E_EVENT_ID_CONFLICT` restricted to historical scope.
- [ ] `58`, `68` and `78` have no *current* competing priority table after approved supersession.
- [ ] `59` and `67` agree on exact boundaries at 0, 5,000, 20,000, 100,000 and 200,000 µs.
- [ ] `69`, `80`, `87` and `94` agree on hash-covered bytes, header/decision/terminal and no digest self-reference.
- [ ] `70` and `87` agree on trusted host approval; example JSON cannot authorize itself.
- [ ] `71`, `79`, `86` and `95` test expected versions and the *same* state sequence, without calling old tests PASS.
- [ ] `89` and `98` approval records reference exact reviewed Git commit and digest set, owner decision separate from code permission.

## 4. Status

**NEEDS RECONCILIATION**. Phase24 additions exist locally, not at the verified Git HEAD. The core policy and runtime error/trace changes are substantive and require owner decision, not editorial replacements hidden behind a general freeze approval.
