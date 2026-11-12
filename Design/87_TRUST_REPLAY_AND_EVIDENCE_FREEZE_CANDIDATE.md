# BionicButterfly — Phase 2.4 Trust Boundary, Replay & Evidence Contract

- **ID:** BB-P24-AUDIT-087 · **Version:** 0.1 · **Status:** PROPOSED / HOST-ONLY.
- **Sources:** `61`, `69–70`, `78`, `80`, `84–86`, RFC 8785 (JCS), SHA-256.

## 1. Trust boundary / authorization is *not* scenario input

The scenario JSON, its own approval flags, its filename, any in-input `policy_id`, or a UI status flag cannot authorize itself. Before any virtual execution the **host composition** must receive a trusted, immutable, independently provisioned (outside scenario) `policy_digest` allowlist tied to a reviewed owner decision and exact G0-A1 baseline. A plain hash identifies bytes but cannot authenticate the author of the decision. Trusted approval record must be established by the owning application or authorized reviewed build, not by user scenario text.

Approval check order: (a) input bytes/limits/syntax/schema; (b) disallow hardware contexts/extra fields; (c) load approved policy snapshot by digest from trusted source; (d) digest/canonicalization match, version/profile/revision checks; (e) initialize deterministic virtual sink. Any failure before (e) rejects the run with zero enabled virtual outputs. A scenario can **request** a known approved policy ID but never mutate an allowlist, switch sink type, load a physical driver, or set execution privileges.

No claim of connected-device access is made: G0-A1 architectural dependency graph excludes serial/GPIO, Wi-Fi, real-time PWM, USB, receiver pairing, camera and IMU libraries. A host test must verify that physical interfaces are absent from the dependency graph and callable services, not merely disabled by a UI checkbox.

## 2. Replay identity versus execution identity

- `scenario_digest = SHA256(JCS(scenario_v1))` after validated I-JSON-compatible restrictions; keep canonical algorithm and version pinned.
- `policy_digest = SHA256(JCS(approved_immutable_policy))`, independently bound to an authorization record; no policy mutates within a run.
- `replay_identity = SHA256(version-tagged length-prefixed canonical tuple of scenario_digest, policy_digest, result_contract_version, exact engine_rev and scheduler_contract_rev/step_us)`. Use length prefixes or a single canonical structured encoding with explicit schema; never concatenate ambiguous raw strings.
- `execution_instance_id` identifies a particular invocation; may differ across repeats and is **outside normative trace**. Wall timestamps, machine paths, UI presentation, camera artwork/frames are nonnormative and cannot affect canonical decision digest.
- `control_trace_sha256` hashes complete, canonical `JSONL` event stream: one JCS object per line plus exactly one LF byte `0x0A`, ordered by evaluation tick, with agreed header/decision/terminal types, stable arrays and integer micro-effort. If a trace cannot finish, report no **complete** control trace SHA, optionally a separately labeled `partial_trace_sha256`.

**JCS caveat:** `json.dumps(sort_keys=True)` alone is not sufficient; duplicate keys in input are rejected rather than silently last-wins; correct Unicode/string escaping and numeric form are tested. Any NaN/Infinity is an input error. Client-side visualization artifacts may have separate digests and never count as control evidence.

## 3. Terminal lifecycle

| Run condition | `run_status` | `evidence_complete` | `assertion_result` interpretation |
|---|---|---|---|
| validation/authorization rejection | `VALIDATION_REJECTED` | no control trace | cannot claim completed core test |
| all expected events evaluated and trace fully committed | `COMPLETED` | true | PASS only if predeclared oracle matched actual trace |
| core unexpected failure | `FAILED` | depends on trace | not PASS even if partial states looked correct |
| quota/sink/serialization failure after some ticks | `FAILED_INCOMPLETE_EVIDENCE` | false | never PASS; no complete digest |
| deliberate injected simulated fault | `COMPLETED` if fully traceable and expected | true | may PASS an *expected-fault test*, not flight readiness |

Partial-trace failure must inhibit further virtual outputs even if the last successfully logged tick was ACTIVE. State and failure record remain traceable if the logging subsystem can report it; do **not** fabricate missing entries. Exact host handling of a disk write that fails irrecoverably is a typed execution failure, not an asserted safe physical shutdown.

## 4. Security and misuse examples

| Threat | Expected response |
|---|---|
| `approved_for_host_execution=true` injected into input | never authorizes; rejection if no independently trusted policy |
| policy bytes changed but same declared `policy_id` | mismatch digest → reject before core |
| malformed JSON or duplicate keys | schema/parser error, no actuation |
| filename with `../../`, URL or shell escapes | no arbitrary file/network execution; host APIs accept scenario **bytes** and bounded path handling is outside pure core |
| fake scenario event claims GPIO/FLIGHT | reject unknown event/context |
| internal UI invokes HAL/sets `output_allowed=true` | no accessible interface for direct sink control |
| input data includes personal identifiers | reject/non-collect as unnecessary; avoid leaking user data into public replay artifacts |

## 5. Change-control principle

All candidate semantics and numeric settings are **design-only** until owner signs exact `policy_digest`, associated file versions and scope. A later code implementation task, if approved, must pin this document/revision and test `P24-T01…T24`. No real hardware or free-flight assurance follows from replay correctness.
