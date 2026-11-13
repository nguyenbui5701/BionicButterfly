"""Installation smoke check, not a simulator executable. Run from any cwd."""

import json
from pathlib import Path

from bb_host_preflight_m0 import validateWire, normalizeExactMicros, mixM0

DESIGN = Path(__file__).resolve().parents[3] / "Design"
schema = json.loads((DESIGN / "contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_text(encoding="utf-8"))
for filename in ("P210_MINIMAL_WIRE_V2.json", "P212_POSITIVE_INBAND_UART_INVALID_V2.json"):
    assert validateWire((DESIGN / "fixtures" / filename).read_bytes(), schema).status == "ACCEPTED_PREFLIGHT"
assert validateWire(b"\xff", schema).diagnostic["primary_issue"]["code"] == "P_UTF8_INVALID"
assert validateWire(b'{"a":0,"a":1}', schema).diagnostic["primary_issue"]["code"] == "P_JSON_DUPLICATE_KEY"
assert normalizeExactMicros("1e-6") == 1
assert mixM0(500000, 250000) == (250000, 750000, ())
print("Smoke: 6 PASS, 0 FAIL. PC-only library; no core runner instantiated.")
