"""DESIGN_CONFORMANCE_ONLY candidate bytes and private append barrier."""
from dataclasses import dataclass, asdict, field
from decimal import Decimal
from hashlib import sha256
from types import MappingProxyType

from . import jcs

ENGINE = "F1_MODEL_ONLY_M0_0.1.0"
SCHEDULER = "TASK002_FIXED_5MS_MODEL_ONLY"
LABEL = "MODEL_TRACE_CANDIDATE_NOT_OPERATIONAL"
MAX_BYTES = 16_777_216


def _domain(value):
    # Only called on TASK-001's already validated scenario. Binary64 conversion
    # belongs to RFC8785 identity serialization, never to effort calculation.
    if type(value) is Decimal:
        return float(value)
    if type(value) in (dict, MappingProxyType):
        return {k: _domain(v) for k, v in value.items()}
    if type(value) in (list, tuple):
        return [_domain(v) for v in value]
    return value


def header(scenario, policy_raw):
    scenario_digest = sha256(jcs.dumps(_domain(scenario))).hexdigest()
    identity = dict(domain="BIONICBUTTERFLY_G0A1_REPLAY_V1", scenario_digest=scenario_digest,
                    policy_digest=sha256(policy_raw).hexdigest(), engine_revision=ENGINE,
                    scheduler_revision=SCHEDULER, result_contract_version=2, trace_format_version=1)
    return dict(record_type="header", trace_format_version=1, result_contract_version=2,
                scenario_wire_schema_version=2, replay_identity=sha256(jcs.dumps(identity)).hexdigest(),
                scenario_digest=scenario_digest, policy_digest=identity["policy_digest"],
                engine_revision=ENGINE, scheduler_revision=SCHEDULER, scheduler_step_us=5000,
                scope="PC_SIM_ONLY", mixer_revision="G0A1_M0_R11")


@dataclass(frozen=True, slots=True)
class R1TraceCandidateTick:
    tick_index: int
    eval_at_us: int
    state_before: str
    state_after: str
    rf_effective: str
    accepted_frame_age_us: int | None
    causal_event_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    record_type: str = field(default="tick", init=False)
    output_allowed: bool = field(default=False, init=False)
    requested_flap_micro: None = field(default=None, init=False)
    requested_steer_micro: None = field(default=None, init=False)
    input_mode: str = field(default="NONE", init=False)
    mixer_clip_tags: tuple = field(default=(), init=False)
    left_micro_effort: None = field(default=None, init=False)
    right_micro_effort: None = field(default=None, init=False)


def terminal(count):
    # A schema-conformance terminal, explicitly denied as operational execution.
    # The public report describes MODEL completion, not SimulationRunReportV2.
    return dict(record_type="terminal", run_status="FAILED", evaluated_tick_count=count,
                fault_codes=["E_OWNER_DENIED"], evidence_complete=True)


class _ModelJournal:
    """In-memory only, no externally supplied sink or receipt.

    Tests may monkeypatch _fault to inject a failure, never a positive receipt.
    Orphan/short bytes are private and are never returned as acknowledged data.
    """
    def __init__(self):
        self._parts = []
        self._size = 0
        self._failed = False
        self._orphan = b""

    def _fault(self, record):
        return None

    def append(self, record):
        if self._failed:
            return False
        try:
            record = asdict(record) if type(record) is R1TraceCandidateTick else record
            fault = self._fault(record)
            if fault in ("BEFORE_APPEND", "SERIALIZER"):
                raise ValueError("injected model append/serializer failure")
            raw = jcs.dumps(record) + b"\n"
            if fault == "QUOTA" or self._size + len(raw) > MAX_BYTES:
                raise ValueError("model journal quota")
            if fault in ("SHORT_WRITE", "AFTER_WRITE_BEFORE_ACK"):
                self._orphan = raw[:-1] if fault == "SHORT_WRITE" else raw
                raise OSError("injected missing complete append acknowledgement")
            self._parts.append(raw)
            self._size += len(raw)
            return True
        except (TypeError, ValueError, OSError, RecursionError):
            self._failed = True
            return False

    def committed_bytes(self):
        return b"".join(self._parts)
