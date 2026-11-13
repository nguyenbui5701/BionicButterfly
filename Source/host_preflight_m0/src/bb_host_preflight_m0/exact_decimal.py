"""Exact, context-independent JSON decimal predicates; never binary floating point."""

from dataclasses import dataclass
from decimal import Decimal
import re

NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")


@dataclass(frozen=True)
class ExactNumber:
    negative: bool
    digits: str
    exponent: int

    @classmethod
    def parse(cls, token: str) -> "ExactNumber":
        if not isinstance(token, str) or NUMBER.fullmatch(token) is None:
            raise ValueError("expected one JSON number token")
        negative = token.startswith("-")
        body = token.lstrip("-").lower()
        mantissa, _, exp = body.partition("e")
        whole, _, fraction = mantissa.partition(".")
        digits = (whole + fraction).lstrip("0")
        if not digits:
            return cls(False, "0", 0)
        # An exponent larger than the entire token cannot cancel its mantissa.
        # Saturation preserves every bounded-domain comparison and integrality
        # predicate below. Such a nonzero value can never be accepted by wire v2.
        exp_digits = exp.lstrip("+-").lstrip("0") or "0"
        bound = len(token) + 32
        large = len(exp_digits) > len(str(bound)) or (
            len(exp_digits) == len(str(bound)) and exp_digits > str(bound)
        )
        exponent = bound if large else int(exp_digits)
        if exp.startswith("-"):
            exponent = -exponent
        exponent -= len(fraction)
        trimmed = digits.rstrip("0")
        exponent += len(digits) - len(trimmed)
        return cls(negative, trimmed, exponent)

    def compare_int(self, other: int) -> int:
        """Compare against a small schema bound without expanding exponents."""
        if self.digits == "0":
            return (0 > other) - (0 < other)
        if self.negative != (other < 0):
            return -1 if self.negative else 1
        if other == 0:
            return -1 if self.negative else 1
        target = str(abs(other))
        length = len(self.digits) + self.exponent
        if length != len(target):
            comparison = (length > len(target)) - (length < len(target))
        else:
            width = max(len(self.digits), len(target))
            left, right = self.digits.ljust(width, "0"), target.ljust(width, "0")
            comparison = (left > right) - (left < right)
        return -comparison if self.negative else comparison

    @property
    def integral(self) -> bool:
        return self.exponent >= 0

    def bounded_int(self) -> int:
        if not self.integral or len(self.digits) + self.exponent > 16:
            raise ValueError("not a bounded integer")
        value = int(self.digits) * 10 ** self.exponent
        return -value if self.negative else value

    def micros(self) -> int:
        if self.compare_int(-1) < 0 or self.compare_int(1) > 0:
            raise ValueError("pilot value outside [-1, 1]")
        if self.exponent < -6:
            raise ValueError("pilot value is not an exact millionth")
        value = int(self.digits) * 10 ** (self.exponent + 6)
        return -value if self.negative else value

    def accepted_value(self) -> int | Decimal:
        if self.integral:
            return self.bounded_int()
        # Called only after the bounded wire domain and micro precision pass.
        return Decimal((int(self.negative), tuple(map(int, self.digits)), self.exponent))


def normalize_exact_micros(raw_number_token: str) -> int:
    """Normalize one pilot JSON number token in [-1,1]; reject, never round."""
    return ExactNumber.parse(raw_number_token).micros()


normalizeExactMicros = normalize_exact_micros
