# Technical notes

These notes keep the detailed data checks, design choices, and measured results.
For setup and everyday use, start with the [README](../README.md).

## Findings from the six CSVs

Each reading file has **12,648 records**, 17 channels × 744 hours, January 1–31.
Year N+1 has no header and is otherwise **identical** to Year N's readings.
Its events differ: **997 / 844 rows**. Synthetic calendar labels **2024 / 2025**
keep the years separate; they are not claimed recording years.

The water code needs trimming. T means both temperature and traffic in the type
table. IDs **15/18** have subzero readings and fit −30…70 °C; use them provisionally.
ID 16 ranges 1.85…30 and is ambiguous. ID **19** has 744 readings without an inventory
entry. Exclude both from temperature. Inventory IDs **7/10/17** have no readings.
Resolve IDs before feature selection; a join on duplicated T would multiply rows.

Both reading files have zero exact duplicates, invalid dates, missing IDs/values,
or out-of-range measurements in checked channels. Each retains **6,696 feature
readings**. Convert source lux to millilux once; preserve water/temperature precision.
At each boundary take each working sensor's most recent reading (at most two hours
old), then the median of available same-type sensors. Actual maximum carry age:
**0.9992 hours**. First hour: no past boundary data.

Events are unsorted with **44 / 31 hour-24 records**, and all event hours are 1–24.
No surrounding chronology supports repair. Keep valid hours 1–23 literal; quarantine
both same-day and following-day midnight for hour 24. A consistent hour-ending
interpretation remains an unresolved alternative for the professor/course owner.
One unknown-kind event row per year also invalidates its hour. N+1 has one anonymous
collision, retained because separate incidents can share measurements.

There is no coverage flag. The explicit assumption is complete January event logs
where sensors operate, except known unknown hours. Disabling
assume_complete_event_log excludes all targets. Count a row once when any valid
recorded CloseCarCm, CloseGuardrailCm, or SkidAngle exists; damage/injury alone
describes an accident. A covered hour without qualifying events has target zero.
LicencePlate is removed at ingestion before features or reports.

| Cleaning / coverage | Year N | Year N+1 |
|---|---:|---:|
| Hourly grid | 744 | 744 |
| Missing boundary features | 1 | 1 |
| Unknown event coverage in grid | 30 | 27 |
| Observed within-hour speed changes excluded | 329 | 329 |
| Usable target hours (exclusions overlap) | 405 | 404 |
| Usable zero-event hours | 114 | 132 |
| Valid dated near-event rows before hourly exclusions | 920 | 793 |

[cleaning_summary.json](../results/cleaning_summary.json) includes counts, safe examples,
SHA-256 source checksums, missingness, feature means, and speed support.

## How a decision is made

One tick takes one UTC timestamp and sensor snapshot. The weather router uses strict
comparisons: light_millilux < 500 OR (water_um > 1000 AND temperature_c < 0).
Cold alone is insufficient. A clear router returns weather 80 without calling the
neural network. A trigger scores reduced limits **70/60/50/40**, choosing the highest
with estimated count ≤1/hour. If none qualifies, select 40 and display **target unmet**.

Independently, live air fetches Open-Meteo with current=european_aqi,
hourly=european_aqi, timezone=GMT, forecast_days=2. Pair timestamps and values;
select the current value and next three complete hourly values strictly after the
decision time. Reject missing hours, wrong units, nonfinite/negative values, and
current readings more than an hour old or in the future. Cache per location for
15 minutes. Failed refresh with expired cache is unavailable. API timeout: 10 seconds.

| Peak European AQI (dimensionless) | Reduction km/h | Air limit km/h |
|---|---:|---:|
| 0 through 60 | 0 | 80 |
| Above 60 through 80 | 10 | 70 |
| Above 80 through 100 | 20 | 60 |
| Above 100 | 30 | 50 |

