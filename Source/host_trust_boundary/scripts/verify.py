"""Task-local build/provenance/test evidence; no runtime execution authority."""

import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
EVIDENCE = PACKAGE / "evidence"
BASELINE = "4c7c92524837c8c728d0f206e5ba4655f9513399"
PREREQUISITES = (("host_preflight_m0", "bb_host_preflight_m0"), ("host_virtual_ticks", "bb_host_virtual_ticks"),
                 ("host_batch_observations", "bb_host_batch_observations"), ("host_temporal_guard_facts", "bb_host_temporal_guard_facts"), ("host_safety_priority_kernel", "bb_host_safety_priority_kernel"), ("host_arm_qualification", "bb_host_arm_qualification"), ("host_health_evidence", "bb_host_health_evidence"), ("host_guard_triage", "bb_host_guard_triage"), ("host_snapshot_commit_gate", "bb_host_snapshot_commit_gate"))


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def provenance():
    record = json.loads((EVIDENCE / "baseline.json").read_text(encoding="utf-8"))
    assert record["baseline"] == BASELINE
    git("merge-base", "--is-ancestor", BASELINE, "HEAD")
    for row in record["pinned_files"]:
        assert git("rev-parse", BASELINE + ":" + row["path"]).decode().strip() == row["git_blob_sha1"]
        assert git("hash-object", row["path"]).decode().strip() == row["git_blob_sha1"], row["path"]
    design_pins = re.findall(r"\| `([^`]+)` \| `([0-9a-f]{40})` \|",
                             (ROOT / "Design/181_TASK009_MERGE_CLOSEOUT_AND_TASK010_BASELINE.md").read_text(encoding="utf-8"))
    assert len(design_pins) == 18
    for path, expected in design_pins:
        raw = (ROOT / path).read_bytes()
        assert git("rev-parse", BASELINE + ":" + path).decode().strip() == expected
        assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == expected, path
    manifest_path = ROOT / "Design/P222_TASK010_RELEASE_MANIFEST.json"
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == record["release_manifest_sha256"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source_main_commit"] == BASELINE and manifest["files"] == record["release_files"]
    for row in manifest["files"]:
        raw = (ROOT / row["path"]).read_bytes()
        assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"], row["path"]
        assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob_sha1"]
    assert hashlib.sha256((ROOT / "Design/contracts/SIM_POLICY_22A_R1.canonical.json").read_bytes()).hexdigest() == record["policy_sha256"]
    assert hashlib.sha256((ROOT / "Source/host_preflight_m0/evidence/baseline.json").read_bytes()).hexdigest() == record["preserved_task001_baseline_sha256"]
    print(f"Provenance: {len(record['pinned_files'])} pinned files + 5 release artifacts + policy MATCH.", flush=True)


def installed_dependencies(environment):
    for folder, module in PREREQUISITES:
        for path in git("ls-tree", "-r", "--name-only", BASELINE, "--", f"Source/{folder}/src/{module}").decode().splitlines():
            if path.endswith(".py"):
                assert (environment / "Lib/site-packages" / module / Path(path).name).read_bytes() == git("show", BASELINE + ":" + path), path


def write_json(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def revision():
    """Git HEAD plus actual executable/config bytes, including uncommitted work."""
    paths = sorted([p for directory in ("src", "tests", "scripts") for p in (PACKAGE / directory).rglob("*.py")]
                   + [PACKAGE / "pyproject.toml", PACKAGE / "MANIFEST.in"])
    hashes = {p.relative_to(PACKAGE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return dict(head=git("rev-parse", "HEAD").decode().strip(),
                branch=git("branch", "--show-current").decode().strip(), files=hashes,
                source_sha256=hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest())


def archive_failed_attempt():
    """Keep previous failures/warnings before a new run overwrites current logs."""
    summary = EVIDENCE / "summary.json"
    if not summary.exists():
        return
    prior = json.loads(summary.read_text(encoding="utf-8"))
    if prior.get("status") != "PASS" or prior.get("warnings"):
        history = EVIDENCE / "history"
        history.mkdir(exist_ok=True)
        target = history / f"attempt-{len(list(history.iterdir())) + 1:03}"
        target.mkdir()
        for path in EVIDENCE.iterdir():
            if path.is_file() and path.suffix in (".json", ".xml", ".log") and path.name != "baseline.json":
                (target / path.name).write_bytes(path.read_bytes())


def main():
    if Path(sys.prefix).resolve() != (PACKAGE / ".venv").resolve():
        raise RuntimeError("run verify.py with this task's .venv Python")
    EVIDENCE.mkdir(exist_ok=True)
    archive_failed_attempt()
    provenance()
    revision_before = revision()
    cache = PACKAGE / ".cache"
    cache.mkdir(exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="verify-", dir=cache))
    python = PACKAGE / ".venv/Scripts/python.exe"
    commands = []
    write_json("summary.json", dict(status="RUNNING", revision=revision_before))

    def run(name, executable, *args, cwd=PACKAGE):
        command = [str(executable), *map(str, args)]
        result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace")
        output = re.sub(re.escape(str(ROOT)), "<REPOSITORY>", result.stdout, flags=re.IGNORECASE)
        output = re.sub(re.escape(ROOT.as_posix()), "<REPOSITORY>", output, flags=re.IGNORECASE)
        output = re.sub(re.escape(str(Path.home())), "<USERPROFILE>", output, flags=re.IGNORECASE)
        (EVIDENCE / (name + ".log")).write_text(output, encoding="utf-8", newline="\n")
        commands.append(dict(name=name, command=[x.replace(str(ROOT), "<REPOSITORY>") for x in command],
                             cwd=str(cwd).replace(str(ROOT), "<REPOSITORY>"), exit_code=result.returncode, log=name + ".log"))
        (EVIDENCE / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"{name}: exit={result.returncode}", flush=True)
        if result.returncode:
            write_json("summary.json", dict(status="FAIL", failed_command=name, revision=revision_before, commands=commands))
            print(output, flush=True)
            raise SystemExit(result.returncode)

    # Build exact Git source copies; never overwrite or depend on old dist files.
    for number, (folder, module) in enumerate(PREREQUISITES, 1):
        prefix = f"Source/{folder}/"
        target = scratch / "source" / folder
        for path in git("ls-tree", "-r", "--name-only", BASELINE, "--", prefix).decode().splitlines():
            relative = path[len(prefix):]
            if relative.startswith(("src/", "tests/", "scripts/")) or ("/" not in relative and (relative.endswith(".md") or relative in ("pyproject.toml", "MANIFEST.in"))):
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(git("show", BASELINE + ":" + path))
        run(f"build-task00{number}", python, "-m", "build", "--wheel", "--no-isolation", "--outdir", scratch / "dependencies", target)
    wheels = [scratch / "dependencies" / f"{module}-0.1.0-py3-none-any.whl" for _, module in PREREQUISITES]
    run("install-prerequisites", python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps", "--force-reinstall", *wheels)
    installed_dependencies(PACKAGE / ".venv")
    run("install", python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps", "--no-build-isolation", "-e", ".")
    run("compile", python, "-m", "compileall", "-q", "src", "tests", "scripts")
    run("tests", python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml=evidence/tests.xml")
    run("smoke", python, "scripts/smoke.py")
    run("dependencies", python, "-m", "pip", "check")
    for number, (folder, _) in enumerate(PREREQUISITES, 1):
        run(f"task00{number}-regression", python, "-B", "-m", "pytest",
            "-q", "-p", "no:cacheprovider", "tests", "--junitxml=" + str(EVIDENCE / f"task00{number}-regression.xml"),
            cwd=ROOT / f"Source/{folder}")
    run("build", python, "-m", "build", "--no-isolation", "--outdir", scratch / "dist")
    run("wheel-environment", python, "-m", "venv", scratch / "wheel-env")
    wheel_python = scratch / "wheel-env/Scripts/python.exe"
    run("wheel-install", wheel_python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps", *wheels,
        scratch / "dist/bb_host_trust_boundary-0.1.0-py3-none-any.whl")
    run("wheel-smoke", wheel_python, "scripts/smoke.py")
    run("wheel-dependencies", wheel_python, "-m", "pip", "check")
    installed_dependencies(scratch / "wheel-env")
    for source in (PACKAGE / "src/bb_host_trust_boundary").glob("*.py"):
        assert source.read_bytes() == (scratch / "wheel-env/Lib/site-packages/bb_host_trust_boundary" / source.name).read_bytes()
    provenance()
    counts = {}
    for filename in ("tests.xml", *(f"task00{i}-regression.xml" for i in range(1, 10))):
        suite = ET.parse(EVIDENCE / filename).getroot().find("testsuite")
        counts[filename] = {key: int(suite.get(key)) for key in ("tests", "failures", "errors", "skipped")}
    environment = dict(python=platform.python_version(), platform=platform.platform(),
                       packages={d.metadata["Name"]: d.version for d in metadata.distributions()},
                       test_results=counts, installed_dependencies_match_pinned_source=True, installed_task010_matches_source=True,
                       effective_timezone_switch_supported=hasattr(time, "tzset"), locales_tested=["C", "English_United States.1252"],
                       TZ_values_tested=["UTC0", "ICT-7"], wheel_environment=(scratch / "wheel-env").relative_to(PACKAGE).as_posix(),
                       artifacts=[dict(path=p.relative_to(PACKAGE).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                  for folder in (scratch / "dependencies", scratch / "dist") for p in sorted(folder.glob("*"))])
    (EVIDENCE / "environment.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    assert revision_before == revision(), "execution-affecting source changed during verification"
    oracle_results = []
    for case in ET.parse(EVIDENCE / "tests.xml").iter("testcase"):
        match = re.fullmatch(r"test_p222_real_preflight\[(P222-T\d{2})\]", case.get("name", ""))
        if match:
            status = "FAIL" if any(case.find(tag) is not None for tag in ("failure", "error", "skipped")) else "PASS"
            oracle_results.append(dict(id=match[1], result=status))
    assert [row["id"] for row in oracle_results] == [f"P222-T{i:02}" for i in range(1, 49)]
    assert all(row["result"] == "PASS" for row in oracle_results)
    assert all(not any(row[k] for k in ("failures", "errors", "skipped")) for row in counts.values())
    negatives = [case for case in ET.parse(EVIDENCE / "tests.xml").iter("testcase")
                 if case.get("classname", "").endswith("test_boundary")]
    assert negatives and all(not any(case.find(tag) is not None for tag in ("failure", "error", "skipped")) for case in negatives)
    families = {}
    for case in negatives:
        family = re.match(r"test_(N\d{2})_", case.get("name", ""))
        assert family, case.get("name")
        families[family[1]] = families.get(family[1], 0) + 1
    assert set(families) == {f"N{i:02}" for i in range(1, 19)}
    for log in ("smoke.log", "wheel-smoke.log"):
        assert (EVIDENCE / log).read_text(encoding="utf-8").strip() == "Smoke: 48 PASS, 0 FAIL"
    warning_lines = [dict(log=path.name, line=line.strip()) for path in EVIDENCE.glob("*.log")
                     for line in path.read_text(encoding="utf-8").splitlines()
                     if "warning" in line.lower()]
    write_json("summary.json", dict(
        status="PASS", revision=revision_before, baseline=BASELINE, test_results=counts,
        oracle_results=oracle_results, negative_tests=dict(result="PASS", cases=len(negatives)), smoke={"development": "48 PASS, 0 FAIL", "installed_wheel": "48 PASS, 0 FAIL"},
        all_commands_exit_zero=True, warnings=warning_lines,
        dependencies=environment["packages"], installed_dependencies_match_pinned_source=True,
        installed_task010_matches_source=True,
        pinned_files=len(json.loads((EVIDENCE / "baseline.json").read_text(encoding="utf-8"))["pinned_files"]),
        full_verification_run=True,
        negative_families=[dict(id=key, result="PASS", tests=value) for key, value in sorted(families.items())],
        limits=["PC_SIM_ONLY TEST_ONLY reference comparison; no runtime trust or executable attestation",
                "Matching tuple/digest is content comparison only; fabricated exact Python objects are not authenticated",
                "No runtime allowlist, ARM, FSM, accepted history, output, ledger or trace publication",
                "Full R1 system/hardware/flight NOT RUN; actual OS timezone switching NOT RUN on Windows without tzset"],
        acceptance={"AC-01": "task-local writes; frozen source/release hashes match",
                    "AC-02": "48 named P222 cases through genuine TASK-001 preflight; exact eight-field output",
                    "AC-03": "exact policy vector and eleven byte mutations, no runtime canonicalization",
                    "AC-04": "all eleven synthetic fields, exact types and fixed ordered combinations",
                    "AC-05": "permanent no-authority result even for matching pins",
                    "AC-06": "genuine rejected preflight wins; hash and comparison spies remain untouched",
                    "AC-07": "N01-N18 exercised; no trust bypass, wrapper and spoof cases",
                    "AC-08": "constant header line-count at 1/20000 events; AST/IO/ledger spies; frozen output",
                    "AC-09": "tests/build/install/pip/dev+wheel smoke and nine read-only regressions executed",
                    "AC-10": "three UAT commands plus full verify supplied; owner UAT/approval pending; no PR"}))
    print("Verification PASS; 48/48 P222; compact evidence/summary.json; owner UAT pending.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        # Never leave an old PASS summary after a failed provenance/build/check.
        if not isinstance(error, SystemExit) or error.code:
            existing = EVIDENCE / "summary.json"
            record = json.loads(existing.read_text(encoding="utf-8")) if existing.exists() else {}
            record.update(status="FAIL", error=f"{type(error).__name__}: {error}")
            EVIDENCE.mkdir(exist_ok=True)
            write_json("summary.json", record)
        raise
