import hashlib
import json
from pathlib import Path
import re
import subprocess

import pytest
from bb_host_integrated_fsm_model import run_fsm_model, ModelOutcome
from bb_host_integrated_fsm_model import model,viewer,trace
from scripts import demo,verify
from scripts.fixtures import inputs
from test_model import wire,run,event,sort


def test_N24_actual_viewer_js_playback_cannot_command_core(monkeypatch):
    args=inputs('nominal'); report=run_fsm_model(**args)
    raw=viewer.render_html(report).decode()
    rows=json.loads(re.search(r'<script type="application/json" id="model-data">(.*?)</script>',raw,re.S)[1])
    def no_core(*a,**k): raise AssertionError('Viewer must not invoke model')
    monkeypatch.setattr(model,'run_fsm_model',no_core)
    result=subprocess.run(['node','scripts/viewer_reference.js'],input=json.dumps(dict(rows=rows,script=viewer._JS)),
        capture_output=True,text=True,encoding='utf-8',check=True)
    assert json.loads(result.stdout)==dict(status='PASS',display_checks=7,external_calls=0,core_callbacks=0)
    assert run_fsm_model(**args)==report


@pytest.mark.parametrize('failure',['quota','replace','permission','short_write'])
def test_N17_offline_failures_preserve_prior_report(failure,monkeypatch,tmp_path):
    target=tmp_path/'report.html'; target.write_bytes(b'previous')
    raw=viewer.render_html(run_fsm_model(**inputs('nominal')))
    def fail(*a,**k): raise OSError('TEST_ONLY IO failure')
    if failure=='quota': monkeypatch.setattr(demo,'MAX_BYTES',1)
    elif failure=='replace': monkeypatch.setattr(demo.os,'replace',fail)
    elif failure=='permission': monkeypatch.setattr(demo.tempfile,'NamedTemporaryFile',fail)
    else:
        original=demo.tempfile.NamedTemporaryFile
        class Short:
            def __enter__(self):
                self.file=original(mode='wb',dir=tmp_path,delete=False);self.name=self.file.name;return self
            def write(self,data):return self.file.write(data[:-1])
            def __exit__(self,*a):self.file.close()
        monkeypatch.setattr(demo.tempfile,'NamedTemporaryFile',lambda **kw:Short())
    with pytest.raises((OSError,ValueError)):demo.write_offline(raw,target)
    assert target.read_bytes()==b'previous' and list(tmp_path.iterdir())==[target]


@pytest.mark.parametrize('path',[r'\\server\file.html','//server/file.html','COM1','file.html:stream','file.exe'])
def test_N24_no_device_network_or_executable_destination(path):
    with pytest.raises(ValueError):demo.write_offline(b'report',path)


def test_N17_cli_failure_no_success_or_complete_candidate(monkeypatch,tmp_path,capsys):
    monkeypatch.setattr(trace._ModelJournal,'_fault',lambda self,record:'BEFORE_APPEND' if record.get('tick_index')==29 else None)
    path=tmp_path/'test.model-candidate.jsonl'
    assert demo.main(['--case','nominal','--candidate',str(path)])==1
    assert not path.exists() and capsys.readouterr().out==''


@pytest.mark.parametrize('flap,steer,state,left,right,tags',[
    (0.05,0,'ARMED_IDLE',None,None,()),(0.050001,0,'ACTUATION_ACTIVE',50001,50001,()),
    (0.999999,0.000002,'ACTUATION_ACTIVE',999997,1000000,('RIGHT_HIGH',)),
    (1,-1,'ACTUATION_ACTIVE',1000000,0,('LEFT_HIGH',)),
    (0.1,0.5,'ACTUATION_ACTIVE',0,600000,('LEFT_LOW',))])
def test_N11_threshold_and_exact_m0_clipping(flap,steer,state,left,right,tags):
    args,data=wire(); body=event(data,'active1')['payload'];body['flap_demand']=flap;body['steering_demand']=steer
    row=run(args,data).model_ticks[29]
    assert row.model_state.value==state
    assert (row.model_effort_left_micro,row.model_effort_right_micro,row.model_clip_tags)==(left,right,tags)


