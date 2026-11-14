# Phase 2.23 — TASK-010 Merge Closeout & TASK-011 Baseline

- Document: BB-P223-184; created 2026-11-14.
- GitHub PR #10: https://github.com/nguyenbui5701/BionicButterfly/pull/10; reviewed HEAD \`ca4f4231ad031c499e2b10a6b7f71d4f9532635d\`; **MERGED**.
- **Authoritative merged `main` = `7872c415c73146e33a5596b010320f76596588cb`** (must match before implement).
- Git baseline root tree SHA-1 `e97b98332b7f13cd5a0e5e04a508b50e1ce306ed`; 816 tree objects in GitHub recursive snapshot, `truncated=false` at design preparation. This does not assert clean local checkout or secure host build.
- TASK-001…010 merged. TASK-010 reported Owner UAT 387 tests plus 1,724 regressions; these are **historical**, not TASK-011 runtime evidence.
- R1/R1.1 authority remains **G0-A1 PC_SIM_ONLY**; physical receiver, servo and flight are NO-GO. No trusted runtime allowlist has been independently provisioned by this design.

## Frozen controlling file pins

| Exact path | Expected SHA-1 of Git blob in pinned baseline |
|---|---|
| `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` | `e6d988d160773219811d28cdb346b5a4590a0fa0` |
| `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md` | `02a0c21faf0b758bb55220debc390c09058021f7` |
| `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md` | `f4c7d0bd857616fcdbbd978176ed8c9065e98d21` |
| `Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md` | `fdc4263fd940f7ffd8f256dd617b7c89cc6274fd` |
| `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` | `b21fcb9ed83775054cf2bde0b6533f5b71cb6eda` |
| `Design/182_G0A1_HOST_REFERENCE_BINDING_STAGE_E2_CONTRACT.md` | `3700ed10a1c7be54ef5ea8af065dee399fe90de1` |
| `Design/183_TASK010_REFERENCE_BINDING_ORACLES_AND_SA_REVIEW.md` | `578c1dc8d32cc4d0ba2f69817241a276a2325bf3` |
| `Design/contracts/SIM_POLICY_22A_R1.canonical.json` | `62c35f82c715d3b3587dcc67d74f1320ba160929` |
| `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | `1d10c76e34be70880a65252d89a6bca89839fea9` |
| `Design/fixtures/P210_MINIMAL_WIRE_V2.json` | `7990a0e2c4a95425a61c27c9024a8a0783520663` |
| `Source/host_trust_boundary/src/bb_host_trust_boundary/boundary.py` | `6fa32d9dd0a8c8a3b3697e7983e72fa9c73d2622` |
| `Source/host_trust_boundary/src/bb_host_trust_boundary/__init__.py` | `a491c7220f638afe7189000b59a5eb730450f18f` |
| `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py` | `506aa23cbe5e01671f3f51c1f2fd64444d7f0578` |
| `Source/host_snapshot_commit_gate/src/bb_host_snapshot_commit_gate/ledger.py` | `b9a5c773da7cf7354e85ab62e2bb0126d81d7d88` |

**Policy SHA-256 of exact original bytes, without LF:** `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`.

## Developer preflight/checkpoint

1. Check `git rev-parse main`, `git rev-parse 7872c415c73146e33a5596b010320f76596588cb^{tree}`, `git status --porcelain` and all above frozen blob pins via `git rev-parse 7872c415c73146e33a5596b010320f76596588cb:<path>` (do not silently rebaseline). Local unrelated edits are not covered by the pinned tree; isolate the task branch. Do not erase an unrelated local evidence edit.
2. Release contains five authored files plus one derived manifest `Design/P223_TASK011_RELEASE_MANIFEST.json`; verify SHA-256, Git blob SHA-1, byte lengths, and that the Design/Task files are unchanged before code.
3. The new `E3` identifiers are synthetic **TEST_ONLY** and do not certify an engine, scheduler, plugin or signed install.
4. Do not run existing TASK-009 internal journal or invoke any actual output. All code is in `Source/host_provisioning_intent/**` only.
5. If implementation asks for an actual owner signing key, trusted root, protected allowlist install, host binary authentication or real runtime permission, STOP: **BLOCKED — DESIGN CLARIFICATION** and a distinct Owner approval.

## Release process

SA writes/finalizes Design and Task; Owner integrates and commits the immutable release; Developer first checks accepted release hashes, implements in new Source subtree, runs targeted tests while coding; Owner performs final full UAT; only then Developer requests permission to open PR, no automatic merge. Full regression rerun not needed merely to package documentation when execution-affecting bytes/dependency are unchanged. The source pin is never changed to accommodate tests.
