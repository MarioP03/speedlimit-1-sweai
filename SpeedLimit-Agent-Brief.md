# SpeedLimit | Coding agent brief

Build a local, zero-cost student prototype that answers one question: **given the light, road water, temperature, and air quality, what speed limit would the software display, and why?** Implement and run the application end to end. The student will draw the diagrams, complete the manual exercises, and prepare the management presentation. Your handoff is working software, reproducible commands, and measured results the student can use in that presentation.

## 1. What the software must do

Implement two entry points. **Training** reads the course CSVs, repairs or excludes bad records, trains a small neural network on Year N, evaluates it, and saves the model with its preprocessing. **Production** is a local GUI that accepts simulated sensor readings, runs a decision on demand and at regular intervals, and displays the recommended limit. A laptop CPU is the target. Use Python, pandas, scikit-learn, Streamlit, pytest, a local Ollama model, and the free educational Open-Meteo endpoint. All setup, training, inference, testing, and demonstrations must work without a paid plan, billing account, or API key.

Implement these course rules exactly:

| Rule | Required behavior |
|---|---|
| Weather router | Trigger when `light_millilux < 500 or (water_um > 1000 and temperature_c < 0)`. Keep the comparisons strict. A negative temperature alone is insufficient. |
| Weather decision | Invoke the trained neural network only when the router triggers in production. Use it to choose a reduction from 80 km/h with the objective of at most one near-accident per hour on average. |
| Air decision | Independently obtain current and forecast air quality via API. Ask a local LLM whether to reduce the limit and by how much. Evaluate air quality even on a bright, dry road. |
| Default | Display 80 km/h when both branches have valid results and neither requests a reduction. |

**Project assumptions to expose in configuration.** Use the observed historical speed levels of 40, 50, 60, 70, and 80 km/h. When both branches request a reduction, choose the lower of their two limits. For example, weather at 60 and air at 70 yields 60 km/h. Each reduction is relative to 80, so the two reductions are never summed. The location, forecast horizon, AQI policy, model target, and unavailable-data behavior below are prototype choices. Record them as such in the README. The Fahrenheit, skidding-only, and electric-car scenarios from the architecture exercise are hypothetical changes. Implement the baseline definitions here.

## 2. Load the actual course data

Accept the source folder through `--data-dir`. On the student's machine the files are in `C:/Users/palag/Documents/Egyetem/IMC MSc AI/Software Engineering in AI`. Keep that path configurable and the original files read-only. Resolve the six V100 files by role:

| Role | Filename |
|---|---|
| Sensor inventory | `Case_Study_Speed_Limit_Sensors_V100.csv` |
| Types, units and ranges | `Case_Study_Speed_Limit_SensorTypes_V100.csv` |
| Training-year measurements | `Case_Study_Speed_Limit_SensorReadingsYearN_V100.csv` |
| Training-year events | `Case_Study_Speed_Limit_AccidentsYearN_V100.csv` |
| Following-year measurements | `Case_Study_Speed_Limit_SensorReadingsYearNPlus1_V100.csv` |
| Following-year events | `AccidentsYearNPlus1_V100.csv` |

1. Parse semicolons and decimal commas. Detect the readings header. Year N+1 starts with data and uses the Year N column order (`Month, Day, Hour, Minute, Second, Sensor, Value`). Assert that the first record survives loading. Keep the two years distinct even when month, day, and hour match.
2. Treat sensor `-1` as the recorded speed limit in km/h. Trim type codes. The light sensor reports lux, so multiply by 1,000 once before routing or model input. Preserve temperature and water precision internally. Display units at every GUI input.
3. Resolve the ambiguous `T` code before joining types to readings. In Year N, sensors 15 and 18 have subzero readings consistent with temperature. Use these as a **documented provisional temperature mapping**, subject to inventory and range checks. Exclude ambiguous sensors from the temperature feature by default. Sensor 19 lacks an inventory entry. Log exclusions and allow explicit ID overrides. A join on the duplicated type code can silently double the number of rows; test row counts.
4. Check duplicates, malformed dates, missing IDs or values, discrepancies between inventory and readings, and values beyond the sensor type's range. Sort chronologically. Correct a bad date only when the surrounding records support the repair. Aggregate working sensors of the same type by median. Use only earlier values for bounded carry-forward and record the maximum age, for example two hours. Save a cleaning summary with counts and examples for each action.
5. Build one row per covered hour. Count a near-accident event once when any of `CloseCarCm`, `CloseGuardrailCm`, or `SkidAngle` contains a valid recorded event measurement. The event file already records incidents; treat presence of those measurements as the course-data encoding and document it. A damage or injury field alone describes an accident. A covered hour with a complete event log and no qualifying events has a target of zero. Exclude hours with unknown coverage. Drop `LicencePlate` before creating features, logs, fixtures, or reports.

