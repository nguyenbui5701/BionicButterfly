import ast
import builtins
from copy import deepcopy
from dataclasses import fields, replace, FrozenInstanceError
from decimal import Decimal, localcontext
from enum import Enum
import locale
from pathlib import Path
import random
import socket
import sys
import time
from types import MappingProxyType

import pytest

from bb_host_arm_qualification import (ArmQualificationProposal, ProposalKind as K, PriorQualificationWindow as W,
    HypotheticalQualificationVerdict as V, HealthVerdict as H, ControlVerdict as C, propose_arm_qualification as propose)
from bb_host_safety_priority_kernel import SafetyState as S
import bb_host_arm_qualification.qualification as runtime
from scripts.scenarios import load_oracles, pipeline

CASES = load_oracles()["cases"]


def case_inputs(number, **changes):
    case = deepcopy(CASES[number-1]); case.update(changes)
    _, _, obs, _, temporal, priority, window, verdict = pipeline(case)
    return obs, temporal, priority, window, verdict


def control(at, identity="v", high=False, flap="0", steer="0"):
    return dict(event_id=identity, event_at_us=at, kind="CONTROL_VALID", arm=high, flap=flap, steer=steer)


def custom(state="DISARMED", tick=5000, events=(), window=None, health="PASS", control_verdict="ADMITTED", prior_times=None):
    commit = None if tick == 0 else tick-5000
    stamp = commit if prior_times is None else None
    times = (stamp, stamp) if prior_times is None else prior_times
    case = dict(pre_state=state, eval_at_us=tick,
                events=[dict(event_id="boot", event_at_us=0, kind="BOOT"), *events],
                prior_timestamp_snapshot=dict(last_committed_eval_at_us=commit,last_accepted_control_at_us=times[0],last_uncontested_healthy_rf_at_us=times[1]),
                prior_qualification_window=dict(last_committed_eval_at_us=commit,low_first_original_at_us=None,low_qualified_committed_eval_at_us=None,high_edge_original_at_us=None,high_edge_committed_eval_at_us=None),
                hypothetical_verdict=dict(health=health,control=control_verdict))
    if window: case["prior_qualification_window"].update(window)
    _, _, obs, _, temporal, priority, window_obj, verdict = pipeline(case)
    return obs, temporal, priority, window_obj, verdict


@pytest.mark.parametrize("position", range(5))
@pytest.mark.parametrize("wrong", [None, {}, [], True, 1, b"{}", "PASS"])
def test_exact_top_level_types(position, wrong):
    args=list(case_inputs(1)); args[position]=wrong
    with pytest.raises(TypeError): propose(*args)


@pytest.mark.parametrize("position", range(5))
def test_forged_subclasses(position):
    args=list(case_inputs(1)); original=args[position]
    forged=type("Forged", (type(original),), {})
    args[position]=forged(**{f.name:getattr(original,f.name) for f in fields(original)})
    with pytest.raises(TypeError): propose(*args)


@pytest.mark.parametrize("verdict", [V("PASS",C.ADMITTED),V(H.PASS,"ADMITTED"),V(True,C.ADMITTED),V(H.FAIL,C.ADMITTED),V(H.UNRESOLVED,C.ADMITTED)])
def test_malformed_or_contradictory_verdict(verdict):
    *args,_=case_inputs(1)
    with pytest.raises((TypeError,ValueError)):propose(*args,verdict)


@pytest.mark.parametrize("case_number", [25,26,27,28,29,30,32])
@pytest.mark.parametrize("control_verdict", [C.ADMITTED,C.UNRESOLVED])
def test_pass_cannot_override_priority_blocker(case_number, control_verdict):
    *args,_=case_inputs(case_number)
    with pytest.raises(ValueError):propose(*args,V(H.PASS,control_verdict))


