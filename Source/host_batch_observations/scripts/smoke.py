"""Ten data-only installation/UAT checks through the real prerequisite chain."""

from bb_host_batch_observations import normalize_tick_observations
from scenarios import load_oracles, pipeline, target_batch


def main():
    recipes = {row["id"]: row for row in load_oracles()["cases"]}
    passed = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        passed.append(name)

    def result(number):
        return normalize_tick_observations(target_batch(recipes[f"P215-T{number:02d}"]))

    check("BOOT retained", result(1).has_boot)
    empty = result(2)
    check("empty tick", empty.source_events == empty.valid_control_groups == empty.causal_event_ids == ())
    equivalent = result(17)
    check("exact decimal equivalence", len(equivalent.valid_control_groups) == 1
          and equivalent.valid_control_groups[0].latest_original_at_us == 7500
          and equivalent.has_duplicate_semantic_control)
    conflict = result(9)
    check("INVALID and conflict coexist", conflict.has_invalid_control and conflict.has_distinct_valid_control_conflict)
    rf = result(11)
    check("RF facts independent", rf.rf_has_unknown and rf.rf_has_healthy and not rf.rf_has_lost)
    lifecycle = result(13)
    check("lifecycle observations", lifecycle.has_catastrophe and lifecycle.has_reset and lifecycle.has_ack)
    check("UTF-8 metadata", result(16).causal_event_ids == ("e\u0301", "\u00e9"))
    _, batches = pipeline(recipes["P215-T18"])
    results = [normalize_tick_observations(batch) for batch in batches]
    check("no carryover", not results[-1].valid_control_groups and results[-1].rf_has_unknown)
    try:
        normalize_tick_observations({})
    except TypeError:
        rejected = True
    else:
        rejected = False
    check("wrong caller rejected", rejected)
    try:
        equivalent.valid_control_groups[0].semantic_control["arm_switch"] = True
    except TypeError:
        immutable = True
    else:
        immutable = False
    check("immutable payload", immutable)
    print(f"Smoke: {len(passed)} PASS, 0 FAIL. Observations only; no state/output authority.")


if __name__ == "__main__":
    main()
