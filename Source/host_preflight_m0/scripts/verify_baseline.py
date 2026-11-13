"""Read-only Git provenance check; writes evidence only inside this package."""

import hashlib
import json
from pathlib import Path
import re
import subprocess

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
BASELINE = "f378ec294a4a05887b03a9431696994dc22c0a4f"
task = (ROOT / "Task/TASK-001_HOST_PREFLIGHT_M0.md").read_text(encoding="utf-8")
paths = set(re.findall(r"`(Design/[^`*]+\.(?:md|json))`", task))
paths.update(path.relative_to(ROOT).as_posix() for pattern in ("P210_*", "P212_*")
             for path in (ROOT / "Design/fixtures").glob(pattern))
rows = []
for path in sorted(paths):
    raw = (ROOT / path).read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if path == "Design/156_G0A1_DIAGNOSTIC_V1_APPROVAL_AND_TASK001_RELEASE.md":
        continue  # New owner-supplied release artifact, checked by package manifest below.
    expected = subprocess.check_output(["git", "rev-parse", BASELINE + ":" + path], cwd=ROOT, text=True).strip()
    assert actual == expected, (path, expected, actual)
    rows.append(dict(path=path, git_blob_sha1=actual, sha256=hashlib.sha256(raw).hexdigest(), result="MATCH"))
manifest = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
release = []
for item in manifest["files"]:
    raw = (ROOT / item["path"]).read_bytes()
    assert len(raw) == item["bytes"]
    assert hashlib.sha256(raw).hexdigest() == item["sha256"]
    release.append(dict(path=item["path"], sha256=item["sha256"], result="MATCH_RELEASE_MANIFEST"))
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
record = dict(baseline=BASELINE, head=head, contracts=rows, release_artifacts=release)
(PACKAGE / "evidence").mkdir(exist_ok=True)
(PACKAGE / "evidence/baseline.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(f"Baseline: {len(rows)} exact Git blobs and {len(release)} release artifacts MATCH; HEAD={head}")
