"""Bounded offline reports. File I/O stays outside the pure studio package."""
from dataclasses import asdict
import json
import os
from pathlib import Path, PureWindowsPath
import tempfile
from bb_host_integrated_fsm_model.viewer import render_console, render_html
from bb_host_virtual_control_studio.studio import BANNER, EFFORT_LABEL
from bb_host_virtual_control_studio.session import MAX_OUTPUT


def console(report):
    text = BANNER + '\n' + EFFORT_LABEL + '\nStudio: ' + report.outcome + '\n'
    text += render_console(report.model) if report.model else (report.diagnostic or 'No acknowledged model ticks')
    if len(text.encode()) > MAX_OUTPUT:
        raise ValueError('diagnostic quota')
    return text


def html(report):
    if report.model is None:
        raise ValueError('no model recording to export')
    return render_html(report.model)


def proof(report):
    value = dict(format='BB_P226_OFFLINE_MODEL_REPORT_V1', authority='NONE',
                 label='MODEL_TRACE_CANDIDATE_NOT_OPERATIONAL', outcome=report.outcome,
                 diagnostic=report.diagnostic, boundary=asdict(report.boundary),
                 model_ticks=[asdict(t) for t in report.model_ticks],
                 candidate_trace_sha256=report.model.candidate_trace_sha256 if report.model else None)
    raw = json.dumps(value, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode()
    if len(raw) > MAX_OUTPUT:
        raise ValueError('diagnostic quota')
    return raw


def write_local(raw, path, suffix):
    if type(raw) is not bytes or len(raw) > MAX_OUTPUT:
        raise ValueError('invalid report type/quota')
    name = str(path)
    win = PureWindowsPath(name)
    if name.startswith(('\\\\', '//')) or win.is_reserved() or ':' in name[2:]:
        raise ValueError('ordinary local path required')
    target = Path(path).absolute()
    if not name.endswith(suffix) or any(p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()) for p in (target, *target.parents)):
        raise ValueError('invalid extension or linked destination')
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=target.parent, prefix='.studio-', delete=False) as stream:
            temporary = Path(stream.name)
            if stream.write(raw) != len(raw):
                raise OSError('short report write')
            stream.flush()
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def export(report, kind, path):
    # Never overwrite a success artifact with an incomplete/invalid run.
    if report.outcome != 'MODEL_REPLAY_COMPLETE':
        raise ValueError('blocked/incomplete session cannot export a completed recording')
    if kind == 'html':
        raw, suffix = html(report), '.html'
    elif kind == 'proof':
        raw, suffix = proof(report), '.model.json'
    elif kind == 'candidate':
        raw, suffix = report.model.candidate_trace, '.model-candidate.jsonl'
    elif kind == 'wire':
        raw, suffix = report.wire_v2, '.wire.json'
    else:
        raise ValueError('unknown export kind')
    write_local(raw, path, suffix)
