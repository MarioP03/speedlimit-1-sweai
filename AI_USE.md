# AI use record

Development date: November 11, 2026. The student writes their own reflection,
diagrams, and slides. This records actual work, not a suggested course reflection.

## Significant coding request

The user asked: “Build the SpeedLimit student project in this folder. Read
`SpeedLimit-Agent-Brief.md` first and use it as the implementation brief.” They
specified inspection of six CSVs, local/free Windows operation, qwen2.5:1.5b,
automatic air fetching/prompting, sensor pipeline, neural-network evaluation, GUI,
offline real-model demo, staged tests, and a continuously updated README for the
student and professor. The full technical requirements remain in the supplied
brief. No other coding-model or subagent prompts were issued. Code and tests were
written by the coding assistant during this session.

## Significant implementation revisions

| Revision | Evidence and resulting change |
|---|---|
| Inspect first | Found duplicated T, unknown inventory 19, missing IDs, headerless N+1, repeated cross-year readings, and invalid hour 24; chose explicit ID mapping and quarantines |
| Runnable pipeline | Added audit counts/checksums, past-only carry/median, complete-log assumption, zero targets, and constant-speed hours; initial nine tests passed |
| Weather model | Fixed scaled 16-unit MLP and chronological splits; tested real predict call routing, training-only scaling, save/reload, and candidate scoring |
| Independent air branch | Added free API validation/cache, local structured output, policy validation, same-parser offline fixtures, and unavailable statuses |
| Production GUI | Serialized timestamped ticks, explicit branch reasons, history, last-complete status; tests cover redraws, Start/Stop, due ticks, and failure |
| Audit count correction | Unknown boundary speed in first hour is not an observed speed change; corrected count to 329, usable row count unchanged |
| Sparse support | No training hours at 40 after exclusions; added a visible unsupported-extrapolation warning alongside target unmet |
| Stage reproducibility | Running prepare/train separately exposed tiny default CSV float-parsing differences that changed fitted weights; added exact round-trip parsing and an artifact equivalence test |
| README readability | User requested B2-level English and clearer startup steps. Rewrote the README around setup and everyday use, kept key design/results, and moved detailed checks into docs/technical-notes.md |

## Actual local-model prompt revisions

Real model: **qwen2.5:1.5b**, Q4_K_M, through local Ollama. Automated tests inject
test doubles; real integration traces are separate evidence.

| Template / experiment | Observed output and revision |
|---|---|
| air_v1.txt | Full policy/schema; peak 45 returned reduction 30, rejected. Rising fixture worked. Saved integration_attempt_prompt_v1.json |
| air_v2.txt | Ordered rules/examples, controlling fields first; model selected current 30 instead of forecast peak. Saved integration_attempt_prompt_v2.json |
| air_v3.txt | Supplied verified maximum, leaving band selection to model; peak 45 returned 20. Saved integration_attempt_prompt_v3.json |
| Four few-shot examples | Policy-derived examples did not resolve wrong amounts. Inputs in air_examples_v1.json, outputs in integration_attempt_few_shot.json |
| Numeric diagnostic | scripts/probe_ollama.py: single simple rule worked; model put 45 in 60–80 and 110 in 80–100 with four rules. Real outputs/metadata in ollama_prompt_probe.json |
| air_v4.txt | Checked band A–D plus all thresholds; clear wrong, rising correct. Saved integration_attempt_prompt_v4.json |
| air_v5.txt, enum grammar | Symbolic lookup table still produced wrong clear amount. Saved integration_attempt_prompt_v5_enum.json |
| air_v5.txt, reason-first integer grammar | Removing the numeric enum did not fix clear selection. Saved integration_attempt_prompt_v5_integer.json |
| air_v6.txt | Application selects applicable rule from the versioned policy; local model chooses/explains reduction from that rule. Latest real outcomes are in demo_offline.json and demo_live.json |
| Validated explanation | All five real structured boundary cases passed, but prose sometimes misstated ranges or ignored the one-sentence instruction. GUI now derives its sentence from validated fields, preserving untouched model_reason and raw_response for inspection |

Peak and applicable-rule selection are deterministic application preprocessing.
This narrows the model's task and must not be presented as autonomous numerical
reasoning. Schema validity alone does not imply policy correctness. Every real
reply still passes the strict policy/evidence validator; a failed reply produces
unavailable rather than a substituted answer. The final prompt, schema, and raw
responses are inspectable in the project.

Final observed results: 64 automated tests passed; five real local-model policy
cases passed; offline four-case sequence returned 80/40/50/40; live API plus local
model returned 80. The running browser GUI visibly showed 80 and combined 40.
Remaining checks include long unattended operation, sleep/resume, alternate live
locations, and clarification of course-data timestamp/inventory semantics.
