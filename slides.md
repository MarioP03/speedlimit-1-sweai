---
theme: default
title: SpeedLimit
layout: default
class: bg-slate-900 text-white
colorSchema: light
aspectRatio: 16/9
drawings:
  persist: false
---

<div class="text-amber-300 uppercase tracking-widest text-sm font-bold">
Software Engineering in AI · Management briefing
</div>

<div class="grid grid-cols-[1fr_200px] items-center gap-10 mt-14">
  <div>
    <div class="text-7xl font-black tracking-tight">SpeedLimit</div>
    <div class="text-3xl leading-snug mt-6">
      Adapting a road’s speed limit to weather and air quality
    </div>
    <div class="mt-10 text-xl text-slate-300">
      Mario Palagyi &amp; Jerome Puthuparampil
    </div>
  </div>
  <div class="text-center">
    <div style="display:grid;place-items:center;width:190px;height:190px;border:16px solid #dc2626;border-radius:50%;background:#fff;color:#101820;font:bold 90px/1 Arial">
      80
    </div>
    <div class="mt-4 text-sm uppercase tracking-widest text-slate-300">
      Starting limit · km/h
    </div>
  </div>
</div>

<div class="absolute bottom-12 left-14 right-14 border-t-4 border-dashed border-amber-300"></div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
01 / Stakeholders and requirements
</div>

# Who needs what from SpeedLimit?

<div class="grid grid-cols-2 gap-12 mt-8">
  <div>
    <div class="text-2xl font-bold text-teal-800 mb-4">People affected</div>
    <div class="text-xl leading-snug">
      <b>Road authorities</b> approve the policy.<br><br>
      <b>Operators</b> need clear decisions and failure alerts.<br><br>
      <b>Drivers and the public</b> bear the consequences of unsafe or inconsistent limits.
    </div>
  </div>
  <div class="border-l-2 border-slate-300 pl-8">
    <div class="text-2xl font-bold text-teal-800 mb-4">Quality priorities</div>
    <div class="text-xl leading-snug">
      <b>Reliability</b> — show incomplete decisions when a required source fails.<br><br>
      <b>Traceability</b> — retain inputs, timestamps and branch reasons.<br><br>
      <b>Maintainability</b> — separate data, models, rules and display.
    </div>
  </div>
</div>

<div class="mt-6 text-base text-slate-600">
Engineers maintain the system. Data owners clarify records. Regulators assess deployment obligations.
</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
02 / Architecture and working MVP
</div>

# Training and operation

<div class="text-lg font-bold text-teal-800 mt-3">Training on historical records</div>

```mermaid
flowchart LR
  A["Course CSVs"] --> B["Clean and align"]
  B --> C["Train and evaluate"]
  C --> D["Saved model + preprocessing"]
```

<div class="text-lg font-bold text-teal-800 mt-3">Each production decision</div>

```mermaid
flowchart LR
  S["Simulated sensors"] --> W["Weather router + model"]
  A["Air-quality API"] --> L["Local LLM + validation"]
  W --> C["Combine valid limits"]
  L --> C
  C --> G["GUI + history"]
```

<div class="mt-4 text-lg">
The weather model runs only on a trigger. Air quality runs independently.
The lower valid limit becomes the recommendation.
</div>

<style>
.mermaid {
  display: flex;
  justify-content: center;
}
</style>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
03 / Features, cleaning and imputation
</div>

# Data choices shaped the model

<div class="grid grid-cols-[0.85fr_1.15fr] gap-10 mt-6">
  <div>
    <div class="text-6xl font-black text-teal-800">405 / 744</div>
    <div class="mt-2 text-xl font-bold">usable Year N hours</div>
    <div class="mt-5 text-lg leading-snug">
      <b>Inputs</b><br>
      Light, road water, temperature and the recorded speed limit at the hour’s start.
    </div>
    <div class="mt-4 text-lg leading-snug">
      <b>Target</b><br>
      Near-accidents in the following hour.
    </div>
  </div>
  <div class="border-l-2 border-slate-300 pl-7 text-lg leading-snug">
    <div class="font-bold text-teal-800">Cleaning</div>
    <div class="mt-1">
      Resolve ambiguous sensors, convert lux to millilux and exclude unclear event times.
      Drop licence plates.
    </div>
    <div class="font-bold text-teal-800 mt-5">Imputation</div>
    <div class="mt-1">
      Carry earlier readings forward for up to two hours.
      Take the median across working sensors.
    </div>
    <div class="font-bold text-teal-800 mt-5">Evaluation</div>
    <div class="mt-1">
      Exclude hours with changing limits. Split hours chronologically and fit preprocessing on training data.
    </div>
  </div>
</div>

<div class="mt-5 text-base text-slate-600">
Provisional assumptions include temperature sensor IDs and complete event coverage for zero-event hours.
</div>

---
layout: default
class: bg-slate-900 text-white
---

<div class="text-sm font-bold tracking-widest text-amber-300 uppercase">
04 / Demonstration and test evidence
</div>

# What did the prototype demonstrate?

