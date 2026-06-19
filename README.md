# MovieCrew

A model-agnostic multi-agent pipeline that turns a concept into a shot-by-shot
Veo prompt pipeline.

## Status

This is the foundation layer: schema, LLM abstraction, and an offline mock
client. Agents, the orchestrator, the CLI, and the video backend are not
built yet (see later PRs).

## Layout

- `moviecrew/schema.py` — stdlib dataclasses for the pipeline's shared
  vocabulary: `Bible` (the consistency layer of locked characters,
  locations, style/palette/mood, and their reference images), `Scene`,
  `Shot`, `VeoPrompt`, `ContinuityFlag`, `RenderPlan`, and the top-level
  `Project`. Also defines Veo's legal clip constraints (4/6/8s durations,
  up to 3 reference images, 16:9 or 9:16) and `clamp_duration()`.
- `moviecrew/llm.py` — `LLMClient` abstract base (`complete_json`) plus
  `AnthropicLLMClient`, which lazily imports the `anthropic` package and
  routes each task to a model (director/continuity -> Opus,
  writer/designer/cinematographer/prompter -> Sonnet, editor -> Haiku).
- `moviecrew/mock.py` — `MockLLMClient`, a deterministic, offline,
  no-API-key implementation of `LLMClient` with canned but coherent JSON
  per task, so the schema can be exercised end to end without any network
  access.

## Development

```bash
pip install -e ".[dev]"
python -m pytest
```

No API key or network access is required to run the tests — they exercise
`MockLLMClient` only. Copy `.env.example` to `.env` and set
`ANTHROPIC_API_KEY` only if you want to use `AnthropicLLMClient`.
