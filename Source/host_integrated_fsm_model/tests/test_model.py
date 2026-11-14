"""N01-N24 system boundaries with genuine upstream data on positive paths."""
import ast
import builtins
from dataclasses import replace, FrozenInstanceError, fields
from decimal import localcontext
import hashlib
import json
import locale
import os
from pathlib import Path
import socket
import subprocess
import time
import tracemalloc

import pytest
from bb_host_integrated_fsm_model import run_fsm_model, ModelOutcome as O
from bb_host_integrated_fsm_model import model, trace, viewer
from scripts.fixtures import inputs, frozen_bytes
from scripts import demo
from test_oracles import denied


def wire(preset="nominal"):
    args=inputs(preset)
    return args,json.loads(args["scenario_raw"])


def run(args,data):
    args=dict(args,scenario_raw=json.dumps(data,separators=(",", ":")).encode())
    report=run_fsm_model(**args)
    denied(report)
    return report


def event(data,identity):
    return next(e for e in data["events"] if e["event_id"]==identity)


def sort(data):
    data["events"].sort(key=lambda e:e["event_at_us"])


def forbidden(*args,**kw):
    raise AssertionError("forbidden integration call")


@pytest.mark.parametrize("name",["scenario_raw","policy_raw","intent_raw","engine_artifact","scheduler_artifact"])
@pytest.mark.parametrize("bad",[None,True,"{}",bytearray(b'{}'),memoryview(b'{}')])
def test_N01_wrong_types(name,bad):
    args=inputs("nominal"); args[name]=bad
    with pytest.raises((TypeError,ValueError)): run_fsm_model(**args)


def test_N01_schema_and_time_types():
    args=inputs("nominal"); args['frozen_wire_v2_schema']={}
    with pytest.raises(ValueError): run_fsm_model(**args)
    args,data=wire(); data['duration_us']=True
    assert run(args,data).outcome is O.MODEL_INPUT_REJECTED


@pytest.mark.parametrize("field",["engine_revision","owner","scope"])
def test_N02_reference_before_scheduler(field,monkeypatch):
    args=inputs("nominal"); args['claimed_host']=replace(args['claimed_host'],**{field:'BAD'})
    monkeypatch.setattr(model,'iter_virtual_ticks',forbidden)
    monkeypatch.setattr(model,'run_shadow_replay',forbidden)
    r=run_fsm_model(**args)
    assert r.outcome is O.MODEL_REFERENCE_BLOCKED and r.model_ticks==() and r.candidate_trace==b''


@pytest.mark.parametrize("field",['intent_raw','engine_artifact','scheduler_artifact'])
def test_N02_intent_blocks(field):
    args=inputs('nominal'); args[field]+=b'\n'
    r=run_fsm_model(**args)
    assert r.outcome is O.MODEL_REFERENCE_BLOCKED and r.model_tick_count==0


def test_N03_policy_cannot_be_overridden():
    args=inputs('nominal'); args['policy_raw']+=b'\n'
    data=json.loads(args['intent_raw']); data['policy_sha256']=hashlib.sha256(args['policy_raw']).hexdigest()
    args['intent_raw']=json.dumps(data,sort_keys=True,separators=(',',':')).encode()
    assert run_fsm_model(**args).model_tick_count==0


@pytest.mark.parametrize("key",['approved','runtime_authorized','owner','plugin','sink','host','engine_revision'])
def test_N04_injected_authority(key):
    args,data=wire(); data[key]=True
    assert run(args,data).outcome is O.MODEL_INPUT_REJECTED
    with pytest.raises(TypeError): run_fsm_model(**inputs('nominal'),**{key:True})


def test_N05_duplicate_id_global_rejected():
    args,data=wire(); data['events'][-1]['event_id']='low1'
    assert run(args,data).model_tick_count==0


def test_N06_conflict_and_equivalent_ids():
    r=run_fsm_model(**inputs('conflict'))
    assert r.model_ticks[3].model_snapshot.control_at_us==10000
    row=r.model_ticks[4]
    assert row.causal_event_ids==('identical-a','identical-b')
    assert row.model_snapshot.low_first_at_us==20000 and row.model_snapshot.low_qualified_eval_us is None
    assert 'R_DUPLICATE_SEMANTIC_OBSERVATION' in row.model_reasons


