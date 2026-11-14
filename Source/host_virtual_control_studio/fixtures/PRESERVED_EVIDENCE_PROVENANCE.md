# TASK001 preserved evidence fixture — not runtime authority

Source: actual Owner-preserved working bytes at
`Source/host_preflight_m0/evidence/baseline.json`, inspected before TASK014 code.
Design/196 explicitly authorizes this task-local evidence-only copy.

Exact SHA-256:
`e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d`.
No normalization, redaction, regenerated JSON or newline conversion was used.
The file contains only baseline/head Git IDs, relative Design/Task paths,
SHA-1/SHA-256 values and result labels. No secrets, personal identities,
absolute local paths or credential material were found.

The historic Git blob differs (updated `head` and CRLF working bytes are pinned
by the old provenance records). TASK014 does not edit that old file. Verification
always reads this immutable fixture, verifies SHA-256 and every inherited
consumer pin, then stages it only into an isolated local Git clone inside the
new task's cache. All historical assertions remain intact. Missing or different
fixture/consumer bytes fail verification. No external dirty worktree is needed.

This fixture is evidence, not a trusted allowlist, signed approval, real
executable identity, ARM credential or permission to publish output.
