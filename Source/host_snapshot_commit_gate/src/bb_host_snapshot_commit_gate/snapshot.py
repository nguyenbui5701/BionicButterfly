"""Frozen TEST_ONLY history; not a trusted restore or state authorization."""

from dataclasses import dataclass

from bb_host_health_evidence import RFStatus
from bb_host_safety_priority_kernel import SafetyState


@dataclass(frozen=True, slots=True)
class OwnerSnapshot:
    generation: int
    last_tick_index: int | None
    last_eval_at_us: int | None
    state: SafetyState
    last_accepted_control_at_us: int | None
    last_uncontested_healthy_rf_at_us: int | None
    last_rf_status: RFStatus | None
    last_rf_original_at_us: int | None
    low_first_original_at_us: int | None
    low_qualified_committed_eval_at_us: int | None
    high_edge_original_at_us: int | None
    high_edge_committed_eval_at_us: int | None
    held_micro_effort: tuple[int, int] | None
    recoverable_causes: tuple[str, ...]


def genesis_snapshot() -> OwnerSnapshot:
    return OwnerSnapshot(0, None, None, SafetyState.BOOT, None, None, None, None,
                         None, None, None, None, None, ())


def _require(condition):
    if not condition:
        raise ValueError("inconsistent TEST_ONLY snapshot history")


def _validate_snapshot(snapshot):
    if type(snapshot) is not OwnerSnapshot or type(snapshot.state) is not SafetyState:
        raise TypeError("expected exact OwnerSnapshot and SafetyState")
    _require(type(snapshot.generation) is int and snapshot.generation >= 0)
    _require(type(snapshot.recoverable_causes) is tuple)
    _require(all(type(cause) is str for cause in snapshot.recoverable_causes))
    _require(snapshot.held_micro_effort is None)
    if snapshot.last_tick_index is None or snapshot.last_eval_at_us is None:
        _require(snapshot == genesis_snapshot())
        return
    _require(type(snapshot.last_tick_index) is int and 0 <= snapshot.last_tick_index <= 12000)
    _require(type(snapshot.last_eval_at_us) is int and snapshot.last_eval_at_us == snapshot.last_tick_index * 5000)
    _require(snapshot.state is not SafetyState.BOOT)
    for value in (snapshot.last_accepted_control_at_us, snapshot.last_uncontested_healthy_rf_at_us,
                  snapshot.last_rf_original_at_us, snapshot.low_first_original_at_us,
                  snapshot.low_qualified_committed_eval_at_us, snapshot.high_edge_original_at_us,
                  snapshot.high_edge_committed_eval_at_us):
        _require(value is None or (type(value) is int and 0 <= value <= snapshot.last_eval_at_us))
    status, rf_at = snapshot.last_rf_status, snapshot.last_rf_original_at_us
    _require((status is None) == (rf_at is None))
    if status is not None and type(status) is not RFStatus:
        raise TypeError("expected exact RFStatus")
    healthy_at = snapshot.last_uncontested_healthy_rf_at_us
    if status is RFStatus.HEALTHY:
        _require(healthy_at == rf_at)
    elif status is None:
        _require(healthy_at is None)
    elif healthy_at is not None:
        _require(healthy_at <= rf_at)
    low, qualified = snapshot.low_first_original_at_us, snapshot.low_qualified_committed_eval_at_us
    edge, edge_commit = snapshot.high_edge_original_at_us, snapshot.high_edge_committed_eval_at_us
    if qualified is not None:
        _require(low is not None and qualified % 5000 == 0 and qualified - low >= 20000)
    _require((edge is None) == (edge_commit is None))
    if edge is not None:
        _require(edge <= edge_commit and edge_commit % 5000 == 0)
    if snapshot.state is SafetyState.DISARMED:
        _require(edge is None)
    elif snapshot.state is SafetyState.ARM_CHECK:
        _require(low is None and qualified is None)
    else:
        _require(low is None and qualified is None and edge is None)
