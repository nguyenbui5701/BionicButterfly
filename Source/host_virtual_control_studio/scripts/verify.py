"""DEV checks and isolated fresh-clone OWNER UAT; no dirty evidence dependency."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
try:
    from ._prerequisites import PREREQUISITES
except ImportError:
    from _prerequisites import PREREQUISITES

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
BASELINE = '0a0a49ba0bbd2a87a1771ef4ad09d0b2f55b4b09'
PRESERVED = 'e6dfcfd1ea13ffb4fb5ba2c3d2b475ef0f62c85d2f84faa666ba6b13af30fd9d'
MANIFEST_SHA = '7c964fef2bdb6b0437abbb9534f98488d9c73ccd17f35e21a754e64f303b38a3'
FIXTURE = PACKAGE / 'fixtures/TASK001_PRESERVED_BASELINE_FOR_REGRESSION.json'
EVIDENCE = PACKAGE / 'evidence/dev'


def git(*args):
    return subprocess.check_output(['git', *map(str,args)], cwd=ROOT)


def digest(raw):return hashlib.sha256(raw).hexdigest()


def preserved_fixture(path=None):
    raw = (FIXTURE if path is None else path).read_bytes()
    if digest(raw) != PRESERVED:
        raise ValueError('BLOCKED — PROVENANCE: preserved TASK001 fixture mismatch')
    return raw


def stage_preserved(regression_root):
    """Only task-local immutable fixture -> isolated clone. No old worktree reads."""
    raw = preserved_fixture()
    for folder, _ in PREREQUISITES:
        path = regression_root / 'Source' / folder / 'evidence/baseline.json'
        if not path.exists():
            raise ValueError('incomplete historical workspace: ' + folder)
        expected = json.loads(path.read_bytes()).get('preserved_task001_baseline_sha256')
        if expected is not None and expected != PRESERVED:
            raise ValueError('BLOCKED — PROVENANCE: incompatible old pin: ' + folder)
    target = regression_root / 'Source/host_preflight_m0/evidence/baseline.json'
    if regression_root.resolve() == ROOT.resolve() or target.is_symlink():
        raise ValueError('only isolated regression staging is permitted')
    target.write_bytes(raw)
    assert digest(target.read_bytes()) == PRESERVED
    return dict(path=target.relative_to(regression_root).as_posix(), sha256=PRESERVED,
                source='TASK014 immutable fixture; no current TASK001 worktree read')


def provenance():
    record = json.loads((PACKAGE / 'evidence/baseline.json').read_bytes())
    assert record['baseline'] == BASELINE
    git('merge-base','--is-ancestor',BASELINE,'HEAD')
    tree = {}
    for line in git('ls-tree','-r',BASELINE).decode().splitlines():
        meta,path=line.split('\t');tree[path]=meta.split()[2]
    pins = re.findall(r'\| `([^`]+)` \| `([0-9a-f]{40})` \|',
        (ROOT / 'Design/194_TASK013_MERGE_CLOSEOUT_AND_TASK014_BASELINE.md').read_text(encoding='utf-8'))
    assert len(pins) == 39
    for path, sha in pins:
        assert tree[path] == sha, path
    normalized = []
    for row in record['pinned_files']:
        assert tree[row['path']] == row['git_blob_sha1'], row['path']
        if row['path'] == 'Source/host_preflight_m0/evidence/baseline.json':
            continue  # Git blob already checked; runtime verifier uses only task-local fixture.
        raw = (ROOT / row['path']).read_bytes()
        raw_sha = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if raw_sha != row['git_blob_sha1']:
            normalized.append(row)
    if normalized:
        hashes=subprocess.check_output(['git','hash-object','--stdin-paths'],cwd=ROOT,
            input=('\n'.join(row['path'] for row in normalized)+'\n').encode()).decode().splitlines()
        assert len(hashes)==len(normalized)
        for row,sha in zip(normalized,hashes,strict=True):
            assert sha==row['git_blob_sha1'],row['path']
    raw = (ROOT / 'Design/P226_TASK014_RELEASE_MANIFEST.json').read_bytes()
    assert digest(raw) == MANIFEST_SHA == record['release_manifest_sha256']
    manifest = json.loads(raw)
    assert manifest['source_main_commit'] == BASELINE and manifest['files'] == record['release_files']
    assert len(manifest['files']) == 10
    for row in manifest['files']:
        raw = (ROOT / row['path']).read_bytes()
        assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], row['path']
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob_sha1'], row['path']
    assert digest((ROOT/'Design/contracts/SIM_POLICY_22A_R1.canonical.json').read_bytes()) == record['policy_sha256']
    preserved_fixture()
    bundle=json.loads((PACKAGE/'vendor/test-wheels/manifest.json').read_bytes())
    for name,sha in bundle['sha256'].items():
        assert digest((PACKAGE/'vendor/test-wheels'/name).read_bytes())==sha,name
    assert digest((PACKAGE/'vendor/rfc8785-0.1.4-py3-none-any.whl').read_bytes()) == '520d690b448ecf0703691c76e1a34a24ddcd4fc5bc41d589cb7c58ec651bcd48'
    print('Provenance: 39 baseline pins + 10 release hashes + manifest + policy + preserved fixture MATCH',flush=True)


def revision():
    paths = sorted(p for d in ('src','scripts','tests','fixtures','vendor') for p in (PACKAGE/d).rglob('*')
                   if p.is_file() and not any(part=='__pycache__' or part.endswith('.egg-info') for part in p.parts)
                   and p.suffix in ('.py','.json','.whl','.txt'))
    paths += [PACKAGE/'pyproject.toml',PACKAGE/'MANIFEST.in']
    hashes = {p.relative_to(PACKAGE).as_posix():digest(p.read_bytes()) for p in paths}
    return dict(head=git('rev-parse','HEAD').decode().strip(), files=hashes,
                source_sha256=digest(json.dumps(hashes,sort_keys=True,separators=(',',':')).encode()))


def clone_baseline(target):
    """Local Git clone, no network and no existing dirty worktree bytes."""
    subprocess.run(['git','clone','--shared','--no-checkout',str(ROOT),str(target)],check=True,capture_output=True)
    subprocess.run(['git','-c','core.autocrlf=false','checkout','--detach',BASELINE],cwd=target,check=True,capture_output=True)
    original = target/'Source/host_preflight_m0/evidence/baseline.json'
    assert original.read_bytes() == git('show',BASELINE+':Source/host_preflight_m0/evidence/baseline.json')
    assert digest(original.read_bytes()) != PRESERVED
    return target


def overlay_task(target):
    destination = target/'Source/host_virtual_control_studio'
    shutil.copytree(PACKAGE,destination,ignore=shutil.ignore_patterns('.cache','.venv','__pycache__','.pytest_cache','build','dist','*.egg-info'))
    manifest = json.loads((ROOT/'Design/P226_TASK014_RELEASE_MANIFEST.json').read_bytes())
    for path in [row['path'] for row in manifest['files']] + ['Design/P226_TASK014_RELEASE_MANIFEST.json']:
        out=target/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((ROOT/path).read_bytes())
    return destination


def main(argv=None):
    global EVIDENCE
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dev',action='store_true');mode.add_argument('--owner',action='store_true')
    args=parser.parse_args(argv)
    if Path(sys.prefix).resolve() != (PACKAGE/'.venv').resolve():raise ValueError('use TASK014 .venv Python')
    EVIDENCE=PACKAGE/'evidence'/('owner' if args.owner else 'dev');EVIDENCE.mkdir(parents=True,exist_ok=True)
    if (EVIDENCE/'summary.json').exists():
        history=EVIDENCE/'history';history.mkdir(exist_ok=True)
        attempt=history/f'attempt-{len(list(history.iterdir()))+1:03}';attempt.mkdir()
        for p in EVIDENCE.iterdir():
            if p.is_file():shutil.copyfile(p,attempt/p.name)
    commands=[]; before=revision()
    def write(name,obj): (EVIDENCE/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8',newline='\n')
    write('summary.json',dict(status='RUNNING',revision=before))
    def run(name,command,cwd=PACKAGE,expected=0):
        result=subprocess.run(list(map(str,command)),cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
        output=result.stdout.replace(str(ROOT),'<REPOSITORY>').replace(str(Path.home()),'<USERPROFILE>')
        (EVIDENCE/(name+'.log')).write_text(output,encoding='utf-8',newline='\n')
        commands.append(dict(name=name,command=[str(s).replace(str(ROOT),'<REPOSITORY>') for s in command],cwd=str(cwd).replace(str(ROOT),'<REPOSITORY>'),exit_code=result.returncode,expected_exit=expected,log=name+'.log'))
        write('commands.json',commands);print(f'{name}: exit={result.returncode} (expected {expected})',flush=True)
        if result.returncode != expected:
            write('summary.json',dict(status='FAIL',failed_command=name,revision=before,commands=commands))
            print(output,flush=True);raise SystemExit(1)
    provenance()
    cache=PACKAGE/'.cache';cache.mkdir(exist_ok=True)
    scratch=Path(tempfile.mkdtemp(prefix='verify-',dir=cache));python=Path(sys.executable)
    clean=clone_baseline(scratch/'fresh-clone')
    clean_task=overlay_task(clean)
    # BOTH copies use the immutable task fixture, never the dirty old source.
    staged=stage_preserved(clean)
    write('fresh-clone.json',dict(status='STAGED',baseline=BASELINE,initial_task001='clean Git blob, not preserved working bytes',staging=staged))
    wheels=[]
    for number,(folder,module) in enumerate(PREREQUISITES,1):
        run(f'build-task{number:03}',[python,'-m','build','--wheel','--no-isolation','--outdir',scratch/'wheels',clean/'Source'/folder])
        wheels.append(scratch/'wheels'/f'{module}-0.1.0-py3-none-any.whl')
    wheels.append(PACKAGE/'vendor/rfc8785-0.1.4-py3-none-any.whl')
    run('install-prerequisites',[python,'-m','pip','install','--disable-pip-version-check','--no-index','--no-deps','--force-reinstall',*wheels])
    run('install',[python,'-m','pip','install','--disable-pip-version-check','--no-index','--no-deps','--no-build-isolation','-e','.'])
    run('tests',[python,'-m','pytest','-q','-p','no:cacheprovider','--junitxml='+str(EVIDENCE/'tests.xml')])
    run('smoke',[python,'scripts/smoke.py'])
    run('dependencies',[python,'-m','pip','check'])
    for case in ('nominal','rf-loss','ambiguous'):
        command=[python,'scripts/studio.py','--case',case,'--text']
        if case!='ambiguous':command += ['--view',EVIDENCE/(case+'.html'),'--proof',EVIDENCE/(case+'.model.json'),'--candidate',EVIDENCE/(case+'.model-candidate.jsonl')]
        run('demo-'+case,command,expected=2 if case=='ambiguous' else 0)
    # Exercise staging from the freshly cloned TASK014 code, not its original worktree.
    run('fresh-clone-fixture-tests',[python,'-B','-m','pytest','-q','-p','no:cacheprovider','tests/test_verification.py','--junitxml='+str(EVIDENCE/'fresh-clone.xml')],cwd=clean_task)
    if args.owner:
        for number,(folder,_) in enumerate(PREREQUISITES,1):
            run(f'task{number:03}-regression',[python,'-B','-m','pytest','-q','-p','no:cacheprovider','tests','--junitxml='+str(EVIDENCE/f'task{number:03}-regression.xml')],cwd=clean/'Source'/folder)
    else:
        # Impacted provenance tests only. No complete prior regression suites.
        for folder,file,test in [('host_trust_boundary','test_boundary','test_N18_installed_local_prerequisite_and_release_provenance'),('host_provisioning_intent','test_intent','test_N18_installed_baseline_and_release_hashes')]:
            run('fresh-'+folder,[python,'-B','-m','pytest','-q','-p','no:cacheprovider',f'tests/{file}.py::{test}','--junitxml='+str(EVIDENCE/(folder+'.xml'))],cwd=clean/'Source'/folder)
    run('build',[python,'-m','build','--no-isolation','--outdir',scratch/'dist'])
    run('wheel-env',[python,'-m','venv',scratch/'wheel-env'])
    wheel_python=scratch/'wheel-env/Scripts/python.exe'
    # Jsonschema is needed by strict P226 action validation in the installed package.
    dependency_cache=PACKAGE/'vendor/test-wheels'
    run('wheel-install',[wheel_python,'-m','pip','install','--disable-pip-version-check','--no-index','--find-links',dependency_cache,*wheels,scratch/'dist/bb_host_virtual_control_studio-0.1.0-py3-none-any.whl'])
    run('wheel-smoke',[wheel_python,'scripts/smoke.py'])
    run('wheel-dependencies',[wheel_python,'-m','pip','check'])
    for folder,module in PREREQUISITES:
        for path in (clean/'Source'/folder/'src'/module).glob('*.py'):
            assert path.read_bytes()==(scratch/'wheel-env/Lib/site-packages'/module/path.name).read_bytes()
    for path in (PACKAGE/'src/bb_host_virtual_control_studio').glob('*.py'):
        assert path.read_bytes()==(scratch/'wheel-env/Lib/site-packages/bb_host_virtual_control_studio'/path.name).read_bytes()
    write('environment.json',dict(python=sys.version,installed_project_bytes_match=True,
        artifacts=[dict(path=p.relative_to(PACKAGE).as_posix(),sha256=digest(p.read_bytes()))
                   for d in (scratch/'wheels',scratch/'dist') for p in sorted(d.glob('*'))]))
    provenance();assert before==revision(),'execution-affecting files changed during check'
    counts={}
    for path in EVIDENCE.glob('*.xml'):
        suite=ET.parse(path).getroot().find('testsuite')
        counts[path.name]={k:int(suite.get(k)) for k in ('tests','failures','errors','skipped')}
        assert not any(counts[path.name][k] for k in ('failures','errors','skipped'))
    names=[c.get('name') for c in ET.parse(EVIDENCE/'tests.xml').iter('testcase')]
    assert {n for n in names if n.startswith('test_p226_real_pipeline[')}=={f'test_p226_real_pipeline[P226-T{i:02}]' for i in range(1,25)}
    assert {m[1] for n in names if (m:=re.match(r'test_(N\d{2})_',n))}=={f'N{i:02}' for i in range(1,25)}
    write('fresh-clone.json',dict(status='PASS',baseline=BASELINE,staging=staged,provenance_tests='all prior regressions' if args.owner else 'TASK010/011 targeted provenance only',current_task001_read=False))
    write('summary.json',dict(status='PASS',mode='OWNER_FULL_UAT' if args.owner else 'DEV_CHECK',revision=before,
        tests=counts,oracle_count=24,negative_families=24,demos={'nominal':0,'rf-loss':0,'ambiguous':2},
        ambiguous='expected MODEL_CONTRACT_BLOCKED; never successful replay',smoke='3 PASS, 0 FAIL dev and wheel',
        prior_regressions='ACTUALLY RUN TASK001-013' if args.owner else 'NOT RUN; only two impacted provenance tests',
        gui_manual='NOT RUN; Owner must record separately',baseline_pins=39,release_hashes=10,policy='MATCH',preserved_fixture='MATCH',
        limits=['MODEL_ONLY, no runtime/ARM/output authority','GUI manual acceptance remains separate','No hardware/PWM/servo/flight','No crash durability claim']))
    print(('OWNER FULL UAT' if args.owner else 'DEV CHECK')+' PASS; GUI manual acceptance separate.',flush=True)


if __name__=='__main__':
    try:main()
    except BaseException as error:
        if not isinstance(error,SystemExit) or error.code:
            EVIDENCE.mkdir(parents=True,exist_ok=True)
            path=EVIDENCE/'summary.json';record=json.loads(path.read_bytes()) if path.exists() else {}
            record.update(status='FAIL',error=f'{type(error).__name__}: {error}')
            path.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
        raise
