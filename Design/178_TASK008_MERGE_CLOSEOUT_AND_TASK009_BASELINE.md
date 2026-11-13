# Phase 2.21 — TASK-008 Closeout and TASK-009 Baseline

- ID BB-P221-178; 2026-11-14; **G0-A1 PC_SIM_ONLY**.
- Verified GitHub [PR #8](https://github.com/nguyenbui5701/BionicButterfly/pull/8) merged, with PR HEAD `a120abb9d7474550634031e71eabc114e6cbf2cc`.
- Verified current `main` merge SHA: **`e61f97e388662a48a13ccb6b308954436cbb87ec`**.
- TASK-001…008 merged. TASK-008 Owner/Developer JUnit evidence: 345 tests, seven prior regressions total 1133, dev/wheel smoke 36 each PASS; SA review reported no major/blocker at that HEAD. These are **historical** claims, not TASK-009 runtime proof.
- TASK-009 is **a limited TEST_ONLY transaction/snapshot gate**, not the final authoritative R1 Committed State Owner; the latter requires complete FSM, trusted host allowlist and R1 control-trace serializer/writer. Keeping these separate is deliberate safety engineering, not an additional policy.

## Immutable parent source SHA pins

| Dependency or controlling Design path | Git blob SHA-1 |
|---|---|
| `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` | `e6d988d160773219811d28cdb346b5a4590a0fa0` |
| `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md` | `02a0c21faf0b758bb55220debc390c09058021f7` |
| `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md` | `fdc4263fd940f7ffd8f256dd617b7c89cc6274fd` |
| `Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md` | `2e154c314fbfdcfed8bc6daa00b72cdf349a6ccb` |
| `Design/134_R11_TRACE_RECORDS_AND_REPLAY_BYTES_CANDIDATE.md` | `c085995e4fc82095ab0f693426a9d3632db9b14b` |
| `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` | `b21fcb9ed83775054cf2bde0b6533f5b71cb6eda` |
| `Design/173_G0A1_RF_CONTROL_HEALTH_EVIDENCE_STAGE_D1.md` | `f2e37723f58ced0457c7951cd07672b488793dda` |
| `Design/176_G0A1_GUARD_TRIAGE_STAGE_D2_CONTRACT.md` | `679ab5c50ff4576f0419e5173e387249def34e8c` |
| `Source/host_guard_triage/src/bb_host_guard_triage/triage.py` | `a847ec9cee86d8f5d354a7a034eb848fd03b4a31` |
| `Source/host_temporal_guard_facts/src/bb_host_temporal_guard_facts/temporal.py` | `707f3f1aa3c1c997839204c137ee907a7696c57a` |
| `Source/host_safety_priority_kernel/src/bb_host_safety_priority_kernel/priority.py` | `6a194b6fea178d8e697901448143c90a1edaf531` |
| `Source/host_health_evidence/src/bb_host_health_evidence/health.py` | `830169669068d6f337d56c21cbee438e5759cf91` |
| `Design/contracts/SIM_POLICY_22A_R1.canonical.json` | `62c35f82c715d3b3587dcc67d74f1320ba160929` |

- Frozen policy content SHA-256: `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. A Git blob hash or policy digest is **not** a trust credential.
- Developer must verify the frozen blobs at `git rev-parse e61f97e388662a48a13ccb6b308954436cbb87ec:<path>` against this index; compare checkout bytes too. Any drift stops work: `BLOCKED — DESIGN CLARIFICATION`.

## Dependency rationale

The first eight tasks are read-only classifiers and proposal modules. None has a **trace-confirmed** owner snapshot or the authority to promote current RF/CONTROL candidates into accepted pilot intent. TASK-009 supplies the *transaction ordering shell*: immutable snapshot, staged fail-closed candidate, append acknowledgment through a fixed **test-only in-memory journal**, then snapshot replacement. It must be impossible for a failed or deferred append to advance state or grant output.

This stage deliberately **does not implement the R1 control-trace schema/JCS byte stream**, an approval credential, complete FSM priority or physical controller. It must not call prior-stage diagnostic outputs `trusted`. A separate later stage must build R1 engine trust and complete decision trace before production commit is possible.

## Token-efficient workflow

Developer tests while coding. Owner runs final verification/UAT on unchanged code; Developer then only audits SHA/file scope and opens PR after explicit Owner permission. Do not duplicate full regression solely to write long reports. Any execution-affecting change after Owner UAT requires affected tests and renewed UAT acceptance. SA reviews; Owner alone merges. Existing Design and TASK-008 files remain immutable historical records.
