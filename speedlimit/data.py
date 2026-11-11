"""Read-only CSV ingestion, explicit provenance, and past-only hourly alignment.

Calendar years 2024/2025 are synthetic disjoint labels, not claimed recording years.
The event files have no minute field: Second is retained inside its recorded hour.
"""
import csv
import hashlib
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from .config import write_json

FILES = {
    "sensors": "Case_Study_Speed_Limit_Sensors_V100.csv",
    "types": "Case_Study_Speed_Limit_SensorTypes_V100.csv",
    "N_readings": "Case_Study_Speed_Limit_SensorReadingsYearN_V100.csv",
    "N_events": "Case_Study_Speed_Limit_AccidentsYearN_V100.csv",
    "NPlus1_readings": "Case_Study_Speed_Limit_SensorReadingsYearNPlus1_V100.csv",
    "NPlus1_events": "AccidentsYearNPlus1_V100.csv",
}
READING_COLUMNS = ["Month", "Day", "Hour", "Minute", "Second", "Sensor", "Value"]
EVENT_MEASUREMENTS = ["CloseCarCm", "CloseGuardrailCm", "SkidAngle"]
FEATURES = ["light_millilux", "water_um", "temperature_c", "speed_kmh"]
UNITS = ["millilux", "micrometers", "degrees Celsius", "km/h"]


def read_prepared(path):
    # Match in-memory build exactly; the default CSV float parser can round last bits
    # differently, which changes a nonlinear optimizer's path despite a fixed seed.
    return pd.read_csv(path, index_col="hour", parse_dates=True, float_precision="round_trip")


class Audit:
    def __init__(self):
        self.actions = {}

    def add(self, name, count=0, examples=()):
        # Callers pass only sensor/date/row-number metadata; never event identifiers.
        self.actions[name] = {"count": int(count), "examples": list(examples)[:5]}


def number(value):
    try:
        result = float(str(value).strip().replace(",", "."))
        return result if np.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def integer(value):
    n = number(value)
    return int(n) if n is not None and n.is_integer() else None


def read_readings(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream, delimiter=";"))
    has_header = bool(rows and [s.strip() for s in rows[0]] == READING_COLUMNS)
    records = rows[1:] if has_header else rows
    if any(len(row) != 7 for row in records):
        raise ValueError(f"Invalid reading column count in {Path(path).name}")
    result = pd.DataFrame(records, columns=READING_COLUMNS)
    # In particular, do not consume the headerless N+1 first record as a header.
    assert not records or result.iloc[0].tolist() == records[0]
    return result, has_header


def timestamp(row, year, event=False):
    fields = ["Month", "Day", "Hour", "Second"] if event else READING_COLUMNS[:5]
    values = {key: integer(row[key]) for key in fields}
    if any(value is None for value in values.values()):
        return pd.NaT
    try:
        return pd.Timestamp(year, values["Month"], values["Day"], values["Hour"],
                            0 if event else values["Minute"], values["Second"])
    except ValueError:
        return pd.NaT


def load_inventory(folder, temperature_ids, audit):
    inventory = pd.read_csv(folder / FILES["sensors"], sep=";")
    types = pd.read_csv(folder / FILES["types"], sep=";")
    inventory["SensorTypeCode"] = inventory.SensorTypeCode.str.strip()
    types["SensorTypeCode"] = types.SensorTypeCode.str.strip()
    if inventory.SensorID.duplicated().any():
        raise ValueError("Duplicate inventory IDs: cannot resolve safely")
    by_id = inventory.set_index("SensorID").SensorTypeCode.to_dict()
    for sid in temperature_ids:
        if sid not in by_id or by_id[sid] != "T":
            raise ValueError(f"Temperature override {sid} must be an inventory T sensor")
    ranges = {}
    for _, row in types.iterrows():
        # Resolve by semantic type, never join on duplicated T.
        ranges[row.Type.strip()] = (float(row.Min), float(row.Max))
    audit.add("duplicated_type_codes_resolved_without_join", types.SensorTypeCode.duplicated().sum(), ["T"])
    audit.add("provisional_temperature_ids", len(temperature_ids), temperature_ids)
    return by_id, ranges


