"""Read-only pinned input adapter. No session-supplied reference identities."""
import hashlib
import json
from pathlib import Path
from bb_host_trust_boundary import ClaimedHostFingerprint

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
CASES = {'nominal': 'NOMINAL', 'rf-loss': 'RF_LOSS', 'ambiguous': 'AMBIGUOUS'}


def frozen_bytes(path):
    record = json.loads((PACKAGE / 'evidence/baseline.json').read_bytes())
    pins = {r['path']: r['git_blob_sha1'] for r in record['pinned_files'] + record['release_files']}
    raw = (ROOT / path).read_bytes()
    if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != pins[path]:
        raise ValueError('frozen fixture mismatch: ' + path)
    return raw


def session(case):
    return frozen_bytes('Design/fixtures/P226_STUDIO_SESSION_' + CASES[case] + '.json')


def dependencies():
    e2 = json.loads(frozen_bytes('Design/fixtures/P222_HOST_REFERENCE_ORACLE_INDEX.json'))
    e3 = json.loads(frozen_bytes('Design/fixtures/P223_HOST_PROVISIONING_INTENT_ORACLE_INDEX.json'))
    engine = e3['engine_artifact_utf8_test_only'].encode()
    scheduler = e3['scheduler_artifact_utf8_test_only'].encode()
    assert b'TEST_ONLY' in engine and b'TEST_ONLY' in scheduler
    return dict(frozen_wire_v2_schema=json.loads(frozen_bytes('Design/contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json')),
                policy_raw=frozen_bytes('Design/contracts/SIM_POLICY_22A_R1.canonical.json'),
                claimed_host=ClaimedHostFingerprint(**e2['reference_host_claim']),
                intent_raw=json.dumps(e3['base_intent'], sort_keys=True, separators=(',', ':')).encode(),
                engine_artifact=engine, scheduler_artifact=scheduler)