The application computes the peak and selects its applicable policy rule before
prompting **qwen2.5:1.5b**. Real experiments showed unreliable comparisons/lookup
when the small model saw all bands together. This makes its task narrower: choose
and explain the reduction using the supplied applicable classroom rule. This
deterministic preprocessing is explicit; the model is not credited with numeric
classification. The same versioned policy renders the prompt and validates the
output. The mapping is a student assumption, not a validated traffic policy.

Ollama must return structured JSON with an allowed integer reduction, correct peak
and controlling timestamp, and a nonempty reason. Invalid/missing responses mean
unavailable; no scripted fallback supplies a decision. Identical readings, policy,
prompt, and model reuse only a previously validated real response. Connection/read
timeouts are 3/90 seconds. The GUI renders a single policy sentence from validated
fields, retaining the untouched model narrative as model_reason and raw_response
in decision evidence. Real experiments showed that free prose can be misleading or
ignore the one-sentence instruction even when structured decisions are correct.
Offline fixtures use the same parser and real local model
with their saved clock; no internet or live API is needed.

Combine valid branches by **minimum**, never by adding reductions. If either required
branch is unavailable, show **decision incomplete**, the available branch result, and
last complete timestamp. Never silently create a fresh 80 after a source failure.

Actual two-active-branch trace: light **499 millilux**, water **0 µm**, temperature
**10 °C** invokes the weather model. Estimates for 70/60/50/40 are **2.431 / 2.224 /
1.830 / 2.332** events/hour. None qualifies: weather **40**, target unmet. Saved
current AQI **30 at 12:00 UTC**, forecasts **65 / 90 / 110 at 13:00 / 14:00 / 15:00**
on November 11, 2026 (fixture decision clock 12:15 UTC) produces a real-model reduction
**30**, air **50**. Final: **min(40,50) = 40 km/h**.
See [demo_offline.json](../results/demo_offline.json) for the raw response, timestamps,
all candidate scores, and inference/cache status. Estimates do not prove safety.

## Design decisions

| Decision | Basis | Reason and trade-off | Where implemented or tested |
|---|---|---|---|
| Predict next-hour near-accident count with recorded speed as input | Student design assumption prescribed by brief; CSV observation: recorded speeds/events, no optimal labels | Supports the course objective ≤1/hour; candidate estimates remain observational, not causal | data.py, weather.py, test_weather.py |
| Provisional temperature IDs 15/18; exclude ambiguous/unknown IDs | CSV observation + documented brief assumption | Avoid duplicated T join and mixing traffic/temperature; needs inventory confirmation | config.json, clean_readings, test_data.py |
| Past-only carry ≤2h then same-type median; exclude uncovered targets | Student design assumption | Bounded missing-data handling without future leakage | build_year, alignment tests |
| AQI bands → reductions 0/10/20/30 | Student design assumption | Course/API provide no validated traffic-speed policy | policies/air_v1.json, test_air.py |
| Both valid → minimum; unavailable → incomplete | Student design assumption required by brief | Reductions are relative to 80; avoid summed reductions and false defaults | decision.py, integration/GUI tests |
| Do not repair hour 24; quarantine candidate midnights | CSV observation → conservative student assumption | Unsorted dates cannot support repair; unresolved encoding limits targets | clean_events, date tests, cleaning report |
| Complete event-log coverage except known unknown hours | Student design assumption | Necessary for meaningful zero targets; disabling it excludes all targets | config.json, coverage tests |
| Exclude speed-changing target hours | Student modeling assumption prescribed by brief | Use speed at boundary; avoid associating outcomes with changing exposures | build_year, speed exclusion tests |
| Scaled seeded 16-unit MLP; chronological 70/15/15 | Course requirement: neural network; student choices: split, size, preprocessing, seed | CPU-sized model, train-only preprocessing; small samples and sparse candidates | train, save/reload/scaler tests |
| Strict weather router; air assessed independently | Course requirement | Darkness OR wet-and-freezing triggers NN; air can reduce a bright, dry road | weather.py, decision.py, boundary/call tests |
| Compute peak/applicable rule before local-model decision | Real inference observation → student engineering assumption | Numeric comparisons and broad lookup prompts failed; narrower prompt still requires inference and validation | air.py, prompts, failed integration traces |
| Vienna, three forecast hours, GMT, 15-minute cache | Student design assumption | Free educational API; bounded calls and conservative freshness checks | config.json, cache/timeout tests |
| Treat N+1 as limited independent evidence | CSV observation | Sensor features repeat exactly despite different event outcomes | assess, year_NPlus1_assessment.json |

