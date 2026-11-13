"""Fixed local verification/build/deployment commands, not a runtime runner."""

import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parents[1]
EVIDENCE = PACKAGE / "evidence"
EVIDENCE.mkdir(exist_ok=True)
commands = []


def run(name, command):
    process = subprocess.run(command, cwd=PACKAGE, text=True, encoding="utf-8", errors="replace",
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.stdout.replace(str(PACKAGE), "<PACKAGE>").replace(PACKAGE.as_posix(), "<PACKAGE>")
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        output = output.replace(user_profile, "<USERPROFILE>")
    (EVIDENCE / (name + ".log")).write_text(output, encoding="utf-8")
    commands.append(dict(name=name, command=[str(x).replace(str(PACKAGE), "<PACKAGE>") for x in command],
                         exit_code=process.returncode, log=name + ".log"))
    print(name + ": exit=" + str(process.returncode))
    if process.returncode:
        print(output)
        raise SystemExit(process.returncode)


python = str(PACKAGE / ".venv/Scripts/python.exe")
run("baseline", [python, "scripts/verify_baseline.py"])
run("editable-install", [python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps",
                         "--no-build-isolation", "-e", "."])
run("dependency-check", [python, "-m", "pip", "check"])
run("compile", [python, "-m", "compileall", "-q", "src", "tests", "scripts"])
run("pytest", [python, "-m", "pytest", "-q", "--junitxml=evidence/pytest.xml"])
run("smoke-development", [python, "scripts/smoke.py"])
run("build", [python, "-m", "build", "--no-isolation"])
run("test-environment", [python, "-m", "venv", ".test-env"])
test_python = str(PACKAGE / ".test-env/Scripts/python.exe")
wheel = "dist/bb_host_preflight_m0-0.1.0-py3-none-any.whl"
run("wheel-install", [test_python, "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps",
                      "--force-reinstall", wheel])
run("wheel-dependency-check", [test_python, "-m", "pip", "check"])
run("smoke-installed-wheel", [test_python, "scripts/smoke.py"])
run("wheel-location", [test_python, "-c", "import bb_host_preflight_m0; print(bb_host_preflight_m0.__file__)"])
installed = PACKAGE / ".test-env/Lib/site-packages/bb_host_preflight_m0"
for source in (PACKAGE / "src/bb_host_preflight_m0").glob("*.py"):
    assert source.read_bytes() == (installed / source.name).read_bytes(), source.name
environment = {
    "python": platform.python_version(), "implementation": platform.python_implementation(),
    "platform": platform.platform(), "architecture": platform.machine(),
    "locales_tested": ["C", "English_United States.1252"], "TZ_values_tested": ["UTC0", "ICT-7"],
    "effective_timezone_switch_supported": hasattr(time, "tzset"),
    "packages": {dist.metadata["Name"]: dist.version for dist in metadata.distributions()},
    "artifacts": [{"path": path.relative_to(PACKAGE).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                  for path in sorted((PACKAGE / "dist").glob("*"))],
    "installed_runtime_matches_source": True,
}
(EVIDENCE / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
(EVIDENCE / "environment.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("Verification and local wheel deployment completed; evidence saved.")
