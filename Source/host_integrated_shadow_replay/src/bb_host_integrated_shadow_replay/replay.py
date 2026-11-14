"""Compose genuine upstream APIs from genesis; preview is arithmetic only."""
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from bb_host_preflight_m0 import validate_wire, RejectedPreflight, mix_m0
from bb_host_virtual_ticks import iter_virtual_ticks
from bb_host_batch_observations import normalize_tick_observations
from bb_host_temporal_guard_facts import evaluate_temporal_guard_facts, PriorCommittedTimestampFacts
from bb_host_safety_priority_kernel import assess_safety_priority, SafetyState
from bb_host_health_evidence import assess_health_evidence, PriorCommittedRFStatus, RFEvidenceKind, ControlEvidenceKind
from bb_host_guard_triage import triage_guard_evidence, ControlGuardLane, GuardReason
from bb_host_snapshot_commit_gate import TestOnlySnapshotLedger, CommitOutcome
from bb_host_trust_boundary import assess_reference_host_boundary, ClaimedHostFingerprint, HostReferenceOutcome
from bb_host_provisioning_intent import inspect_provisioning_intent, ProvisioningIntentOutcome


class ShadowReplayOutcome(str, Enum):
    INPUT_REJECTED = "INPUT_REJECTED"
    REFERENCE_OR_INTENT_BLOCKED = "REFERENCE_OR_INTENT_BLOCKED"
    SHADOW_DIAGNOSTICS_COMPLETE = "SHADOW_DIAGNOSTICS_COMPLETE"
    BLOCKED_NEEDS_FULL_FSM = "BLOCKED_NEEDS_FULL_FSM"
    SHADOW_EVIDENCE_INCOMPLETE = "SHADOW_EVIDENCE_INCOMPLETE"


@dataclass(frozen=True, slots=True)
class ShadowTick:
    tick_index: int
    eval_at_us: int
    causal_event_ids: tuple[str, ...]
    pre_state: SafetyState
    test_state_after: SafetyState
    rf_evidence: RFEvidenceKind
    control_evidence: ControlEvidenceKind
    triage_reasons: tuple[GuardReason, ...]
    e1_outcome: CommitOutcome
    arm_switch_requested: bool
    preview_left_micro: int | None
    preview_right_micro: int | None
    preview_clip_tags: tuple[str, ...]
    runtime_authorized: bool = field(default=False, init=False)
    actual_virtual_output: None = field(default=None, init=False)
    physical_output: None = field(default=None, init=False)


@dataclass(frozen=True, slots=True)
class ShadowReplayReport:
    outcome: ShadowReplayOutcome
    preflight_status: str
    e2_outcome: HostReferenceOutcome
    e3_outcome: ProvisioningIntentOutcome
    shadow_ticks: tuple[ShadowTick, ...]
    shadow_tick_count: int
    blocked_at_tick: int | None
    runtime_authorized: bool = field(default=False, init=False)
    requires_full_fsm: bool = field(default=True, init=False)
    actual_virtual_output: None = field(default=None, init=False)
    physical_output: None = field(default=None, init=False)
    canonical_control_trace_sha256: None = field(default=None, init=False)


def _micro(value):
    """Exact rational conversion, independent of Decimal context precision."""
    if type(value) is int:
        return value * 1_000_000
    if type(value) is not Decimal or not value.is_finite():
        raise TypeError("expected genuine preflight int or finite Decimal demand")
    numerator, denominator = value.as_integer_ratio()
    micro, remainder = divmod(numerator * 1_000_000, denominator)
    if remainder:
        raise ValueError("nonintegral micro demand at validated boundary")
    return micro


