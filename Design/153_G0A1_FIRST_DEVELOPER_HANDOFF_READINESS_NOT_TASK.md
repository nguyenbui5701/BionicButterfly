# G0-A1 — Proposed First Isolated Developer Work Package (NOT A TASK)

- **ID:** BB-P212-HANDOFF-153 · **Status:** SA scoping; **not permission to implement**.

## 1. Potential minimal module after a separate owner request

**Name:** HOST_PREFLIGHT_M0 (validation + virtual arithmetic only). No event scheduler, safety state machine implementation, trace writer, runtime file transaction, OS adapter or UI. Split implementation into independent pure functions as agreed in PR design. The host should not load policy from user-provided scenario data.

**Required entrypoints, behavior not language-specific:**

- `validateWire(raw_utf8_bytes, pinned_schema, max_size)` → immutable accepted scenario **or** `VALIDATION_REJECTED` with single diagnostic sidecar v1 **if separately approved**; no partial accept. Validated scenarios still may have runtime fault events, and do **not** automatically possess trusted host policy.
- `normalizeExactMicros(decimal_tokens)` → signed integer micro units, reject fractions not integral at 1e-6 scale, reject NaN/Infinity and boolean-as-number; no floating pre-rounding.
- `mixM0(flap_micro, steer_micro)` → bounded left/right integer micro effort plus clipping tags, exactly as frozen contract. This function does **not** assert output authorization; calling it is not a servo command.

## 2. Inputs, outputs and exclusions

| Boundary | Allowed | Forbidden |
|---|---|---|
| Input | v2 JSON bytes, approved frozen schema | RC hardware packets, web `approved=true`, v1 auto-migration |
| Arithmetic | int micro exactly; 12 golden vectors | PWM duty, servo pulse, inferred 6DOF physics |
| Failure | rejected typed preflight; zero core ticks | parse repair, last-wins duplicate keys, guessed E code |
| Logging | deterministic diagnostic sidecar outside core trace | hash/trace modification, real device logging |
| Repository | later isolated PR after authorized task | direct `main` edits or firmware changes |

**No files or concrete coding directories are mandated at this stage**; Developer may propose structure within those boundaries only after handoff authorization. The task will include exact Git SHA and contract digests (never pin a movable `main` instead of a commit).

## 3. Proposed acceptance, evidence and review gate

1. Frozen v2 positive scenarios including legal in-band INVALID UART are accepted by input validator.
2. All P212 negative cases produce the chosen primary `P_*` diagnostic, exact JSON Pointer and zero created core ticks; wrong context denied.
3. No duplicate member may be accepted at any nesting depth and no wrong numeric precision may be rounded silently.
4. All 12 P210 M0 golden arithmetic vectors match exact integer outputs and clip tags.
5. Repeated validation of the exact same raw bytes returns exactly equivalent canonical diagnostic content, independent of OS locale and time-zone.
6. No physical device IO, no system wall-clock/host RNG effects, no remote network connections, no plugins, no UI control path.
7. Unit tests and a small negative parser fuzz corpus are recorded by Developer with reproducible commands, environment and actual PASS/FAIL counts.
8. SA review checks diff and assertions using **isolated `ReviewPR/` checkout** per `11_HANDOFF_PR_WORKFLOW.md`.

## 4. Gates before creating any `Task/` Markdown

- Owner approves proposed diagnostic contract if detailed parser rejection output is included in the first task (R1.1 owner approval does **not** automatically cover the new `P_*` sidecar).
- Phase 2.12 files integrated and their current Git commit verified, with no unexpected source changes.
- Owner **explicitly requests task issuance** for the chosen limited work package. Previous permission to continue SA design is not automatically permission to create a task or change production files.
- Physical/flight scope remains **NO-GO**, and G0-A1 full runtime certification requires later host allowlist/trace/replay testing.

This document is a **handoff boundary and acceptance review**, not a coding task. No `Task/`, `Source/`, `ReviewPR/` operation or Git write is executed by SA in Phase 2.12.
