# TASK-001 — HOST_PREFLIGHT_M0 delivery evidence

**Status:** OWNER ACCEPTED — the owner confirmed acceptance testing and authorized
PR creation on 2026-11-13 (Asia/Saigon). SA review remains pending.

**Branch:** `feature/TASK-001-host-preflight-m0`.
**Baseline / initial delivery HEAD:** `f378ec294a4a05887b03a9431696994dc22c0a4f`.
**Release authority:** owner-supplied `Design/156` and TASK-001, both matching
`PACKAGE_MANIFEST.json`. The newest owner instruction authorizes commit, push and
PR creation, and explicitly prohibits self-merge.

Pre-PR recheck: **203 PASS, 0 FAIL, 0 SKIP** in 5.05 s; development and
installed-wheel smoke each **6 PASS, 0 FAIL**; dependency check passed.
See [pr-verification.log](pr-verification.log). Before this recheck, all 20
delivered source/doc/test file hashes matched the owner-tested inventory. Only
handoff documentation/evidence is updated for this PR; runtime and tests are unchanged.

## Actual verification results

| Check | Actual result | Evidence |
|---|---|---|
| Full unit/integration suite | **203 PASS, 0 FAIL, 0 SKIP, 0 XFAIL**, 4.24 s | [pytest.log](pytest.log), [pytest.xml](pytest.xml) |
| P212-T01..T26 | **26/26 PASS** | `tests/test_oracles.py::test_p212` / XML |
| Complete P_* registry | **27/27 PASS** | `test_all_registry_codes` / XML |
| Frozen M0 golden vectors | **12/12 PASS** | `tests/test_math.py::test_frozen_golden` / XML |
| Valid P210/P212 scenarios | **6/6 PASS** | `test_all_positive_examples` / XML |
| Development smoke | **6 PASS, 0 FAIL** | [smoke-development.log](smoke-development.log) |
| Installed-wheel smoke | **6 PASS, 0 FAIL** | [smoke-installed-wheel.log](smoke-installed-wheel.log) |
| Syntax compilation | Exit 0 | [compile.log](compile.log) |
| Dependencies, development and test deployment | No broken requirements | [dependency-check.log](dependency-check.log), [wheel-dependency-check.log](wheel-dependency-check.log) |
| Wheel + source distribution build | Both built, exit 0 | [build.log](build.log) |
| Exact baseline verification | **32 Git blobs MATCH; 2 release artifacts MATCH** | [baseline.json](baseline.json), [baseline.log](baseline.log) |

These are executed results, not fixture-authored PASS claims. Full commands and
exit codes are in [commands.json](commands.json); interpreter, installed package
versions, platform and artifact SHA-256 values are in [environment.json](environment.json).
Initial dependency installation needed approved PyPI network access after the
sandbox blocked it. The recorded reproduction run builds/installs offline from
already installed pinned tools.

No test failures were encountered in the executed suites (118, then 199, then
203 tests as coverage was added). No known failing mandatory software check remains.

## Acceptance map

| AC | Developer evidence and outcome |
|---|---|
| AC-01 | PASS: all created deliverables under `Source/host_preflight_m0/`; runtime has no third-party imports. `test_runtime_has_only_pure_standard_library_imports` checks every module's AST. Dependency licenses reviewed in `DEPENDENCIES.md`. |
| AC-02 | PASS: raw, lexical, schema and semantic rejection tests; construction/mixer spies confirm no accepted scenario construction or mixer invocation on rejection. Explicit absence of runner/clock/trace/sink integration checked by import/call audit. No fabricated core execution counters. |
| AC-03 | PASS: machine-oracle tests assert full primary issue, stage, pointer, frozen E-code, original SHA-256, zero evaluated ticks and incomplete evidence; independent Draft 2020-12 validation checks sidecars. Two frozen reference sidecars also match exactly. |
| AC-04 | PASS: all six positive examples and P212-T26 accepted, including UART INVALID; distinct controls in the same tick accepted without rounding original time. No claim of runtime FSM execution. |
| AC-05 | PASS: 27 parameterized registry cases; overlapping RAW/LEX/SCHEMA/SEMANTIC errors, nested duplicates at depths 1/2/8/15/16, UTF-8 path ordering and `~`/`/` escaping covered. |
| AC-06 | PASS: exponent, negative zero, exact six-digit values, seventh-place rejection, nonfinite/boolean/type rejection, very long exponent/mantissa, identifier UTF-8 boundaries and C0/C1 controls. Decimal context precision=2 does not affect exact results. |
| AC-07 | PASS: 12 pinned M0 vectors, equality/no clipping and invalid direct caller tests. |
| AC-08 | PASS within platform capability: repeated accepted data and byte-identical sidecars under actual locales `C` and `English_United States.1252`, with TZ environment values `UTC0` and `ICT-7`. Effective OS timezone change **NOT RUN**: Windows Python has no `time.tzset`. Runtime imports no timezone/locale/environment API. |
| AC-09 | Developer audit PASS: no tracked baseline changes, frozen bytes match; all new task files within allowlist. SA review **PENDING**, not self-approved. No runtime safety/FSM/report/policy implementation. |
| AC-10 | PASS: PowerShell instructions in README, actual install/build/test/smoke output, pinned tool versions, local wheel deployment and environment details recorded. Logs replace machine-specific package/user-profile paths. |

