# TASK-013 — Integrated system acceptance, model golden cases, UAT split

- ID BB-P225-192 · scope F1 `PC_SIM_ONLY / MODEL_ONLY`, baseline `eb4dbc8830d864c9cfd5c4d94bf00180aa960b5d`.
- Success means **one runnable** R1 behavior-model and JCS candidate trace/visualization package; not adding a standalone checker, not granting runtime output. Owner must be able to observe MODEL DISARMED → ARM_CHECK → ARMED_IDLE → ACTIVE, differential effort bars, RF LOST → CONTINGENCY, recovery via qualified ACK and catastrophe latch in offline browser/console. Output grants remain 0.

## 1. Frozen P225 model oracles

Machine-readable source `Design/fixtures/P225_F1_ORACLE_INDEX.json` contains **24 explicit requirements (P225-T01..T24)**; `expected` values come from Design/115, not calculated by the runtime under test. At least 18 separate negative/boundary families; do not invent 48 gratuitous tests. Run each test through genuine TASK-001–005, TASK-007/008 and E2/E3 real APIs. TASK-006 hypothetical PASS objects or TASK-009 E1 positive state seeding cannot stand in for admission. Assert both modeled behavior and **permanent operational denial** on every case. Test reference revisions are synthetically distinct and remain TEST_ONLY.

**Mandatory fixtures:** `nominal` tests two LOW original timestamps exactly 20ms apart, later HIGH edge, later HIGH confirmation exactly 100ms later, ACTIVE (>0.05), no-new-frame S1, RF loss to CONTINGENCY, restored HEALTHY + two LOW + later ACK to DISARMED, rearm and catastrophe latch. `recovery` includes earlier HIGH without LOW, short LOW interval and ACK without proper qualification, then valid recovery. `conflict` covers valid distinct conflict, equivalent duplicate, INVALID+VALID, RESET and catastrophe priority. Every MODEL positive must be labeled as counterfactual.

## 2. Separate negative/failure classes

N01 wrong raw Python types and frozen preflight mismatch; N02 E2/E3 mismatch/rejection -> zero modeled ticks; N03 foreign policy bytes, no override; N04 unauthorized scenario key and injected host/plugin/sink; N05 event ID duplicate rejected preflight; N06 conflicting valid control no admitted frame; N07 INVALID in-band with simultaneous VALID; N08 RF HEALTHY+LOST same tick -> LOST; N09 accepted original timestamps vs quantized ticks; N10 low 19999us FAIL and 20000us PASS; N11 high confirmation 99999us FAIL and 100000us PASS; N12 two independent timeouts inclusive 200000us vs 200001us; N13 HIGH held on boot, reset, no auto-rearm; N14 catastrophe+RESET+ACK+LOW => latch; N15 CONTINGENCY ACK without *prior* committed LOW must not recover; N16 S1 no accepted timestamp refresh; N17 model append short write/quota/no ack/terminal failure and no uncommitted render; N18 RFC8785 Unicode, UTF-16 key order, ECMAScript numbers and I-JSON malformed inputs; N19 complete trace SHA always null on operational result even if candidate hash exists; N20 no OS file, network, GPIO/PWM/serial, callback or hardware APIs in pure runtime; N21 deterministic replay locale/TZ differences; N22 60s/20000-event bound; N23 no positive verdict from TASK-006/D2; N24 model HTML cannot call API to affect state/output.

**Required outputs:** 24 named oracle JUnit tests; meaningful negative tests by class; CLI demos for three cases, read-only self-contained HTML viewer; vector-by-vector RFC8785 independent comparison (not just local self-consistency); negative system test proving UI cannot change model run. CLI prints `MODEL_ONLY / RUNTIME_NOT_PROVISIONED / NO_ACTUATOR_OUTPUT` and uses a distinct `model_state` label. Full R1 trace digest, PASS runtime, accepted runtime control/physical output never asserted.

## 3. DEV CHECK versus OWNER FULL UAT

**Developer**: `python -m pytest -q -p no:cacheprovider`, demo/smoke, JCS conformance, build, wheel install and pip check for TASK-013 only; targeted impacted regression when necessary. Prepare `scripts/verify.py --dev|--owner`; `--dev` must not run all TASK-001…012 regressions or claim they PASS. Save machine-readable evidence and actual errors/retries as they happen.

**Owner** (in `Source/host_integrated_fsm_model` on Windows PowerShell):

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\demo.py --case nominal
.\.venv\Scripts\python.exe scripts\demo.py --case recovery --view evidence\owner\viewer.html
.\.venv\Scripts\python.exe scripts\verify.py --owner
```

Owner runs all **12 prior TASK regressions once** inside `--owner`, including TASK-012 (111 tests), full provenance, package build/wheel and fixed demo oracles. Report ACTUALLY RUN vs NOT RUN with real totals; no false PASS. After Owner confirms UAT, Developer checks hashes and obtains Owner's explicit permission before opening PR. No full-suite rerun solely for unchanged PR packaging. SA reviews exact HEAD in isolated worktree if available; Owner alone merges.

## 4. Acceptance criteria (AC01–AC12)

| AC | Concrete evidence |
|---|---|
| 01 | Exactly new `Source/host_integrated_fsm_model/**`; no edits to TASK001–012, R1 policy or Design. |
| 02 | Genuine v2 preflight, E2/E3 gates, 5ms scheduler, observation/temporal/priority/health/triage integration. |
| 03 | FSM model BOOT, SELF_TEST, DISARMED, LOW, EDGE, ARM_CHECK, IDLE, ACTIVE, S1, CONTINGENCY, ACK, FAULT_LATCHED, with immutable prior and exact original times. |
| 04 | Uses measured policy constants, exact Decimal-to-micro M0; no new wire event or synthetic TASK006 admission. |
| 05 | Model ARM/ACTIVE can be viewed offline, but **operational output fields never become authorized**. |
| 06 | Strict RFC8785/JCS serializer independently conformance-tested; candidate schema and bytes checked; no fake complete R1 runtime digest. |
| 07 | Private model append-before-state/visualization; fault injection before/short/after/terminal append; sticky fail closed and no publish of tentative tick. |
| 08 | Run three real pinned scenarios, console timeline and standalone read-only HTML effort/state viewer; demo examples document not physical wing motion. |
| 09 | All 24 P225 oracle IDs and negative classes N01–N24; deterministic event order, duplicate semantics, expected state timestamps. |
| 10 | 60s+20k-event legal case, memory/serialization quota, no O(ticks*events) rescan or huge unbounded object copies. |
| 11 | Developer DEV CHECK only, Owner FULL UAT regression TASK001–012 once, genuine evidence. |
| 12 | Policy/blob pins from baseline and 9 release hashes independently verified; test-only and G0-B no-go maintained. |

**STOP** if normative R1 policy and an intended modeled positive transition conflict; record a `BLOCKED — DESIGN CLARIFICATION` with exact tick, state and clauses. No silent fix by modifying upstream code or granting trust from source hashes.
