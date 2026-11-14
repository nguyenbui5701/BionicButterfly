"""Run unchanged from normal and clean Git checkouts; task-local fixture only."""
import hashlib
import json
from pathlib import Path
import pytest
from scripts import verify


def scratch_baselines(tmp_path):
    for folder,_ in verify.PREREQUISITES:
        name='Source/'+folder+'/evidence/baseline.json'
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(verify.git('show',verify.BASELINE+':'+name))
    return tmp_path


def test_N24_stages_exact_fixture_with_no_modified_historical_file(tmp_path,monkeypatch):
    root=scratch_baselines(tmp_path)
    p=root/'Source/host_preflight_m0/evidence/baseline.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()!=verify.PRESERVED
    # After setup, make any use of the original worktree impossible.
    monkeypatch.setattr(verify,'ROOT',tmp_path/'does-not-exist')
    result=verify.stage_preserved(root)
    assert result['sha256']==verify.PRESERVED
    assert p.read_bytes()==verify.preserved_fixture()


@pytest.mark.parametrize('failure',['missing','mismatch','consumer'])
def test_N24_cannot_skip_or_repin_fixture(failure,tmp_path,monkeypatch):
    root=scratch_baselines(tmp_path)
    p=root/'Source/host_preflight_m0/evidence/baseline.json';before=p.read_bytes()
    if failure in ('missing','mismatch'):
        fixture=tmp_path/'bad.json'
        if failure=='mismatch':fixture.write_bytes(b'{}')
        monkeypatch.setattr(verify,'FIXTURE',fixture)
    else:
        pin=root/'Source/host_integrated_fsm_model/evidence/baseline.json'
        record=json.loads(pin.read_bytes());record['preserved_task001_baseline_sha256']='0'*64
        pin.write_text(json.dumps(record),encoding='utf-8')
    with pytest.raises((FileNotFoundError,ValueError)):verify.stage_preserved(root)
    assert p.read_bytes()==before


def test_N24_preserved_fixture_contents_are_only_hash_metadata():
    obj=json.loads(verify.preserved_fixture())
    assert set(obj)=={'baseline','head','contracts','release_artifacts'}
    for row in obj['contracts']+obj['release_artifacts']:
        assert set(row)<= {'path','git_blob_sha1','sha256','result'}
        assert row['path'].startswith(('Design/','Task/'))
        assert ':' not in row['path'] and '..' not in Path(row['path']).parts


def test_frozen_action_schema_matches_release():
    from bb_host_virtual_control_studio._schema import SCHEMA
    from scripts.fixtures import frozen_bytes
    assert SCHEMA==json.loads(frozen_bytes('Design/fixtures/P226_STUDIO_ACTIONS.schema.json'))
