from unittest.mock import Mock

import numpy as np
import pytest

from speedlimit.air import AirUnavailable, utc
from speedlimit.decision import combine, decide


@pytest.mark.parametrize("weather,air,expected", [(80, 80, 80), (60, 80, 60), (80, 70, 70), (60, 70, 60)])
def test_both_branches_minimum(weather, air, expected):
    result = combine({"status": "valid", "limit": weather}, {"status": "valid", "limit": air})
    assert result["status"] == "complete" and result["limit"] == expected


@pytest.mark.parametrize("failed", ["weather", "air", "both"])
def test_incomplete_never_fresh_default(failed):
    weather = {"status": "unavailable" if failed in ("weather", "both") else "valid", "limit": 60}
    air = {"status": "unavailable" if failed in ("air", "both") else "valid", "limit": 70}
    result = combine(weather, air)
    assert result["status"] == "incomplete" and result["limit"] is None


def test_air_independent_no_weather_model_call():
    network = Mock()
    source, model = Mock(), Mock()
    model.decide.return_value = {"status": "valid", "limit": 70}
    result = decide({"pipeline": network}, source, model, "live", utc("2026-11-11T12:15Z"),
                    {"light_millilux": 1000, "water_um": 0, "temperature_c": 10})
    assert result["limit"] == 70 and network.predict.call_count == 0
    assert source.live.call_count == model.decide.call_count == 1


def test_source_failure_keeps_weather_branch():
    network = Mock()
    network.predict.return_value = np.array([2, .8, .5, .3])
    source, model = Mock(), Mock()
    source.live.side_effect = AirUnavailable("API timeout")
    result = decide({"pipeline": network}, source, model, "live", utc("2026-11-11T12:15Z"),
                    {"light_millilux": 499, "water_um": 0, "temperature_c": 10})
    assert result["status"] == "incomplete" and result["limit"] is None
    assert result["weather"]["limit"] == 60 and model.decide.call_count == 0
