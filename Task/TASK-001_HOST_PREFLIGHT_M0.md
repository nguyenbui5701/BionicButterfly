# TASK-001 — HOST_PREFLIGHT_M0 (PC-only Input Preflight + Diagnostic Sidecar v1 + Virtual Mixer M0)

| Field | Value |
|---|---|
| **Task ID** | `TASK-001` |
| **Status** | **OPEN — AUTHORIZED FOR DEVELOPER IMPLEMENTATION** |
| **Issued by** | Solution Architect (SA), based on explicit owner approval, 2026-11-13 |
| **Assignee** | AI Developer / coding agent |
| **Repository** | `https://github.com/nguyenbui5701/BionicButterfly` |
| **Source baseline — immutable** | `f378ec294a4a05887b03a9431696994dc22c0a4f` (`BionicButterfly Phase 2.12`) |
| **Scope/gate** | **G0-A1, PC_SIM_ONLY**; software *design* R1.1 + Diagnostic Sidecar v1 owner-approved |
| **Decision evidence** | `Design/156_G0A1_DIAGNOSTIC_V1_APPROVAL_AND_TASK001_RELEASE.md` plus the owner's explicit chat authorization |
| **Task branch** | `feature/TASK-001-host-preflight-m0` (from an owner-provided/verified current branch containing this task and the pinned contracts) |
| **PR/merge** | Create PR, submit test evidence; **do not self-approve or merge** |

> **Important:** This task implements pure host functions. An accepted preflight scenario is **NOT** authorized to run the R1 state machine, control an actuator, or claim valid flight. This first task deliberately does not create a simulator executable.

## A. Goal and success boundary

Build a small deterministic host-only library that:

1. Validates **raw bytes** as the approved closed **Scenario Wire v2**, with strict syntax, schema and cross-event semantic checks.
2. For rejected input, produces **one deterministic preflight diagnostic sidecar** using exactly the approved `P_*` registry/JSON Schema, with no core tick or virtual output.
3. Converts valid exact decimal pilot token values to integer micro units without binary floating rounding, and evaluates the **approved pure M0 mixer** including clipping tags.
4. Provides reproducible automated tests and PR evidence (actual PASS/FAIL counts, not authored expectation marked as test success).

**Do not** implement event scheduler, BOOT→ACTIVE FSM, ACK/RESET safety transitions, RF freshness, policy allowlist, trace writer, canonical replay, UI, network service, sensor, battery monitor, GPIO/PWM, hardware RC, servo, or physical flight control. These belong to later tasks and gates.

## B. Pre-implementation reading — required, exact paths

All paths are in the BionicButterfly repository. The Developer **must read these files and verify their exact Git blob SHA against the pinned baseline before coding**. A movable `main` is not a substitute for the pin.

