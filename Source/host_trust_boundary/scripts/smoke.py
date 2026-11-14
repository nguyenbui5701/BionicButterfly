"""Run every authored P222 oracle against genuine preflight and installed E2."""
from scenarios import INDEX, exercise


def main():
    failures = []
    for case in INDEX["cases"]:
        try:
            exercise(case)
        except Exception as error:
            failures.append((case["id"], repr(error)))
    for case_id, error in failures:
        print(case_id, error)
    print(f"Smoke: {len(INDEX['cases']) - len(failures)} PASS, {len(failures)} FAIL")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
