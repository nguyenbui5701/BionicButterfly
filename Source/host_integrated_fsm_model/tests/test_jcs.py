"""Independent RFC8785/V8 vectors, not self-consistency alone (N18)."""
from dataclasses import asdict
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

import pytest
from jsonschema import Draft202012Validator
from bb_host_integrated_fsm_model import jcs,trace,run_fsm_model
from scripts.fixtures import frozen_bytes,inputs

# Numeric facts from RFC8785 Appendix B, IEEE754 hex -> canonical decimal.
# https://www.rfc-editor.org/rfc/rfc8785.html#appendix-B
VECTORS=[
('0000000000000000','0'),('8000000000000000','0'),('0000000000000001','5e-324'),
('8000000000000001','-5e-324'),('7fefffffffffffff','1.7976931348623157e+308'),
('ffefffffffffffff','-1.7976931348623157e+308'),('4340000000000000','9007199254740992'),
('c340000000000000','-9007199254740992'),('4430000000000000','295147905179352830000'),
('44b52d02c7e14af5','9.999999999999997e+22'),('44b52d02c7e14af6','1e+23'),
('44b52d02c7e14af7','1.0000000000000001e+23'),('444b1ae4d6e2ef4e','999999999999999700000'),
('444b1ae4d6e2ef4f','999999999999999900000'),('444b1ae4d6e2ef50','1e+21'),
('3eb0c6f7a0b5ed8c','9.999999999999997e-7'),('3eb0c6f7a0b5ed8d','0.000001'),
('41b3de4355555553','333333333.3333332'),('41b3de4355555554','333333333.33333325'),
('41b3de4355555555','333333333.3333333'),('41b3de4355555556','333333333.3333334'),
('41b3de4355555557','333333333.33333343'),('becbf647612f3696','-0.0000033333333333333333'),
('43143ff3c1cb0959','1424953923781206.2')]


def node(values):
    result=subprocess.run(['node','scripts/jcs_reference.js'],input=json.dumps(values,ensure_ascii=True),
                          capture_output=True,text=True,encoding='utf-8',check=True)
    return json.loads(result.stdout)


@pytest.mark.parametrize('bits,expected',VECTORS,ids=[v[0] for v in VECTORS])
def test_N18_rfc_number_vector(bits,expected):
    value=struct.unpack('>d',bytes.fromhex(bits))[0]
    assert jcs.dumps(value)==expected.encode()


def test_N18_independent_v8_all_vectors_and_generated_binary64():
    values=[struct.unpack('>d',bytes.fromhex(bits))[0] for bits,_ in VECTORS]
    seed=0x731a39c57f018fab
    while len(values)<4120:
        seed=(seed*6364136223846793005+1442695040888963407)&((1<<64)-1)
        value=struct.unpack('>d',seed.to_bytes(8,'big'))[0]
        if math.isfinite(value): values.append(value)
    expected=node(values)
    comparisons=[]
    for value,reference in zip(values,expected,strict=True):
        encoded=jcs.dumps(value).decode()
        assert encoded==reference,(value,reference,encoded)
        comparisons.append(dict(ieee754=struct.pack('>d',value).hex(),expected_v8=reference,result='PASS'))
    Path('evidence/jcs-vectors.json').write_text(json.dumps(dict(
        source='https://www.rfc-editor.org/rfc/rfc8785.html#appendix-B',
        reference_engine=subprocess.check_output(['node','--version']).decode().strip(),
        vector_count=len(comparisons),comparisons=comparisons),indent=2)+'\n',encoding='utf-8',newline='\n')


