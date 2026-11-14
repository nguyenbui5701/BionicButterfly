# TASK-012 — integration acceptance, demo requirements and next servo bench gate

- ID **BB-P224-189**; baseline `ccb6babea26be805f752b80488a7232eff70aa06`; TASK-012 is **INTEGRATION**, not another pure reference checker.
- Owner decision from chat: Developer does **DEV CHECK** for new task (and impacted upstream suites only); Owner performs **OWNER FULL UAT** (full TASK-001..011 regression) once. No duplicated full suite runs solely for PR packaging.

## 1. The demonstration contract: see a full timeline, not just a number of tests

The test/CLI must use the **four pinned real v2 scenario JSON files** and frozen schema, plus E2/P222 and E3/P223 test-only references; it must not self-fabricate accepted headers. The core processes actual ticks through TASK-001/002/003/004/005/007/008/009 and separate E2/E3 preflight gates. M0 preview uses the frozen TASK-001 algebra only.

**Demo acceptance:**

- `pilot`: 8 rows T0..35ms, show two independent raw intent values and M0 preview L/R at eligible ticks; show ARM request but no granted ARM or active; LOST suppresses preview; catastrophe latches; output remains inhibited.
- `hazard`: LOST + INVALID, RESET with RF HEALTHY and catastrophe, then final RESET remains latched; never unauthorized output.
- `conflict`: different valid controls same tick -> conflict, semantically duplicate valid body -> one control group with both IDs, INVALID+VALID -> deny preview. All 4 tick summaries keep original causal IDs.
- `minimal`: BOOT and T1 non-armed bookkeeping, no preview, two complete in-memory E1 commits. `SELF_TEST` hold is **intentional pending full FSM**, not a passing self-test.
- Preflight rejection, E2 mismatch, E3 mismatch return **zero shadow ticks**. No accidental scenario-driven `owner` or `approved` mutation. If shadow E1 internal append fails, no publication of uncommitted tick and no retry.
- For every case `runtime_authorized=False`, `requires_full_fsm=True`, `actual_virtual_output=None`, `physical_output=None`, `canonical_control_trace_sha256=None`. End-user console must display `PC_SIM_ONLY / NO_OUTPUT / NOT A FLIGHT TEST`.

## 2. Machine oracles P224 and regression

Fixture `Design/fixtures/P224_INTEGRATED_SHADOW_ORACLE_INDEX.json` has exactly **20 P224-T01..T20 named cases**. Tests require real upstream packages for all valid cases, independent expected values from fixture and frozen spec, no patching upstream imports to fake a pass. Fault injection in T19/20 is explicitly private test-only and may use monkeypatch, not public error injection.

Additional required adversarial tests (do **not** inflate oracles count into artificial 48):

1. Input type, bool-as-int, mutated/rejected preflight, wrong schema, malformed and unauthorized scenario key, mismatched policy, E2/E3 wrong reference and impossible synthetic fingerprint.
2. Per-tick causal event timestamps (including subgrid original time), deterministic replay, and T0 BOOT exclusivity.
3. No skipped/duplicated tick, no double-call to upstream scheduler, correct E1 prior bridge, no positive accepted RF/control history or LOW/HIGH qualification.
4. ARM HIGH, apparent healthy RF/current candidate cannot trigger actual state change. No arbitrary test-only prior injection into public runner.
5. Fault precedence RESET vs catastrophe, FAULT_LATCHED persistence, error and quota failure fail-closed; no tentative tick printed after failed E1 append.
6. Correct exact Decimal math; preview clipped at [0, 1000000] in micro-units and tagged, never relabeled as servo angle/PWM or authorized output.
7. No scenario-selected path/driver/plugin/engine claim; no network, serial, RC, filesystem from pure core; only CLI can read fixtures or emit an offline report file.
8. Full cycle execution for a 60s legal scenario with 12001 ticks and at most 20000 events, bounded report and time/memory. No performance guarantee invented; report actual elapsed and peak process memory if measured. 20000 events concentrated in one tick must not be rescanned by every later tick.
9. CLI write/serialization/quota/permission failures do not leave a misleading complete report; no full R1 canonical control SHA anywhere.
10. Test physical safety by static import/namespace inspection: source has **no PWM/GPIO/servo, firmware, serial, network, external callback or hardware drivers**.

