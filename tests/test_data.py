import csv
from pathlib import Path

import pandas as pd
import pytest

from speedlimit.config import ROOT, load_config
from speedlimit.data import Audit, FEATURES, FILES, build_year, clean_events, clean_readings, read_readings, read_prepared


def write_readings(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["Month", "Day", "Hour", "Minute", "Second", "Sensor", "Value"])
        writer.writerows(rows)


@pytest.fixture
def course():
    if not all((ROOT / name).exists() for name in FILES.values()):
        pytest.skip("Course data not present")
    return ROOT


@pytest.mark.parametrize("label,header", [("N", True), ("NPlus1", False)])
def test_header_and_first_record(course, label, header):
    frame, found = read_readings(course / FILES[f"{label}_readings"])
    assert found == header
    assert len(frame) == 12648
    assert frame.iloc[0].tolist() == ["1", "1", "0", "3", "35", "6", "0,00"]


def test_mapping_conversion_no_row_multiplication(course):
    audit = Audit()
    raw, _ = clean_readings(course, "N", load_config(), audit)
    assert len(raw) == 744 * 9  # speed, three light, three water, two temperature
    assert set(raw.loc[raw.feature == "temperature_c", "sensor_id"]) == {15, 18}
    frame, _ = read_readings(course / FILES["N_readings"])
    expected = float(frame.loc[frame.Sensor == "2", "Value"].iloc[0].replace(",", ".")) * 1000
    assert raw.loc[raw.sensor_id == 2].iloc[0].value == expected
    assert audit.actions["unknown_inventory_readings_excluded"]["count"] == 744


def test_hourly_past_only_speed_changes_zero_events(course):
    hourly, report = build_year(course, "N", load_config())
    assert len(hourly) == 744
    assert not hourly.iloc[0].usable
    assert hourly.loc[hourly.usable, FEATURES].notna().all().all()
    assert ((hourly.near_count == 0) & hourly.usable).any()
    assert not hourly.loc[hourly.speed_changed, "usable"].any()
    assert 0 < report["maximum_used_carry_age_hours"] <= 2


def test_unknown_event_coverage_excludes_everything(course):
    config = load_config()
    config["assume_complete_event_log"] = False
    hourly, _ = build_year(course, "N", config)
    assert not hourly.usable.any()


def test_event_count_privacy_and_invalid_date(tmp_path):
    path = tmp_path / "events.csv"
    path.write_text("Month;Day;Hour;Second;LicencePlate;Damage;Injured;CloseCarCm;CloseGuardrailCm;SkidAngle\n"
                    "1;1;1;0;PRIVATE;0;0;5;10;20\n"
                    "1;1;2;0;PRIVATE;1;0;;;\n"
                    "1;1;24;0;PRIVATE;;;3;;\n"
                    "1;1;3;0;PRIVATE;;;;;\n")
    audit = Audit()
    counts, unknown, all_unknown = clean_events(path, 2024, audit)
    assert counts.sum() == 1
    assert pd.Timestamp("2024-01-01 00:00") in unknown
    assert pd.Timestamp("2024-01-02 00:00") in unknown
    assert pd.Timestamp("2024-01-01 03:00") in unknown
    assert not all_unknown
    assert "PRIVATE" not in str(audit.actions) and "LicencePlate" not in str(audit.actions)


def test_invalid_override(course):
    config = load_config()
    config["temperature_ids"] = [19]
    with pytest.raises(ValueError, match="inventory"):
        clean_readings(course, "N", config, Audit())


def test_prepared_artifact_exact_float_round_trip(tmp_path, course):
    hourly, _ = build_year(course, "N", load_config())
    artifact = tmp_path / "prepared.csv"
    hourly.to_csv(artifact)
    loaded = read_prepared(artifact)
    pd.testing.assert_frame_equal(hourly, loaded, check_freq=False)


def test_bounded_forward_fill_and_no_future_leakage(tmp_path, course):
    for role in ("sensors", "types"):
        (tmp_path / FILES[role]).write_bytes((course / FILES[role]).read_bytes())
    rows = [[1, 1, h, 10, 0, sid, value] for h in (0, 3) for sid, value in
            [(-1, "80"), (1, "100,25"), (2, "0,4"), (15, "-1,25")]]
    write_readings(tmp_path / FILES["N_readings"], rows)
    (tmp_path / FILES["N_events"]).write_text(
        "Month;Day;Hour;Second;LicencePlate;Damage;Injured;CloseCarCm;CloseGuardrailCm;SkidAngle\n")
    hourly, _ = build_year(tmp_path, "N", load_config())
    assert hourly.iloc[0][FEATURES].isna().all()
    assert hourly.iloc[1].water_um == 100.25
    assert hourly.iloc[1].temperature_c == -1.25
    assert hourly.iloc[1].light_millilux == 400
    assert hourly.iloc[3][FEATURES].isna().all()  # 2h50 old, future 03:10 forbidden


def test_cleaning_duplicate_missing_range_date(tmp_path, course):
    for role in ("sensors", "types"):
        (tmp_path / FILES[role]).write_bytes((course / FILES[role]).read_bytes())
    rows = [[1, 1, 0, 0, 0, 15, "-2,125"], [1, 1, 0, 0, 0, 15, "-2,125"],
            [1, 1, 0, 0, 0, 1, "10001"], [1, 32, 0, 0, 0, 2, "2"],
            [1, 1, 0, 0, 0, 2, ""], [1, 1, 0, 0, 0, 19, "-2"]]
    write_readings(tmp_path / FILES["N_readings"], rows)
    audit = Audit()
    frame, _ = clean_readings(tmp_path, "N", load_config(), audit)
    assert len(frame) == 1 and frame.iloc[0].value == -2.125
    for action in ("exact_reading_duplicates_removed", "invalid_reading_dates_excluded_no_supported_repair",
                   "missing_or_invalid_reading_id_value", "outside_semantic_range_excluded"):
        assert audit.actions[action]["count"] == 1
