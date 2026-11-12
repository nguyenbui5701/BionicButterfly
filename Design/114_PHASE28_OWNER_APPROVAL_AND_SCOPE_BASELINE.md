# BionicButterfly — Phase 2.8 Owner Approval and Scope Baseline

- **Document ID:** BB-P28-APP-114 | **Rev:** 1.0 | **Date:** 2026-11-13
- **Decision:** **APPROVED: G0-A1 Candidate R1**, with scope below. **Implementation and physical-flight authorizations are NOT granted.**
- **Reviewed owner repository:** [BionicButterfly main at source commit](https://github.com/nguyenbui5701/BionicButterfly/tree/3d9a4f28d521190d10579cab48d8b732817892c9/Design)
- **Pinned source commit:** `3d9a4f28d521190d10579cab48d8b732817892c9`; Phase2.7 files `107–113` confirmed present on GitHub.

## 1. Evidence of owner decision

The owner accepted Candidate R1 in the current conversation by stating:

> tôi xác nhận phê duyệt hết, bạn cứ làm tiếp

**Interpretation is bounded to the immediately preceding SA approval request:** Candidate R1 for G0-A1 PC-only, including D-075…D-090, SIM_POLICY_CANDIDATE_22A, recovery semantics and clarified subchoices from `113`. It is **not** a blanket approval of all older hardware candidates, every previously pending D-001…D-074, real-flight G4 policy, development code, or a permission to issue `Task/` without a later task-scoping request.

The machine-readable human decision record is `contracts/G0A1_OWNER_APPROVAL_R1.record.json`. Its provenance is a chat statement, **not** a forged cryptographic signature and **not** a host-executable policy allowlist.

## 2. Approved architecture slice

**Included:** PC_SIM_ONLY; strict versioned JSON scenario input, independently approved immutable SIM policy, deterministic virtual-clock batching, single-authority safety FSM, synthetic RF/serial states, dimensionless virtual L/R effort, trace-commit-before-output, replay identity, JSONL trace with externally calculated SHA-256, typed errors and offline acceptance oracles.

**Excluded:** physical ESP32/UART/CRSF/ELRS/GPIO, servo PWM, LiPo control, wing physics/lift proof, flight-specific contingency action, camera/IMU, cockpit UI takeover, V2 autonomy, motor/servo bench and free-flight authorization. V1 product goal remains real manual RC flight; the simulator alone cannot prove controllability.

## 3. Accepted D-075–D-090 and subchoices

| Group | D-IDs | Accepted R1 resolution | Source |
|---|---|---|---|
| Batch/safety/ACK | D-075–077, D-083–087 | normalize before effects; catastrophe/hazard before RESET; previous-tick LOW for ACK; S1; narrow recoverable allowlist; SELF_TEST guard | `115`, `101`, `109` |
| Schema/trust | D-078, D-080, D-089 | scenario v1/result-errors v2; immutable approved SIM policy; 22A numbers, PC-only | `116`, `117` |
| Replay/output | D-079, D-081, D-088 | stable replay identity, canonical JSONL SHA external, append-before-publication | `118` |
| Baseline/changes | D-082, D-090 | verified Git HEAD; controlled source reconciliation and expected-blob guard | `119` |

**Explicit Phase27 subchoices approved as part of R1:** recoverable warning enum `VOLTAGE_WARNING_RECOVERABLE` is *only* a non-critical recovered simulated warning; equivalent distinct-ID ACK events within one tick are one logical ACK. Duplicate **global event IDs** are still a preflight schema error. The warning enum is a *cause category*, **not** an unapproved new scenario v1 event type.

## 4. Approval stages are separate

| Stage | Status after this decision | What it proves |
|---|---|---|
| Candidate R1 architecture selection | **OWNER APPROVED** | owner chose specific PC-only design behavior |
| Phase2.8 reconciliation artifact | Prepared by SA; revisioned package | design text and patches can be reviewed against source blobs |
| Exact merged Git design baseline freeze | **PENDING owner-side integration + SA review** | same approved text committed without conflicts |
| Executable implementation acceptance | **NOT RUN / no implementation evidence** | nothing proved about runtime yet |
| Physical G0-B/G3/G4 | **HOLD / NO-GO** | not authorized; independent testing needed |

## 5. Change control

Owner approval is not permission for SA to silently change any R1 safety invariant. A changed event priority, policy value, result enum, replay field or exposure boundary requires R2 with impacted oracle revisions and owner decision. SA shall check expected Git blob SHAs before integrating patches; if source moved, re-review rather than overwrite.
