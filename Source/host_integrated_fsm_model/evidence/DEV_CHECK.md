# TASK-013 DEV CHECK — PASS

Final command actually run: `.venv\Scripts\python.exe scripts\verify.py --dev`.
Machine-readable result: [dev/summary.json](dev/summary.json); exact commands,
exit codes and logs: [dev/commands.json](dev/commands.json).

- 189 unit/integration/conformance tests PASS; zero failures, errors or skips.
- 24/24 named P225 oracles PASS; all N01–N24 negative/boundary families covered.
- Independent JCS: RFC8785 vectors, 4120 Node/V8 numeric comparisons, Unicode,
  malformed I-JSON, frozen P210 bytes, candidate schema/order/identity checks.
- Dev smoke and installed-wheel smoke: each 3 PASS, 0 FAIL.
- CLI `nominal`, `recovery`, `conflict`: each exit 0, with console, offline HTML
  and explicitly labeled non-operational candidate JSONL saved under `dev/`.
- Build/sdist/wheel/install/dependency checks exit 0. All 27 recorded commands
  exit 0. Final build/test command logs contain no warnings.
- 32/32 explicit baseline pins, 570 inherited pinned files, 9/9 release hashes,
  release manifest and frozen policy MATCH. Prior Source modules unchanged;
  pre-existing TASK-001 baseline evidence edit preserved byte-for-byte.
- Stress: 60 seconds simulated, 20000 events, 12001 ticks; 46.933 seconds elapsed,
  38573986 bytes peak Python allocations, 5340591 candidate bytes. Process peak
  memory was not measured. See [dev/performance.json](dev/performance.json).
- Actual Edge offline rendering PASS; JS playback across seven selected ticks
  and attempted display mutation also tested. See `dev/viewer-browser.json`,
  `.log`, `.png` and `dev/tests.xml`.

Execution/test/script/dependency fingerprint:
`09918fc67cb9d611a543b21ca099d1ba532d147f8442dd3bb3bf9dd6e0e66931`.
The final audit matches the actual worktree to DEV CHECK:
[dev/final-audit.json](dev/final-audit.json).

## Observe the integrated model

Open [nominal viewer](dev/viewer-nominal.html) in a local browser. At 145ms:
MODEL ACTUATION_ACTIVE and mathematical effort 250000/750000. At 150ms S1 holds
without refreshing accepted timestamps; 155ms RF LOST enters CONTINGENCY;
190ms qualified ACK returns DISARMED; 335ms catastrophe latches permanently.
Recovery and conflict viewers are alongside it. Playback never calls the model.

## Owner handoff and limits

**TASK-001–012 full regression NOT RUN by Developer. OWNER FULL UAT NOT RUN.**
The prepared `scripts/verify.py --owner` executes those twelve suites once from
isolated baseline copies, then records Owner results under `evidence/owner/`.
Six PowerShell UAT commands are in [README](../README.md). Node on PATH is needed
for independent conformance tests; it is already available in this environment.

No unresolved test failure remains. Development failures and corrected reruns
are retained; see [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md) and `dev/history/`.
The ACK+HIGH priority bug was fixed against Design/115, without changing R1.

HEALTHY+UNKNOWN together has no approved effective-RF ordering in the inherited
contracts. That input stops with `MODEL_CONTRACT_BLOCKED` and requires SA
clarification; it is not assigned an invented RF priority. This is covered by
an explicit negative test and is not a positive P225 fixture transition.

All effort is MODEL_ONLY: runtime_authorized=False, output_allowed=False,
actual_virtual_output=None, physical_output=None, control_trace_sha256=None.
Candidate format conformance is not an operational R1 completion claim.
No hardware/servo/flight tests or actual OS timezone changes were performed.
G0-B worksheet remains unapproved. No commit, push or Pull Request was created.
