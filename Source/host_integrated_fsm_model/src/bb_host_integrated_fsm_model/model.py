"""One stateful, counterfactual R1 model. No operational authority or IO."""
from dataclasses import dataclass, field, replace
from decimal import Decimal
from enum import Enum
from hashlib import sha256

from bb_host_preflight_m0 import validate_wire, RejectedPreflight, mix_m0
from bb_host_virtual_ticks import iter_virtual_ticks
from bb_host_batch_observations import normalize_tick_observations
from bb_host_temporal_guard_facts import evaluate_temporal_guard_facts, PriorCommittedTimestampFacts
from bb_host_safety_priority_kernel import assess_safety_priority, SafetyState as State
from bb_host_health_evidence import assess_health_evidence, PriorCommittedRFStatus, RFStatus, RFEvidenceKind
from bb_host_guard_triage import triage_guard_evidence
from bb_host_trust_boundary import assess_reference_host_boundary, ClaimedHostFingerprint, HostReferenceOutcome
from bb_host_provisioning_intent import inspect_provisioning_intent, ProvisioningIntentOutcome
from bb_host_integrated_shadow_replay import run_shadow_replay

from .trace import _ModelJournal, R1TraceCandidateTick, header, terminal, LABEL


class ModelOutcome(str, Enum):
    MODEL_INPUT_REJECTED = "MODEL_INPUT_REJECTED"
    MODEL_REFERENCE_BLOCKED = "MODEL_REFERENCE_BLOCKED"
    MODEL_REPLAY_COMPLETE = "MODEL_REPLAY_COMPLETE"
    MODEL_EVIDENCE_INCOMPLETE = "MODEL_EVIDENCE_INCOMPLETE"
    MODEL_CONTRACT_BLOCKED = "MODEL_CONTRACT_BLOCKED"


@dataclass(frozen=True, slots=True)
class ModeledPrior:
    state: State = State.BOOT
    last_eval_at_us: int | None = None
    control_at_us: int | None = None
    healthy_rf_at_us: int | None = None
    rf_status: RFStatus | None = None
    rf_at_us: int | None = None
    held_input: tuple[int, int] | None = None
    low_first_at_us: int | None = None
    low_first_eval_us: int | None = None
    low_qualified_eval_us: int | None = None
    high_edge_at_us: int | None = None
    high_edge_eval_us: int | None = None
    causes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ModelTick:
    tick_index: int
    eval_at_us: int
    causal_event_ids: tuple[str, ...]
    original_event_times_us: tuple[int, ...]
    model_state_before: State
    model_state: State
    model_snapshot: ModeledPrior
    rf_effective: str
    control_evidence: str
    triage_reasons: tuple[str, ...]
    model_reasons: tuple[str, ...]
    arm_switch_requested: bool
    observed_flap_micro: int | None
    observed_steer_micro: int | None
    model_input_mode: str
    model_effort_left_micro: int | None
    model_effort_right_micro: int | None
    model_clip_tags: tuple[str, ...]
    runtime_authorized: bool = field(default=False, init=False)
    output_allowed: bool = field(default=False, init=False)
    actual_virtual_output: None = field(default=None, init=False)
    physical_output: None = field(default=None, init=False)
    airborne_estimate: str = field(default="UNKNOWN", init=False)


@dataclass(frozen=True, slots=True)
class ModelReplayReport:
    outcome: ModelOutcome
    preflight_status: str
    e2_outcome: str
    e3_outcome: str
    model_ticks: tuple[ModelTick, ...]
    model_tick_count: int
    blocked_at_tick: int | None
    diagnostic: str | None
    candidate_trace: bytes
    candidate_trace_sha256: str | None
    shadow_comparator_outcome: str | None
    shadow_comparator_tick_count: int
    runtime_authorized: bool = field(default=False, init=False)
    output_allowed: bool = field(default=False, init=False)
    actual_virtual_output: None = field(default=None, init=False)
    physical_output: None = field(default=None, init=False)
    control_trace_sha256: None = field(default=None, init=False)
    candidate_label: str = field(default=LABEL, init=False)
    conformance_scope: str = field(default="DESIGN_CONFORMANCE_ONLY", init=False)


_ARMED = (State.ARM_CHECK, State.ARMED_IDLE, State.ACTUATION_ACTIVE)
_RECOVERABLE = frozenset(("E_RF_NOT_HEALTHY", "E_FRAME_STALE", "E_CONTROL_BATCH_CONFLICT",
                         "E_FRAME_INVALID", "VOLTAGE_WARNING_RECOVERABLE"))
