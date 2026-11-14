import ast
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
import json
from pathlib import Path
import sys
import pytest
from bb_host_integrated_fsm_model import run_fsm_model, trace
from bb_host_virtual_control_studio import *
from bb_host_virtual_control_studio import session as api
from scripts import fixtures, offline, studio, verify
from test_oracles import denied


def data(case='nominal'):return json.loads(fixtures.session(case))
def raw(d):return json.dumps(d,separators=(',',':')).encode()
def action(d,name):return next(a for a in d['actions'] if a['id']==name)
def run(d):
    r=run_studio_session(raw(d),**fixtures.dependencies());denied(r);return r
def reject(d):
    r=run(d);assert r.outcome=='SESSION_REJECTED' and r.model_ticks==() and r.model is None


@pytest.mark.parametrize('bad',[b'{"a":1,"a":2}',b'{"actions":[{"id":"a","id":"b"}]}'])
def test_N01_duplicate_json_keys(bad):
    assert run_studio_session(bad,**fixtures.dependencies()).outcome=='SESSION_REJECTED'

@pytest.mark.parametrize('key',['approved','sink','signature','runtime_authorized','clock','context','owner','plugin','policy_raw'])
def test_N02_unknown_authority_keys(key):
    d=data();d[key]=True;reject(d)
    with pytest.raises(TypeError):run_studio_session(fixtures.session('nominal'),**fixtures.dependencies(),**{key:True})

@pytest.mark.parametrize('field',['duration_us','at_us','flap_micro','steer_micro'])
@pytest.mark.parametrize('bad',[True,'2026-11-14',1.5])
def test_N03_noninteger_time_demands(field,bad):
    d=data();target=d if field=='duration_us' else action(d,'low1');target[field]=bad;reject(d)

@pytest.mark.parametrize('token',[b'NaN',b'Infinity',b'-Infinity',b'1e999'])
def test_N04_nonfinite(token):
    bad=fixtures.session('nominal').replace(b'195000',token)
    assert run_studio_session(bad,**fixtures.dependencies()).model_ticks==()

@pytest.mark.parametrize('bad',[b'\xef\xbb\xbf{}',b'\xff',b'{"x":"\\ud800"}',b'['*20+b'0'+b']'*20])
def test_N05_malformed_unicode_bom_depth(bad):
    assert run_studio_session(bad,**fixtures.dependencies()).outcome=='SESSION_REJECTED'

def test_N06_no_action_at_boot():
    d=data();d['actions'][0]['at_us']=0;reject(d)

def test_N07_ids_unique_and_no_boot_collision():
    d=data();d['actions'][1]['id']=d['actions'][0]['id'];reject(d)
    d=data();d['actions'][0]['id']='studio_boot';r=run(d)
    ids=[e['event_id'] for e in json.loads(r.wire_v2)['events']]
    assert len(ids)==len(set(ids))

def test_N08_input_and_action_quotas():
    assert run_studio_session(b' '*2097153,**fixtures.dependencies()).outcome=='SESSION_REJECTED'
    d=data();d['actions']=[dict(id=str(i),at_us=5000,kind='ACK') for i in range(20000)];reject(d)

@pytest.mark.parametrize('time',[-1,1,200000])
def test_N09_reordered_or_outside_duration(time):
    d=data();d['actions'][1]['at_us']=time;reject(d)

@pytest.mark.parametrize('value',[0.5,500000.0,1000001,-1])
def test_N10_nonintegral_or_outofrange_micro(value):
    d=data();action(d,'active')['flap_micro']=value;reject(d)

def test_N10_exact_decimal_tokens_independent_context():
    d=data();action(d,'active').update(flap_micro=999999,steer_micro=-2)
    with localcontext() as ctx:
        ctx.prec=2;wire=session_to_wire_v2(raw(d))
    obj=json.loads(wire,parse_float=Decimal);a=obj['events'][7]['payload']
    assert a['flap_demand']==Decimal('0.999999') and a['steering_demand']==Decimal('-0.000002')
    r=run(d);assert (r.model_ticks[29].model_effort_left_micro,r.model_ticks[29].model_effort_right_micro)==(1000000,999997)

def test_N11_rf_provenance_injection():
    d=data();d['actions'][0]['rf_provenance']='TRUSTED';reject(d)