<div class="grid grid-cols-4 gap-4 mt-6 text-center">
  <div v-for="item in [{label:'Clear',speed:80},{label:'Dark',speed:40},{label:'Poor air forecast',speed:50},{label:'Both',speed:40}]" :key="item.label">
    <div class="text-lg font-bold mb-2">{{ item.label }}</div>
    <div style="display:grid;place-items:center;width:92px;height:92px;margin:auto;border:9px solid #dc2626;border-radius:50%;background:white;color:#101820;font:bold 43px/1 Arial">
      {{ item.speed }}
    </div>
    <div class="mt-1 text-sm text-slate-300">km/h</div>
  </div>
</div>

<div class="grid grid-cols-2 gap-8 mt-7">
  <div class="text-lg leading-snug">
    <b class="text-amber-300">64 automated tests + 5 real-model checks</b><br>
    Checks covered boundaries, failures and branch combination.
    Automated API/LLM tests used prepared responses.
  </div>
  <div class="text-lg leading-snug">
    <b class="text-amber-300">Test error of 0.86 incidents/hour</b><br>
    A constant estimate scored 0.91.
    The constant estimate performed better the following year.
  </div>
</div>

<div class="mt-5 border-l-4 border-amber-300 pl-4 text-base">
In darkness, every speed missed the target. The fallback at 40 estimated 2.33 events/hour,
with zero usable training hours at that speed.
</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
05 / Human oversight and deployment
</div>

# What would responsible operation require?

<div class="grid grid-cols-2 gap-10 mt-7">
  <div>
    <div class="text-2xl font-bold text-teal-800 mb-4">People in the loop</div>
    <div class="text-lg leading-snug">
      <b>Before deployment</b><br>
      A traffic-safety specialist approves the speed policy.
      A data specialist validates labels and model evidence.
    </div>
    <div class="text-lg leading-snug mt-5">
      <b>During operation</b><br>
      A trained operator investigates failed or uncertain decisions
      and follows an approved fallback procedure.
    </div>
  </div>
  <div class="border-l-2 border-slate-300 pl-7">
    <div class="text-2xl font-bold text-teal-800 mb-4">Compliance assessment</div>
    <div class="text-lg leading-snug">
      A deployment that sets road limits could qualify as high-risk AI
      because it performs a road-traffic safety function.
    </div>
    <div class="text-lg leading-snug mt-5">
      The next phase needs risk management, documented data and performance,
      oversight, monitoring and the applicable conformity process.
      Worldwide deployment requires local reviews.
    </div>
  </div>
</div>

<div class="mt-5 text-sm text-slate-600">
Preliminary assessment. Compliance has not been demonstrated.
EU AI Act references — Annex III(2), Articles 9 and 14.
</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
06 / Architectural change requests
</div>

# Can the design accommodate change?

<div class="mt-7 text-lg">

| Requested change | Components affected | Work required |
|---|---|---|
| Some sensors use Fahrenheit | Input adapters and cleaning | Convert to Celsius before routing or model input. Test units and boundaries. |
| Only skidding counts as a near-accident | Target construction, training and evaluation | Rebuild hourly labels, retrain and compare results. |
| Electric cars are exempt from air restrictions | Vehicle inputs, air policy, decision combination and display | Apply air restrictions by vehicle type. Preserve weather restrictions and resolve how different limits reach drivers. |

</div>

<div class="mt-7 text-xl font-bold text-teal-800">
Separate components make the affected responsibilities easier to identify.
</div>

<div class="mt-4 text-base text-slate-600">
These are proposed design changes. The current prototype implements the baseline case.
</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
07 / AI use and lessons learned
</div>

# What did we learn from implementation?

<div class="grid grid-cols-2 gap-10 mt-7">
  <div>
    <div class="text-2xl font-bold text-teal-800">Two uses of AI</div>
    <div class="mt-4 text-lg leading-snug">
      <b>Development</b><br>
      A coding assistant wrote the code and tests.
      Reproducible commands and saved results support inspection.
    </div>
    <div class="mt-4 text-lg leading-snug">
      <b>Operation</b><br>
      Early local-model prompts misread pollution bands.
      The revised prompt supplies the applicable rule.
      Python validates the returned decision.
    </div>
  </div>
  <div class="border-l-2 border-slate-300 pl-7">
    <div class="text-2xl font-bold text-teal-800">Lessons for the next phase</div>
    <div class="mt-4 text-lg leading-snug">
      Data assumptions can change what the model learns.
      Passing software tests gives limited evidence about road safety.
    </div>
    <div class="mt-4 text-lg leading-snug">
      Prompt revisions need real-model tests.
      Historical predictions cannot establish the safety effect of changing a sign.
    </div>
  </div>
</div>

<div class="mt-5 text-sm text-slate-600">
Course reflection gap — the development record contains prompt revisions,
but the required no-AI comparison still needs to be documented.
</div>

---
layout: default
class: bg-slate-900 text-white
---

<div class="text-sm font-bold tracking-widest text-amber-300 uppercase">
08 / Recommendation
</div>

