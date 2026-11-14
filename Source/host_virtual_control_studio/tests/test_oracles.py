"""24 authored P226 expectations through real Studio -> F1 -> upstream APIs."""
import json
from pathlib import Path
import pytest
from bb_host_preflight_m0 import validate_wire
from bb_host_integrated_fsm_model import run_fsm_model
from bb_host_virtual_control_studio import run_studio_session, StudioController
from bb_host_virtual_control_studio.studio import BANNER, EFFORT_LABEL
from scripts import fixtures, offline, verify


def denied(report):
    b = report.boundary
    assert b.runtime_authorized is False and b.output_allowed is False
    assert b.actual_virtual_output is None and b.physical_output is None and b.control_trace_sha256 is None
    assert b.requires_owner_provisioning is True
    if report.model:
        assert report.model.runtime_authorized is False and report.model.control_trace_sha256 is None
    for row in report.model_ticks:
        assert row.runtime_authorized is False and row.output_allowed is False
        assert row.actual_virtual_output is None and row.physical_output is None


@pytest.fixture(scope='module')
def reports():
    return {case:run_studio_session(fixtures.session(case), **fixtures.dependencies()) for case in fixtures.CASES}


@pytest.mark.parametrize('oracle',[f'P226-T{i:02}' for i in range(1,25)])
def test_p226_real_pipeline(oracle,reports,tmp_path):
    index=json.loads(fixtures.frozen_bytes('Design/fixtures/P226_STUDIO_ORACLE_INDEX.json'))
    item=next(x for x in index['items'] if x['id']==oracle)
    n=int(oracle[-2:]); report=reports.get(item['case'],reports['nominal'])
    for r in reports.values():denied(r)
    rows=report.model_ticks
    at=lambda us:rows[us//5000]
    if n==1:
        wire=json.loads(report.wire_v2)
        assert validate_wire(report.wire_v2,fixtures.dependencies()['frozen_wire_v2_schema']).status=='ACCEPTED_PREFLIGHT'
        assert len([e for e in wire['events'] if e['type']=='BOOT'])==1
        assert wire['events'][0]['event_at_us']==0
    elif n==2:assert at(15000).model_snapshot.low_qualified_eval_us is None
    elif n==3:assert at(35000).model_snapshot.low_qualified_eval_us==35000
    elif n==4:assert at(40000).model_state.value=='ARM_CHECK' and at(40000).model_snapshot.high_edge_at_us==40000
    elif n==5:assert at(140000).model_state.value=='ARMED_IDLE'
    elif n==6:assert (at(145000).model_state.value,at(145000).model_effort_left_micro,at(145000).model_effort_right_micro)==('ACTUATION_ACTIVE',250000,750000)
    elif n==7:
        assert at(150000).model_input_mode=='S1_HELD'
        assert at(150000).model_snapshot.control_at_us==145000
        assert (at(150000).model_effort_left_micro,at(150000).model_effort_right_micro)==(250000,750000)
    elif n==8:assert at(155000).model_state.value=='CONTINGENCY' and at(155000).model_effort_left_micro is None
    elif n==9:assert at(165000).model_snapshot.low_qualified_eval_us is None and at(185000).model_snapshot.low_qualified_eval_us==185000
    elif n==10:assert at(190000).model_state.value=='DISARMED'
    elif n==11:
        assert len(rows)==40 and [r.eval_at_us for r in rows]==list(range(0,200000,5000))
        assert all(list(r.causal_event_ids)==sorted(r.causal_event_ids) for r in rows)
    elif n==12:assert run_studio_session(fixtures.session('nominal'),**fixtures.dependencies())==report
    elif n==13:
        c=StudioController();c.load(fixtures.session('nominal'))
        assert c.run(**fixtures.dependencies())==report
        assert run_fsm_model(report.wire_v2,**fixtures.dependencies())==report.model
    elif n==14:
        assert BANNER in offline.console(report) and 'Dimensionless' in EFFORT_LABEL
        assert b'Not servo angles' in offline.html(report)
    elif n==15:assert at(10000).model_state.value=='DISARMED'
    elif n==16:assert at(45000).model_state.value=='CONTINGENCY' and at(45000).model_effort_left_micro is None
    elif n==17:assert at(50000).model_snapshot.control_at_us==40000
    elif n==18:assert at(60000).model_state.value=='CONTINGENCY' and 'E_FRAME_INVALID' in at(60000).model_reasons
    elif n==19:assert all(r.model_state.value=='FAULT_LATCHED' for r in rows[13:])
    elif n==20:
        proof=json.loads(offline.proof(report))
        ticks=[json.loads(line) for line in report.model.candidate_trace.splitlines() if json.loads(line)['record_type']=='tick']
        assert len(proof['model_ticks'])==len(ticks)==16
        assert [r['tick_index'] for r in ticks]==list(range(16))
    elif n==21:assert report.outcome=='MODEL_CONTRACT_BLOCKED' and [r.eval_at_us for r in rows]==[0,5000,10000]
    elif n==22:assert report.outcome!='MODEL_REPLAY_COMPLETE' and report.model.candidate_trace_sha256 is None
    elif n==23:
        for r in reports.values():denied(r)
    elif n==24:
        raw=verify.preserved_fixture()
        assert len(raw)>0
        with pytest.raises((FileNotFoundError,ValueError)):verify.preserved_fixture(tmp_path/'absent.json')
        wrong=tmp_path/'wrong.json';wrong.write_bytes(b'{}')
        with pytest.raises(ValueError):verify.preserved_fixture(wrong)
