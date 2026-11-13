# G0-A1 — Stage E1 Snapshot Commit Barrier (TASK-009)

- ID BB-P221-179; **derived internal test harness**, not a new R1/R1.1 policy.
- Source main pin `e61f97e388662a48a13ccb6b308954436cbb87ec`, scope **PC_SIM_ONLY / TEST_ONLY LEDGER**.
- Authoritative R1 context: `Design/115` (prior snapshot + fault priority), `118` (one complete trace record before virtual publish), `116` (approved policy), `141` (frozen precedence), `134` (future full trace schema), `164/167/173/176` (partial evidence/provisional decisions).

## 1. What it is — and is not

Implement a **state-owning in-memory test ledger** with a strict `prepare → append full internal record → acknowledge append → replace snapshot` transaction. Expose **no virtual output or publish callback**, no real servo/mixer/RC hardware, no full trace hash or successful R1 trace claim. Internal journal bytes are **NOT** the R1 JCS header/tick/terminal trace. This stage proves sequencing and immutability on PC only, not crash-consistent fsync or operational host authorization.

The ledger may commit only **unambiguous negative/administrative changes** listed in §3. It may NOT mark a raw RF HEALTHY / current control candidate *accepted*, grant ARM, resolve a HIGH edge, claim S1 ACTIVE hold, clear CONTINGENCY by ACK, authorize SELF_TEST readiness, or write any positive held effort. `TASK-005 provisional_next_state`, TASK-006 proposals, TASK-007 labels and TASK-008 `POTENTIAL_S1_UNVERIFIED` are **not committed transition commands**. Healthy diagnostic labels and `TRUST_NOT_PROVEN` do not become credentials. This implementation is intentionally a **partial owner shell**, not the final state-authorizing FSM.

**Names:** use `TestOnlySnapshotLedger` and `TestOnlyAtomicJournal` explicitly. Do not expose a generic `CommittedStateOwner` class that could be mistaken for production-ready R1 authority.

## 2. Immutable data model

`OwnerSnapshot` is frozen/slotted with exactly **14 fields**:

```text
  generation: int                                # 0 for genesis; increases by one ONLY after acknowledged test append
  last_tick_index: int | None                    # None at genesis
  last_eval_at_us: int | None                    # None at genesis; always tick_index*5000
  state: SafetyState                             # R1 closed 8 values
  last_accepted_control_at_us: int | None        # historical only; never newly accepted by TASK-009
  last_uncontested_healthy_rf_at_us: int | None  # historical only; never newly accepted by TASK-009
  last_rf_status: RFStatus | None                 # historical only; never refreshed by TASK-009
  last_rf_original_at_us: int | None             # historical only; never refreshed by TASK-009
  low_first_original_at_us: int | None
  low_qualified_committed_eval_at_us: int | None
  high_edge_original_at_us: int | None
  high_edge_committed_eval_at_us: int | None
  held_micro_effort: tuple[int,int] | None        # always None in any E1 ledger commit
  recoverable_causes: tuple[str, ...]             # test-only historical causes; no new causes invented in E1
```

All temporal fields must be exact ints (`bool` invalid), original event times never rounded, all values `0<=timestamp<=last_eval_at_us`, state-qualified LOW/HIGH window consistency per Design/170 (DISARMED may hold LOW, ARM_CHECK may hold HIGH, other states have no arm window); `low_qualified_committed_eval_at_us`/`high_edge_committed_eval_at_us` must lie on a 5000µs grid. `(last_rf_status,last_rf_original_at_us)` are jointly present or absent; a prior HEALTHY status must pair with its accepted-healthy timestamp; LOST/UNKNOWN can coexist with an *older* accepted-healthy timestamp (never promote it). `recoverable_causes` is a closed immutable tuple of **previously recorded strings**; E1 may clear all causes only for a hard-reset/terminal-fault administrative transition, not manufacture, clear via ACK or apply a runtime allowlist. Do not interpret cause tuples as actual recoverability approval.