_CLEAR = dict(low_first_at_us=None, low_first_eval_us=None, low_qualified_eval_us=None,
              high_edge_at_us=None, high_edge_eval_us=None)


def _micro(value):
    if type(value) is int:
        return value * 1_000_000
    if type(value) is not Decimal or not value.is_finite():
        raise TypeError("validated decimal demand required")
    n, d = value.as_integer_ratio()
    micro, remainder = divmod(n * 1_000_000, d)
    if remainder:
        raise ValueError("nonintegral demand millionths")
    return micro


def _fresh(at, now):
    return at is not None and 0 <= now - at <= 200000


def _advance(prior, obs, temporal, health):
    """Draft only. No mutation/append/display; every time is a MODEL time."""
    now = obs.eval_at_us
    p = replace(prior, last_eval_at_us=now)
    reasons = set()
    if obs.has_duplicate_semantic_control:
        reasons.add("R_DUPLICATE_SEMANTIC_OBSERVATION")
    if obs.rf_has_lost and (obs.rf_has_healthy or obs.rf_has_unknown):
        reasons.add("R_RF_CONFLICT")
    if prior.state is State.FAULT_LATCHED or obs.has_catastrophe:
        return replace(p, state=State.FAULT_LATCHED, held_input=None, causes=("E_SIM_FAULT",), **_CLEAR), ("E_SIM_FAULT", "R_CATASTROPHIC_LATCH"), "UNKNOWN"
    if health.rf_evidence is RFEvidenceKind.AMBIGUOUS_CURRENT:
        raise ValueError("HEALTHY+UNKNOWN effective RF unresolved by frozen R1; SA clarification required")
    if obs.rf_events:
        status = RFStatus.LOST if obs.rf_has_lost else RFStatus.UNKNOWN if obs.rf_has_unknown else RFStatus.HEALTHY
        p = replace(p, rf_status=status, rf_at_us=health.latest_current_rf_original_at_us,
                    healthy_rf_at_us=temporal.observed_uncontested_healthy_rf_at_us
                    if status is RFStatus.HEALTHY else prior.healthy_rf_at_us)
    rf = (p.rf_status.value if p.rf_status is not None else "UNKNOWN")
    if p.rf_status is RFStatus.HEALTHY and not _fresh(p.healthy_rf_at_us, now):
        rf = "UNKNOWN"
    clean = not obs.has_invalid_control and not obs.has_distinct_valid_control_conflict
    candidate = temporal.observed_uncontested_valid_control_at_us
    body = obs.valid_control_groups[0].semantic_control if candidate is not None else None
    accepted = body is not None and clean and rf == "HEALTHY" and not obs.has_reset
    control_at = candidate if accepted else prior.control_at_us
    hazards = set()
    if rf != "HEALTHY": hazards.add("E_RF_NOT_HEALTHY")
    if not _fresh(control_at, now): hazards.add("E_FRAME_STALE")
    if obs.has_invalid_control: hazards.add("E_FRAME_INVALID")
    if obs.has_distinct_valid_control_conflict: hazards.add("E_CONTROL_BATCH_CONFLICT")
    reasons.update(hazards)
    if not obs.valid_control_groups and not obs.has_invalid_control:
        reasons.add("R_NO_NEW_FRAME")
    if hazards:
        p = replace(p, **_CLEAR)
    if prior.state in _ARMED and hazards:
        return replace(p, state=State.CONTINGENCY, held_input=None,
                       causes=tuple(sorted(hazards)), **_CLEAR), tuple(sorted(reasons)), rf
    if prior.state is State.CONTINGENCY:
        p = replace(p, causes=tuple(sorted(set(prior.causes) | hazards)), held_input=None)
        if obs.has_reset or hazards:
            if obs.has_ack: reasons.add("R_ACK_DENIED")
            return replace(p, **_CLEAR), tuple(sorted(reasons)), rf
        # With restored health, coherent LOW takes precedence over ACK. The
        # qualification used by a later ACK comes only from prior committed p.
    elif obs.has_reset:
        return replace(p, state=State.SELF_TEST, held_input=None, causes=(), **_CLEAR), ("R_RESET_APPLIED",), rf
    elif prior.state is State.BOOT:
        return replace(p, state=State.SELF_TEST), ("R_BOOT_OBSERVED",), rf
    elif prior.state is State.SELF_TEST:
        return replace(p, state=State.DISARMED, held_input=None, **_CLEAR), ("R_SELF_TEST_COMPLETE",), rf
    if accepted:
        p = replace(p, control_at_us=candidate)
    # R1 priority: coherent LOW > qualified ACK > HIGH. A simultaneous HIGH
    # cannot erase a previously committed LOW before ACK is evaluated.
    if (prior.state is State.CONTINGENCY and obs.has_ack
            and not (accepted and not body["arm_switch"])):
        if (p.low_qualified_eval_us is not None and p.low_qualified_eval_us < now
                and p.causes and set(p.causes) <= _RECOVERABLE and not hazards):
            p = replace(p, state=State.DISARMED, held_input=None, causes=(), **_CLEAR)
            reasons.update(("R_ACK_ACCEPTED", "R_HEALTH_RESTORED"))
        else:
            reasons.add("R_ACK_DENIED")
            if accepted:
                p = replace(p, **_CLEAR)
        return p, tuple(sorted(reasons)), rf
    if accepted:
        flap, steer = _micro(body["flap_demand"]), _micro(body["steering_demand"])
        neutral = flap <= 20000 and abs(steer) <= 50000
        if not body["arm_switch"]:
            reasons.add("R_LOW_OBSERVED")
            if prior.state in _ARMED:
                p = replace(p, state=State.DISARMED, held_input=None, **_CLEAR)
            elif prior.state in (State.DISARMED, State.CONTINGENCY):
                if p.low_first_at_us is None:
                    p = replace(p, low_first_at_us=candidate, low_first_eval_us=now)
                elif (p.low_qualified_eval_us is None and p.low_first_eval_us < now
                      and candidate - p.low_first_at_us >= 20000):
                    p = replace(p, low_qualified_eval_us=now)
                    reasons.add("R_LOW_QUALIFIED")
            if obs.has_ack and prior.state is State.CONTINGENCY:
                reasons.add("R_ACK_DENIED")
        elif prior.state is State.DISARMED:
            qualified = p.low_qualified_eval_us is not None and p.low_qualified_eval_us < now
            p = replace(p, **_CLEAR)
            if qualified and neutral:
                p = replace(p, state=State.ARM_CHECK, high_edge_at_us=candidate, high_edge_eval_us=now)
                reasons.add("R_ARM_EDGE_ACCEPTED")
            else:
                reasons.add("E_ARM_PRECONDITION")
        elif prior.state is State.ARM_CHECK:
            if not neutral:
                p = replace(p, **_CLEAR)
                reasons.add("E_ARM_PRECONDITION")
            elif (p.high_edge_at_us is not None and p.high_edge_eval_us < now
                  and candidate - p.high_edge_at_us >= 100000):
                p = replace(p, state=State.ARMED_IDLE, **_CLEAR)
                reasons.add("R_ARM_CONFIRMED")
        elif prior.state in (State.ARMED_IDLE, State.ACTUATION_ACTIVE):
            if prior.state is State.ACTUATION_ACTIVE or flap > 50000:
                p = replace(p, state=State.ACTUATION_ACTIVE, held_input=(flap, steer))
                reasons.add("R_ACTIVE_DEMAND_ACCEPTED")
        elif prior.state is State.CONTINGENCY:
            p = replace(p, **_CLEAR)
            if obs.has_ack: reasons.add("R_ACK_DENIED")
    if p.state is State.ACTUATION_ACTIVE and not accepted:
        reasons.add("R_ACTIVE_HELD_S1")
    return p, tuple(sorted(reasons)), rf


