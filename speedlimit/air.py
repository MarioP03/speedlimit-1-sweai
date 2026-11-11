import hashlib
import json
import math
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from string import Template

import requests

from .config import ROOT

API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
OLLAMA_URL = "http://127.0.0.1:11434"
SCHEMA = {
    "type": "object",
    "properties": {
        "reason": {"type": "string", "minLength": 1},
        "controlling_aqi": {"type": "number", "minimum": 0},
        "controlling_time": {"type": "string"},
        "reduction_kmh": {"type": "integer", "minimum": 0, "maximum": 30},
    },
    "required": ["reduction_kmh", "controlling_aqi", "controlling_time", "reason"],
    "additionalProperties": False,
}


class AirUnavailable(ValueError):
    pass


def utc(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime):
        raise AirUnavailable("Invalid timestamp")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)  # Open-Meteo requested timezone=GMT
    return value.astimezone(timezone.utc)


def aqi(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise AirUnavailable("AQI must be finite and nonnegative")
    return float(value)


def parse_readings(payload, decision_time, horizon=3):
    now = utc(decision_time)
    try:
        if horizon < 1 or horizon > 24:
            raise AirUnavailable("Forecast horizon must be 1..24 hours")
        for key in ("current_units", "hourly_units"):
            if payload[key]["european_aqi"] != "EAQI":
                raise AirUnavailable("Expected European AQI units (EAQI)")
        current_time = utc(payload["current"]["time"])
        if not timedelta(0) <= now - current_time <= timedelta(hours=1):
            raise AirUnavailable("Current AQI is stale or in the future")
        current = {"time": current_time.isoformat(), "aqi": aqi(payload["current"]["european_aqi"])}
        times, values = payload["hourly"]["time"], payload["hourly"]["european_aqi"]
        if len(times) != len(values):
            raise AirUnavailable("Unpaired hourly timestamps and values")
        parsed = [utc(value) for value in times]
        if parsed != sorted(set(parsed)):
            raise AirUnavailable("Hourly times must be unique and chronological")
        paired = dict(zip(parsed, values))
        first_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        forecast = []
        for offset in range(horizon):
            stamp = first_hour + timedelta(hours=offset)
            if stamp not in paired:
                raise AirUnavailable("Missing complete forecast hour")
            forecast.append({"time": stamp.isoformat(), "aqi": aqi(paired[stamp])})
        return {"unit": "European AQI (dimensionless)", "current": current, "forecast": forecast,
                "effective_decision_time": now.isoformat()}
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise AirUnavailable(str(error)) from error


class AirSource:
    def __init__(self, config, get=None, clock=None):
        self.config = config
        self.get = get or requests.get
        self.clock = clock or time.monotonic
        self.cache = {}

    def live(self, now):
        key = (self.config["latitude"], self.config["longitude"])
        cached = self.cache.get(key)
        hit = cached is not None and self.clock() - cached[0] < self.config["api_cache_seconds"]
        if hit:
            payload = cached[1]
        else:
            try:
                response = self.get(API_URL, params={"latitude": key[0], "longitude": key[1],
                                    "current": "european_aqi", "hourly": "european_aqi",
                                    "timezone": "GMT", "forecast_days": 2},
                                    timeout=self.config["api_timeout_seconds"])
                response.raise_for_status()
                payload = response.json()
            except (requests.RequestException, ValueError) as error:
                raise AirUnavailable(f"Open-Meteo refresh failed; no fresh cache: {error}") from error
        try:
            readings = parse_readings(payload, now, self.config["forecast_hours"])
        except AirUnavailable:
            if hit:
                # Even a young cache can cross a current-reading freshness boundary.
                del self.cache[key]
                return self.live(now)
            raise
        if not hit:
            self.cache[key] = (self.clock(), payload)
        readings.update(source="live Open-Meteo / CAMS ENSEMBLE", api_cache_hit=hit,
                        location=self.config["location_name"], latitude=key[0], longitude=key[1])
        return readings

    def fixture(self, name):
        if name not in ("clear", "rising"):
            raise AirUnavailable("Unknown fixture")
        payload = json.loads((ROOT / "fixtures" / f"{name}.json").read_text())
        readings = parse_readings(payload, utc(payload["decision_time"]), self.config["forecast_hours"])
        readings.update(source=payload["label"], api_cache_hit=False, location="Classroom fixture; saved clock")
        return readings


def load_policy(config):
    return json.loads((ROOT / config["air_policy"]).read_text(encoding="utf-8"))


def expected_reduction(peak, policy):
    peak = aqi(peak)
    for band in policy["bands"]:
        if band["upper_inclusive"] is None or peak <= band["upper_inclusive"]:
            return band["reduction_kmh"]
    raise AirUnavailable("Policy has no matching band")


def peak_band_code(peak, policy):
    for index, band in enumerate(policy["bands"]):
        if band["upper_inclusive"] is None or peak <= band["upper_inclusive"]:
            return chr(ord("A") + index)
    raise AirUnavailable("No matching band")


def prompt_for(readings, policy):
    lines = []
    lower = 0
    for index, band in enumerate(policy["bands"]):
        upper, reduction = band["upper_inclusive"], band["reduction_kmh"]
        label = f"0 through {upper}" if lower == 0 else (f"above {lower} through {upper}" if upper is not None else f"above {lower}")
        lines.append(f"Band {chr(ord('A') + index)}: peak {label} -> reduction_kmh = {reduction}")
        lower = upper
    template = Template((ROOT / "speedlimit/prompts/air_v6.txt").read_text(encoding="utf-8"))
    peak = max([readings["current"], *readings["forecast"]], key=lambda row: row["aqi"])
    period = "current" if peak == readings["current"] else "forecast"
    return template.substitute(unit=policy["unit"], policy_version=policy["version"], bands="\n".join(lines),
                               lookup="\n".join(f"{chr(ord('A') + i)} -> {b['reduction_kmh']}" for i, b in enumerate(policy["bands"])),
                               readings=json.dumps({"current": readings["current"], "forecast": readings["forecast"]}),
                               schema=json.dumps(SCHEMA), peak_aqi=peak["aqi"], peak_time=peak["time"], peak_period=period,
                               peak_band=peak_band_code(peak["aqi"], policy),
                               selected_rule=lines[ord(peak_band_code(peak["aqi"], policy)) - ord("A")])


def validate_reply(content, readings, policy):
    reply = json.loads(content)
    if not isinstance(reply, dict) or set(reply) != set(SCHEMA["required"]):
        raise AirUnavailable("Unexpected JSON response fields")
    reduction = reply["reduction_kmh"]
    allowed = [band["reduction_kmh"] for band in policy["bands"]]
    if type(reduction) is not int or reduction not in allowed:
        raise AirUnavailable("Reduction must be an allowed integer")
    all_values = [readings["current"], *readings["forecast"]]
    peak = max(row["aqi"] for row in all_values)
    if reduction != expected_reduction(peak, policy):
        raise AirUnavailable("Local model response is inconsistent with classroom policy")
    if aqi(reply["controlling_aqi"]) != peak or reply["controlling_time"] not in {
            row["time"] for row in all_values if row["aqi"] == peak}:
        raise AirUnavailable("Incorrect controlling AQI or timestamp")
    if not isinstance(reply["reason"], str) or not reply["reason"].strip() or len(reply["reason"]) > 1000:
        raise AirUnavailable("Missing or excessive explanation")
    return reply


def messages_for(readings, policy):
    return [{"role": "user", "content": prompt_for(readings, policy)}]


class LocalAirModel:
    def __init__(self, config, post=None):
        self.config = config
        self.post = post or requests.post
        self.policy = load_policy(config)
        self.cache = {}

    def decide(self, readings):
        messages = messages_for(readings, self.policy)
        key = hashlib.sha256((self.config["ollama_model"] + json.dumps(self.policy, sort_keys=True) + json.dumps(messages)).encode()).hexdigest()
        if key in self.cache:
            return {**self.cache[key], "ollama_status": "cached_validated"}
        content = None
        try:
            response = self.post(OLLAMA_URL + "/api/chat", json={
                "model": self.config["ollama_model"], "stream": False, "format": SCHEMA,
                "options": {"temperature": 0, "seed": self.config["seed"], "num_predict": 256, "num_ctx": 4096},
                "messages": messages},
                timeout=(3, self.config["ollama_timeout_seconds"]))
            response.raise_for_status()
            body = response.json()
            content = body["message"]["content"]
            reply = validate_reply(content, readings, self.policy)
            period = "current" if reply["controlling_time"] == readings["current"]["time"] else "forecast"
            # Keep the untouched model narrative, but display an auditable sentence.
            explanation = (f"Peak {period} European AQI {reply['controlling_aqi']:g} at "
                           f"{reply['controlling_time']} requires {reply['reduction_kmh']} km/h reduction.")
            result = {"status": "valid", "limit": self.config["base_speed"] - reply["reduction_kmh"],
                      **reply, "model_reason": reply["reason"], "reason": explanation,
                      "ollama_status": "inferred", "model": self.config["ollama_model"],
                      "policy_version": self.policy["version"], "prompt_version": "air_v6",
                      "request_hash": key, "raw_response": content}
            if len(self.cache) >= 128:
                self.cache.pop(next(iter(self.cache)))
            self.cache[key] = result
            return result
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            return {"status": "unavailable", "limit": None, "reason": f"Local Ollama decision unavailable: {error}",
                    "ollama_status": "unavailable", "model": self.config["ollama_model"], "raw_response": content}


def air_decision(source, model, mode, now):
    try:
        readings = source.live(now) if mode == "live" else source.fixture(mode)
        return {**model.decide(readings), "readings": readings}
    except (AirUnavailable, OSError, ValueError) as error:
        return {"status": "unavailable", "limit": None, "reason": str(error),
                "ollama_status": "not_called_source_unavailable"}
