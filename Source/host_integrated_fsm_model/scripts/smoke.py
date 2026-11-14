"""Three genuine integrated model/trace/viewer cases, no old regression."""
from demo import inputs
from bb_host_integrated_fsm_model import run_fsm_model, ModelOutcome
from bb_host_integrated_fsm_model.viewer import render_console,render_html,BANNER


def main():
    failures=[]
    for case,count in (("nominal",71),("recovery",50),("conflict",9)):
        try:
            result=run_fsm_model(**inputs(case))
            assert result.outcome is ModelOutcome.MODEL_REPLAY_COMPLETE,result.diagnostic
            assert result.model_tick_count==count and result.runtime_authorized is False
            assert result.control_trace_sha256 is None and result.actual_virtual_output is None and result.physical_output is None
            assert BANNER in render_console(result) and BANNER.encode() in render_html(result)
            assert len(result.candidate_trace.splitlines())==count+2
            if case=="nominal":
                assert result.model_ticks[29].model_effort_left_micro==250000
                assert result.model_ticks[38].model_state.value=="DISARMED"
        except Exception as error:
            failures.append((case,repr(error)))
    for case,error in failures: print(case,error)
    print(f"Smoke: {3-len(failures)} PASS, {len(failures)} FAIL")
    return bool(failures)


if __name__=="__main__":
    raise SystemExit(main())
