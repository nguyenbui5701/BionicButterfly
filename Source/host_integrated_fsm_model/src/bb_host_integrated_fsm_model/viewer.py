"""Pure offline HTML/console rendering of acknowledged MODEL records only."""
import base64
from hashlib import sha256
from html import escape
import json

from .model import ModelReplayReport

BANNER = "MODEL_ONLY / RUNTIME_NOT_PROVISIONED / NO_ACTUATOR_OUTPUT"
MAX_BYTES = 16_777_216
_CSS = """body{margin:0;background:#0b1220;color:#e4edf8;font:16px system-ui,sans-serif}main{max-width:1120px;margin:32px auto;padding:20px}h1{margin-bottom:8px}.notice{color:#ffc66d;border-left:4px solid;padding:12px;background:#1c2534}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.card{background:#172235;border:1px solid #314057;border-radius:12px;padding:22px;margin:18px 0}.bar{height:22px;background:#344055;border-radius:8px;overflow:hidden}.fill{height:100%;width:0;background:#65d6c2}button,input{accent-color:#65d6c2}button{padding:9px 16px;background:#203a50;color:white;border:1px solid #688099;border-radius:6px;margin:6px}input{width:95%}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{width:100%;border-collapse:collapse}td,th{padding:10px;text-align:left;border-bottom:1px solid #354056}.muted{color:#a8b9cf}strong{color:#73e3d1}@media(max-width:700px){.grid{display:block}}"""
_JS = """'use strict';
const data=JSON.parse(document.getElementById('model-data').textContent);
const slider=document.getElementById('tick'); let timer=null;
function show(){const r=data[Number(slider.value)]; if(!r)return;
 document.getElementById('time').textContent=(r[0]/1000)+' ms';
 document.getElementById('state').textContent=r[1];
 document.getElementById('rf').textContent=r[2];
 document.getElementById('details').textContent='INPUT F/S micro: '+r[6]+' / '+r[7]+'\\nARM switch request: '+r[8]+' (operational ARM NOT GRANTED)\\nModel mode: '+r[5]+'\\nLOW qualified at: '+r[9]+' us; HIGH edge: '+r[10]+' us\\nModel reasons: '+r[11].join(', ')+'\\nOriginal event times: '+r[12].join(', ')+' us\\nCausal IDs: '+r[13].join(', ')+'\\nD2: '+r[14].join(', ');
 ['left','right'].forEach((side,i)=>{const v=r[i+3]; document.getElementById(side).textContent=v===null?'INHIBITED':String(v)+' micro / '+(v/1000000).toFixed(6)+' dimensionless'; document.getElementById(side+'-bar').style.width=(v===null?0:v/10000)+'%';});
}
slider.max=Math.max(0,data.length-1); slider.addEventListener('input',show);
document.getElementById('play').addEventListener('click',()=>{if(timer!==null)return;timer=setInterval(()=>{if(Number(slider.value)>=data.length-1){clearInterval(timer);timer=null;return;}slider.value=Number(slider.value)+1;show();},100);});
document.getElementById('pause').addEventListener('click',()=>{clearInterval(timer);timer=null;});
document.getElementById('start').addEventListener('click',()=>{slider.value=0;show();});
show();"""


def _checked(report):
    if type(report) is not ModelReplayReport or type(report.model_ticks) is not tuple:
        raise TypeError("exact immutable model report required")
    if (report.runtime_authorized is not False or report.output_allowed is not False
            or report.actual_virtual_output is not None or report.physical_output is not None
            or report.control_trace_sha256 is not None or len(report.model_ticks) > 12001
            or len(report.model_ticks) != report.model_tick_count):
        raise ValueError("invalid model report boundary")