@pytest.mark.parametrize('flap,steer,allowed',[(0.02,0.05,True),(0.020001,0,False),(0,-0.050001,False)])
def test_N11_edge_neutrality(flap,steer,allowed):
    args,data=wire(); body=event(data,'edge1')['payload'];body['flap_demand']=flap;body['steering_demand']=steer
    assert (run(args,data).model_ticks[8].model_state.value=='ARM_CHECK')==allowed


def test_N13_disarming_low_not_first_rearm_sample():
    args,data=wire();event(data,'active1')['payload']['arm_switch']=False
    row=run(args,data).model_ticks[29]
    assert row.model_state.value=='DISARMED' and row.model_snapshot.low_first_at_us is None


def test_N08_unknown_rf_cannot_refresh_control():
    args,data=wire();event(data,'lost')['payload']['rf_health']='UNKNOWN'
    data['events'].append(dict(event(data,'active1'),event_id='control-with-unknown',event_at_us=155000))
    sort(data); row=run(args,data).model_ticks[31]
    assert row.model_state.value=='CONTINGENCY' and row.model_snapshot.control_at_us==145000


def test_N19_candidate_no_authority_flags_cannot_be_initialized():
    with pytest.raises(TypeError):trace.R1TraceCandidateTick(0,0,'BOOT','SELF_TEST','UNKNOWN',None,(),(),output_allowed=True)


def test_N20_owner_regressions_are_not_scheduled_by_dev():
    assert verify.regression_targets(False)==()
    assert [i for i,_ in verify.regression_targets(True)]==list(range(1,13))
    assert verify.regression_targets(True)[-1][1][0]=='host_integrated_shadow_replay'


def test_N17_genuine_f0_append_failure_blocks_model(monkeypatch):
    from bb_host_snapshot_commit_gate import TestOnlyAtomicJournal as Journal
    def failed(self,raw): raise OSError('TEST_ONLY F0 journal failure')
    monkeypatch.setattr(Journal,'_append',failed)
    report=run_fsm_model(**inputs('nominal'))
    assert report.outcome is ModelOutcome.MODEL_EVIDENCE_INCOMPLETE
    assert report.model_ticks==() and report.candidate_trace==b''
    assert report.shadow_comparator_outcome=='SHADOW_EVIDENCE_INCOMPLETE'


@pytest.mark.parametrize('high,prior_low_qualified,expected',[
    (True,True,'DISARMED'),(False,True,'CONTINGENCY'),(True,False,'CONTINGENCY')])
def test_N15_low_then_ack_then_high_priority(high,prior_low_qualified,expected):
    # Frozen Design/115 priority 5 > 6 > 7. ACK consumes prior qualification;
    # a simultaneous HIGH cannot rearm or take priority over that recovery.
    args,data=wire()
    if not prior_low_qualified:
        data['events']=[e for e in data['events'] if e['event_id']!='recovery-low2']
    source=event(data,'active1' if high else 'recovery-low1')
    data['events'].append(dict(source,event_id='control-with-ack',event_at_us=190000))
    sort(data); row=run(args,data).model_ticks[38]
    assert row.model_state.value==expected
    assert ('R_ACK_ACCEPTED' in row.model_reasons)==(expected=='DISARMED')
    assert row.model_effort_left_micro is None and row.runtime_authorized is False
    if expected=='DISARMED':
        assert row.model_snapshot.low_first_at_us is None
        assert row.model_snapshot.high_edge_at_us is None


def test_N08_ambiguous_healthy_unknown_stops_without_inventing_rf_priority():
    args,data=wire()
    data['events'].append(dict(event_id='ambiguous-rf',event_at_us=110000,
        type='SIM_RF_STATUS',payload=dict(rf_health='UNKNOWN',rf_provenance='INJECTED_SIM')))
    sort(data); report=run(args,data)
    assert report.outcome is ModelOutcome.MODEL_CONTRACT_BLOCKED
    assert report.blocked_at_tick==22 and report.model_tick_count==22
    assert report.candidate_trace_sha256 is None
    assert 'SA clarification required' in report.diagnostic
