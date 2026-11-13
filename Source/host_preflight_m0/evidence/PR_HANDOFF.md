TASK-001 adds the approved PC-only host library: raw Wire v2 bytes produce either an immutable accepted scenario or exactly one closed Diagnostic Sidecar v1. Exact decimal pilot tokens normalize to integer millionths, and pure M0 arithmetic returns bounded efforts with deterministic clip tags.

The owner confirmed acceptance testing and authorized this PR on **2026-11-13 (Asia/Saigon)**. **SA review is requested; do not self-approve or merge.**

## Scope and authority

- Task: `Task/TASK-001_HOST_PREFLIGHT_M0.md` (owner-supplied local release artifact).
- Branch: `feature/TASK-001-host-preflight-m0` to `main`.
- Immutable baseline and verified remote main: `f378ec294a4a05887b03a9431696994dc22c0a4f`.
- Approval: `Design/156_G0A1_DIAGNOSTIC_V1_APPROVAL_AND_TASK001_RELEASE.md`, matched to the owner-supplied release manifest.
- All changed files are in `Source/host_preflight_m0/**`; Design, Task, root files and ReviewPR are unchanged.
- Runtime uses only the standard library; test/build dependencies are pinned and license-reviewed. No third-party reference source was copied.

## Verification actually executed

| Check | Result |
|---|---|
| Pre-PR full unit/integration suite | **203 PASS, 0 FAIL, 0 SKIP**, 5.05 s |
| P212-T01..T26 | **26/26 PASS** (included above) |
| Complete P_* registry | **27/27 PASS** (included above) |
| Frozen M0 vectors | **12/12 PASS** (included above) |
| Approved positive scenario fixtures | **6/6 PASS** (included above) |
| Development smoke | **6 PASS, 0 FAIL** |
| Installed-wheel smoke | **6 PASS, 0 FAIL** |
| pip dependency check | PASS, no broken requirements |
| Delivery build / compile | Wheel and sdist built; syntax compilation exit 0 |
| Baseline provenance | **32 exact Git blobs and 2 release artifacts MATCH** |

Python **3.11.15**, Windows 10 AMD64. Runtime/test files are byte-identical to the owner-tested delivery; pre-PR changes update only handoff documentation/evidence. No software failures were found in the executed suites. The initial sandbox dependency-install attempt was blocked by network permissions; installation succeeded after approval. The built wheel **0.1.0** is installed in local `.test-env`, and its runtime files match source.