@pytest.mark.parametrize('conflict',[False,True])
def test_N12_duplicate_and_conflicting_control(conflict):
    d=data();extra=dict(action(d,'low2'),id='other-low',flap_micro=1 if conflict else 0)
    d['actions'].insert(3,extra);row=run(d).model_ticks[7]
    assert len(row.causal_event_ids)==2
    assert (row.model_snapshot.low_qualified_eval_us==35000)==(not conflict)

def test_N13_invalid_valid_batch():
    d=data();d['actions'].insert(3,dict(id='bad',at_us=35000,kind='CONTROL_INVALID'))
    row=run(d).model_ticks[7];assert row.model_snapshot.control_at_us==15000 and row.model_snapshot.low_qualified_eval_us is None

def test_N14_healthy_lost_lost():
    d=data();d['actions'].insert(8,dict(id='healthy-with-lost',at_us=155000,kind='RF_HEALTHY'))
    row=run(d).model_ticks[31];assert row.rf_effective=='LOST' and row.model_state.value=='CONTINGENCY'

def test_N15_ambiguous_no_uncommitted_display_or_export(tmp_path):
    r=run(data('ambiguous'));assert r.model.blocked_at_tick==3 and len(r.model_ticks)==3
    assert '  15000 |' not in offline.console(r)
    for kind,suffix in [('html','.html'),('proof','.model.json'),('candidate','.model-candidate.jsonl')]:
        p=tmp_path/('blocked'+suffix)
        with pytest.raises(ValueError):offline.export(r,kind,p)
        assert not p.exists()

def test_N16_held_high_no_arm():
    r=run(data('rf-loss'));assert r.model_ticks[2].model_state.value=='DISARMED'

@pytest.mark.parametrize('time,expected',[(139999,'ARM_CHECK'),(140000,'ARMED_IDLE')])
def test_N17_high_confirmation_exact_boundary(time,expected):
    d=data();action(d,'confirm')['at_us']=time
    assert run(d).model_ticks[28].model_state.value==expected

@pytest.mark.parametrize('time,qualifies',[(34999,False),(35000,True)])
def test_N17_low_exact_boundary(time,qualifies):
    d=data();action(d,'low2')['at_us']=time
    assert (run(d).model_ticks[7].model_snapshot.low_qualified_eval_us is not None)==qualifies

def test_N18_active_not_confirmed():
    d=data();d['actions']=[a for a in d['actions'] if a['id']!='confirm']
    assert run(d).model_ticks[29].model_effort_left_micro is None

@pytest.mark.parametrize('channel',['rf','control'])
@pytest.mark.parametrize('delta,state',[(0,'ACTUATION_ACTIVE'),(1,'CONTINGENCY')])
def test_N19_independent_freshness(channel,delta,state):
    d=data();d['duration_us']=350000;d['actions']=[a for a in d['actions'] if a['at_us']<=145000]
    if channel=='control':
        action(d,'active')['at_us']-=delta
        d['actions'].append(dict(id='rf-late',at_us=300000,kind='RF_HEALTHY'))
    else:
        d['actions'].append(dict(id='rf-final',at_us=145000-delta,kind='RF_HEALTHY'))
        d['actions'].append(dict(action(d,'active'),id='control-late',at_us=300000))
    d['actions'].sort(key=lambda a:a['at_us']);r=run(d)
    assert r.model_ticks[69].model_state.value==state and r.model_ticks[70].model_state.value=='CONTINGENCY'

@pytest.mark.parametrize('reset',[False,True])
def test_N20_ack_not_same_tick_qualification_or_reset(reset):
    d=data()
    if reset:d['actions'].append(dict(id='reset-ack',at_us=190000,kind='RESET'))
    else:action(d,'ack')['at_us']=185000
    d['actions'].sort(key=lambda a:a['at_us'])
    assert run(d).model_ticks[38 if reset else 37].model_state.value=='CONTINGENCY'

def test_N21_catastrophe_latch():
    r=run(data('rf-loss'));assert all(t.model_state.value=='FAULT_LATCHED' for t in r.model_ticks[13:])

@pytest.mark.parametrize('fault',['BEFORE_APPEND','SHORT_WRITE','AFTER_WRITE_BEFORE_ACK','SERIALIZER','QUOTA'])
def test_N22_append_failure_clears_stale_controller_and_no_file(fault,monkeypatch,tmp_path):
    c=StudioController();c.load(fixtures.session('nominal'));c.run(**fixtures.dependencies())
    c.seek(29);assert c.row.model_effort_left_micro==250000
    monkeypatch.setattr(trace._ModelJournal,'_fault',lambda self,r:fault if r.get('tick_index')==29 else None)
    r=c.run(**fixtures.dependencies())
    assert r.outcome=='MODEL_EVIDENCE_INCOMPLETE' and len(r.model_ticks)==29 and c.index==0
    assert ' 145000 |' not in offline.console(r)
    with pytest.raises(ValueError):offline.export(r,'html',tmp_path/'bad.html')
    assert not (tmp_path/'bad.html').exists()

