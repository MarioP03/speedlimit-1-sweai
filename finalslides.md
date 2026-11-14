---
theme: default
title: SpeedLimit - Six-minute management briefing
author: Mario Palagyi and Jerome Puthuparampil
info: |
  Six main slides for a six-minute management presentation.
  Nine backup slides support technical discussion.
  Based on the implemented prototype and recorded project evidence.
layout: none
defaults:
  layout: none
canvasWidth: 1280
aspectRatio: 16/9
colorSchema: light
fonts:
  sans: Arial
  provider: none
drawings:
  persist: false
---

<div class="sl-deck sl-dark">
<div class="sl-cover">
  <div>
    <h1>SpeedLimit</h1>
    <p class="sl-subtitle">Speed recommendations from<br>weather and air quality</p>
    <p class="sl-authors">Mario Palagyi &amp; Jerome Puthuparampil</p>
  </div>
</div>
<p class="sl-cover-purpose">Local speed limit setting website prototype that lets operators automatically or manually adjust speed limit based on weather and air conditions</p>
<div class="sl-footer"><span>Classroom prototype</span><span>01 / 07</span></div>
</div>

<style>
:global(.sl-deck) { position:relative; width:1280px; height:720px; box-sizing:border-box; padding:48px 64px 66px; background:#fafaf9; color:#0f172a; font-family:Arial,sans-serif; font-size:25px; line-height:1.35; }
:global(.sl-deck *) { box-sizing:border-box; }
:global(.sl-deck h1) { margin:12px 0 28px; font-size:44px; font-weight:750; line-height:1.12; letter-spacing:-1px; color:inherit; }
:global(.sl-deck h2) { margin:0 0 12px; font-size:27px; font-weight:700; line-height:1.2; color:#0f766e; }
:global(.sl-deck p) { margin:12px 0; }
:global(.sl-deck strong) { font-weight:750; }
:global(.sl-deck ul), :global(.sl-deck ol) { padding-left:27px; margin:12px 0; }
:global(.sl-deck li) { margin:12px 0; }
:global(.sl-deck code) { font-size:.88em; }
:global(.sl-deck table) { width:100%; border-collapse:collapse; margin:14px 0; font-size:22px; line-height:1.28; }
:global(.sl-deck th) { text-align:left; background:#0f172a; color:#fff; padding:11px 14px; font-weight:700; }
:global(.sl-deck td) { padding:11px 14px; border-bottom:1px solid #cbd5e1; vertical-align:top; }
:global(.sl-deck a) { color:#0f766e; text-decoration:underline; }
:global(.sl-kicker) { color:#0f766e; font-size:15px; font-weight:700; letter-spacing:1.7px; text-transform:uppercase; }
:global(.sl-footer) { position:absolute; left:64px; right:64px; bottom:24px; display:flex; justify-content:space-between; gap:24px; border-top:1px solid #cbd5e1; padding-top:12px; font-size:15px; line-height:1.2; color:#64748b; }
:global(.sl-dark) { background:#0f172a; color:#fff; }
:global(.sl-dark .sl-kicker), :global(.sl-dark h2), :global(.sl-dark .sl-accent) { color:#fcd34d; }
:global(.sl-dark .sl-muted) { color:#cbd5e1; }
:global(.sl-dark .sl-footer) { color:#cbd5e1; border-color:#475569; }
:global(.sl-dark table th) { background:#1e293b; }
:global(.sl-dark table td) { border-color:#475569; }
:global(.sl-dark a) { color:#fcd34d; }
:global(.sl-muted) { color:#475569; }
:global(.sl-accent) { color:#0f766e; }
:global(.sl-small) { font-size:21px; line-height:1.35; }
:global(.sl-note) { margin-top:20px; padding-left:18px; border-left:4px solid #d97706; font-size:22px; line-height:1.32; }
:global(.sl-cols) { display:grid; grid-template-columns:1fr 1fr; gap:46px; align-items:start; }
:global(.sl-cover) { display:grid; grid-template-columns:1fr 270px; gap:50px; align-items:center; margin-top:64px; }
:global(.sl-cover h1) { font-size:88px; letter-spacing:-3px; margin:0 0 24px; }
:global(.sl-subtitle) { font-size:36px; line-height:1.22; }
:global(.sl-authors) { margin-top:34px !important; font-size:23px; color:#cbd5e1; }
:global(.sl-base) { text-align:center; border-left:2px solid #fcd34d; padding-left:34px; }
:global(.sl-base strong) { display:block; font-size:128px; line-height:1; font-weight:800; color:#fcd34d; }
:global(.sl-base span) { display:block; margin-top:16px; font-size:21px; }
:global(.sl-cover-purpose) { margin-top:54px !important; max-width:930px; font-size:27px; }
:global(.sl-training) { padding-bottom:18px; margin-bottom:18px; border-bottom:1px solid #cbd5e1; font-size:23px; }
:global(.sl-diagram) { display:flex; justify-content:center; align-items:center; width:100%; height:290px; }
:global(.sl-diagram .mermaid) { width:100%; height:100%; display:flex; justify-content:center; align-items:center; }
:global(.sl-diagram svg) { width:100% !important; height:100% !important; max-width:100% !important; max-height:100% !important; }
:global(.sl-sequence) { height:445px; }
:global(.sl-stat) { margin:18px 0 6px; font-size:94px; font-weight:800; letter-spacing:-4px; line-height:1; color:#0f766e; }
:global(.sl-data-grid) { display:grid; grid-template-columns:350px 1fr; gap:54px; }
:global(.sl-data-list p) { margin:0 0 21px; font-size:25px; }
:global(.sl-results) { display:grid; grid-template-columns:repeat(4,1fr); gap:26px; margin:26px 0 30px; text-align:center; }
:global(.sl-result-label) { font-size:21px; min-height:31px; }
:global(.sl-result-number) { font-size:78px; font-weight:800; line-height:1.05; color:#fcd34d; }
:global(.sl-result-unit) { font-size:17px; color:#cbd5e1; }
:global(.sl-testline) { margin:20px 0 !important; font-size:25px; }
:global(.sl-risk-table td:first-child) { width:32%; font-weight:700; color:#0f766e; }
:global(.sl-next) { margin-top:34px; }
:global(.sl-next li) { margin:22px 0; }
:global(.sl-decision) { margin-top:30px !important; padding-top:22px; border-top:2px solid #fcd34d; font-size:28px; }
:global(.sl-backup table) { font-size:21px; }
:global(.sl-backup td), :global(.sl-backup th) { padding:9px 12px; }
:global(.sl-tight table) { font-size:20px; }
:global(.sl-tight td), :global(.sl-tight th) { padding:8px 11px; }
</style>

---
layout: default
class: sl-deck
---

# Project and approach

<h2>Stakeholders</h2>

<p>Drivers and passengers, road operators, traffic authorities, emergency services, nearby residents, environmental agencies, data and sensor experts, software engineers, and legal specialists.</p>

<h2 style="margin-top:28px">Three-step exercise process</h2>

<p>We completed the exercises through manual work, an initial AI prompt, and a refined prompt, following the process defined in class.</p>

<h2 style="margin-top:28px">AI use and lessons learned</h2>

<ul>
  <li>We mainly present the initial-prompt outputs because we judged them the most useful for this prototype.</li>
  <li>With GPT 6.1 Sol, more elaborate prompts sometimes added complexity without improving the result.</li>
  <li>Some manual and initial-prompt solutions were similar. We kept the classroom prototype simple where more complexity didn't offer any benefit.</li>
</ul>

<div class="sl-footer"><span>AI model: GPT 6.1 Sol · Scope: classroom prototype</span><span>02 / 07</span></div>

---

<div class="sl-deck">

# Training and operation

<div class="sl-training"><strong class="sl-accent">Training:</strong> clean historical records, align hours, train and save the weather model.</div>

```mermaid
flowchart LR
  A["Course CSVs"] --> B["Clean and align"]
  B --> C["Train and evaluate"]
  C --> D["Saved model + preprocessing"]
```

<div class="sl-training"><strong class="sl-accent">Production:</strong> different steps depending on weather or air branch, validate and combine, then decision in GUI</div>

```mermaid
flowchart LR
  S["Simulated sensors"] --> W["Weather rule and saved model"]
  A["Live or saved AQI"] --> L["Air policy and local LLM"]
  W --> C["Validate and combine"]
  L --> C
  C --> G["GUI and evidence"]
```

<div class="sl-footer"><span>Weather branch invokes only on trigger of condition · Air runs independently</span><span>03 / 07</span></div>
</div>

---
layout: default
class: sl-deck
---

<div class="sl-kicker">Data engineering</div>
<h1>Data quality shaped the model</h1>
<div class="sl-data-grid">
  <div>
    <div class="sl-stat">405 / 744</div>
    <p><strong>usable Year N hours</strong></p>
    <p class="sl-small sl-muted" style="margin-top:30px">
      Inputs at hour start:<br>
      light, water, temperature,<br>
      recorded speed limit.
    </p>
    <p class="sl-small">
      <strong>Target:</strong> near-accidents<br>
      in the following hour.
    </p>
  </div>
  <div class="sl-data-list">
    <p style="font-size:23px;line-height:1.25;margin-bottom:16px">
      <strong class="sl-accent">Sensor meaning</strong><br>
      Resolve ambiguous sensor identities.
      <span class="sl-muted" style="display:block;font-size:18px;line-height:1.25;margin-top:6px">
        IDs 15/18 provisionally represent temperature.
        ID 16 is ambiguous; ID 19 has no inventory entry.
        Both are excluded from model inputs.
      </span>
    </p>
    <p style="font-size:23px;line-height:1.25;margin-bottom:16px">
      <strong class="sl-accent">Event timing</strong><br>
      Set aside events with unresolved times.
      <span class="sl-muted" style="display:block;font-size:18px;line-height:1.25;margin-top:6px">
        44 events use hour 24, including event-file row 74.
        Incidents use hours 1–24; sensors use 0–23.
        The full hour convention remains unresolved.
      </span>
    </p>
    <p style="font-size:23px;line-height:1.25;margin-bottom:0">
      <strong class="sl-accent">Time alignment</strong><br>
      Use past readings; exclude speed-changing hours.
      <span class="sl-muted" style="display:block;font-size:18px;line-height:1.25;margin-top:6px">
        A 09:50 reading can supply the 10:00 example.
        One speed per hour simplifies reality and loses data.
        Further engineering could model shorter intervals after
        timestamp clarification.
      </span>
    </p>
  </div>
</div>
<div class="sl-note">Provisional assumptions: temperature IDs, event-hour interpretation, and complete event logs for zero-event hours.</div>
<div class="sl-footer"><span>Raw CSVs stay unchanged · Cleaning actions and source checksums are recorded</span><span>04 / 07</span></div>


---

<div class="sl-deck sl-dark">
<div class="sl-kicker">Evidence</div>

# Demonstration and measured results
<div class="sl-results" style="grid-template-columns:repeat(5,minmax(0,1fr));gap:16px">
  <div>
    <div class="sl-result-label" style="font-size:19px">Clear</div>
    <div class="sl-result-number" style="font-size:64px">80</div>
    <div class="sl-result-unit">km/h</div>
  </div>
  <div>
    <div class="sl-result-label" style="font-size:19px">Black Ice</div>
    <div class="sl-result-number" style="font-size:64px">70</div>
    <div class="sl-result-unit">km/h</div>
  </div>
  <div>
    <div class="sl-result-label" style="font-size:19px">Dark</div>
    <div class="sl-result-number" style="font-size:64px">40</div>
    <div class="sl-result-unit">km/h</div>
  </div>
  <div>
    <div class="sl-result-label" style="font-size:19px">Poor air forecast</div>
    <div class="sl-result-number" style="font-size:64px">50</div>
    <div class="sl-result-unit">km/h</div>
  </div>
  <div>
    <div class="sl-result-label" style="font-size:19px">Both</div>
    <div class="sl-result-number" style="font-size:64px">40</div>
    <div class="sl-result-unit">km/h</div>
  </div>
</div>

<p class="sl-testline"><strong class="sl-accent">64 automated tests passed</strong> and five recorded real-model checks passed.</p>

| Evaluation dataset | Network MAE | Baseline MAE |
|---|---:|---:|
| Year N test | **0.86** | 0.91 |
| Year N+1 | 0.91 | **0.89** |

<p class="sl-small sl-muted">MAE: average absolute prediction error, measured in near-accidents per hourly example. Lower = better</p>

<p class="sl-small sl-muted">Validation also favored the baseline. Predictive improvement remains limited.</p>
<div class="sl-footer"><span>Real-model checks and demos recorded 13 Nov</span><span>05 / 07</span></div>
</div>

---

<div class="sl-deck">
<div class="sl-kicker">Risks and lessons</div>

# Limits that determine the next step

<div class="sl-risk-table">

| Limitation | Consequence |
|---|---|
| Data Engineering | Low predictive performance and oversimplified data engineering, leading to information loss, highlighting this step's importance. |
| No training hours at 40 km/h | The dark-road fallback has weak support. Every candidate misses the target in that example. |
| Year N+1 repeats sensor readings | Following-year results provide limited independent evidence. |
| LLM made numerical policy errors | Python supplies the checked peak and applicable rule, then validates the response. |

</div>

<div class="sl-note" style="margin-top:30px"><strong>Historical associations do not establish the safety effect of changing speed limit.</strong></div>
<p class="sl-small sl-muted" style="margin-top:22px">The AQI-to-speed mapping is an educated assumption. Validation further needed</p>
<div class="sl-footer"><span>Target unmet and unsupported-speed warnings remain visible in the GUI</span><span>06 / 07</span></div>
</div>

---

<div class="sl-deck sl-dark">
<div class="sl-kicker">Recommendation</div>

# Continue controlled validation

<ol class="sl-next">
  <li><strong class="sl-accent">Clarify data definitions</strong><br>Confirm sensors (e.g. T, and IDs), event times, and logging coverage (0 accidents recorded hours).</li>
  <li><strong class="sl-accent">Strengthen the model evidence</strong><br>Collect observations at reduced speeds (40 km/h) and compare simpler models.</li>
  <li><strong class="sl-accent">Validate the operating policy</strong><br>Human oversight and failure response, then check reliability over time.</li>
</ol>

<p class="sl-decision"><strong>Further plans include:</strong> Examine data in detail, fix excluded data thus better model performance, human oversight</p>
<div class="sl-footer"><span>Thank you! - Technical backup slides follow</span><span>07 / 07</span></div>
</div>

---

<div class="sl-deck sl-backup">
<div class="sl-kicker">Backup A · Sequence</div>

# One timestamped decision

<div class="sl-diagram sl-sequence">

```mermaid
sequenceDiagram
  participant G as GUI
  participant D as Decision service
  participant W as Weather
  participant A as Air source
  participant L as Local LLM
  G->>D: Sensor snapshot and UTC time
  D->>W: Apply weather rule
  opt Weather trigger
    W->>W: Score 70, 60, 50, 40
  end
  W-->>D: Status, limit, evidence
  D->>A: Current and three future AQI hours
  A-->>D: Validated readings or unavailable
  opt Air readings valid
    D->>L: Checked peak and applicable rule
    L-->>D: Structured reply or cached valid response
    D->>D: Validate policy and evidence
  end
  D-->>G: Minimum valid limit or incomplete
```

</div>

<div class="sl-footer"><span>Logical independence · Sequential execution · Both branches required for a new final limit</span><span>Backup A</span></div>
</div>

---

<div class="sl-deck sl-backup sl-tight">
<div class="sl-kicker">Backup B · Data audit</div>

# Source-data findings and handling

| Finding | Handling |
|---|---|
| Semicolons, decimal commas, water code `W ` | Explicit parsing, numeric normalization, trimmed codes |
| Headerless N+1 reading file | Assign known columns and preserve the first observation |
| `T` means temperature and traffic | Use IDs 15/18 provisionally and exclude ambiguous ID 16 |
| Unknown ID 19 and missing IDs 7/10/17 | Exclude unknown readings and record inventory discrepancies |
| Hour-24 events: 44 in N, 31 in N+1 | Quarantine invalid dates and plausible affected midnights |
| No event-coverage field | Assume complete logs except known uncertain hours |
| Identifying licence plates | Drop at the ingestion boundary |
| N+1 readings repeat N exactly | Flag limited independence in the assessment |

<p class="sl-small sl-muted">Actual checked sensor readings had zero exact duplicates, invalid dates, missing numeric IDs/values, or out-of-range values.</p>
<div class="sl-footer"><span>Provisional mappings and event-hour semantics still require confirmation</span><span>Backup B</span></div>
</div>

---

<div class="sl-deck sl-backup">
<div class="sl-kicker">Backup C · Feature engineering</div>

# What one training row means

<p><strong class="sl-accent">At 10:00:</strong> use weather and posted speed known by 10:00.<br><strong class="sl-accent">Target:</strong> near-accidents from 10:00 inclusive to 11:00 exclusive.</p>

| Step | Implemented rule |
|---|---|
| Align readings | Latest value at or before the boundary, at most two hours old |
| Combine sensors | Median across available sensors of the same feature |
| Normalize units | Lux multiplied by 1,000 once, water in µm, temperature in °C |
| Count events | One row counts once if any valid near-event measurement exists |
| Distinguish zero and unknown | Zero requires assumed coverage, unknown coverage excludes the hour |
| Keep usable targets | All features present, coverage acceptable, no within-hour speed change |

<div class="sl-note">A 09:50 reading can describe 10:00. A 10:10 reading cannot. The first hour has no past boundary features.</div>
<div class="sl-footer"><span>405 usable N hours and 404 N+1 hours · Exclusion categories overlap</span><span>Backup C</span></div>
</div>

---

<div class="sl-deck sl-backup">
<div class="sl-kicker">Backup D · Weather model</div>

# Model and evaluation

<p class="sl-small"><strong>StandardScaler + MLPRegressor:</strong> four inputs, 16 ReLU hidden units, one count estimate.<br>Chronological 70/15/15 split, training-only scaling, seed 42.</p>

| Partition | Hours | Network MAE | Training-mean baseline MAE |
|---|---:|---:|---:|
| N training | 283 | 0.902 | 0.993 |
| N validation | 61 | 1.190 | 1.104 |
| N test | 61 | 0.860 | 0.910 |
| N+1, frozen model | 404 | 0.907 | 0.888 |

<p class="sl-small"><strong>Training support at 40 / 50 / 60 / 70 / 80:</strong> 0 / 7 / 84 / 15 / 177 hours.</p>
<div class="sl-note"><strong>N+1 verdict: insufficient evidence.</strong> Its sensor inputs repeat N exactly. The original model remains unchanged.</div>
<div class="sl-footer"><span>MAE measures average absolute count error in events/hour · No causal intervention test</span><span>Backup D</span></div>
</div>

---

<div class="sl-deck sl-backup">
<div class="sl-kicker">Backup E · Weather tests</div>

# Strict boundaries and fallback

<p class="sl-small"><code>light &lt; 500 OR (water &gt; 1000 AND temperature &lt; 0)</code><br>Units: millilux, µm, °C. Clear weather returns 80 without a network call.</p>

<div class="sl-cols">
<div>

| Light | Water | Temp. | Trigger |
|---:|---:|---:|---|
| 499 | 0 | 10 | Yes |
| 500 | 1000 | -1 | No |
| 500 | 1001 | -1 | Yes |
| 500 | 1001 | 0 | No |

</div>
<div>

| Dark-road candidate | Estimated events/h |
|---|---:|
| 70 km/h | 2.431 |
| 60 km/h | 2.224 |
| 50 km/h | 1.830 |
| 40 km/h | 2.332 |

</div>
</div>

<div class="sl-note">Choose the highest candidate with estimate ≤1. If none qualifies, choose 40 and display <strong>target unmet</strong>.</div>
<div class="sl-footer"><span>The fallback chooses the lowest allowed speed · Scores can be nonmonotonic</span><span>Backup E</span></div>
</div>

---

<div class="sl-deck sl-backup">
<div class="sl-kicker">Backup F · Air-quality branch</div>

# Air policy and guarded local inference

<p class="sl-small">Take the maximum European AQI across the current reading and next three complete hourly forecasts.</p>

| Peak AQI | Reduction from 80 | Air limit |
|---|---:|---:|
| 0 through 60 | 0 km/h | 80 km/h |
| Above 60 through 80 | 10 km/h | 70 km/h |
| Above 80 through 100 | 20 km/h | 60 km/h |
| Above 100 | 30 km/h | 50 km/h |

<p class="sl-small"><strong class="sl-accent">Python:</strong> verifies peak and selects the applicable rule.<br><strong class="sl-accent">Qwen:</strong> returns structured fields that Python validates against the rule and evidence.</p>
<div class="sl-note">The GUI derives its sentence from checked fields. It retains original model prose and raw JSON for inspection.</div>
<div class="sl-footer"><span>Source: Open-Meteo / CAMS ENSEMBLE · Speed mapping: student assumption</span><span>Backup F</span></div>
</div>

---

<div class="sl-deck sl-backup">
<div class="sl-kicker">Backup G · Operational behavior</div>

# Reliability and failure behavior

| Situation | Implemented behavior |
|---|---|
| Both branches valid | Final limit is the minimum, such as min(60,70) = 60 |
| Required branch unavailable | Incomplete, no new final limit, last complete time remains visible |
| Weather target unmet | Lowest candidate with warnings, branch can still be valid |
| Start / Stop | Immediate decision then due ticks / stop future ticks |
| Slow request or GUI redraw | Busy guard avoids overlap, redraw alone causes no decision |
| API freshness | Cache up to 15 minutes, validate again and fail on unsuccessful expired refresh |
| Repeated identical LLM input | Reuse a previously validated response |

<p class="sl-small sl-muted">Scheduling depends on the active page. Long unattended use and browser sleep/resume still need checks.</p>
<div class="sl-footer"><span>“Complete” describes software branch validity · Road-sign failure control remains unimplemented</span><span>Backup G</span></div>
</div>

---

<div class="sl-deck sl-backup">
<div class="sl-kicker">Backup H · Maintainability</div>

# Architectural change requests

| Proposed change | Components affected | Required work |
|---|---|---|
| Sensors report Fahrenheit | Input adapters and cleaning | Convert to Celsius before routing or inference, test boundary equivalence |
| Only skidding counts | Event target construction, training, evaluation | Rebuild labels in both years, retrain, compare results |
| Electric cars exempt from air restrictions | Vehicle inputs, air policy, combination, display | Preserve weather limits and resolve how vehicle-specific limits reach drivers |

<div class="sl-note">Separate responsibilities make change impact easier to identify. These changes remain proposals.</div>
<p class="sl-small sl-muted" style="margin-top:24px">Current scope: one laptop application, simulated weather inputs, a local weather model, Open-Meteo, and local Ollama.</p>
<div class="sl-footer"><span>Core modules: data, weather, air, decision orchestration, GUI</span><span>Backup H</span></div>
</div>

---

<div class="sl-deck sl-backup">
<div class="sl-kicker">Backup I · Accountability</div>

# AI use and human oversight

<div class="sl-cols">
  <div>
    <h2>Development and operation</h2>
    <p>A coding assistant wrote the implementation and tests.</p>
    <p>The local Qwen model participates in the runtime air branch.</p>
    <p class="sl-small sl-muted">Prompt failures and revisions are recorded. The course's required AI-free comparison still needs its own evidence.</p>
  </div>
  <div>
    <h2>Decisions requiring people</h2>
    <p><strong>Data owners:</strong> confirm sensor and event definitions.</p>
    <p><strong>Traffic specialists:</strong> approve the speed policy and failure procedure.</p>
    <p><strong>Engineers and operators:</strong> verify reliability and investigate uncertain results.</p>
  </div>
</div>

<div class="sl-note">Safety benefit, deployment readiness, and formal compliance remain unestablished.</div>
<div class="sl-footer"><span>Actual provenance and bounded evidence support a defensible discussion</span><span>Backup I</span></div>
</div>

---
layout: default
class: sl-deck sl-backup sl-tight
---

<div class="sl-kicker">Backup J · Hour exclusions</div>

# How 744 hours became 405

<p class="sl-small">One example pairs conditions known at hour start with near-accidents during the following hour.</p>

| Preparation step | Newly excluded | Remaining |
|---|---:|---:|
| January: 31 days × 24 hours | — | 744 |
| Require readings available at hour start | 1 | 743 |
| Require interpretable incident coverage | 29 | 714 |
| Exclude hours with changing posted limits | 309 | **405** |

<p class="sl-small sl-muted">
There are 329 speed-changing hours overall.
Twenty already fail the incident-coverage rule, so only 309 are additional exclusions.
The 405 examples are then split into training, validation, and test sets.
</p>

<p class="sl-small">
<strong class="sl-accent">Why exclude changing speeds?</strong>
An hour with 80 km/h until 10:20 and 60 km/h afterwards cannot be faithfully represented by one speed for the entire hour.
</p>

<p class="sl-small sl-muted">
This is a simplifying model choice, not an unavoidable cleaning rule.
It loses data and may introduce selection bias.
Clarifying event times could enable shorter constant-speed intervals with duration-aware targets.
</p>

<div class="sl-footer"><span>Counts reflect current preparation rules · Timestamp assumptions still need confirmation</span><span>Backup J</span></div>

---
layout: default
class: sl-deck sl-backup
---

<div class="sl-kicker">Backup K · Data relationships</div>

# How the source data connect

```mermaid
flowchart LR
  M["Sensor inventory and types"] -->|IDs, meanings and units| F["Hourly features"]
  R["Sensor readings"] -->|Latest known readings| F
  E["Incident records"] -->|Count qualifying events| Y["Hourly target"]
  F --> D["Join by hour and filter"]
  Y --> D
```

<p class="sl-small">
<strong class="sl-accent">Sensor mapping:</strong>
the readings' Sensor field matches inventory SensorID.
The inventory's SensorTypeCode connects to the type definitions.
</p>

<p class="sl-small sl-muted">
This mapping needs exceptions: T means both temperature and traffic,
sensor 19 lacks an inventory entry, and special sensor −1 records the posted speed limit.
</p>

<p class="sl-small">
<strong class="sl-accent">Incident relationship:</strong>
events have no sensor-ID link. They connect to sensor-derived features through the constructed hourly timeline.
</p>

<p class="sl-small sl-muted">
Incidents use hours 1–24 and sensors use 0–23.
If incidents use an hour-ending convention, all event hours may need realignment.
Quarantining hour 24 alone does not settle this question.
</p>

<div class="sl-footer"><span>Four feature values and one incident-count target per eligible hour</span><span>Backup K</span></div>

---
layout: default
class: sl-deck sl-backup sl-tight
---

<div class="sl-kicker">Backup L · Feature selection</div>

# Model inputs and excluded fields

| Weather-model input | Role |
|---|---|
| Light, in millilux | Represents lighting conditions |
| Road water, in µm | Represents water on the road |
| Temperature, in °C | Represents temperature and freezing conditions |
| Posted speed limit, in km/h | Allows predictions at different candidate limits |

<p class="sl-small">
<strong class="sl-accent">Target:</strong>
qualifying near-accidents in the following hour.
The data contain no labels identifying the optimal speed.
</p>

<p class="sl-small sl-muted">
<strong>Other channels:</strong>
humidity, wind, noise, and air pressure are outside the selected prototype feature set.
This does not establish that they are irrelevant.
Traffic cannot be confidently identified from the duplicated T code.
</p>

<p class="sl-small sl-muted">
<strong>Unclear sensors:</strong>
ID 16 has ambiguous meaning and ID 19 lacks an inventory entry.
Temperature IDs 15/18 remain provisional.
</p>

<p class="sl-small sl-muted">
<strong>Event fields:</strong>
close-car, guardrail, and skid measurements construct the target rather than becoming inputs.
Damage or injury alone does not qualify for this target.
Licence plates are discarded.
</p>

<p class="sl-small sl-muted">
<strong>Separate or unavailable information:</strong>
AQI belongs to the air branch.
Future readings and incident outcomes cannot be prediction inputs because they would leak future information.
</p>

<div class="sl-footer"><span>Four inputs · One predicted count · Additional features require further evaluation</span><span>Backup L</span></div>
