> **Phase 2.8 / G0-A1 R1 approved-scope reconciliation notice (2026-11-13).** The owner approved **PC_SIM_ONLY Candidate R1** in conversation after Phase 2.7; see [`114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md`](114_PHASE28_OWNER_APPROVAL_AND_SCOPE_BASELINE.md). For G0-A1 host-only behavior, the **current controlling specification** is `118 (no terminal self-hash)`; this file’s earlier DRAFT/PROPOSED/PENDING language and any conflicting priority, policy or replay rules are **retained as historical design context, not independently authoritative**. This notice does **not** approve flight/bench hardware, claim tests passed, or authorize tasks. Guard against overwrites: original Git blob SHA `d5ea99889c906c14b63012648347fb585ea7f6a9`, base main `3d9a4f28d521190d10579cab48d8b732817892c9`.

# BionicButterfly — Trace Terminal & Transaction Semantics (Targeted Patch Proposal)

- **ID:** BB-P25-TRACE-094 | **Version:** 0.1 | **Status:** PROPOSED FIX of `87`, `69`, `80`; no implementation.
- **Issue:** replay hash must have an unambiguous, non-circular byte definition and proof cannot be considered complete after logging failure.

## 1. Define the hash *before* the report object

A canonical JSONL stream shall contain exactly these **normative** record types in this sequence:

1. `header` — stable schema versions, **replay identity**, scenario/policy digests, engine and scheduler version, no wall-time, execution ID, absolute path or user name.
2. `decision` — exactly one per committed evaluation tick, including sorted causal IDs, pre/post state, reasons, integer virtual effort or null.
3. `terminal` — final control disposition (COMPLETE/FAILED), tick count, any *stable error codes*. **Must NOT include `control_trace_sha256`, execution_instance_id, wall-clock values, signing proof or a string that itself contains this digest.**

Encoding: one JCS-compatible JSON object per line with exactly LF `0x0A` after **every** record including terminal. Hash **the exact UTF-8 bytes of header+decisions+terminal** using SHA-256. The top-level `SimulationRunReportV2.control_trace_sha256` is computed *after* those bytes are finalized and written; it exists **outside** the hashed trace. `execution_instance_id` and human display metadata also stay outside the trace. This avoids recursive digest identity.

`partial_trace_sha256` is separately tagged and **may cover only committed records actually persisted**; it must never be assigned to `control_trace_sha256`. A final `COMPLETED` run requires valid header, all planned normative decisions and a terminal record; expected injected fault may still complete when fully observed. Validation-rejected scenario has **no control trace** and its diagnostic report is external.

## 2. Output and logging transaction candidate

Within tick `T` in memory: compute normalized batch → evaluate tentative decision → calculate optional virtual effort → construct canonical `decision` → check trace size and write/append success → **only then expose the new virtual output/state** as committed. If append fails, no new output for that failed tick may be made externally observable, run enters `FAILED_INCOMPLETE_EVIDENCE`, stops future virtual evaluation and exports explicit failure metadata. If the host uses an append mechanism that could report success before durability, its durability semantics must be stated in the implementation design; no impossible cross-platform atomic-disk guarantee is claimed.

Since G0-A1 has **no physical actuator**, this is an achievable host-only architectural target. It is **not** a guarantee of physical robot safety during logging failures; actual device control is out of scope.

## 3. Canonical field & version rules

- `trace_format_version` and `result_contract_version` are separate from scenario schema v1.
- Replay identity is formed from explicit canonical structured field names/version/digests, not unseparated concatenation.
- Reference policy digest shall be computed from **approved immutable policy bytes**, excluding volatile review timestamps and scenario-embedded self-approval flags.
- JCS RFC 8785 pin and reject duplicate JSON keys/nonfinite values, keep stable field and array order as defined by the schema.
- An all-zero virtual command differs from **null when not authorized**; never conflate disarmed with `0` servo angle.

## 4. Targeted review tests

- `P25-T01`: terminal contains a fake `control_trace_sha256` field ⇒ schema rejection, never recursively hash.
- `P25-T10`: trace quota/append failure on would-be ACTIVE tick ⇒ no exposed ACTIVE output, run incomplete, no complete digest.
- `P25-T11`: same input and policy but different execution ID ⇒ equal normative digest.
- `P25-T12`: one byte of canonical decision modified after execution ⇒ digest mismatch.

**Not yet approved:** do not change `69/80/87` without an owner-approved versioned patch. The existing `87` wording is an ambiguity to resolve, not proof that an implementation already hashes itself.
