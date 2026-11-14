# TASK-013 integrated FSM model

MODEL_ONLY / RUNTIME_NOT_PROVISIONED / NO_ACTUATOR_OUTPUT.

This runnable PC package composes genuine TASK-001 preflight and M0, TASK-002
scheduling, TASK-003 observations, TASK-004 timestamps, TASK-005 priority,
TASK-007 health, TASK-008 diagnostic triage, and TASK-010/011 reference/intent
gates. TASK-012 runs separately as the F0 comparator, including its genuine
TASK-009 E1 journal. F1 never seeds or modifies E1. TASK-006 hypotheses are never
used as admission or authority.

The eight-state model owns immutable `ModeledPrior` history starting at BOOT.
It models distinct-tick LOW/HIGH qualification at exact original timestamps,
neutrality, strict ACTIVE threshold, independent RF/control freshness, S1 held
input, RF loss, qualified ACK recovery and permanent catastrophe latch. These
are counterfactual model decisions, not runtime authorization. D2 retains
`TRUST_NOT_PROVEN` even on a displayed MODEL ACTIVE tick.

## Run the integrated experience

From `Source/host_integrated_fsm_model` in Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\demo.py --case nominal --view evidence\dev\viewer-nominal.html
.\.venv\Scripts\python.exe scripts\demo.py --case recovery --view evidence\dev\viewer-recovery.html
.\.venv\Scripts\python.exe scripts\demo.py --case conflict --view evidence\dev\viewer-conflict.html
```

Open the generated `.html` locally in Edge or another modern browser. Use the
slider, Play timeline, Pause and Start to inspect recorded ticks. At nominal
145ms the MODEL ACTIVE effort pair is 250000/750000; 150ms holds it without
refreshing timestamps; 155ms RF loss enters CONTINGENCY with null effort;
190ms qualified ACK returns DISARMED; 335ms catastrophe latches. Recovery and
conflict presets show denied early ACK/HIGH, duplicate/conflicting frames,
RESET and catastrophe precedence. Each CLI prints the complete timeline.

HTML is standalone, uses no service or remote resource, and has a restrictive
Content Security Policy. The controls change only the displayed index in an
embedded recording, never model inputs or a Python process. Effort bars are
dimensionless mathematical M0 values, not servo position, PWM or physical wing
motion. `runtime_authorized=False`, `output_allowed=False`,
`actual_virtual_output=None`, `physical_output=None`, `control_trace_sha256=None`
remain permanent public results.

Optional `--candidate evidence\dev\nominal.model-candidate.jsonl` writes the
complete candidate byte stream after model analysis. This filename and report
label distinguish `MODEL_TRACE_CANDIDATE_NOT_OPERATIONAL` / `DESIGN_CONFORMANCE_ONLY`.
Its header uses the F1 MODEL revision. Its closed tick schema keeps all actual
output/request fields null and `input_mode=NONE`, even for MODEL ACTIVE. The
candidate terminal uses `FAILED` and `E_OWNER_DENIED` to avoid claiming trusted
runtime completion; public model success is only `MODEL_REPLAY_COMPLETE`.
The optional candidate digest is never a `control_trace_sha256`.

Exit codes: 0 MODEL analysis complete, 2 input/reference/contract blocked or
incomplete evidence, 1 adapter/integration/report error. A failed internal append
never exposes that tick or retries it; complete candidate hash is absent after
header/tick/terminal failure. Local file writes serialize first, then use a
temporary file plus atomic replacement; no power-loss durability is promised.

## Verification and Owner commands

The prepared `.venv` is Python 3.11. Independent conformance tests also require
`node` on PATH (development used Node/V8 v24.16.0). Node is a test reference,
not a runtime dependency, server or viewer connection. The JCS library wheel
`rfc8785==0.1.4` is stored offline in `vendor/`, with its SHA-256 and Apache-2.0
license. Exact build/test pins are in `pyproject.toml`.

Developer runs only:

```powershell
.\.venv\Scripts\python.exe scripts\verify.py --dev
```

This runs new tests, all 24 P225 oracles and N01–N24 families, independent JCS
vectors, three demos, dev/installed-wheel smoke, build/install/pip and provenance.
It builds dependency wheels from baseline Git without executing old test suites.

Owner runs the six Design/192 commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\demo.py --case nominal
.\.venv\Scripts\python.exe scripts\demo.py --case recovery --view evidence\owner\viewer.html
.\.venv\Scripts\python.exe scripts\verify.py --owner
```

