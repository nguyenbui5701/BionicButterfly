# TASK-014 — INTEGRATED PC VIRTUAL CONTROL STUDIO + FRESH-CLONE UAT

| Field | Definition |
|---|---|
| Baseline | `0a0a49ba0bbd2a87a1771ef4ad09d0b2f55b4b09` (TASK-013 merged PR #13) |
| Status | SA DESIGN RELEASED / DEVELOPER NOT RUN |
| Branch | `feature/TASK-014-virtual-control-studio` |
| Source-only write scope | **`Source/host_virtual_control_studio/**`** |
| Runtime | **PC_SIM_ONLY / MODEL_ONLY / RUNTIME_UNPROVISIONED / NO_OUTPUT** |
| Output | Pure local scenarios, MODEL timeline, effort bars, offline labeled records; no positive virtual runtime commands |

## Read first and verify before coding

1. `Design/07`, `10`, `11`; frozen `115–118`, `132–134`, `141`; `179`, `182`, `185`, `188`, `191`.
2. New `Design/194`, `/195`, `/196`, `/197`, `Design/fixtures/P226_*`, `Design/P226_TASK014_RELEASE_MANIFEST.json`.
3. Existing actual code under `Source/host_integrated_fsm_model/**`, `host_integrated_shadow_replay`, TASK-001…011, especially `run_fsm_model`, `ModelReplayReport`, vendor pinned rfc8785, `scripts/verify.py`.
4. Verify **39/39** Git blob SHA-1 pins in Design/194 against **baseline commit tree**, **10/10** release artifact Git blob SHA-1 and SHA-256 plus release manifest pin (separate), and policy SHA-256 `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. STOP `BLOCKED — DESIGN CLARIFICATION` on mismatch; never silently re-pin.

## Deliver ONE runnable product

- Python >=3.11 package `bb-host-virtual-control-studio==0.1.0` with a pure `session_to_wire_v2(raw_actions: bytes) -> bytes` and pure testable `run_studio_session(raw_actions: bytes, ...) -> StudioSessionReport` that uses genuine existing `run_fsm_model`, no copy of FSM. Keep required upstream preflight/policy/E2/E3 bound outside user session. Pure core accepts only typed caller-validated dependency objects as F1 requires, but **no output/authority flags or arbitrary callback**. No file/network/device imports in pure modules.
- Single offline Tkinter studio (`scripts/studio.py --gui`) for user to append simulated RF/CONTROL/ACK/RESET/FAULT events, replay on click, play/pause/scrub model states and L/R effort in a read-only timeline. CLI (`--case nominal|rf-loss|ambiguous --text`) works without tkinter/display. Offline `--view local.html` and offline candidate export must be clearly labeled MODEL ONLY.
- Use closed action schema P226, strict parsing and exact integer-millionth decimal JSON conversion. Real generated wire-v2 must validate with TASK-001. No plugins, shell commands, serial, RF/USB/network, PWM/servo, actuator sink, physical output, dynamic imports, config override, protected trust-root provisioning, real ARM. Build direct F1 comparator determinism and duplicate conflict tests; no unacknowledged model row.
- **Resolve fresh-clone Owner verification** as in Design/196: task-local immutable verified fixture of Owner-preserved TASK001 evidence; stage only into scratch regression workspace; never modify old module or relax provenance. If the exact preserved source bytes unavailable or unsafe, report BLOCKED and propose a migration instead of cheating.

## Acceptance

Deliver AC01–AC12 in Design/196, 24 named independent P226 oracle tests plus N01–N24 negative families, and actual demo samples for three cases. Include pinned transaction/model limits and deterministic hash check. GUI manual smoke should be separate from programmatic headless tests. `scripts/verify.py --dev` only TASK014 tests, current build/wheel/pip/smoke. Owner `--owner` performs TASK-001…013 historical regression **once** using isolated immutable baseline checkout with task-local verified evidence fixture; do not rely on dirty workspace or network; count ACTUALLY RUN cases only. Preserve real failures/logs. Do not quietly mark UI tested by headless test alone.

**DEV CHECK → OWNER FULL UAT → Owner authorizes PR → SA PR review → Owner merges.** Developer must not create PR in advance, push unapproved Design edits, merge, or claim actual runtime provisioned. All output fields permanently negative. If required UI/model behavior conflicts with frozen R1, HOLD and return exact source/tick to SA.

**Next gates (out of this task):** SC-G1 independently approved trusted virtual runtime output; HB-G0B reviewed physical schematic/BOM/servo-only bench; G3 wings and G4 flight remain NO-GO. The user's actual objective is manual RC-controlled wings, but this task does not energize a single servo.