def test_N07_invalid_valid_does_not_accept():
    r=run_fsm_model(**inputs('conflict')); row=r.model_ticks[5]
    assert row.model_snapshot.control_at_us==20000 and row.model_snapshot.low_first_at_us is None
    assert 'E_FRAME_INVALID' in row.model_reasons and row.model_effort_left_micro is None


@pytest.mark.parametrize('reset',[False,True])
def test_N08_lost_dominates_same_tick_healthy_reset(reset):
    args,data=wire()
    data['events'] += [dict(event_id='healthy-with-lost',event_at_us=155000,type='SIM_RF_STATUS',payload=dict(rf_health='HEALTHY',rf_provenance='INJECTED_SIM'))]
    if reset: data['events'] += [dict(event_id='reset-with-lost',event_at_us=155000,type='SIM_RESET',payload={})]
    sort(data); row=run(args,data).model_ticks[31]
    assert row.model_state.value=='CONTINGENCY' and row.rf_effective=='LOST'
    assert row.model_snapshot.control_at_us==145000


def test_N09_original_subgrid_times():
    args,data=wire(); event(data,'low1')['event_at_us']=14998
    event(data,'low2')['event_at_us']=34999
    r=run(args,data)
    assert r.model_ticks[3].model_snapshot.control_at_us==14998
    assert r.model_ticks[7].model_snapshot.low_qualified_eval_us==35000


@pytest.mark.parametrize('second,qualified',[(34999,False),(35000,True)])
def test_N10_low_boundary(second,qualified):
    args,data=wire(); event(data,'low2')['event_at_us']=second
    r=run(args,data)
    assert (r.model_ticks[7].model_snapshot.low_qualified_eval_us is not None)==qualified
    assert r.model_ticks[8].model_state.value==('ARM_CHECK' if qualified else 'DISARMED')


@pytest.mark.parametrize('confirm,state',[(139999,'ARM_CHECK'),(140000,'ARMED_IDLE')])
def test_N11_high_boundary(confirm,state):
    args,data=wire(); event(data,'confirm1')['event_at_us']=confirm
    assert run(args,data).model_ticks[28].model_state.value==state


@pytest.mark.parametrize('channel',['control','rf'])
@pytest.mark.parametrize('delta,state',[(0,'ACTUATION_ACTIVE'),(1,'CONTINGENCY')])
def test_N12_independent_freshness(channel,delta,state):
    args,data=wire()
    data['events']=[e for e in data['events'] if e['event_at_us']<=145000]
    if channel=='control':
        event(data,'active1')['event_at_us']=145000-delta
        data['events'].append(dict(event_id='rf-late',event_at_us=300000,type='SIM_RF_STATUS',payload=dict(rf_health='HEALTHY',rf_provenance='INJECTED_SIM')))
    else:
        data['events'].append(dict(event_id='rf-final',event_at_us=145000-delta,type='SIM_RF_STATUS',payload=dict(rf_health='HEALTHY',rf_provenance='INJECTED_SIM')))
        data['events'].append(dict(event(data,'active1'),event_id='control-late',event_at_us=300000))
    sort(data); r=run(args,data)
    assert r.outcome is O.MODEL_REPLAY_COMPLETE,r.diagnostic
    assert r.model_ticks[69].model_state.value==state
    assert r.model_ticks[70].model_state.value=='CONTINGENCY'


def test_N13_held_high_reset_and_no_timer_confirmation():
    args,data=wire(); data['events']=[e for e in data['events'] if e['event_id']!='confirm1']
    r=run(args,data)
    assert r.model_ticks[28].model_state.value=='ARM_CHECK'
    assert r.model_ticks[29].model_state.value!='ACTUATION_ACTIVE'
    conflict=run_fsm_model(**inputs('conflict'))
    assert conflict.model_ticks[6].model_state.value=='SELF_TEST'
    assert conflict.model_ticks[6].model_snapshot.low_first_at_us is None
    assert conflict.model_ticks[6].model_snapshot.control_at_us==20000


def test_N14_catastrophe_always_latched():
    r=run_fsm_model(**inputs('conflict'))
    assert all(t.model_state.value=='FAULT_LATCHED' and t.model_effort_left_micro is None for t in r.model_ticks[7:])


