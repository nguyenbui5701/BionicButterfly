# Phase 2.26 — TASK-013 merge closeout, baseline and TASK-014 scope

- Document BB-P226-194; status **SA DESIGN RELEASE, TASK-014 NOT EXECUTED**; baseline `main` commit **`0a0a49ba0bbd2a87a1771ef4ad09d0b2f55b4b09`**.
- PR #13 (reviewed HEAD `e3956e280cdd94a2a1ff66de9588de614e45968e`) merged 2026-11-14 08:02:16 UTC. TASK-001..013 merged. Historical Owner UAT for TASK-013: 189 new tests + 2614 older regressions = 2803 PASS, 24/24 P225, N01–N24; these are historical evidence, NOT TASK-014 test results.
- Decision: build a **single interactive PC-only offline virtual-control studio** powered by the genuine integrated F1 model; do not add E4/E5 checker packages or enable actuator outputs merely because hashes match.
- Frozen R1/R1.1 policy remains unchanged and is **not a runtime credential**. Exact canonical policy SHA-256: `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`.
- Git review verified the **complete non-truncated tree (1321 entries)** for the baseline. The 39 Git blob SHA-1 pins below are actual baseline **Git object IDs**, not SHA-256 over content. Verify via `git rev-parse 0a0a49ba0bbd2a87a1771ef4ad09d0b2f55b4b09:<path>`; do NOT require current HEAD to remain equal to baseline after adding this release.
- Normal Git blob of historical TASK-001 `evidence/baseline.json` is pinned here. The separate modified *working copy* from TASK-013 Owner UAT is discussed in Design/196 and MUST NOT be confused with this Git blob. No historical Source file may be changed.

## Frozen reference byte pins (39)

