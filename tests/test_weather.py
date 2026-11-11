from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from speedlimit.config import load_config
from speedlimit.data import FEATURES
from speedlimit.weather import load_model, train, triggered, weather_decision


@pytest.mark.parametrize("light,water,temp,expected", [(499, 0, 10, True), (500, 1000, -1, False),
                                                     (500, 1001, -1, True), (500, 1001, 0, False)])
def test_router_and_actual_network_invocation(light, water, temp, expected):
    network = Mock()
    network.predict.return_value = np.array([2, .8, .5, .3])
    assert triggered(light, water, temp) == expected
    result = weather_decision({"pipeline": network}, light, water, temp)
    assert result["triggered"] == expected
    assert result["model_called"] == expected
    assert network.predict.call_count == int(expected)


@pytest.mark.parametrize("scores,limit,unmet", [([.5, .4, .3, .2], 70, False),
                                              ([2, 1, .5, .4], 60, False),
                                              ([2, 2, 2, 2], 40, True),
                                              ([-1, -1, -1, -1], 70, False)])
def test_candidate_selection(scores, limit, unmet):
    network = Mock()
    network.predict.return_value = np.array(scores)
    result = weather_decision({"pipeline": network}, 499, 0, 10)
    assert result["limit"] == limit and result["target_unmet"] == unmet
    assert result["predicted_count"] >= 0
    assert network.predict.call_args.args[0].speed_kmh.tolist() == [70, 60, 50, 40]


def test_missing_model_and_bad_sensor():
    assert weather_decision(None, 499, 0, 10)["status"] == "unavailable"
    assert weather_decision(None, 500, 0, -10)["limit"] == 80
    for values in [(float("nan"), 0, 10), (1000, -1, 10), (1000, 0, -31)]:
        assert weather_decision(None, *values)["status"] == "unavailable"


def test_model_save_reload_and_training_only_preprocessing(tmp_path):
    n = 50
    frame = pd.DataFrame({"light_millilux": np.arange(n) * 100, "water_um": np.arange(n),
                          "temperature_c": np.arange(n) / 10, "speed_kmh": [80] * n,
                          "near_count": np.arange(n) % 3, "weather_trigger": np.arange(n) < 5,
                          "usable": True, "year_label": "N"}, index=pd.date_range("2024-01-01", periods=n, freq="h"))
    bundle, metrics = train(frame, tmp_path, load_config())
    reloaded = load_model(tmp_path / "weather_model.joblib")
    np.testing.assert_allclose(bundle["pipeline"].predict(frame[FEATURES]), reloaded["pipeline"].predict(frame[FEATURES]))
    np.testing.assert_allclose(bundle["pipeline"]["scale"].mean_, frame.iloc[:35][FEATURES].mean())
    assert metrics["train"]["all"]["n"] == 35
    assert metrics["validation"]["all"]["n"] == 7
    assert metrics["test"]["all"]["n"] == 8
