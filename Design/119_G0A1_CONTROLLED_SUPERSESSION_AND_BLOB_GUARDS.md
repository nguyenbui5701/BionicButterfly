# BionicButterfly — Controlled Document Reconciliation R1

- **Document ID:** BB-P28-RECON-119 | **Date:** 2026-11-13 | **Source commit:** `3d9a4f28d521190d10579cab48d8b732817892c9`
- **Owner approval:** `114`; **scope:** G0-A1 PC-only. Physical-state design `27`, parts/pinout and free-flight gate documents **remain separate and unapproved**.

## 1. A single source of truth per topic

| G0-A1 topic | Current controlling document | Historical source documents now annotated |
|---|---|---|
| Decision scope, ADRs D-075–090 | `114`, approval record | `108`, `113` |
| Atomic tick, FSM, S1, recovery, ACK | **`115`** | `58`, `68`, `84`, `100`, `101`, `109` |
| SIM numeric policy and host trust | **`116`**, exact canonical policy JSON and digest | `67`, `70`, `87`, `102`, `110` |
| Input v1 / result-error v2 | **`117`** | `57`, `61`, `78`, `85` |
| Complete trace/replay/external SHA | **`118`** | `59`, `69`, `80`, `87`, `94`, `103`, `110` |
| Test design coverage/status | **`120`** | `71`, `95`, `104`, `111` |
| Freeze / developer handoff | **`121`, `122`** | `93`, `113` |

The old documents are kept verbatim **below a new front-of-file supersession banner** for historical traceability. They do not become software acceptance evidence. Source files that were not included in this package must not be presumed changed; `27` remains proposed **physical** safety design, outside G0-A1.

## 2. Git overwrite guard

`PHASE28_SOURCE_BLOB_GUARDS.json` lists each updated path, exact blob SHA expected from `3d9a4f28d521190d10579cab48d8b732817892c9`, new blob SHA and reason. A source file may only be replaced if the owner's local/remote current Git blob matches the recorded `original_git_blob_sha`; if HEAD has advanced or local file is edited, **STOP and perform a three-way semantic merge**. Never blindly extract and overwrite a newer file. All updates are prepend-only notices, not destructive rewrites.

## 3. Review sequence before a formal merged baseline freeze

1. Confirm owner decision `114` is correctly scoped, not construed as flight permission.
2. Validate the canonical policy JSON exact bytes and SHA-256 against `116`; inspect both machine record and readable copy.
3. Review changes to every updated file (only the prepend notices) against expected blob. Check no existing state machine table is mistakenly promoted above `115`.
4. Check v1 input/v2 result naming, transition/collision/rate boundaries and oracle mapping in `120`.
5. After owner integrates files into Git, record the **new exact commit SHA** and rerun file-sha/digest audit. Only then publish a final G0-A1 **configuration-controlled Design Freeze** record. No implementation test has been run and no task has been authorized by this artifact.

## 4. Approvals and their limits

The owner approved the **design selection**, not any code build, UART driver, servo command path, data collector, RF-loss behavior while airborne, power/cable sizing, airborne disarm or free flight. The trust allowlist is NOT auto-created by Git commit, policy SHA or markdown approval banner.
