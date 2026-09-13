# Movie editor

The Final edit workspace previews the saved cut and supports trim in/out, split,
reorder, mute, removal and in-session undo. The + buttons insert library videos,
uploaded videos or new generations. Continue previous clip extracts its **trimmed**
last frame; selecting the next clip extracts its trimmed first frame. An image
chosen from the library or uploaded locally is copied into an owned starting-frame
version. The prompt stays editable in the existing generation workspace. A generated
candidate enters the cut only when the user chooses Add to edit.

Canvas settings persist with the cut: landscape, portrait or square; fit with black
bars or centre crop; export sizes 720p, 1080p and 4K. Export size is ordinary resizing,
not AI enhancement. The browser preview loads each clip sequentially and may briefly
buffer at a cut; export produces the continuous file.

## Optional AI processing

Set **FAL_KEY** using Settings → Generation, or the server environment. This is a
fal key, not an OpenRouter or Topaz desktop licence. Existing R2/S3 storage publishes
temporary provider inputs. Keys and signed input URLs stay on the server.

- AI expand: `fal-ai/luma-dream-machine/ray-2-flash/reframe`; selected ranges up to
  30 seconds / 100 MB. Target ratio follows the canvas. The default Keep original
  picture option composites the original source rectangle over the generated video.
  Review seams and surrounding motion. This is not pixel-exact restoration after
  scaling and encoding. Process individual shots, not a film containing cuts.
- Topaz: `topaz/upscale/video/precision`, Proteus, 2× or 4× dimensions; up to five
  minutes. Original frame rate is requested by omitting interpolation. H.264 output
  is requested for browser playback.

Both operations trim the source before submitting, restore source audio, verify the
returned duration and save separate project-owned video versions. They never replace
an edit automatically. Replace matching selection refuses if the trim has since
changed. Finished film exports can also be upscaled. Export at an appropriate canvas
resolution when incorporating an upscaled clip so it is not reduced again.

Submission is idempotent by request UUID. Unknown submission outcomes remain
uncertain, and known provider jobs resume polling without resubmitting. No hard-coded
price is shown; the UI explicitly says an estimate is unavailable. Paid processing
requires a configured key and an explicit Create new version action.

Contracts verified against provider documentation:
- https://fal.ai/models/topaz/upscale/video/precision/api
- https://fal.ai/models/fal-ai/luma-dream-machine/ray-2-flash/reframe/api
- https://fal.ai/docs/documentation/model-apis/inference/queue

Tests use controlled provider responses and real FFmpeg media. Live processing must
be verified with the owner's fal credentials before claiming production readiness.
