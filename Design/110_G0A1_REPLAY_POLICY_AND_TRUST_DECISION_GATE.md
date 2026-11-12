# BionicButterfly — Replay, SIM Policy & Trust Decision Gate

- **ID:** BB-P27-TRACE-110 | **Rev:** 0.1 | **Status:** PROPOSED CONTRACT CONFIRMATION
- **Candidate sources:** `69`, `70`, `80`, `87`, `94`, `102`, `103`; external standard considered: RFC 8785 (JCS), https://www.rfc-editor.org/rfc/rfc8785.

## 1. Three identities must never be conflated

| Identity | Input bytes | Stable across identical replay? | Trust role |
|---|---|---|---|
| `scenario_digest` | JCS validated **scenario domain object** | yes | contents identity, not signature |
| `policy_digest` | JCS versioned exact **policy domain object** | yes | authorization lookup key only; caller may not approve its own digest |
| `replay_identity` | JCS domain/version + scenario/policy digest + engine/scheduler/result/trace version | yes | records what is being replayed |
| `control_trace_sha256` | exact complete normative UTF-8 JSONL bytes | yes if engine/inputs deterministic | evidence integrity, not itself an oracle PASS |
| `execution_instance_id` | external invocation metadata | no | nonnormative audit metadata; excluded from control trace |

A candidate tuple identical across runs does not imply identical control bytes unless the engine obeys the contract; tests must compare expected state/transitions and can also compare hashes.

## 2. Exact terminal/digest convention proposal

Normative stream consists of exactly: `JCS(header) + LF`, then one `JCS(decision_i)+LF` per evaluated tick, then `JCS(terminal)+LF` once at end. `terminal` **must NOT contain** `control_trace_sha256` or wall-time UUID. The external report, generated after terminal append success, contains full-stream `SHA-256`; it may also contain volatile invocation metadata, outside normative digest. No UTF-8 BOM, CRLF, hidden spaces, or unordered reason codes.

**Failure taxonomy:**

- Preflight invalid scenario/trust: `VALIDATION_REJECTED`, no virtual core ticks, no fabricated complete control-trace digest.
- Expected in-band simulated fault with complete recorded trace: run can be `COMPLETED`, and a fault-oracle can PASS if all expected transitions match.
- Runtime exception/explicit modeled failure with complete terminal: `FAILED`, and normal-completion oracle cannot PASS.
- Quota/append/serialization/partial evidence: `FAILED_INCOMPLETE_EVIDENCE`, `control_trace_sha256=null`, no PASS for core run; possible separate `partial_trace_sha256` only for demonstrably committed bytes.
- A source `approved_for_host_execution:true` flag inside a scenario or copied sample is **not an authorization**.

## 3. Independently approved SIM policy requirement

Policy candidate `SIM_POLICY_CANDIDATE_22A` in `102`: 5ms tick; 20ms LOW observations; 100ms HIGH confirmation; 200ms independent frame/RF freshness; numeric values apply only to host simulation. Never copy as hardware flight limits. An independent owner-controlled approval record must bind:

`reviewed_design_git_sha`, `selected_contract_revision`, `policy_canonical_sha256`, `policy_format_rev`, `allowed_engine_contract_rev`, `scope=PC_SIM_ONLY`, explicit `APPROVED` decision and trusted immutable provenance. Approval is not achieved by setting a boolean in input JSON, writing a purported SHA in README, or publishing ZIP.

Candidate approval signing workflow is a **governance procedure**: owner first accepts exact policy bytes/domain schema and normative doc revision; SA then computes reference digest and adds a reviewed record; later Developer only implements exact accepted version. Current owner status is **PENDING**; no deployable host allowlist exists.

## 4. Open wire-format and implementation-policy choices to be declared

| Item | Preferred SA option | Consequence if altered |
|---|---|---|
| Scenario input schema | strict v1, unknown fields rejected unless schema explicitly permits | changes to v1 need explicit version increment |
| Result/error contract | separate v2 with typed distinct `E_DUPLICATE_EVENT_ID`, `E_CONTROL_BATCH_CONFLICT`, `E_FRAME_INVALID` | callers/test oracles must know exact result schema |
| JCS serial encoding | RFC 8785 compliant I-JSON values, UTF-8 LF, no duplicate JSON keys | different JSON print formatting cannot be considered same trace |
| Tick timestamp | signed/unsigned bounds checked integer microseconds, never float age calculation | changes boundary tests |
| Observation/commit failure | no tentative virtual output, typed failed evidence | a loose streaming logger would violate safety contract |
| Canonical `causal_event_ids` | unique, sorted as typed schema defines (not input order) | changes trace hashes and replay equality |
| Policy digest contents | exact approved typed policy object only, excludes approval prose/timestamps | recompute digest if policy schema changes |
| Terminal evidence | no nested/self SHA, one committed terminal | avoids circular hashing |

## 5. Invariants suitable for implementation review, not yet implemented

`∀ tick: visible_output != null ⇒ committed_trace_decision && state==ACTUATION_ACTIVE && frame_fresh && rf_healthy && approved_host_policy`. `∀ run: complete_control_trace_sha256 != null ⇒ terminal_committed && all_required_tick_decisions_committed`. A failed append must not let a GUI, callback or alternate sink reveal a transient active command. These are **acceptance properties**, not currently tested facts.

**SA gate:** no final owner signature or final policy digest is created by this file. User acceptance of the exact approved contract is a separate explicit decision.