Only `--owner` executes all TASK-001–012 regression suites. It uses baseline
copies under this task's `.cache/` because TASK-012's stress test writes relative
evidence. One explicit exception is TASK-001's preserved `evidence/baseline.json`:
its updated `head` and CRLF working bytes have a separate SHA-256 pin in the
inherited records. Staging verifies that pin and every consumer's expected hash,
then copies those exact bytes into the isolated workspace. The Git version of
that evidence file does not satisfy the preserved pin. No old Source/evidence
is modified, and no provenance assertion is bypassed. No old regression PASS is claimed
by DEV CHECK. Evidence is separate under `evidence/dev/` and `evidence/owner/`:
summary, JUnit, actual command logs, environment/build hashes, console timelines,
HTML and candidate JSONL. The executable/test/script/vendor fingerprint binds
results to the actual worktree, including uncommitted changes.

For a fresh checkout, create `.venv` with Python >=3.11, install the exact `test`
extra tooling pins from `pyproject.toml`, ensure Node is available, then run
`verify.py --dev` or Owner `--owner`. Verification installs pinned project wheels
and the bundled JCS wheel locally. The CLI requires this repository's frozen
Design fixtures; the runtime package takes seven independent explicit inputs.

## Evidence scope and remaining boundaries

Provenance checks 32 explicit Design/190 Git pins against baseline
`eb4dbc8830d864c9cfd5c4d94bf00180aa960b5d`, nine manifest-listed release files,
the manifest separately, the policy digest and 570 baseline files. Explicit pins
and release SHA-256 use exact bytes. Historical baseline files accept exact Git
blob bytes or Git's configured checkout normalization (old logs may store CRLF).
Task text also says “33 pins” once; the Owner instruction, Design/190 table and
manifest consistently specify 32, which is the checked inventory.

Independent JCS verification uses RFC 8785 Appendix B, 4120 deterministic binary64
comparisons with Node/V8, UTF-16 sorting/control escapes/no-normalization vectors,
strict malformed I-JSON rejection, exact P210 hand-authored bytes, frozen policy,
candidate schema/order/identity and every emitted candidate line. Binary64 is
only used for JCS number serialization; M0 arithmetic remains exact integer
millionths converted from TASK-001 Decimal values.

The 60s/20000-event test records elapsed time, Python allocation peak and candidate
bytes in `performance.json`; process peak memory is not measured. Locale tests
exercise C/English and different TZ environment values; actual Windows OS timezone
changes are not performed. Timing measurements are not performance guarantees.

HEALTHY+UNKNOWN in one tick is explicitly unresolved in the inherited contracts;
the model stops with `MODEL_CONTRACT_BLOCKED` and a diagnostic requiring SA
clarification, rather than inventing effective RF precedence. No positive oracle
uses that ambiguous batch. Unsupported voltage events remain rejected by v2.

The full **operational** R1 FSM/host trust/authorized trace/output integration,
hardware, PWM, servo, RF devices and G2/G3/G4 validation are outside this release.
See `evidence/hardware_ready_template.md` for an unapproved G0-B decision worksheet.
Owner FULL UAT and explicit permission are required before PR creation.

References: [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html),
[rfc8785.py upstream](https://github.com/trailofbits/rfc8785.py), and frozen
Design/190–193 plus R1/R1.1 in the repository. No runtime network access is used.