def render_console(report):
    _checked(report)
    lines=[BANNER, "Counterfactual model effort only; not servo position, PWM, lift or flight readiness.",
           "T(us) | model_state | RF / control | ARM request | model effort L/R | mode | model reasons"]
    for r in report.model_ticks:
        pair="--" if r.model_effort_left_micro is None else f"{r.model_effort_left_micro}/{r.model_effort_right_micro}"
        lines.append(f"{r.eval_at_us:7} | {r.model_state.value} | {r.rf_effective}/{r.control_evidence} | "
                     f"{r.arm_switch_requested} (NOT GRANTED) | {pair} | {r.model_input_mode} | {','.join(r.model_reasons)}")
        lines.append(f"        INPUT F/S micro={r.observed_flap_micro}/{r.observed_steer_micro}; original_us={r.original_event_times_us}; "
                     f"LOW_qualified={r.model_snapshot.low_qualified_eval_us}; HIGH_edge={r.model_snapshot.high_edge_at_us}; IDs={r.causal_event_ids}")
    lines.append(f"{report.outcome.value}: {report.model_tick_count} MODEL commits; blocked_at_tick={report.blocked_at_tick}; {report.diagnostic or ''}")
    lines.append(f"F0 comparator: {report.shadow_comparator_outcome}, {report.shadow_comparator_tick_count} ticks (separate, no authority)")
    lines.append("runtime_authorized=False; output_allowed=False; actual_virtual_output=None; physical_output=None; control_trace_sha256=None")
    raw="\n".join(lines)
    if len(raw.encode()) > MAX_BYTES:
        raise ValueError("console diagnostic quota")
    return raw


def render_html(report):
    _checked(report)
    data=[]
    for r in report.model_ticks:
        data.append([r.eval_at_us,r.model_state.value,r.rf_effective,r.model_effort_left_micro,
            r.model_effort_right_micro,r.model_input_mode,r.observed_flap_micro,r.observed_steer_micro,
            r.arm_switch_requested,r.model_snapshot.low_qualified_eval_us,r.model_snapshot.high_edge_at_us,
            r.model_reasons,r.original_event_times_us,r.causal_event_ids,r.triage_reasons])
    payload=json.dumps(data,ensure_ascii=True,separators=(",", ":"),allow_nan=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    js_hash=base64.b64encode(sha256(_JS.encode()).digest()).decode()
    css_hash=base64.b64encode(sha256(_CSS.encode()).digest()).decode()
    # Inline style attributes are limited to locally calculated effort bar width;
    # no state/control endpoint or message bridge exists in this standalone file.
    csp=f"default-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; script-src 'sha256-{js_hash}'; style-src 'sha256-{css_hash}'; style-src-attr 'unsafe-inline'"
    doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="{csp}"><title>TASK-013 · Offline FSM model</title><style>{_CSS}</style></head><body><main>
<p class="muted">BIONIC BUTTERFLY / TASK-013 / OFFLINE REPLAY</p><h1>FSM model &amp; effort timeline</h1>
<p class="notice">{BANNER}<br>Counterfactual dimensionless effort. Not servo angles, wing pose, lift or a flight test. Operational ARM is never granted.</p>
<p>Result: <strong>{escape(report.outcome.value)}</strong> · {report.model_tick_count} acknowledged model ticks · {escape(report.diagnostic or '')}</p>
<div class="card"><label for="tick">Read-only playback: <strong id="time">--</strong></label><p><input id="tick" type="range" min="0" max="0" value="0"></p><button id="start">Start</button><button id="play">Play timeline</button><button id="pause">Pause</button><p>model_state: <strong id="state">--</strong> · RF: <span id="rf">--</span></p></div>
<div class="grid"><section class="card"><h2>Left model effort</h2><p id="left">--</p><div class="bar"><div id="left-bar" class="fill"></div></div></section><section class="card"><h2>Right model effort</h2><p id="right">--</p><div class="bar"><div id="right-bar" class="fill"></div></div></section></div>
<div class="card"><pre id="details"></pre></div><p class="muted">Viewer changes only the displayed index in this acknowledged recording. No model input, core callbacks, network or device access.</p><p>runtime_authorized=False · output_allowed=False · actual_virtual_output=None · physical_output=None · control_trace_sha256=None</p>
<p>{escape(report.candidate_label)} / DESIGN_CONFORMANCE_ONLY</p><noscript>Enable local JavaScript to inspect the immutable timeline. The CLI provides a text alternative.</noscript>
<script type="application/json" id="model-data">{payload}</script><script>{_JS}</script></main></body></html>'''
    raw=doc.encode("utf-8")
    if len(raw)>MAX_BYTES:
        raise ValueError("offline HTML diagnostic quota")
    return raw
