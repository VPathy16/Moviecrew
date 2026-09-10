# MovieCrew for Blender

Block a shot from the MovieCrew pipeline and render it as a numbered take.

The pipeline writes `project.json` — scenes, shots, and the cinematographer's
`camera_move` / `lens` / `framing`. This add-on picks a scene and shot out of
it, blocks the camera, and renders the result into a takes tree that the
MovieCrew portal reads.

## Install

Requires **Blender 4.2 or newer** (this is an extension, not a legacy add-on).

1. Build the extension. Blender's own builder is preferred — it validates the
   manifest and leaves build artefacts out:
   ```
   cd blender
   blender --command extension build --source-dir moviecrew_blender
   ```
   Without Blender on your `PATH`, zip it by hand — but **exclude
   `__pycache__`**. Running the test suite can compile `bridge.py` into the
   package, and that bytecode is built for your system Python, not the 3.11
   Blender ships:
   ```
   cd blender
   zip -r moviecrew.zip moviecrew_blender -x '*__pycache__*' '*.pyc'
   ```
2. In Blender: **Edit → Preferences → Add-ons → ▾ → Install from Disk**, pick
   the built zip, and enable **MovieCrew**.
3. In the add-on's preferences, set **MovieCrew Repository** to the folder
   containing the `moviecrew` package — this repo's root.

   Skip step 3 if MovieCrew is already installed into Blender's own Python
   (`pip install -e .` against Blender's interpreter); the add-on tries a
   plain import first.

**No wheels are bundled and none are needed.** MovieCrew's core is stdlib-only,
which is what lets this extension stay a few kilobytes of Python instead of
shipping per-platform binaries. Adding a third-party dependency to the core
would break that, so it's worth protecting.

## Use

The **floating bar** is the camera icon in the 3D viewport header — click it
for the popover. The same controls are docked in the sidebar under
<kbd>N</kbd> → **MovieCrew**.

1. **Load Project** — point at a `project.json`.
2. Pick **Scene** and **Shot**. The panel shows what the pipeline wrote for
   that shot: its move, lens, framing and duration.
3. Choose how the camera gets blocked:
   - **From Shot** — press *Auto-Block Shot* and the camera is keyed from the
     written cinematography.
   - **By Hand** — block it yourself; the take records that you did.
4. Set **Takes** to your takes root.
5. **Render Take** — renders the next take number as MP4 and writes its record.

Re-block and render again for take 2, take 3, and so on. Every take of a shot
lands side by side for the portal to compare.

## How auto-blocking works

`moviecrew/blocking.py` reads the shot's prose and computes camera geometry:

| Written | Becomes |
|---|---|
| `"24mm"` | 24mm focal length |
| `"wide, low angle"` | camera 9m back, 0.6m high |
| `"slow dolly-in"` | travels 35% closer, at 0.6× the normal distance |
| `"pan left"` | 20° yaw, camera stationary |
| `"zoom in"` | focal length climbs, camera stationary |

A dolly moves the camera; a zoom changes the lens — they're kept distinct.
Moves that travel (dolly, track, crane, orbit) re-aim at the subject as they
go; moves that redirect (pan, tilt) deliberately let it leave frame.

**Anything it can't parse is reported, not silently defaulted.** Auto-blocking
a shot whose move reads `"vertigo rack whip-snap"` warns that it fell back to
static. That warning is the signal to block it by hand.

What comes out is a *starting block*, not a finished shot — a sane camera that
honours what the pipeline wrote, which you then adjust.

## Why the logic lives outside the add-on

The parsing and geometry are in `moviecrew/blocking.py`, which never imports
`bpy`; the add-on's `bridge.py` only pushes computed numbers onto datablocks.
That's the same split `assembly.py` uses to test its ffmpeg invocation without
shelling out, and it means the fiddly parts have real test coverage
(`tests/test_blocking.py`, `tests/test_blender_bridge.py`) without needing
Blender in CI.
