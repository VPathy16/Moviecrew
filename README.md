<p align="center">
  <img src="moviecrew/portal/static/moviecrew-mark.svg" width="72" height="72" alt="MovieCrew logo">
</p>

# MovieCrew

**A story. An entire crew.**

MovieCrew is a model-agnostic filmmaking workspace that brings a director, writer,
production designer, cinematographer, editor, prompt artist, and continuity reviewer
into one workflow. Develop a concept, establish your cast and world, generate shots,
and assemble the results into a film.

The website uses a compact charcoal-and-coral interface with visual references,
model controls, saved versions, and a timeline editor. Blender previz remains an
optional production path; it is not required for the main website workflow.

**Current status:** a working local, single-user application. Shared accounts,
workspace permissions, cloud persistence migration, and billing are planned work—not
shipped SaaS features. Track delivery in the
[production roadmap](https://github.com/VPathy16/Moviecrew/issues/32).

## Open the website

Start the server using the instructions below, then open:

| Address | Purpose |
| --- | --- |
| [MovieCrew home](http://127.0.0.1:8000/) | Start a film, browse saved films, and enter the unified workspace |
| [Studio](http://127.0.0.1:8000/studio) | Alternate entry point to the same website |
| [Legacy portal](http://127.0.0.1:8000/legacy) | Earlier production and Blender-take tools |

These are local addresses, not a hosted public service. If you start on port `8001`,
use [http://127.0.0.1:8001](http://127.0.0.1:8001/) instead. No public production
website is currently configured in this repository.

## The filmmaking workflow

```mermaid
flowchart LR
    A[Concept and brief] --> B[Your crew]
    B --> C[Cast and world]
    C --> D[Approve reference sheets]
    D --> E[Storyboard images]
    E --> F[Shots and video]
    F --> G[Review takes]
    G --> H[Final edit]
    H --> I[Export film]
    G --> F
```

### 1. Start with a concept

Describe the story on the home screen. Set the creative brief, including genre,
language, intended duration, and film references. The crew develops the story and
production plan, with progress shown while planning runs in the background.

### 2. Bring in the crew

**Your crew** brings the creative outputs together:

- **Director:** the film's vision and story direction.
- **Writer:** scenes and story development.
- **Production designer:** characters, locations, and props.
- **Cinematographer:** shots, framing, and camera direction.
- **Editor:** proposed ordering and grouping of shots.
- **Prompt artist:** generation prompts for individual shots.
- **Continuity:** checks across the written plan and prompts.

These are AI-assisted proposals for review. The current continuity pass checks text;
it does not certify the consistency of generated video. Better sequencing context
and footage evaluation are active roadmap items.

### 3. Establish the cast and world

Create and review character, environment, and asset sheets before generating shots.
Character creation supports **face → full body → accessories → costume**, with
reference images and editable descriptions.

Approve the sheets and apply their versions to the shots. Image generation binds
approved references rather than silently using unapproved drafts. The current image
workflow accepts up to four reference images; an oversized set is rejected before
generation so you can choose a smaller set.

### 4. Create the storyboard

Generate still images for the shots using the available image models. Review the
images, edit prompts, regenerate, and choose the version you want to use. Model,
aspect ratio, quality, and other supported controls are available through compact
selectors; available settings depend on the selected model and endpoint.

### 5. Generate and review video

In **Shots & video**, choose the shot, prompt, model, duration, ratio, resolution,
and supported audio/reference options. Review the estimate when available, then
explicitly start generation.

Use a shot image as the visual starting point, or choose character-reference mode
where supported. These are distinct input modes; attaching an image is not a
guarantee that the model will preserve its appearance or perform the intended action.
Generated clips remain available for preview and selection before entering the edit.

### 6. Edit the film on a visual timeline

In **Final edit**:

- Drag clip edges to trim and drag clips to reorder.
- Scrub the playhead and change timeline zoom.
- Right-click a clip or select **⋯** for trim, split, mute, move, remove, extension,
  and enhancement actions.
- Open **Trim…** for precise in/out values; use Undo for changes in the current session.
- Use **+** to insert a library video, upload media, or generate from an image.
- Save the edit and preview the sequence before exporting.

**Extend before** generates a prequel using the trimmed opening frame as an ending
constraint. **Extend after** generates a sequel using the final visible frame of the
trimmed clip as its starting constraint. Only models advertising the required frame
position are offered. These operations use a boundary still, not the full motion
history; separate character sheets are not attached in this mode. Review the result
before inserting it.

### 7. Choose the canvas and export

Choose landscape **16:9**, portrait **9:16**, or square **1:1**, then:

| Operation | Result |
| --- | --- |
| Fit | Preserve the picture and add black bars where needed |
| Crop | Fill the canvas by cropping the edges |
| AI expand | Generate surrounding content as a new candidate version |
| Upscale · Topaz | Enhance and increase dimensions through the optional fal integration |
| Export size | Resize the assembled film to 720p, 1080p, or 4K |

A 4K export setting is ordinary resizing; it does not mean native 4K generation or
Topaz enhancement. The browser may buffer between preview clips; exporting creates
the assembled video file.

See the [editor guide](docs/editor.md) for extension behavior, enhancement limits,
audio preservation, and recovery details.

## Run locally

### Requirements

- Python **3.10 or newer**; CI covers 3.10, 3.11, and 3.12.
- **FFmpeg and ffprobe** on your PATH for video processing and export.
- A modern browser.

Install FFmpeg through your system's package manager, for example `brew install ffmpeg`
on macOS or `sudo apt-get install ffmpeg` on Debian/Ubuntu.

```bash
git clone https://github.com/VPathy16/Moviecrew.git
cd Moviecrew
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[portal,dev]"
python -m moviecrew.portal
```

On Windows, activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell.
The server binds to `127.0.0.1:8000`. To use another port:

```bash
PORT=8001 python -m moviecrew.portal
```

For development with automatic backend reload:

```bash
python -m uvicorn moviecrew.portal.app:app --host 127.0.0.1 --port 8000 --reload
```

### Try the offline workflow

Without configured provider credentials, the default planning backend is mock and
the application supports offline previews. Stub images and preview outputs are not
AI-generated footage. Saved settings can restore credentials at startup, so absence
of a key in the current shell alone does not establish offline mode.

For an isolated offline trial on macOS/Linux, use a fresh directory and remove
inherited provider keys:

```bash
trial_dir=$(mktemp -d)
env -u OPENROUTER_API_KEY -u ANTHROPIC_API_KEY -u FAL_KEY \
  MOVIECREW_SETTINGS_PATH="$trial_dir/settings.json" \
  MOVIECREW_PROJECTS_ROOT="$trial_dir/projects" \
  python -m moviecrew.portal
```

This trial uses temporary storage. Use the normal persistent defaults for films you
want to keep, and do not add live credentials to the offline trial.

### Connect live providers

Open **Settings** in the sidebar to configure OpenRouter and R2/S3 storage. Optional
fal credentials enable Topaz upscaling and AI canvas expansion. The fal integration
uses a fal API key, not a Topaz desktop licence.

Model availability and valid settings depend on the connected endpoint. Planning,
image generation, video generation, and enhancement can incur provider charges.
Review prompts, references, and estimates before starting paid work; some enhancement
operations do not provide an estimate.

## Storage and configuration

Settings are saved in an owner-readable/writable local file. Secret fields are
masked in responses. Settings currently apply to the whole installation.

| Variable | Purpose |
| --- | --- |
| `MOVIECREW_PROJECTS_ROOT` | Project database and new project directories; defaults to `~/.moviecrew/projects` |
| `MOVIECREW_SETTINGS_PATH` | Saved provider settings; defaults to `~/.moviecrew/settings.json` |
| `OPENROUTER_API_KEY` | OpenRouter-backed planning and image/video workflows |
| `ANTHROPIC_API_KEY` | Optional direct Anthropic planning backend; install `.[anthropic]` to use it |
| `FAL_KEY` | Optional Topaz and AI canvas-expansion integration |
| `MOVIECREW_S3_ENDPOINT` | R2/S3-compatible endpoint |
| `MOVIECREW_S3_BUCKET` | Media bucket name |
| `MOVIECREW_S3_ACCESS_KEY` | Storage access key |
| `MOVIECREW_S3_SECRET_KEY` | Storage secret key |
| `MOVIECREW_S3_REGION` | Storage region; use `auto` for R2 |
| `MOVIECREW_ASSET_BASE_URL` | Optional public asset base for workflows requiring it |
| `MOVIECREW_TAKES_ROOT` | Optional Blender-take directory; defaults to `./takes` |
| `MOVIECREW_PUBLIC_BASE_URL` | Provider-reachable portal address for legacy take delivery |
| `PORT` | Port for `python -m moviecrew.portal`; defaults to `8000` |

Projects, drafts, approved sheets, generations, and cuts have local persistence.
Some provider inputs are delivered through signed R2/S3 URLs. This does **not** mean
all project media has been migrated to cloud storage: saved records can still depend
on local files. Back up the database **and** its referenced media directories.

Keep credentials out of Git. The current portal has no multi-user authorization
boundary; run it locally until the SaaS access-control work is complete. A bucket
connection or a Firebase project alone does not make this deployment a secure shared
service.

## Optional Blender and CLI workflows

The Blender add-on can load a project, block camera/staging, and render previz takes.
The legacy portal lets you review those takes and submit compatible generative
renders using video references. Provider delivery must use a reachable media address;
loopback URLs cannot be fetched by a remote generation provider.

See [the Blender add-on](blender/moviecrew_blender/) and the earlier
[camera-transfer](docs/media/camera-transfer.gif) and
[staging-transfer](docs/media/staging-transfer.gif) experiments. These demonstrate
specific tested examples, not universal guarantees of action or camera transfer.

Generate a plan from the command line:

```bash
python -m moviecrew "A solo climber decides to turn back from Everest." \
  --backend mock --out project.json
```

For live planning, select `--backend openrouter` or `--backend anthropic` with the
appropriate credentials. Run `python -m moviecrew --help` for the full CLI options.

## Development

```bash
python -m pip install -e ".[dev,portal]"
python -m pytest
python -m pyflakes moviecrew tests
```

Include **both** the dev and portal extras: portal tests import FastAPI. FFmpeg-based
tests need FFmpeg/ffprobe. Tests use offline implementations and controlled provider
transports; they do not establish live-model quality or complete SaaS readiness.

The core Python package is dependency-light. The portal uses FastAPI/Uvicorn;
OpenRouter clients use standard-library HTTP transports. The website is served from
`moviecrew/portal/static/studio.html`, with timeline behavior in `editor.js`.

| Area | Source |
| --- | --- |
| Shared film schema | `moviecrew/schema.py` |
| Crew and planning | `moviecrew/agents.py`, `moviecrew/crew.py` |
| Local project persistence | `moviecrew/projects.py` |
| Settings and asset storage | `moviecrew/settings.py`, `moviecrew/assets.py` |
| Image generation and model controls | `moviecrew/image_studio.py`, `moviecrew/image_openrouter.py` |
| Video provider adapters | `moviecrew/render.py`, `moviecrew/render_openrouter.py` |
| Cast and world approval | `moviecrew/portal/world.py` |
| Video jobs, cuts and exports | `moviecrew/portal/film_workflow.py` |
| Extensions and enhancement | `moviecrew/portal/film_enhance.py` |
| Website and timeline | `moviecrew/portal/static/` |
| Optional previz | `blender/moviecrew_blender/`, `moviecrew/blocking.py` |

## What comes next

The [prioritized GitHub backlog](https://github.com/VPathy16/Moviecrew/issues/32)
contains implementation issues with dependencies and acceptance criteria:

- **P0:** backup/restore, sequence contracts, better Editor/Prompter context, identity,
  workspace permissions, durable media/jobs, spending controls, and launch gates.
- **P1:** model capabilities, role-aware references, input provenance, footage
  evaluation, revisioned timelines, playback, audio, and contextual UX.
- **P2:** targeted repairs, evaluated visual recipes, reusable workspace assets,
  production-validated enhancements, and a capped paid pilot.

Firebase Auth with PostgreSQL and private R2 is a proposed target architecture,
not a current runtime dependency. The
[architecture decision issue](https://github.com/VPathy16/Moviecrew/issues/37)
tracks that choice. See also the [brand guide](docs/brand.md) and
[longer-term production architecture](docs/ROADMAP.md).

### Review direction before writing

New films in the unified workspace pause after the Director proposal. Edit the title, logline and story beats, add character roles and motivations, and save or regenerate with feedback. Previous versions can be restored. **Approve & continue to Writer** passes the approved story and cast into writing, then pauses at the existing cast/world approval step.

Drafts and revision history persist in the local project store. Existing completed films keep their original workflow and media. A later direction edit on a reviewed project marks it as needing review; it does not automatically rewrite accepted scenes. Legacy API clients keep the one-pass flow unless they send `review_director: true` to `/api/plan`.
