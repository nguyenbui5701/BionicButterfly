# Phase 2.20 — TASK-007 Closeout and TASK-008 Immutable Baseline

- ID: BB-P220-175 · Date: 2026-11-14 · Scope: **G0-A1 PC_SIM_ONLY**.
- Confirmed GitHub PR #7 **merged**: https://github.com/nguyenbui5701/BionicButterfly/pull/7
- **Authoritative main HEAD:** `7c09bb5ab4d05d16bfa53439b5dab5b465ec8b05` (merge of PR #7).
- TASK-001…TASK-007 merged. Previous TASK-007 Owner UAT and SA review accepted 258 tests + 875 regressions; these are historical evidence, **not** TASK-008 test results.
- TASK-008 remains **DESIGN RELEASE ONLY / RUNTIME NOT RUN**.

## Frozen dependency/blob pins (read-only)

| Path | Expected Git blob SHA-1 in the baseline |
|---|---|
| `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` | `e6d988d160773219811d28cdb346b5a4590a0fa0` |
| `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md` | `02a0c21faf0b758bb55220debc390c09058021f7` |
| `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md` | `f4c7d0bd857616fcdbbd978176ed8c9065e98d21` |
| `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md` | `fdc4263fd940f7ffd8f256dd617b7c89cc6274fd` |
| `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` | `b21fcb9ed83775054cf2bde0b6533f5b71cb6eda` |
| `Design/161_G0A1_TICK_OBSERVATION_NORMALIZATION_CONTRACT.md` | `8e503343242c70473d8b0e593cdda2de6dce41be` |
| `Design/164_G0A1_TEMPORAL_GUARD_FACTS_CONTRACT.md` | `eed1c062d3de85a2beb361118ba9fd776dd90a36` |
| `Design/167_G0A1_SAFETY_PRIORITY_KERNEL_STAGE_C1_CONTRACT.md` | `160d2773df5f68192e7c1638c7be8652144bf904` |
| `Design/170_G0A1_ARM_QUALIFICATION_PROPOSALS_STAGE_C2.md` | `790c9c2f45cd5cc05880f4caaa82f17b315f7334` |
| `Design/173_G0A1_RF_CONTROL_HEALTH_EVIDENCE_STAGE_D1.md` | `f2e37723f58ced0457c7951cd07672b488793dda` |
| `Source/host_batch_observations/src/bb_host_batch_observations/normalizer.py` | `9cf0a1bb6333049dafc46d69691292fe9b7ea3b8` |
| `Source/host_temporal_guard_facts/src/bb_host_temporal_guard_facts/temporal.py` | `707f3f1aa3c1c997839204c137ee907a7696c57a` |
| `Source/host_safety_priority_kernel/src/bb_host_safety_priority_kernel/priority.py` | `6a194b6fea178d8e697901448143c90a1edaf531` |
| `Source/host_arm_qualification/src/bb_host_arm_qualification/qualification.py` | `57e47ed1ba360af45dfc41ce694179a17b8c7dc4` |
| `Source/host_health_evidence/src/bb_host_health_evidence/health.py` | `830169669068d6f337d56c21cbee438e5759cf91` |
| `Design/contracts/SIM_POLICY_22A_R1.canonical.json` | `62c35f82c715d3b3587dcc67d74f1320ba160929` |
| `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | `1d10c76e34be70880a65252d89a6bca89839fea9` |
| `Design/fixtures/P219_HEALTH_EVIDENCE_ORACLE_INDEX.json` | `6e1ad515d9e7f101dd0a63c0cc70e91e723b5d42` |

**Policy canonical SHA-256:** `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. A content digest does not authenticate an executable, an input snapshot or a physical device.

## Before implementation

1. `git rev-parse main` and `git merge-base --is-ancestor 7c09bb5ab4d05d16bfa53439b5dab5b465ec8b05 HEAD` must confirm the pinned parent; do not silently swap a new baseline.
2. `git rev-parse 7c09bb5ab4d05d16bfa53439b5dab5b465ec8b05:<pinned-path>` must match every above blob SHA-1; `git hash-object <pinned-path>` must match checked-out bytes; no modifications to pre-existing Source or frozen Design.
3. Verify all five authored release files against `Design/P220_TASK008_RELEASE_MANIFEST.json` (bytes, SHA-256, Git blob SHA-1), which is intentionally outside its own five-file list.
4. PR #7 accepted safety evidence is diagnostic only: HEALTHY_CARRIED / SINGLE_CANDIDATE remain **untrusted and uncommitted**.
5. If any hashes fail or active norms conflict, STOP with `BLOCKED — DESIGN CLARIFICATION`. Never regenerate the policy digest, edit Design or silently replace a pinned dependency.

## Transition rationale

Stage D1 classified current and previously committed **test-synthetic** RF status and visible control candidates. Stage D2 combines these facts into an explicit fail-closed per-tick **guard triage** and an armed-state prior-continuity audit; it still cannot assert real PASS/ADMITTED, accept timestamps, own committed state or authorize outputs. Trust allowlist, true prior trace owner, effective-health resolution and full FSM remain independent future gates.

## Process and owner responsibilities

Developer codes/debugs/tests in its task-only Source subtree. Owner runs final full UAT once, including regressions/build/wheel; after accepted UAT and explicit PR permission Developer does only source/manifest/scope/hash checks and opens the PR without duplicating full tests unless execution-affecting content changed. SA reviews contracted safety logic independently; Owner alone merges.