## Results and limitations

Frozen model: StandardScaler and MLPRegressor, 16 ReLU hidden units, lbfgs, alpha 1,
seed 42, max_iter 2000. No selection using test or N+1. Negative predictions clamp to
zero. Four inputs: light (millilux), water (µm), temperature (°C), speed (km/h).
Features are known at hour start; the target counts events in the following
half-open interval. The saved bundle includes preprocessing, feature order/units,
configuration, seed, split date ranges, versions, and creation time.

| Partition | Hours | Observed mean | Predicted mean | MLP MAE | Training-mean baseline MAE |
|---|---:|---:|---:|---:|---:|
| N train | 283 | 1.3710 | 1.3721 | 0.9017 | 0.9925 |
| N validation | 61 | 1.4262 | 1.4397 | 1.1900 | 1.1039 |
| N test | 61 | 1.1803 | 1.4315 | 0.8597 | 0.9104 |
| N+1 frozen model | 404 | 1.0891 | 1.3914 | 0.9067 | 0.8877 |

Test improvement is small; validation and N+1 are worse than the constant baseline.
Weather-triggered subset sizes: **104/17/22/142** for train/validation/test/N+1.
Test subset MAE **0.7919** vs baseline **0.9634**, observed mean **1.0000**, predicted
mean **1.3021**. N+1 subset MAE **0.9315** vs baseline **0.9489**.
Full subset means/metrics are in [training_metrics.json](../results/training_metrics.json).
Both years have 1/744 missing boundary rows (0.1344% per feature); usable coverage is
405/744 vs 404/744. The N+1 report compares feature means, missingness, target rates,
coverage, held-out errors, and support at each speed.

**Year N+1 assessment: insufficient evidence.** Student heuristic: fewer than 100
hours → insufficient; otherwise MAE above max(1.25×test MAE, test MAE+0.2) → recommend
retraining; repeated sensor features → insufficient independent evidence; otherwise
retain. Threshold **1.0746** exceeds actual N+1 error **0.9067**, but repeated inputs
prevent retention evidence. Preserve the original model. Clarify event-hour encoding
and coverage, and collect independent data before a meaningful retraining decision.

Training hours at 40/50/60/70/80: **0/7/84/15/177**. Only seven raw 40 observations
exist, and none survive constant-speed selection. The demo's 40 prediction extrapolates
without training support; the GUI flags this. Candidate scores can be nonmonotonic.
Small observational data cannot establish counterfactual or causal safety.
**Estimated near-accident rates are not claims about real-world safety.**
SciPy emits an ignored iprint optimizer-option warning with sklearn 1.6.1; it is
recorded in fit_warnings. Fitting completes.

Verified on November 11, 2026:

| Check | Actual result |
|---|---|
| Offline automated suite | **64 passed**, no failures/skips; results/pytest.xml |
| Separate prepare → train → evaluate commands | Passed; exact float round-trip reproduces the one-command build's metrics |
| Installed dependency consistency | pip check: no broken requirements |
| Local Ollama readiness | Required qwen2.5:1.5b tag present; saved weather artifact present |
| Real local-model smoke | Five policy cases passed: clear, exact 60/80/100, clean now with forecast 110 |
| Offline fixture + real inference | **80 → 40 → 50 → 40**, all complete; first clear/rising inference real, repeated fixtures use validated cache |
| Live Open-Meteo + real inference | Complete **80 km/h**, Vienna current AQI 44, next three forecasts 46/46/46 at 18:00/19:00/20:00 UTC; snapshot 17:07 UTC |
| Running browser GUI | Visibly verified baseline 80 and both-active 40 with target-unmet and unsupported-speed warnings; actual local inference |
| GUI scheduling/failure behavior | Offline widget tests cover Start/Stop, due ticks, redraw suppression, busy guard, bounded history, and last-complete state |

