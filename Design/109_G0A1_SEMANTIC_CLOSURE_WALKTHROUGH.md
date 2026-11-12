# BionicButterfly — G0-A1 Safety Semantics Review & Closure Walkthrough

- **ID:** BB-P27-SEM-109 | **Rev:** 0.1 | **Status:** PROPOSED WALKTHROUGH / NOT NORMATIVE UNTIL OWNER APPROVES
- **Primary candidate:** `100`, `101`; inherited conflict history `58`, `68`, `84`, `93`, `95`.

## 1. One-tick causality model

At fixed `T=k×step_us`:

1. **PRE-SNAPSHOT** — snapshot is immutable, previous tick's state and LOW qualification frozen. No event callback may mutate an output.
2. **COLLECT** all eligible original-timestamped events and IDs; no rounding of event times; reject invalid scenario structure before run.
3. **NORMALIZE** all valid control bodies as a batch: same-tick semantically identical frames ⇒ one logical observation, preserving IDs; *different* valid bodies ⇒ conflict and no trusted LOW/HIGH/demand observation. A deliberately invalid in-band frame generates diagnostics and breaks the LOW qualification window; it cannot refresh accepted pilot input.
4. **HEALTH** compute effective RF state and age independently of UART frame age; conflicting RF HEALTHY vs LOST in a tick resolves LOST. Model simulated critical power/scheduler/catastrophic causes with independent typed source.
5. **DECIDE** one transition using pre-state and the complete hazard flags: catastrophe, already latched, current active hazard, contingency recovery rules, ordinary RESET, trusted disarm, qualified ACK, arm qualification, eligible demand/held intent. Priorities are *logical conditions*, not callback order.
6. **BOUND** compute one virtual command only if post-state ACTIVE and every guard remains qualified; otherwise both virtual efforts are **null** (not physical servo zero PWM).
7. **TRACE COMMIT** validate/serialize/append complete tick record and commit the decision before it becomes observer-visible. Failure is `FAILED_INCOMPLETE_EVIDENCE` and no new active output is exposed.

## 2. Collision table to approve (all are SIM_ONLY)

| Pre-state | Same-tick inputs | Proposed result | Output | Distinguishing point |
|---|---|---|---|---|
| ACTIVE | catastrophe + RESET + trusted LOW | `FAULT_LATCHED` | null | catastrophe first, not ordinary RESET |
| ACTIVE | RF LOST + RESET | `CONTINGENCY` | null | active hazard first |
| ACTIVE | two different valid LOW/HIGH bodies | `CONTINGENCY` | null | neither qualifies as accepted pilot LOW |
| DISARMED | two different valid LOW/HIGH bodies | `DISARMED` | null | no LOW qualification, conflict reason |
| DISARMED | duplicate equivalent LOW bodies in same tick | `DISARMED` | null | counts as ONE observation |
| ARM_CHECK | no frame, valid RF/fresh prior | `ARM_CHECK` | null | 100 ms elapse cannot confirm HIGH |
| ACTUATION_ACTIVE | no frame, dual freshness intact | `ACTUATION_ACTIVE` | bounded held virtual intent (S1) | no synthetic frame; ages advance |
| ACTUATION_ACTIVE | frame stale (strictly > timeout), RF fresh | `CONTINGENCY` | null | independent accepted-frame age |
| ACTUATION_ACTIVE | UART frame valid but RF LOST | `CONTINGENCY` | null | UART diagnostic time cannot refresh pilot authority |
| CONTINGENCY | valid LOW #2 + ACK same tick | `CONTINGENCY` | null | ACK uses **pre-snapshot** LOW qualification |
| CONTINGENCY | ACK next tick, eligible prior LOW and cause in allowlist, all health restored | `DISARMED` | null | consumes qualification; requires fresh LOW sequence before ARM |
| FAULT_LATCHED | RESET + ACK + healthy RF | `FAULT_LATCHED` | null | terminal for current run |
| SELF_TEST | RF UNKNOWN, policy/critical power okay | `DISARMED` | null | does not mean ready to arm |
| SELF_TEST | simulated critical power failure | `SELF_TEST` | null | power health prohibits passing self-test |

## 3. Important clarifications not to silently skip

- **Contingency LOW tracking:** while `CONTINGENCY`, *healthy, coherent* LOW observations can build the recovery LOW window, but state remains CONTINGENCY. The qualifying second LOW must commit in an earlier tick than ACK; RF restoration alone is not an ACK. RESET cannot substitute for ACK.
- **An interrupted LOW window:** invalid in-band control, HIGH, conflict, RF LOST/UNKNOWN/stale, wrong map/profile and critical power/scheduler event reset window. An empty tick does not create a new LOW observation, and does not erase the window if dual freshness remains valid.
- **Disarm when RF LOST:** a low bit from an unqualified receiver is not treated as trusted pilot LOW. The simulator goes to CONTINGENCY/inhibit from hazard, not to an independently certified DISARM by trusting a lost link. This is *logical* behavior and does not promise real flight response.
- **Active output at zero:** virtual effort `0` may be an authorized command; virtual output `null` means inhibited. Conflate neither with physical wing position or power-off angle.
- **SELF_TEST recovery:** critical power/scheduler hazards hold SELF_TEST (not a hardcoded max wait); catastrophic fault latches. Fresh RF is a *new ARM prerequisite*, not necessarily a condition to show DISARMED.

## 4. Edge timestamp boundaries and false confidence traps

- Original event timestamp comparison: `LOW@15,000us` and `LOW@35,000us` satisfy `20,000us` separation; `LOW@15,001us` and `LOW@35,000us` do not.
- `HIGH@40,000us` + `HIGH@140,000us` satisfy the proposed `100,000us` confirmation interval (if current RF and neutral all qualify). `HIGH@139,999us` evaluated at `140,000us` does **not** satisfy interval.
- Freshness `<=200,000us` still current; `>200,000us` stale. **Neither threshold is approved for actual RC hardware.**
- Two different valid control bodies in one tick conflict even if they were transmitted sequentially with different original timestamps within 5ms; this sacrifices sub-tick user-switch detail for deterministic batch policy. Owner may amend, but it requires a different policy revision and test oracle change.

## 5. Residual semantic questions before a design freeze

| Gap | Current candidate resolution | Must pin in signed contract? |
|---|---|---|
| Definition of `recoverable_voltage_warning` | only *noncritical* named virtual warning; critical power fault not automatically ACK-clearable | **YES**, exact enum plus source semantics |
| `SIM_ACK_FAULT` duplicate IDs | duplicate **global event ID** invalid scenario; equivalent distinct-ID ACKs in same tick count as one or are rejected by a declared event-specific cardinality rule | **YES**, choose deterministic policy; recommendation: equivalent distinct-ID ACKs count once |
| Secondary noncatastrophic fault while in CONTINGENCY | combine cause set, never clear with ACK until all current causes recovered and all are on allowlist | **YES** |
| Active load > scenario bounds | reject at preflight if static; runtime overrun fail closed with incomplete evidence | **YES** |
| Contradictory RF status within same tick while DISARMED | effective LOST, no arm, output null, log source IDs | already specified; owner still approves |

**SA recommendation:** resolve the first two precise enum/cardinality questions as part of policy/trace versioning, not as Developer choices. A reviewer should never need to infer safety from a filename or table order. All behavior here remains design-only until explicitly approved and tested under a separately authorized task.
