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
BASELINE = "efe7fa3aff1beeb01af98b98a06593bd8e7af192"
PREREQUISITES = (("host_preflight_m0", "bb_host_preflight_m0"), ("host_virtual_ticks", "bb_host_virtual_ticks"),
                 ("host_batch_observations", "bb_host_batch_observations"), ("host_temporal_guard_facts", "bb_host_temporal_guard_facts"))


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def provenance():
    record = json.loads((EVIDENCE / "baseline.json").read_text(encoding="utf-8"))
    assert record["baseline"] == BASELINE
    git("merge-base", "--is-ancestor", BASELINE, "HEAD")
    for row in record["pinned_files"]:
        assert git("rev-parse", BASELINE + ":" + row["path"]).decode().strip() == row["git_blob_sha1"]
        assert git("hash-object", row["path"]).decode().strip() == row["git_blob_sha1"], row["path"]
    manifest_path = ROOT / "Design/P217_TASK005_RELEASE_MANIFEST.json"
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


def main():
    EVIDENCE.mkdir(exist_ok=True)
    provenance()
    cache = PACKAGE / ".cache"
    cache.mkdir(exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="verify-", dir=cache))
    python = PACKAGE / ".venv/Scripts/python.exe"
    commands = []

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
            print(output, flush=True)
            raise SystemExit(result.returncode)

    # Build exact Git source copies; never overwrite or depend on old dist files.
    for number, (folder, module) in enumerate(PREREQUISITES, 1):
        prefix = f"Source/{folder}/"
        target = scratch / "source" / folder
        for path in git("ls-tree", "-r", "--name-only", BASELINE, "--", prefix).decode().splitlines():
            relative = path[len(prefix):]
            if relative.startswith("src/") or relative in ("pyproject.toml", "README.md", "MANIFEST.in"):
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
        run(f"task00{number}-regression", ROOT / f"Source/{folder}/.venv/Scripts/python.exe", "-B", "-m", "pytest",
            "-q", "-p", "no:cacheprovider", "tests", "--junitxml=" + str(EVIDENCE / f"task00{number}-regression.xml"),
            cwd=ROOT / f"Source/{folder}")
    run("build", python, "-m", "build", "--no-isolation", "--outdir", scratch / "dist")
    run("wheel-environment", python, "-m", "venv", scratch / "wheel-env")
    wheel_python = scratch / "wheel-env/Scripts/python.exe"
    run("wheel-install", wheel_python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps", *wheels,
        scratch / "dist/bb_host_safety_priority_kernel-0.1.0-py3-none-any.whl")
    run("wheel-smoke", wheel_python, "scripts/smoke.py")
    run("wheel-dependencies", wheel_python, "-m", "pip", "check")
    installed_dependencies(scratch / "wheel-env")
    for source in (PACKAGE / "src/bb_host_safety_priority_kernel").glob("*.py"):
        assert source.read_bytes() == (scratch / "wheel-env/Lib/site-packages/bb_host_safety_priority_kernel" / source.name).read_bytes()
    provenance()
    counts = {}
    for filename in ("tests.xml", *(f"task00{i}-regression.xml" for i in range(1, 5))):
        suite = ET.parse(EVIDENCE / filename).getroot().find("testsuite")
        counts[filename] = {key: int(suite.get(key)) for key in ("tests", "failures", "errors", "skipped")}
    environment = dict(python=platform.python_version(), platform=platform.platform(),
                       packages={d.metadata["Name"]: d.version for d in metadata.distributions()},
                       test_results=counts, installed_dependencies_match_pinned_source=True, installed_task005_matches_source=True,
                       effective_timezone_switch_supported=hasattr(time, "tzset"), locales_tested=["C", "English_United States.1252"],
                       TZ_values_tested=["UTC0", "ICT-7"], wheel_environment=(scratch / "wheel-env").relative_to(PACKAGE).as_posix(),
                       artifacts=[dict(path=p.relative_to(PACKAGE).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                  for folder in (scratch / "dependencies", scratch / "dist") for p in sorted(folder.glob("*"))])
    (EVIDENCE / "environment.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("Verification complete; owner UAT commands are in README.", flush=True)


if __name__ == "__main__":
    main()
