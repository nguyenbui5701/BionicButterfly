# TASK-014 — integrated studio acceptance, test strategy, reproducible Owner UAT

- BB-P226-196; baseline `0a0a49ba0bbd2a87a1771ef4ad09d0b2f55b4b09`; 24 named oracles P226-T01…T24; separate negative families N01…N24. This is **one real integrated system**: interactive offline UI + deterministic scenario construction + existing F1 FSM + transaction/trace denial + viewer, not another checker.

## 1. Acceptance matrix (AC01…AC12)

| ID | Observable acceptance |
|---|---|
| AC01 | Only new `Source/host_virtual_control_studio/**` plus approved Design/Task P226 release files; no prior Source/R1/policy edits. |
| AC02 | Exact 39 baseline Git blob pins, P226 release hashes, policy digest and inherited dependencies checked; STOP on mismatch. |
| AC03 | One real complete runnable CLI text demo + Tkinter offline UI with replayable RC-like controls; no API requests to any external service. |
| AC04 | Closed P226 action schema → generated validated genuine wire-v2 bytes; unique causal IDs, original timestamp order, float-free millionth serialization. |
| AC05 | Uses genuine F1 `run_fsm_model`; no duplicate FSM/priority logic, fake TASK-006 positive verdict or E1 positive state injection. |
| AC06 | Shows ARM request, model LOW/HIGH timing, MODEL ACTIVE L/R effort, RF loss, ACK recovery, catastrophic latch, all NO_ACTUATOR_OUTPUT. |
| AC07 | Competing LOST/HEALTHY, conflicting/INVALID frames, HEALTHY+UNKNOWN fail-closed; no unacknowledged tick to display. |
| AC08 | Immutable runtime boundary remains permanently denied; no positive virtual output, R1 complete `control_trace_sha256`, physical PWM or servo output. |
| AC09 | Export/playback deterministic, local, labeled model-only HTML and JSON; no file path, network or plugin bypass. |
| AC10 | 24/24 independent P226 fixture oracles + N01…N24 and programmatic headless GUI-controller tests, artifact integrity checks. |
| AC11 | Verification is genuinely reproducible from fresh checkout without any out-of-tree preserved TASK-001 working file; no weakening original provenance. |
| AC12 | DEV CHECK only new suite; Owner alone runs FULL UAT with TASK-001…013 regression once, wheel smoke, pip and provenance. |

## 2. Required negative families

N01 duplicate JSON keys; N02 unknown keys or injected `approved`/`sink`/`signature`; N03 bool-as-int and invalid datetime; N04 NaN/Infinity/nonfinite; N05 malformed Unicode/BOM; N06 action at T0; N07 duplicate action IDs; N08 overlong action count or bytes; N09 time reorder/out of duration; N10 decimal micro nonintegrality; N11 unauthorized RF provenance; N12 control valid/conflict same-tick; N13 INVALID+VALID same-tick; N14 HEALTHY+LOST override LOST; N15 HEALTHY+UNKNOWN `MODEL_CONTRACT_BLOCKED`; N16 early HIGH with no prior committed LOW; N17 HIGH confirmation one µs early; N18 new ACTIVE before confirmed HIGH; N19 S1 stale RF or frame; N20 ACK same tick as second LOW or RESET; N21 catastrophic latch reset no clear; N22 injected F1 journal append failure leaves no extra display row/file; N23 fake trust/session/world config cannot grant actual virtual output; N24 fresh-clone pinned TASK-001 evidence and no edits to old Source.

Require test coverage on exact 20,000us / 100,000us / 200,000us boundaries, unclamped+clipped model M0 pairs and GUI repeated replay determinism. Separate tests verify Tkinter import only in GUI adapter; headless CI must pass without a display. Demonstrate 60s/20k-event MAX in core using existing F1 tests as inherited regression; add at least one new bounded studio large-session test without quadratic replay.

## 3. Fix the inherited preserved TASK-001 evidence dependency **within this task**

In prior TASK-013, `scripts/verify.py --owner` required **local, uncommitted** `Source/host_preflight_m0/evidence/baseline.json` with SHA-256 `e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d`, different from the committed Git blob. **No file bytes are supplied in this SA package**, so Developer must **read the actual Owner-preserved local file** and verify its SHA-256 before copying a permitted evidence-only fixture into:

`Source/host_virtual_control_studio/fixtures/TASK001_PRESERVED_BASELINE_FOR_REGRESSION.json`

Requirements:
- Inspect fixture for secrets/personal/local paths; redact nothing silently (would change pinned digest), fail BLOCKED if unsafe to commit and return to SA for an approved alternative.
- Exact fixture bytes must have SHA-256 `e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d`; **NOT** the Git blob SHA-1. Include provenance comment as *separate* MD file; do not edit the JSON fixture content.
- In isolated scratch copy of historical TASK-001…013 from BASELINE, verify each inherited regression evidence pin against this fixture, then stage ONLY in scratch copy, never write old Source. `--owner` must not read a modified file from current working tree. Preserve original assertions and actual PASS/FAIL output. If compatible migration cannot be proven, report `BLOCKED — PROVENANCE` (no quiet skip/rebaseline).
- Validate with **two different checks**: (a) normal Owner checkout with preserved evidence present, and (b) new temporary clean Git checkout + only new TASK-014 release/code/fixture branch; owner regression must no longer depend on an untracked external file. The clean-clone case may need local wheel installation; no network required when pinned wheels present.
- Preserve any older source test failure evidence; no false `tests PASS` attribution when not run.

## 4. DEV vs OWNER commands

Developer runs `python -m pytest -q -p no:cacheprovider`, `scripts/smoke.py`, `scripts/demo.py --case nominal|rf-loss|ambiguous --text`, wheel build/install/pip, `scripts/verify.py --dev`; run impacted old test only when needed. GUI verified in a Windows interactive session by Owner; headless tests cover controller. Developer must NOT run full TASK-001..013 suite routinely.

Owner (PowerShell inside new module) runs:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\studio.py --case nominal --text
.\.venv\Scripts\python.exe scripts\studio.py --case rf-loss --text
.\.venv\Scripts\python.exe scripts\studio.py --case ambiguous --text
.\.venv\Scripts\python.exe scripts\verify.py --owner
```

Owner also opens `scripts/studio.py --gui` once and verifies the workflow manually; document observed PASS/FAIL and do not silently mark unobserved UI PASS. `verify.py --owner` must run actual older regression from complete immutable baseline scratch copies after fixture staging; audit each JUnit, record counts and command statuses. After Owner UAT PASS + explicit PR permission, Developer checks exact executable hashes and creates PR; no rerun if unchanged. SA review, Owner merge.

## 5. Truthful release limitations

- F2 is **not trusted runtime provisioning**. `MODEL_REPLAY_COMPLETE` is never `SimulationRunReportV2.COMPLETED` and cannot authorize virtual/physical output.
- Mock signed claims/test root/GUI toggle are not permission. G0-B requires exact selected parts/datasheets and separate Owner approval; nothing in Studio implements physical safety.
- Real process crash durability, Windows GUI user studies, live RC radio, real PWM and aerodynamic wing movement remain NOT TESTED until separately evidenced.