def test_N23_immutable_no_authority_constructor_or_callback():
    b=VirtualRuntimeBoundary()
    with pytest.raises(FrozenInstanceError):b.output_allowed=True
    with pytest.raises(TypeError):VirtualRuntimeBoundary(runtime_authorized=True)
    for key in ('sink','approved','prior','callback','clock'):
        with pytest.raises(TypeError):run_studio_session(fixtures.session('nominal'),**fixtures.dependencies(),**{key:True})

def test_N23_real_reference_mismatch_no_model():
    deps=fixtures.dependencies();deps['claimed_host']=replace(deps['claimed_host'],owner='FAKE')
    r=run_studio_session(fixtures.session('nominal'),**deps)
    assert r.outcome=='MODEL_REFERENCE_BLOCKED' and r.model_ticks==();denied(r)

def test_N24_fixture_exact_no_dirty_worktree_dependency(tmp_path,monkeypatch):
    from scripts import verify
    expected=verify.preserved_fixture()
    monkeypatch.setattr(verify,'ROOT',tmp_path/'nonexistent-owner-worktree')
    assert verify.preserved_fixture()==expected
    with pytest.raises(ValueError):verify.stage_preserved(tmp_path)

def test_controller_edit_invalidates_and_replay_never_on_append(monkeypatch):
    c=StudioController();c.load(fixtures.session('nominal'));r=c.run(**fixtures.dependencies())
    c.play();c.step();assert c.index==1
    c.pause();c.step();assert c.index==1
    c.append(dict(id='last',at_us=195000,kind='ACK'))
    assert c.report is None and c.row is None and not c.playing
    for bad in (b'{}',b'NaN'):
        with pytest.raises(SessionError):c.load(bad)
        assert c.report is None
    c.load(fixtures.session('nominal'));assert c.run(**fixtures.dependencies())==r

def test_headless_does_not_import_tk_or_duplicate_fsm():
    assert 'tkinter' not in sys.modules
    import bb_host_virtual_control_studio
    for path in Path(bb_host_virtual_control_studio.__file__).parent.glob('*.py'):
        tree=ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):assert not {n.name for n in node.names}&{'tkinter','socket','subprocess','os','pathlib','serial','time'}
            if isinstance(node,ast.ImportFrom):assert node.module not in {'tkinter','socket','os','subprocess','pathlib','serial','time'}
            if isinstance(node,ast.Call):assert getattr(node.func,'id','') not in {'eval','exec','open','__import__'}

@pytest.mark.parametrize('case,code',[('nominal',0),('rf-loss',0),('ambiguous',2)])
def test_cli_actual_outcome(case,code,capsys):
    assert studio.main(['--case',case,'--text'])==code
    assert 'NO OUTPUT' in capsys.readouterr().out

@pytest.mark.parametrize('path',['//remote/a.html',r'\\server\a.html','COM1','a.html:stream','a.exe'])
def test_offline_reject_nonlocal_device_wrong_suffix(path):
    with pytest.raises(ValueError):offline.write_local(b'x',path,'.html')

def test_offline_replace_failure_preserves_existing(tmp_path,monkeypatch):
    p=tmp_path/'old.html';p.write_bytes(b'old')
    def fail(*args):raise OSError('TEST ONLY replacement failure')
    monkeypatch.setattr(offline.os,'replace',fail)
    with pytest.raises(OSError):offline.write_local(b'new',p,'.html')
    assert p.read_bytes()==b'old' and list(tmp_path.iterdir())==[p]

def test_large_session_one_f1_call(monkeypatch):
    import bb_host_virtual_control_studio.studio as core
    original=core.run_fsm_model;calls=[]
    def observed(*args):calls.append(1);return original(*args)
    monkeypatch.setattr(core,'run_fsm_model',observed)
    d=data();d['duration_us']=1000000
    d['actions']=[dict(id=f'a{i}',at_us=5000,kind='ACK') for i in range(10000)]
    r=run(d);assert len(r.model_ticks)==201 and calls==[1]
    assert len(r.wire_v2)<=2097152 and len(offline.proof(r))<=16777216
