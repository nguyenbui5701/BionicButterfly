# G0-A1 — R1.1 Authoritative Contract Hierarchy and Frozen Byte Index

- **Doc:** BB-P211-HIER-141 · **State:** Owner-approved **PC-only** design contract; **not runtime certification**
- **Git pin:** `479f65b1f0f077c0a3a75384dbc6b51b8a24e492` · machine index: `contracts/G0A1_R11_FROZEN_DESIGN_BASELINE_PHASE211.json`

## 1. Selected and versioned contracts

| Domain | Authoritative document | Exactly frozen behavior |
|---|---|---|
| Security/authority/safety FSM | `115` | PC_SIM owner, BOOT/SELF_TEST/DISARMED/ARM_CHECK/ARMED_IDLE/ACTIVE/CONTINGENCY/FAULT_LATCHED; priorities + S1 holds |
| Numeric runtime SIM policy | `116` + `contracts/SIM_POLICY_22A_R1.canonical.json` | 5ms step, LOW 20ms, HIGH 100ms, two independent 200ms ages, 60s duration, fixed quotas and digest `d7567197dd43480d7e96dac121fbb707d3097b6c443b1b7ab55e822dbac66e10` |
| Result/error base | `117` | result v2 and preflight/runtime code distinctions |
| Trace atomicity/replay | `118` | JCS+LF control stream, independent identity and full hash outside trace, append-before-publish |
| v2 event wire | `132` + `contracts/G0A1_SCENARIO_WIRE_V2_CANDIDATE.schema.json` | **six event types** and strict semantic preflight, `schema_version=2`, closed objects, no self approval |
| M0 virtual mixing | `133` + `contracts/G0A1_MIXER_M0_R11_CANDIDATE.json` | `F±S`, exact micro integers, saturating outputs and clip tags; virtual only |
| Trace schema and external result | `134` + `contracts/G0A1_TRACE_RECORDS_R11_CANDIDATE.schema.json` + `contracts/G0A1_EXTERNAL_REPORT_R11_CANDIDATE.schema.json` | closed header/tick/terminal, external digest; no unsupported success claims |
| Design examples/oracles | `135`, `136`, `120`, frozen fixtures | design reference, not executable proof |

**Important:** filenames containing `_CANDIDATE` are preserved *byte-for-byte* for provenance. Their listed exact hash is now part of the **owner-approved R1.1 design** by decision dated 2026-11-13. Rewriting filenames or schema `$id` is NOT needed and would require migration/review of referenced hashes.

## 2. Precedence for conflicts

1. Physical/airborne conditions NEVER inherit any of these host-only rules; `27` hardware/flight policies retain separate unresolved status.
2. Within PC-only wire/mixer/closed trace fields, **new approved R1.1** (`132–134` and pinned machine contracts) refines R1.
3. For fault priority/state/authority/numeric SIM policy, **approved R1** (`115–118`) retains precedence. A schema v2 data-field extension does **not** change fault behavior.
4. Historic drafts `57–114`, `126`, `131`, older conflict matrices, and supersession annotations remain context/evidence; they do not have independent authority to override this order.
5. If two approved requirements still conflict, **raise SA defect and HOLD that operation**; do not choose the most convenient interpretation. Only an explicit change control may revise the byte contract.

## 3. Permanent restrictions

- `scenario.context=PC_SIM`, provenance SIM_ONLY, virtual owner SIMULATOR only. No physical device APIs, plug-in loading, GPIO/UART/PWM, receiver binding, IMU or real flight output.
- `AirborneEstimate=UNKNOWN`; no 6DOF lift, stable flight, yaw/roll authority or E-stop proof follows from M0.
- Approval of design is not a provisioned runtime allowlist. An executable must separately protect both policy digest and engine/scheduler revision.
- Enforce both original event timestamp and fixed evaluation timestamp; never silently snap to tick boundaries.
- A zero-valued *authorized* pair `(0,0)` is not an inhibited `(null,null)` pair.

## 4. Audit invariants

- Every normative contract is listed in the machine index with the SHA-256 and Git blob SHA-1 at the pinned Git commit.
- Any change to bytes at an authoritative path invalidates this freeze index until reviewed, even when a document appears cosmetically changed.
- The future developer must READ the pinned tree, not mix downloaded ZIP files with unverified local working-tree edits.