`genesis_snapshot()` produces generation=0, state=BOOT, every time/intent/window/cause empty. For non-genesis testing, a **private test fixture factory** may seed synthetic prior snapshots, clearly reported `TEST_ONLY`; no application-facing arbitrary restore, untrusted scenario source or external state selection is allowed.

`TestOnlyAtomicJournal` owns a private ordered list of **complete internal bytes**. `SnapshotCommitResult` is frozen/slotted with exactly five fields: `outcome` (enum `COMMITTED_TEST_ONLY|DEFERRED_NEEDS_FULL_FSM|FAILED_INCOMPLETE_EVIDENCE`), `tick_index`, `eval_at_us`, `snapshot_generation` (int or None), `requires_full_fsm=True`. It contains no `output_allowed`, micro-effort pair, trace SHA, acceptance token or `state_after` permission. To inspect a committed test snapshot, read the ledger's **test-only frozen snapshot view**, not a returned R1 state authorization.

## 3. Strictly permitted fail-closed state transitions

The ledger is a test-only owner, seeded with a coherent `OwnerSnapshot`. Every incoming tick must be the next consecutive tick after its last acknowledged tick, with TASK-003/004/005/007/008 genuine upstream records all agreeing on current index, timestamp and **prior** state. Only cases below are eligible for an E1 commit; all other cases **DEFER**, do not append or advance snapshot.

Decision priority:

A. Prior `FAULT_LATCHED` -> hold `FAULT_LATCHED` (never clear, even RESET/ACK/HEALTHY). No new accepted history.

B. Current catastrophe -> `FAULT_LATCHED`, clears LOW/HIGH/held intent; preserves historical RF/control observation timestamps for forensics only. E1 cannot invent a reason code or grant ACK recovery.

C. Prior `CONTINGENCY` -> hold `CONTINGENCY`, even ACK/RESET/HEALTHY; full approved ACK recovery is **deferred** rather than forbidden forever.

D. Prior `ARM_CHECK`, `ARMED_IDLE`, `ACTUATION_ACTIVE` + **explicit** invalid-control/valid-conflict/RF LOST/standalone UNKNOWN OR missing/expired **either** prior-committed RF/control timestamp -> `CONTINGENCY` (even simultaneous RESET); clear LOW/HIGH/held intent. Ambiguous HEALTHY+UNKNOWN is **not** an R1 effective-health choice; E1 must DEFER rather than silently hold ACTIVE or commit an invented priority. Prior FAULT_LATCHED and catastrophe still outrank this.

E. Ordinary RESET in `DISARMED` or `SELF_TEST` with no catastrophe -> `SELF_TEST`, clear LOW/HIGH/held intent and cause tuple. No same-tick control admission. A RESET from an armed state **without a proven hazard** is deferred pending full FSM health adjudication; do not force SELF_TEST from C1 provisional data.

F. Initial BOOT at T0 with approved normalized BOOT -> `SELF_TEST`; no positive state authority.

G. `DISARMED` with no RESET/catastrophe -> may commit `DISARMED` bookkeeping hold; do not modify accepted-control, accepted-RF, windows or intent even if a current LOW/HIGH appears. `SELF_TEST` with no RESET/catastrophe -> may commit `SELF_TEST` bookkeeping hold; readiness to DISARMED is deferred.

H. All others (including healthy ARMED_IDLE/ACTIVE/ARM_CHECK, `POTENTIAL_S1_UNVERIFIED`, ambiguous armed RF, ACK recovery and any positive window/intent update) -> `DEFERRED_NEEDS_FULL_FSM`, no journal append, no advancement. This is intentionally not a full R1-per-tick simulator and cannot PASS whole-run oracles. Tests must NEVER interpret a deferred armed tick as a successful run.

Whenever an E1 commit transitions **into** `SELF_TEST`, `CONTINGENCY` or `FAULT_LATCHED`, clear all four qualification window fields and `held_micro_effort`, leave previous accepted timestamp data unchanged. Never advance RF status in E1 based on fresh observational data, especially not current HEALTHY (future trusted arbiter needed). A negative RF observation recorded in the internal test journal may be used for a test but is not converted into a trusted prior effective status; thus the next operational decision MUST pass through a later full R1 arbiter.

