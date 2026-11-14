# TASK014 development record

- Before code: verified 39 baseline Git object IDs against merged PR13 baseline
  `0a0a49ba0bbd2a87a1771ef4ad09d0b2f55b4b09`; ten release artifact SHA-256/Git
  hashes, separate manifest and policy MATCH. The manifest SHA-256 is
  `7c964fef2bdb6b0437abbb9534f98488d9c73ccd17f35e21a754e64f303b38a3`.
- Inspected actual preserved TASK001 evidence and copied exact verified bytes
  into the explicitly approved task-local fixture. No historical source edited.
- First unit/integration run: 104 PASS, 1 FAIL because P226-T01 used the wrong
  expected TASK001 status string (`ACCEPTED` vs real `ACCEPTED_PREFLIGHT`). The
  test assertion was corrected against the public API; FSM/input behavior did
  not change. Original JUnit is `development.xml`; corrected run added fresh
  clone fixture checks and passed 111 tests (`development-corrected.xml`).
- Programmatic hidden Tk smoke created actual widgets and exercised nominal
  replay/ACTIVE effort and ambiguous blocking. See `gui-adapter-smoke.json`.
  This is not a manual GUI acceptance result; Owner must run that workflow.
- Full old TASK001–013 regression has NOT been run by Developer. Only impacted
  TASK010/011 provenance tests are scheduled in DEV CHECK from the isolated
  clean Git clone. Owner `--owner` schedules all thirteen old suites once.
- First DEV CHECK ran all tests/demos/build/wheel successfully, but its final
  fingerprint guard failed because it included generated `.egg-info/*.txt`
  metadata. Excluded only generated metadata; source/test/config/vendor/fixture
  bytes remain fingerprinted. The failed run is preserved in `dev/history/`.
  Batched equivalent Git tree and normalized-content hash checks to avoid
  thousands of Windows Git subprocess launches; pin assertions are unchanged.
