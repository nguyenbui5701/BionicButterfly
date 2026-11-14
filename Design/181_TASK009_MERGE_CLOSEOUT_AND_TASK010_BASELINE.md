# Phase 2.22 — TASK-009 Merge Closeout and TASK-010 Frozen Baseline

- Document: **BB-P222-181** · Source scope: G0-A1 **PC_SIM_ONLY / REFERENCE_VERIFICATION_ONLY**.
- Verified PR #9 merged: https://github.com/nguyenbui5701/BionicButterfly/pull/9
- Verified merged main SHA: **`4c7c92524837c8c728d0f206e5ba4655f9513399`**.
- TASK-001…TASK-009 merged; PR #9 source TEST_ONLY ledger is not an authoritative R1 FSM or trace writer.
- TASK-009 Owner UAT evidence: **246 PASS**, prior TASK-001…008 **1478 PASS**, smoke **48/48** dev and wheel; SA recommended merge for E1 scope. These are historical Developer/Owner artifacts, **not** TASK-010 proof.

## Frozen source and normative byte pins

Every file below must exist at the exact `main` SHA and match the listed Git blob SHA-1. No Developer rewrite or auto-rebaseline.

| Pinned relative path | Git blob SHA-1 |
|---|---|
| `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` | `e6d988d160773219811d28cdb346b5a4590a0fa0` |
| `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md` | `02a0c21faf0b758bb55220debc390c09058021f7` |
| `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md` | `f4c7d0bd857616fcdbbd978176ed8c9065e98d21` |
| `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md` | `fdc4263fd940f7ffd8f256dd617b7c89cc6274fd` |
| `Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md` | `2e154c314fbfdcfed8bc6daa00b72cdf349a6ccb` |
| `Design/134_R11_TRACE_RECORDS_AND_REPLAY_BYTES_CANDIDATE.md` | `c085995e4fc82095ab0f693426a9d3632db9b14b` |
| `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` | `b21fcb9ed83775054cf2bde0b6533f5b71cb6eda` |
| `Design/179_G0A1_COMMITTED_SNAPSHOT_GATE_STAGE_E1.md` | `745d4bba1e06d29b253ddeb2bcdedb93b7e96506` |
| `Design/180_TASK009_SNAPSHOT_GATE_ORACLES_AND_SA_REVIEW.md` | `468d3551c2160e6bd244d8ef3f5c1d50513cdbc6` |
| `Design/contracts/SIM_POLICY_22A_R1.canonical.json` | `62c35f82c715d3b3587dcc67d74f1320ba160929` |
| `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | `1d10c76e34be70880a65252d89a6bca89839fea9` |
| `Design/contracts/G0A1_SIM_POLICY_CORE_V1.schema.json` | `f4a024c147a610a208033819cf631ba2044197d1` |
| `Design/contracts/G0A1_OWNER_APPROVAL_R1.record.json` | `2bdc8d96205272ee736213332e6599835b89a681` |
| `Design/fixtures/P210_MINIMAL_WIRE_V2.json` | `7990a0e2c4a95425a61c27c9024a8a0783520663` |
| `Design/fixtures/P210_MINIMAL_DESIGN_TRACE.jsonl` | `4b7677fa4cdd6d15da61751349c872997fa6f2bc` |
| `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py` | `506aa23cbe5e01671f3f51c1f2fd64444d7f0578` |
| `Source/host_snapshot_commit_gate/src/bb_host_snapshot_commit_gate/ledger.py` | `b9a5c773da7cf7354e85ab62e2bb0126d81d7d88` |
| `Task/TASK-009_HOST_SNAPSHOT_COMMIT_GATE.md` | `53f0bd04715c5b5323c0e6f352de336d497ea37c` |

- **Approved policy canonical SHA-256:** `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10` — SHA over the exact `Design/contracts/SIM_POLICY_22A_R1.canonical.json` bytes (no LF appended). This is a content identifier, **NOT** a signed policy or host trust credential.
- Source R1.1 precedence: Design/141. R1 authority: 115–118. Supplied JSON owner approval record is **only chat provenance**; that file explicitly says `trusted_runtime_policy_allowlist_provisioned=false`.
- The P210 design trace header uses `engine_revision=G0A1_DESIGN_REFERENCE_1`, `scheduler_revision=FIXED_5MS_DESIGN_1`; these are design-example values, **not** certified runtime executable identities. Do not install them as a trusted host allowlist.

## Why Stage E2 is intentionally bounded

Stage E1 proved a TEST_ONLY internal journal/snapshot order, not trust. TASK-010 will produce a **fail-closed reference comparison** (policy bytes, context, owner and version tuple) on a genuine TASK-001 preflight result, with an explicitly synthetic host fingerprint. Even a completely matching fingerprint yields `runtime_authorized=False` and `requires_trusted_host_provisioning=True`. A genuine authenticated allowlist provisioned from protected host build/deployment, reviewed engine binary identity, and owner release sign-off are future gates.

## Token-efficient workflow

Developer writes only `Source/host_trust_boundary/**`, tests while debugging, then supplies UAT commands. Owner runs final full verification once. Developer may open PR only after Owner explicit approval and may omit duplicate expensive re-runs if source/test/dependency bytes match UAT exactly. SA conducts independent scope/code/evidence review; Owner merges.
