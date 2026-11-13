# Phase 2.19 — TASK-006 Merge Closeout and TASK-007 Source Baseline

- ID: BB-P219-172 · Date: 2026-11-13 · Scope: **PC_SIM_ONLY**.
- Verified GitHub pull request: [PR #6](https://github.com/nguyenbui5701/BionicButterfly/pull/6), **merged**.
- Pinned, merged `main`: `a47dc157453547125f5172b4ef165c3b522ff0c8`. No TASK-007 runtime exists at this source pin.
- TASK-006 PR HEAD before merge: `3dae9fc642a302bb2675a4c139e7e5cf716dd61d`.
- Owner/Developer UAT evidence at PR #6: TASK-006 221 PASS; TASK-001…005 regressions 654 PASS; both smoke 16 PASS; total reported 875 tests PASS. This is historical **Developer/Owner evidence**, not an independently executed TASK-007 or SA regression.

## Why TASK-007 now

The previous six components cover strict input, tick scheduling, observation grouping, prior timestamp ages, *provisional* safety-priority constraints and *hypothetical* LOW/HIGH qualification. **None has a proven source of effective RF status or accepted control authority.** In particular, a prior healthy timestamp may still be within 200ms while a later RF LOST was seen; relying on age alone would be unsafe.

The next narrow phase computes a **non-authoritative evidence classification** over (a) current RF/control batch, (b) timestamp ages, (c) prior committed **RF status** supplied separately as a synthetic record, and (d) current provisional safety blockers. It never manufactures a `HealthVerdict.PASS` or `ControlVerdict.ADMITTED` for TASK-006; no operational wiring between these two packages may be introduced here.

## Frozen reference guards

All paths below were inspected at merged source pin; preserve them byte-for-byte. A Developer must compare the named Git blobs, not merely trust moving `main`.

| Path | Git blob SHA-1 |
|---|---|
| `Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md` | `e6d988d160773219811d28cdb346b5a4590a0fa0` |
| `Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md` | `02a0c21faf0b758bb55220debc390c09058021f7` |
| `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md` | `f4c7d0bd857616fcdbbd978176ed8c9065e98d21` |
| `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` | `b21fcb9ed83775054cf2bde0b6533f5b71cb6eda` |
| `Design/161_G0A1_TICK_OBSERVATION_NORMALIZATION_CONTRACT.md` | `8e503343242c70473d8b0e593cdda2de6dce41be` |
| `Design/164_G0A1_TEMPORAL_GUARD_FACTS_CONTRACT.md` | `eed1c062d3de85a2beb361118ba9fd776dd90a36` |
| `Design/167_G0A1_SAFETY_PRIORITY_KERNEL_STAGE_C1_CONTRACT.md` | `160d2773df5f68192e7c1638c7be8652144bf904` |
| `Design/170_G0A1_ARM_QUALIFICATION_PROPOSALS_STAGE_C2.md` | `790c9c2f45cd5cc05880f4caaa82f17b315f7334` |
| `Source/host_batch_observations/src/bb_host_batch_observations/normalizer.py` | `9cf0a1bb6333049dafc46d69691292fe9b7ea3b8` |
| `Source/host_temporal_guard_facts/src/bb_host_temporal_guard_facts/temporal.py` | `707f3f1aa3c1c997839204c137ee907a7696c57a` |
| `Source/host_safety_priority_kernel/src/bb_host_safety_priority_kernel/priority.py` | `6a194b6fea178d8e697901448143c90a1edaf531` |
| `Source/host_arm_qualification/src/bb_host_arm_qualification/qualification.py` | `57e47ed1ba360af45dfc41ce694179a17b8c7dc4` |
| `Design/contracts/SIM_POLICY_22A_R1.canonical.json` | `62c35f82c715d3b3587dcc67d74f1320ba160929` |
| `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | `1d10c76e34be70880a65252d89a6bca89839fea9` |
| `Design/fixtures/P210_MINIMAL_WIRE_V2.json` | `7990a0e2c4a95425a61c27c9024a8a0783520663` |

**Approved policy SHA-256:** `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. A hash identifies bytes, not trust; a separate host-provisioned allowlist is still absent.

## Workflow modification for token savings

Developer runs targeted tests/debug during coding. Owner runs final UAT verification and keeps exact JUnit, logs, source revision and test environment evidence; Developer does **not** repeat a full regression purely to write a verbose PR report if code, test dependencies, and verified bytes have not changed. Any change that invalidates UAT requires rerunning affected tests before the PR may be recommended. SA reviews Design/code/safety; Owner decides merge. No rule bypass and no flight authorization.

## Gate and future sequence

TASK-007 Stage D1 is evidence **only**. A later task must independently provision trusted policy and engine/host context, own trace-committed RF/control history and resolve full R1 health/state transitions. Full P28 state/output oracles, source allowlist, active S1 hold, ACK recovery, append-before-publish, real receiver/servo/flight remain **NOT RUN / NO-GO**.
