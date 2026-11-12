# BionicButterfly — G0-A1 Simulator Trust Boundaries & Abuse Cases

- **ID:** BB-G0A-SEC-062 · **Rev:** 0.1 · **Date:** 2026-11-12
- **Status:** PROPOSED / ALL SECURITY TESTS NOT RUN
- **Purpose:** protect safety semantics and replay integrity even when inputs are untrusted local scenario files or a later optional UI.

## 1. Asset and trust inventory

| Asset | Trust boundary | Main failure mode | Protection to design |
|---|---|---|---|
| host-only code/build composition | runtime config/scenario ↔ binary capability | user payload enables GPIO/flight context | compile-time composition exclusion + dependency review |
| SIM policy | file/UI ↔ safety state | unapproved profile, permissive defaults or mutation | typed validated version/digest, DISARMED-only mutation |
| simulated observation | input parser ↔ safety | spoofed RF `HEALTHY`, fake frame freshness, duplicate arm edge | `INJECTED_SIM` provenance, strict age/identity/state guards |
| virtual clock | scenario ↔ scheduler | backward time, overflows, event storms | validated u64 times, bounded events/duration, deterministic failures |
| trace/evidence | trace store ↔ reviewer | tampered evidence, mixed revisions, fabricated PASS | canonical hash, run ID, status, immutable append semantics |
| future UI viewer | UI ↔ core | mutation/re-entrancy, accidental authority escalation | read-only projection, explicit service ports, no physical adapter |
| third-party example code | untrusted repositories ↔ project | licensing/provenance compromise | clean independent implementation, per-file audit (01/12) |

## 2. Threat cases and expected behavior

| Threat ID | Attack or fault input | Expected design response | Test ref |
|---|---|---|---|
| `TH-01` | scenario sets `context=FLIGHT_TEST_APPROVED` or imports a `hardware_driver` name | reject before simulation; host factory has no driver port | PC-A16, SEC-01 |
| `TH-02` | simulated RF healthy but UART frame stale/invalid | no arm; independent statuses persisted | PC-A07–09, SEC-02 |
| `TH-03` | same-timestamp conflicting LOW/HIGH frames | reject conflict, no spurious arm edge | TIME-03, SEC-03 |
| `TH-04` | repeated high after reboot/fault | no autoarm; observed valid LOW required | PC-A01/02/17, SEC-04 |
| `TH-05` | NaN, Infinity, huge integer, duplicate JSON key or unexpected actuator field | validation failure, no motion | PC-A09, SEC-05 |
| `TH-06` | huge event count, long duration, nested payload or repeated time | fixed limit and explicit typed failure; not hang/allocate indefinitely | TIME-06, SEC-06 |
| `TH-07` | config write and ARM in same tick | deny conflicting mutation, preserve config revision | CFG-07, SEC-07 |
| `TH-08` | UI sends physical PWM targets or servo endpoints while armed | unauthorized schema rejected; no GPIO port exists | PC-A12/13, SEC-08 |
| `TH-09` | interrupted trace or changed configuration hash | report integrity failure; refuse PASS status | TIME-06, SEC-09 |
| `TH-10` | reference source code/assets copied into future task despite licensing concerns | provenance gate blocks release; record actionable issue | DF-15, SEC-10 |

## 3. Parser hardening and data governance

- Input uses candidate **JSON** with strict type validation; duplicate keys MUST be rejected by the parser or an explicit duplicate-key check, because many JSON parsers otherwise silently overwrite prior keys.
- Reject unknown event types, unknown fields at security-sensitive objects, illegal context, invalid numeric encodings, invalid strings and oversized payloads. Do not use dynamic code execution or load modules named inside scenario data.
- Scenario paths must not permit directory traversal or arbitrary output-file overwrite if a future CLI/UI accepts user filenames; restrict to configured workspace/output location.
- Protect source maps, secrets and credentials by **not storing real binding keys, tokens, passwords or personal pilot data** in SIM scenarios or examples.
- `SIM_ONLY` is a **claim label and build capability boundary**, not authentication. A future network service would need a fresh security model and explicit owner approval.

## 4. Test evidence and release gate

- Keep a separate set of **SEC-01…SEC-10** scenarios, negative tests and expected denial codes. The fact that this table exists does not show a secure implementation.
- For any reviewer: cite exact source/commit, test run, config/scenario hash and stored trace. A local or remote PASS badge is not enough.
- An abuse test that crashes the process, hangs indefinitely or creates a partial trace falsely labeled PASS must fail the G1 gate.

**Current finding:** no host software exists in this phase, no security tests executed, no authorization to connect physical hardware.
