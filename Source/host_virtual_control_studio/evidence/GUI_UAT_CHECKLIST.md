# Manual GUI UAT — NOT RUN by Developer

Run `scripts/studio.py --gui` using TASK014 `.venv` Python. Record actual results
below after interacting with the visible Windows application. Automated hidden
Tk/controller tests do not constitute these manual checks.

| Check | Expected | Owner observed result |
|---|---|---|
| Launch | Permanent MODEL_ONLY / NOT PROVISIONED / NO OUTPUT banner | NOT RUN |
| Nominal preset + Run entire simulation | 40 acknowledged model rows | NOT RUN |
| Select 145000us | ACTIVE, effort 250000/750000, ARM NOT GRANTED | NOT RUN |
| Play/pause/scrub | Playback changes displayed index only | NOT RUN |
| 155000us then 190000us | CONTINGENCY/inhibited, later DISARMED by qualified ACK | NOT RUN |
| rf-loss preset | Early HIGH denied; catastrophe latched after RESET | NOT RUN |
| ambiguous preset | MODEL_CONTRACT_BLOCKED, only 0/5000/10000us rows | NOT RUN |
| New empty session | Duration configurable; no report until explicit replay | NOT RUN |
| Append RC/RF events | Sliders/ARM only edit future inputs; replay is explicit | NOT RUN |
| Bad time/demand | Error visible; previous display/report cleared | NOT RUN |
| HTML/model/candidate export | Complete recording only; local labels NO OUTPUT | NOT RUN |
| Exit/reopen | No device activity or persisted runtime authority | NOT RUN |

Suggested manual protocol, duration 195000us: RF_HEALTHY at 10000; LOW neutral
at 15000 and 35000; HIGH neutral at 40000; RF_HEALTHY at 110000; HIGH neutral
at 140000; HIGH flap=500000 steering=250000 at 145000. To continue: RF_LOST
155000, RF_HEALTHY 160000, LOW neutral 165000/185000, ACK 190000. Set kind,
original time, ARM/flap/steering then click Append for each event. Do not append
out of order; Reset is an input action, not a shortcut to authorize control.

Owner/date/Windows version/result/issues: NOT RECORDED.
