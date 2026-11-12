# BionicButterfly — G0-A1 Replay, Trace and Output Commit Contract R1

- **Document ID:** BB-G0A1-TRACE-118 | **Revision:** R1 / 1.0
- **Supersedes PC-only conflicting proposals:** `59`, `69`, `80`, `87`, `94`, `103`, `110`.

## 1. Exact bytes: complete control trace

For an accepted run with a complete trace, canonical stream bytes are:

```text
JCS(header) + 0x0A
JCS(tick_0) + 0x0A
JCS(tick_1) + 0x0A
... exactly one decision per evaluated tick ...
JCS(terminal) + 0x0A
```

UTF-8 no BOM, RFC8785 JCS-compatible I-JSON object serialization, LF only, no blank line, no trailing spaces. Header includes `trace_format_version=1`, `result_contract_version=2`, `replay_identity`, scenario digest, policy digest, engine and scheduler revisions, step and scope. Tick records include index/original causal IDs/`eval_at_us`/pre/post-state/RF/effective frame age/reasons/output gate and bounded or null virtual pair. Terminal includes `COMPLETED` or `FAILED`, tick counts and stable fault codes. **Terminal excludes** self-hash, `execution_instance_id` and wall clock.

`control_trace_sha256 = SHA256(exact full stream)` is written **only** in an external complete report after terminal append acknowledgement. Do not hash the digest field itself. `partial_trace_sha256` may be included in a failure report *only* over provably committed bytes, never labeled a complete trace.

## 2. Replay identity and authorization separate

`scenario_digest = SHA256(JCS(validated scenario domain object))`; `policy_digest = SHA256(exact approved policy domain bytes)` as `116`. `replay_identity` is SHA256(JCS object with exactly: `domain="BIONICBUTTERFLY_G0A1_REPLAY_V1"`, scenario and policy digests, `engine_revision`, `scheduler_revision`, `result_contract_version=2`, `trace_format_version=1`). This identity specifies replay inputs+revisions, **not** a passing oracle.

Different wall times, invocation UUIDs, GUI colors or local file paths may modify **external human metadata only**, never normative trace bytes. Changing scheduler tick size or engine revision changes identity; identical traces across different schedulers are not required.

## 3. Transaction/failure ordering

At each tick: immutable pre-state -> full-batch normalize -> pure transition and mixer -> check trace quota -> serialize whole record -> acknowledge complete append -> then expose one virtual post-state/output. A trace write failure before publication must not leak a tentative active output through UI or alternate callback. This is an *observational virtual-output sequencing property*; no unproven crash-consistent `fsync`/storage guarantee or real servo guarantee is claimed.

- Preflight rejection: `VALIDATION_REJECTED`, zero core decisions, no fabricated terminal or full-trace digest.
- Complete successful trace: `COMPLETED`, full trace/digest; PASS requires independent oracle comparison.
- Runtime model failure with committed terminal: `FAILED`, report complete evidence if available; normal-success oracle not PASS.
- Serialization/append/quota/terminal failure: `FAILED_INCOMPLETE_EVIDENCE`, `control_trace_sha256=null`, no PASS of core-run success, **no uncommitted virtual output**.

## 4. Evidence and acceptance boundary

The G0-A1 test harness must compare both **expected transitions/reasons/virtual outputs** and replay bytes across identical contract/policy/schedule runs. A digest match alone does not show expected control behavior. A preflight-rejection test may PASS as an oracle even though `run_status=VALIDATION_REJECTED`; it is not a core-execution PASS.

A scenario may never choose an actuator adapter, UART/PWM driver, executable plugin, physical RF binding, alternative policy allowlist or context. Host approval digest alone does not certify an executable or authorize flight.
