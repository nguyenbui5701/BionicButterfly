"""Exercise all P220 recipes through genuine upstream libraries and D2."""

from dataclasses import asdict

from bb_host_guard_triage import triage_guard_evidence
from scenarios import load_oracles, pipeline, source_recipe, expected_fields


def main():
    passed = failed = 0
    for case in load_oracles()["cases"]:
        try:
            _, _, obs, _, temporal, priority, _, health = pipeline(source_recipe(case))
            result = triage_guard_evidence(obs, temporal, priority, health)
            assert asdict(result) == expected_fields(case, obs, temporal, priority)
            passed += 1
        except Exception as error:
            failed += 1
            print(f"{case['id']}: FAIL {error!r}")
    print(f"Smoke: {passed} PASS, {failed} FAIL")
    return int(bool(failed) or passed != 36)


if __name__ == "__main__":
    raise SystemExit(main())
