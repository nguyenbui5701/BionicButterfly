"""TEST_ONLY prepare -> complete append -> private ack -> frozen snapshot swap."""

from dataclasses import dataclass, replace
from enum import Enum
import json

from bb_host_safety_priority_kernel import SafetyState
from bb_host_health_evidence import RFEvidenceKind

from .snapshot import OwnerSnapshot, genesis_snapshot, _validate_snapshot
from .journal import TestOnlyAtomicJournal
from ._validation import _validate_tick


class CommitOutcome(str, Enum):
    COMMITTED_TEST_ONLY = "COMMITTED_TEST_ONLY"
    DEFERRED_NEEDS_FULL_FSM = "DEFERRED_NEEDS_FULL_FSM"
    FAILED_INCOMPLETE_EVIDENCE = "FAILED_INCOMPLETE_EVIDENCE"


@dataclass(frozen=True, slots=True)
class SnapshotCommitResult:
    outcome: CommitOutcome
    tick_index: int
    eval_at_us: int
    snapshot_generation: int | None
    requires_full_fsm: bool


_ARMED = (SafetyState.ARM_CHECK, SafetyState.ARMED_IDLE, SafetyState.ACTUATION_ACTIVE)


def _decision(snapshot, observations, temporal, health):
    state = snapshot.state
    if state is SafetyState.FAULT_LATCHED:
        return state, "LATCH_PERSIST"
    if observations.has_catastrophe:
        return SafetyState.FAULT_LATCHED, "CATASTROPHE_LATCH"
    if state is SafetyState.CONTINGENCY:
        return state, "CONTINGENCY_HOLD"
    if state in _ARMED:
        if health.rf_evidence is RFEvidenceKind.AMBIGUOUS_CURRENT:
            return None, "DEFER"
        if (observations.has_invalid_control or observations.has_distinct_valid_control_conflict
                or observations.rf_has_lost or (observations.rf_has_unknown and not observations.rf_has_healthy)):
            return SafetyState.CONTINGENCY, "ARMED_EXPLICIT_CONTINGENCY"
        if not temporal.prior_control_within_timeout or not temporal.prior_rf_within_timeout:
            return SafetyState.CONTINGENCY, "ARMED_STALE_CONTINGENCY"
        return None, "DEFER"
    if observations.has_reset:
        return SafetyState.SELF_TEST, "NONARMED_RESET"
    if state is SafetyState.BOOT:
        return SafetyState.SELF_TEST, "BOOT_INITIALIZE"
    return state, "NONARMED_HOLD"


def _serialize_record(tick_index, eval_at_us, pre_state, next_state, decision):
    # Restricted ASCII fields only; this is NOT general RFC8785 JCS/R1 trace.
    record = dict(format="BB_E1_TEST_JOURNAL_V1", tick_index=tick_index, eval_at_us=eval_at_us,
                  pre_state=pre_state.value, next_test_state=next_state.value, decision_kind=decision)
    return (json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


class TestOnlySnapshotLedger:
    """No public restore, supplied journal, receipt, callback or output interface.

    Python privacy is not a security boundary. This class proves only internal
    in-memory test sequencing, never authenticated or crash-durable history.
    """

    __slots__ = ("__snapshot", "__journal", "__failed")

    def __init__(self):
        self.__snapshot = genesis_snapshot()
        self.__journal = TestOnlyAtomicJournal()
        self.__failed = False

    @property
    def snapshot(self) -> OwnerSnapshot:
        return self.__snapshot

    @property
    def journal_records(self):
        return self.__journal.records

    @property
    def journal_partial_bytes(self):
        return self.__journal.partial_bytes

    @property
    def journal_acknowledged_append_count(self):
        return self.__journal.acknowledged_append_count

    @property
    def failure_status(self):
        return CommitOutcome.FAILED_INCOMPLETE_EVIDENCE if self.__failed else None

    def commit_tick(self, observations, temporal, priority, health, triage) -> SnapshotCommitResult:
        if self.__failed:
            raise ValueError("terminal FAILED_INCOMPLETE_EVIDENCE ledger cannot accept or retry ticks")
        prior = self.__snapshot
        if type(self.__journal) is not TestOnlyAtomicJournal:
            raise TypeError("expected the fixed private TEST_ONLY journal")
        _validate_snapshot(prior)
        _validate_tick(prior, observations, temporal, priority, health, triage)
        next_state, decision = _decision(prior, observations, temporal, health)
        if next_state is None:
            return SnapshotCommitResult(CommitOutcome.DEFERRED_NEEDS_FULL_FSM,
                                        observations.tick_index, observations.eval_at_us, None, True)
        changes = dict(generation=prior.generation + 1, last_tick_index=observations.tick_index,
                       last_eval_at_us=observations.eval_at_us, state=next_state)
        if decision not in ("LATCH_PERSIST", "CONTINGENCY_HOLD", "NONARMED_HOLD"):
            changes.update(low_first_original_at_us=None, low_qualified_committed_eval_at_us=None,
                           high_edge_original_at_us=None, high_edge_committed_eval_at_us=None, held_micro_effort=None)
        if decision in ("NONARMED_RESET", "CATASTROPHE_LATCH"):
            changes["recoverable_causes"] = ()
        candidate = replace(prior, **changes)
        _validate_snapshot(candidate)
        try:
            self.__journal._check_serialization_fault()
            record = _serialize_record(observations.tick_index, observations.eval_at_us, prior.state, next_state, decision)
            count = self.__journal.acknowledged_append_count
            ack = self.__journal._append(record)
            if not self.__journal._is_full_ack(ack, record, count):
                raise ValueError("no private complete-append acknowledgment")
        except Exception:
            self.__failed = True
            return SnapshotCommitResult(CommitOutcome.FAILED_INCOMPLETE_EVIDENCE,
                                        observations.tick_index, observations.eval_at_us, None, True)
        self.__snapshot = candidate
        return SnapshotCommitResult(CommitOutcome.COMMITTED_TEST_ONLY,
                                    observations.tick_index, observations.eval_at_us, candidate.generation, True)
