"""Developer verification/evidence only; no simulator or runtime entrypoint."""

import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import subprocess
import time
import xml.etree.ElementTree as ET

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
BASELINE = "ca457f784975c2d0959b1baf988483fa042f5c67"
EVIDENCE = PACKAGE / "evidence"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def verify_provenance():
    manifest = json.loads((ROOT / "Design/P214_TASK002_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["source_baseline_commit"] == BASELINE
    for row in manifest["files"]:
        raw = (ROOT / row["path"]).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"]
        assert blob == row["git_blob_sha1"], row["path"]
    paths = [
        "Design/07_AI_CODING_RULES.md", "Design/10_SA_OPERATING_RULES.md", "Design/11_HANDOFF_PR_WORKFLOW.md",
        "Design/115_G0A1_APPROVED_ATOMIC_SAFETY_CONTRACT_R1.md",
        "Design/116_G0A1_APPROVED_POLICY_DIGEST_AND_TRUST_R1.md",
        "Design/118_G0A1_REPLAY_AND_OUTPUT_TRANSACTION_R1.md",
        "Design/132_R11_SCENARIO_WIRE_V2_CLOSED_EVENT_SCHEMA_CANDIDATE.md",
        "Design/141_G0A1_R11_AUTHORITATIVE_CONTRACT_HIERARCHY.md",
        "Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json",
        "Design/fixtures/P210_MINIMAL_WIRE_V2.json", "Design/fixtures/P210_NOMINAL_M0_WIRE_V2.json",
        "Source/host_preflight_m0/tests/conftest.py", "Source/host_preflight_m0/pyproject.toml",
    ]
    paths += [p.relative_to(ROOT).as_posix() for p in
              (ROOT / "Source/host_preflight_m0/src/bb_host_preflight_m0").glob("*.py")]
    rows = []
    for path in sorted(paths):
        expected = git("rev-parse", BASELINE + ":" + path).decode().strip()
        actual = git("hash-object", path).decode().strip()
        assert actual == expected, path
        rows.append(dict(path=path, git_blob_sha1=expected, result="MATCH"))
    record = dict(baseline=BASELINE, branch=git("branch", "--show-current").decode().strip(),
                  pinned_files=rows, release_files=manifest["files"], release_result="5/5 MATCH")
    (EVIDENCE / "baseline.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Provenance: {len(rows)} pinned files and 5 release artifacts MATCH.", flush=True)


def main():
    EVIDENCE.mkdir(exist_ok=True)
    preserved = ROOT / "Source/host_preflight_m0/evidence/baseline.json"
    preserved_hash = hashlib.sha256(preserved.read_bytes()).hexdigest()
    verify_provenance()
    python = str(PACKAGE / ".venv/Scripts/python.exe")
    test_python = str(PACKAGE / ".test-env/Scripts/python.exe")
    preflight_wheel = "../host_preflight_m0/dist/bb_host_preflight_m0-0.1.0-py3-none-any.whl"
    commands = []

    def run(name, executable, *args):
        command = [executable, *args]
        result = subprocess.run(command, cwd=PACKAGE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace")
        output = result.stdout.replace(str(ROOT), "<REPOSITORY>").replace(ROOT.as_posix(), "<REPOSITORY>")
        output = output.replace(str(Path.home()), "<USERPROFILE>")
        (EVIDENCE / (name + ".log")).write_text(output, encoding="utf-8")
        commands.append(dict(name=name, command=[x.replace(str(ROOT), "<REPOSITORY>") for x in command],
                             exit_code=result.returncode, log=name + ".log"))
        (EVIDENCE / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
        print(f"{name}: exit={result.returncode}", flush=True)
        if result.returncode:
            print(output, flush=True)
            raise SystemExit(result.returncode)

    run("install", python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps",
        "--no-build-isolation", "-e", ".")
    run("compile", python, "-m", "compileall", "-q", "src", "tests", "scripts")
    run("tests", python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml=evidence/tests.xml")
    run("smoke", python, "scripts/smoke.py")
    run("dependencies", python, "-m", "pip", "check")
    # -B and no cache provider keep the read-only TASK-001 tree unchanged.
    run("task001-regression", str(ROOT / "Source/host_preflight_m0/.venv/Scripts/python.exe"),
        "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "../host_preflight_m0/tests",
        "--junitxml=evidence/task001-regression.xml")
    run("build", python, "-m", "build", "--no-isolation")
    run("test-environment", python, "-m", "venv", ".test-env")
    run("wheel-install", test_python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps",
        "--force-reinstall", preflight_wheel, "dist/bb_host_virtual_ticks-0.1.0-py3-none-any.whl")
    run("wheel-smoke", test_python, "scripts/smoke.py")
    run("wheel-dependencies", test_python, "-m", "pip", "check")
    for environment in (".venv", ".test-env"):
        installed = PACKAGE / environment / "Lib/site-packages"
        for source in (ROOT / "Source/host_preflight_m0/src/bb_host_preflight_m0").glob("*.py"):
            path = source.relative_to(ROOT).as_posix()
            assert (installed / "bb_host_preflight_m0" / source.name).read_bytes() == git("show", BASELINE + ":" + path)
    for source in (PACKAGE / "src/bb_host_virtual_ticks").glob("*.py"):
        assert source.read_bytes() == (PACKAGE / ".test-env/Lib/site-packages/bb_host_virtual_ticks" / source.name).read_bytes()
    assert hashlib.sha256(preserved.read_bytes()).hexdigest() == preserved_hash
    counts = {}
    for filename in ("tests.xml", "task001-regression.xml"):
        suite = ET.parse(EVIDENCE / filename).getroot().find("testsuite")
        counts[filename] = {key: int(suite.get(key)) for key in ("tests", "failures", "errors", "skipped")}
    environment = dict(python=platform.python_version(), platform=platform.platform(),
                       packages={d.metadata["Name"]: d.version for d in metadata.distributions()},
                       effective_timezone_switch_supported=hasattr(time, "tzset"),
                       locales_tested=["C", "English_United States.1252"], TZ_values_tested=["UTC0", "ICT-7"],
                       test_results=counts, installed_preflight_matches_pinned_source=True,
                       installed_scheduler_matches_source=True, preserved_task001_baseline_sha256=preserved_hash,
                       artifacts=[dict(path=p.relative_to(PACKAGE).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                  for p in sorted((PACKAGE / "dist").glob("*"))])
    (EVIDENCE / "environment.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Verification complete. Owner UAT: README's three commands.", flush=True)


if __name__ == "__main__":
    main()