@pytest.mark.parametrize("verdict", [V(H.PASS,C.ABSENT), V(H.FAIL,C.ABSENT)])
def test_absent_contradicts_visible_candidate(verdict):
    *args,_=case_inputs(1)
    with pytest.raises(ValueError):propose(*args,verdict)


@pytest.mark.parametrize("control_verdict", [C.ADMITTED,C.DENIED])
def test_admitted_or_denied_requires_current_candidate(control_verdict):
    *args,_=case_inputs(6)
    with pytest.raises(ValueError):propose(*args,V(H.PASS,control_verdict))


@pytest.mark.parametrize("position", [0,1,2])
@pytest.mark.parametrize("changes", [{"tick_index":True},{"tick_index":1.0},{"tick_index":-1},{"tick_index":12001},
                                    {"eval_at_us":True},{"eval_at_us":-1},{"eval_at_us":15000.0},{"eval_at_us":15001},
                                    {"tick_index":4,"eval_at_us":20000}])
def test_tick_metadata_rejects_before_output(position,changes,monkeypatch):
    args=list(case_inputs(1));args[position]=replace(args[position],**changes)
    def forbidden(*a,**kw):pytest.fail("constructed output for invalid caller")
    monkeypatch.setattr(runtime,"ArmQualificationProposal",forbidden)
    with pytest.raises(ValueError):propose(*args)


@pytest.mark.parametrize("changes", [{"requires_full_fsm":False},{"requires_full_fsm":1},{"blocks_control_qualification":0},
                                    {"pre_state":"DISARMED"},{"provisional_next_state":"SELF_TEST"},
                                    {"priority_category":"CAN_ARM"},{"provisional_next_state":S.ACTUATION_ACTIVE}])
def test_priority_shape(changes):
    obs,temporal,priority,window,verdict=case_inputs(1)
    with pytest.raises((ValueError,TypeError)):propose(obs,temporal,replace(priority,**changes),window,verdict)


@pytest.mark.parametrize("name", ["last_committed_eval_at_us","low_first_original_at_us","low_qualified_committed_eval_at_us","high_edge_original_at_us","high_edge_committed_eval_at_us"])
@pytest.mark.parametrize("value", [True,1.0,Decimal(1),-1,40001,"1"])
def test_invalid_window_scalar(name,value):
    obs,temporal,priority,window,verdict=case_inputs(9)
    with pytest.raises(ValueError):propose(obs,temporal,priority,replace(window,**{name:value}),verdict)


@pytest.mark.parametrize("changes", [
    {"last_committed_eval_at_us":None},{"last_committed_eval_at_us":40000},{"last_committed_eval_at_us":35001},
    {"low_first_original_at_us":None},{"low_qualified_committed_eval_at_us":40000},
    {"low_qualified_committed_eval_at_us":15000},{"low_qualified_committed_eval_at_us":34999},
    {"high_edge_original_at_us":30000},{"high_edge_original_at_us":30000,"high_edge_committed_eval_at_us":30000},
])
def test_qualified_low_history_must_be_possible_and_prior(changes):
    obs,t,p,w,v=case_inputs(9)
    with pytest.raises(ValueError):propose(obs,t,p,replace(w,**changes),v)


@pytest.mark.parametrize("changes", [{"high_edge_original_at_us":None},{"high_edge_committed_eval_at_us":None},
                                    {"high_edge_original_at_us":40001},{"high_edge_committed_eval_at_us":40001},
                                    {"high_edge_committed_eval_at_us":140000},{"low_first_original_at_us":15000}])
def test_high_history_invariants(changes):
    obs,t,p,w,v=case_inputs(14)
    with pytest.raises(ValueError):propose(obs,t,p,replace(w,**changes),v)


@pytest.mark.parametrize("case_number", [20,23,32])
def test_other_states_require_empty_windows(case_number):
    obs,t,p,w,v=case_inputs(case_number)
    with pytest.raises(ValueError):propose(obs,t,p,replace(w,low_first_original_at_us=15000),v)


