# BionicButterfly — G0-A1 R1 Potential Developer Handoff Boundary (NOT A TASK)

- **Document ID:** BB-P28-HANDOFF-122 | **Status:** Design-only; not a `Task/` issuance or software authorization.

## 1. Future modules and owned interfaces

| Component | Accepts | Produces | Contract / negative boundary |
|---|---|---|---|
| StrictScenarioParser | UTF-8 JSON v1 | accepted typed scenario or validation rejection | `117`; rejects duplicates/unknown fields before runner created |
| HostPolicyProvisioner | independently trusted policy ref and canonical bytes | immutable approved policy or rejection | `116`; no self-approval, cannot switch to GPIO |
| DeterministicScheduler | immutable virtual scenario+5ms policy | one eligible batch per tick | `115`; timestamps retained; no wall time |
| BatchNormalizer | full event batch | one coherent accepted control or typed conflict | `115/117`; no callback side-effects |
| SafetySupervisor | immutable pre-snapshot, policy, batch | one typed post-state decision | `115`; no direct actuator publication |
| VirtualEffortGate | authorized demand+decision | bounded integer pair/null | `115/117`; never PWM microseconds |
| TraceCommitter | checked decision+output+revision metadata | complete JSONL append ack | `118`; commit before any virtual sink observer |
| VirtualSink | committed output record | SIM_ONLY observer update | no physical device HAL |
| OracleHarness | fixed expected vectors | reproducible PASS/FAIL evidence | `120`; cannot substitute visual demonstration |

## 2. Future task split (not yet created)

A future SA handoff *may* split strict parser/policy provisioning, deterministic scheduler/normalizer, FSM+effort gate, trace/replay and host-only test harness, with source paths and acceptance IDs attached at that time. Developer must not choose a different timer, ACK allowlist, USB/UART transport, or flight-policy response by inference.

## 3. Handoff prerequisites

Exact Phase2.8 merged Git commit and checksum; no unresolved PC-only P0 conflicts; runtime implementation boundaries and test instrumentation reviewed; **separate owner direction to issue tasks**. A contract approval in chat is not a requirement that SA automatically modify source. Physical actuator/receiver work remains excluded and separately gated.