Automated network/LLM tests use doubles; smoke/demo evidence uses real Ollama.
Early real-model failures remain in results/integration_attempt_*.json. The final
prompt supplies only the applicable rule: treating this as independent LLM numerical
reasoning would overstate what was demonstrated. Free model prose remains unverified;
the displayed policy sentence uses validated structured fields.

Still to check on the laptop: prolonged unattended operation and browser sleep/resume,
fresh live observations at other locations, and any changed model/dependency version.
These bounded smoke checks do not establish long-term reliability. Ask the course
owner to confirm temperature inventory and event-hour/coverage semantics before
treating the measured target as settled. No physical road-safety validation was done.

## One-minute demonstration

1. Select Offline saved clear readings; light 1000, water 0, temperature 10; Decide
   now. A valid real-model reply gives **80**.
2. Set light **499**; decide. Weather selects **40**, target unmet, estimate **2.332/h**.
3. Restore light 1000; choose Offline saved rising forecast; decide. Weather 80,
   air 50 → **50**.
4. Lower light to 499; decide. Both active → **40**. Start schedules ticks; Stop ends them.

The offline CLI runs these four cases and saves all evidence. Fixtures are labeled
synthetic saved classroom readings with a fixed clock, not live observations.
Each new fixture needs real inference; repeated identical valid readings can use
the real-result cache. Future invalid model replies still yield incomplete.

## Results files and source map

| File | Purpose |
|---|---|
| results/weather_model.joblib | Frozen Year N model/scaler; load only this trusted local artifact |
| results/model_metadata.json | Feature schema, units, split dates, seed, versions, speed support |
| results/hourly_N.csv, hourly_NPlus1.csv | Clean hourly features, targets, coverage/exclusion flags |
| results/cleaning_summary.json | Audit counts/examples and source checksums |
| results/training_metrics.json, predictions_*.csv | Split/subset errors and per-hour predictions |
| results/year_NPlus1_assessment.json | Frozen-model assessment and rationale |
| results/demo_offline.json, demo_live.json | Actual branch decisions, raw local replies, timestamps |
| results/pytest.xml | Offline test results |
| results/local_model_smoke.json | Five real local-model policy/boundary cases |
| results/verification.json | Test/integration summary, artifact checksum, source-integrity check |
| speedlimit/data.py, weather.py | Data pipeline, training, assessment, weather production route |
| speedlimit/air.py, decision.py | API/fixtures, local model, validation, branch combination |
| app.py, tests/ | Production screen and offline component/integration/GUI checks |

## AI use

Local application model: **qwen2.5:1.5b**, Q4_K_M 1.5B, through Ollama.
Exact active prompt: [air_v6.txt](../speedlimit/prompts/air_v6.txt), rendered by
prompt_for in [air.py](../speedlimit/air.py) from [air_v1.json](../speedlimit/policies/air_v1.json).
The JSON SCHEMA in air.py is passed as format; stream=false, temperature 0, seed 42,
context 4096, output budget 256. Only AQI values, times, units, and classroom policy
facts are sent. Invalid replies remain unavailable. Caches are in memory; restart
to clear them. [AI_USE.md](../AI_USE.md) records the actual development request and
significant implementation/prompt revisions. No separate coding-model or subagent
prompts were issued.

Attribution: [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)
and **CAMS ENSEMBLE** ([Copernicus Atmosphere Monitoring Service](https://atmosphere.copernicus.eu/)).
See [free educational/non-commercial terms](https://open-meteo.com/en/terms) and
[Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs).
These sources provide data/API behavior, not endorsement of the classroom speed policy.