def clean_readings(folder, label, config, audit):
    frame, header = read_readings(folder / FILES[f"{label}_readings"])
    audit.add("input_readings", len(frame))
    audit.add("header_present", int(header))
    audit.add("first_record_preserved", 1, [frame.iloc[0].tolist()])
    by_id, ranges = load_inventory(folder, config["temperature_ids"], audit)
    duplicated = frame.duplicated()
    audit.add("exact_reading_duplicates_removed", duplicated.sum())
    frame = frame.loc[~duplicated].copy()
    year = 2024 if label == "N" else 2025
    frame["time"] = frame.apply(lambda row: timestamp(row, year), axis=1)
    bad_dates = frame.time.isna()
    audit.add("invalid_reading_dates_excluded_no_supported_repair", bad_dates.sum(),
              frame.index[bad_dates].tolist())
    frame["sensor_id"] = frame.Sensor.map(integer)
    frame["value"] = frame.Value.map(number)
    bad_values = frame.sensor_id.isna() | frame.value.isna()
    audit.add("missing_or_invalid_reading_id_value", bad_values.sum(), frame.index[bad_values].tolist())
    frame = frame.loc[~bad_dates & ~bad_values].copy()
    observed = set(frame.sensor_id.astype(int))
    unknown = sorted(observed - set(by_id) - {-1})
    audit.add("unknown_inventory_readings_excluded", frame.sensor_id.isin(unknown).sum(), unknown)
    audit.add("inventory_ids_without_readings", len(set(by_id) - observed), sorted(set(by_id) - observed))
    ambiguous = [sid for sid, code in by_id.items() if code == "T" and sid not in config["temperature_ids"]]
    audit.add("ambiguous_T_readings_excluded_from_features", frame.sensor_id.isin(ambiguous).sum(), ambiguous)
    feature_map = {"L": ("light_millilux", "light", 1000), "W": ("water_um", "water", 1)}
    valid_rows = []
    out_of_range = []
    ignored = 0
    for row in frame.itertuples():
        sid = int(row.sensor_id)
        if sid == -1:
            feature, multiplier = "speed_kmh", 1
            valid = row.value in config["speed_levels"]
        elif sid in config["temperature_ids"]:
            feature, multiplier = "temperature_c", 1
            low, high = ranges["temperature"]
            valid = low <= row.value <= high
        elif by_id.get(sid) in feature_map:
            feature, semantic, multiplier = feature_map[by_id[sid]]
            low, high = ranges[semantic]
            valid = low <= row.value <= high
        else:
            # Range-check even unused unambiguous channels for the cleaning report.
            code = by_id.get(sid)
            semantics = {"N": "noise", "H": "humidity", "WS": "wind strength",
                         "WD": "wind direction", "AP": "air pressure"}
            if code in semantics:
                low, high = ranges[semantics[code]]
                if not low <= row.value <= high:
                    out_of_range.append({"row": int(row.Index), "sensor": sid, "value": row.value})
            ignored += 1
            continue
        if not valid:
            out_of_range.append({"row": int(row.Index), "sensor": sid, "value": row.value})
            continue
        valid_rows.append((row.time, sid, feature, row.value * multiplier))
    audit.add("outside_semantic_range_excluded", len(out_of_range), out_of_range)
    audit.add("unused_reading_channels", ignored)
    result = pd.DataFrame(valid_rows, columns=["time", "sensor_id", "feature", "value"])
    # Conflicting same-sensor timestamps are reduced by median, never duplicated by a join.
    conflicts = result.duplicated(["time", "sensor_id"], keep=False)
    audit.add("same_sensor_timestamp_collisions_median", conflicts.sum())
    result = result.groupby(["time", "sensor_id", "feature"], as_index=False).value.median()
    audit.add("feature_readings_after_cleaning", len(result))
    assert len(result) <= len(frame)
    return result.sort_values("time"), year


def clean_events(path, year, audit):
    # Discard LicencePlate at the CSV boundary, before any DataFrame or diagnostics.
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        rows = [{k: v for k, v in r.items() if k != "LicencePlate"}
                for r in csv.DictReader(stream, delimiter=";")]
    audit.add("input_events", len(rows))
    # Identical anonymous measurements can be different incidents: retain them.
    duplicate_count = sum(n - 1 for n in Counter(tuple(r.items()) for r in rows).values())
    audit.add("anonymous_event_collisions_retained", duplicate_count)
    near = []
    unknown_hours = set()
    invalid_dates = []
    unknown_kinds = []
    accidents = 0
    unknown_entire_period = False
    for index, row in enumerate(rows):
        time = timestamp(row, year, event=True)
        if pd.isna(time):
            invalid_dates.append({"row": index, **{k: row.get(k) for k in ("Month", "Day", "Hour", "Second")}})
            try:
                day = pd.Timestamp(year, integer(row["Month"]), integer(row["Day"]))
                if integer(row["Hour"]) == 24:
                    # Unsorted 1..24 data does not justify a date repair. Quarantine
                    # both plausible midnight interpretations, retaining 1..23 literally.
                    unknown_hours.update([day, day + pd.Timedelta(days=1)])
                else:
                    unknown_hours.update(pd.date_range(day, periods=24, freq="h"))
            except (ValueError, TypeError):
                unknown_entire_period = True
            continue
        values = [number(row.get(key)) for key in EVENT_MEASUREMENTS]
        valid_near = any(value is not None and value >= 0 for value in values)
        invalid_measurement = any(str(row.get(key, "")).strip() and
                                  (number(row.get(key)) is None or number(row.get(key)) < 0)
                                  for key in EVENT_MEASUREMENTS)
        if valid_near:
            near.append(time.floor("h"))  # one row = one near incident, even with multiple fields
        elif any(number(row.get(key)) is not None and number(row[key]) > 0
                 for key in ("Damage", "Injured")):
            accidents += 1
        else:
            unknown_hours.add(time.floor("h"))
            unknown_kinds.append(index)
        if invalid_measurement:
            unknown_hours.add(time.floor("h"))
    audit.add("invalid_event_dates_not_repaired", len(invalid_dates), invalid_dates)
    audit.add("event_rows_without_known_kind", len(unknown_kinds), unknown_kinds)
    audit.add("accident_only_rows_not_near_events", accidents)
    audit.add("qualifying_near_events", len(near))
    audit.add("unknown_event_hours", len(unknown_hours), [str(t) for t in sorted(unknown_hours)])
    counts = pd.Series(Counter(near), dtype="int64")
    return counts, unknown_hours, unknown_entire_period


