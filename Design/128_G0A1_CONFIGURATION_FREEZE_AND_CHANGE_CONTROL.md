# BionicButterfly — G0-A1 Configuration Freeze & Change-Control Policy

- **ID:** BB-P29-CM-128 | **Current reference:** `15803143960e3fc82a468d99e83474670237857f`
- **Role:** SA; no write operation to GitHub performed in this phase.

## 1. Frozen baseline registry

| Configuration item | Key | Immutable reference | Rule |
|---|---|---|---|
| Git `Design/` source snapshot | `G0A1_DESIGN_R1_SOURCE` | `15803143960e3fc82a468d99e83474670237857f` | read-only baseline, approved architecture bytes |
| Safety semantics | `G0A1_R1_SAFETY` | `Design/115` Git blob `e6d988d160773219811d28cdb346b5a4590a0fa0` | no silent override by historical docs |
| Policy core | `SIM_POLICY_CANDIDATE_22A` | SHA256 `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10` | immutable canonical 603-byte JSON, independent trusted approval later |
| Input/results | `G0A1_R1_RESULT_V2` | `Design/117` Git blob `f4c7d0bd857616fcdbbd978176ed8c9065e98d21` | wire-schema completeness to be reviewed |
| Replay | `G0A1_R1_TRACE_V1` | `Design/118` Git blob `fdc4263fd940f7ffd8f256dd617b7c89cc6274fd` | no self-hash, append-before-publication |
| Approved scope | `G0A1_R1_APPROVAL` | `Design/114` and owner chat declaration | PC_SIM_ONLY only, not flight authorization |

## 2. Release control levels

- **L0 — Design snapshot lock (achieved):** all relevant source files and exact policy digest pinned; cannot accidentally drift with moving main.
- **L1 — Full G0-A1 interface specification ready (HOLD):** resolve `P29-F01–F03` with a reviewed compatibility revision, close test vectors, update ADR and record owner decision where observable choices are made.
- **L2 — Developer handoff ready (HOLD):** L1 accepted; tests typed and independent trusted runtime allowlist design reviewed; SA issued a task **only after separate direction**.
- **L3 — Executable G1 acceptance (NOT RUN):** code exists, automated conformance passes, complete replay evidence, no physical I/O.
- **L4 — Hardware/flight (NO-GO):** separate G0-B/G3/G4 program with measurements and approved safe flight contingency.

## 3. Document change classes

| Change type | Required process |
|---|---|
| Typo, formatting | may be documentation-only new commit, note exact ref; no semantic change |
| Scenario wire field / output formula / trace record field | **R1.1 candidate**, impact review, oracle update, owner decision if behavior selected |
| Safety priority, ACK condition, timeout, policy numeric, error semantics | **R2 design amendment**, independent explicit owner approval; update digest and all affected test vectors |
| Physical adapter / receiver / battery / airframe | separate G0-B and G4 design gate; **never** include under G0-A1 |

## 4. Snapshot integration process

The Phase 2.9 package contains **only new files** `123–130` and machine evidence; it does not overwrite `01–122`. Integrating these files into main creates a *new* commit and must be identified as **documentation addition**, not evidence that the previously frozen bytes were modified. If future owner revisions change `115–118` or canonical policy, review the diff and issue a new baseline record. Keep audit file hashes and explicit status distinctions.