@pytest.mark.parametrize('at,reset,state',[(185000,False,'CONTINGENCY'),(190000,True,'CONTINGENCY'),(190000,False,'DISARMED')])
def test_N15_ack_prior_commit_and_reset(at,reset,state):
    args,data=wire(); event(data,'ack')['event_at_us']=at
    if reset: data['events'].append(dict(event_id='reset-ack',event_at_us=at,type='SIM_RESET',payload={}))
    sort(data); r=run(args,data)
    assert r.model_ticks[at//5000].model_state.value==state
    if state=='DISARMED':
        assert r.model_ticks[at//5000].model_snapshot.low_first_at_us is None


def test_N16_s1_recomputes_held_input_without_refresh():
    r=run_fsm_model(**inputs('nominal'))
    a,b=r.model_ticks[29:31]
    assert b.model_snapshot.control_at_us==a.model_snapshot.control_at_us==145000
    assert b.model_snapshot.healthy_rf_at_us==a.model_snapshot.healthy_rf_at_us==110000
    assert b.model_snapshot.held_input==(500000,250000) and b.model_input_mode=='S1_HELD'
    assert (b.model_effort_left_micro,b.model_effort_right_micro)==(250000,750000)


@pytest.mark.parametrize('where',['header','tick','terminal'])
@pytest.mark.parametrize('fault',['BEFORE_APPEND','SHORT_WRITE','AFTER_WRITE_BEFORE_ACK','QUOTA','SERIALIZER'])
def test_N17_append_fault_no_uncommitted_display(where,fault,monkeypatch):
    seen=[]
    def inject(self,record):
        seen.append((record['record_type'],record.get('tick_index')))
        if record['record_type']==where and (where!='tick' or record['tick_index']==29): return fault
    monkeypatch.setattr(trace._ModelJournal,'_fault',inject)
    r=run_fsm_model(**inputs('nominal')); denied(r)
    assert r.outcome is O.MODEL_EVIDENCE_INCOMPLETE and r.candidate_trace_sha256 is None
    assert r.model_tick_count=={'header':0,'tick':29,'terminal':71}[where]
    records=[json.loads(x) for x in r.candidate_trace.splitlines()]
    assert len([x for x in records if x['record_type']=='tick'])==r.model_tick_count
    assert not any(x['record_type']=='terminal' for x in records)
    assert len(seen)=={'header':1,'tick':31,'terminal':73}[where]
    if where=='tick':
        assert not any(row.model_effort_left_micro is not None for row in r.model_ticks)
        assert ' 145000 |' not in viewer.render_console(r)
        assert '250000 micro' not in viewer.render_html(r).decode()


def test_N17_sticky_private_failure(monkeypatch):
    calls=[]
    def failure(self,r): calls.append(r); return 'BEFORE_APPEND'
    monkeypatch.setattr(trace._ModelJournal,'_fault',failure)
    journal=trace._ModelJournal()
    assert journal.append({}) is False and journal.append({}) is False and len(calls)==1
    assert journal.committed_bytes()==b''


def test_N19_immutable_and_no_authority_or_external_completed_claim():
    from jsonschema import Draft202012Validator
    r=run_fsm_model(**inputs('nominal')); denied(r)
    schema=json.loads(frozen_bytes('Design/contracts/G0A1_EXTERNAL_REPORT_R11_CANDIDATE.schema.json'))
    assert not Draft202012Validator(schema).is_valid({'run_status':'COMPLETED','evidence_complete':True,'control_trace_sha256':None})
    assert r.candidate_trace_sha256==hashlib.sha256(r.candidate_trace).hexdigest()
    for obj in (r,*r.model_ticks,*[t.model_snapshot for t in r.model_ticks]):
        assert not hasattr(obj,'__dict__')
        for f in fields(obj):
            with pytest.raises(FrozenInstanceError): setattr(obj,f.name,None)
    with pytest.raises(ValueError): replace(r,runtime_authorized=True)
    for parameter in ('prior','snapshot','output_sink','authorized','callback','clock'):
        with pytest.raises(TypeError): run_fsm_model(**inputs('nominal'),**{parameter:True})


def test_N20_core_has_no_io_hardware_or_environment(monkeypatch):
    args=inputs('nominal')
    with monkeypatch.context() as patch:
        for obj,name in ((builtins,'open'),(Path,'open'),(socket,'socket'),(os,'getenv'),(subprocess,'Popen'),(time,'time')):
            patch.setattr(obj,name,forbidden)
        assert run_fsm_model(**args).outcome is O.MODEL_REPLAY_COMPLETE
    forbidden_modules={'os','pathlib','socket','subprocess','serial','ctypes','time','random','bb_host_arm_qualification'}
    for path in Path(model.__file__).parent.glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node,ast.Import): assert not ({n.name for n in node.names}&forbidden_modules)
            if isinstance(node,ast.ImportFrom): assert node.module not in forbidden_modules
            if isinstance(node,ast.Call): assert getattr(node.func,'id','') not in {'eval','exec','open','__import__','OwnerSnapshot','AcceptedPreflight'}


def test_N21_replay_decimal_locale_timezone(monkeypatch):
    args=inputs('nominal'); expected=run_fsm_model(**args)
    previous=locale.setlocale(locale.LC_ALL)
    try:
        for loc in ('C','English_United States.1252'):
            locale.setlocale(locale.LC_ALL,loc)
            for zone in ('UTC0','ICT-7'):
                monkeypatch.setenv('TZ',zone)
                for precision in (2,28,60):
                    with localcontext() as ctx:
                        ctx.prec=precision
                        assert run_fsm_model(**args)==expected
    finally:
        locale.setlocale(locale.LC_ALL,previous)


def test_N22_long_60s_20000_events(monkeypatch):
    args,data=wire(); data['duration_us']=60000000
    data['events']=data['events'][:1]+[dict(event_id=f'a{i}',event_at_us=5000,type='SIM_ACK_FAULT',payload={}) for i in range(19999)]
    seen=[]; genuine=model.normalize_tick_observations
    def observe(batch): seen.append(len(batch.events)); return genuine(batch)
    monkeypatch.setattr(model,'normalize_tick_observations',observe)
    tracemalloc.start(); start=time.perf_counter()
    try:
        r=run(args,data); elapsed=time.perf_counter()-start
        _,peak=tracemalloc.get_traced_memory()
    finally: tracemalloc.stop()
    assert r.outcome is O.MODEL_REPLAY_COMPLETE,r.diagnostic
    assert r.model_tick_count==12001 and seen[:2]==[1,19999] and sum(seen[2:])==0
    assert len(r.candidate_trace)<=16777216
    assert len(viewer.render_html(r))<=16777216
    Path('evidence/performance.json').write_text(json.dumps(dict(events=20000,ticks=12001,elapsed_seconds=elapsed,
        peak_python_allocation_bytes=peak,process_peak_memory='NOT MEASURED',candidate_bytes=len(r.candidate_trace)),indent=2)+'\n',encoding='utf-8')


def test_N23_genuine_upstream_order_never_admits_d2_or_task006(monkeypatch):
    import bb_host_arm_qualification
    monkeypatch.setattr(bb_host_arm_qualification,'propose_arm_qualification',forbidden)
    names=['normalize_tick_observations','evaluate_temporal_guard_facts','assess_safety_priority','assess_health_evidence','triage_guard_evidence']
    seen=[]
    for name in names:
        original=getattr(model,name)
        def observed(*args,_name=name,_original=original,**kw):
            seen.append(_name)
            return _original(*args,**kw)
        monkeypatch.setattr(model,name,observed)
    r=run_fsm_model(**inputs('nominal'))
    assert seen==names*71
    assert r.model_ticks[29].model_state.value=='ACTUATION_ACTIVE'
    assert r.model_ticks[29].output_allowed is False
    assert all('TRUST_NOT_PROVEN' in t.triage_reasons for t in r.model_ticks)


@pytest.mark.parametrize('case,count',[('nominal',71),('recovery',50),('conflict',9)])
def test_N24_cli_viewer_is_self_contained(case,count,tmp_path,capsys):
    path=tmp_path/'nested/viewer.html'
    assert demo.main(['--case',case,'--view',str(path)])==0
    text=path.read_text(encoding='utf-8')
    assert viewer.BANNER in text and viewer.BANNER in capsys.readouterr().out
    assert 'connect-src &#' not in text and "connect-src 'none'" in text
    for token in ('fetch(', 'XMLHttpRequest','WebSocket','WebUSB','navigator.serial','postMessage(', 'import(', 'http://', 'https://', 'onclick='):
        assert token not in text
    assert 'textContent=' in text and 'innerHTML' not in text


def test_N24_html_escapes_hostile_event_ids():
    args,data=wire(); data['events'][0]['event_id']='</script><img src=x onerror=alert(1)>'
    r=run(args,data); raw=viewer.render_html(r)
    assert b'<img' not in raw and b'\\u003c/script\\u003e' in raw
    assert run(args,data)==r