@pytest.mark.parametrize("position,name", [(0,"has_invalid_control"),(0,"rf_has_lost"),(1,"has_valid_control_conflict"),
                                         (1,"has_rf_unknown_observation"),(1,"prior_control_within_timeout")])
def test_mirrors_and_flags(position,name):
    args=list(case_inputs(1));args[position]=replace(args[position],**{name:False if name=='prior_control_within_timeout' else True})
    with pytest.raises(ValueError):propose(*args)


@pytest.mark.parametrize("delta", [-1,1])
def test_admitted_candidate_must_match_group_original_timestamp(delta):
    obs,t,p,w,v=case_inputs(2)
    with pytest.raises(ValueError):propose(obs,replace(t,observed_uncontested_valid_control_at_us=34999+delta),p,w,v)


@pytest.mark.parametrize("flap,steer,kind", [("0.020000","0.05",K.HIGH_EDGE_ELIGIBLE),("2e-2","-0.05",K.HIGH_EDGE_ELIGIBLE),
    ("0.020001","0",K.CLEAR_WINDOW),("0.02","0.050001",K.CLEAR_WINDOW),("0.02","-0.050001",K.CLEAR_WINDOW)])
def test_neutrality_exact_even_under_low_decimal_precision(flap,steer,kind):
    case=deepcopy(CASES[8]);case['events'][-1].update(flap=flap,steer=steer)
    _,_,obs,_,t,p,w,v=pipeline(case)
    for precision in (2,28):
        with localcontext() as context:
            context.prec=precision
            assert propose(obs,t,p,w,v).proposal_kind is kind


@pytest.mark.parametrize("flap,expected", [("0.049999",K.NO_CHANGE),("0.050000",K.NO_CHANGE),("5e-2",K.NO_CHANGE),("0.050001",K.DEMAND_OBSERVED)])
def test_strict_demand_boundary(flap,expected):
    case=deepcopy(CASES[19]);case['events'][-1]['flap']=flap
    _,_,obs,_,t,p,w,v=pipeline(case)
    with localcontext() as context:
        context.prec=2
        assert propose(obs,t,p,w,v).proposal_kind is expected


def test_already_qualified_low_never_refreshes_commit_anchor():
    args=custom(tick=45000,events=[control(44999)],window={'low_first_original_at_us':15000,'low_qualified_committed_eval_at_us':35000})
    result=propose(*args)
    assert result.proposal_kind is K.HOLD_WINDOW
    assert (result.proposed_low_first_original_at_us,result.proposed_low_qualified_committed_eval_at_us)==(15000,35000)


@pytest.mark.parametrize("case_number", [6,16])
def test_health_failure_breaks_continuity_without_new_frame(case_number):
    *args,_=case_inputs(case_number)
    result=propose(*args,V(H.FAIL,C.ABSENT))
    assert result.proposal_kind is K.BLOCKED_CLEAR
    assert all(getattr(result,f.name) is None for f in fields(result) if f.name.startswith('proposed_'))


@pytest.mark.parametrize("case_number", [2,13])
@pytest.mark.parametrize("verdict", [V(H.UNRESOLVED,C.UNRESOLVED),V(H.PASS,C.UNRESOLVED),V(H.PASS,C.DENIED)])
def test_unresolved_preserves_only_proposal_denied_clears(case_number,verdict):
    obs,t,p,w,_=case_inputs(case_number);result=propose(obs,t,p,w,verdict)
    assert result.proposal_kind is (K.CLEAR_WINDOW if verdict.control is C.DENIED else K.DEFER)
    values=tuple(getattr(result,f.name) for f in fields(result) if f.name.startswith('proposed_'))
    assert values==((None,)*4 if verdict.control is C.DENIED else (w.low_first_original_at_us,w.low_qualified_committed_eval_at_us,w.high_edge_original_at_us,w.high_edge_committed_eval_at_us))


