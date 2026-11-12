# BionicButterfly — Flight Readiness and V1 Acceptance Evidence Standard

- **Document ID:** BB-ACCEPT-040 | **Revision:** 0.1 | **Date:** 2026-11-12
- **Status:** PROPOSED / ALL EVIDENCE NOT RUN
- **Not a flight authorization.** V1 is **not complete** without documented, repeatable operator-controlled free flight.
- **Cross-refs:** `14`, `18`, `24`, `27`, `30`, `31`, `35–39`, `41`.

## 1. Phase gates and independent decision rights

| Gate | Meaning | Examples of relevant evidence | Who can authorize | Status |
|---|---|---|---|---|
| **G0-A** | PC-only design freeze | mathematical input schema, safety FSM, test contract | owner after SA review | NOT APPROVED |
| **G1** | deterministic host-only test execution | trace replay, state invariants, mixer saturation | owner-approved implementation scope | NOT RUN |
| **G0-B/G2** | bounded no-wing servo electrical bench | wiring proof, supply current, start-up pulses, RF health | separate owner authorization | NOT APPROVED / NOT RUN |
| **G3** | restrained wing load experiment | servo/wings, force/moment sensor logs, safety fixture | separate owner authorization | NOT APPROVED / NOT RUN |
| **G0-C/G4** | **controlled free-flight experiment** | hazard signoff, pilot/site permissions, safe flight plan, logs | explicit owner flight approval | **NO-GO** |

There is **no acceleration from simulation or one favorable force reading directly to G4**.

## 2. V1 product acceptance: what counts and what does not

| ID | Evidence statement required | Examples of false positives / limits |
|---|---|---|
| **FA-01** | measured complete aircraft mass and CG with actual battery, antenna and fasteners | CAD sum or 70 g budget is not measured mass |
| **FA-02** | verified electrical/thermal/mechanical reliability over predeclared test envelope | unloaded servo movement alone insufficient |
| **FA-03** | recorded reproducible mean force (and limitations) with baseline and uncertainty | one scale peak is not validated sustained lift |
| **FA-04** | measured differential wing moment/sign/coupling or a documented equivalent qualified method | left/right wing visual asymmetry ≠ turn proof |
| **FA-05** | separate stability assessment for pitch/roll/yaw with clear passive/active mechanism | two inputs alone not guarantee recoverability |
| **FA-06** | explicit in-air RF-loss, low-voltage, disarm and recovery safety analysis | immediate wing power cut is not an approved plan |
| **FA-07** | qualified pilot/site conditions, protection plan, permissions and go/no-go checklist | unrestricted backyard flight not assumed safe |
| **FA-08** | **operator-commanded powered free flight** evidenced with synchronized video and command/telemetry logs | 'briefly hopped' or 'fell after launch' ≠ full V1 |
| **FA-09** | **intentional directional response and recovery** under approved, measurable acceptance criteria | random drift or passive circular path not claimed pilot steerability |
| **FA-10** | documented intact controlled landing/recovery and post-flight inspection | uncontrolled crash is not a qualified recovery |
| **FA-11** | repeat runs or statistically justified repeatability criteria predeclared, not cherry-picked | one unrepeatable success ≠ robust acceptance |
| **FA-12** | traceable CAD/mechanism/power/firmware/RC revision and independent safety review | unidentified revisions cannot be used to freeze design |

**Specific numeric goals** (flight duration, minimum controlled response, height/site radius, acceptable drift, wind, battery end threshold, allowed handling and number of repeats) must be set by the owner, based on G3 evidence and site risk, **before** G4 trials. None have been approved in these files. Do not invent '30 s hover' or '2 m altitude' as acceptance facts.

## 3. Flight test record (planned format, not an instruction to launch)

```yaml
record_version: 1
trial_id: null
status: "NOT_RUN"
owner_signed_G0C_G4: null
safety_review_ref: null
pilot_and_observer: null
site_and_permissions: null
weather_wind_surface: null
physical_airframe_revision: null
actual_mass_kg: null
cg_body_m: null
wing_and_servo_revisions: null
battery_and_power_revisions: null
rc_tx_rx_firmware_versions: null
firmware_git_commit: null
approved_profile_hash: null
range_and_boundary_limits: null
flight_contingency_plan_ref: null
actual_logs_and_video_refs: []
observed_takeoff: null
observed_directional_response: null
observed_pitch_roll_yaw: null
observed_landing_or_recovery: null
postflight_damage_or_anomalies: null
acceptance_criteria_revision: null
result: "NOT_RUN"
reviewer_and_decision: null
```

Store actual *raw* telemetry and logs, not only graphs; use a synchronized timing anchor between video and commands. If onboard logs would compromise weight/power, qualify an external receiver/logger plan and disclose observability gaps.

## 4. Evidence quality and truthful statuses

Accepted statuses: `NOT_RUN`, `BLOCKED`, `INCONCLUSIVE`, `FAIL`, `PASS`. `BLOCKED` means no permission/equipment/criteria, not a test failure; `INCONCLUSIVE` means data exist but cannot support claim. Never convert `INCONCLUSIVE` to `PASS` by averaging longer or selecting only favorable directions. Record negative experiments and defects just as positive ones.

- Stage **PASS** proves only the stage's approved acceptance criteria, not the subsequent stage.
- Report measured, estimated, simulated and inferred variables with distinct labels and uncertainty.
- Model validity region must cover the tested control setting; never extrapolate to higher amplitude or new battery chemistry without revisiting bounds.
- G4 must not include casual in-air failure injection; use prior G3 safety analysis and appropriate controlled safeguards with human oversight.

## 5. Review board checklist for any future G4 decision

- [ ] Flight-specific servo/failsafe/energy policies documented and verified as far as safely possible.
- [ ] Real multi-axis force/moment/attitude evidence sufficient to support intended turn/control strategy.
- [ ] No outstanding unmitigated critical hardware/RF/structural hazards.
- [ ] Qualified transmitter/receiver/model and authenticated arm intent; no web takeover in flight.
- [ ] Operating site, pilot, observer and jurisdictional rules approved; route for stopping trials and safe recovery agreed.
- [ ] Positive owner authorization referencing **exact** firmware, profile, mechanism and test plan revisions.
- [ ] Event recording and measurement capability accepted; loss of logging labeled as loss of evidence.

**Current determination: G4 NO-GO.** This conclusion can change only on new measurements, review and explicit owner authorization; adding documentation alone cannot close it.
