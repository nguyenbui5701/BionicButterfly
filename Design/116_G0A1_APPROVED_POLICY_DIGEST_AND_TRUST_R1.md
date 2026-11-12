# BionicButterfly — G0-A1 SIM Policy R1 / Trust Boundary

- **Document ID:** BB-G0A1-POL-116 | **Revision:** R1 / 1.0 | **Status:** Owner-approved **design policy** (not installed runtime allowlist).
- **Source references:** `67`, `70`, `87`, `102`, `110`, `114`.

## 1. Pinned byte-level domain record

Only `contracts/SIM_POLICY_22A_R1.canonical.json` is the policy digest input. It contains the fields and numbers of `SIM_POLICY_CANDIDATE_22A` preserved from `67`/`102`, but **does not contain mutable** `approved_for_host_execution`, `owner_approval_ref`, physical PWM fields, timestamps or signatures.

- Policy id: `SIM_POLICY_CANDIDATE_22A`
- Policy format: `G0A1_SIM_POLICY_CORE_V1`
- Canonical bytes: RFC 8785/JCS-compatible UTF-8 JSON with lexicographically sorted ASCII field keys, no whitespace or BOM, **no terminal LF**. Here all strings are ASCII and numbers are simple finite integers/`0.02`/`0.05`; the included canonical bytes are the reference. A future runtime must use a standards-compliant implementation and verify it matches this test vector, not assume Python JSON sorting handles general JCS input.
- **Reference SHA-256:** `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10`
- The readable JSON and JSON Schema are review assets; **neither is the signed policy input**. JSON Schema alone cannot detect duplicate JSON keys or Unicode surrogate problems; parser-level canonical checks remain required.

### Exact numerical specification

| Field | Approved for PC-only value | Meaning |
|---|---:|---|
| scheduler_step_us | 5,000 | evaluation scheduler period |
| arm_low_observation_us | 20,000 | two accepted LOW observations, distinct ticks |
| arm_high_qualification_us | 100,000 | a later confirming HIGH at or beyond original timestamp boundary |
| frame_timeout_us / rf_status_timeout_us | 200,000 / 200,000 | independent freshness, inclusive age equality |
| neutral_flap_max / neutral_steer_abs_max | 0.02 / 0.05 | inclusive arm neutrality |
| active_flap_threshold | 0.05 | strict `>` for virtual ACTIVE |
| virtual_left_range / virtual_right_range | [0,1] each | dimensionless, quantized integer micro-effort |
| max_scenario_duration_us | 60,000,000 | max nominal virtual time |
| max_events / max_input_bytes / max_trace_bytes | 20,000 / 2,097,152 / 16,777,216 | resource limits |
| max_json_nesting / max_event_id_utf8_bytes / max_generic_string_bytes | 16 / 64 / 256 | parser limits |
| allowed_context / owner | PC_SIM / SIMULATOR | no physical authority |

No approved parameter here represents the ESP32 timing loop, radio link timeout, physical servo pulse, wing-beat frequency, lift requirement or airborne contingency policy.

## 2. Distinct approval and trust claims

1. The owner **has accepted the design choice**: in-chat approval, recorded in `114` and `contracts/G0A1_OWNER_APPROVAL_R1.record.json`.
2. The above SHA identifies policy **content**; it is **not** an authentication signature.
3. A future host executable must only trust an independently provisioned immutable allowlist/build configuration containing the expected policy digest, selected contract revision, host scope, permitted engine revision and bound review reference. Scenario JSON cannot install/modify this allowlist, select physical adapters, or set `approved=true` to bypass it.
4. **No trusted runtime allowlist has been provisioned by this design phase.** The JSON approval record is a review artifact, not a deployable credential.
5. If any core policy byte, schema version or selected contract revision changes, new digest + review + owner decision are required. The old allowlist cannot authorize changed content.

## 3. Required future preflight order (design, not code)

First decode UTF-8 and validate strict scenario v1 with quotas; validate typed policy against `contracts/G0A1_SIM_POLICY_CORE_V1.schema.json` and parser-level restrictions; canonicalize and compare exact hash against independently trusted built-in digest; verify engine/result/scheduler revision and `PC_SIM_ONLY` composition; **then** create the virtual-clock runner. Any mismatch ⇒ `VALIDATION_REJECTED`, zero core ticks and no virtual output. UI and scenario cannot choose a different sink.

## 4. Binding to Git

Reviewed Design source at approval: `3d9a4f28d521190d10579cab48d8b732817892c9`. The exact **reconciled** phase2.8 Git commit cannot be known until the owner integrates this package and it is inspected. Therefore the design *selection* is owner-approved; the merged configuration-controlled Design Freeze remains conditional. A future binding record may point at the merged commit without changing the policy digest if policy bytes are unchanged.
