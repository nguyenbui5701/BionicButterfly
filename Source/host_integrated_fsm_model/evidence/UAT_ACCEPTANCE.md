# TASK-013 — OWNER FULL UAT ACCEPTED

Owner explicitly confirmed OWNER FULL UAT PASS and authorized a pull request
from `feature/TASK-013-integrated-fsm-model` into `main`. Owner alone decides
merge after review. This document records that confirmation, not a new test run
or an independent SA review approval.

## Accepted version and actual evidence

Baseline and test-time HEAD: `eb4dbc8830d864c9cfd5c4d94bf00180aa960b5d`.
The implementation was uncommitted when tested; the exact accepted files are
bound by `revision.files` in both summary files and the aggregate fingerprint:

`09918fc67cb9d611a543b21ca099d1ba532d147f8442dd3bb3bf9dd6e0e66931`.

- DEV CHECK: **189 PASS**, no failures/errors/skips; [dev/summary.json](dev/summary.json).
- OWNER FULL UAT: **189 TASK013 tests PASS**, **24/24 P225 PASS**, N01–N24 covered;
  [owner/summary.json](owner/summary.json).
- Owner regression TASK001–012: **2614 PASS**, no failures/errors/skips.
- Smoke development/installed wheel: each **3 PASS, 0 FAIL**.
- CLI `nominal`, `recovery`, `conflict`: each exit 0 with recorded timelines,
  offline HTML and explicitly non-operational candidate JSONL.
- Owner build/install/wheel/dependency checks exit 0. All **39** actual Owner
  commands exit 0; no warnings recorded. See [owner/commands.json](owner/commands.json).
- Provenance: **32/32** explicit baseline pins, **9/9** release artifact hashes,
  release manifest separately, **570** inherited pinned files and policy MATCH.

PR preparation compared current source, tests, scripts, vendored dependency and
build configuration bytes to Owner and DEV fingerprints. They are identical,
including the regression staging fix. Only acceptance/clarification/review
documentation is added after UAT; no execution-affecting change or full
regression rerun was necessary. Original final DEV/Owner evidence bytes, demos,
JUnit and execution logs are retained. Historical failures and earlier handoff
status remain as history; this acceptance supersedes their pending-UAT status.

## Scope and reviewer notes

The PR contains only `Source/host_integrated_fsm_model/**` and ten approved
Design/Task release files (nine manifest entries plus the manifest itself), all
with original release bytes/hashes. No TASK001–012 module or frozen R1/R1.1
contract is changed.

The existing out-of-scope working modification to
`Source/host_preflight_m0/evidence/baseline.json` is deliberately excluded from
the PR and left untouched. Its preserved bytes have SHA-256
`e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d`,
which prior approved provenance records require. That local prerequisite
contains an updated `head` field and CRLF; a fresh checkout's Git blob is not
the same evidence. TASK013's Owner staging verifies the preserved hash and all
consumer expectations before copying it only into the isolated TASK013 cache.
It never changes an old module or disables a provenance assertion.

SA's HEALTHY+UNKNOWN decision is recorded in
[SA_CLARIFICATION.md](SA_CLARIFICATION.md). The accepted implementation already
blocks unresolved batches before commit/display and never claims completion
for that blocked run. No FSM change was needed.

## MODEL_ONLY limits

All eight states and left/right M0 effort are counterfactual model diagnostics.
`runtime_authorized=False`, `output_allowed=False`, `actual_virtual_output=None`,
`physical_output=None`, and `control_trace_sha256=None` remain permanent.
Candidate JCS bytes/hash demonstrate format conformance only; the candidate
terminal is denied as operational execution. This is not a completed authorized
R1 runtime, trusted allowlist, physical output or flight qualification.

No PWM/servo/ESP32/hardware or flight control was implemented or tested. Offline
file replacement does not claim crash durability. G0-B remains unapproved;
actual Windows OS timezone switching and process peak memory were not measured.