@pytest.mark.parametrize("state", ['ARM_CHECK','ARMED_IDLE','ACTUATION_ACTIVE'])
def test_low_disarm_does_not_seed_new_low(state):
    result=propose(*custom(state=state,events=[control(4999)]))
    assert result.proposal_kind is K.LOW_DISARM_OBSERVED
    assert result.proposed_low_first_original_at_us is None


@pytest.mark.parametrize("kind", ['RF_UNKNOWN','RF_LOST','RESET','CATA','CONTROL_INVALID'])
def test_hazards_cannot_be_bypassed_by_pass(kind):
    hazard=dict(event_id='hazard',event_at_us=5000,kind=kind)
    args=custom(events=[control(4999),hazard],health='FAIL',control_verdict='UNRESOLVED')
    assert propose(*args).proposal_kind is K.BLOCKED_CLEAR
    with pytest.raises(ValueError):propose(*args[:-1],V(H.PASS,C.ADMITTED))


def test_t0_and_self_test_are_never_positive():
    args=custom(state='BOOT',tick=0,health='UNRESOLVED',control_verdict='ABSENT')
    assert propose(*args).proposal_kind is K.BLOCKED_CLEAR
    with pytest.raises(ValueError):propose(*args[:3],W(0,None,None,None,None),args[4])
    assert propose(*custom(state='SELF_TEST',events=[control(4999)])).proposal_kind is K.DEFER


def test_terminal_tick_original_low_time_preserved():
    result=propose(*custom(tick=60000000,events=[control(59999999)]))
    assert result.tick_index==12000 and result.proposed_low_first_original_at_us==59999999


def test_interruption_requires_new_low_anchor_and_second_frame():
    # Explicitly synthetic future commits, not a runtime state owner.
    first=propose(*custom(tick=15000,events=[control(15000)]))
    interrupted=propose(*custom(tick=25000,control_verdict='ABSENT',health='FAIL',window={'low_first_original_at_us':first.proposed_low_first_original_at_us}))
    assert interrupted.proposal_kind is K.BLOCKED_CLEAR
    fresh=propose(*custom(tick=35000,events=[control(35000)]))
    assert fresh.proposal_kind is K.LOW_START and fresh.proposed_low_first_original_at_us==35000
    later=propose(*custom(tick=50000,events=[control(49999)],window={'low_first_original_at_us':35000}))
    assert later.proposal_kind is K.LOW_PENDING


def test_no_same_tick_commit_can_be_reused_for_high():
    obs,t,p,w,v=case_inputs(9)
    with pytest.raises(ValueError):propose(obs,t,p,replace(w,low_qualified_committed_eval_at_us=40000),v)
    obs,t,p,w,v=case_inputs(14)
    with pytest.raises(ValueError):propose(obs,t,p,replace(w,high_edge_original_at_us=140000,high_edge_committed_eval_at_us=140000),v)


def test_closed_result_and_enum_shapes():
    result=propose(*case_inputs(1))
    assert {f.name for f in fields(result)}=={'tick_index','eval_at_us','pre_state','proposal_kind','proposed_low_first_original_at_us','proposed_low_qualified_committed_eval_at_us','proposed_high_edge_original_at_us','proposed_high_edge_committed_eval_at_us','requires_full_fsm'}
    assert [k.value for k in K]==['DEFER','NO_CHANGE','HOLD_WINDOW','LOW_START','LOW_PENDING','LOW_QUALIFIED','HIGH_EDGE_ELIGIBLE','HIGH_PENDING','HIGH_CONFIRMED','DEMAND_OBSERVED','LOW_DISARM_OBSERVED','BLOCKED_CLEAR','CLEAR_WINDOW']
    assert [k.value for k in H]==['PASS','FAIL','UNRESOLVED']
    assert [k.value for k in C]==['ADMITTED','ABSENT','DENIED','UNRESOLVED']
    for obj in (result,case_inputs(1)[3],case_inputs(1)[4]):
        assert not hasattr(obj,'__dict__')
        for f in fields(obj):
            with pytest.raises(FrozenInstanceError):setattr(obj,f.name,None)
            with pytest.raises(FrozenInstanceError):delattr(obj,f.name)


