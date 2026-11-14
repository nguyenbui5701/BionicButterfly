"""A single genuine F1 invocation; no model state machine or output publisher."""
from dataclasses import dataclass, field
from bb_host_integrated_fsm_model import run_fsm_model, ModelReplayReport
from bb_host_trust_boundary import ClaimedHostFingerprint
from .session import session_to_wire_v2, SessionError

BANNER = 'MODEL_ONLY / NOT PROVISIONED / NO OUTPUT'
EFFORT_LABEL = 'Dimensionless model effort; not servo position, PWM, lift or flight readiness.'


@dataclass(frozen=True, slots=True)
class VirtualRuntimeBoundary:
    runtime_authorized: bool = field(default=False, init=False)
    output_allowed: bool = field(default=False, init=False)
    actual_virtual_output: None = field(default=None, init=False)
    physical_output: None = field(default=None, init=False)
    control_trace_sha256: None = field(default=None, init=False)
    requires_owner_provisioning: bool = field(default=True, init=False)


@dataclass(frozen=True, slots=True)
class StudioSessionReport:
    outcome: str
    wire_v2: bytes
    model: ModelReplayReport | None
    diagnostic: str | None
    boundary: VirtualRuntimeBoundary = field(default_factory=VirtualRuntimeBoundary, init=False)

    @property
    def model_ticks(self):
        return self.model.model_ticks if self.model is not None else ()


def run_studio_session(raw_actions: bytes, frozen_wire_v2_schema: dict, policy_raw: bytes,
                       claimed_host: ClaimedHostFingerprint, intent_raw: bytes,
                       engine_artifact: bytes, scheduler_artifact: bytes) -> StudioSessionReport:
    try:
        wire = session_to_wire_v2(raw_actions)
    except (SessionError, TypeError) as error:
        return StudioSessionReport('SESSION_REJECTED', b'', None, str(error))
    model = run_fsm_model(wire, frozen_wire_v2_schema, policy_raw, claimed_host,
                         intent_raw, engine_artifact, scheduler_artifact)
    return StudioSessionReport(model.outcome.value, wire, model, model.diagnostic)