def build_year(folder, label, config):
    folder = Path(folder)
    audit = Audit()
    readings, year = clean_readings(folder, label, config, audit)
    counts, unknown_hours, unknown_all = clean_events(folder / FILES[f"{label}_events"], year, audit)
    if readings.empty:
        raise ValueError("No usable sensor readings")
    start, end = readings.time.min().floor("h"), readings.time.max().floor("h")
    grid = pd.date_range(start, end, freq="h")
    hourly = pd.DataFrame(index=grid)
    hourly.index.name = "hour"
    max_age = pd.Timedelta(hours=config["max_carry_hours"])
    ages = []
    for feature in FEATURES:
        channels = []
        for sid, source in readings.loc[readings.feature == feature].groupby("sensor_id"):
            source = source.sort_values("time")
            aligned = pd.merge_asof(pd.DataFrame({"hour": grid}),
                                    source[["time", "value"]], left_on="hour", right_on="time",
                                    direction="backward", tolerance=max_age)
            age = (aligned.hour - aligned.time).dt.total_seconds() / 3600
            ages.extend(age.dropna().tolist())
            channels.append(aligned.value.rename(str(sid)))
        hourly[feature] = pd.concat(channels, axis=1).median(axis=1).to_numpy() if channels else np.nan
    # At least one raw reading in the target hour is required to establish coverage.
    covered = set(readings.time.dt.floor("h"))
    hourly["sensor_covered"] = hourly.index.isin(covered)
    hourly["event_covered"] = (config["assume_complete_event_log"] and not unknown_all)
    hourly.loc[hourly.index.isin(unknown_hours), "event_covered"] = False
    hourly["near_count"] = counts.reindex(grid, fill_value=0).astype(int)
    # Any differing speed after boundary and strictly before next boundary invalidates the target hour.
    speed = readings.loc[readings.feature == "speed_kmh"].copy()
    speed["hour"] = speed.time.dt.floor("h")
    speed = speed.join(hourly.speed_kmh, on="hour", rsuffix="_boundary")
    changed = speed.loc[speed.speed_kmh.notna() & (speed.time > speed.hour) & (speed.value != speed.speed_kmh), "hour"]
    hourly["speed_changed"] = hourly.index.isin(changed)
    hourly["usable"] = (hourly[FEATURES].notna().all(axis=1) & hourly.sensor_covered &
                         hourly.event_covered & ~hourly.speed_changed)
    hourly["weather_trigger"] = ((hourly.light_millilux < 500) |
                                  ((hourly.water_um > 1000) & (hourly.temperature_c < 0)))
    hourly["year_label"] = label
    audit.add("covered_grid_hours", len(grid))
    audit.add("hours_missing_boundary_features", hourly[FEATURES].isna().any(axis=1).sum())
    audit.add("hours_unknown_event_coverage", (~hourly.event_covered).sum())
    audit.add("hours_speed_changes_excluded", hourly.speed_changed.sum())
    audit.add("usable_target_hours", hourly.usable.sum())
    audit.add("usable_zero_event_hours", ((hourly.near_count == 0) & hourly.usable).sum())
    report = {
        "year_label": label,
        "calendar_label_only": year,
        "actions": audit.actions,
        "maximum_used_carry_age_hours": max(ages) if ages else None,
        "feature_missing_fraction": hourly[FEATURES].isna().mean().to_dict(),
        "usable_feature_means": hourly.loc[hourly.usable, FEATURES].mean().to_dict(),
        "raw_speed_counts": readings.loc[readings.feature == "speed_kmh", "value"].value_counts().sort_index().to_dict(),
        "usable_speed_counts": hourly.loc[hourly.usable, "speed_kmh"].value_counts().sort_index().to_dict(),
        "event_coverage_assumption": config["assume_complete_event_log"],
        "source_sha256": {role: hashlib.sha256((folder / filename).read_bytes()).hexdigest()
                          for role, filename in FILES.items() if role in ("sensors", "types", f"{label}_readings", f"{label}_events")},
    }
    return hourly, report


def prepare(folder, out, config):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    frames, reports = {}, {}
    for label in ("N", "NPlus1"):
        frames[label], reports[label] = build_year(folder, label, config)
        frames[label].to_csv(out / f"hourly_{label}.csv")
    a, _ = read_readings(Path(folder) / FILES["N_readings"])
    b, _ = read_readings(Path(folder) / FILES["NPlus1_readings"])
    reports["cross_year"] = {"readings_identical_after_header_normalization": a.equals(b),
                            "warning": "Repeated sensor features limit independence of Year N+1 assessment"}
    write_json(out / "cleaning_summary.json", reports)
    write_json(out / "preparation_config.json", config)
    return frames, reports