def run_fsm_model(scenario_raw: bytes, frozen_wire_v2_schema: dict, policy_raw: bytes,
                  claimed_host: ClaimedHostFingerprint, intent_raw: bytes,
                  engine_artifact: bytes, scheduler_artifact: bytes) -> ModelReplayReport:
    if type(frozen_wire_v2_schema) is not dict:
        raise TypeError("exact frozen schema dict required")
    preflight = validate_wire(scenario_raw, frozen_wire_v2_schema)
    e2 = assess_reference_host_boundary(preflight, policy_raw, claimed_host)
    e3 = inspect_provisioning_intent(e2, intent_raw, policy_raw, engine_artifact, scheduler_artifact)
    rows = []
    journal = None
    shadow_outcome, shadow_count = None, 0
    def report(outcome, blocked=None, diagnostic=None):
        raw = journal.committed_bytes() if journal is not None else b""
        digest = sha256(raw).hexdigest() if outcome is ModelOutcome.MODEL_REPLAY_COMPLETE else None
        return ModelReplayReport(outcome, preflight.status, e2.outcome.value, e3.outcome.value,
            tuple(rows), len(rows), blocked, diagnostic, raw, digest, shadow_outcome, shadow_count)
    if type(preflight) is RejectedPreflight:
        return report(ModelOutcome.MODEL_INPUT_REJECTED)
    if (e2.outcome is not HostReferenceOutcome.REFERENCE_MATCH_NO_AUTHORITY
            or e3.outcome is not ProvisioningIntentOutcome.INTENT_CONSISTENT_UNPROVISIONED):
        return report(ModelOutcome.MODEL_REFERENCE_BLOCKED)
    # Separate genuine F0 comparator (includes TASK009); never a seed or verdict.
    shadow = run_shadow_replay(scenario_raw, frozen_wire_v2_schema, policy_raw, claimed_host,
                               intent_raw, engine_artifact, scheduler_artifact)
    shadow_outcome, shadow_count = shadow.outcome.value, shadow.shadow_tick_count
    del shadow
    if shadow_outcome != "SHADOW_DIAGNOSTICS_COMPLETE":
        outcome = (ModelOutcome.MODEL_EVIDENCE_INCOMPLETE
                   if shadow_outcome == "SHADOW_EVIDENCE_INCOMPLETE" else ModelOutcome.MODEL_CONTRACT_BLOCKED)
        return report(outcome, 0, "separate F0 comparator did not complete: " + shadow_outcome)
    journal = _ModelJournal()
    if not journal.append(header(preflight.scenario, policy_raw)):
        return report(ModelOutcome.MODEL_EVIDENCE_INCOMPLETE, 0, "candidate header append failed")
    prior = ModeledPrior()
    expected = preflight.scenario["duration_us"] // 5000 + 1
    for batch in iter_virtual_ticks(preflight):
        try:
            if batch.tick_index != len(rows) or len(rows) >= expected:
                raise ValueError("nonconsecutive model scheduler tick")
            obs = normalize_tick_observations(batch)
            temporal = evaluate_temporal_guard_facts(obs, PriorCommittedTimestampFacts(
                prior.last_eval_at_us, prior.control_at_us, prior.healthy_rf_at_us))
            priority = assess_safety_priority(prior.state, obs, temporal)
            health = assess_health_evidence(obs, temporal, priority, PriorCommittedRFStatus(
                prior.last_eval_at_us, prior.rf_status, prior.rf_at_us))
            triage = triage_guard_evidence(obs, temporal, priority, health)
            draft, reasons, rf = _advance(prior, obs, temporal, health)
            left = right = None
            clips, mode = (), "NONE"
            if draft.state is State.ACTUATION_ACTIVE:
                if draft.held_input is None:
                    raise ValueError("model ACTIVE without committed modeled intent")
                left, right, clips = mix_m0(*draft.held_input)
                mode = "FRESH" if draft.control_at_us != prior.control_at_us else "S1_HELD"
            candidate = R1TraceCandidateTick(batch.tick_index, batch.eval_at_us, prior.state.value,
                draft.state.value, rf, None if draft.control_at_us is None else batch.eval_at_us - draft.control_at_us,
                obs.causal_event_ids, reasons)
            flap = steer = None
            if len(obs.valid_control_groups) == 1:
                body = obs.valid_control_groups[0].semantic_control
                flap, steer = _micro(body["flap_demand"]), _micro(body["steering_demand"])
            row = ModelTick(batch.tick_index, batch.eval_at_us, obs.causal_event_ids,
                tuple(event["event_at_us"] for event in obs.source_events), prior.state, draft.state, draft,
                rf, health.control_evidence.value, tuple(r.value for r in triage.unresolved_reasons), reasons,
                any(g.semantic_control["arm_switch"] for g in obs.valid_control_groups),
                flap, steer, mode, left, right, clips)
        except (TypeError, ValueError) as error:
            return report(ModelOutcome.MODEL_CONTRACT_BLOCKED, batch.tick_index, str(error))
        if not journal.append(candidate):
            return report(ModelOutcome.MODEL_EVIDENCE_INCOMPLETE, batch.tick_index, "candidate tick append failed")
        prior = draft
        rows.append(row)
    if len(rows) != expected:
        return report(ModelOutcome.MODEL_CONTRACT_BLOCKED, len(rows), "missing model scheduler tick")
    if not journal.append(terminal(len(rows))):
        return report(ModelOutcome.MODEL_EVIDENCE_INCOMPLETE, len(rows), "candidate terminal append failed")
    return report(ModelOutcome.MODEL_REPLAY_COMPLETE)
