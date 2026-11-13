"""Small integration smoke suite through the real prerequisite libraries."""

from dataclasses import FrozenInstanceError, asdict

from bb_host_temporal_guard_facts import evaluate_temporal_guard_facts
from scenarios import load_oracles, pipeline, synthetic_prior


def main():
    cases = load_oracles()["cases"]
    passed = 0
    for number in (1, 3, 4, 5, 6, 15, 19, 20, 21, 22):
        case = cases[number - 1]
        observations = pipeline(case)[2]
        prior = synthetic_prior(case)
        result = evaluate_temporal_guard_facts(observations, prior)
        assert asdict(result) == case["expected"], case["id"]
        passed += 1
    try:
        evaluate_temporal_guard_facts({}, prior)
    except TypeError:
        passed += 1
    else:
        raise AssertionError("wrong caller type accepted")
    try:
        result.prior_control_age_us = 0
    except FrozenInstanceError:
        passed += 1
    else:
        raise AssertionError("mutable output")
    print(f"Smoke: {passed} PASS, 0 FAIL")


if __name__ == "__main__":
    main()
