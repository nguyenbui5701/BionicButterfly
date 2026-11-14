# TASK-013 — SA clarification accepted

Source: SA decision relayed and approved by Owner in the TASK-013 OWNER UAT
ACCEPTED / CREATE PR instruction. This records the decision; it does not amend
any frozen Design, R1/R1.1 contract, policy, fixture or prior module.

For an unresolved RF batch containing HEALTHY+UNKNOWN with no approved effective
RF ordering:

- Keep `MODEL_CONTRACT_BLOCKED`.
- Do not interpret the batch as HEALTHY or grant ARM/ACTIVE.
- Do not commit or display the unarbitrated tick.
- Do not return `MODEL_REPLAY_COMPLETE` for the blocked run.
- Keep `runtime_authorized=False`, `output_allowed=False`,
  `actual_virtual_output=None`, `physical_output=None`, and
  `control_trace_sha256=None`.

## Existing implementation review

No FSM change was required. In `model.py`, `_advance` rejects
`RFEvidenceKind.AMBIGUOUS_CURRENT`. `run_fsm_model` returns
`MODEL_CONTRACT_BLOCKED` from that exception before appending the candidate tick,
swapping the private model prior, or adding the public display row. Console and
HTML render only the acknowledged `model_ticks`. The blocked report has no
complete candidate digest and does not claim model replay completion.

Existing test
`test_N08_ambiguous_healthy_unknown_stops_without_inventing_rf_priority`
is recorded PASS in both `dev/tests.xml` and `owner/tests.xml`. It injects the
ambiguous batch at 110000us, asserts blocked tick 22, exactly 22 prior committed
rows, `MODEL_CONTRACT_BLOCKED`, and no candidate trace digest. Source review
confirms that the rejected tick never reaches the append/display barrier.

The verified executable/test/script/dependency fingerprint is
`09918fc67cb9d611a543b21ca099d1ba532d147f8442dd3bb3bf9dd6e0e66931`.
It matches the Owner-accepted run, including the regression staging repair.
No regression or FSM tests were rerun merely to package this PR.

This is an approved fail-closed MODEL_ONLY limitation, not a newly invented RF
precedence, runtime trust decision, full operational R1 FSM completion, or
permission for PWM, servo, hardware or flight control.