## 4. Internal append-before-snapshot ordering

`commit_tick(observations, temporal, priority, health, triage)` on a `TestOnlySnapshotLedger`:

1. Require exact imported upstream types (including SafetyState/RFStatus), fixed field shape, 5000µs grid, matching tick and prior state, monotonic consecutive tick; validate snapshot historical invariants, C1 and D1/D2 consistency. Do not rerun raw wire, re-scan event groups or reinterpret health as PASS.
2. Compute allowed **test-only negative decision** and candidate snapshot in *local temporary memory*, without touching current ledger or publishing anything. If DEFER, return a result with no append and no advancement.
3. Serialize a **complete internal test record** using a closed ASCII-only stable format with fixed keys `format="BB_E1_TEST_JOURNAL_V1"`, `tick_index`, `eval_at_us`, `pre_state`, `next_test_state`, `decision_kind`; deterministic key order and `LF` terminator. A simple Python standard-library `json.dumps(sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)` is suitable **only for these known restricted ASCII fields**. Do **not** claim it is RFC8785 JCS for arbitrary R1 records.
4. Have the ledger itself call its **private fixed TEST_ONLY journal** to append a complete record. A short write, exception, quota rejection, or missing full-append acknowledgment **must** transition the *ledger's failure status* to `FAILED_INCOMPLETE_EVIDENCE` without replacing its previously committed snapshot or exposing any new virtual output. Even if unacknowledged bytes reached the in-memory journal, terminal failure is sticky; no retry of that tick or later ticks in the same ledger instance.
5. Only AFTER complete internal append acknowledgment, atomically swap the ledger snapshot for the next frozen one, increment `generation` and last tick, and return `COMMITTED_TEST_ONLY`. A journal receipt must not be accepted from a caller or scenario JSON; it is an internal append outcome, **not** an authentication credential or R1 trace append receipt.

The private test journal may support deterministic fault modes `NONE`, `FAIL_BEFORE_APPEND`, `SHORT_WRITE`, `FAIL_AFTER_WRITE_BEFORE_ACK`, `QUOTA_DENIED`, `SERIALIZATION_FAILED` in unit tests. Report that actual R1 JCS record writer, terminal trace/report SHA, fsync/crash consistency, engine allowlist and virtual-output publisher are **NOT IMPLEMENTED**; G0-B/G4 remains NO-GO.

## 5. Hard validation and prohibitions

- Only consecutive ticks; at T0 BOOT must be the sole wire event. Stage E1 currently only marks negative/admin transitions; it MUST NOT commit a positive frame/rf timestamp, a LOW/HIGH qualification, actual RF recovery, an accepted demand, an `ARMED_IDLE/ACTUATION_ACTIVE` transition, or any non-null effort.
- Reject untrusted caller-supplied journal receipt, arbitrary snapshot restores at production API, bool-as-int, original times >prior committed eval, disjoint RF status/timestamp pairs, non-grid qualified/edge timestamps, mutable causes/intents, conflicting state/window, stale cross-stage pre-state/index, replay of a previously appended tick, and any new `E_*`/`P_*` public runtime code.
- No callback, UI output, event handler, external network/FS, device, PWM/RC/servo, JSON approval overrides, full trace SHA, no background concurrency or execution plugin in Stage E1. E1 is not host trust and its test journal **must not be imported by physical controller code**.
- No automatic success classification of entire scenario. If deferred at any tick, report `DEFERRED_NEEDS_FULL_FSM`; if append fails, report `FAILED_INCOMPLETE_EVIDENCE` and no success. A successful internal append is **test-local only**, not a PASS of R1 full-system behavior.

**This Stage E1 ledger provides testable transaction and snapshot-ordering mechanics, not the final trusted committed-state owner.** A later task must implement separately trusted host policy provisioning, complete R1 full FSM, canonical control trace and append-before-virtual-publish gate.
