"""PRIVATE TEST_ONLY fixture seeding. Never scenario restore or host authority."""

from .snapshot import _validate_snapshot
from .ledger import TestOnlySnapshotLedger
from .journal import JournalFaultMode


def _seed_for_test(snapshot, *, fault_mode=JournalFaultMode.NONE, byte_quota=16777216):
    _validate_snapshot(snapshot)
    ledger = TestOnlySnapshotLedger()
    ledger._TestOnlySnapshotLedger__snapshot = snapshot
    ledger._TestOnlySnapshotLedger__journal._configure_test_fault(fault_mode, byte_quota)
    return ledger