| Existing file, relative to repository root | Git blob SHA-1 at baseline |
|---|---|
| `Design/07_AI_CODING_RULES.md` | `a3760b54389d082f9f5f8c0b7cd7296cbe640eb8` |
| `Design/10_SA_OPERATING_RULES.md` | `a0d802028e4a86d6f0a8ead6466fb4fe94b319cb` |
| `Design/11_HANDOFF_PR_WORKFLOW.md` | `3e4cbb254f086958a98a6e2bc8817b86e341d2aa` |
| `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` | `e6d988d160773219811d28cdb346b5a4590a0fa0` |
| `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md` | `02a0c21faf0b758bb55220debc390c09058021f7` |
| `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md` | `f4c7d0bd857616fcdbbd978176ed8c9065e98d21` |
| `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md` | `fdc4263fd940f7ffd8f256dd617b7c89cc6274fd` |
| `Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md` | `2e154c314fbfdcfed8bc6daa00b72cdf349a6ccb` |
| `Design/133_R11_VIRTUAL_MIXER_M0_EXACT_ARITHMETIC_CANDIDATE.md` | `8ea4f2f556d83d6132df86751c9ffd29b931575d` |
| `Design/134_R11_TRACE_RECORDS_AND_REPLAY_BYTES_CANDIDATE.md` | `c085995e4fc82095ab0f693426a9d3632db9b14b` |
| `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` | `b21fcb9ed83775054cf2bde0b6533f5b71cb6eda` |
| `Design/179_G0A1_COMMITTED_SNAPSHOT_GATE_STAGE_E1.md` | `745d4bba1e06d29b253ddeb2bcdedb93b7e96506` |
| `Design/182_G0A1_HOST_REFERENCE_BINDING_STAGE_E2_CONTRACT.md` | `3700ed10a1c7be54ef5ea8af065dee399fe90de1` |
| `Design/185_G0A1_HOST_PROVISIONING_INTENT_STAGE_E3_CONTRACT.md` | `5248bd54ff4bd4661d5b866e555223b494b8984a` |
| `Design/188_G0A1_INTEGRATED_SHADOW_REPLAY_STAGE_F0_CONTRACT.md` | `9557ad0e21d1d9863204b82c265136889e462dc2` |
| `Design/189_TASK012_INTEGRATION_ACCEPTANCE_AND_G0B_ROADMAP.md` | `2482724078248a3813f53b9a80ef39ad5e7c9c2e` |
| `Design/190_TASK012_MERGE_CLOSEOUT_AND_TASK013_BASELINE.md` | `7378ce99dfacec093392062817299083c61c7190` |
| `Design/191_G0A1_F1_INTEGRATED_FSM_MODEL_AND_TRACE_CONTRACT.md` | `6e3199ddc1709ac4bcb117aeb22be02d814e7397` |
| `Design/192_TASK013_INTEGRATED_SYSTEM_ACCEPTANCE_AND_UAT.md` | `cd0fe9ec3c4368ce8fb53e2d86d0a7cbce2b9738` |
| `Design/193_G0B_PARALLEL_BENCH_READINESS_DECISION_PACKET.md` | `2b5aefa27873409e13eb09de062ef51e98d14697` |
| `Design/contracts/SIM_POLICY_22A_R1.canonical.json` | `62c35f82c715d3b3587dcc67d74f1320ba160929` |
| `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | `1d10c76e34be70880a65252d89a6bca89839fea9` |
| `Design/contracts/G0A1_TRACE_RECORDS_R11_CANDIDATE.schema.json` | `ef0c1c8d7754042f72449e54e37c650c8fee4be8` |
| `Design/contracts/G0A1_EXTERNAL_REPORT_R11_CANDIDATE.schema.json` | `c7da5879ef976d7e11186d484ea1e66453229c9a` |
| `Design/fixtures/P225_F1_ORACLE_INDEX.json` | `003317f058d8452eee0e1491ad23b148c075559f` |
| `Design/fixtures/P225_F1_NOMINAL_WIRE_V2.json` | `60b54a3c27d9eb2bc5b8e84ce57cb18b263b10c8` |
| `Design/fixtures/P225_F1_RECOVERY_WIRE_V2.json` | `c3e9a57b99a34bb526ca7efe3613db65cffcaa5d` |
| `Design/fixtures/P225_F1_CONFLICT_WIRE_V2.json` | `bb4564ea1d12b897b879f944c99815898c1d4ab4` |
| `Design/P225_TASK013_RELEASE_MANIFEST.json` | `8c3090d80c9bdf0c117e28d9ca2a2936888d894f` |
| `Source/host_integrated_fsm_model/src/bb_host_integrated_fsm_model/model.py` | `0c869b52a3475dde22a3542df7b50b560b735245` |
| `Source/host_integrated_fsm_model/src/bb_host_integrated_fsm_model/trace.py` | `6993877d5415b22eb25d717a2044712421c8919f` |
| `Source/host_integrated_fsm_model/src/bb_host_integrated_fsm_model/jcs.py` | `ae31b5fab0e87338b9d976acb805e21b1a4adef2` |
| `Source/host_integrated_fsm_model/src/bb_host_integrated_fsm_model/viewer.py` | `3110f547e96dc7202c09132a153d90e6da220059` |
| `Source/host_integrated_fsm_model/scripts/verify.py` | `0a7e621d66b23b6888628979790adf09ac66a906` |
| `Source/host_integrated_fsm_model/evidence/UAT_ACCEPTANCE.md` | `c6f05700ee3f97926d4f5cee08dfbf1234c92f83` |
| `Source/host_integrated_fsm_model/evidence/SA_CLARIFICATION.md` | `fb6c9bbbe5feb89c7394642c503d9ea96bab5535` |
| `Source/host_integrated_shadow_replay/src/bb_host_integrated_shadow_replay/replay.py` | `378c44dc864339bdaa84c746ed92125604446458` |
| `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py` | `506aa23cbe5e01671f3f51c1f2fd64444d7f0578` |
| `Source/host_preflight_m0/evidence/baseline.json` | `3fd5c53d4697d9a98905e4658bf444274d0e027c` |

## Verified implementation surfaces

- TASK-013 `run_fsm_model` provides an immutable **MODEL_ONLY** record; good model transitions are counterfactual and **never** mean operational ARM or virtual/physical output.
- `ModelReplayReport`: always `runtime_authorized=False`, `output_allowed=False`, `actual_virtual_output=None`, `physical_output=None`, `control_trace_sha256=None`; optional `candidate_trace_sha256` is **DESIGN_CONFORMANCE_ONLY**.
- TASK-013 `scripts/verify.py --owner` has a known environmental dependency: an uncommitted, preserved TASK-001 evidence file whose SHA-256 is **`e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d`**; clean Git copy differs. TASK-014 must make its own verification self-contained **without modifying old evidence**.
- In unresolved same-tick RF `HEALTHY+UNKNOWN`, existing F1 returns `MODEL_CONTRACT_BLOCKED` before candidate append or display. Keep this conservative result; never invent a runtime RF precedence.

## Ownership

SA alone authors Design/Task release, Developer implements only new `Source/host_virtual_control_studio/**`, Owner runs full UAT and authorizes PR/merge after SA review. This release does **not** provision a signer/trust root, authorize protected install, approve G0-B, or grant PWM/real RC/flight.
