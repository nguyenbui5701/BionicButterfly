# BionicButterfly — Developer Handoff Readiness (Design Review Only)

- **ID:** BB-P29-HANDOFF-130 | **Status:** **NOT A TASK; HANDOFF HOLD**
- **Role boundary:** SA defines contracts, test criteria, review; AI Developer writes implementation only after separate owner instruction.

## 1. Proposed future implementation modules (not authorized)

| Component | Required design source | Entry criterion | Current status |
|---|---|---|---|
| StrictScenarioParser | `117`, future closed event schema | P29-F01 closed, duplicate keys/IDs correctly diagnosed | HOLD |
| ApprovedHostPolicyLoader | `116`, canonical policy, independent owner allowlist | no scenario self-approval, trusted repo digest | DESIGN LOCKED; runtime not provisioned |
| VirtualScheduler/BatchNormalizer | `115`, `101`, `104` | 5ms stable batching, original time retained, conflicting batch invalidation | DESIGN LOCKED; test NOT RUN |
| VirtualSafetyFSM | `115`, `120`, `127` | strict state priority and ACK/RESET edge oracles | DESIGN LOCKED; test NOT RUN |
| VirtualMixer/Sink | `115`, `117`, future mixer selection | P29-F02 closed; null pair distinct from 0, no physical adapter | HOLD |
| TraceCommitter/Replay | `118`, future trace JSON schema | P29-F03 closed; external full SHA and append-before-publication | HOLD |
| ConformanceHarness | `120`, `127` | exact reference fixtures and expected hash, negative tests | HOLD |

## 2. Future handoff file list (read-only contract references)

Mandatory: `Design/114–122`, `Design/123–130` and eventual approved R1.1 interface supplement, plus `Design/07_AI_CODING_RULES.md`, `Design/10_SA_OPERATING_RULES.md`, `Design/11_HANDOFF_PR_WORKFLOW.md`. `Design/27` is a **separate unapproved physical safety proposal**, never to be imported as a PC-only permission. The exact filename list and approved Git SHA must be restated in each future Task.

## 3. Stop conditions

Stop before writing implementation if a module requires guessing event field names, accepted wire type set, mixing coefficients, trace required keys, alternate policy numbers or a physical I/O adapter. Escalate to SA and version the design. Do not treat the existence of a test oracle as evidence of a passing test.

## 4. Exit path

After owner accepts Phase2.10 interface choices (if necessary), SA verifies new Git and completes G0-A1 **full design freeze**. Only then, on separate explicit owner direction, issue a bounded PC-only Task; PR review stays isolated in `ReviewPR/` according to existing project workflow. Do not conflate architecture freeze with firmware readiness or flight authorization.
