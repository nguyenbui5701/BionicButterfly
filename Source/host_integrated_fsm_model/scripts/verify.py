"""Task-local build/provenance/test evidence; no runtime execution authority."""

import argparse
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
import zipfile

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
EVIDENCE_ROOT = PACKAGE / "evidence"
EVIDENCE = EVIDENCE_ROOT / "dev"
BASELINE = "eb4dbc8830d864c9cfd5c4d94bf00180aa960b5d"
PREREQUISITES = (("host_preflight_m0", "bb_host_preflight_m0"), ("host_virtual_ticks", "bb_host_virtual_ticks"),
                 ("host_batch_observations", "bb_host_batch_observations"), ("host_temporal_guard_facts", "bb_host_temporal_guard_facts"), ("host_safety_priority_kernel", "bb_host_safety_priority_kernel"), ("host_arm_qualification", "bb_host_arm_qualification"), ("host_health_evidence", "bb_host_health_evidence"), ("host_guard_triage", "bb_host_guard_triage"), ("host_snapshot_commit_gate", "bb_host_snapshot_commit_gate"), ("host_trust_boundary", "bb_host_trust_boundary"), ("host_provisioning_intent", "bb_host_provisioning_intent"), ("host_integrated_shadow_replay", "bb_host_integrated_shadow_replay"))


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def provenance():
    record = json.loads((EVIDENCE_ROOT / "baseline.json").read_text(encoding="utf-8"))
    assert record["baseline"] == BASELINE
    git("merge-base", "--is-ancestor", BASELINE, "HEAD")
    for row in record["pinned_files"]:
        assert git("rev-parse", BASELINE + ":" + row["path"]).decode().strip() == row["git_blob_sha1"]
        raw = (ROOT / row["path"]).read_bytes()
        raw_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        # Historical evidence sometimes intentionally stores CRLF in the Git
        # blob. Prefer exact raw bytes; only otherwise accept Git's configured
        # checkout normalization. Explicit Design/190 pins below stay raw-exact.
        assert raw_blob == row["git_blob_sha1"] or git("hash-object", row["path"]).decode().strip() == row["git_blob_sha1"], row["path"]
    design_pins = re.findall(r"\| `([^`]+)` \| `([0-9a-f]{40})` \|",
                             (ROOT / "Design/190_TASK012_MERGE_CLOSEOUT_AND_TASK013_BASELINE.md").read_text(encoding="utf-8"))
    assert len(design_pins) == 32
    for path, expected in design_pins:
        raw = (ROOT / path).read_bytes()
        assert git("rev-parse", BASELINE + ":" + path).decode().strip() == expected
        assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == expected, path
    manifest_path = ROOT / "Design/P225_TASK013_RELEASE_MANIFEST.json"
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == record["release_manifest_sha256"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source_main_commit"] == BASELINE and manifest["files"] == record["release_files"]
    assert len(manifest["files"]) == 9
    for row in manifest["files"]:
        raw = (ROOT / row["path"]).read_bytes()
        assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"], row["path"]
        assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob_sha1"]
    assert hashlib.sha256((ROOT / "Design/contracts/SIM_POLICY_22A_R1.canonical.json").read_bytes()).hexdigest() == record["policy_sha256"]
    assert hashlib.sha256((ROOT / "Source/host_preflight_m0/evidence/baseline.json").read_bytes()).hexdigest() == record["preserved_task001_baseline_sha256"]
    vendor = json.loads((PACKAGE / "vendor/manifest.json").read_text(encoding="utf-8"))
    assert vendor["sha256"] == "520d690b448ecf0703691c76e1a34a24ddcd4fc5bc41d589cb7c58ec651bcd48"
    assert hashlib.sha256((PACKAGE / "vendor" / vendor["wheel"]).read_bytes()).hexdigest() == vendor["sha256"]
    print(f"Provenance: {len(record['pinned_files'])} pinned files + 9 release artifacts + policy MATCH.", flush=True)


def installed_dependencies(environment):
    for folder, module in PREREQUISITES:
        for path in git("ls-tree", "-r", "--name-only", BASELINE, "--", f"Source/{folder}/src/{module}").decode().splitlines():
            if path.endswith(".py"):
                assert (environment / "Lib/site-packages" / module / Path(path).name).read_bytes() == git("show", BASELINE + ":" + path), path
    with zipfile.ZipFile(PACKAGE / "vendor/rfc8785-0.1.4-py3-none-any.whl") as wheel:
        for path in wheel.namelist():
            if path.startswith("rfc8785/") and path.endswith(".py"):
                assert (environment / "Lib/site-packages" / path).read_bytes() == wheel.read(path), path


def write_json(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def revision():
    """Git HEAD plus actual executable/config bytes, including uncommitted work."""
    paths = sorted([p for directory in ("src", "tests", "scripts") for p in (PACKAGE / directory).rglob("*") if p.is_file() and p.suffix in (".py", ".js", ".json")]
                   + list((PACKAGE / "vendor").glob("*")) + [PACKAGE / "pyproject.toml", PACKAGE / "MANIFEST.in"])
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


def regression_targets(owner):
    """DEV never schedules a prior regression; OWNER explicitly includes all 12."""
    return tuple(enumerate(PREREQUISITES, 1)) if owner else ()


def stage_preserved_regression_evidence(regression_root):
    """Retain the byte-exact working evidence required by inherited SHA pins.

    Prior approved provenance records pin preserved Windows working bytes,
    including an updated head field and CRLF, rather than this file's Git blob. Copy
    only that verified evidence exception, never alter old source or assertions.
    """
    relative = "Source/host_preflight_m0/evidence/baseline.json"
    record = json.loads((EVIDENCE_ROOT / "baseline.json").read_text(encoding="utf-8"))
    expected = record["preserved_task001_baseline_sha256"]
    raw = (ROOT / relative).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise ValueError("preserved TASK001 evidence SHA-256 mismatch")
    for folder, _ in PREREQUISITES:
        prior = json.loads((regression_root / "Source" / folder / "evidence/baseline.json").read_text(encoding="utf-8"))
        pinned = prior.get("preserved_task001_baseline_sha256")
        if pinned is not None and pinned != actual:
            raise ValueError("incompatible preserved TASK001 evidence pin: " + folder)
    destination = regression_root / relative
    destination.write_bytes(raw)
    if destination.read_bytes() != raw:
        raise OSError("preserved regression evidence copy differs")
    return dict(path=relative, sha256=actual, source="verified preserved working bytes",
                scope="isolated regression workspace only")


def main(argv=None):
    global EVIDENCE
    parser = argparse.ArgumentParser(description="TASK013 DEV CHECK or OWNER FULL UAT")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dev", action="store_true")
    mode.add_argument("--owner", action="store_true")
    args = parser.parse_args(argv)
    EVIDENCE = EVIDENCE_ROOT / ("owner" if args.owner else "dev")
    if Path(sys.prefix).resolve() != (PACKAGE / ".venv").resolve():
        raise RuntimeError("run verify.py with this task's .venv Python")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
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

    run("node-reference-version", "node", "--version")
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
        run(f"build-task{number:03}", python, "-m", "build", "--wheel", "--no-isolation", "--outdir", scratch / "dependencies", target)
    wheels = [scratch / "dependencies" / f"{module}-0.1.0-py3-none-any.whl" for _, module in PREREQUISITES] + [PACKAGE / "vendor/rfc8785-0.1.4-py3-none-any.whl"]
    run("install-prerequisites", python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps", "--force-reinstall", *wheels)
    installed_dependencies(PACKAGE / ".venv")
    run("install", python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps", "--no-build-isolation", "-e", ".")
    run("compile", python, "-m", "compileall", "-q", "src", "tests", "scripts")
    run("tests", python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml=" + str(EVIDENCE / "tests.xml"))
    run("smoke", python, "scripts/smoke.py")
    run("dependencies", python, "-m", "pip", "check")
    for preset in ("nominal", "recovery", "conflict"):
        run("demo-" + preset, python, "scripts/demo.py", "--case", preset,
            "--view", EVIDENCE / ("viewer-" + preset + ".html"),
            "--candidate", EVIDENCE / ("demo-" + preset + ".model-candidate.jsonl"))
    if args.owner:
        # Task012's stress test writes relative evidence/performance.json. Run all
        # old tests from baseline copies inside THIS task's cache, with the
        # verified preserved TASK001 evidence exception below. No prior Source
        # file or evidence is written during OWNER FULL UAT.
        regression_root = scratch / "regression-workspace"
        for path in git("ls-tree", "-r", "--name-only", BASELINE, "--", "Design", "Task", "Source").decode().splitlines():
            parts = path.split("/")
            include = path.startswith(("Design/", "Task/")) or (
                len(parts) > 2 and parts[1] in {folder for folder, _ in PREREQUISITES}
                and (parts[2] in ("src", "scripts", "tests", "evidence") or len(parts) == 3))
            if include and not path.startswith("Design/assets/"):
                destination = regression_root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(git("show", BASELINE + ":" + path))
        write_json("regression-staging.json", stage_preserved_regression_evidence(regression_root))
        for number, (folder, _) in regression_targets(True):
            run(f"task{number:03}-regression", python, "-B", "-m", "pytest",
                "-q", "-p", "no:cacheprovider", "tests", "--junitxml=" + str(EVIDENCE / f"task{number:03}-regression.xml"),
                cwd=regression_root / f"Source/{folder}")
    run("build", python, "-m", "build", "--no-isolation", "--outdir", scratch / "dist")
    run("wheel-environment", python, "-m", "venv", scratch / "wheel-env")
    wheel_python = scratch / "wheel-env/Scripts/python.exe"
    run("wheel-install", wheel_python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps", *wheels,
        scratch / "dist/bb_host_integrated_fsm_model-0.1.0-py3-none-any.whl")
    run("wheel-smoke", wheel_python, "scripts/smoke.py")
    run("wheel-dependencies", wheel_python, "-m", "pip", "check")
    installed_dependencies(scratch / "wheel-env")
    for source in (PACKAGE / "src/bb_host_integrated_fsm_model").glob("*.py"):
        assert source.read_bytes() == (scratch / "wheel-env/Lib/site-packages/bb_host_integrated_fsm_model" / source.name).read_bytes()
    provenance()
    counts = {}
    for filename in ("tests.xml", *(f"task{i:03}-regression.xml" for i in range(1, 13) if args.owner)):
        suite = ET.parse(EVIDENCE / filename).getroot().find("testsuite")
        counts[filename] = {key: int(suite.get(key)) for key in ("tests", "failures", "errors", "skipped")}
    environment = dict(python=platform.python_version(), platform=platform.platform(),
                       packages={d.metadata["Name"]: d.version for d in metadata.distributions()},
                       test_results=counts, installed_dependencies_match_pinned_source=True, installed_task013_matches_source=True,
                       wheel_environment=(scratch / "wheel-env").relative_to(PACKAGE).as_posix(),
                       artifacts=[dict(path=p.relative_to(PACKAGE).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                  for folder in (scratch / "dependencies", scratch / "dist") for p in sorted(folder.glob("*"))])
    (EVIDENCE / "environment.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    assert revision_before == revision(), "execution-affecting source changed during verification"
    oracle_results = []
    for case in ET.parse(EVIDENCE / "tests.xml").iter("testcase"):
        match = re.fullmatch(r"test_p225_real_pipeline\[(P225-T\d{2})\]", case.get("name", ""))
        if match:
            status = "FAIL" if any(case.find(tag) is not None for tag in ("failure", "error", "skipped")) else "PASS"
            oracle_results.append(dict(id=match[1], result=status))
    assert [row["id"] for row in oracle_results] == [f"P225-T{i:02}" for i in range(1, 25)]
    assert all(row["result"] == "PASS" for row in oracle_results)
    assert all(not any(row[k] for k in ("failures", "errors", "skipped")) for row in counts.values())
    negatives = [case for case in ET.parse(EVIDENCE / "tests.xml").iter("testcase")
                 if not case.get("classname", "").endswith("test_oracles")]
    assert negatives and all(not any(case.find(tag) is not None for tag in ("failure", "error", "skipped")) for case in negatives)
    assert {re.match(r"test_(N[0-9]{2})_", c.get("name", ""))[1]
            for c in negatives if re.match(r"test_(N[0-9]{2})_", c.get("name", ""))} == {f"N{i:02}" for i in range(1, 25)}
    for name in ("performance.json", "jcs-vectors.json"):
        (EVIDENCE / name).write_bytes((EVIDENCE_ROOT / name).read_bytes())
    for log in ("smoke.log", "wheel-smoke.log"):
        assert (EVIDENCE / log).read_text(encoding="utf-8").strip() == "Smoke: 3 PASS, 0 FAIL"
    warning_lines = [dict(log=path.name, line=line.strip()) for path in (EVIDENCE / c["log"] for c in commands)
                     for line in path.read_text(encoding="utf-8").splitlines()
                     if "warning" in line.lower()]
    write_json("summary.json", dict(
        status="PASS", mode="OWNER_FULL_UAT" if args.owner else "DEV_CHECK",
        revision=revision_before, baseline=BASELINE, test_results=counts,
        oracle_results=oracle_results, additional_tests=dict(result="PASS", cases=len(negatives)),
        smoke={"development": "3 PASS, 0 FAIL", "installed_wheel": "3 PASS, 0 FAIL"},
        demos={preset: "exit 0; console + offline HTML + labeled candidate JSONL saved" for preset in ("nominal", "recovery", "conflict")},
        all_commands_exit_zero=True, warnings=warning_lines,
        installed_dependencies_match_pinned_source=True, installed_task013_matches_source=True,
        pinned_files=len(json.loads((EVIDENCE_ROOT / "baseline.json").read_text(encoding="utf-8"))["pinned_files"]),
        baseline_design_pins=32, release_artifacts=9, policy="MATCH",
        prior_regressions="ACTUALLY RUN: TASK001-012" if args.owner else "NOT RUN: reserved for OWNER FULL UAT",
        full_verification_run=args.owner,
        negative_families=sorted(set(re.match(r"test_(N[0-9]{2})_", c.get("name", ""))[1]
            for c in negatives if re.match(r"test_(N[0-9]{2})_", c.get("name", "")))),
        jcs_reference="RFC8785 Appendix B plus 4120 Node/V8 binary64 comparisons and Unicode/candidate vectors",
        limits=["MODEL_ONLY: no operational runtime/ARM/output; no complete R1 runtime claim",
                "No physical output, device/firmware/servo or flight tests",
                "Ambiguous HEALTHY+UNKNOWN stops MODEL_CONTRACT_BLOCKED for SA; no invented effective RF priority",
                "Candidate terminal FAILED/E_OWNER_DENIED is schema-conformance only, not runtime execution",
                "Atomic offline replacement is not power-loss durability; actual OS timezone switching not tested"],
        acceptance={
            "AC-01": "new task subtree only; prior Source and approved release/policy unchanged",
            "AC-02": "real TASK001-005/007/008, E2/E3, separate TASK012/F0+E1 comparator",
            "AC-03": "eight-state model, exact original LOW/HIGH times, independent freshness, S1 and qualified ACK",
            "AC-04": "frozen constants and genuine exact M0; no synthetic TASK006 admission",
            "AC-05": "counterfactual MODEL ACTIVE visible; permanent operational denial",
            "AC-06": "pinned offline rfc8785, independent RFC/V8 and candidate schema/order/identity vectors",
            "AC-07": "sticky private append barrier with before/short/after/quota/serializer and terminal failures",
            "AC-08": "three genuine CLI demos and self-contained offline HTML state/effort viewer",
            "AC-09": "24 authored P225 oracles and all N01-N24 adversarial families",
            "AC-10": "60s/12001-tick/20000-event test, bounded bytes/allocations, no repeated event rescan",
            "AC-11": "DEV only new tests; OWNER all twelve prior regressions in isolated copies",
            "AC-12": "32 pins + nine release files + manifest and policy MATCH; G0-B remains not approved"}))
    print(f"{'OWNER FULL UAT' if args.owner else 'DEV CHECK'} PASS; 24/24 P225; evidence/{EVIDENCE.name}/summary.json.", flush=True)



if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        # Never leave an old PASS summary after a failed provenance/build/check.
        if not isinstance(error, SystemExit) or error.code:
            existing = EVIDENCE / "summary.json"
            record = json.loads(existing.read_text(encoding="utf-8")) if existing.exists() else {}
            record.update(status="FAIL", error=f"{type(error).__name__}: {error}")
            EVIDENCE.mkdir(parents=True, exist_ok=True)
            write_json("summary.json", record)
        raise
