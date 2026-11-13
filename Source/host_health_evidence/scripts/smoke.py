"""Smoke the real pipeline and installed library against all release recipes."""

from dataclasses import asdict

from bb_host_health_evidence import assess_health_evidence
from scenarios import load_oracles, pipeline


def main():
    passed = failed = 0
    for case in load_oracles()["cases"]:
        try:
            _, _, obs, _, temporal, priority, prior_rf = pipeline(case)
            result = assess_health_evidence(obs, temporal, priority, prior_rf)
            assert asdict(result) == case["expected"]
            passed += 1
        except Exception as error:
            failed += 1
            print(f"{case['id']}: FAIL {error!r}")
    print(f"Smoke: {passed} PASS, {failed} FAIL")
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
