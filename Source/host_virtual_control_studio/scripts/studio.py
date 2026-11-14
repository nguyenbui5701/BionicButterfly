"""CLI works without Tcl/Tk; GUI adapter is imported only on --gui."""
import argparse
import sys
from bb_host_virtual_control_studio import run_studio_session
try:
    from . import fixtures, offline
except ImportError:
    import fixtures, offline


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline MODEL_ONLY Virtual Control Studio; NO OUTPUT')
    parser.add_argument('--case', choices=tuple(fixtures.CASES), default='nominal')
    parser.add_argument('--text', action='store_true')
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--view', metavar='LOCAL.html')
    parser.add_argument('--proof', metavar='LOCAL.model.json')
    parser.add_argument('--candidate', metavar='LOCAL.model-candidate.jsonl')
    parser.add_argument('--wire', metavar='LOCAL.wire.json')
    args = parser.parse_args(argv)
    try:
        if args.gui:
            if any((args.text, args.view, args.proof, args.candidate, args.wire)):
                raise ValueError('--gui cannot be combined with CLI export/text')
            try:
                from .gui import launch
            except ImportError:
                from gui import launch
            return launch(args.case)
        report = run_studio_session(fixtures.session(args.case), **fixtures.dependencies())
        print(offline.console(report))
        for kind, path in (('html', args.view), ('proof', args.proof), ('candidate', args.candidate), ('wire', args.wire)):
            if path:
                offline.export(report, kind, path)
        return 0 if report.outcome == 'MODEL_REPLAY_COMPLETE' else 2
    except (ValueError, TypeError, OSError, ImportError) as error:
        print('Studio error: ' + str(error) + '; NO OUTPUT', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
