from bb_host_virtual_control_studio import run_studio_session, StudioController
try:
    from .fixtures import session, dependencies
except ImportError:
    from fixtures import session, dependencies


def main():
    for case,count,outcome in [('nominal',40,'MODEL_REPLAY_COMPLETE'),('rf-loss',16,'MODEL_REPLAY_COMPLETE'),('ambiguous',3,'MODEL_CONTRACT_BLOCKED')]:
        raw=session(case);r=run_studio_session(raw,**dependencies())
        assert r.outcome==outcome and len(r.model_ticks)==count
        assert r.boundary.runtime_authorized is False and r.boundary.physical_output is None
        c=StudioController();c.load(raw);assert c.run(**dependencies())==r
    print('Smoke: 3 PASS, 0 FAIL')


if __name__=='__main__':main()
