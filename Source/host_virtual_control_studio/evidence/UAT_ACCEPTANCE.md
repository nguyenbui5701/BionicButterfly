# TASK-014 Owner UAT acceptance

Owner explicitly accepted OWNER FULL UAT and GUI MANUAL UAT (6/6 PASS), reported SA acceptance of the GUI results, and authorized creating the TASK-014 pull request into main. This document records that confirmation; no merge is authorized.

## Accepted execution and evidence

- Baseline: `0a0a49ba0bbd2a87a1771ef4ad09d0b2f55b4b09`.
- Executable/test/script/dependency/fixture aggregate SHA-256: `887bc6fa96627b370c9c72db3c01966e3330d2f8cdae7d9f5aa216c0e7998e28`. Every file in `owner/summary.json` revision.files matches the current worktree and DEV CHECK revision.
- DEV CHECK: 111 tests PASS; P226 24/24; negative families N01-N24 PASS.
- OWNER FULL UAT: 111 tests PASS; TASK-001-013 regression 2,803 PASS; fresh-clone fixture tests 6 PASS. All recorded JUnit counts and 40 command exit codes were checked against the preserved logs; no test was rerun for PR preparation.
- Smoke: 3 PASS, 0 FAIL in development and installed wheel. Build/install/dependency checks PASS.
- Demo nominal and rf-loss: exit 0. Demo ambiguous: expected exit 2, MODEL_CONTRACT_BLOCKED; not successful replay.
- Actual run records: [owner summary](owner/summary.json), [owner commands](owner/commands.json), [DEV summary](dev/summary.json), [fresh-clone evidence](owner/fresh-clone.json).

## GUI Manual UAT

Owner reports 6/6 PASS and SA acceptance. The supplied [GUI screenshot](owner/gui/GUI.png) is retained byte-for-byte, SHA-256 `289c78277ffcdbefabfaf60a84c86d1b92aad5627a7d3c53a9021dd760c327bb`. It shows the offline studio, model timeline/effort, MODEL_ONLY banner and disabled runtime/output authority.

The screenshot supports the Owner's report; it does not independently establish every manual action. No individual results have been invented. The earlier GUI_UAT_CHECKLIST template and automated summary's GUI NOT RUN field remain unchanged: the automated runner did not execute manual UAT. This separate Owner acceptance supersedes their pending-manual status.

## Provenance and fresh-clone audit

39/39 baseline pins, 10/10 release artifacts, release manifest, policy and preserved fixture MATCH. Manifest SHA-256: `7c964fef2bdb6b0437abbb9534f98488d9c73ccd17f35e21a754e64f303b38a3`. Policy SHA-256: `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`. Preserved fixture SHA-256: `e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d`.

The recorded Owner run used an isolated clone at the baseline and the pinned TASK-014 fixture, not the dirty historical TASK-001 worktree. Read-only inspection of that clone confirmed the exact staged fixture and 132 unchanged historical Python source/test/script Git blobs. Existing provenance checks were executed by the Owner run and are not bypassed. The existing TASK-001 evidence change is excluded from this PR and left untouched.

## PR scope and limits

Only Source/host_virtual_control_studio/** and the 10 manifest-listed approved Design/Task release artifacts plus their manifest are included. Since accepted UAT, PR preparation adds only this acceptance record, the supplied screenshot and PR_VERIFICATION.json. Existing evidence, executable code, tests, scripts and dependencies remain unchanged; full regression was not repeated.

MODEL_ONLY remains mandatory: runtime_authorized=False, actual_virtual_output=None, physical_output=None. No authoritative ARM/output, runtime provisioning, PWM, receiver, servo or flight control. Ambiguous contracts remain blocked. No crash durability claim. Bundled offline test wheels target Windows CPython 3.11 x64.
