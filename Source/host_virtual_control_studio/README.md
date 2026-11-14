# TASK-014 Virtual Control Studio

**MODEL_ONLY / NOT PROVISIONED / NO OUTPUT.** One offline PC application for
editing simulated RC inputs, replaying the genuine TASK013 FSM, and inspecting
acknowledged state/effort/trace. No copied FSM, trusted runtime, physical receiver,
PWM or servo interface is included. All effort is dimensionless model arithmetic.

## Run on Windows

In `Source/host_virtual_control_studio`, using the prepared Python 3.11 `.venv`:

```powershell
.\.venv\Scripts\python.exe scripts\studio.py --gui
```

Select a preset and click **Run entire simulation**. Choose a timeline row or
use Play/Pause/scrub. The nominal model reaches ACTIVE at 145000us with effort
250000/750000, holds at 150000 without refreshing timestamps, enters CONTINGENCY
on RF LOST at 155000, and returns DISARMED on qualified ACK at 190000.

To author inputs, set Duration (us), click **New empty session**, then choose
event kind and original time. For CONTROL_VALID, set ARM switch request, flap
micro (0..1000000) and steering micro (-1000000..1000000). Click **Append simulated
event** once per action in nondecreasing time order. Equal times are allowed;
the genuine FSM resolves the entire batch. Duration changes are applied when
creating a session or appending an event. Editing a slider does not replay.
Run the whole session explicitly; BOOT is inserted automatically at time zero.
Protocol instructions are in [GUI UAT checklist](evidence/GUI_UAT_CHECKLIST.md).

The editor clears the previous report when an input edit/load fails or the
session changes. Playback only reads committed model rows. A blocked/failed run
cannot export a complete recording. Successful exports are locally labeled
HTML, `.model.json`, `.model-candidate.jsonl`, or scenario `.wire.json` files.
No background server, network, plugin, USB/serial or hardware callback exists.

CLI works without importing Tkinter or requiring a display:

```powershell
.\.venv\Scripts\python.exe scripts\studio.py --case nominal --text --view evidence\nominal.html
.\.venv\Scripts\python.exe scripts\studio.py --case rf-loss --text
.\.venv\Scripts\python.exe scripts\studio.py --case ambiguous --text
```

Exit 0 means MODEL_REPLAY_COMPLETE, **not operational authorization**. Exit 2
means the model was blocked/incomplete (expected for `ambiguous`, which stops
before 15000us with three acknowledged rows and no complete candidate digest).
Exit 1 means CLI/input adapter/export error. Smoke explicitly checks all three
expected outcomes, so ambiguous's intentional exit 2 is never called a completed
replay. `scripts/demo.py` is an alias to this same CLI.

## Integration and input contract

`session_to_wire_v2(raw_actions: bytes) -> bytes` enforces the closed P226 schema
and additional ID/order/time constraints, rejects duplicate keys/bools as ints,
floats/nonfinite/Unicode/BOM/overquota inputs, and emits exact integer-millionth
decimal tokens without binary floating point. Original timestamps and action
order are retained. Wire event IDs are deterministic `action_00001` etc., with
separate `studio_boot`; they map by action index to session IDs (including any
user ID that happens to equal `studio_boot`).

`run_studio_session(raw_actions, frozen_wire_v2_schema, policy_raw, claimed_host,
intent_raw, engine_artifact, scheduler_artifact)` calls real TASK013
`run_fsm_model` exactly once after session conversion. The immutable result
retains the exact F1 report; the Studio does not reinterpret its transitions.
Policy/E2/E3 inputs are loaded from fixed independently pinned TEST_ONLY sources
by the adapter; session/GUI cannot select them. The core/controller has no I/O
or Tk imports. GUI controls edit inputs; they cannot change a committed report.

`VirtualRuntimeBoundary` is frozen and permanently denies runtime/output:
`runtime_authorized=False`, `output_allowed=False`, `actual_virtual_output=None`,
`physical_output=None`, `control_trace_sha256=None`,
`requires_owner_provisioning=True`. No init argument enables those fields.
Candidate trace identity/digest is only DESIGN_CONFORMANCE_ONLY from F1.

## Developer verification and Owner UAT

Developer runs `scripts/verify.py --dev`: new tests/oracles/negative families,
headless controller, demos, builds, installed wheel/pip, and two impacted
TASK010/011 provenance tests. It does not execute complete old regression suites.
Final evidence is under `evidence/dev/`. Manual GUI UAT is **separate**, never
inferred from headless controller or hidden-widget smoke.

Owner commands (Design/196):

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\studio.py --case nominal --text
.\.venv\Scripts\python.exe scripts\studio.py --case rf-loss --text
.\.venv\Scripts\python.exe scripts\studio.py --case ambiguous --text
.\.venv\Scripts\python.exe scripts\verify.py --owner
```

Then launch `scripts/studio.py --gui` and record observed manual checks in
`evidence/GUI_UAT_CHECKLIST.md`. Owner `--owner` runs each TASK001–013 historical
regression once, separately audits JUnit, and retains actual logs/exit codes in
`evidence/owner/`. Ambiguous exit 2 is expected and checked explicitly.

## Fresh checkout without preserved external files

Use a full local Git checkout including baseline history, Python **3.11 x64**
(the bundled rpds wheel is cp311 Windows x64), and Node on PATH for inherited
TASK013 independent JCS tests. The CLI/runtime itself does not need Node.
The offline test-tool wheels and license notices are supplied under `vendor/`.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --find-links vendor\test-wheels setuptools==80.9.0 wheel==0.45.1 build==1.2.2.post1 pytest==8.3.5 jsonschema==4.26.0
.\.venv\Scripts\python.exe scripts\verify.py --owner
```

Verification builds all local project wheels from the immutable Git baseline
without network access. It creates a fresh local Git clone inside this task's
ignored cache; the initial TASK001 evidence is proven to be its clean Git blob.
It checks and stages the exact task-local
`fixtures/TASK001_PRESERVED_BASELINE_FOR_REGRESSION.json` only into that isolated
clone. The old tests keep their original provenance assertions. It checks all
inherited preserved-evidence pins and blocks missing/changed fixtures; it never
reads or rewrites a dirty current TASK001 file. See the fixture provenance MD.
New TASK014 release/code/fixtures are overlaid in the clone for independent
fixture tests. All generated outputs stay inside the new task's scope/cache.

Baseline: `0a0a49ba0bbd2a87a1771ef4ad09d0b2f55b4b09`; 39 explicit Git pins,
10 release artifacts plus separately pinned manifest, unchanged R1 policy.
The local preserved TASK001 modification is intentionally left untouched.

## Limits

HEALTHY+UNKNOWN without an approved ordering remains MODEL_CONTRACT_BLOCKED.
No unresolved tick is committed/displayed. Sliders cannot bypass LOW/HIGH,
freshness, ACK or catastrophic-latch behavior. Model completion does not prove
an operational R1 runtime, trust provisioning, actual wing movement or safety.
Windows manual UI acceptance, hardware/RC/servo/PWM/flight, process crash
durability and SC-G1/HB-G0B approvals are not provided by DEV CHECK. No PR is
created until Owner UAT acceptance and explicit permission.
