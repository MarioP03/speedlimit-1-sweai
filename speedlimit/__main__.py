import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import ROOT, load_config, write_json
from .data import prepare, read_prepared
from .weather import assess, load_model, train


def main():
    parser = argparse.ArgumentParser(description="SpeedLimit local student project")
    parser.add_argument("--config", type=Path, default=ROOT / "config.json")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "train", "evaluate", "build"):
        command = sub.add_parser(name)
        command.add_argument("--data-dir", type=Path, default=ROOT)
        command.add_argument("--out", type=Path, default=ROOT / "results")
        command.add_argument("--temperature-ids", type=int, nargs="+", help="Explicit inventory T sensor IDs")
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--out", type=Path, default=ROOT / "results")
    demo = sub.add_parser("demo", help="Real Ollama inference; never uses scripted replies")
    demo.add_argument("--source", choices=["offline", "live"], default="offline")
    demo.add_argument("--out", type=Path, default=ROOT / "results")
    smoke = sub.add_parser("smoke", help="Five real local-model policy cases; requires Ollama, no internet")
    smoke.add_argument("--out", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    config = load_config(args.config)
    if args.command == "smoke":
        from .air import LocalAirModel, parse_readings, utc
        model = LocalAirModel(config)
        checks = []
        cases = [("clear", [20, 20, 20, 20], 0), ("boundary_60", [60, 30, 40, 20], 0),
                 ("boundary_80", [30, 80, 40, 20], 10), ("boundary_100", [30, 40, 100, 20], 20),
                 ("clean_now_high_forecast", [30, 65, 90, 110], 30)]
        for name, values, expected in cases:
            payload = json.loads((ROOT / "fixtures/clear.json").read_text())
            payload["current"]["european_aqi"] = values[0]
            payload["hourly"]["european_aqi"] = [*values, 0]
            readings = parse_readings(payload, utc(payload["decision_time"]), config["forecast_hours"])
            result = model.decide(readings)
            passed = result["status"] == "valid" and result["reduction_kmh"] == expected
            checks.append({"case": name, "expected_reduction_kmh": expected, "passed": passed,
                           "readings": readings, "result": result})
            print(json.dumps({"case": name, "passed": passed, "result": result}), flush=True)
        write_json(args.out / "local_model_smoke.json", {"checked_utc": datetime.now(timezone.utc).isoformat(),
                   "real_inference": True, "all_passed": all(c["passed"] for c in checks), "checks": checks})
        return 0 if all(c["passed"] for c in checks) else 1
    if args.command == "doctor":
        import requests
        from .air import OLLAMA_URL
        report = {"model_artifact": (args.out / "weather_model.joblib").exists(), "required_model": config["ollama_model"]}
        try:
            response = requests.get(OLLAMA_URL + "/api/tags", timeout=5)
            response.raise_for_status()
            report["installed_models"] = [m["name"] for m in response.json()["models"]]
            report["ollama_ready"] = config["ollama_model"] in report["installed_models"]
        except (requests.RequestException, ValueError, KeyError) as error:
            report.update(ollama_ready=False, error=str(error))
        print(json.dumps(report, indent=2))
        return 0 if report["ollama_ready"] and report["model_artifact"] else 1
    if args.command == "demo":
        from .air import AirSource, LocalAirModel
        from .decision import decide
        bundle = load_model(args.out / "weather_model.joblib")
        source, model = AirSource(config), LocalAirModel(config)
        cases = [("live", "live", 1000, 0, 10)] if args.source == "live" else [
            ("baseline", "clear", 1000, 0, 10), ("weather_only", "clear", 499, 0, 10),
            ("air_only", "rising", 1000, 0, 10), ("both", "rising", 499, 0, 10)]
        traces = []
        for name, mode, light, water, temperature in cases:
            trace = decide(bundle, source, model, mode, datetime.now(timezone.utc),
                           {"light_millilux": light, "water_um": water, "temperature_c": temperature})
            traces.append({"case": name, **trace})
            print(json.dumps(traces[-1], indent=2))
        write_json(args.out / f"demo_{args.source}.json", traces)
        return 0 if all(t["status"] == "complete" for t in traces) else 1
    if args.temperature_ids:
        config["temperature_ids"] = args.temperature_ids
    if args.command in ("prepare", "build"):
        frames, cleaning = prepare(args.data_dir, args.out, config)
        print(json.dumps({label: {"usable_hours": int(frame.usable.sum())} for label, frame in frames.items()}, indent=2))
    else:
        saved_config = json.loads((args.out / "preparation_config.json").read_text())
        if saved_config != config:
            parser.error("Configuration changed since preparation; rerun prepare/build")
        frames = {label: read_prepared(args.out / f"hourly_{label}.csv")
                  for label in ("N", "NPlus1")}
        cleaning = json.loads((args.out / "cleaning_summary.json").read_text())
    if args.command in ("train", "build"):
        bundle, metrics = train(frames["N"], args.out, config)
        print(json.dumps(metrics, indent=2))
    if args.command in ("evaluate", "build"):
        bundle = load_model(args.out / "weather_model.joblib")
        if bundle["data_config"] != config:
            parser.error("Model configuration differs from prepared data")
        metrics = json.loads((args.out / "training_metrics.json").read_text())
        assessment = assess(bundle, frames["NPlus1"], cleaning, metrics, args.out)
        print(json.dumps({"assessment": assessment["verdict"], "rationale": assessment["rationale"],
                          "evaluation": assessment["evaluation"]}, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