def run_shadow_replay(scenario_raw: bytes, frozen_wire_v2_schema: dict, policy_raw: bytes,
                      claimed_host: ClaimedHostFingerprint, intent_raw: bytes,
                      engine_artifact: bytes, scheduler_artifact: bytes) -> ShadowReplayReport:
    """Run TEST_ONLY observation, without IO, callback, initial-state or output API.

Typed-boundary exceptions deliberately propagate; no coercion into a successful
demo. E1 failure/defer returns only already acknowledged rows, without retry.
"""
    if type(frozen_wire_v2_schema) is not dict:
        raise TypeError("expected exact frozen schema dict")
    preflight = validate_wire(scenario_raw, frozen_wire_v2_schema)
    e2 = assess_reference_host_boundary(preflight, policy_raw, claimed_host)
    e3 = inspect_provisioning_intent(e2, intent_raw, policy_raw, engine_artifact, scheduler_artifact)

    def report(outcome, rows=(), blocked=None):
        return ShadowReplayReport(outcome, preflight.status, e2.outcome, e3.outcome,
                                  tuple(rows), len(rows), blocked)

    if type(preflight) is RejectedPreflight:
        return report(ShadowReplayOutcome.INPUT_REJECTED)
    if (e2.outcome is not HostReferenceOutcome.REFERENCE_MATCH_NO_AUTHORITY
            or e3.outcome is not ProvisioningIntentOutcome.INTENT_CONSISTENT_UNPROVISIONED):
        return report(ShadowReplayOutcome.REFERENCE_OR_INTENT_BLOCKED)
    ledger = TestOnlySnapshotLedger()
    rows = []
    expected_ticks = preflight.scenario["duration_us"] // 5000 + 1
    for batch in iter_virtual_ticks(preflight):
        if batch.tick_index != len(rows) or len(rows) >= expected_ticks:
            raise ValueError("TEST_ONLY integration: nonconsecutive/extra scheduler tick")
        prior = ledger.snapshot
        obs = normalize_tick_observations(batch)
        temporal = evaluate_temporal_guard_facts(obs, PriorCommittedTimestampFacts(
            prior.last_eval_at_us, prior.last_accepted_control_at_us, prior.last_uncontested_healthy_rf_at_us))
        priority = assess_safety_priority(prior.state, obs, temporal)
        health = assess_health_evidence(obs, temporal, priority, PriorCommittedRFStatus(
            prior.last_eval_at_us, prior.last_rf_status, prior.last_rf_original_at_us))
        triage = triage_guard_evidence(obs, temporal, priority, health)
        commit = ledger.commit_tick(obs, temporal, priority, health, triage)
        if commit.outcome is CommitOutcome.DEFERRED_NEEDS_FULL_FSM:
            return report(ShadowReplayOutcome.BLOCKED_NEEDS_FULL_FSM, rows, batch.tick_index)
        if commit.outcome is CommitOutcome.FAILED_INCOMPLETE_EVIDENCE:
            return report(ShadowReplayOutcome.SHADOW_EVIDENCE_INCOMPLETE, rows, batch.tick_index)
        if commit.outcome is not CommitOutcome.COMMITTED_TEST_ONLY:
            raise ValueError("TEST_ONLY integration: unknown E1 outcome")
        after = ledger.snapshot
        if (after.generation != prior.generation + 1 or commit.snapshot_generation != after.generation
                or after.last_tick_index != batch.tick_index or after.last_eval_at_us != batch.eval_at_us):
            raise ValueError("TEST_ONLY integration: missing acknowledged snapshot")
        left = right = None
        tags = ()
        if (len(obs.valid_control_groups) == 1 and not obs.has_invalid_control
                and not obs.has_distinct_valid_control_conflict
                and health.rf_evidence is RFEvidenceKind.HEALTHY_CURRENT
                and not obs.has_reset and not obs.has_catastrophe
                and not priority.blocks_control_qualification
                and triage.control_lane is ControlGuardLane.UNTRUSTED_CANDIDATE):
            body = obs.valid_control_groups[0].semantic_control
            left, right, tags = mix_m0(_micro(body["flap_demand"]), _micro(body["steering_demand"]))
        # Raw observed HIGH in any valid group is a request, including a denied
        # conflicting/INVALID tick; never a control admission or state decision.
        arm_requested = any(group.semantic_control["arm_switch"] for group in obs.valid_control_groups)
        rows.append(ShadowTick(batch.tick_index, batch.eval_at_us, obs.causal_event_ids,
            prior.state, after.state, health.rf_evidence, health.control_evidence,
            triage.unresolved_reasons, commit.outcome, arm_requested, left, right, tags))
    if len(rows) != expected_ticks:
        raise ValueError("TEST_ONLY integration: missing scheduler ticks")
    return report(ShadowReplayOutcome.SHADOW_DIAGNOSTICS_COMPLETE, rows)
