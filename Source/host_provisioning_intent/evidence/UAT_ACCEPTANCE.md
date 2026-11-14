# TASK-011 — Owner UAT acceptance and PR handoff

The Owner explicitly confirmed TASK-011 UAT PASS and authorized a pull request
from `feature/TASK-011-host-provisioning-intent` into `main` in the conversation.
This accepts TEST_ONLY intent inspection; it grants no actual provisioning,
runtime, ARM, FSM or output authority. Developer must not merge the PR.

- Frozen baseline: `7872c415c73146e33a5596b010320f76596588cb`.
- Accepted execution fingerprint (SHA-256):
  `59af85857699a65a80afdbfc997cdda4d25f1b7e787d7d704fc94af15ba851f0`.
- Unit/integration: **392 PASS**; **48/48 P223**; **18/18 negative families**.
- TASK-001 through TASK-010 regressions: **2,111 PASS**.
- Development and installed-wheel smoke: **48 PASS, 0 FAIL** each.
- Build, install, pip check and full verification: **PASS**, recorded commands exit 0.
- Provenance: **424 pinned files + 5 manifest-listed release artifacts + policy MATCH**;
  the release manifest itself is separately SHA-256-pinned in `baseline.json`.

PR preparation compares current code/test/script/configuration hashes with
`summary.json`, installed dependency versions with the accepted environment,
installed prerequisite source bytes with frozen Git, and built artifact hashes
with `environment.json`. No execution-affecting change is part of this handoff;
full regression is not rerun for PR packaging. This acceptance note is the only
post-UAT addition to the task subtree.

Scope is `Source/host_provisioning_intent/**` and the six immutable release files:
Design/184, Design/185, Design/186, the P223 oracle index, the P223 release manifest
and TASK-011. Release contents/hashes are preserved. The pre-existing local edit
to TASK-001 `evidence/baseline.json` remains outside the PR and is not overwritten.

Evidence: [summary.json](summary.json) (AC-01 through AC-10 and coverage),
[tests.xml](tests.xml), [commands.json](commands.json),
[environment.json](environment.json), [baseline.json](baseline.json), development
JUnit and per-command logs. The historical pending-UAT entry in `summary.json`
describes verification time; this acceptance note supersedes that handoff status
without rewriting the original evidence.

Limits: synthetic TEST_ONLY artifact consistency is not authenticated executable
identity or protected provisioning. No real signer/key, allowlist, runtime
permission, ARM, FSM, journal/trace publication or output is created. Full R1
runtime, hardware and flight are NOT RUN; actual OS timezone switching was NOT
RUN on Windows without `tzset`.

Owner workflow decision effective from TASK-012: Developer runs DEV CHECK only;
Owner directly runs OWNER FULL UAT, including all regression. Preserve evidence
and never mark an unexecuted check PASS. This prospective rule does not change
the historical TASK-011 checks or its accepted implementation.
