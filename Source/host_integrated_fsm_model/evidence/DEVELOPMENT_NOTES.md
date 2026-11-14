# TASK-013 development history

- Initial 24-oracle run failed because the new fixture adapter used the wrong
  P222 filename. Corrected only TASK-013 adapter to the existing frozen
  `P222_HOST_REFERENCE_ORACLE_INDEX.json`; rerun 24/24 PASS. Original failed
  JUnit is retained in `oracle-development.xml`, rerun in `oracle-development-2.xml`.
- A later system review added explicit stopping when the separate genuine F0
  comparator fails its append; no model row is emitted. Dedicated test PASS.
- General baseline provenance initially rejected TASK-012 bootstrap.log because
  Git auto-CRLF filtering differed from its deliberately preserved CRLF blob.
  TASK-013 provenance now checks raw Git bytes first, then Git's configured
  checkout normalization; all 32 explicit pins and nine release hashes remain
  raw-exact. No previous file was changed.
- No previous-task regression suite has been run by Developer for this task.
  Only OWNER FULL UAT may execute all twelve prior suites, from isolated baseline
  copies under TASK-013 to avoid old tests modifying prior evidence.
- Browser check: generated nominal HTML opened in local headless Edge, actual
  JavaScript rendered SELF_TEST, timestamps and effort diagnostics. Screenshot
  `dev/viewer-browser.png` and DOM/log `dev/viewer-browser.log` retain evidence.
  Independent Node DOM harness executes playback and attempts display edits;
  it provides no core callback or external API.
- Additional R1 priority review reproduced ACK+HIGH incorrectly remaining in
  CONTINGENCY after prior LOW qualification (`ack-high-development-failure.log`).
  Fixed model arbitration to apply LOW > ACK > HIGH as Design/115 requires.
  Added three real-pipeline simultaneous-input cases; their first run exposed
  two incorrect fixture ID references in the new tests, preserved in
  `ack-priority-development.xml`. Corrected IDs to the approved fixture names.
  Added explicit HEALTHY+UNKNOWN fail-closed contract coverage.
- DEV CHECK after the priority fix ran 186 tests successfully, including all
  24 P225 oracles and N01-N24. Build succeeded but setuptools warned about an
  unused `tests/*.json` sdist pattern. Removed that empty pattern (no test data
  files were omitted). The earlier logs are retained in `dev/history/`; final
  DEV CHECK verifies the cleaned packaging and the same model/test behavior.
- Owner FULL UAT stopped at TASK010's N18 provenance test (386 passed, 1 failed).
  TASK013 staged TASK001 baseline evidence using its Git blob, but TASK004-012
  explicitly pin preserved working bytes with an updated `head` field and CRLF.
  Git blob SHA-256: `da3806957bc2738c08cb2c6b4f4b484ac8ba517a603a0756cd20a47c0f61fbfa`.
  Required working SHA-256: `e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d`.
  Fixed staging only: verify the preserved pin and all inherited consumer pins,
  then copy those exact working bytes into TASK013's isolated regression tree.
  No original TASK001-012 file, pin or assertion was changed. Added staging
  integrity tests. Actual targeted TASK010 and TASK011 N18 reruns each PASS;
  see `regression-staging-repair/`. Owner's original FAIL logs remain under
  `owner/`. Developer did not rerun the complete prior regression suites.
