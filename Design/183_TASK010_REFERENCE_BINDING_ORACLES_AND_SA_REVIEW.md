# TASK-010 — Reference Host Binding Oracles and SA Code Review

- ID **BB-P222-183** · baseline `4c7c92524837c8c728d0f206e5ba4655f9513399` · TEST_ONLY diagnostic scope.
- Fixture: `Design/fixtures/P222_HOST_REFERENCE_ORACLE_INDEX.json` with **48 P222-T01…T48** and **18 mandatory negative test families**.
- **Status: ALL DESIGN-SPECIFIED ONLY; Developer runtime NOT RUN, no host allowlist provisioned.**

## 1. Test strategy: build on real TASK-001, never self-assert from fixture

Start with pinned `Design/fixtures/P210_MINIMAL_WIRE_V2.json` and approved schema `Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json`. Use real `bb_host_preflight_m0.validate_wire` on exact raw bytes for every case. Supply the policy raw bytes from frozen `Design/contracts/SIM_POLICY_22A_R1.canonical.json` as a separate TEST fixture, not from scenario; apply byte mutations to a copy for negative tests, preserving original file. Supply an independent *synthetic claim* as exact `ClaimedHostFingerprint`, with documented overrides from the P222 fixture. Assert actual returned preflight accepted/rejected type first, then E2 output. Never substitute manually built `AcceptedPreflight` for the **positive 48** cases; test forged wrappers separately in adversarial tests.

- Case `P222-T01`: perfect reference match yields `REFERENCE_MATCH_NO_AUTHORITY`, `reference_pin_match=True`, `runtime_authorized=False`, `requires_trusted_host_provisioning=True`, `requires_full_fsm=True`; reasons ALWAYS include `HOST_IDENTITY_NOT_ATTESTED` then `TRUST_NOT_PROVISIONED`.
- Cases `T02–T12`: eleven exact canonical-policy byte mutations; each must mismatch. Raw SHA must be calculated from actual bytes, not from reserialized JSON. Policy digest from Design/116 must match canonical base vector.
- Cases `T13–T23`: independently mismatch each of the 11 fingerprint fields (engine/scheduler/scope/owner/versions etc.), assert named reason; mismatch must never become authority.
- Cases `T24–T28`: combined policy and host field mismatch, exact deterministic order and no mistaken short-circuit to success.
- Cases `T29–T43`: 15 illegal wire-v2 mutations (approval keys, owner/sink/engine/scheduler injection, wrong context/provenance/version/clock, unknown event, BOOT/UTF-8/duplicate key). Preflight must reject before E2; E2 response is `UPSTREAM_REJECTED` and never hashes/dereferences further candidate.
- Cases `T44–T48`: rejected wire cannot be rescued by policy, good test fingerprint or mixed conditions; valid wire with hostile policy/claim remains mismatch.

The fixture `=sha256(...)` is a declarative assertion, **not** executable code: compare to `hashlib.sha256(actual_selected_policy_bytes).hexdigest()` explicitly. Assert exact eight immutable E2 fields, closed enum ordering, exact Python types and `runtime_authorized=False` in **every** case, not just T01.

## Exact recipe encoding (do not guess)

The machine fixture contains `policy_variant_mutations` and `wire_variant_mutations`. Their definitions are the deterministic raw-byte/test-fixture transformations required for every P222 case. A test must assert its mutation occurred and that real TASK-001 actually ACCEPTED the legal case or REJECTED the illegal one. Do not derive an expected result from the implementation under test. Preserve the original frozen policy file byte-for-byte.

For `REORDERED_KEYS`, reverse the root dictionary insertion order before JSON encoding; keeping the already-sorted input order would accidentally regenerate the same canonical bytes and invalidate this negative case. For `DUPLICATE_JSON_KEY`, insert a duplicate raw key in the JSON byte stream (normal `dict` construction cannot represent duplicates). For `UNKNOWN_EVENT`, keep the event structural shape legal so TASK-001 rejects due to the unsupported event type rather than a missing field.

## 2. Negative/injection and architecture checks

Implement **all 18 N01…N18** test families explicitly, with no unrun claims. Include false `approved=True` in accepted scenario wrappers, forged dataclass and callable wrapper, and false assertion that signature strings are an allowlist. Spoofed user-supplied host information must never grant permission. Test strict type failures and output stability. A large valid event batch must not be traversed again by E2; only TASK-001 does the event validation. In E2 runtime ban filesystem, network, subprocess, environment, clock, OS trust service, device, output, R1 journal/trace or task-009 ledger calls.

## 3. UAT evidence, review and gates

Developer codes/tests while implementing. Owner performs final `pytest`, `scripts/smoke.py`, `pip check`, and optional one full `scripts/verify.py` pass (build/wheel/regression TASK-001…009; no fabricated counts). Keep JUnit per P222 ID, summary source hashes, exact baseline policy hash, actual mismatched/rejected cases and fail/error/skip. Developer need not repeat full tests just to create PR **if** execution-affecting bytes/dependencies are unchanged after Owner UAT; otherwise rerun relevant checks and request reapproval.

SA review rejects any code path that produces operational host approval, full FSM, output, or a runtime allowlist silently. A passing reference comparison is **not** cryptographic host attestation and MUST NOT be used as real trust by a future task; separate approved provisioned allowlist and binary identity are prerequisites. PC_SIM_ONLY; hardware/flight tests remain NOT RUN.
