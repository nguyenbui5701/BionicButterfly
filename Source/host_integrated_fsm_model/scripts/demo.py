"""Offline adapter only; no server or device integration."""
import argparse
import os
from pathlib import Path, PureWindowsPath
import sys
import tempfile

from bb_host_integrated_fsm_model import run_fsm_model, ModelOutcome
from bb_host_integrated_fsm_model.viewer import render_console, render_html, MAX_BYTES
try:
    from .fixtures import inputs
except ImportError:
    from fixtures import inputs


def write_offline(raw, path):
    if type(raw) is not bytes or len(raw)>MAX_BYTES:
        raise ValueError("offline file byte quota/type")
    name=str(path)
    if name.startswith(("\\\\","//")) or PureWindowsPath(name).is_reserved() or ":" in name[2:]:
        raise ValueError("ordinary local report file required")
    target=Path(path).absolute()
    if target.suffix.lower() not in (".html", ".jsonl") or any(p.is_symlink() for p in (target,*target.parents)):
        raise ValueError("local non-link HTML/JSONL report required")
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(mode="wb",prefix=".model-",suffix=".tmp",dir=target.parent,delete=False) as handle:
            temporary=Path(handle.name)
            if handle.write(raw)!=len(raw):
                raise OSError("short offline report write")
            handle.flush()
        os.replace(temporary,target)
        temporary=None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser=argparse.ArgumentParser(description="MODEL_ONLY offline FSM replay; NO_ACTUATOR_OUTPUT")
    parser.add_argument("--case",choices=("nominal","recovery","conflict"),default="nominal")
    parser.add_argument("--view",metavar="LOCAL.html")
    parser.add_argument("--candidate",metavar="LOCAL.model-candidate.jsonl",help="DESIGN_CONFORMANCE_ONLY bytes; not runtime trace")
    args=parser.parse_args(argv)
    try:
        report=run_fsm_model(**inputs(args.case))
        console=render_console(report)
        if args.view:
            if Path(args.view).suffix.lower()!=".html": raise ValueError("viewer must end .html")
            write_offline(render_html(report),args.view)
        if args.candidate:
            if not args.candidate.endswith('.model-candidate.jsonl'):
                raise ValueError("candidate filename must end .model-candidate.jsonl")
            if report.outcome is not ModelOutcome.MODEL_REPLAY_COMPLETE:
                raise ValueError("no complete candidate export from blocked/incomplete model")
            write_offline(report.candidate_trace,args.candidate)
        print(console)
        return 0 if report.outcome is ModelOutcome.MODEL_REPLAY_COMPLETE else 2
    except (TypeError,ValueError,OSError) as error:
        print(f"MODEL diagnostic failure: {error}; NO_ACTUATOR_OUTPUT",file=sys.stderr)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
