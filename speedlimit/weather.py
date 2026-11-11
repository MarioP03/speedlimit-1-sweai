"""A small observational neural network, not a causal safety guarantee."""
import platform
import warnings
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import mean_absolute_error
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import write_json
from .data import FEATURES, UNITS


def triggered(light_millilux, water_um, temperature_c):
    return light_millilux < 500 or (water_um > 1000 and temperature_c < 0)


def metric(frame, predictions, baseline):
    if frame.empty:
        return {"n": 0, "mae": None, "baseline_mae": None,
                "mean_observed": None, "mean_predicted": None}
    y = frame.near_count.to_numpy()
    return {"n": len(frame), "mae": float(mean_absolute_error(y, predictions)),
            "baseline_mae": float(mean_absolute_error(y, np.full(len(y), baseline))),
            "mean_observed": float(y.mean()), "mean_predicted": float(np.mean(predictions))}


def evaluate_frame(bundle, frame):
    predictions = np.maximum(0, bundle["pipeline"].predict(frame[FEATURES])) if len(frame) else np.array([])
    subset = frame.weather_trigger.to_numpy(dtype=bool)
    return {"all": metric(frame, predictions, bundle["training_mean"]),
            "weather_triggered": metric(frame.loc[subset], predictions[subset], bundle["training_mean"]),
            "speed_counts": {str(int(k)): int(v) for k, v in frame.speed_kmh.value_counts().sort_index().items()}}


def train(hourly, out, config):
    frame = hourly.loc[hourly.usable].sort_index()
    if len(frame) < 30:
        raise ValueError(f"Only {len(frame)} usable hours; require at least 30 to split")
    i, j = int(len(frame) * .7), int(len(frame) * .85)
    partitions = {"train": frame.iloc[:i], "validation": frame.iloc[i:j], "test": frame.iloc[j:]}
    pipeline = Pipeline([("scale", StandardScaler()),
                         ("network", MLPRegressor(hidden_layer_sizes=(16,), solver="lbfgs", alpha=1.,
                                                  max_iter=2000, random_state=config["seed"]))])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        pipeline.fit(partitions["train"][FEATURES], partitions["train"].near_count)
    bundle = {
        "pipeline": pipeline, "feature_order": FEATURES, "units": UNITS,
        "target": config["model_target"], "seed": config["seed"],
        "training_mean": float(partitions["train"].near_count.mean()),
        "training_speed_counts": {str(int(k)): int(v) for k, v in partitions["train"].speed_kmh.value_counts().items()},
        "created_utc": datetime.now(timezone.utc).isoformat(), "data_config": config,
        "dependencies": {package: version(package) for package in ("numpy", "pandas", "scikit-learn", "joblib")},
        "python": platform.python_version(),
        "partition_ranges": {name: {"start": str(part.index.min()), "end": str(part.index.max()), "n": len(part)}
                             for name, part in partitions.items()},
    }
    metrics = {name: evaluate_frame(bundle, part) for name, part in partitions.items()}
    metrics["fit_warnings"] = [{"category": w.category.__name__, "message": str(w.message)} for w in caught]
    metrics["design"] = {"hidden_units": 16, "solver": "lbfgs", "alpha": 1., "seed": config["seed"],
                         "split": "chronological 70/15/15; no model selection on test or NPlus1",
                         "negative_predictions": "clamped to zero"}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, out / "weather_model.joblib")
    write_json(out / "training_metrics.json", metrics)
    write_json(out / "model_metadata.json", {k: v for k, v in bundle.items() if k != "pipeline"})
    for name, part in partitions.items():
        predictions = part[["year_label", *FEATURES, "near_count", "weather_trigger"]].copy()
        predictions["predicted_count"] = np.maximum(0, pipeline.predict(part[FEATURES]))
        predictions.to_csv(out / f"predictions_{name}.csv")
    return bundle, metrics


def load_model(path):
    # Only load artifacts created by this project; joblib/pickle is executable data.
    bundle = joblib.load(path)
    if bundle["feature_order"] != FEATURES or bundle["units"] != UNITS:
        raise ValueError("Model feature schema or units mismatch")
    return bundle


