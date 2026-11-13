# TASK-001 — Host preflight + M0 (0.1.0)

Pure Python 3.11+ library for approved PC_SIM_ONLY input preflight, one external
Diagnostic Sidecar v1 on rejection, and exact integer M0 arithmetic. There is no
simulator executable, event scheduler, safety state machine, trace writer, host
policy allowlist, network service, hardware adapter or runtime UART fault handler.
Accepted preflight data and M0 results confer no ARM/output or flight permission.

## Windows PowerShell setup

Run these commands from `Source\host_preflight_m0`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\smoke.py
```

The checked workstation's `python` is 3.10.5 and its `py` launcher has no
registered interpreters. Python **3.11.15** was already available here, so the
actual environment creation command was:

```powershell
& "$env:APPDATA\uv\python\cpython-3.11.15-windows-x86_64-none\python.exe" -m venv .venv
```

Use an existing 3.11+ interpreter; do not substitute 3.10. All runtime code uses
the standard library. Exact test/build dependency versions are in `pyproject.toml`;
the installed versions and reviewed licenses are recorded in `DEPENDENCIES.md`
and `evidence/environment.json`. Network access is needed only to install tools,
never to import or invoke this library.

## Build, reproduce evidence, install for owner testing

```powershell
.\.venv\Scripts\python.exe scripts\verify_baseline.py
.\.venv\Scripts\python.exe scripts\verify_delivery.py
.\.test-env\Scripts\python.exe scripts\smoke.py
```

`verify_delivery.py` runs the full suite, pip dependency check, syntax compilation,
smoke check, wheel/sdist build, and installs the built wheel into `.test-env`.
It saves actual command outputs under `evidence/`. It uses offline build/install
commands after initial setup. `.test-env` contains the installed wheel with no
runtime dependencies; `.venv` is the editable development/test installation.
This local PC-only installation is the task's test deployment. No server/URL is
part of the approved library scope. Build artifacts and environments are ignored.

## Public API

```python
import json
from pathlib import Path
from bb_host_preflight_m0 import validateWire, normalizeExactMicros, mixM0

# Explicit caller-owned local fixture/schema reads, outside the pure library.
design = Path("../../Design")  # from Source/host_preflight_m0
schema = json.loads((design / "contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_text())
raw = (design / "fixtures/P210_MINIMAL_WIRE_V2.json").read_bytes()
result = validateWire(raw, schema)
assert result.status == "ACCEPTED_PREFLIGHT"
assert result.scenario["events"][0]["type"] == "BOOT"

assert normalizeExactMicros("1e-6") == 1
assert mixM0(500000, 250000) == (250000, 750000, ())
```

Snake-case aliases are available. `validate_wire` requires immutable `bytes`, the
approved decoded schema, and optionally the frozen `PolicyLimits()` object.
Changing schema or limits is a trusted-caller error (`TypeError`/`ValueError`),
not a new scenario diagnostic code. The schema fingerprint is checked without
depending on dictionary order; it is not a host trust/approval loader.

An accepted result contains only `status` and deeply immutable `scenario`
(mapping proxies, tuples, integers and exact Decimal pilot values). No micro
fields are injected into wire data. A rejection contains only `status` and one
`diagnostic` dictionary matching the frozen closed sidecar schema.
`canonical_sidecar(diagnostic)` serializes it deterministically for comparison;
it is not a runtime trace or a claim of RFC8785 replay certification.

`normalize_exact_micros` accepts a single JSON number **string** in the union of
pilot domains `[-1,1]`. It rejects whitespace, booleans, Python floats, nonfinite
tokens, out-of-domain values and nonintegral millionths. Flap's narrower `[0,1]`
domain is enforced by wire schema / direct mixer preconditions. `mix_m0` accepts
exact Python integers (not booleans), returning `(left, right, tuple_of_tags)`;
invalid direct callers raise instead of silently clamping inputs.

## Validation decisions

- Raw byte limit precedes UTF-8 decode and BOM detection; SHA-256 uses original
  bytes even for malformed/oversized inputs.
- Left-to-right strict JSON scanning preserves raw token order (UTF-8 decoding
  is order-preserving), detects nested duplicates, and limits container depth to
  16 including the root container. Lexical diagnostics expose root except for a
  duplicate member's escaped JSON Pointer.
- Schema evaluation covers **only the pinned wire schema's keywords**, not
  arbitrary JSON Schema documents. Its two tagged unions select the event type
  and UART status before branch payload validation. Otherwise properties follow
  decoded UTF-8 byte order, arrays use integer index order, and type errors
  precede enum/range errors at the same member. Specialized codes replace generic
  errors at their actual violating paths; they do not override earlier paths.
  An independent pinned Draft 2020-12 validator checks the differential corpus.
- Semantic passes follow the registry's category order. Identifier paths within
  a category follow canonical traversal, including events before scenario_id.
- Number predicates use decimal digit/exponent arithmetic without binary64 or
  Decimal context rounding. Exponents whose magnitude exceeds the whole token
  length cannot cancel the mantissa; a bounded comparison sentinel avoids
  constructing enormous integers. Such nonzero numbers always fail schema range
  or micro precision. Accepted values retain their exact mathematical value;
  zero, including exponent-form negative zero, normalizes to zero.

## Evidence and limits

See `evidence/REPORT.md` for the AC-01..AC-10 map and actual results, and
`evidence/baseline.json` for all verified paths/hashes. The P212 recipes are in
`tests/test_oracles.py`; no generated mutation input is treated as a design oracle.
All six valid P210/P212 scenario examples, injected UART INVALID, and distinct
same-tick controls are accepted only at preflight. Runtime `E_FRAME_INVALID`,
batch conflict resolution, freshness and all FSM behavior remain unimplemented.

The determinism test uses two actual Windows locales and two `TZ` environment
values. Windows Python lacks `time.tzset`; an effective OS timezone switch was
not performed. The library does not import time, locale or environment APIs.

Design/Task/ReviewPR remain unchanged. The owner confirmed acceptance testing and
authorized PR creation on 2026-11-13. SA review and owner merge remain separate.
See `evidence/PR_HANDOFF.md` for review commands and the source-only PR's release
artifact prerequisites.
