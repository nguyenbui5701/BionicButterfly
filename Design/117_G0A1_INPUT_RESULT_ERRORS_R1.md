# BionicButterfly — G0-A1 Input v1 / Result & Error v2 Approved Interface

- **Document ID:** BB-G0A1-SCHEMA-117 | **Revision:** R1 / 1.0
- **Priority:** Refines `57`, `61`, `78`, `85`, `100–101`, `115`; no real hardware adapter or flight-event provenance.

## 1. Input v1 is a strict, simulated-only domain

`schema_version=1`, `provenance=SIM_ONLY`, scenario `context=PC_SIM`, typed `event_id`, integer microsecond `event_at_us`, and known event types only. No unknown keys or permissions via JSON; mandatory `BOOT` at timestamp 0. Validate unique event IDs **globally**, even if two events describe equivalent observations. Reject malformed UTF-8, duplicate object keys, NaN, Infinity, negative/nonintegral time, unknown event types, physical-output targets and excessive resource use **preflight**.

**Do not silently add** new event types in R1. Existing in-band typed `SIM_CONTROL_FRAME(uart_frame_status=INVALID)` is a valid fault injection; malformed input structure is not. Preserve original event timestamps and causal IDs; per-tick deduplication never means globally repeated IDs are acceptable.

## 2. Result/Error contract v2 (exact semantic distinctions)

| v2 code | Level | Required semantic consequence |
|---|---|---|
| `E_DUPLICATE_EVENT_ID` | preflight | reject whole scenario; no core run or canonical trace |
| `E_CONTROL_BATCH_CONFLICT` | runtime | distinct valid control payloads in same tick; no trusted accepted control, no timestamp refresh |
| `R_DUPLICATE_SEMANTIC_OBSERVATION` | runtime reason | equivalent unique-ID control events counted once, original IDs retained sorted |
| `E_FRAME_INVALID` | runtime for valid injected INVALID | breaks LOW qualification; cannot refresh accepted intent; if armed, CONTINGENCY |
| `E_RF_NOT_HEALTHY` | runtime guard | RF LOST/UNKNOWN/stale invalidates new arm and active output |
| `E_FRAME_STALE` | runtime guard | independent accepted-intent freshness exceeded |
| `E_ARM_PRECONDITION`, `E_ARM_EDGE_ABSENT` | guards | no new arm if qualification absent |
| `E_CONTEXT_DENIED`, `E_OWNER_DENIED` | preflight/runtime as applicable | cannot cross PC-only trust boundary |
| `E_CONFIG_LOCKED`, `E_PROFILE_INVALID` | configuration | no mid-run policy mutation or unauthorized profile |
| `E_NUMERIC_INVALID`, `E_INPUT_OVERFLOW` | runtime failure | inhibit output, typed failed result as appropriate |
| `VOLTAGE_WARNING_RECOVERABLE` | fault reason only | ACK-clearable **only** after separately demonstrated recovery; no new wire type invented |

`E_EVENT_ID_CONFLICT` from old `57` is **DEPRECATED**, never emitted by v2; old records without sufficient context are `AMBIGUOUS_LEGACY_ERROR`, not silently mapped to another code. Any newly introduced code must have a schema version and oracle updates.

## 3. Typed data boundaries

- `SimulationRunReportV2` has `run_status`, `assertion_result`, `evidence_complete`, scenario/policy digests, replay identity, engine/scheduler revisions, trace version, optional external execution-instance ID and complete digest if applicable.
- Run statuses: `VALIDATION_REJECTED`, `COMPLETED`, `FAILED`, `FAILED_INCOMPLETE_EVIDENCE`. A simulated fault may be fully traced under `COMPLETED`, with a predeclared fault oracle PASS. No successful core trace exists for preflight rejection.
- Test assertion statuses: `PASS|FAIL|INCONCLUSIVE|NOT_RUN` **only for explicit oracles**, never a synonym for physical flight success.
- If `output_allowed` false, both virtual effort fields are JSON `null`; if true both are integers in `[0,1000000]`. Quantizer: `floor(clamp(x,0,1)·1000000+0.5)` on finite nonnegative output, with clipping reasons.
- Canonical causal IDs and reason codes are sorted using the declared schema comparator. Never blend caller-invocation UUID or wall time into trace.

## 4. Migration constraints

No physical `RC_PRIMARY` or `GROUND_ARMED` claim is inferred from host-only v2 names; `SELF_TEST` with RF UNKNOWN may show virtual DISARMED but not permit ARM. Legacy scenarios under draft v1 with ambiguous event conflicts must be revalidated rather than automatically reported PASS. Developer must not guess or auto-correct a malformed scenario: typed rejection with path is required.
