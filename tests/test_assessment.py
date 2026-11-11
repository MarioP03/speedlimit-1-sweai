from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from speedlimit.data import FEATURES
from speedlimit.weather import assess


@pytest.mark.parametrize("n,repeated,prediction,expected", [
    (99, False, 1.2, "insufficient evidence"),
    (100, True, 1.2, "insufficient evidence"),
    (100, False, 1.2, "retain"),
    (100, False, 2., "recommend retraining"),
    (100, True, 2., "recommend retraining"),
])
def test_assessment_evidence_thresholds_and_frozen_artifact(tmp_path, n, repeated, prediction, expected):
    frame = pd.DataFrame({"light_millilux": 1000., "water_um": 0., "temperature_c": 10.,
                          "speed_kmh": 80., "near_count": 1, "weather_trigger": False,
                          "usable": True}, index=pd.date_range("2025-01-01", periods=n, freq="h"))
    network = Mock()
    network.predict.return_value = np.full(n, prediction)
    bundle = {"pipeline": network, "training_mean": 1.}
    report = {"actions": {"covered_grid_hours": {"count": n}, "usable_target_hours": {"count": n}},
              "feature_missing_fraction": dict.fromkeys(FEATURES, 0),
              "usable_feature_means": frame[FEATURES].mean().to_dict()}
    cleaning = {"N": report, "NPlus1": report,
                "cross_year": {"readings_identical_after_header_normalization": repeated}}
    artifact = tmp_path / "weather_model.joblib"
    artifact.write_bytes(b"frozen model must stay unchanged")
    result = assess(bundle, frame, cleaning, {"test": {"all": {"mae": .5}}}, tmp_path)
    assert result["verdict"] == expected
    assert artifact.read_bytes() == b"frozen model must stay unchanged"
    assert result["evaluation"]["all"]["n"] == n
