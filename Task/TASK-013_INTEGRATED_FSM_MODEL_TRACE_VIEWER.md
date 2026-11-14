# TASK-013 — INTEGRATED FSM MODEL + JCS TRACE ENGINE + OFFLINE VIEWER

| Field | Requirement |
|---|---|
| State | OPEN — SA DESIGN RELEASED; **Owner to integrate/assign** |
| Baseline | `eb4dbc8830d864c9cfd5c4d94bf00180aa960b5d` (merged PR #12) |
| Goal | One runnable integrated **R1 behavior-model** with model ARM/ACTIVE/recovery timeline, RFC8785 candidate trace and offline read-only wing effort viewer |
| Write scope | **`Source/host_integrated_fsm_model/**` only** |
| Branch | `feature/TASK-013-integrated-fsm-model` |
| Runtime scope | **PC_SIM_ONLY / MODEL_ONLY / NO_ACTUATOR_OUTPUT** |
| Merge | Owner alone after Owner FULL UAT, PR, independent SA review |

## First read, in order

1. `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`.
2. Frozen `Design/115`, `116`, `117`, `118`, `132`, `133`, `134`, `141` and exact policy/schema/trace bytes (files in Design/190 pin table).
3. Existing actual APIs in `Source/host_preflight_m0`, `host_virtual_ticks`, `host_batch_observations`, `host_temporal_guard_facts`, `host_safety_priority_kernel`, `host_health_evidence`, `host_guard_triage`, `host_snapshot_commit_gate`, `host_trust_boundary`, `host_provisioning_intent`, `host_integrated_shadow_replay`. Treat TASK-006 only as hypothetical; E1 only as negative TEST_ONLY journal.
4. **New:** Design/190, /191, /192, /193, P225 oracle index and three genuine v2 wire fixtures, and P225 release manifest.
5. Verify **all 32** Git blob pins in Design/190, nine release hashes + manifest separately and frozen policy SHA d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10. STOP `BLOCKED — DESIGN CLARIFICATION` on any mismatch; never change old files or normative R1 to make tests pass.

## Deliver a working product, not a checker

Build pip-installable `bb-host-integrated-fsm-model==0.1.0` (Python >=3.11) and:

```powershell
.\.venv\Scripts\python.exe scripts\demo.py --case nominal
.\.venv\Scripts\python.exe scripts\demo.py --case recovery
.\.venv\Scripts\python.exe scripts\demo.py --case conflict
.\.venv\Scripts\python.exe scripts\demo.py --case nominal --view evidence\dev\model_viewer.html
```

CLI prints full model timeline, RF/control health, qualified LOW/HIGH edges, MODEL ARM/ACTIVE, mathematical M0 L/R bars and modeled loss/recovery/latch. Generated HTML is entirely offline/read-only and displays **modeled dimensionless effort**, not physical wing angles. The viewer cannot write state or control a servo. Package contains **one stateful FSM model**, a dedicated standards-correct JCS candidate trace module, private model transaction barrier, and CLI/viewer; do not split into another 5 standalone checkers.

Implement Design/191 §§1–5 exactly. Use independent `ModelPrior` from BOOT, not E1's restrictive snapshot. No TEST_ONLY D2 or TASK-006 data may grant real runtime authorization. A MODEL nominal ACTIVE is a **mathematical hypothesis** and never the real approved output of R1. `runtime_authorized=False`, `actual_virtual_output=None`, `physical_output=None`, `control_trace_sha256=None` in every public runtime report. No scenario-driven permission/sink/plugin. Candidate JCS streams and `candidate_trace_sha256` are **test-only**; reject any positive actual `SimulationRunReportV2.COMPLETED` claim.

Pass **24 named P225 oracles** and N01–N24 adversarial families through real upstream modules, plus 60s/20k-event stress and JCS independent vectors, 3 CLI cases, wheel smoke, package check. `--dev` runs only new tests; `--owner` runs all TASK-001–012 regressions once; never claim an unrun suite PASS. Add provenance evidence including baseline 33 pins, nine file manifest, policy; record test runs and UAT separately.

**Developer should NOT run full regression merely to prepare PR.** When ready, report DEV CHECK results, demo excerpts and evidence; do not create PR until Owner runs full UAT and explicitly authorizes. Owner can inspect offline viewer; NEVER claim G2 bench readiness based on HTML or virtual model.

## Scope prohibitions and security stop

No trusted allowlist provisioning/keys/signers, no OS privilege claims, no installed executable attestation, no actual authority, no PWM/UART/GPIO/ESP32 firmware, no RF bind, no servo/wing actuation. No changes to existing `Source/*` outside new task, Design or Task. Never treat an Owner-approved Design or digest as an operational credential. If approved R1 clauses conflict (notably effective RF/ACK semantics) and no deterministic resolution exists, stop with `BLOCKED — DESIGN CLARIFICATION` and exact case; do not invent precedence.

SA will review the PR at the exact Owner-accepted SHA. After this task, the next Owner-gated milestones are (a) protected PC-only runtime host authorization **in a combined output-integrated implementation task, not a new standalone checker** and (b) G0-B exact part+schematic approval to allow future G2 unloaded servo bench. G3/G4 remain NO-GO.