def test_N18_unicode_order_controls_and_no_normalization():
    value={'\u20ac':'euro','\r':'return','\ufb33':'hebrew','1':'one','\U0001f600':'emoji','\u0080':'control','\u00f6':'o'}
    assert list(json.loads(jcs.dumps(value)))==['\r','1','\u0080','\u00f6','\u20ac','\U0001f600','\ufb33']
    examples=[value,{'2':0,'10':0,'\U0001f600':{'\ufb33':[1e-6,1e21]}},
              ''.join(chr(i) for i in range(32))+'"\\/',{'é':'é','e\u0301':'e\u0301'},[-0.0,0.002,4.5,1e30]]
    assert [jcs.dumps(x).decode() for x in examples]==node(examples)
    assert jcs.dumps('é')!=jcs.dumps('e\u0301')
    assert jcs.dumps('\b\t\n\f\r\x0f')==b'"\\b\\t\\n\\f\\r\\u000f"'


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),-float('inf'),'\ud800',{'\udfff':0},2**53,-2**53,Decimal('0.1'),{1:'bad'},object()])
def test_N18_invalid_ijson_values(bad):
    with pytest.raises((TypeError,ValueError)): jcs.dumps(bad)


@pytest.mark.parametrize('raw',[b'{"a":1,"a":2}',b'{"a":{"b":1,"b":2}}',b'NaN',b'Infinity',b'1e9999',b'1e-9999',b'"\\ud800"',b'\xef\xbb\xbf{}',b'\xff',b'9007199254740993',b'['*18+b'0'+b']'*18])
def test_N18_strict_decode(raw):
    with pytest.raises((TypeError,ValueError)): jcs.loads(raw)


def test_N18_p210_policy_and_candidate_shapes_independent():
    reference=frozen_bytes('Design/fixtures/P210_MINIMAL_DESIGN_TRACE.jsonl')
    assert b''.join(jcs.dumps(jcs.loads(line))+b'\n' for line in reference.splitlines())==reference
    policy=frozen_bytes('Design/contracts/SIM_POLICY_22A_R1.canonical.json')
    assert jcs.dumps(jcs.loads(policy))==policy
    schema=json.loads(frozen_bytes('Design/contracts/G0A1_TRACE_RECORDS_R11_CANDIDATE.schema.json'))
    validator=Draft202012Validator(schema)
    for preset in ('nominal','recovery','conflict'):
        r=run_fsm_model(**inputs(preset))
        records=[jcs.loads(line) for line in r.candidate_trace.splitlines()]
        for record in records: validator.validate(record)
        assert [jcs.dumps(x).decode() for x in records]==node(records)
        assert records[0]['engine_revision']==trace.ENGINE and 'MODEL_ONLY' in trace.ENGINE
        assert records[0]['engine_revision']!='G0A1_DESIGN_REFERENCE_1'
        assert records[-1]['run_status']=='FAILED' and records[-1]['fault_codes']==['E_OWNER_DENIED']
        assert records[-1]['evaluated_tick_count']==len(records)-2==r.model_tick_count
        for i,row in enumerate(records[1:-1]):
            assert row['tick_index']==i and row['eval_at_us']==i*5000
            assert row['state_before']==('BOOT' if i==0 else records[i]['state_after'])
            assert row['output_allowed'] is False and row['input_mode']=='NONE' and row['mixer_clip_tags']==[]
            assert all(row[k] is None for k in ('requested_flap_micro','requested_steer_micro','left_micro_effort','right_micro_effort'))
        h=records[0]
        identity=dict(domain='BIONICBUTTERFLY_G0A1_REPLAY_V1',**{k:h[k] for k in (
            'scenario_digest','policy_digest','engine_revision','scheduler_revision','result_contract_version','trace_format_version')})
        assert h['replay_identity']==hashlib.sha256(node([identity])[0].encode()).hexdigest()


def test_N17_real_serializer_error_and_quota(monkeypatch):
    original=trace.jcs.dumps
    def fail(value):
        if isinstance(value,dict) and value.get('tick_index')==29: raise ValueError('TEST serializer error')
        return original(value)
    monkeypatch.setattr(trace.jcs,'dumps',fail)
    r=run_fsm_model(**inputs('nominal'))
    assert r.outcome.value=='MODEL_EVIDENCE_INCOMPLETE' and r.model_tick_count==29
    monkeypatch.setattr(trace.jcs,'dumps',original)
    monkeypatch.setattr(trace,'MAX_BYTES',1)
    assert run_fsm_model(**inputs('nominal')).model_tick_count==0
