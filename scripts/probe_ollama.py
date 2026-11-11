"""Development diagnostic: real requests, kept to document prompt experiments."""
import json
from pathlib import Path

import requests

cases = [
    ("simple_clear", "AQI is 45. The rule is: if AQI is at most 60, reduction_kmh is 0. What is reduction_kmh? Return JSON.",
     {"type": "object", "properties": {"reduction_kmh": {"type": "integer", "enum": [0, 10, 20, 30]}}, "required": ["reduction_kmh"]}),
    ("four_rules_clear", "AQI is 45. Rules: AQI <= 60 => reduction 0; 60 < AQI <= 80 => reduction 10; 80 < AQI <= 100 => reduction 20; AQI > 100 => reduction 30. Return JSON with your reason first, then reduction_kmh.",
     {"type": "object", "properties": {"reason": {"type": "string"}, "reduction_kmh": {"type": "integer", "enum": [0, 10, 20, 30]}}, "required": ["reason", "reduction_kmh"]}),
    ("four_rules_high", "AQI is 110. Rules: AQI <= 60 => reduction 0; 60 < AQI <= 80 => reduction 10; 80 < AQI <= 100 => reduction 20; AQI > 100 => reduction 30. Return JSON with your reason first, then reduction_kmh.",
     {"type": "object", "properties": {"reason": {"type": "string"}, "reduction_kmh": {"type": "integer", "enum": [0, 10, 20, 30]}}, "required": ["reason", "reduction_kmh"]}),
]
results = []
show = requests.post("http://127.0.0.1:11434/api/show", json={"model": "qwen2.5:1.5b"}, timeout=10)
show.raise_for_status()
details = show.json()
for name, prompt, schema in cases:
    response = requests.post("http://127.0.0.1:11434/api/chat", json={"model": "qwen2.5:1.5b",
                             "stream": False, "format": schema, "options": {"temperature": 0, "seed": 42, "num_ctx": 4096},
                             "messages": [{"role": "user", "content": prompt}]}, timeout=90)
    response.raise_for_status()
    result = {"case": name, "prompt": prompt, "schema": schema, "response": response.json()}
    results.append(result)
    print(name, result["response"]["message"]["content"], flush=True)
Path("results/ollama_prompt_probe.json").write_text(json.dumps({"model_details": details, "probes": results}, indent=2))
