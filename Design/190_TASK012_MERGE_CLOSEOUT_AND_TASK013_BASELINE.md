# Phase 2.25 — TASK-012 merge closeout / TASK-013 baseline

- Document ID: BB-P225-190 · Release: F1.0 DESIGN-ONLY · 2026-11-14.
- Repository: `nguyenbui5701/BionicButterfly`; controlling `main` commit: **`eb4dbc8830d864c9cfd5c4d94bf00180aa960b5d`**.
- PR #12 merged as `eb4dbc8830d864c9cfd5c4d94bf00180aa960b5d`; reviewed source HEAD `8c81fe937de947eb0a338664e0a5385bc8938438`.
- Current merged TASK-001…012: source under `Source/host_*`; TASK-012 full UAT reported 111 TASK-012 tests + 2,503 prior regressions, 20/20 P224 oracles, 4/4 demo smoke. Those are *historical evidence*, **not TASK-013 results**.
- Owner priority: **integrate a real end-to-end runnable simulator and begin G0-B preparations in parallel**, avoid creating more independent trust-check tasks.
- Approved normative PC-only contracts: Design/115–118, Design/132–134 via Design/141. No hardware/flight authority.
- Frozen policy raw content SHA-256: `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`, NOT an executable trust credential.
- Security finding F1-SEC-01: `Design/116` states independently provisioned trusted runtime allowlist **does not exist**. TASK-010 and TASK-011 return negative authority. No test-only model, fabricated PASS/ADMITTED, repository manifest, or owner UAT may bypass this boundary. Stage F1 therefore builds a **full behavior model + R1 serialization candidate + visual simulation only**; operational `output_allowed`, `control_trace_sha256`, `runtime_authorized` remain negative/null until *separate* Owner-approved, protected runtime provisioning. See Design/191 §2.

## Exact Git blob SHA-1 pins at frozen baseline

Verify with `git rev-parse eb4dbc8830d864c9cfd5c4d94bf00180aa960b5d:<path>` (or GitHub Git tree API); not a SHA-256 of source bytes. Do not require feature-branch HEAD to equal old main. A mismatch in **any** pin requires SA clarification before coding.

