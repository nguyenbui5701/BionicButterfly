"""Representative real-pipeline smoke checks, also run on installed wheels."""

from dataclasses import asdict, FrozenInstanceError

from bb_host_safety_priority_kernel import SafetyState, assess_safety_priority
from scenarios import load_oracles, pipeline


def main():
    cases = load_oracles()["cases"]
    passed = 0
    for index in (1, 2, 3, 5, 9, 11, 13, 16, 18, 22):
        case = cases[index - 1]
        _, _, obs, _, temporal = pipeline(case)
        state = SafetyState(case["pre_state"])
        result = assess_safety_priority(state, obs, temporal)
        expected = dict(case["expected"], tick_index=case["eval_at_us"] // 5000,
                        eval_at_us=case["eval_at_us"], pre_state=state)
        assert asdict(result) == expected, case["id"]
        passed += 1
    try:
        assess_safety_priority("ACTUATION_ACTIVE", obs, temporal)
    except TypeError:
        passed += 1
    else:
        raise AssertionError("raw state string accepted")
    try:
        result.provisional_next_state = SafetyState.ACTUATION_ACTIVE
    except FrozenInstanceError:
        passed += 1
    else:
        raise AssertionError("mutable assessment")
    print(f"Smoke: {passed} PASS, 0 FAIL")


if __name__ == "__main__":
    main()