def test_no_source_or_member_event_reads():
    class Poison:
        def __getitem__(self,key):raise AssertionError('event read')
        def __getattr__(self,key):raise AssertionError('event attribute read')
        def __iter__(self):raise AssertionError('event iteration')
    obs,t,p,w,v=case_inputs(5)
    group=replace(obs.valid_control_groups[0],member_events=(Poison(),)*19999)
    poisoned=replace(obs,source_events=(Poison(),)*19999,rf_events=(Poison(),)*19999,valid_control_groups=(group,))
    assert propose(poisoned,t,p,w,v)==propose(obs,t,p,w,v)


def test_constant_runtime_work_for_real_duplicate_groups():
    counts=[]
    for size in (1,5000):
        args=custom(events=[control(4999,str(i)) for i in range(size)])
        lines=0
        def trace(frame,action,arg):
            nonlocal lines
            if frame.f_code.co_filename==runtime.__file__ and action=='line':lines+=1
            return trace
        previous=sys.gettrace()
        try:
            sys.settrace(trace);result=propose(*args)
        finally:sys.settrace(previous)
        assert result.proposal_kind is K.LOW_START
        counts.append(lines)
    assert counts[0]==counts[1] and counts[0]<500


def test_no_io_or_upstream_reruns(monkeypatch):
    import bb_host_preflight_m0,bb_host_virtual_ticks,bb_host_batch_observations,bb_host_temporal_guard_facts,bb_host_safety_priority_kernel
    args=case_inputs(9);expected=propose(*args)
    def forbidden(*a,**kw):raise AssertionError('prohibited side effect or pipeline rerun')
    with monkeypatch.context() as m:
        for module,names in ((builtins,('open',)),(time,('time','monotonic','sleep')),(random,('random',)),(socket,('socket',)),
            (bb_host_preflight_m0,('validate_wire','mix_m0','mixM0')),(bb_host_virtual_ticks,('iter_virtual_ticks',)),
            (bb_host_batch_observations,('normalize_tick_observations',)),(bb_host_temporal_guard_facts,('evaluate_temporal_guard_facts',)),
            (bb_host_safety_priority_kernel,('assess_safety_priority',))):
            for name in names:m.setattr(module,name,forbidden)
        assert propose(*args)==expected


def test_static_architecture_boundary():
    allowed={'dataclasses','decimal','enum','types','bb_host_batch_observations','bb_host_temporal_guard_facts','bb_host_safety_priority_kernel','qualification'}
    prohibited={'open','print','eval','exec','compile','__import__','float','sleep','time','mixM0','mix_m0','validate_wire','iter_virtual_ticks','normalize_tick_observations','evaluate_temporal_guard_facts','assess_safety_priority','abs'}
    for path in Path(runtime.__file__).parent.glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node,ast.Import):assert all(a.name in allowed for a in node.names)
            if isinstance(node,ast.ImportFrom):assert node.module in allowed
            if isinstance(node,ast.Call):
                name=node.func.id if isinstance(node.func,ast.Name) else getattr(node.func,'attr','')
                assert name not in prohibited


def test_determinism_locale_tz_decimal_and_no_hidden_window(monkeypatch):
    args=case_inputs(11);expected=propose(*args);saved=locale.setlocale(locale.LC_ALL)
    try:
        for name in ('C','English_United States.1252'):
            locale.setlocale(locale.LC_ALL,name)
            for tz in ('UTC0','ICT-7'):
                monkeypatch.setenv('TZ',tz)
                with localcontext() as ctx:
                    ctx.prec=2
                    assert propose(*case_inputs(29)).proposal_kind is K.BLOCKED_CLEAR
                    assert propose(*args)==expected
    finally:locale.setlocale(locale.LC_ALL,saved)
