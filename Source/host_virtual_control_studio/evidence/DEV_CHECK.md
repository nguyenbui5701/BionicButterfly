# TASK014 DEV CHECK — PASS

Actual final command: `.venv\Scripts\python.exe scripts\verify.py --dev`.
Machine result: [dev/summary.json](dev/summary.json); all actual invocations:
[dev/commands.json](dev/commands.json); final hash/scope audit:
[dev/final-audit.json](dev/final-audit.json).

- TASK014 unit/integration/headless controller: **111 PASS**, zero failed,
  errors or skipped. Includes **24/24 P226**, all N01–N24 negative families,
  exact 20ms/100ms/200ms boundaries, real F1 comparator and 10000-action case.
- Six additional fixture/schema checks from the fresh clone: **6 PASS**.
- Targeted historical provenance in the clean clone: TASK010 **1 PASS**,
  TASK011 **1 PASS**. Complete old suites were **NOT RUN** by Developer.
- Development and installed-wheel smoke: each **3 PASS, 0 FAIL**.
- CLI nominal: exit **0**, 40 ticks; rf-loss: exit **0**, 16 ticks; ambiguous:
  exit **2**, expected MODEL_CONTRACT_BLOCKED with 3 acknowledged ticks.
  Intentional blocked replay is not labeled MODEL_REPLAY_COMPLETE.
- Build/sdist/wheel/install/pip checks: exit 0. All 29 recorded commands matched
  expected exit codes; no warnings recorded in the final command logs.
- Programmatic **hidden real Tk widgets**: PASS for launch, nominal replay,
  effort at ACTIVE and blocked ambiguous recording. See
  [gui-adapter-smoke.json](gui-adapter-smoke.json). Manual GUI UAT **NOT RUN**.
- 39 baseline Git pins, 10 release artifact hashes, manifest, policy and preserved
  fixture MATCH. 1225 inherited Git blobs checked. No historical module edited;
  existing TASK001 working evidence is unchanged. All writes remain in TASK014.

Final execution/test/script/dependency/fixture fingerprint:
`887bc6fa96627b370c9c72db3c01966e3330d2f8cdae7d9f5aa216c0e7998e28`.

## Observable demo

Nominal: LOW samples 15000/35000us, HIGH edge 40000, confirmation 140000,
MODEL ACTIVE 145000 with L/R=250000/750000, S1 at 150000 without time refresh,
LOST→CONTINGENCY 155000, qualified ACK→DISARMED 190000. The GUI allows editing
these simulated inputs and replaying the whole scenario via the genuine F1 API.
Generated nominal HTML/proof/candidate and full console logs are in `dev/`.

rf-loss: early HIGH denied, RF LOST interrupts ARM_CHECK, UART-valid while LOST
does not refresh accepted control, INVALID cannot rearm, catastrophe persists
through RESET. Ambiguous: no row at 15000us, no complete candidate hash/export.

## Fresh-checkout evidence and review matrix

The clean local Git clone initially contains the committed TASK001 evidence
blob, not the modified Owner working copy. Staging reads only TASK014's immutable
fixture and verifies every consumer's existing pin before copying inside the
isolated clone. See [dev/fresh-clone.json](dev/fresh-clone.json). Missing or
wrong fixture and mismatched consumer expectations fail closed in tests.
Owner full regression has been prepared, not claimed as already executed.

| Acceptance | Evidence / status |
|---|---|
| AC01 scope | final-audit.json; old source and release bytes unchanged |
| AC02 pins | baseline.json, verification logs and final provenance MATCH |
| AC03 integrated CLI/Tk | three real demos + hidden widget smoke; manual GUI pending Owner |
| AC04 conversion | strict schema/parser negatives, exact numeric tokens and TASK001 acceptance |
| AC05 genuine F1 | direct comparator and one-F1-invocation large-session test |
| AC06 behavior | authored P226 expectations and nominal/rf-loss timelines |
| AC07 hazards/transaction | N12–N22; no unacknowledged row/export |
| AC08 authority | frozen deny-only boundary, N23 and every oracle |
| AC09 offline export | deterministic outputs, blocked export and file-write failure tests |
| AC10 test coverage | 24 named oracles, N01–N24, headless controller and fixture checks |
| AC11 clean clone | verified immutable fixture + targeted original provenance checks PASS |
| AC12 UAT split | DEV only new suite/two impacted tests; `--owner` schedules all 13 prior suites |

## Handoff and limitations

Owner: follow [README](../README.md), run `scripts/verify.py --owner` and the
visible GUI workflow in [GUI_UAT_CHECKLIST.md](GUI_UAT_CHECKLIST.md). Full
regression TASK001–013 and manual GUI acceptance remain **NOT RUN** here.

No unresolved development test failure remains. Initial test-label error and
generated-metadata fingerprint failure, including original logs, are preserved
in development JUnit and `dev/history/`; see DEVELOPMENT_NOTES.md.

The packaged offline toolchain targets Windows x64 CPython 3.11; Node on PATH is
needed for inherited TASK013 JCS tests, not the Studio runtime. MODEL_ONLY does
not provision trust, authorize ARM/output or establish physical safety.
runtime_authorized=False, actual_virtual_output=None, physical_output=None.
No PWM/servo/receiver/ESP32 HAL/flight, crash durability or SC-G1/HB-G0B approval
is implemented or claimed. No commit/push/PR was created for TASK014.
