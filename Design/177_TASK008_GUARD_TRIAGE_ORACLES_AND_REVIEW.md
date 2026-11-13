# G0-A1 TASK-008 — Stage D2 Guard Triage Oracles and SA Review

- ID: BB-P220-177 · Baseline: `7c09bb5ab4d05d16bfa53439b5dab5b465ec8b05` · Scope `PC_SIM_ONLY`.
- Machine-readable fixture: `Design/fixtures/P220_GUARD_TRIAGE_ORACLE_INDEX.json` — exactly **36 P220-T01…T36 positive cases** plus **18 mandatory negative/test families**.
- **SA test status:** specification and static fixture validation only; TASK-008 Python, integration, regressions and physical/flight runtime are **NOT RUN**.

## 1. Required real data path for each positive case

Use the existing, pinned **P219** reference recipe selected by `source_case_id`, but generate legal v2 wire bytes and invoke the actual TASK-001 preflight → TASK-002 virtual scheduler → TASK-003 tick normalizer → TASK-004 temporal evaluator → TASK-005 C1 priority → TASK-007 D1 health evidence → **TASK-008 D2 triage**. The P219 recipe's separately synthetic `pre_state`, prior timestamps and RF snapshot must stay outside wire JSON. Never call TASK-006 or construct an admitted guard verdict. All **ten** D2 fields (metadata, enum lanes, candidate timestamps, ordered reasons and full-FSM marker) must be checked against **P220-authored expectations** and the actual upstream metadata, including exact Python types, immutable result, ordered enum tuple and `requires_full_fsm=True`.

`expected.current_*_candidate_original_at_us` values beginning with `=temporal.` are **declarative equality assertions** to actual TASK-004 data, not literal Python expressions; test code must explicitly access the typed field and compare. Do not eval fixture strings or accept an arbitrary user-provided expected timestamp as true. This intentionally avoids copying previous stage's raw timestamps while still checking the D2 mirror contract.

In addition, assert D2 does not mutate accepted scenario, normalized observations, temporal ages, priority assessment, D1 evidence or synthetic inputs. At T0 no past record can be created.

## 2. Positive oracle families

| P220 IDs | Safety coverage |
|---|---|
| T01–03 | BOOT no evidence, all-current HEALTHY observed, latest timestamp mirrored but never committed |
| T04–11 | LOST beats HEALTHY regardless order; UNKNOWN-only fails; HEALTHY+UNKNOWN stays ambiguous; triple mix LOST dominates |
| T12–18 | silence carried HEALTHY fresh=200000, stale=200001; carried LOST/UNKNOWN despite old fresh HEALTHY; later current HEALTHY not automatically committed |
| T19–24 | INVALID + VALID, conflict, single diagnostic candidate, RF missing/fresh/stale, no accepted timestamp refresh |
| T25–28 | ambiguous RF, LOST, RESET, catastrophe with current control — block; no priority inversion |
| T29–32 | no new control despite fresh prior frame; armed stale prior with current healthy/control remains blocked; duplicate equivalent grouping; current healthy after stale prior only diagnostic |
| T33–36 | prior UNKNOWN, current UNKNOWN, combined INVALID/conflict, latched prior despite healthy current |

## 3. Mandatory negative and structural tests

Implement **all 18** named test families listed in P220 JSON (N01…N18). Include adversarial contradictory dataclasses, mismatched timestamp mirrors, malformed enum values, original source provenance, invalid control/contradictory candidates, stale/control per-channel independence, and explicit positive-authorization API leakage checks. Specifically:

- Demonstrate exact `200000` vs `200001` µs boundary for **each** channel, including armed states with fresh in-tick candidates and previously stale records.
- Demonstrate armed `POTENTIAL_S1_UNVERIFIED` when prior RF/control ages are fresh and no new frame exists; verify it is **never** output permission. If prior hazard is active, `HAZARD_OR_UNRESOLVED` wins; if prior age stale, `PRIOR_STALE_OR_MISSING` wins.
- Verify constant work after Stage D1, even with thousands of RF records or equivalent control events; do not reread nested source RF events or members.
- Verify closed eight-source-field assumptions, frozen records, exact 10 D2 fields and no `rf_effective`, `HealthVerdict.PASS`, `ControlVerdict.ADMITTED`, accepted timestamp, post-state, ARM, output, mixer, trace or hardware imports.
- Verify `TRUST_NOT_PROVEN` always present and last in the exact internal reason ordering. Internal labels are **not** new R1 E_* codes.

## 4. Acceptance evidence and owner UAT (token-efficient)

Developer codes/debugs/test once as needed. Unit and real-pipeline oracle tests must be fully runnable from the TASK-008 directory. Owner accepts via three Windows PowerShell commands (`pytest`, `smoke.py`, `pip check`) and one optional aggregate `scripts/verify.py` including independent read-only TASK-001…007 regressions, exact local wheel verification/build and machine-readable artifacts. Historic previous suite counts are references, NOT presumed PASS.

Developer MUST NOT rerun the entire suite solely to create verbose PR handoff after owner UAT if no execution-affecting files/dependencies changed. Instead record the immutable source/test/config/hash inventory and actual UAT results, and use JUnit to verify 36 case IDs. If execution-affecting material changed, rerun relevant tests and request owner reapproval. Retain historical failing attempts/warnings honestly.

SA review checks: source diff, frozen R1/R1.1 hierarchy, 36 P220 named JUnit cases, 18 negative families, 5/5 Design/Task release hashes, pinned dependency paths, no accidental authorization, report of TRUE PASS/FAIL/SKIP and limitations. No claim of full R1 FSM, trace, policy allowlist, committed-state owner, S1 output or hardware/flight certification.