Evidence:
- [Pre-PR execution log](https://github.com/nguyenbui5701/BionicButterfly/blob/feature/TASK-001-host-preflight-m0/Source/host_preflight_m0/evidence/pr-verification.log)
- [AC-01..AC-10 evidence map and delivery report](https://github.com/nguyenbui5701/BionicButterfly/blob/feature/TASK-001-host-preflight-m0/Source/host_preflight_m0/evidence/REPORT.md)
- [Full testcase inventory and results](https://github.com/nguyenbui5701/BionicButterfly/blob/feature/TASK-001-host-preflight-m0/Source/host_preflight_m0/evidence/pytest.xml)
- [Build/install/test commands and exit codes](https://github.com/nguyenbui5701/BionicButterfly/blob/feature/TASK-001-host-preflight-m0/Source/host_preflight_m0/evidence/commands.json)
- [Interpreter/dependency versions and artifact SHA-256](https://github.com/nguyenbui5701/BionicButterfly/blob/feature/TASK-001-host-preflight-m0/Source/host_preflight_m0/evidence/environment.json)
- [All selected paths and pinned hashes](https://github.com/nguyenbui5701/BionicButterfly/blob/feature/TASK-001-host-preflight-m0/Source/host_preflight_m0/evidence/baseline.json)

## Critical frozen Git blobs

| Contract | Git blob SHA-1 |
|---|---|
| Design/150 diagnostic sidecar | `b96beba505a4db94c16e1c0f2b0f8ec65fd740f9` |
| Design/151 precedence/pointers | `d1ba14b4d8cf31926353fb72fb20c29c148a9a40` |
| Sidecar schema | `d41091455e112cbcede1c7c0ce391c91827bfb41` |
| Issue registry | `ed7cb5305bf40996a006ac853d7b1990de4eaa70` |
| Wire v2 schema | `1d10c76e34be70880a65252d89a6bca89839fea9` |
| M0 machine contract | `dfde74e76b1bd7eb44088e6d49d06dd1a46cc759` |
| M0 golden vectors | `165aee1347a619c6f2514e522bf0e4fc4b518a6c` |
| P212 oracle index | `41b5536d37042cb68e71f0c37c40e0b08272617f` |

## Reproduce in an isolated SA checkout

SA should use `ReviewPR/pr-<PR_NUMBER>/` according to Design/11. Developer has not created or modified that area. From the checkout's `Source/host_preflight_m0`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q src tests scripts
.\.venv\Scripts\python.exe -m build --no-isolation
.\.venv\Scripts\python.exe -m venv .test-env
.\.test-env\Scripts\python.exe -m pip install --no-index --no-deps dist\bb_host_preflight_m0-0.1.0-py3-none-any.whl
.\.test-env\Scripts\python.exe scripts\smoke.py
```

If `py -3.11` is unavailable, use an existing Python 3.11+ executable as documented in README. The task workstation uses an existing uv-managed Python 3.11.15.

**Release artifacts:** `Design/156`, `Task/TASK-001_HOST_PREFLIGHT_M0.md` and root `PACKAGE_MANIFEST.json` were already untracked when work began. They remain untouched and excluded from this source-only PR. The commands above run with the tracked Design fixtures. The aggregate `verify_delivery.py` and `verify_baseline.py` additionally require those original release artifacts. SA can read them from the owner's original workspace and verify the SHA-256 values recorded in `evidence/baseline.json`. This PR does not silently publish or modify them.

## Review focus and limits

- Verify raw/LEX/schema/semantic precedence, first offending token, pointer escaping, closed tagged unions and malformed-input rejection before any accepted data construction.
- Review the frozen-schema-only evaluator and independent Draft 2020-12 differential corpus, exact digit/exponent predicates (including oversized exponents), immutable accepted data and direct M0 caller rejection.
- Review sidecar isolation and source import/call audit: no core runner, clock, trace sink or actuator is instantiated. No fabricated simulator report is used as evidence.
- Check license/version pins and the AC table in REPORT.md. SA review remains pending; owner acceptance testing is not a substitute for code review.
- Effective OS timezone switching was **NOT RUN** because Windows Python lacks `time.tzset`; two actual locales and two TZ environment values were tested with equivalent results.
- No event scheduler, safety FSM, host policy allowlist, runtime E_FRAME_INVALID handling, trace/replay, network, GPIO/PWM, servo or physical flight implementation. No hardware/flight readiness claim.

## Complete changed-file inventory

**40 new files**, all under the allowed subtree:

- `Source/host_preflight_m0/.gitignore`
- `Source/host_preflight_m0/DEPENDENCIES.md`
- `Source/host_preflight_m0/MANIFEST.in`
- `Source/host_preflight_m0/README.md`
- `Source/host_preflight_m0/evidence/PR_HANDOFF.md`
- `Source/host_preflight_m0/evidence/REPORT.md`
- `Source/host_preflight_m0/evidence/baseline.json`
- `Source/host_preflight_m0/evidence/baseline.log`
- `Source/host_preflight_m0/evidence/build.log`
- `Source/host_preflight_m0/evidence/commands.json`
- `Source/host_preflight_m0/evidence/compile.log`
- `Source/host_preflight_m0/evidence/dependency-check.log`
- `Source/host_preflight_m0/evidence/editable-install.log`
- `Source/host_preflight_m0/evidence/environment.json`
- `Source/host_preflight_m0/evidence/pr-verification.log`
- `Source/host_preflight_m0/evidence/pytest.log`
- `Source/host_preflight_m0/evidence/pytest.xml`
- `Source/host_preflight_m0/evidence/smoke-development.log`
- `Source/host_preflight_m0/evidence/smoke-installed-wheel.log`
- `Source/host_preflight_m0/evidence/source-inventory.json`
- `Source/host_preflight_m0/evidence/test-environment.log`
- `Source/host_preflight_m0/evidence/wheel-dependency-check.log`
- `Source/host_preflight_m0/evidence/wheel-install.log`
- `Source/host_preflight_m0/evidence/wheel-location.log`
- `Source/host_preflight_m0/pyproject.toml`
- `Source/host_preflight_m0/scripts/smoke.py`
- `Source/host_preflight_m0/scripts/verify_baseline.py`
- `Source/host_preflight_m0/scripts/verify_delivery.py`
- `Source/host_preflight_m0/src/bb_host_preflight_m0/__init__.py`
- `Source/host_preflight_m0/src/bb_host_preflight_m0/diagnostics.py`
- `Source/host_preflight_m0/src/bb_host_preflight_m0/exact_decimal.py`
- `Source/host_preflight_m0/src/bb_host_preflight_m0/lexer.py`
- `Source/host_preflight_m0/src/bb_host_preflight_m0/mixer.py`
- `Source/host_preflight_m0/src/bb_host_preflight_m0/schema.py`
- `Source/host_preflight_m0/src/bb_host_preflight_m0/wire.py`
- `Source/host_preflight_m0/tests/conftest.py`
- `Source/host_preflight_m0/tests/test_boundaries.py`
- `Source/host_preflight_m0/tests/test_isolation.py`
- `Source/host_preflight_m0/tests/test_math.py`
- `Source/host_preflight_m0/tests/test_oracles.py`
