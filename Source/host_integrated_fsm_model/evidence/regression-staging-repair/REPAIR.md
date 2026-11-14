# Owner regression staging repair

Owner's original FULL UAT failed at TASK010 N18: 1 failed, 386 passed.
The original log and JUnit remain in `../owner/task010-regression.log` and
`../owner/task010-regression.xml`; `../owner/summary.json` remains FAIL until
Owner performs a successful new run. The next Owner run archives the failure.

TASK013 copied TASK001 `evidence/baseline.json` from its Git blob into the
isolated regression workspace. Prior TASK004–012 provenance records instead
explicitly pin preserved working bytes. Those bytes include a different `head`
field and CRLF. The fix copies that one evidence file only after verifying both
TASK013's expected SHA-256 and every inherited consumer's expected SHA-256.

| Source | SHA-256 |
|---|---|
| Git blob, incorrect for the preserved-evidence check | `da3806957bc2738c08cb2c6b4f4b484ac8ba517a603a0756cd20a47c0f61fbfa` |
| Preserved worktree, explicitly pinned by existing records | `e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d` |

Changes affecting execution/testing: `scripts/verify.py` and new
`tests/test_verification.py` only. No FSM/JCS/viewer/dependency changes, no prior
module or normative/release edits, and no disabled or modified provenance
assertion. Every staging write targets TASK013's isolated cache workspace.

Actually rerun by Developer in the corrected isolated Owner workspace:

- TASK010 `test_N18_installed_local_prerequisite_and_release_provenance`:
  **1 PASS**, exit 0. See `task010.log` and `task010.xml`.
- TASK011 `test_N18_installed_baseline_and_release_hashes`:
  **1 PASS**, exit 0. See `task011.log` and `task011.xml`.
- New tests check the real Git-versus-preserved mismatch, source immutability,
  rejection of changed source bytes and rejection of inconsistent consumer pins.

The targeted-run `summary.json` retains its run-time revision. Subsequent edits
before final DEV CHECK only clarified comments and renamed the new test; the
staging logic exercised by those two inherited tests did not change.
Final TASK013 DEV CHECK results and current fingerprint are in
`../dev/summary.json`. No complete prior-task suite was rerun by Developer.

Owner should run `.venv\Scripts\python.exe scripts\verify.py --owner` again from
`Source/host_integrated_fsm_model`. Targeted PASS does not constitute OWNER FULL
UAT acceptance. No PR created.
