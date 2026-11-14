"""Offline CLI adapter. Console/file diagnostics are not actuator publication."""
import argparse
from decimal import Decimal
import json
import os
from pathlib import Path, PureWindowsPath
import sys
import tempfile

from bb_host_integrated_shadow_replay import run_shadow_replay, ShadowReplayOutcome
from bb_host_integrated_shadow_replay.diagnostic import diagnostic_bytes
try:
    from .fixtures import inputs
except ImportError:
    from fixtures import inputs


def render(report, scenario_raw):
    lines = ["PC_SIM_ONLY / NO_OUTPUT / NOT A FLIGHT TEST",
             "NO OUTPUT / ARM NOT GRANTED | MATH_PREVIEW_UNTRUSTED",
             "HEALTHY* = observed, NOT committed/authorized; SELF_TEST = UNRESOLVED_FULL_FSM",
             "T(ms) | RF | INPUT (original us) | E1 STATE / COMMIT | ARM REQUEST | PREVIEW L/R (micro) | OUTPUT"]
    # Reporting-only view of the same frozen demo bytes. Never feeds the runner.
    events = iter(json.loads(scenario_raw, parse_float=Decimal)["events"])
    pending = next(events, None)
    for tick in report.shadow_ticks:
        observed = []
        while pending is not None and pending["event_at_us"] <= tick.eval_at_us:
            event = pending
            body = event["payload"]
            detail = event["type"]
            if detail == "SIM_CONTROL_FRAME" and body["uart_frame_status"] == "VALID":
                detail = f"F={body['flap_demand']} S={body['steering_demand']}"
            elif detail == "SIM_CONTROL_FRAME":
                detail = "INVALID"
            observed.append(f"{event['event_id']}@{event['event_at_us']}:{detail}")
            pending = next(events, None)
        rf = "HEALTHY*" if tick.rf_evidence.value == "HEALTHY_CURRENT" else tick.rf_evidence.value
        preview = "--" if tick.preview_left_micro is None else f"{tick.preview_left_micro}/{tick.preview_right_micro}"
        if tick.preview_clip_tags:
            preview += " " + ",".join(tick.preview_clip_tags)
        arm = "REQUESTED_NOT_GRANTED" if tick.arm_switch_requested else "NONE"
        lines.append(f"{tick.eval_at_us // 1000:5} | {rf} | {'; '.join(observed) or 'NONE'} | "
            f"{tick.test_state_after.value} / {tick.e1_outcome.value} | {arm} | {preview} | INHIBITED")
        lines.append(f"      control={tick.control_evidence.value}; reasons={','.join(r.value for r in tick.triage_reasons)}")
    lines.append(f"{report.outcome.value}: {report.shadow_tick_count} acknowledged shadow ticks; blocked_at_tick={report.blocked_at_tick}")
    lines.append("runtime_authorized=False; requires_full_fsm=True; actual_virtual_output=None; physical_output=None")
    return "\n".join(lines)


def write_offline(report, destination):
    """Serialize fully under quota, then atomically replace a local JSONL file."""
    raw_path = str(destination)
    win = PureWindowsPath(raw_path)
    if raw_path.startswith(("\\\\", "//")) or win.is_reserved() or ":" in raw_path[2:]:
        raise ValueError("only ordinary local JSONL paths are supported")
    target = Path(destination).absolute()
    if target.suffix.lower() != ".jsonl":
        raise ValueError("offline report path must end in .jsonl")
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError("offline report path must not traverse links")
    raw = diagnostic_bytes(report)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=".shadow-", suffix=".tmp", dir=target.parent, delete=False) as handle:
            temporary = Path(handle.name)
            if handle.write(raw) != len(raw):
                raise OSError("short offline report write")
            handle.flush()
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="TEST_ONLY PC shadow replay; NO OUTPUT")
    parser.add_argument("--case", choices=("pilot", "hazard", "conflict", "minimal"), default="pilot")
    parser.add_argument("--jsonl", help="optional local offline diagnostic .jsonl path")
    args = parser.parse_args(argv)
    try:
        values = inputs(args.case)
        report = run_shadow_replay(**values)
        console = render(report, values["scenario_raw"])
        if args.jsonl:
            write_offline(report, args.jsonl)
        print(console)
        return 0 if report.outcome is ShadowReplayOutcome.SHADOW_DIAGNOSTICS_COMPLETE else 2
    except (OSError, TypeError, ValueError) as error:
        print(f"TEST_ONLY INTEGRATION/REPORT ERROR: {error}; NO OUTPUT", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
