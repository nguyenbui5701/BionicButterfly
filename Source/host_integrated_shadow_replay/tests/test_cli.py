import json
from pathlib import Path
import pytest
from bb_host_integrated_shadow_replay import run_shadow_replay
from bb_host_integrated_shadow_replay import diagnostic
from scripts import demo
from scripts.fixtures import inputs


@pytest.mark.parametrize("preset,count", [("pilot",8), ("hazard",6), ("conflict",4), ("minimal",2)])
def test_demo_console_and_jsonl(preset, count, capsys, tmp_path):
    target = tmp_path / "report.jsonl"
    assert demo.main(["--case",preset,"--jsonl",str(target)]) == 0
    console = capsys.readouterr().out
    assert "PC_SIM_ONLY / NO_OUTPUT / NOT A FLIGHT TEST" in console
    assert "UNRESOLVED_FULL_FSM" in console and f"{count} acknowledged shadow ticks" in console
    records = [json.loads(line) for line in target.read_bytes().splitlines()]
    assert len(records) == count+2
    assert all(r["authority"]=="NONE" for r in records)
    if preset == "pilot":
        assert "200000/600000" in console and "REQUESTED_NOT_GRANTED" in console and "LOST_CURRENT" in console


@pytest.mark.parametrize("failure", ["quota", "serialization", "replace", "permission", "short_write"])
def test_atomic_report_failures_preserve_previous_file(failure, monkeypatch, tmp_path):
    report = run_shadow_replay(**inputs("pilot"))
    target = tmp_path / "report.jsonl"
    target.write_bytes(b"previous report\n")
    def fail(*args, **kwargs):
        raise OSError("TEST_ONLY report failure")
    if failure == "quota":
        monkeypatch.setattr(diagnostic, "MAX_DIAGNOSTIC_BYTES", 1)
    elif failure == "serialization":
        monkeypatch.setattr(diagnostic.json, "dumps", fail)
    elif failure == "replace":
        monkeypatch.setattr(demo.os, "replace", fail)
    elif failure == "permission":
        monkeypatch.setattr(demo.tempfile, "NamedTemporaryFile", fail)
    else:
        original = demo.tempfile.NamedTemporaryFile
        class ShortWrite:
            def __enter__(self):
                self.file = original(mode="wb", dir=tmp_path, delete=False)
                self.name = self.file.name
                return self
            def write(self, data):
                return self.file.write(data[:-1])
            def __exit__(self, *args):
                self.file.close()
        monkeypatch.setattr(demo.tempfile, "NamedTemporaryFile", lambda **kw: ShortWrite())
    with pytest.raises((OSError, ValueError)):
        demo.write_offline(report, target)
    assert target.read_bytes() == b"previous report\n"
    assert list(tmp_path.iterdir()) == [target]


@pytest.mark.parametrize("path", [r"\\server\share\report.jsonl", "//server/share/report.jsonl", "COM1", "report.jsonl:stream", "report.txt"])
def test_forbidden_output_paths(path):
    with pytest.raises(ValueError):
        demo.write_offline(run_shadow_replay(**inputs("minimal")), path)


def test_cli_failure_no_success_console(monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise ValueError("TEST_ONLY boundary error")
    monkeypatch.setattr(demo, "run_shadow_replay", fail)
    assert demo.main(["--case","minimal"]) == 1
    captured = capsys.readouterr()
    assert captured.out == "" and "NO OUTPUT" in captured.err
