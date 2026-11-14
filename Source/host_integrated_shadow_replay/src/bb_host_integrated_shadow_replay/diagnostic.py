"""Pure, bounded offline diagnostic JSONL; NOT canonical R1 control trace."""
from dataclasses import fields
import json

from .replay import ShadowReplayReport, ShadowTick

MAX_DIAGNOSTIC_BYTES = 16_777_216


def diagnostic_bytes(report: ShadowReplayReport) -> bytes:
    if type(report) is not ShadowReplayReport or type(report.shadow_ticks) is not tuple:
        raise TypeError("expected exact immutable shadow report")
    if not 0 <= len(report.shadow_ticks) <= 12001 or report.shadow_tick_count != len(report.shadow_ticks):
        raise ValueError("invalid shadow count")
    if (report.runtime_authorized is not False or report.requires_full_fsm is not True
            or report.actual_virtual_output is not None or report.physical_output is not None
            or report.canonical_control_trace_sha256 is not None):
        raise ValueError("invalid shadow authority flags")
    chunks = []
    total = 0

    def append(kind, data):
        nonlocal total
        record = dict(data, diagnostic_record_type=kind, authority="NONE",
                      physical_output=None, actual_virtual_output=None)
        raw = (json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
        total += len(raw)
        if total > MAX_DIAGNOSTIC_BYTES:
            raise ValueError("offline shadow diagnostic exceeds 16 MiB quota")
        chunks.append(raw)

    append("shadow_header", dict(format="BB_F0_SHADOW_DIAGNOSTIC_V1", scope="PC_SIM_ONLY",
        preflight_status=report.preflight_status, e2_outcome=report.e2_outcome, e3_outcome=report.e3_outcome,
        preview_label="MATH_PREVIEW_UNTRUSTED", runtime_authorized=False))
    for index, tick in enumerate(report.shadow_ticks):
        if type(tick) is not ShadowTick or tick.tick_index != index:
            raise ValueError("invalid shadow tick")
        if tick.runtime_authorized is not False or tick.actual_virtual_output is not None or tick.physical_output is not None:
            raise ValueError("invalid shadow tick authority flags")
        append("shadow_tick", {f.name: getattr(tick, f.name) for f in fields(tick)})
    append("shadow_terminal", dict(outcome=report.outcome, shadow_tick_count=report.shadow_tick_count,
        blocked_at_tick=report.blocked_at_tick, runtime_authorized=False, requires_full_fsm=True))
    return b"".join(chunks)
