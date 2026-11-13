"""Private fixed in-memory test append path. NOT an R1 trace writer/receipt."""

from enum import Enum


class JournalFaultMode(str, Enum):
    NONE = "NONE"
    FAIL_BEFORE_APPEND = "FAIL_BEFORE_APPEND"
    SHORT_WRITE = "SHORT_WRITE"
    FAIL_AFTER_WRITE_BEFORE_ACK = "FAIL_AFTER_WRITE_BEFORE_ACK"
    QUOTA_DENIED = "QUOTA_DENIED"
    SERIALIZATION_FAILED = "SERIALIZATION_FAILED"


class TestOnlyAtomicJournal:
    __slots__ = ("__records", "__fragment", "__ack_count", "__marker", "__mode", "__quota", "__used")

    def __init__(self):
        self.__records = []
        self.__fragment = b""
        self.__ack_count = 0
        self.__marker = object()
        self.__mode = JournalFaultMode.NONE
        self.__quota = 16777216
        self.__used = 0

    @property
    def records(self):
        return tuple(self.__records)

    @property
    def partial_bytes(self):
        return self.__fragment

    @property
    def acknowledged_append_count(self):
        return self.__ack_count

    def _configure_test_fault(self, mode, quota):
        if type(mode) is not JournalFaultMode:
            raise TypeError("expected exact TEST_ONLY journal fault mode")
        if type(quota) is not int or quota < 0 or self.__used or self.__records or self.__ack_count:
            raise ValueError("fault setup only on unused private test journal")
        self.__mode, self.__quota = mode, quota

    def _check_serialization_fault(self):
        if self.__mode is JournalFaultMode.SERIALIZATION_FAILED:
            raise ValueError("injected TEST_ONLY serialization failure")

    def _append(self, record):
        if type(record) is not bytes or not record.endswith(b"\n") or record.count(b"\n") != 1:
            raise ValueError("expected one complete internal record")
        if self.__mode is JournalFaultMode.FAIL_BEFORE_APPEND:
            raise OSError("injected TEST_ONLY before-append failure")
        if self.__mode is JournalFaultMode.QUOTA_DENIED or self.__used + len(record) > self.__quota:
            raise ValueError("TEST_ONLY journal quota denied")
        if self.__mode is JournalFaultMode.SHORT_WRITE:
            self.__fragment = record[:-1]
            self.__used += len(self.__fragment)
            return None
        self.__records.append(record)
        self.__used += len(record)
        if self.__mode is JournalFaultMode.FAIL_AFTER_WRITE_BEFORE_ACK:
            raise OSError("injected TEST_ONLY missing acknowledgment after full write")
        self.__ack_count += 1
        return self.__marker

    def _is_full_ack(self, ack, record, prior_count):
        return (ack is self.__marker and self.__ack_count == prior_count + 1
                and len(self.__records) == self.__ack_count and self.__records[-1] == record and not self.__fragment)
