"""Read-only pinned Design fixture adapter; never a runtime trust provider."""
import hashlib
import json
from pathlib import Path

from bb_host_trust_boundary import ClaimedHostFingerprint

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]


def frozen_bytes(path):
    record = json.loads((PACKAGE / "evidence/baseline.json").read_text(encoding="utf-8"))
    pins = {row["path"]: row["git_blob_sha1"] for row in record["pinned_files"] + record["release_files"]}
    raw = (ROOT / path).read_bytes()
    if hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() != pins[path]:
        raise ValueError("fixture pin mismatch: " + path)
    return raw


def index():
    return json.loads(frozen_bytes("Design/fixtures/P224_INTEGRATED_SHADOW_ORACLE_INDEX.json"))


def inputs(preset):
    spec = index()
    e2 = json.loads(frozen_bytes(spec["e2_fixture"]))
    e3 = json.loads(frozen_bytes(spec["e3_fixture"]))
    manifest = json.dumps(e3["base_intent"], sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")
    engine = e3["engine_artifact_utf8_test_only"].encode("ascii")
    scheduler = e3["scheduler_artifact_utf8_test_only"].encode("ascii")
    assert b"TEST_ONLY" in engine and b"TEST_ONLY" in scheduler
    return dict(scenario_raw=frozen_bytes(spec["demo_presets"][preset]),
        frozen_wire_v2_schema=json.loads(frozen_bytes(spec["wire_v2_schema"])),
        policy_raw=frozen_bytes(spec["policy_raw"]), claimed_host=ClaimedHostFingerprint(**e2["reference_host_claim"]),
        intent_raw=manifest, engine_artifact=engine, scheduler_artifact=scheduler)