The schema mutation corpus compares more than 500 mutations against the
independent `jsonschema` validator. The truncation corpus rejects every strict
prefix of the nominal wire bytes and repeats each rejection for determinism.
These cases execute inside named tests; they are not added to the 203 pytest
item count as separate PASS items.

## Implemented files

- `src/bb_host_preflight_m0/wire.py`: public result types, fixed limits, RAW and
  semantic validation, immutable accepted scenario construction.
- `lexer.py`: strict ordered JSON parser with duplicate/depth/surrogate checks.
- `schema.py`: deterministic evaluation of the exact frozen schema's keyword
  subset and discriminated event/UART branches.
- `diagnostics.py`: closed sidecar and deterministic serialization.
- `exact_decimal.py`, `mixer.py`: exact micro normalization and M0 arithmetic.
- `__init__.py`: snake-case and task-named API exports.
- `tests/`: oracle, registry, math, boundary, differential, determinism and
  isolation checks. `scripts/`: smoke and reproducible delivery verification.
- `pyproject.toml`, `MANIFEST.in`, local `.gitignore`, README, dependency review
  and this evidence folder complete the deliverable.

At initial delivery, `git status` was checked: `Design/156`, `Task/` and
`PACKAGE_MANIFEST.json` were already untracked owner-supplied files. They remain
untouched and excluded from the source-only PR. Initial delivery was uncommitted;
commit and push are now authorized by the owner. See the PR's Files changed tab
for the submitted inventory. Build environments, caches, egg metadata
and distributions are excluded by the task-local `.gitignore`.

## Local test deployment and owner verification

Version **0.1.0**, Windows AMD64, CPython **3.11.15**. The built wheel is installed
in `.test-env/Lib/site-packages`; [wheel-location.log](wheel-location.log)
confirms import origin. Every installed runtime `.py` file was compared byte for
byte with source. There are no runtime package dependencies.

From `BionicButterfly/Source/host_preflight_m0`:

```powershell
.\.test-env\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pytest -q
```

The first command tests the deployed wheel; the second runs the full editable
development suite. See README for API usage and clean setup. This is a local
PC-only library deployment; no hosted endpoint or simulator was created.

## Remaining scope and review

No known software bug remains from these checks. Effective timezone switching
was not tested on this Windows host. No full simulator, policy allowlist, FSM,
runtime UART invalid handling, trace/replay, GPIO, servo or flight test was run;
all are outside TASK-001. No hardware safety or flight readiness is asserted.

**Pull Request: OWNER AUTHORIZED — SA REVIEW PENDING.** Owner acceptance testing
is complete. PR creation is recorded in GitHub; merge remains the owner's decision.

The three owner-supplied release artifacts are not tracked on the baseline and
are not added outside the task's write allowlist. Full unit tests, smoke tests and
package build work in a clean PR checkout using the tracked Design fixtures.
`scripts/verify_baseline.py` and the aggregate `verify_delivery.py` additionally
require those original release artifacts at their repository paths. SA can read
them from the owner's original workspace and compare their hashes with
`evidence/baseline.json`; do not interpret their absence in a clean checkout as
a contract change. See `evidence/PR_HANDOFF.md` for self-contained review commands.
