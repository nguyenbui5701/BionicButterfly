"""Bounded strict JSON reader preserving exact number tokens and member order.

Scanning is left-to-right, so character positions have the same ordering as
raw UTF-8 byte positions after strict decoding. No later token can win over
an earlier offending token. Public syntax/depth/surrogate/nonfinite paths
remain root; only duplicate members disclose their known parent path.
"""

from json.decoder import scanstring

from .diagnostics import Issue
from .exact_decimal import ExactNumber, NUMBER


class Reader:
    def __init__(self, text: str):
        self.text, self.pos = text, 0

    def skip(self):
        while self.pos < len(self.text) and self.text[self.pos] in " \r\n\t":
            self.pos += 1

    def syntax(self):
        raise Issue("P_JSON_SYNTAX")

    def string(self) -> str:
        try:
            value, end = scanstring(self.text, self.pos + 1, True)
        except ValueError:
            self.syntax()
        # Syntax wins over surrogate within a single malformed string token.
        if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            raise Issue("P_JSON_SURROGATE")
        self.pos = end
        return value

    def value(self, path=(), depth=0):
        self.skip()
        if self.pos >= len(self.text):
            self.syntax()
        char = self.text[self.pos]
        if char in "{[":
            if depth >= 16:
                raise Issue("P_JSON_DEPTH")
            self.pos += 1
            self.skip()
            is_object = char == "{"
            closing = "}" if is_object else "]"
            result = {} if is_object else []
            if self.pos < len(self.text) and self.text[self.pos] == closing:
                self.pos += 1
                return result
            while True:
                self.skip()
                if is_object:
                    if self.pos >= len(self.text) or self.text[self.pos] != '"':
                        self.syntax()
                    key = self.string()
                    if key in result:
                        raise Issue("P_JSON_DUPLICATE_KEY", path + (key,))
                    self.skip()
                    if self.pos >= len(self.text) or self.text[self.pos] != ":":
                        self.syntax()
                    self.pos += 1
                    result[key] = self.value(path + (key,), depth + 1)
                else:
                    result.append(self.value(path + (len(result),), depth + 1))
                self.skip()
                if self.pos >= len(self.text):
                    self.syntax()
                delimiter = self.text[self.pos]
                self.pos += 1
                if delimiter == closing:
                    return result
                if delimiter != ",":
                    self.syntax()
                # Closing delimiter after a comma is invalid, not an empty value.
        if char == '"':
            return self.string()
        for token, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(token, self.pos):
                self.pos += len(token)
                return value
        for token in ("NaN", "Infinity", "-Infinity"):
            if self.text.startswith(token, self.pos):
                end = self.pos + len(token)
                if end < len(self.text) and self.text[end] not in " \r\n\t,]}":
                    self.syntax()
                raise Issue("P_JSON_NONFINITE")
        number = NUMBER.match(self.text, self.pos)
        if number:
            self.pos = number.end()
            return ExactNumber.parse(number.group())
        self.syntax()

    def read(self):
        result = self.value()
        self.skip()
        if self.pos != len(self.text):
            self.syntax()
        return result
