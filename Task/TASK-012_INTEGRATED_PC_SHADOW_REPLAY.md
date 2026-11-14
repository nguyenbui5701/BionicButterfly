# TASK-012 — INTEGRATED_PC_SHADOW_REPLAY (Stage F0)

| Attribute | Decision |
|---|---|
| State | **SA RELEASED FOR OWNER → DEVELOPER HANDOFF** |
| Baseline merged main | `ccb6babea26be805f752b80488a7232eff70aa06` (PR #11) |
| Work objective | **One runnable end-to-end PC demo**, not an isolated policy checker |
| Developer may write | **`Source/host_integrated_shadow_replay/**` ONLY** |
| Scope | G0-A1 `PC_SIM_ONLY` **TEST_ONLY/NO_OUTPUT** |
| Branch recommendation | `feature/TASK-012-integrated-pc-shadow-replay` |
| PR | Only after Owner FULL UAT PASS and explicit authorization; Developer does not merge |

## Mandatory reading (before code)

1. Workflow `Design/07_AI_CODING_RULES.md`, `10_SA_OPERATING_RULES.md`, `11_HANDOFF_PR_WORKFLOW.md`.
2. Frozen approved Design/115, 116, 117, 118, 132, 133, 134, 141 and exact R1/R1.1 contracts/schemas. Do NOT reinterpret standalone `_CANDIDATE` suffix outside the approved Design/141 hierarchy.
3. Derived Design/179 (E1), 182 (E2), 185 (E3); read actual `Source/host_*` **public interfaces** and `Source/host_preflight_m0` exact M0 mixer. Keep all old modules immutable.
4. **New** Design/187 baseline/pins; **Design/188 Stage F0 integrated contract**; **Design/189 acceptance, DEV/OWNER UAT and G0-B roadmap**; `Design/fixtures/P224_*` four demo JSON + P224 20-oracle index + `Design/P224_TASK012_RELEASE_MANIFEST.json`.
5. Verify exact Git blob SHA pins from Design/187 against the **baseline commit**, release manifest hashes and R1 policy digest `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. Stop with `BLOCKED — DESIGN CLARIFICATION` on any conflict; do not silently modify frozen Design.

## Deliverable: a functioning integrated demo

Create Python >=3.11 package `bb-host-integrated-shadow-replay==0.1.0` with pure `run_shadow_replay(...)` and closed/frozen typed results defined in Design/188. CLI `scripts/demo.py` must allow:

```powershell
.\.venv\Scripts\python.exe scripts\demo.py --case pilot
.\.venv\Scripts\python.exe scripts\demo.py --case hazard
.\.venv\Scripts\python.exe scripts\demo.py --case conflict
.\.venv\Scripts\python.exe scripts\demo.py --case minimal
```

Output is an actual timeline of observed RC-like *simulated* control, RF, commit/no-commit and **mathematical wing preview**; always show `NO OUTPUT / ARM NOT GRANTED`. Use only genuine TASK-001→TASK-002→TASK-003→TASK-004→TASK-005→TASK-007→TASK-008→TASK-009 and E2→E3 integrations. TASK-006 remains hypothetical, not an authority input. Process current scenarios from actual frozen wire-v2 parser; exact original timestamps retained. E1 snapshot from real genesis; no arbitrary snapshot seeds; no fake positive data or state.

## Acceptance (AC-01…AC-12)

| AC | Required observable proof |
|---|---|
| 01 | Code/config/test/evidence only new `Source/host_integrated_shadow_replay/**` plus **nine** owner-approved Design/Task release files; no prior Source/policy changes. |
| 02 | Four actual bundled v2 demo files accepted by real preflight; valid E2/E3 TEST_ONLY context, no scenario approval injection. |
| 03 | All 10 composable upstream packages integrated: TASK-001/002/003/004/005/007/008/009 plus TASK-010/011 gates; TASK-006 only read as historical hypothetical boundary, never passed as verdict. |
| 04 | E1 genesis T0; prior facts derived from read-only snapshot; each chronological tick exactly once; no accepted RF/control timestamps/ARM/ACTIVE invented. |
| 05 | CLI visibly displays ARM request denial, RF LOST, conflict, RESET, catastrophe and left/right **preview** on actual eligible ticks; final state not falsely flight-ready. |
| 06 | Proper `mix_m0` exact Decimal→micro arithmetic and clipping tags, preview math never becomes real R1/servo output. |
| 07 | Input rejected/E2 mismatch/E3 mismatch produces ZERO shadow ticks and no trace/output; upstream-first ordering verified. |
| 08 | E1 ack/append ordering respected; fault injection before/after write yields failed incomplete evidence, no uncommitted row, no retry. |
| 09 | Strict immutable results, deterministic ordered causal IDs, stable replay/timeline under same inputs, correct quota and no output authority. |
| 10 | 20 genuine named P224 oracles + meaningful boundary/negative/property tests and four actual smoke demos; do not fabricate 48 arbitrary cases. |
| 11 | DEV CHECK only by Codex; Owner FULL UAT runs old TASK-001..011 regressions once. Store per-check evidence as ACTUALLY RUN / NOT RUN; never claim unexecuted regressions PASS. |
| 12 | `scripts/verify.py --dev` targeted and `--owner` full; package build/installed-wheel smoke; read-only provenance/hashes. No PR before Owner UAT and explicit permission. |

## Developer testing and Owner UAT

During coding, run unit/integration/P224, `scripts/smoke.py`, build/wheel smoke/dependency and optionally targeted impacted TASK checks. Do **NOT** run all old regressions by default. Provide repeatable one-command DEV CHECK and the exact five Owner UAT commands in Design/189. `scripts/verify.py --owner` must execute full old regressions; do not skip silently.

Developer final message must include `DEV CHECK PASS/FAIL`, actual unit/oracle/smoke counts, affected prior tests if run, evidence, 4 screenshots or console snippets proving visible timeline (console snippets sufficient), known incomplete FSM/actuation boundary and commands. Owner runs FULL UAT, explicitly approves PR. Codex then checks content hashes/PR diff only; SA reviews; Owner merges.

## Forbidden and next milestone

NO GPIO/PWM/servo, real receiver, RF hardware, ESP-IDF, physical flight, trusted signer/key, runtime allowlist, input-selected plug-in, virtual output publication, canonical R1 complete trace hash or caller-supplied permission. A green preview is **not** flight-ready. If an upstream API cannot be composed without a fake positive PASS, **STOP and return a design defect to SA**. This is the first integrated demonstration, not the last step before enabling physical wings. After F0, prioritize full FSM+trace PC and G0-B bench readiness in parallel.
