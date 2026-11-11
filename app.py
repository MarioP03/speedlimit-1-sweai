"""One-screen production GUI. Run with python -m streamlit run app.py."""
import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from speedlimit.air import AirSource, LocalAirModel
from speedlimit.config import ROOT, load_config
from speedlimit.decision import decide
from speedlimit.weather import load_model

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--config", type=Path, default=ROOT / "config.json")
parser.add_argument("--model", type=Path, default=ROOT / "results/weather_model.joblib")
args, _ = parser.parse_known_args()
config = load_config(args.config)

st.set_page_config(page_title="SpeedLimit", page_icon="🚦", layout="wide")
st.title("SpeedLimit")
st.caption("Local student prototype · 80 km/h base limit · simulated road sensors")


@st.cache_resource
def saved_model(path, modified):
    return load_model(path)


bundle = None
model_warning = None
try:
    bundle = saved_model(str(args.model), args.model.stat().st_mtime_ns)
except Exception as error:
    model_warning = f"Weather model unavailable: {error}. Run python -m speedlimit build --data-dir ."

if "source" not in st.session_state or st.session_state.get("config") != config:
    st.session_state.update(source=AirSource(config), air_model=LocalAirModel(config), config=config,
                            history=[], running=False, busy=False, next_due=0., last_complete=None)

if model_warning:
    st.warning(model_warning)

a, b, c = st.columns(3)
a.number_input("Light (millilux)", min_value=0., max_value=1_000_000_000., value=1000., step=1., key="light")
b.number_input("Road water (µm)", min_value=0., max_value=10000., value=0., step=.1, key="water")
c.number_input("Temperature (°C)", min_value=-30., max_value=70., value=10., step=.1, key="temperature")
left, right = st.columns([2, 1])
left.selectbox("Air source", options=["live", "clear", "rising"],
               format_func=lambda s: {"live": f"Live · {config['location_name']}",
                                      "clear": "Offline · saved clear readings",
                                      "rising": "Offline · saved rising forecast"}[s], key="mode")
right.number_input("Tick interval (seconds)", min_value=5, max_value=3600, value=config["tick_seconds"], step=5, key="interval")
st.caption("Offline fixtures keep their saved UTC clock and still call real local qwen2.5:1.5b. "
           "Start runs a decision immediately, then at the chosen interval while this page is open.")


@st.fragment(run_every="1s")
def panel():
    first, second, third, fourth = st.columns([1, 1, 1, 3])
    manual = first.button("Decide now", type="primary", disabled=st.session_state.busy)
    if second.button("Start", disabled=st.session_state.running):
        st.session_state.running = True
        st.session_state.next_due = 0.
    if third.button("Stop", disabled=not st.session_state.running):
        st.session_state.running = False
    fourth.write("Running" if st.session_state.running else "Stopped")
    due = st.session_state.running and time.monotonic() >= st.session_state.next_due
    if (manual or due) and not st.session_state.busy:
        st.session_state.busy = True
        try:
            snapshot = datetime.now(timezone.utc)
            sensors = {"light_millilux": st.session_state.light, "water_um": st.session_state.water,
                       "temperature_c": st.session_state.temperature}
            with st.spinner("Reading air quality and asking local Ollama…"):
                result = decide(bundle, st.session_state.source, st.session_state.air_model,
                                st.session_state.mode, snapshot, sensors)
            st.session_state.history = [result, *st.session_state.history][:20]
            if result["status"] == "complete":
                st.session_state.last_complete = result["snapshot_time"]
        finally:
            st.session_state.busy = False
            # Schedule from completion: a slow local model cannot create overlapping ticks.
            st.session_state.next_due = time.monotonic() + st.session_state.interval
    if not st.session_state.history:
        st.info("Ready. Choose Decide now or Start to obtain air quality and run a decision.")
        return
    result = st.session_state.history[0]
    if result["status"] == "complete":
        st.metric("Recommended speed limit", f"{result['limit']} km/h")
    else:
        st.error("Decision incomplete — no new final speed limit")
    st.caption(f"Snapshot (UTC): {result['snapshot_time']} · Last complete decision (UTC): "
               f"{st.session_state.last_complete or 'none'}")
    wcol, acol = st.columns(2)
    weather, air = result["weather"], result["air"]
    with wcol:
        st.subheader("Weather branch")
        st.write(f"{weather['status'].title()} · " + (f"{weather['limit']} km/h" if weather["limit"] is not None else "unavailable"))
        st.write(weather["reason"])
        if weather.get("model_called") and weather.get("predicted_count") is not None:
            st.write(f"Estimated near-accidents/hour at selected speed: {weather['predicted_count']:.3f}")
            st.caption(f"Training hours at this speed: {weather.get('training_hours_at_selected_speed', 0)}")
            if not weather.get("training_hours_at_selected_speed", 0):
                st.warning("No training hours at this speed; candidate estimate extrapolates beyond observed support -> The model is predicting a situation it did not learn from directly.")
        if weather.get("target_unmet"):
            st.warning("Target unmet: no candidate has estimated count ≤1/hour")
        st.caption("Router: light < 500 OR (water > 1000 AND temperature < 0). "
                   "Neural network is called only on a trigger. Estimates do not establish real-world safety.")
    with acol:
        st.subheader("Air branch")
        st.write(f"{air['status'].title()} · " + (f"{air['limit']} km/h" if air["limit"] is not None else "unavailable"))
        st.write(air["reason"])
        if "model_reason" in air:
            st.caption("Policy explanation from validated fields; original model wording is in decision evidence.")
        st.caption(f"Local model: {air.get('model', config['ollama_model'])} · Response: {air['ollama_status']}")
        if "readings" in air:
            readings = air["readings"]
            st.caption(readings["source"] + " · " + readings["location"])
            st.caption("European AQI (dimensionless) · all timestamps UTC")
            st.dataframe([{"period": "current", **readings["current"]},
                          *[{"period": "forecast", **row} for row in readings["forecast"]]], hide_index=True)
    st.caption("Data: Open-Meteo Air Quality API and CAMS ENSEMBLE. Classroom AQI-to-speed mapping is a student assumption.")
    st.markdown("[Open-Meteo](https://open-meteo.com/en/docs/air-quality-api) · "
                "[CAMS ENSEMBLE](https://atmosphere.copernicus.eu/)")
    with st.expander("Decision evidence and local model response"):
        st.json(result)
    st.subheader("Recent decisions")
    st.dataframe([{"time (UTC)": r["snapshot_time"], "status": r["status"], "final km/h": r["limit"],
                   "weather km/h": r["weather"]["limit"], "air km/h": r["air"]["limit"],
                   "air response": r["air"]["ollama_status"]} for r in st.session_state.history], hide_index=True)


panel()