## 3. Train the weather neural network

**Predict an hourly near-accident count.** The files record the speed limit in force and events that occurred. They do not label an optimal limit. Use the recorded speed as an input during training. At decision time, change that input to a candidate speed and estimate the count for each candidate. This is an observational student model. A prediction below one is an estimate, not evidence that changing a road sign would achieve that outcome.

- Form features from light in millilux, road water in micrometers, temperature in °C, and speed in km/h. Align weather to the start of the target hour using only readings available by then. Use the speed in force at that boundary. For this simple model, exclude target hours with a change of speed during the hour and report how many were excluded. Count events in the following one-hour interval. The event count and future sensor readings must never enter the features.
- Split Year N chronologically, for example the first 70% of usable hours for training, the next 15% for validation, and the last 15% for testing. Keep whole hours together. Fit preprocessing on the training partition. Use a seeded, scaled `MLPRegressor` with one small hidden layer, such as 16 units. Clamp negative predicted counts to zero. Compare held-out mean absolute error against a constant training-mean baseline. Report sample sizes, mean observed and predicted counts, and weather-triggered subset results. Report small sample sizes and weak results honestly.
- On a weather trigger, score reduced candidate limits 70, 60, 50, and 40. Pick the highest candidate with an estimated count ≤1. If none meets the target, display the lowest candidate and a visible **target unmet** flag. Show the estimate for the selected speed. If the model is missing or required inputs are unusable, return **unavailable**. Persist the feature order, units, model and preprocessing together, plus the seed, date ranges, and dependency versions.
- Run the frozen Year N model on Year N+1 with the same cleaning and feature logic. Compare feature coverage, missingness, target rate, and held-out error. Report **retain**, **recommend retraining**, or **insufficient evidence**, with the actual metrics and rationale. Inspect the small number of observations at each speed when interpreting candidate scores. Preserve the original model for the demo.

## 4. Implement the free air-quality API and local LLM

