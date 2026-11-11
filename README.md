# SpeedLimit

SpeedLimit suggests a road speed limit using light, road water, temperature, and
air quality. It shows the limit and explains the decision.

This student project runs free on a laptop. It uses a small weather neural network,
Open-Meteo air data, and local **qwen2.5:1.5b** through Ollama. No paid account or
API key is needed.

## Start the project on Windows

Use **PowerShell**. You need **Python 3.13** and
[Ollama for Windows](https://ollama.com/download/windows).

### 1. Set up Python — first time only

Open PowerShell and run:

~~~powershell
Set-Location 'C:\Users\palag\Documents\Egyetem\msc_projects\speedlimit-1-sweai'
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
~~~

This creates a separate Python environment and installs the packages.
You do not need to activate it.

### 2. Set up the local language model — first time only

Open the Ollama desktop app, then run:

~~~powershell
ollama pull qwen2.5:1.5b
ollama list
~~~

The list should include **qwen2.5:1.5b**. The download is about 1 GB.
Internet is needed for installation and this first download.

If Ollama is not running, open another PowerShell window and run:

~~~powershell
ollama serve
~~~

Leave that window open. If it says the address is already in use, Ollama is
probably already running.

### 3. Prepare the data and train the weather model

The six course CSV files are already in the folder:

~~~powershell
.\.venv\Scripts\python.exe -m speedlimit build --data-dir .
~~~

This cleans the data, trains the model, and checks Year N+1. Output goes into
**results**. The original CSVs stay unchanged. Repeat after changing data or model settings.

### 4. Launch the app

~~~powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
~~~

Open [localhost:8501](http://localhost:8501). Keep PowerShell open while using the app.
Press **Ctrl+C** in PowerShell to stop the server.

**Next time:** open the project folder in PowerShell, make sure Ollama is running,
and use the launch command above. You do not need to install or train again.

If the app cannot find a model, check the setup:

~~~powershell
.\.venv\Scripts\python.exe -m speedlimit doctor
~~~

## Try the app

Enter light in **millilux**, road water in **µm**, and temperature in **°C**.
Choose **Live** air data or an **Offline** example.

- **Decide now** makes one decision.
- **Start** makes a decision now, then repeats it at the chosen interval.
- **Stop** stops future decisions. A request already running finishes first.

Keep the browser page open for repeated decisions. The default interval is 60 seconds.
Live air data needs internet. Offline examples use saved readings, but still call
the real local model, so Ollama must be running.

For a short demo, keep water at **0** and temperature at **10**:

| Step | Light | Air source | Recorded result |
|---|---:|---|---:|
| Clear conditions | 1000 | Offline: saved clear readings | 80 km/h |
| Dark road | 499 | Offline: saved clear readings | 40 km/h |
| Poor air forecast | 1000 | Offline: saved rising forecast | 50 km/h |
| Both problems | 499 | Offline: saved rising forecast | 40 km/h |

The dark-road examples also show **target unmet**: no tested speed reached the
model's target of at most one near-accident per hour.

## How a decision is made

The two branches work separately.

**Weather check.** The course rule runs the neural network only when:

- light is below **500 millilux**, **or**
- water is above **1000 µm** and temperature is below **0 °C**.

The comparisons are strict; cold alone is not enough. The model checks **70, 60,
50, and 40 km/h**. It chooses the highest speed with an estimated count of at most
one event per hour. If none qualifies, it chooses 40 with a warning.
Clear weather gives 80 without calling the model.

**Air-quality check.** AQI means **Air Quality Index**. A higher value means more
pollution. The app gets the current European AQI and the next three hourly forecasts.
It uses the highest value:

| Highest AQI | Air branch limit |
|---|---:|
| 0–60 | 80 km/h |
| Above 60, up to 80 | 70 km/h |
| Above 80, up to 100 | 60 km/h |
| Above 100 | 50 km/h |

This speed table is a **student assumption**, not an official traffic rule.

The app finds the highest AQI and matching rule, then asks local Ollama for a
reduction and explanation. It checks the reply before using it. The small model
needed this help because it made number-comparison errors. Original replies are saved.

**Final limit.** Use the lower limit from the two branches. Reductions are never
added together. If either required branch fails, show **decision incomplete** and
the last complete decision time. A failed request must not produce a new 80 km/h.

### One actual example

With light **499 millilux**, water **0 µm**, and temperature **10 °C**, weather chose
**40 km/h**. Its estimate was **2.332 near-accidents/hour**, so the target was unmet.
Saved current AQI was **30**, with forecasts **65, 90, 110**. Real qwen2.5:1.5b
returned a 30 km/h reduction for peak 110, giving air **50 km/h**.
Final: **40 km/h**, the lower of the two. Readings, times, and replies are in
[demo_offline.json](results/demo_offline.json).

## Main design choices

The basis column separates **course requirements**, **CSV findings**, and
**student choices**.

| Decision | Basis | Reason and trade-off | Where implemented or tested |
|---|---|---|---|
| Predict next-hour near-accidents using recorded speed | Student choice from brief; CSV has no ideal-speed labels | Compares speeds, but cannot prove a safety effect | [weather.py](speedlimit/weather.py), weather tests |
| Use temperature IDs 15 and 18 | CSV finding; temporary student choice | T also means traffic. Exclude unclear IDs and 19, which has no inventory entry | [data.py](speedlimit/data.py), data tests |
| Use past readings up to two hours old; take the median across sensors | Student choice | Handles gaps without future data; excludes hours with too little information | data.py, data tests |
| Map AQI to speed as shown above | Student choice | Easy to repeat; no real traffic-safety study supports it | [air_v1.json](speedlimit/policies/air_v1.json), air tests |
| Take the lower limit; show incomplete on failure | Student choice from brief | Avoids added reductions and false defaults | [decision.py](speedlimit/decision.py), GUI tests |
| Small neural network; split data in time order, 70/15/15% | Course: network; student choice: size and split | Fits a laptop; data preparation learns only from training data | weather.py, weather tests |
| Exclude hours with speed changes or unclear event times | CSV finding and student choice | Fewer training hours; hour 24 needs course clarification | data.py, cleaning report |
| Assume complete event logs except known problem hours | Student choice | Allows zero-event targets, but file coverage is not confirmed | [config.json](config.json), data tests |

Code is split into data cleaning, weather modeling, air/Ollama, and the
[GUI](app.py). [decision.py](speedlimit/decision.py) combines the branches.

Settings are in [config.json](config.json). The defaults are Vienna, three forecast
hours, and a 60-second update interval. Air readings are reused for up to 15 minutes
to avoid repeated API requests. Decisions do not overlap, and redrawing the screen
does not start a new request.

## Tests and results

Run the automated tests without internet:

~~~powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=results/pytest.xml
~~~

To check the real local model and repeat the demos:

~~~powershell
.\.venv\Scripts\python.exe -m speedlimit smoke
.\.venv\Scripts\python.exe -m speedlimit demo --source offline
.\.venv\Scripts\python.exe -m speedlimit demo --source live
~~~

Only the live demo needs internet. All three need Ollama. Automated tests use
prepared replies; smoke checks and demos use the **real local model**.

Checks recorded on November 11, 2026: **64 automated tests** and **five real-model
checks passed**, including AQI 60, 80, and 100. Offline results were **80 → 40 → 50 →
40**. Live API plus Ollama returned **80 km/h**. The running GUI was also checked.

The weather model had **405 usable Year N hours**. MAE means average prediction
error, in near-accidents per hour. Lower is better. The baseline always predicts
the training data's average count.

| Data | Hours | Neural network MAE | Simple baseline MAE |
|---|---:|---:|---:|
| Training | 283 | 0.902 | 0.993 |
| Validation | 61 | 1.190 | 1.104 |
| Test | 61 | 0.860 | 0.910 |
| Year N+1, using the unchanged model | 404 | 0.907 | 0.888 |

The improvement on the test set is small. The model was worse than the baseline
on validation and Year N+1.

**Year N+1: insufficient evidence for a retraining decision.** Its sensor readings
repeat Year N exactly, although events differ. The original model was kept for the demo.

Important limits:

- There are no usable training hours at 40 km/h. Predictions at this speed have
  weak support, and the GUI warns about this.
- Temperature IDs, hour-24 event records, and event-log coverage still need confirmation.
- Long unattended use, browser sleep/resume, and other live locations still need checks.
- **Estimated event rates do not prove real-world road safety.**

More data checks, full metrics, and the retraining rule are in the
[technical notes](docs/technical-notes.md).

<details>
<summary>Run preparation, training, and evaluation separately</summary>

Use these instead of the build command when working on one stage:

~~~powershell
.\.venv\Scripts\python.exe -m speedlimit prepare --data-dir .
.\.venv\Scripts\python.exe -m speedlimit train
.\.venv\Scripts\python.exe -m speedlimit evaluate
~~~

To use the original course folder:

~~~powershell
.\.venv\Scripts\python.exe -m speedlimit build --data-dir 'C:\Users\palag\Documents\Egyetem\IMC MSc AI\Software Engineering in AI'
~~~

</details>

## Where to find things

| File or folder | What it contains |
|---|---|
| [results/weather_model.joblib](results/weather_model.joblib) | Saved weather model and its data preparation |
| [results/cleaning_summary.json](results/cleaning_summary.json) | Data problems, excluded rows, and cleaning counts |
| [results/training_metrics.json](results/training_metrics.json) | Full training, validation, and test results |
| [results/year_NPlus1_assessment.json](results/year_NPlus1_assessment.json) | Year N+1 results and retraining assessment |
| [results/verification.json](results/verification.json) | Summary of tests and integration checks |
| [results/demo_offline.json](results/demo_offline.json), [demo_live.json](results/demo_live.json) | Saved decisions and original model replies |

## AI use and data sources

The exact local-model prompt is [air_v6.txt](speedlimit/prompts/air_v6.txt).
The app checks its JSON reply before using it. Invalid replies mean unavailable.
The displayed explanation uses checked values; original model wording is kept
in the evidence panel.

[AI_USE.md](AI_USE.md) records the development request and important code and prompt
revisions, including failed prompt attempts.

Air data comes from [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api) and
**CAMS ENSEMBLE** ([Copernicus Atmosphere Monitoring Service](https://atmosphere.copernicus.eu/)).
The API is used under its [free educational terms](https://open-meteo.com/en/terms).