def weather_decision(bundle, light_millilux, water_um, temperature_c):
    values = [light_millilux, water_um, temperature_c]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(v) for v in values):
        return {"status": "unavailable", "limit": None, "reason": "Unusable sensor inputs", "model_called": False}
    if not (0 <= light_millilux <= 1_000_000_000 and 0 <= water_um <= 10000 and -30 <= temperature_c <= 70):
        return {"status": "unavailable", "limit": None, "reason": "Sensor outside course range", "model_called": False}
    route = bool(triggered(*values))
    if not route:
        return {"status": "valid", "limit": 80, "triggered": False, "model_called": False,
                "reason": "Weather router clear", "predicted_count": None, "target_unmet": False}
    if bundle is None:
        return {"status": "unavailable", "limit": None, "triggered": True,
                "reason": "Weather model unavailable; run training", "model_called": False}
    candidates = [70, 60, 50, 40]
    rows = pd.DataFrame([[*values, speed] for speed in candidates], columns=FEATURES)
    try:
        predictions = np.maximum(0, bundle["pipeline"].predict(rows))
        if not np.isfinite(predictions).all():
            raise ValueError("Nonfinite weather predictions")
    except (ValueError, RuntimeError) as error:
        return {"status": "unavailable", "limit": None, "triggered": True,
                "reason": str(error), "model_called": True}
    chosen = next((i for i, estimate in enumerate(predictions) if estimate <= 1), 3)
    estimate = float(predictions[chosen])
    support = bundle.get("training_speed_counts", {}).get(str(candidates[chosen]), 0)
    return {"status": "valid", "limit": candidates[chosen], "triggered": True, "model_called": True,
            "predicted_count": estimate, "target_unmet": estimate > 1,
            "candidate_estimates": {str(speed): float(p) for speed, p in zip(candidates, predictions)},
            "training_hours_at_selected_speed": support,
            "reason": ("Target unmet; lowest candidate" if estimate > 1 else "Highest reduced candidate with estimate <= 1/hour")
                      + "; observational estimate, not a safety guarantee"}


def assess(bundle, hourly, cleaning, training_metrics, out):
    frame = hourly.loc[hourly.usable].sort_index()
    evaluation = evaluate_frame(bundle, frame)
    reference = training_metrics["test"]["all"]
    n, error = evaluation["all"]["n"], evaluation["all"]["mae"]
    threshold = max(reference["mae"] * 1.25, reference["mae"] + .2)
    if n < 100:
        verdict, rationale = "insufficient evidence", "Fewer than 100 usable following-year hours"
    elif error > threshold:
        verdict, rationale = "recommend retraining", "Following-year MAE exceeds max(1.25 * test MAE, test MAE + 0.2)"
    elif cleaning["cross_year"]["readings_identical_after_header_normalization"]:
        verdict, rationale = "insufficient evidence", "Sensor inputs repeat Year N exactly; no independent evidence for retention"
    else:
        verdict, rationale = "retain", "At least 100 hours and no material MAE deterioration by the stated heuristic"
    report = {
        "verdict": verdict, "rationale": rationale, "evaluation": evaluation,
        "year_N_test_reference": reference, "mae_deterioration_threshold": threshold,
        "year_N_coverage": cleaning["N"], "year_NPlus1_coverage": cleaning["NPlus1"],
        "feature_means_NPlus1": frame[FEATURES].mean().to_dict(),
        "feature_means_N": cleaning["N"]["usable_feature_means"],
        "coverage_comparison": {label: {
            "covered_hours": cleaning[label]["actions"]["covered_grid_hours"]["count"],
            "usable_hours": cleaning[label]["actions"]["usable_target_hours"]["count"],
            "missing_fraction": cleaning[label]["feature_missing_fraction"],
        } for label in ("N", "NPlus1")},
        "cautions": ["Small reduced-speed support; counterfactual candidates are weakly supported",
                     "Calendar years are synthetic labels", "Hour-24 encoding remains unresolved",
                     "Retraining cannot fix missing causal evidence or ambiguous event encoding"],
        "frozen_model_preserved": True,
    }
    write_json(Path(out) / "year_NPlus1_assessment.json", report)
    predicted = frame.copy()
    predicted["predicted_count"] = np.maximum(0, bundle["pipeline"].predict(frame[FEATURES])) if len(frame) else []
    predicted.to_csv(Path(out) / "predictions_NPlus1.csv")
    return report
