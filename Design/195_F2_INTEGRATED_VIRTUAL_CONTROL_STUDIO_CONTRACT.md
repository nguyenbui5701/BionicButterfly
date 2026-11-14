# Stage F2 — Integrated virtual control studio and denial-first transaction rehearsal

- Document BB-P226-195; baseline `0a0a49ba0bbd2a87a1771ef4ad09d0b2f55b4b09`; **PC_SIM_ONLY / MODEL_ONLY / RUNTIME_UNPROVISIONED / NO_ACTUATOR_OUTPUT**.
- Authority order: approved Design/141, 115–118, 132–134/133, existing Stage F1 Design/191. New UI creates a **scenario**, not a trust root, operational frame, credential, new event type or normative R1 execution success.

## 1. User-facing product — one integrated workflow

Provide a Windows-friendly **Tkinter offline studio** with CLI fallback and a pure testable controller. User can select scenario preset, append *simulated* RF changes and RC-like control samples (flap demand 0..1, steering -1..1, ARM switch), replay the complete session, play/pause/scrub an **acknowledged MODEL timeline**, inspect state/LOW-HIGH windows/fail reasons, and watch abstract left/right **effort bars**. Displays MODEL states; no actual wing pose, servo angle, beat frequency, lift, stability, actual PWM or physical safety inference. Show a bright permanent `MODEL_ONLY / NOT PROVISIONED / NO OUTPUT` banner. Pure controller must function in headless tests without importing tkinter; GUI is only an adapter; if Tcl/Tk unavailable, CLI runs all fixtures.

- CLI: `python scripts/studio.py --case nominal|rf-loss|ambiguous --text` (actual full trace of model states) and `--view path.html` as offline read-only playback. GUI: `python scripts/studio.py --gui` (no web server or sockets). Exports only labeled **OFFLINE MODEL** files and scenario inputs, never an executable or trusted policy.
- A GUI click **'Append simulated event'** does not advance hardware: it adds a closed typed event to a local virtual timeline, then **'Run entire simulation'** builds one strict v2 scenario and invokes genuine TASK-001→TASK-013 APIs. It must NOT call arbitrary code, invoke `eval`, import a plugin, access serial/UART/BLE/WebUSB, connect internet or emit external data. All UI timeline editing only builds future inputs. **No per-slider-movement racing replay**; replay only on explicit action.
- Use approved 5ms virtual clock (T0 BOOT), original event timestamps preserved; all non-BOOT times >0, nondecreasing. Session fixture is **not** wire-v2 input and never passed to `validate_wire` directly. Convert it into the approved closed wire-v2 shape using only allowed six event types; do NOT invent real RC/UART input or a `TRUSTED` status.
- Retain true semantics: two clean LOW at original times ≥20ms apart, HIGH edge on later committed tick, confirming neutral HIGH at ≥100ms later, ACTIVE next distinct HIGH demand >0.05, independent 200ms RF/frame freshness, S1 hold without refreshing timestamps, RF LOST→CONTINGENCY, qualifying recovery ACK, catastrophic latch. A simple slider at 50% without the protocol must **not** jump to ARMED/ACTIVE.

## 2. Four strict layers, one integrated app

```text
Offline operator edits → P226 action validation → deterministic wire-v2 scenario
  → real TASK-001 preflight + E2/E3 denied-authority reference boundaries
  → real TASK-013 F1 model and F0 comparator (existing dependencies)
  → internally acknowledged immutable ModelTick timeline
  → offline timeline viewer, effort bar playback, fault diagnostics
  → OPTIONAL proof report with authority=NONE and candidate trace label
```

The runner/adapter must **not** copy the F1 FSM, fork the old engine or write a twelfth checker. Use `bb_host_integrated_fsm_model.run_fsm_model` unchanged and its exact immutable report. Use only TEST_ONLY pinned fixture references for E2/E3; neither session JSON nor GUI controls can configure engine, policy, authority, sink, content manifests, host identity, or plugin import paths. Any preflight, E2/E3 or F1 model failure remains fail-closed and visible; do not normalize it into MODEL_REPLAY_COMPLETE.

## 3. Session/action input contract