| Priority | File | Reason / pinned blob (where critical) |
|---|---|---|
| 1 | `Design/07_AI_CODING_RULES.md` | Developer ownership, safety, no silent design changes |
| 1 | `Design/10_SA_OPERATING_RULES.md` | Distinguish Developer and SA responsibilities |
| 1 | `Design/11_HANDOFF_PR_WORKFLOW.md` | Task branch, PR, isolated SA review |
| 1 | `Design/156_G0A1_DIAGNOSTIC_V1_APPROVAL_AND_TASK001_RELEASE.md` | Owner approval, exact authorized scope; issued together with task |
| 1 | `Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md` | Approved R1/R1.1 authority precedence |
| 1 | `Design/150_G0A1_PARSER_DIAGNOSTIC_SIDECAR_CONTRACT.md` | Sidecar shape, isolation; blob `b96beba505a4db94c16e1c0f2b0f8ec65fd740f9` |
| 1 | `Design/151_G0A1_PREFLIGHT_PRECEDENCE_POINTER_AND_ERROR_REGISTRY.md` | Exact stage/order/JSON Pointer rules; blob `d1ba14b4d8cf31926353fb72fb20c29c148a9a40` |
| 1 | `Design/contracts/G0A1_PREFLIGHT_DIAGNOSTIC_V1_CANDIDATE.schema.json` | Approved closed sidecar schema; blob `d41091455e112cbcede1c7c0ce391c91827bfb41` |
| 1 | `Design/contracts/G0A1_PREFLIGHT_ISSUE_REGISTRY_V1_CANDIDATE.json` | Approved 27-code registry; blob `ed7cb5305bf40996a006ac853d7b1990de4eaa70` |
| 1 | `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | Frozen input union v2; blob `1d10c76e34be70880a65252d89a6bca89839fea9` |
| 1 | `Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md` | Cross-field limits beyond JSON Schema |
| 1 | `Design/133_R11_VIRTUAL_MIXER_M0_EXACT_ARITHMETIC_CANDIDATE.md` | F±S, micro units, clips and independence from active-state gate |
| 1 | `Design/contracts/G0A1_MIXER_M0_R11_CANDIDATE.json` | Frozen M0 machine contract; blob `dfde74e76b1bd7eb44088e6d49d06dd1a46cc759` |
| 1 | `Design/fixtures/P210_M0_GOLDEN_VECTORS.json` | 12 approved golden vectors; blob `165aee1347a619c6f2514e522bf0e4fc4b518a6c` |
| 1 | `Design/fixtures/P212_PREFLIGHT_NEGATIVE_ORACLE_INDEX.json` | P212-T01..T26 cases; blob `41b5536d37042cb68e71f0c37c40e0b08272617f` |
| 2 | `Design/117_G0A1_INPUT_RESULT_ERRORS_R1.md` | Preserve frozen `E_*` / result semantics |
| 2 | `Design/136_R11_INTERFACE_TEST_ORACLES_AND_STATIC_CHECKS.md` | Inherited R1.1 validation/oracles |
| 2 | `Design/142_R11_INPUT_EVENT_AND_PARSER_FREEZE_REVIEW.md` | Known parser gap, now authorized for closure |
| 2 | `Design/153_G0A1_FIRST_DEVELOPER_HANDOFF_READINESS_NOT_TASK.md` | Pre-task technical decomposition, not authority to expand scope |
| 2 | `Design/154_PHASE212_PARSER_DIAGNOSTIC_ORACLE_MATRIX.md` | Test meaning, not runtime PASS |

Also read positive and negative exemplars in `Design/fixtures/P210_*` and `Design/fixtures/P212_*`, especially `P210_MINIMAL_WIRE_V2.json`, `P212_INVALID_DUPLICATE_KEY_RAW.json`, `P212_INVALID_DUPLICATE_EVENT_ID_WIRE_V2.json`, and `P212_POSITIVE_INBAND_UART_INVALID_V2.json`.

**Preflight baseline check:** include the verified commit, selected paths, and hashes in the PR description. If any exact pinned file differs, stop and request SA reconciliation before implementing changed behavior. The approved contract may have `_CANDIDATE` in its historical filename; it is approved **by exact bytes and the separate decision record**, not by filename.

## C. Allowed implementation area and technology (for THIS task only)

- **Allowed write subtree:** `Source/host_preflight_m0/**` (create folder; no `Source/` currently present on the checked public repository).
- **Suggested layout:** `Source/host_preflight_m0/pyproject.toml`, `src/bb_host_preflight_m0/{wire.py, diagnostics.py, exact_decimal.py, mixer.py}`, `tests/`, `README.md`, local `.gitignore`.
- **Task-local implementation profile:** Python **3.11+**, pure host runtime, deterministic tests. Use Python's standard library where possible; a JSON Schema Draft 2020-12 validator may be an explicitly pinned, license-reviewed dependency. Dependencies and exact versions must be declared in `pyproject.toml` (including test extras). This choice **does not** decide the future ESP32 firmware toolchain.
- **No other writes:** do not modify `Design/`, `Task/`, root `.gitignore`, `README.md`, firmware, CI workflow, lockfiles outside allowed subtree, or `ReviewPR/`. If any of those become necessary, request change-control approval.
- No use of physical/network adapters, plugin loading, arbitrary file path execution, subprocess actuator scripts, remote fetch, realtime clock, OS environment-based behavior, RNG, hardware interface libraries or external media/licensed source reuse.
- Keep `Source/host_preflight_m0/.venv`, caches, bytecode and build artifacts out of Git via a local `.gitignore` under the allowed subtree.

## D. Required public library boundary (behavior, not prescribed class names)

1. `validateWire(raw_bytes, frozen_wire_v2_schema, policy_limits)` → either `ACCEPTED_PREFLIGHT` + immutable validated scenario data, **or** `VALIDATION_REJECTED` + exactly one Diagnostic Sidecar v1 object. No partial accepted result; never instantiate a core runner, safety state machine or trace writer. Raw size check occurs **before** decoding/JSON parsing.
2. `normalizeExactMicros(raw_number_token)` → integer micro units for a valid exact decimal pilot value. Do not parse to binary64 before scaling. Integers and exponents such as `1e-6` are permitted by the approved six-micro-decimal rule; values such as `0.0000005` are rejected, never rounded. Boolean-as-integer is invalid; `NaN`, `Infinity`, `-Infinity` are invalid JSON. Returned field names or internal types may follow Python conventions, but observable outputs and tests must match approved bytes/semantics.
3. `mixM0(flap_micro, steer_micro)` → `(left_micro_effort, right_micro_effort, sorted_mixer_clip_tags)`, using exact integers. Input validity follows the approved domains `F∈[0,1000000]`, `S∈[-1000000,1000000]`; output clamped to `[0,1000000]` on each side. If a direct library caller violates the typed preconditions, **reject the call** without output or silently clamping invalid inputs (no new public `P_*` code invented for invalid direct invocation). `M0` is pure arithmetic, **never an actuator driver or proof of ARM permission**.

Do **not** introduce extra top-level output fields into frozen R1.1 `SimulationRunReportV2`. Diagnostic Sidecar is a **separate, closed external object**, and `P_*` must never enter `reason_codes` or the trace.

## E. Normative parser safety, order and deterministic diagnostic contract

- RAW precedence: `P_INPUT_TOO_LARGE` (>2,097,152 input bytes) → `P_UTF8_INVALID` → `P_UTF8_BOM`. Hash exactly the **raw original bytes** (SHA-256), including malformed and oversized inputs; do not leak their contents.
- LEX: strict UTF-8 JSON, no duplicate keys at any depth, no comment/trailing comma, NaN/Infinity, unpaired surrogate, or depth >16. Use the deterministic **first offending raw-byte token** selection with tie rules from `151`; no last-wins duplicate repair.
- SCHEMA: validate against approved Draft 2020-12 **closed** v2 union; explicitly distinguish wrong version/context/provenance/config_id/event type/array capacity/alignment from generic validation errors; choose a unique violation according to `151` (do not leak validator-specific `oneOf` error order).
- SEMANTIC: global `event_id` uniqueness → BOOT exactly first T0 and no other event at T0 → original event timestamp nondecreasing and within duration → exact UTF-8 identifier byte limits/control characters → exact decimal micro precision. No silent migration from wire v1 to v2.
- Return **one primary issue** using exactly `P_*`, `stage`, `json_pointer`, and `frozen_base_error_code` from the approved registry. JSON Pointer segments must escape `~` to `~0` and `/` to `~1`. Use `""` for root/non-trustworthy syntax tree. Use `null` only where the approved schema/registry specifies it. `run_status=VALIDATION_REJECTED`, `evaluated_tick_count=0`, `evidence_complete=false`, `scope=PC_SIM_ONLY`, `diagnostic_format_version=1`.
- Legal in-band `SIM_CONTROL_FRAME` with `uart_frame_status=INVALID` **must pass parser preflight**; `E_FRAME_INVALID` belongs to later runtime logic, not a `P_*` parser issue. Same-tick distinct VALID frames are accepted at preflight; conflict resolution belongs to the future FSM.
- Validation is independent of wall time, locale, timezone and dictionary input iteration order. An accepted scenario is **not** a host-trusted policy; loader/allowlist is explicitly deferred.

## F. Acceptance criteria — must be evidenced, not merely checked in a checklist

| ID | Observable acceptance condition | Minimum proof |
|---|---|---|
| **AC-01** | Package contains no hardware/network effects, and all source/test writes stay in `Source/host_preflight_m0/**`. | PR changed-file list + import/dependency review. |
| **AC-02** | Complete raw/LEX/SCHEMA/SEMANTIC validation of v2 bytes; rejection prevents creating core ticks or virtual outputs. | P212 negative tests and mock counters `tick_count=0`, no trace/actuation call. |
| **AC-03** | For each `P212-T01..T25`, exact primary `code`, `stage`, RFC6901 pointer, `frozen_base_error_code` and raw SHA-256; sidecar validates against approved JSON Schema. | Machine-oracle-driven tests and source bytes / mutation recipe. |
| **AC-04** | `P212-T26` and all approved valid v2 fixture examples are accepted at *preflight*, including injected UART INVALID. | Positive fixture tests; no claim that later FSM ran. |
| **AC-05** | Every one of the 27 `P_*` registry values is represented by at least one focused unit test, with deterministic multiple-error precedence, nested duplicate-key and pointer-escaping cases. | Test case inventory + run output, no ignored/xfail unknown behavior. |
| **AC-06** | Exact pilot Decimal→micro conversion: exponent case, `-0`, six digits, seventh fractional digit, invalid boolean/nonfinite, UTF-8 identifier byte length/control tests. | Unit suite showing exact integers and rejected cases. |
| **AC-07** | `mixM0` matches **all 12** frozen P210 vectors, including correct clip tags and no clipping on equality; direct out-of-range/mis-typed caller is rejected. | Independent golden-vector test + boundary tests. |
| **AC-08** | Same raw bytes evaluated repeatedly produce equivalent deterministic accepted data or byte-equivalent stable canonical sidecar under two locale/timezone settings where supported. | Repeat-run comparison; report environment and platform. |
| **AC-09** | No changes to frozen R1/R1.1 contracts, Safety FSM, trace, report, policy or source outside allowlist; no code asserts hardware safety/flight readiness. | Git diff audit + SA review. |
| **AC-10** | Test run instructions and actual build/install/test logs are reproducible on Windows VS Code PowerShell; no secrets or sample user data leakage. | README, actual commands, Python+dep versions, test counts, output summary. |

**Scope qualifier:** For a library with no runner, "zero core ticks" means that no runner/clock/trace/sink is instantiated or invoked; test with call-spies/explicit absence, not a fabricated simulator summary. Do **not** create a full `SimulationRunReportV2` just to satisfy that phrase.

## G. Minimum test suite and test invocation (Windows PowerShell)

Developer creates runnable tests under the allowed subtree and records whether dependencies were successfully installed. Suggested commands after the module exists:

```powershell
cd Source\host_preflight_m0
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest -q
```

If `py -3.11` is unavailable, document the available Python executable/version and adjust commands **without changing the approved observable behavior**. An implementation-language change or new installation privilege should be raised as a task clarification before coding further.

Tests must include:

- Oracle-driven test `P212-T01..T26`; use raw bytes when required (not only parsed dictionaries); positive `INVALID` UART preflight.
- All 12 `P210_M0_GOLDEN_VECTORS.json` cases; plus clipping equality and invalid direct mixer inputs.
- Exhaustive registry coverage 27 codes and explicit precedence cases where RAW, LEX and SCHEMA errors coexist.
- Nested keys including `~` and `/`, duplicate member at arbitrary depth, Unicode surrogate/byte length, and 20,001-event capacity.
- Repeat deterministic result comparison; forbid strings of exception messages as public error codes.
- Negative security tests: wrong context `FLIGHT_TEST_APPROVED`, provenance `REAL_RF`, unapproved root property, `schema_version=1`, invalid or excess decimal precision.

**No invented test PASS:** if a case cannot run, record `NOT RUN` or `BLOCKED` and why. All mandatory AC checks must pass before PR can be accepted; untested oracles mean task remains open.

## H. Developer PR handoff package / Definition of Done

1. Implementation and unit tests only in `Source/host_preflight_m0/**`; documented Python and pinned dependency versions + licenses. Avoid unrelated work.
2. PR from `feature/TASK-001-host-preflight-m0`; include task ID in PR title and link to this task file.
3. PR description identifies `f378ec294a4a05887b03a9431696994dc22c0a4f`, Design `156`, the approved Sidecar schema/registry blobs, and the frozen scenario and M0 blobs. Compare against any later branch HEAD without modifying pinned contracts.
4. Exact source diff/file list; tests executed with command/output, actual PASS/FAIL/SKIP, PYTHON/platform/library versions, and provenance notes.
5. Acceptance table **AC-01..AC-10** with each linked to a test and result. No "PASS" based only on authored Design fixture.
6. Declare known limitations: no full simulator runner, no host policy allowlist, no GPIO/servo/flight safety claim, no runtime `E_FRAME_INVALID` handling.
7. Developer leaves `Task/` and `Design/` unchanged; no direct `main` commit, no force push, no automatic merge or cleanup.
8. **SA reviews only via isolated `ReviewPR/pr-<id>/` checkout**, inspecting diff, reproducibility, safety and licenses. A BLOCKER/MAJOR finding requires changes and re-review. Only the owner decides acceptance/merge; SA closes/removes task/checkout after owner confirms completion.

## I. Stop conditions / Request for SA clarification

Raise `BLOCKED — DESIGN CLARIFICATION` with the exact contract path, test vector, observed ambiguity and alternative outcomes if:

- Approved `150/151` disagree with pinned diagnostic schema/registry or existing frozen `E_*`/`R_*` behavior.
- The Python JSON Schema library returns non-deterministic error ordering that cannot be mapped using `151` without undocumented shortcuts.
- M0 clipping/Decimal semantics differ from the approved machine contract/golden vectors.
- Developer needs to modify `Design/`, root files, `Task/`, `ReviewPR/`, the real firmware, add networking or any runner/actuator access.
- The exact baseline hashes do not match, a library license is incompatible with public repository usage, or the test expectations are materially inconsistent with the approved schema.

**Do not** guess the design choice, introduce unsupported codes, weaken tests, or bypass safety restrictions just to mark the task done.

## J. Tracking

- **Task created by SA:** 2026-11-13. **Implementation:** NOT STARTED. **Tests:** NOT RUN. **PR:** NONE.
- **Design approval:** explicit owner chat decision (Diagnostic Sidecar v1 + first Developer task) recorded in `Design/156`.
- **Runtime G1:** NOT RUN. **G0-B/G4 hardware/flight:** NO-GO.
- **Completed by / PR / review / owner merge:** pending.
