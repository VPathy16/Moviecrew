# MovieCrew

A model-agnostic multi-agent pipeline that turns a concept into a shot-by-shot
Veo prompt pipeline.

## Status

The pipeline runs end to end: the seven agents, the CLI, the storyboard gate,
the Blender previz add-on, the render abstraction, and the portal that ties
them together. What remains is per-shot staging of actors (see `Roadmap`).

## The arc

1. **Plan** — a concept goes through the seven agents and comes out as a
   `Project`: bible, scenes, shots, and a `RenderPlan` of prompts.
2. **Storyboard** — one still per shot for review; approving promotes each
   anchored frame into that shot's reference images.
3. **Previz** — the Blender add-on blocks a camera from the shot's prose and
   renders a take. Every shot can have as many takes as you like.
4. **Generate** — pick a take in the portal, pick a model, and the take is
   sent as the driving reference for a generative render.
5. **Review** — finished renders are downloaded into the takes tree and shown
   in the portal beside the take that drove them, playable and downloadable.

## Portal

```bash
pip install -e ".[portal]"
MOVIECREW_TAKES_ROOT=./takes python -m uvicorn moviecrew.portal.app:app --reload
```

Then open http://127.0.0.1:8000.

| variable | what it does |
| --- | --- |
| `MOVIECREW_TAKES_ROOT` | where Blender writes takes and renders are stored. Server-side only — a browser cannot redirect it. |
| `OPENROUTER_API_KEY` | opts into real generation. Without it the portal uses `FakeRenderClient` and spends nothing. |
| `MOVIECREW_PUBLIC_BASE_URL` | an address a provider can fetch takes from. Required for models that drive motion from a video, because a provider cannot reach your loopback address. |

Renders land in `<takes root>/<scene>/<shot>/renders/<job id>.mp4`. They are
downloaded rather than linked: a provider URL expires, and the render cost
real money.

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
