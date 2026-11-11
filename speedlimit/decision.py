from .air import air_decision
from .weather import weather_decision


def combine(weather, air):
    complete = weather["status"] == "valid" and air["status"] == "valid"
    return {"status": "complete" if complete else "incomplete",
            "limit": min(weather["limit"], air["limit"]) if complete else None,
            "weather": weather, "air": air}


def decide(bundle, source, model, mode, now, sensors):
    # One timestamped snapshot; air runs independently even when weather is clear/unavailable.
    weather = weather_decision(bundle, **sensors)
    air = air_decision(source, model, mode, now)
    return {"snapshot_time": now.isoformat(), "sensors": dict(sensors), **combine(weather, air)}
