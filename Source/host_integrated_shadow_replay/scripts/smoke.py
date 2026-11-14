"""Exercise all four real integrated demo presets; no prior regression suites."""
from demo import inputs, render
from bb_host_integrated_shadow_replay import run_shadow_replay, ShadowReplayOutcome
from bb_host_integrated_shadow_replay.diagnostic import diagnostic_bytes


def main():
    failures = []
    for preset, count in (("pilot", 8), ("hazard", 6), ("conflict", 4), ("minimal", 2)):
        try:
            values = inputs(preset)
            report = run_shadow_replay(**values)
            assert report.outcome is ShadowReplayOutcome.SHADOW_DIAGNOSTICS_COMPLETE
            assert report.shadow_tick_count == count and report.runtime_authorized is False
            assert report.actual_virtual_output is None and report.physical_output is None
            assert "NO OUTPUT / ARM NOT GRANTED" in render(report, values["scenario_raw"])
            assert diagnostic_bytes(report).endswith(b"\n")
        except Exception as error:
            failures.append((preset, repr(error)))
    for preset, error in failures:
        print(preset, error)
    print(f"Smoke: {4 - len(failures)} PASS, {len(failures)} FAIL")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
