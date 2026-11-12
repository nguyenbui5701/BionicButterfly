# BionicButterfly — Phase 2.1 G0-A1 Test Matrix & Coverage Obligations

- **ID:** BB-G0A-TEST-063 · **Rev:** 0.1 · **Date:** 2026-11-12
- **Status:** TEST SPECIFICATION / NOT RUN / NO TEST EVIDENCE
- **Baseline:** `52_DESIGN_VERIFICATION_AND_EVIDENCE_PLAN.md` has PC-A01–PC-A20. This file **does not replace** those IDs; it adds precise input and output behavior and coverage for `56–62`.

## 1. Regression crosswalk to preexisting G0-A test IDs

| Original test IDs | Main invariant | New contract / additional scenarios |
|---|---|---|
| PC-A01–04 | no autoarm; edge + qualification | `57–58`, `CFG-03`, `SEC-04` |
| PC-A05–06 | one owner; invalid source denied | `56–58`, `TH-08` |
| PC-A07–09 | separate RF/serial health; finite/schema | `57–59`, `SEC-02/05` |
| PC-A10–11 | bounded virtual L/R; invalid profile blocks | `57`, `60`, `CFG-02/03` |
| PC-A12–13 | armed config/OTA denied | `60–62`, `CFG-04/07`, `SEC-07/08` |
| PC-A14–15 | deterministic replay/clock partitioning | `59`, `TIME-01/02/08` |
| PC-A16 | no hardware/flight context in host | `56`, `60`, `SEC-01` |
| PC-A17–18 | lost link/fault priority/recovery | `58–59`, `TIME-07`, `SEC-04` |
| PC-A19–20 | unknown physical telemetry / no hover claim | `56–57`, `61`, UI view test |

**Consistency note:** PC-A14's “byte-identical normalized event trace” only applies after **canonical serialization** is specified; numeric equivalence for cross-engine simulations may instead use predeclared float tolerance (59). Do not claim both at once without a stable format.

## 2. New Phase 2.1 test cases (all NOT RUN)

| Test | Scenario | Required observation | Scope |
|---|---|---|---|
| `G1B-01` | valid JSON, fixed step, no arm events | BOOT→SELF_TEST→DISARMED and no motion | pure core |
| `G1B-02` | ARM HIGH at boot; no LOW seen | `E_ARM_EDGE_ABSENT`, never armed | FSM |
| `G1B-03` | valid LOW then HIGH, neutral/healthy; qualification window elapses | ARMED_IDLE **only if** declared guards; output inhibited until subsequent active demand | FSM |
| `G1B-04` | HIGH + nonneutral flap at ARM | arm denied; reason identifies neutral failure | FSM |
| `G1B-05` | RF health UNKNOWN but valid serial frames | block new arm, trace independent states | RF boundary |
| `G1B-06` | frames continue while RF status LOST | link-contingency only in simulator; no physical servo policy | FSM |
| `G1B-07` | two contradictory frames in same time batch | one typed conflict, no transient enabled output | scheduler |
| `G1B-08` | ARM + critical fault + config write same tick | fault dominates; no config mutation or arm | scheduler |
| `G1B-09` | different file/event presentation order with same event set | identical canonical states/reasons | scheduler |
| `G1B-10` | clock long pause and restart injection | no phantom new arm or hidden extra cycles | time |
| `G1B-11` | NaN/Infinity/duplicate keys in JSON | parse reject and zero virtual outputs | schema/security |
| `G1B-12` | huge event count, duration, queue and trace quotas | typed bounded failure, no crash or false PASS | resources |
| `G1B-13` | attempt flight context or hardware driver via scenario | rejected; composition contains no physical driver | isolation |
| `G1B-14` | invalid SIM_ONLY profile with physical servo range present | deny output; error and config digest | config |
| `G1B-15` | crash during disarmed **persistent** profile update (if storage is within approved G0-A1 scope) | old/new complete version only; no partial active config; otherwise test is DEFERRED and immutable in-memory config tested | config |
| `G1B-16` | post-fault link recovery with ARM high | remain unarmed; require separate low→high and ACK | recovery |
| `G1B-17` | exceed normalized output then saturation | finite bounded virtual output and explicit clip reason | planner/gate |
| `G1B-18` | telemetry when wing sensor absent | measured angle/lift/airborne null or UNKNOWN; no fabricated hover | reporting |
| `G1B-19` | same run/config with identical clock/seed repeated | canonical state/reason equal, numerical output within approved precision | reproducibility |
| `G1B-20` | failed trace append / disk full | result FAILED_INCOMPLETE_EVIDENCE; not PASS | evidence |
| `G1B-21` | UI attempts arbitrary actuator target, bypasses validator | rejected; cannot access virtual sink directly | API/security |
| `G1B-22` | wrong mapping/profile revision or unknown event type | explicit invalid mapping/schema; no arm | schema |
| `G1B-23` | duplicate same frame content with new event id | no duplicate arm edge or duplicated side effect | FSM |
| `G1B-24` | wrapped/backward time inside run | reject; reset requires new run or explicit reviewed reset semantics | time |

## 3. Gate acceptance categories

- **Document validation:** names, identifiers, complete required coverage, no contradictory scope and source references. These checks can be performed now on the *authored design package*; they are **not implementation tests**.
- **G0-A1 approval:** owner and SA review exact Git commit and settle `52` DF requirements, `49` CF conflicts within host scope; resolve the open SIM policy numbers, time precision and API semantics. This is a **design approval only**.
- **G1 test execution:** when a separately approved Developer task exists, run PC-A01–20 + G1B-01–24 and TIME/CFG/SEC tests where applicable. Each test must carry commit hash, scenario/config digests, expected/actual and result. There are **zero executed G1 tests today**.
- **G2/G3/G4:** board, power, servo, RF, physical force and real flight remain separate; no test here replaces those gates.

## 4. Evidence record, coverage and honesty

```json
{
  "test_id": "G1B-__",
  "status": "NOT_RUN",
  "code_commit": null,
  "design_baseline_commit": null,
  "scenario_digest": null,
  "sim_policy_digest": null,
  "actual_core_trace_digest": null,
  "expected_state_or_reason": null,
  "observed_state_or_reason": null,
  "numeric_tolerance_policy": null,
  "test_environment": "PC_SIM_ONLY",
  "reviewer": null,
  "blockers": []
}
```

**Coverage does not mean PASS.** For critical invariants use positive and negative examples; absence of a test run must remain NOT_RUN. Consider property-based and differential model checking once design is approved, but do not require a particular tool/library now.
