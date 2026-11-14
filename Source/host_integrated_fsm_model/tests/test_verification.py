"""Regression staging must preserve approved evidence bytes, not relax pins."""
import hashlib
import json

import pytest

from scripts import verify


@pytest.fixture
def staged(tmp_path):
    relative = "Source/host_preflight_m0/evidence/baseline.json"
    for folder, _ in verify.PREREQUISITES:
        path = "Source/" + folder + "/evidence/baseline.json"
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((verify.ROOT / path).read_bytes())
    # Reproduce the Owner failure: git show lacks the preserved updated head
    # field and CRLF working bytes pinned by prior provenance records.
    (tmp_path / relative).write_bytes(verify.git("show", verify.BASELINE + ":" + relative))
    return tmp_path, relative


def test_regression_staging_preserves_approved_bytes_without_touching_source(staged):
    root, relative = staged
    original = (verify.ROOT / relative).read_bytes()
    record = json.loads((verify.EVIDENCE_ROOT / "baseline.json").read_text())
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() != record["preserved_task001_baseline_sha256"]
    result = verify.stage_preserved_regression_evidence(root)
    assert (root / relative).read_bytes() == original
    assert (verify.ROOT / relative).read_bytes() == original
    assert result["sha256"] == record["preserved_task001_baseline_sha256"]


def test_regression_staging_rejects_changed_source(staged, tmp_path, monkeypatch):
    root, relative = staged
    before = (root / relative).read_bytes()
    source = tmp_path / "changed-source"
    target = source / relative
    target.parent.mkdir(parents=True)
    target.write_bytes(before)  # Git bytes do not satisfy the preserved pin.
    monkeypatch.setattr(verify, "ROOT", source)
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        verify.stage_preserved_regression_evidence(root)
    assert (root / relative).read_bytes() == before


def test_regression_staging_rejects_conflicting_consumer_pin(staged):
    root, relative = staged
    before = (root / relative).read_bytes()
    consumer = root / "Source/host_trust_boundary/evidence/baseline.json"
    record = json.loads(consumer.read_text())
    record["preserved_task001_baseline_sha256"] = "0" * 64
    consumer.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="incompatible.*host_trust_boundary"):
        verify.stage_preserved_regression_evidence(root)
    assert (root / relative).read_bytes() == before
