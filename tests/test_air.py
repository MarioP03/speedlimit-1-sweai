import copy
import json
from unittest.mock import Mock

import pytest
import requests

from speedlimit.air import AirSource, AirUnavailable, LocalAirModel, load_policy, parse_readings, utc, validate_reply
from speedlimit.config import ROOT, load_config


@pytest.fixture
def payload():
    return json.loads((ROOT / "fixtures/clear.json").read_text())


def response_for(readings, reduction):
    peak = max([readings["current"], *readings["forecast"]], key=lambda row: row["aqi"])
    return json.dumps({"reduction_kmh": reduction, "controlling_aqi": peak["aqi"],
                       "controlling_time": peak["time"], "reason": f"Peak AQI {peak['aqi']} at {peak['time']}."})


@pytest.mark.parametrize("values,reduction", [([20, 20, 20, 20], 0), ([60, 60, 60, 60], 0),
                                             ([60, 80, 70, 70], 10), ([90, 100, 80, 70], 20),
                                             ([20, 30, 40, 110], 30), ([60.01, 0, 0, 0], 10)])
def test_policy_pairs_through_ollama_parser(payload, values, reduction):
    payload["current"]["european_aqi"] = values[0]
    payload["hourly"]["european_aqi"] = [values[0], *values[1:], 0]
    readings = parse_readings(payload, utc(payload["decision_time"]))
    reply = response_for(readings, reduction)
    post = Mock(return_value=Mock(json=lambda: {"message": {"content": reply}}))
    result = LocalAirModel(load_config(), post=post).decide(readings)
    assert result["status"] == "valid" and result["reduction_kmh"] == reduction
    assert result["limit"] == 80 - reduction and result["controlling_aqi"] == max(values)
    assert result["reason"] and result["controlling_time"]
    sent = post.call_args.kwargs["json"]
    assert sent["stream"] is False and sent["options"]["temperature"] == 0
    assert sent["format"]["type"] == "object"


@pytest.mark.parametrize("mutation", ["missing", "negative", "null", "duplicate", "unpaired", "stale", "unit"])
def test_bad_readings(payload, mutation):
    if mutation == "missing":
        del payload["hourly"]["time"][2]
        del payload["hourly"]["european_aqi"][2]
    elif mutation == "negative":
        payload["hourly"]["european_aqi"][2] = -1
    elif mutation == "null":
        payload["hourly"]["european_aqi"][2] = None
    elif mutation == "duplicate":
        payload["hourly"]["time"][2] = payload["hourly"]["time"][1]
    elif mutation == "unpaired":
        payload["hourly"]["european_aqi"].pop()
    elif mutation == "stale":
        payload["current"]["time"] = "2026-11-11T10:00"
    else:
        payload["current_units"]["european_aqi"] = "USAQI"
    with pytest.raises(AirUnavailable):
        parse_readings(payload, utc(payload["decision_time"]))


def test_forecast_strictly_after_boundary(payload):
    readings = parse_readings(payload, utc("2026-11-11T12:00:00Z"))
    assert readings["forecast"][0]["time"] == "2026-11-11T13:00:00+00:00"


@pytest.mark.parametrize("content", ["not JSON", "{}", "[]", '{"reduction_kmh":10}', "null"])
def test_bad_model_response_unavailable(payload, content):
    post = Mock(return_value=Mock(json=lambda: {"message": {"content": content}}))
    readings = parse_readings(payload, utc(payload["decision_time"]))
    assert LocalAirModel(load_config(), post=post).decide(readings)["status"] == "unavailable"


def test_policy_inconsistent_and_wrong_evidence(payload):
    readings = parse_readings(payload, utc(payload["decision_time"]))
    for change in ({"reduction_kmh": 10}, {"controlling_aqi": 0}, {"controlling_time": "wrong"},
                   {"reason": ""}, {"reduction_kmh": False}):
        reply = json.loads(response_for(readings, 0))
        reply.update(change)
        with pytest.raises(AirUnavailable):
            validate_reply(json.dumps(reply), readings, load_policy(load_config()))


def test_api_cache_expiration_and_timeout(payload):
    get = Mock(return_value=Mock(json=lambda: payload))
    clock = Mock(return_value=0)
    source = AirSource(load_config(), get=get, clock=clock)
    now = utc(payload["decision_time"])
    assert not source.live(now)["api_cache_hit"]
    clock.return_value = 899
    assert source.live(now)["api_cache_hit"] and get.call_count == 1
    clock.return_value = 900
    get.side_effect = requests.Timeout("test timeout")
    with pytest.raises(AirUnavailable, match="no fresh cache"):
        source.live(now)
    assert get.call_count == 2


def test_ollama_timeout_missing_model_and_cache(payload):
    readings = parse_readings(payload, utc(payload["decision_time"]))
    post = Mock(return_value=Mock(json=lambda: {"message": {"content": response_for(readings, 0)}}))
    model = LocalAirModel(load_config(), post=post)
    assert model.decide(readings)["ollama_status"] == "inferred"
    assert model.decide(copy.deepcopy(readings))["ollama_status"] == "cached_validated"
    assert post.call_count == 1
    for error in (requests.Timeout("timeout"), requests.HTTPError("404 model missing")):
        post.side_effect = error
        assert LocalAirModel(load_config(), post=post).decide(readings)["status"] == "unavailable"


def test_cache_is_per_location(payload):
    get = Mock(return_value=Mock(json=lambda: payload))
    source = AirSource(load_config(), get=get)
    source.live(utc(payload["decision_time"]))
    source.config = {**source.config, "latitude": 47.5}
    source.live(utc(payload["decision_time"]))
    assert get.call_count == 2


def test_young_cache_with_stale_current_reading_refreshes(payload):
    fresh = copy.deepcopy(payload)
    fresh["current"]["time"] = "2026-11-11T13:00"
    get = Mock(side_effect=[Mock(json=lambda: payload), Mock(json=lambda: fresh)])
    clock = Mock(return_value=0)
    source = AirSource(load_config(), get=get, clock=clock)
    source.live(utc("2026-11-11T12:59Z"))
    clock.return_value = 120
    result = source.live(utc("2026-11-11T13:01Z"))
    assert get.call_count == 2 and not result["api_cache_hit"]
    assert result["current"]["time"] == "2026-11-11T13:00:00+00:00"


def test_explanation_uses_verified_fields_and_retains_model_narrative(payload):
    readings = parse_readings(payload, utc(payload["decision_time"]))
    reply = json.loads(response_for(readings, 0))
    reply["reason"] = "Unreliable free prose with an incorrect pollution claim."
    post = Mock(return_value=Mock(json=lambda: {"message": {"content": json.dumps(reply)}}))
    result = LocalAirModel(load_config(), post=post).decide(readings)
    assert result["status"] == "valid"
    assert "forecast" in result["reason"] and "45" in result["reason"]
    assert readings["forecast"][-1]["time"] in result["reason"]
    assert result["model_reason"] == reply["reason"]
    assert "incorrect pollution" not in result["reason"]
