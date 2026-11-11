import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_config(path=None):
    config = json.loads(Path(path or ROOT / "config.json").read_text(encoding="utf-8"))
    if config["combination"] != "minimum" or config["unavailable_behavior"] != "incomplete":
        raise ValueError("Only minimum combination and incomplete failure behavior are implemented")
    if config["model_target"] != "next_hour_near_accident_count":
        raise ValueError("This model predicts next-hour near-accident counts")
    if config["base_speed"] != 80 or config["speed_levels"] != [40, 50, 60, 70, 80]:
        raise ValueError("This baseline requires observed 40/50/60/70/80 speed levels")
    if config["max_carry_hours"] <= 0 or config["forecast_hours"] < 1:
        raise ValueError("Carry age and forecast horizon must be positive")
    return config


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
