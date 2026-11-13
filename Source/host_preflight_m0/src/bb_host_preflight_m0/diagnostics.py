"""Closed external sidecar, separate from all runtime reports and traces."""

from hashlib import sha256
import json

_STAGES = {
    "RAW": "INPUT_TOO_LARGE UTF8_INVALID UTF8_BOM",
    "LEX": "JSON_SYNTAX JSON_DUPLICATE_KEY JSON_DEPTH JSON_SURROGATE JSON_NONFINITE",
    "SCHEMA": "SCHEMA_REQUIRED SCHEMA_UNKNOWN_FIELD SCHEMA_TYPE SCHEMA_ENUM SCHEMA_RANGE "
              "WIRE_VERSION CONTEXT_DENIED PROVENANCE_DENIED CONFIG_ID EVENT_TYPE DURATION_GRID EVENT_COUNT",
    "SEMANTIC": "EVENT_ID_DUPLICATE BOOT_SEQUENCE EVENT_TIMESTAMP_ORDER EVENT_TIMESTAMP_RANGE "
                "IDENTIFIER_BYTES IDENTIFIER_CONTROL DECIMAL_PRECISION",
}
STAGES = {"P_" + code: stage for stage, codes in _STAGES.items() for code in codes.split()}


def pointer(path: tuple) -> str:
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in path)


class Issue(Exception):
    def __init__(self, code: str, path: tuple = ()):
        super().__init__(code)
        self.code, self.path = code, path


def sidecar(raw: bytes, issue: Issue) -> dict:
    base = None
    if issue.code == "P_EVENT_ID_DUPLICATE":
        base = "E_DUPLICATE_EVENT_ID"
    elif issue.code in ("P_CONTEXT_DENIED", "P_PROVENANCE_DENIED"):
        base = "E_CONTEXT_DENIED"
    return {
        "diagnostic_format_version": 1,
        "scope": "PC_SIM_ONLY",
        "run_status": "VALIDATION_REJECTED",
        "evaluated_tick_count": 0,
        "evidence_complete": False,
        "raw_input_sha256": sha256(raw).hexdigest(),
        "primary_issue": {
            "code": issue.code, "stage": STAGES[issue.code],
            "json_pointer": pointer(issue.path), "frozen_base_error_code": base,
        },
    }


def canonical_sidecar(diagnostic: dict) -> bytes:
    """Stable sidecar serialization; not a canonical runtime trace writer."""
    return json.dumps(diagnostic, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
