"""Representative proposal outcomes through the real upstream pipeline."""

from dataclasses import asdict, FrozenInstanceError

from bb_host_arm_qualification import propose_arm_qualification
from bb_host_safety_priority_kernel import SafetyState
from scenarios import load_oracles, pipeline


def main():
    cases = load_oracles()["cases"]
    passed = 0
    for number in (1, 2, 3, 6, 7, 9, 11, 13, 14, 19, 21, 29, 31, 32):
        case = cases[number - 1]
        _, _, obs, _, temporal, priority, window, verdict = pipeline(case)
        result = propose_arm_qualification(obs, temporal, priority, window, verdict)
        expected = dict(case["expected"], tick_index=case["eval_at_us"] // 5000,
                        eval_at_us=case["eval_at_us"], pre_state=SafetyState(case["pre_state"]))
        assert asdict(result) == expected, case["id"]
        passed += 1
    try:
        propose_arm_qualification({}, temporal, priority, window, verdict)
    except TypeError:
        passed += 1
    else:
        raise AssertionError("invalid caller accepted")
    try:
        result.requires_full_fsm = False
    except FrozenInstanceError:
        passed += 1
    else:
        raise AssertionError("mutable proposal")
    print(f"Smoke: {passed} PASS, 0 FAIL")


if __name__ == "__main__":
    main()
