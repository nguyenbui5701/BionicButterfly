"""All P223 recipes through actual TASK-001 -> E2 -> E3."""
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
