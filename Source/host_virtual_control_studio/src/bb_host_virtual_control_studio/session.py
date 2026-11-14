"""Closed P226 actions to deterministic wire-v2 bytes. No I/O or FSM logic."""
import json
import re
from jsonschema import Draft202012Validator
from ._schema import SCHEMA

MAX_INPUT = 2_097_152
MAX_OUTPUT = 16_777_216
KINDS = ('RF_HEALTHY', 'RF_LOST', 'RF_UNKNOWN', 'CONTROL_VALID',
         'CONTROL_INVALID', 'RESET', 'ACK', 'CATASTROPHE')


class SessionError(ValueError):
    """Invalid studio input; never a successful model result."""


def _reject(value):
    raise SessionError('integer JSON tokens required; nonfinite/decimal rejected')


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise SessionError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def _shape(value, depth=0):
    if depth > 16:
        raise SessionError('session nesting quota')
    if type(value) is str:
        value.encode('utf-8', 'strict')
    elif type(value) is dict:
        for key, child in value.items():
            _shape(key, depth + 1)
            _shape(child, depth + 1)
    elif type(value) is list:
        for child in value:
            _shape(child, depth + 1)


def parse_session(raw: bytes) -> dict:
    if type(raw) is not bytes:
        raise TypeError('session requires exact bytes')
    if len(raw) > MAX_INPUT or raw.startswith(b'\xef\xbb\xbf'):
        raise SessionError('session quota or BOM')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                           parse_float=_reject, parse_constant=_reject)
        _shape(value)
        error = next(Draft202012Validator(SCHEMA).iter_errors(value), None)
        if error is not None:
            raise SessionError('closed P226 schema violation at ' + '/'.join(map(str, error.absolute_path)))
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', value['session_id']):
            raise SessionError('invalid session identifier')
        if type(value['duration_us']) is not int:
            raise SessionError('duration must be integer, not boolean')
        seen, last = set(), 0
        for action in value['actions']:
            at = action['at_us']
            if type(at) is not int or not last <= at <= value['duration_us'] or at == 0:
                raise SessionError('invalid original action time/order')
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', action['id']) or action['id'] in seen:
                raise SessionError('invalid/duplicate action ID')
            if action['kind'] == 'CONTROL_VALID':
                if any(type(action[k]) is not int for k in ('flap_micro', 'steer_micro')):
                    raise SessionError('demands require exact integers')
            seen.add(action['id'])
            last = at
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise SessionError('malformed UTF-8/JSON or nesting quota') from error


def encode_session(value: dict) -> bytes:
    raw = json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode('ascii')
    parse_session(raw)
    return raw


def _millionths(value):
    # Exact signed decimal token construction; independent of Decimal context.
    magnitude = abs(value)
    whole, remainder = divmod(magnitude, 1_000_000)
    return ('-' if value < 0 else '') + str(whole) + ('.' + f'{remainder:06d}'.rstrip('0') if remainder else '')


def session_to_wire_v2(raw_actions: bytes) -> bytes:
    session = parse_session(raw_actions)
    events = ['{"event_id":"studio_boot","event_at_us":0,"type":"BOOT","payload":{}}']
    simple = {'RESET': 'SIM_RESET', 'ACK': 'SIM_ACK_FAULT', 'CATASTROPHE': 'SIM_CATASTROPHIC_FAULT'}
    for action in session['actions']:
        kind = action['kind']
        if kind.startswith('RF_'):
            event_type = 'SIM_RF_STATUS'
            payload = json.dumps(dict(rf_health=kind[3:], rf_provenance='INJECTED_SIM'), separators=(',', ':'))
        elif kind == 'CONTROL_VALID':
            event_type = 'SIM_CONTROL_FRAME'
            payload = ('{"uart_frame_status":"VALID","map_revision":"sim-map-v1","arm_switch":'
                       + ('true' if action['arm_switch'] else 'false') + ',"flap_demand":'
                       + _millionths(action['flap_micro']) + ',"steering_demand":'
                       + _millionths(action['steer_micro']) + '}')
        elif kind == 'CONTROL_INVALID':
            event_type, payload = 'SIM_CONTROL_FRAME', '{"uart_frame_status":"INVALID"}'
        else:
            event_type, payload = simple[kind], '{}'
        # Prefix distinguishes user action 'studio_boot' from mandatory BOOT.
        # P226 IDs can be 64 bytes, so use an injective numeric event ID instead.
        identity = f'action_{len(events):05d}'
        events.append('{"event_id":' + json.dumps(identity) + ',"event_at_us":' + str(action['at_us'])
                      + ',"type":' + json.dumps(event_type) + ',"payload":' + payload + '}')
    wire = ('{"schema_version":2,"scenario_id":' + json.dumps('studio_' + session['session_id'])
            + ',"context":"PC_SIM","provenance":"SIM_ONLY","config_id":"sim-only-c0-v1",'
            '"clock":{"start_us":0,"step_us":5000},"duration_us":' + str(session['duration_us'])
            + ',"events":[' + ','.join(events) + ']}').encode('ascii')
    if len(wire) > MAX_INPUT:
        raise SessionError('generated wire-v2 exceeds input byte quota')
    return wire
