# G0-A1 — R1.1 M0 Mixer, Closed Trace, Hash and Output Boundary Review

- **Doc:** BB-P211-MT-143 · **Approved:** R11-D03/D04 · **Audit scope:** design/fixture only.

## 1. Exact M0 mathematics

For schema-v2 exact decimal demands `flap_demand` and `steering_demand`:

```text
F = exact_decimal(flap) × 1_000_000     integer in [0,1_000_000]
S = exact_decimal(steer) × 1_000_000    integer in [-1_000_000,1_000_000]
left_raw  = F - S
right_raw = F + S
L = min(1_000_000,max(0,left_raw))
R = min(1_000_000,max(0,right_raw))
```

Clip tags only for strict `<0` or `>1_000_000`; equality **not** clipping. Positive steering raises R relative L **virtually**; no real roll/yaw sign inference. A held S1 intent recomputes from **original accepted input**, never feedback from quantized L/R. M0 is a mathematical operation; `state_after=ACTUATION_ACTIVE` plus all R1 authority/freshness guards and trace commit are required before exposing its numbers. Otherwise pair is `(null,null)`.

**Independent static check performed:** all 12 values and clip tags in `fixtures/P210_M0_GOLDEN_VECTORS.json` recomputed with Python `Decimal`, matched 12/12; no engine executed.

## 2. Complete trace bytes and external digest

`JCS(header)+LF`, exactly one JCS tick per evaluated time, `JCS(terminal)+LF` for a fully completed run. Header includes wire schema version 2, mixer revision `G0A1_M0_R11`, result contract version 2, trace format version 1 and pinned engine/scheduler identity. Tick has fixed present keys, explicit `null` pairs if inhibited, reasons and causal IDs sorted bytewise. Terminal has only final status, count, errors and evidence bit.

`control_trace_sha256` belongs **outside** the stream in the external report after complete append acknowledgement. Source JSON/trace/replay digests are separate domains. Design fixture trace has 4 records, 1433 bytes and SHA-256 `1cdaa68e016d4227d8623adf285a6d28ace9092bf1c45ef7a21b65638a4a10a3`. It is **hand-authored**; source attestation explicitly states `runtime_executed=false`.

## 3. Operational safety ordering to verify in implementation

1. Gather full batch at fixed tick, normalize and evaluate one immutable pre-state.
2. Tentatively compute safety decision and bounded M0 pair.
3. Serialize **one complete decision record**, check size budget, commit append and await acknowledgement.
4. Only after step 3 publish virtual post-state/output to UI/harness.
5. Append failure, quota failure, serialization failure or missing terminal ⇒ `FAILED_INCOMPLETE_EVIDENCE`, complete hash `null`; **no tentative active output** appears externally.

This is a virtual observability guarantee, not a claim of power-failure-safe hardware disk writes.

## 4. Static vs runtime gate

| Evidence | Result | Limitation |
|---|---|---|
| 12 exact algebra vectors | PASS_STATIC | not post-FSM output |
| 4 JSONL record schemas | PASS_STATIC | not whole-stream semantic sequence proof |
| SHA-256 of authored bytes | PASS_STATIC | not independent RFC8785 Unicode conformance |
| External report validates | PASS_STATIC | `assertion_result=NOT_RUN` |
| Append-failure injection | NOT RUN | requires engine writer |
| Replay identity across two executions | NOT RUN | requires version-bound runtime |

Do not equate G1 runtime PASS with flight or mechanical acceptance.
