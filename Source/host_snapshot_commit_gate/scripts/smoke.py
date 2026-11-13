"""All 48 E1 oracle outcomes, including expected DEFER and terminal failures."""

from scenarios import exercise, load_oracles


def main():
    passed = failed = 0
    for case in load_oracles()["cases"]:
        try:
            ledger, prior, result, _ = exercise(case)
            expected = case["expected"]
            assert result.outcome.value == expected["outcome"]
            assert ledger.snapshot.generation - prior.generation == expected["snapshot_advance"]
            assert ledger.journal_acknowledged_append_count == expected["journal_acknowledged_append_count"]
            assert expected["next_test_state"] is None or ledger.snapshot.state.value == expected["next_test_state"]
            assert result.requires_full_fsm is True
            passed += 1
        except Exception as error:
            failed += 1
            print(f"{case['id']}: FAIL {error!r}")
    print(f"Smoke: {passed} PASS, {failed} FAIL")
    return int(bool(failed) or passed != 48)


if __name__ == "__main__":
    raise SystemExit(main())