Session file schema is supplied as `Design/fixtures/P226_STUDIO_ACTIONS.schema.json` and must be enforced by a strict parser (reject duplicates, unknown keys, bool-as-int, raw overquota, Unicode invalid, NaN/Infinity). Session actions each must include **unique id**, integer `at_us` (original microseconds) and one of `RF_HEALTHY`, `RF_LOST`, `RF_UNKNOWN`, `CONTROL_VALID`, `CONTROL_INVALID`, `RESET`, `ACK`, `CATASTROPHE`. `CONTROL_VALID` requires `flap_micro` and `steer_micro` signed integers in frozen ranges and `arm_switch` true/false; these are a UI input convenience, NOT a new wire revision. Emit demands as **integer decimal/fractional values** retaining exact millionths; use `Decimal(micro)/1_000_000`, serialize exact JSON numeric tokens (not a string); avoid binary float. `CONTROL_INVALID` maps to in-band invalid UART. `RF_*` maps injected-sim provenance. Original session is not a real receiver stream.

- Fixed `context` `PC_SIM`, `provenance=SIM_ONLY`, `config_id=sim-only-c0-v1`, step=5000; generated `scenario_id` deterministic ASCII from the session ID; do not let user override those fields or `schema_version=2`.
- Closed session size ≤2,097,152 bytes, action count ≤19,999 plus one BOOT, virtual duration 5,000..60,000,000 microseconds, max 12,001 model ticks, output diagnostic ≤16,777,216 bytes. If multiple action original timestamps coincide, preserve session order and deterministic event IDs.
- Never allow an action at 0, negative/noninteger/over-duration time, changing prior state directly, importing a file as Python, or deleting BOOT. Replaying a session must reproduce identical generated wire bytes and candidate hash independent of filename, wall time and OS timezone.

## 4. Denial-first operational boundary and safety gate

- Operational data type `VirtualRuntimeBoundary` must be frozen and deny-only, with exact values `runtime_authorized=False`, `output_allowed=False`, `actual_virtual_output=None`, `physical_output=None`, `control_trace_sha256=None`, `requires_owner_provisioning=True`. No boolean `approved` caller arg, external callback, host attestation stub with PASS, or mock certificate/secret as authority.
- MODEL_ACTIVE allows only `model_effort_left/right_micro` in display. Trace candidate is only Stage F1 `MODEL_TRACE_CANDIDATE_NOT_OPERATIONAL`; not an R1 `COMPLETED` runtime trace even if serialization and digest match. A protocol-level successful MODEL run still has `TRUST_NOT_PROVEN` and **no actual output publication**. A test-only synthetic `PASS` MUST NOT flow into output gate. Do not add PWM/angle mapping, serial packets, RC device link, or hardware HAL.
- Runtime trust may **not** be created from E2 reference equality, E3 self-consistency, CI green tests, Owner UAT approval for this task, a manifest with `signature`, a repository SHA, or a GUI toggle. Design/197 is a future **Owner security decision** packet, not a provisioned allowlist.
- Transactional model reporting: no view render, timeline row, or file export from an unacknowledged model tick; if internal F1 append fails or session validation fails, surface blocked outcome without making optimistic output. F1 error `HEALTHY+UNKNOWN` remains `MODEL_CONTRACT_BLOCKED` and no candidate complete digest. Offline HTML may have Play/Pause/slider for local playback, but no control injection bridge into already-committed model and no network/device permissions.

## 5. Determinism/scale/observability

At least three guaranteed demo sessions: `nominal` reaches MODEL ACTIVE with one displayed bounded pair, later RF LOST and separately qualified recovery; `rf-loss` shows unsafe HIGH/invalid/recovered but no illicit model output; `ambiguous` hits HEALTHY+UNKNOWN and terminates `MODEL_CONTRACT_BLOCKED` before the ambiguous tick. For each real scenario, tests compare state history and effort to authored P226 oracle values; direct F1 `run_fsm_model` on generated wire bytes must produce exact same result as Studio. Bad session -> zero full-model ticks; do not reuse previously successful report or stale HTML. No event/tick O(N*M) rescans, no unbounded GUI history copies.

## 6. Gate after TASK-014 (not delivered by TASK-014)

A later, separately Owner-approved trust/provisioning stage must bind protected allowlist, approved engine/scheduler revision, policy digest, executable identity, install path protection, signer, and owner review; prove append-before-publish and restrict **virtual sink only**. **No actual `output_allowed=true` runtime path is released under F2**. G0-B servo-only bench, G3 wings and G4 flight remain distinct, unapproved gates. Protect against test fixture/adversarial input self-approval.