<div class="mt-10 text-5xl font-black leading-tight">
Continue classroom validation
</div>

<div class="mt-7 text-2xl leading-snug max-w-3xl">
Confirm the data meanings, collect independent observations at lower speeds,
and agree on a validated speed policy before considering a road trial.
</div>

<div class="mt-6 text-xl leading-snug text-slate-300 max-w-3xl">
The next decision should depend on better evidence at 40 km/h,
reliable operation over time and an approved human response to failures.
</div>

<div class="absolute bottom-14 left-14 right-14">
  <div class="border-t-4 border-dashed border-amber-300 mb-5"></div>
  <div class="text-2xl font-bold">Thank you. Questions?</div>
</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
Backup / Weather-router test exercise
</div>

# Four boundary tests

<div class="text-lg mt-5">

| Test case ID | Illuminance (millilux) | Water level (µm) | Temperature (°C) | Expected reduction decision |
|---|---:|---:|---:|---|
| W1 | 499 | 0 | 10 | Yes |
| W2 | 500 | 1000 | −1 | No |
| W3 | 500 | 1001 | −1 | Yes |
| W4 | 500 | 1001 | 0 | No |

</div>

<div class="mt-7 text-lg">

The rule is `light < 500 OR (water > 1000 AND temperature < 0)`.

These cases check strict comparisons and the combination of AND with OR.
The tests also verify whether the neural network was called.

</div>

<div class="mt-5 text-base text-slate-600">
“Yes” means the router requests weather-model evaluation.
The prediction and speed selection happen afterward.
</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
Backup / Air-quality test exercise
</div>

# Reference answers come from the policy

<div class="text-base mt-4">

| Test | Current AQI | Next three forecasts | Expected reduction |
|---|---:|---|---:|
| A1 — Clear | 30 | 35, 40, 45 | 0 km/h |
| A2 — Boundary 60 | 60 | 40, 50, 55 | 0 km/h |
| A3 — Boundary 80 | 40 | 60, 70, 80 | 10 km/h |
| A4 — Boundary 100 | 40 | 80, 90, 100 | 20 km/h |
| A5 — Forecast deterioration | 30 | 65, 90, 110 | 30 km/h |
| A6 — Incomplete forecast | 30 | Missing an hour | Unavailable |

</div>

<div class="mt-5 text-lg leading-snug">
The golden reduction comes from the versioned classroom policy.
Test the peak value, timestamp and structured amount.
Explanation wording may vary.
</div>

<div class="mt-4 text-base text-slate-600">
Also test malformed JSON, a wrong reduction, an API timeout and a missing local model.
The policy’s speed reductions are student assumptions.
</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
Backup / Sequence-diagram exercise
</div>

# One timestamped decision

```mermaid
sequenceDiagram
  participant G as GUI
  participant D as Decision service
  participant W as Weather
  participant A as Air source
  participant L as Local LLM
  G->>D: Sensor snapshot and time
  D->>W: Apply router
  opt Weather trigger
    W->>W: Score candidate speeds
  end
  W-->>D: Limit and model evidence
  D->>A: Request current and forecast AQI
  A-->>D: Validated readings or failure
  opt Air readings valid
    D->>L: Readings and applicable policy rule
    L-->>D: Structured response
    D->>D: Validate response
  end
  D->>D: Combine branch results
  D-->>G: Limit or incomplete status
```

<div class="text-sm text-slate-600">
Branches return status and evidence. Both must be valid for a new final limit.
</div>

---
layout: default
class: bg-stone-50 text-slate-900
---

<div class="text-sm font-bold tracking-widest text-teal-700 uppercase">
Backup / Component test planning
</div>

# Five scenarios per component

<div class="text-sm">

| Component and responsibility | Five proposed test scenarios |
|---|---|
| Loader reads the course CSVs | Semicolon delimiter; decimal comma; detected header; headerless N+1; first row retained |
| Cleaner normalizes sensor and event records | Unit conversion; ambiguous sensor; unknown ID; invalid event time; plate removal |
| Hourly builder creates model inputs and targets | Past-only alignment; stale reading; zero events; speed-changing hour; missing coverage |
| Trainer fits and evaluates the weather model | Chronological split; training-only scaler; repeatable seed; save/reload; baseline comparison |
| Weather service routes and scores candidates | Clear path; exact thresholds; highest qualifying speed; target unmet; missing model |
| Air source supplies usable AQI readings | Correct forecast times; missing hour; negative value; valid cache; expired-cache refresh failure |
| LLM adapter validates structured decisions | Correct amount; malformed JSON; wrong amount; wrong timestamp; timeout |
| Decision service combines branch results | Both clear; weather lower; air lower; both active; branch unavailable |
| GUI controls and displays decisions | Decide now; Start tick; Stop; redraw suppression; last complete timestamp |

</div>

<div class="mt-4 text-sm text-slate-600">
This is a proposed coverage checklist. The recorded 64-test suite must be checked
before claiming that every listed scenario already has an implemented test.
</div>