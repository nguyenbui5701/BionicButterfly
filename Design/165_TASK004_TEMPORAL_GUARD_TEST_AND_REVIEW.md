# G0-A1 — TASK-004 Temporal Guard Oracle / Review Matrix

- ID: BB-P216-165 | Source pin: `ed106d22c52647090768ef60fb1e4c33384e9227` | Oracle file: `Design/fixtures/P216_TEMPORAL_GUARD_ORACLE_INDEX.json`.
- At document-authoring time all cases are **SPECIFIED ONLY / NOT RUN against Developer code**.

## 1. Required oracle execution

For each **positive** case P216-T01..T22, construct legal wire-v2 original bytes from `P210_MINIMAL_WIRE_V2.json`, run actual TASK-001 `validate_wire` → TASK-002 `iter_virtual_ticks` → TASK-003 `normalize_tick_observations`, and invoke TASK-004 evaluator with an independent **synthetic, test-labeled prior-committed snapshot** (never from scenario JSON). Assert every exact output field, the absence of authorization fields, immutability of source/snapshot and repeated determinism. Positive cases include R1's 200000/200001 microsecond boundary on each independent channel and no automatic timestamp refresh.

| Oracle IDs | Meaning |
|---|---|
| T01–T02 | Initial/absent prior timestamps ⇒ both unknown and not fresh |
| T03–T06 | Accepted-control/RF exact 200000 boundary vs 200001 expiry |
| T07–T11 | Independent cross-channel freshness, staleness and missing fields |
| T12–T16 | Current RF HEALTHY-only candidate, duplicate healthy, mixed LOST, mixed UNKNOWN and LOST-only; no invented effective RF priority |
| T17–T20 | Current uncontested VALID control candidate, INVALID + VALID, semantic conflict + INVALID, RESET + VALID retained as only an observed candidate |
| T21–T22 | Prior RF-age fresh with current LOST; prior stale control with a new VALID observed candidate does not auto-refresh |

## 2. Additional negative/boundary tests (mandatory)

- `NormalizedTickObservations` wrong type, mutable object, forged subclass; prior snapshot wrong type/shape; `True` as int, float, negative, future timestamp, mismatched tick grid, omitted last committed tick, and prior-timestamp after last commit: reject with ordinary `TypeError`/`ValueError` before output.
- `T0` snapshot must be `(None,None,None)`; T>0 requires valid committed evaluation tick strictly before current evaluation tick. Test 60s final allowed tick; equal age in RF/control field independently, no float or clock.
- Confirm output fields exactly match contract, no `rf_effective`, `can_arm`, `accepted_frame_at_us`, `output_allowed`, `reason_codes`, state transitions or refreshed history. No FSM, M0, policy digest trust or trace IO imports.
- Current RF observations with conflicting statuses must not promote an uncontested HEALTHY candidate. Current LOST can coexist with `prior_rf_within_timeout=True` (age alone is not a health authorization).
- Re-run read-only TASK-001 (historically 203), TASK-002 (44), TASK-003 (59) regressions. These historical counts are **not** assumed PASS if dependency or environment changes; report actual results. Run build, package install, unit/integration, smoke, `pip check`, and isolation review.

## 3. Delivery and SA review

- Allowed Developer changes: only `Source/host_temporal_guard_facts/**`.
- Developer provides three Windows PowerShell commands for Owner UAT: pytest without cache, smoke, pip check. Owner can execute, inspect and share results instead of asking AI to repeatedly run identical commands.
- No PR until Owner accepts UAT and explicitly requests PR. Review in isolated `ReviewPR/pr-<n>`; request Developer fixes on BLOCKER/MAJOR, Owner only authorizes merge.
- Result of TASK-004 **cannot** certify host permit, ARM, 8-state FSM, actual RF, aircraft, lift, safety under real flight or in-air contingency.
