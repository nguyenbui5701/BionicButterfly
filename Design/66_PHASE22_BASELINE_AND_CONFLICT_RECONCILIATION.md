# BionicButterfly — Phase 2.2 Baseline & Conflict Reconciliation

- **ID:** BB-G0A-BASE-066 | **Revision:** 0.1 | **Date:** 2026-11-12
- **Author:** Solution Architect | **Status:** PROPOSED / REMOTE BASELINE UNVERIFIED
- **Scope:** bounded **G0-A1 host-only deterministic simulator**. V1 remains actual manually RC-controlled free flight; V2 autonomy deferred. No physical I/O, no developer task and no automatic Git push.

## 1. Source-of-truth hierarchy

1. **Explicit owner decision:** V1 RC manual real flight; V2 autonomy later; owner chooses when to push.
2. **Verified project Git revision, when available:** exact path, content SHA, commit and approval record. **Not available to independently inspect in this review.** Owner said Design through Phase 2.0 is pushed to `main`; this is recorded as owner report, not a verified commit.
3. **Local available artifact snapshots:** `BionicButterfly_Phase20_System_Design_Freeze/Design/{48…55}` and `BionicButterfly_Phase21_Software_Architecture_Design/Design/{56…65}`. These are the *actual bytes* reviewed for this Phase 2.2 package; see hash manifest.
4. **Pre-Phase 2.0 documents:** referenced in 48–65 and preceding conversation. Their current owner-repo revisions were **not** reverified; their untested hardware assumptions retain OPEN status.

**Never treat later document number as proof that an older conflicting paragraph has been patched in the owner's Git tree.** This package is intentionally **additive** (`66…74`) and contains no replacements for `01…65`.

## 2. Baseline comparison and scope

| Source | Local evidence reviewed | Git `main` verification | Result |
|---|---|---|---|
| Phase 2.0 | 8 Markdown files `48–55` and manifest | Not verified from current runtime | Local snapshot review only |
| Phase 2.1 | 10 Markdown files `56–65` and manifest | Not verified from current runtime | Local snapshot review only |
| Owner's `Design/` | Reported by user as pushed through Phase 2.0 | GitHub content fetch not available here | **UNVERIFIED**, not absent |
| Current Phase 2.2 | New files `66–74` | No Git operations performed | Self-contained design proposal |

**Pre-freeze action:** on a future authorized review, record the exact `git rev-parse HEAD`, compare `Design/48–74` to local artifact hashes, identify hand-edited changes and adjudicate all conflicts. If the owner has edited an older file, do **not** overwrite it blindly with an earlier ZIP revision.

## 3. Phase 2.2 host-specific conflicts and intended disposition

`RESOLVED IN PROPOSAL` means a coherent new rule is written in 67–71; it does **not** mean that the owner's existing files or software have been changed or approved.

| ID | Source tension | Proposed precise resolution | Disposition | Owner freeze impact |
|---|---|---|---|---|
| **P22-C01** | `51` shows YAML sample; `57` proposes strict JSON | `ScenarioV1` canonical interchange is UTF-8 strict JSON v1; YAML in `51` is non-normative legacy illustration | RESOLVED IN PROPOSAL | approve D-059 |
| **P22-C02** | `59` allows event times off-grid but says one batch per evaluation; semantics across tick partitions unspecified | Eligible events `(previous_eval_us, eval_us]` (except initial tick includes time 0), fold by event-time, one atomic commit; no within-tick arm edge or unobserved enabled intermediate output | RESOLVED IN PROPOSAL | approve D-060 |
| **P22-C03** | `58` arm debounce and qualification numbers TBD | Candidate low observation 20 ms, high qualification 100 ms, periodic accepted samples + independent RF freshness; exact edges in `67/68` | PROPOSED NUMBERS | owner decision D-061 |
| **P22-C04** | `57/59` mention byte-identical trace and tolerant floats without defining stable cross-platform representation | Canonical JSON input/config, integer microsecond time and integer micro-effort trace output; cross-engine numeric comparison explicitly tolerance-based | RESOLVED IN PROPOSAL | owner D-062 |
| **P22-C05** | `60` permits DISARMED config update and crash-safe persistence but G0-A1 may omit storage | G0-A1 loads immutable, validated `SimPolicy` before run; change requires a **new run**. Persistent profile writes/rollback in running app DEFERRED | PROPOSED SCOPE REDUCTION | owner D-063 |
| **P22-C06** | `58` refers to “critical hardware SIM fault” while host must have no hardware | All such events are **injected virtual faults**; they cannot select physical hardware action | RESOLVED IN PROPOSAL | review 68 |
| **P22-C07** | `57` input-frame validity vs RF health age could leave indefinitely healthy RF after one status | Separate frame timeout and RF-health status TTL; `UNKNOWN` after RF status expires, even if serial frames continue | RESOLVED IN PROPOSAL | owner D-061 |
| **P22-C08** | `58/59` contradictory same-owner frames within one tick: semantic of denial after conflict ambiguous | Entire control component of that tick invalid; preserve no motion, revoke arm-edge candidate, contingency if already armed | RESOLVED IN PROPOSAL | tests P22-T08/09 |
| **P22-C09** | `60` SIM profile has `null` numeric fields but an executable template might silently default | No executable/pilot-armed simulation until all required `SimPolicy` fields are present, schema-valid, and explicitly approved | RESOLVED IN PROPOSAL | owner D-061 |
| **P22-C10** | `57` sample arm timeline could suggest immediate qualification | Provide normative test timeline with distinct accepted low and high frames, explicit guards and delayed motion | RESOLVED IN PROPOSAL | `71` oracle |
| **P22-C11** | `51/63` test PC-A15 expects same results over different scheduler partitions | Same-tick partition invariance is not identical to changing tick size. G0-A1 **fixes one tick size**, cross-tick-size equivalence deferred and labeled research | PROPOSED SCOPE REFINEMENT | owner D-064 |
| **P22-C12** | `58` says stop virtual motion on SIM contingency; a reader might treat it as G4 in-air failsafe | SIM-only virtual sink inhibited; **no** actual servo stop, PWM, battery cutoff or in-air response | RESOLVED IN PROPOSAL | G4 still NO-GO |

## 4. Boundary to physical V1

Phase 2.2 deliberately does **not** close Phase 2.0 conflict IDs `CF-02/03/05/06/07/12/15`, does not select servo/linkage/battery/RX, does not prove free-flight force/control, and does not address flight-specific RC-loss, emergency disarm or low-battery recovery. Open hardware/flight hazards remain independent and can block G0-B/G0-C despite a later G0-A1 approval.

## 5. Required evidence to mark conflicts CLOSED

For each P22-Cxx: exact original path+revision+paragraph, proposed canonical rule, reviewer, owner decision, accepted Design commit, test cases and evidence. **New draft files alone are not closure.** A source conflict can be `DEFERRED_OUT_OF_G0A` only with an explicit prohibition on the excluded capability.

## 6. Status and next document

`67` proposes a bounded SIM_ONLY numeric policy; `68` defines precise safety transitions; `69` defines deterministic replay and trace; `70` narrows configuration scope; `71` specifies acceptance vectors; `72` records closure evidence and stop conditions; `73` ADRs; `74` owner review packet. **Freeze readiness remains conditional, not approved.**
