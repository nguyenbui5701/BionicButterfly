# BionicButterfly — Potential Developer Handoff Boundaries (SA Prepared, NOT a Task)

- **ID:** BB-P25-HANDOFF-097 | **Rev:** 0.1 | **Status:** FUTURE PLAN ONLY / NO TASK ISSUED.
- **Role rules:** `07_AI_CODING_RULES.md`, `10_SA_OPERATING_RULES.md`, `11_HANDOFF_PR_WORKFLOW.md` remain binding after explicit owner approval.

## 1. First *possible* implementation slice **only after G0-A1 approved and owner separately authorizes task**

Purpose: create host-only deterministic pure-core simulator, no physical actuator or RC/ESP32 code. Suggested bounded files to design and implement later: scenario parser/validator, strict event normalization, immutable policy loader, safety/authority FSM, virtual mixer/envelope, trace/replay collector and host tests.

**Do not silently select toolchains or languages:** Owner may select a repo language/toolchain after reviewing source state; SA must then create a version-pinned `Task/TASK-...md` with exact allowed source files, accepted APIs, test oracles, no-go cases and review steps. This phase does **not** produce such a task.

## 2. Required files a future Developer must read

- `02`, `07`, `10`, `11` — requirements, roles, workflow.
- Approved versions of `56–61`, `67–71`, `78–80`, `84–87`, Phase25 `92`, `94–96` and exact signed owner approval record.
- `27`, `28`, `32`, `37` only as boundary/forward-compatibility context; physical behavior is *not* in scope.

## 3. Mandatory negative scope and quality gates

The eventual PC task must not include: ESP-IDF/Arduino/real GPIO/UART, PWM, network RF pairing, real servo pulses, physics 'lift' claims, hardware emergency flight policy, autonomous GPS, UI control of a real airframe, setting `approved=true` from input JSON, or unreviewed source copying. Test vectors must cover invalid event ID, same-tick conflict, RESET+catastrophe, ACK ordering, stale frame vs RF health, arbitrary config writes, replay hash integrity, trace quota fail and no-event tick case.

## 4. Future review handshake

Owner approves exact G0-A1 design commit + separate first task. SA drafts task in `Task/` referencing fixed artifact versions. AI Developer implements only in allowed implementation paths. SA reviews PR in isolated `ReviewPR/`, comparing diff to design and confirming test evidence (not just green CI label). Owner controls commits/pushes, as already requested.

**No `Task/` file is present in this Phase25 package.**
