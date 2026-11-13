"""Small installation/UAT check. No simulator, dispatcher or device access."""

import json
from pathlib import Path

from bb_host_preflight_m0 import AcceptedPreflight, validate_wire
from bb_host_virtual_ticks import iter_virtual_ticks


def main():
    design = Path(__file__).resolve().parents[3] / "Design"
    schema = json.loads((design / "contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json").read_text(encoding="utf-8"))
    data = json.loads((design / "fixtures/P210_MINIMAL_WIRE_V2.json").read_text(encoding="utf-8"))

    def accept():
        result = validate_wire(json.dumps(data).encode(), schema)
        assert isinstance(result, AcceptedPreflight)
        return result

    data["duration_us"] = 15000
    data["events"] += [dict(event_id=str(t), event_at_us=t, type="SIM_RESET", payload={})
                       for t in (4999, 5000, 5001)]
    batches = tuple(iter_virtual_ticks(accept()))
    assert [b.eval_at_us for b in batches] == [0, 5000, 10000, 15000]
    assert [e["event_id"] for e in batches[0].events] == ["boot"]
    assert [e["event_at_us"] for e in batches[1].events] == [4999, 5000]
    assert [e["event_at_us"] for e in batches[2].events] == [5001]
    assert batches[3].events == ()
    data["duration_us"] = 60000000
    assert sum(1 for _ in iter_virtual_ticks(accept())) == 12001
    for bad in (data, validate_wire(b"{}", schema)):
        try:
            iter_virtual_ticks(bad)
        except TypeError:
            pass
        else:
            raise AssertionError("invalid caller was accepted")
    print("Smoke: 8 PASS, 0 FAIL (clock, BOOT, boundaries, empty tick, max duration, two invalid callers).")


if __name__ == "__main__":
    main()