| Path | Git blob SHA-1 |
|---|---|
| `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` | `e6d988d160773219811d28cdb346b5a4590a0fa0` |
| `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md` | `02a0c21faf0b758bb55220debc390c09058021f7` |
| `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md` | `f4c7d0bd857616fcdbbd978176ed8c9065e98d21` |
| `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md` | `fdc4263fd940f7ffd8f256dd617b7c89cc6274fd` |
| `Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md` | `2e154c314fbfdcfed8bc6daa00b72cdf349a6ccb` |
| `Design/133_R11_VIRTUAL_MIXER_M0_EXACT_ARITHMETIC_CANDIDATE.md` | `8ea4f2f556d83d6132df86751c9ffd29b931575d` |
| `Design/134_R11_TRACE_RECORDS_AND_REPLAY_BYTES_CANDIDATE.md` | `c085995e4fc82095ab0f693426a9d3632db9b14b` |
| `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` | `b21fcb9ed83775054cf2bde0b6533f5b71cb6eda` |
| `Design/170_G0A1_ARM_QUALIFICATION_PROPOSALS_STAGE_C2.md` | `790c9c2f45cd5cc05880f4caaa82f17b315f7334` |
| `Design/179_G0A1_COMMITTED_SNAPSHOT_GATE_STAGE_E1.md` | `745d4bba1e06d29b253ddeb2bcdedb93b7e96506` |
| `Design/182_G0A1_HOST_REFERENCE_BINDING_STAGE_E2_CONTRACT.md` | `3700ed10a1c7be54ef5ea8af065dee399fe90de1` |
| `Design/185_G0A1_HOST_PROVISIONING_INTENT_STAGE_E3_CONTRACT.md` | `5248bd54ff4bd4661d5b866e555223b494b8984a` |
| `Design/188_G0A1_INTEGRATED_SHADOW_REPLAY_STAGE_F0_CONTRACT.md` | `9557ad0e21d1d9863204b82c265136889e462dc2` |
| `Design/189_TASK012_INTEGRATION_ACCEPTANCE_AND_G0B_ROADMAP.md` | `2482724078248a3813f53b9a80ef39ad5e7c9c2e` |
| `Design/contracts/SIM_POLICY_22A_R1.canonical.json` | `62c35f82c715d3b3587dcc67d74f1320ba160929` |
| `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | `1d10c76e34be70880a65252d89a6bca89839fea9` |
| `Design/contracts/G0A1_TRACE_RECORDS_R11_CANDIDATE.schema.json` | `ef0c1c8d7754042f72449e54e37c650c8fee4be8` |
| `Design/contracts/G0A1_EXTERNAL_REPORT_R11_CANDIDATE.schema.json` | `c7da5879ef976d7e11186d484ea1e66453229c9a` |
| `Design/fixtures/P210_NOMINAL_M0_WIRE_V2.json` | `4e772fe51f0cfb5e085e7da81030dca02814d0b3` |
| `Design/fixtures/P210_MINIMAL_DESIGN_TRACE.jsonl` | `4b7677fa4cdd6d15da61751349c872997fa6f2bc` |
| `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py` | `506aa23cbe5e01671f3f51c1f2fd64444d7f0578` |
| `Source/host_preflight_m0/src/bb_host_preflight_m0/mixer.py` | `93ad14f32332596697b76c9ea68b3ea8affe8319` |
| `Source/host_virtual_ticks/src/bb_host_virtual_ticks/scheduler.py` | `755e74b740f1a68eb6f095b6895d80cba3831928` |
| `Source/host_batch_observations/src/bb_host_batch_observations/normalizer.py` | `9cf0a1bb6333049dafc46d69691292fe9b7ea3b8` |
| `Source/host_temporal_guard_facts/src/bb_host_temporal_guard_facts/temporal.py` | `707f3f1aa3c1c997839204c137ee907a7696c57a` |
| `Source/host_safety_priority_kernel/src/bb_host_safety_priority_kernel/priority.py` | `6a194b6fea178d8e697901448143c90a1edaf531` |
| `Source/host_health_evidence/src/bb_host_health_evidence/health.py` | `830169669068d6f337d56c21cbee438e5759cf91` |
| `Source/host_guard_triage/src/bb_host_guard_triage/triage.py` | `a847ec9cee86d8f5d354a7a034eb848fd03b4a31` |
| `Source/host_snapshot_commit_gate/src/bb_host_snapshot_commit_gate/ledger.py` | `b9a5c773da7cf7354e85ab62e2bb0126d81d7d88` |
| `Source/host_trust_boundary/src/bb_host_trust_boundary/boundary.py` | `6fa32d9dd0a8c8a3b3697e7983e72fa9c73d2622` |
| `Source/host_provisioning_intent/src/bb_host_provisioning_intent/intent.py` | `eceb4fe38b34ece781c8a6099d395e98d7a75298` |
| `Source/host_integrated_shadow_replay/src/bb_host_integrated_shadow_replay/replay.py` | `378c44dc864339bdaa84c746ed92125604446458` |

## Real API inventory and inheritance

- Real TASK-001 preflight and M0; TASK-002 scheduler; TASK-003 normalizer; TASK-004 temporal facts; TASK-005 partial priority; TASK-007 health facts; TASK-008 triage; TASK-012 F0 shadow as a diagnostic comparator.
- TASK-006 `HypotheticalQualificationVerdict` **not trustworthy**, cannot be an authority source.
- TASK-009 E1 test ledger is **not** the full authoritative R1 owner. TASK-013 owns its own fully modeled state timeline, **never alters or patches E1**. The F1 model snapshot is not a credential or a replacement for protected runtime admission.
- TASK-010 E2 + TASK-011 E3 assess only reference/intent consistency and **never authenticate** a host executable.
- R1 trace writer must be RFC8785/JCS-correct; TEST_ONLY shadow JSONL is NOT normative R1 trace. Reference P210 design trace is hand-authored only and **not** execution UAT evidence.
- STOP on a conflict between frozen controlling contracts. Developer may not alter Design, Task, policy or old Source to force passing tests.