## 3. Developer DEV CHECK vs Owner FULL UAT

**Developer:** implement and test **TASK-012** unit/integration/20 P224, run `scripts/smoke.py`, package build/wheel-install/smoke and dependency check, static provenance of baseline/release; only target old TASK if a change impacts that API. Do NOT run full TASK-001..011 regressions as a routine DEV CHECK. Return exact results; do not claim not-run suites PASS.

**Owner:** from `Source/host_integrated_shadow_replay` run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\demo.py --case pilot
.\.venv\Scripts\python.exe scripts\verify.py --owner
```

`verify.py --owner` performs provenance/build/install/current suite/dev+wheel smoke + all prior TASK-001..011 regressions read-only, writes JUnit/compact evidence and truthfully counts PASS/FAIL/SKIP. `verify.py --dev` is separate and runs only TASK-012 DEV CHECK; MUST NOT label earlier regressions PASS.

After Owner UAT PASS + explicit PR permission, Developer checks exact hashes, creates PR and does not rerun full tests if no execution-affecting change. SA reviews PR against Design/188 and this document; Owner alone merges.

## 4. G0-B: parallel physical preparation, not a new proof-by-paper chain

The main project objective is **RC manual butterfly movement and eventually flight**, not endless offline trust diagnostics. This release includes a **G0-B readiness worksheet** to progress physical decisions in parallel with software; it does NOT authorize energizing servos.

| Mandatory decision/evidence before G2 servo-only power-up | Current as verified from Design/20–29, 31/35/38 | Next required action |
|---|---|---|
| Exact MCU, board revision, IO and power source | Candidate XIAO ESP32-C3; NOT FINAL | Select part; verify datasheet and boot-pin/PWM behavior |
| Exact left/right servo spec, PWM period, voltage, stall current, stroke/torque | Model TBD; NO MEASURED LOAD | Obtain exact datasheets; review disconnected-servo output envelope |
| RC transmitter, receiver firmware, channel mapping and UART voltage | Candidate ELRS/CRSF; NOT SELECTED | Verify 2.4 GHz variants, CH5 ARM semantics, RF fail state |
| Power/supply | Candidate 2S+BEC; not a wiring permit | Draw reviewed schematic with isolation, current limit, USB backfeed protection |
| Bench interlock and instrumentation | Planned only | Current-limited supply, meter/scope, physical stop, safe working area; documented signoff |
| Physical control/failsafe policy | G2/G3 and flight require different evidence | G2 servo-only safe state and loss-of-RF test plan; no in-flight fail response invented |
| Wing frame and mass/CG | Two-servo candidate ~70g estimate | CAD, mass budget, mechanical clearance; first G2 test **without wings** |
| RF/servo traces and acceptance criteria | Hardware evidence NOT RUN | Approval of G0-B Design/22–25, 27/28 before physical tests |

### Stage gates after TASK-012

- **NEXT software integration:** full R1 PC-only FSM + normative JCS/LF trace and append-before-output behavior in one cohesive G1 milestone after explicit security/Owner design gate; no extra disconnected E4/E5 trust check task unless a real blocker demands it.
- **NEXT physical (parallel):** signed G0-B bench design review, finalized schematic/BOM and servo-only G2 approval, then tested firmware HAL in a separate hardware-gated task. Do not call a PC M0 preview a servo control signal.
- **After G2:** restrained wings G3 for force, moment, CG, power and yaw/roll/pitch control evidence; free flight G4 remains NO-GO until distinct in-air contingencies approved.