**Fetch.** Call `https://air-quality-api.open-meteo.com/v1/air-quality` with configurable latitude and longitude, `current=european_aqi`, `hourly=european_aqi`, `timezone=GMT`, and `forecast_days=2`. Use a labeled demo location, for example Vienna (48.21, 16.37). Pair timestamps with their values. Take the current index and the next three complete hourly forecast values strictly after the decision time. Validate finite, nonnegative values, timestamps, and coverage. Cache per location for 15 minutes. Bound request time and show an unavailable status for an expired cache and failed refresh. Credit Open-Meteo and the CAMS ENSEMBLE provider in the GUI and README. [API documentation](https://open-meteo.com/en/docs/air-quality-api) · [Free educational use](https://open-meteo.com/en/terms)

**Decide.** Run `ollama pull qwen2.5:1.5b` once on the laptop. Send only the AQI values, times, units, and classroom policy to `http://127.0.0.1:11434/api/chat`. Set `stream=false`, temperature 0, and a JSON schema via `format`. Ask for a reduction in km/h and a one-sentence reason identifying the controlling current or forecast value. Parse and validate `message.content`. Cache a valid result for the same readings, policy version, and model. Downloading the model needs internet once; inference runs locally. [Local model](https://ollama.com/library/qwen2.5%3A1.5b) · [Structured output API](https://docs.ollama.com/capabilities/structured-outputs)

**Give the LLM an explicit classroom decision policy.** Use the highest AQI among the current and three forecast values. For this demo, use the following bands and reductions. The km/h mapping is a student assumption. The course and API supply no validated traffic-speed policy.

| Peak European AQI | Demo reduction | Air branch limit |
|---|---:|---:|
| 0 through 60 | 0 km/h | 80 km/h |
| Above 60 through 80 | 10 km/h | 70 km/h |
| Above 80 through 100 | 20 km/h | 60 km/h |
| Above 100 | 30 km/h | 50 km/h |

Use one versioned policy definition to render the prompt and validate the response. Require an allowed integer reduction and a nonempty reason. Flag malformed JSON, a policy-inconsistent amount, an Ollama timeout, or a missing model as **air decision unavailable**. Display the actual model response status. A live decision must go through local inference. Provide labeled AQI fixtures for the offline demonstration that exercise the same parser and still call the real local model. Reserve scripted LLM replies for automated tests.

## 5. Build one production screen

Provide three editable sensor inputs, a live/fixture air source selector, and **Decide now**, **Start**, and **Stop** controls. Use a configurable tick interval, for example 60 seconds. Each tick takes one timestamped snapshot, invokes the weather router, obtains the air result, and combines the two outcomes. Load the saved model once. Avoid overlapping ticks or repeating API calls when the UI redraws.

Show the final km/h prominently, then show the reason for each branch, the weather model's predicted count if invoked, and current/forecast AQI with source and timestamps. Keep a short decision history. If either required branch is unavailable, display **decision incomplete**, the available branch's result, and the time of the last complete decision, if any. Never silently display a fresh 80 when a source has failed.

## 6. Verify the project and hand it over

**Weather router.** Put the following four boundary cases in a parametrized test. Assert whether the weather model was called as well as the router result.

| Case | Light (millilux) | Water (µm) | Temperature (°C) | Weather trigger |
|---|---:|---:|---:|---|
| W1 | 499 | 0 | 10 | Yes |
| W2 | 500 | 1000 | −1 | No |
| W3 | 500 | 1001 | −1 | Yes |
| W4 | 500 | 1001 | 0 | No |

**Air branch.** Test at least five input/expected-result pairs against the documented demo policy. Include an all-clear forecast, the exact 60, 80, and 100 boundaries, and a currently clean location whose forecast exceeds 100. Also exercise missing forecast hours, an invalid model response, and an API timeout. Assert the decision amount and structured fields; allow different wording for equivalent explanations. Run a separate local-model smoke test and identify which evidence used real inference.

**Integration.** Exercise both clear (80), weather only, air only, and both active. For a controlled integration test, set weather to 60 and air to 70 and assert a final 60. Verify incomplete status on source failure and no model call on the clear-weather path. Cover CSV header detection, unit conversion, the ambiguous sensor mapping, time alignment, zero-event hours, and model save/reload. Aim for the architecture exercise's five meaningful cases per component. Keep automated tests runnable offline.

**Deliver and run** a README with copyable Windows commands to set up a virtual environment, install the pinned dependencies, download/start the local model, prepare data, train, evaluate Year N+1, run tests, and start the GUI. Expose these actions as a small CLI or scripts. Include a one-minute demo sequence the student can repeat: show the 80 baseline, lower light below 500, then select a fixture with a rising AQI forecast. Record the actual outputs. Run one live API + local LLM decision and one offline fixture + local LLM decision; identify any integration that the environment prevented you from verifying.

Return the model artifact, cleaning counts, evaluation metrics, year-over-year assessment, test results, and a short example decision trace. Keep the implemented policy and LLM prompt in the project so the student can explain and reproduce a decision. These outputs are the evidence for the student's own diagrams and slides.

## Course references

Use PDF viewer page numbers. The case study V220, pp. 3, 5–11 supplies the governing rules and data definitions. Pages 16–19 cover preparation, implementation, and retraining assessment. The Introduction deck, p. 23 defines the MVP and GUI. Architectural Quality, p. 19 covers the full system. Architecture of Machine Learning-Powered Applications, pp. 28, 42, and 76 covers features, cleaning, and the weather subsystem. The Importance of Testing, pp. 25 and 38 defines the weather and LLM test exercises.
