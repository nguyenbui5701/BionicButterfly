# TASK-011 — HOST_PROVISIONING_INTENT (SafetySupervisor Stage E3)

| Attribute | Required value |
|---|---|
| Status | **OPEN — SA DESIGN RELEASED; OWNER TO INTEGRATE AND ASSIGN** |
| Baseline `main` | `7872c415c73146e33a5596b010320f76596588cb` (merged PR #10) |
| Scope | **G0-A1 PC_SIM_ONLY / TEST_ONLY**, offline provisioning **INTENT INSPECTION ONLY** |
| Developer write scope | **`Source/host_provisioning_intent/**` ONLY** |
| Suggested branch | `feature/TASK-011-host-provisioning-intent` |
| PR policy | After Owner final UAT PASS and explicit PR approval; Owner alone merges |

## Purpose

TASK-010 can compare an untrusted test host claim with a fixed reference, but cannot bind that claim to actual artifact bytes. TASK-011 implements a **strict offline proposal checker** tying a closed candidate provisioning manifest to frozen policy SHA and SHA-256 of two independent **synthetic TEST_ONLY engine/scheduler artifacts**. Correctly matched input returns `INTENT_CONSISTENT_UNPROVISIONED`, never runtime permission. This is a tangible preparation step for later authenticated provisioning, NOT actual allowlist install, binary attestation, signature verification, host identity proof, FSM, trace or output.

## Read, in order

1. `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`.
2. Approved Design/115, **/116**, /117, /118, /132, /134, /141 and frozen R1 policy/schema bytes; don't assume a filename `_CANDIDATE` means unapproved in current hierarchy.
3. `Design/182_G0A1_HOST_REFERENCE_BINDING_STAGE_E2_CONTRACT.md` and actual read-only TASK-001 + TASK-010 `validate_wire`, E2 API. TASK-009 may be read for understanding, must not be called by E3.
4. **New** `Design/184_TASK010_MERGE_CLOSEOUT_AND_TASK011_BASELINE.md`, `Design/185_G0A1_HOST_PROVISIONING_INTENT_STAGE_E3_CONTRACT.md`, `Design/186_TASK011_PROVISIONING_ORACLES_AND_SA_REVIEW.md`, `Design/fixtures/P223_HOST_PROVISIONING_INTENT_ORACLE_INDEX.json`, `Design/P223_TASK011_RELEASE_MANIFEST.json`.
5. Verify baseline `7872c415c73146e33a5596b010320f76596588cb`, all 14 frozen Git blob pins, policy SHA `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10` and 5/5 release-hash manifest entries **before coding**. If any mismatch, STOP — DESIGN CLARIFICATION; never edit frozen R1/Design or old Source to pass tests.

## Implementation and acceptance (AC-01…AC-10)

| AC | Observable criterion |
|---|---|
| AC-01 | New pip-installable `bb-host-provisioning-intent` 0.1.0; all writes only new task subtree; prior TASK-001…010/source/policy/Design unchanged. |
| AC-02 | Exact 9-field frozen `ProvisioningIntentAssessment` and closed enums; **permanent** no runtime authority with owner provision needed and full FSM needed. |
| AC-03 | Inspect 16-field strict TEST_ONLY canonical JSON manifest; duplicated, missing/unknown, reordered, whitespace, BOM, non-ASCII, NaN, malformed, oversized rejected without calling hash. |
| AC-04 | Compare exact raw R1 policy digest and declared hash to independently supplied policy bytes; changed policy never passes even if request digest matches modified bytes. |
| AC-05 | Bind engine/scheduler artifact digest to actual **synthetic** bytes; changing one post-manifest returns mismatch, but matching never authenticates actual binaries. |
| AC-06 | All upstream E2 rejection/mismatch short-circuits to `UPSTREAM_NOT_ELIGIBLE` before parsing/hashing E3 candidate; forged positive E2 cannot confer authority. |
| AC-07 | All **48 P223-T01…T48** through genuine TASK-001 → TASK-010 → TASK-011 (or explicit E2 reject cases) + all **18 negative families** with exact expected reason order. |
| AC-08 | Runtime pure bounded, immutable output, no file/network/OS/env/clock/RNG/signatures/secret storage/allowlist/publisher, no event rescan, no TASK-009 journal/mixer/device import. |
| AC-09 | Real tests and JUnit, dev/wheel smoke, build/install/dependency, read-only TASK-001…010 regression, policy/baseline/release provenance; report actual PASS/FAIL/ERROR/SKIP. |
| AC-10 | Owner receives `pytest`, `smoke.py`, `pip check`, `verify.py` UAT commands; after accepted UAT no expensive full retest for mere PR packaging unless execution-affecting bytes/deps change. |

## Mandatory implementation details

- Public pure `inspect_provisioning_intent(reference, intent_raw, policy_raw, engine_artifact, scheduler_artifact) -> ProvisioningIntentAssessment` as frozen Design/185.
- Use exact literal synthetic vectors and mutation rules from P223 fixture; do not improvise owner approval, actual engine/scheduler IDs, signature keys or unapproved output fields.
- Input validation and candidate parsing must return `MALFORMED_INTENT` for malformed raw request and error TypeError/ValueError for wrong Python argument type/size; mismatching canonical typed request gives `INTENT_MISMATCH`. All three result digests null on upstream/malformed branches.
- Test via real `validate_wire` and actual TASK-010 output; no E2 synthetic PASS/ADMITTED shortcut.
- Python >=3.11, pure stdlib plus pinned TASK-010 types; no `cryptography` signer, trusted key bundle, provisioning writer or actual binary attestation in TASK-011. Freeze task dependencies from local verified packages.
- Verify no secret/private keys, no runtime enabling API, no `approved=True` or physical interface.

## Developer/Owner UAT on Windows

From `Source/host_provisioning_intent` after Developer prepares `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
# Owner final full verification, once:
.\.venv\Scripts\python.exe scripts\verify.py
```

Developer runs targeted tests while coding; prepares compact logs/JUnit, exact implementation hash and 3 UAT commands. Owner signs off; only then authorizes PR creation. If execution code/tests/deps unchanged, do not rerun full regression solely for PR packaging; preserve historical failures honestly. Developer never merges, pushes others' branches or modifies Design/Task.

## Stop gates / future owner action

If asked to install real trust root, issue a signature/certificate, store a private key, approve real engine/scheduler binary, grant host runtime execution, create FSM/ARM/PASS/ADMITTED, write canonical R1 trace, open virtual/physical output or any servo/flight mode: **STOP — DESIGN CLARIFICATION**. Separate owner-reviewed architecture/provisioning threat model and security approvals required. Existing TASK-010 is reference-check only; this E3 artifact is candidate review only.

**Deliverable status at release: DESIGN ONLY / TASK-011 runtime NOT RUN. Physical/flight NO-GO.**
