"""Render a colour-coded staging previz.

Two rules the renderer enforces, because they are what the generative model
reads back:

  colour  = cast.  A saturated hue marks a character or a hero prop, and the
            prompt says who each hue is.
  grey    = environment.  Road, kerbs, buildings, street furniture.  Never
            cast, only there to make space legible.
  white   = the face a figure is turned toward.

v2 adds the depth cues v1 lacked.  In v1 every mark floated in an empty void,
identically lit at every distance, so the only thing separating a block at
15m from one at 6m was its size — and the render flattened everyone into one
shallow band near the lens.  A pure Z move (an actor walking toward camera)
vanished entirely.  So: converging road markings, kerbs, building masses down
both sides, atmospheric falloff toward the horizon, and a mid-ground occluder
an actor passes behind and then in front of.  Overlap is unambiguous ordering
in a way size alone is not.
"""
import numpy as np
from PIL import Image, ImageDraw

W, H, FPS, SECS = 854, 480, 24, 5.0
LENS_MM, SENSOR_MM = 28.0, 36.0
F = W * LENS_MM / SENSOR_MM
CAM_Z = 1.55
CX, CY = W / 2.0, H / 2.0

SKY    = (188, 192, 198)
ROAD   = (150, 152, 158)
KERB   = (176, 178, 183)
PAINT  = (232, 233, 236)
BUILD  = (128, 131, 138)
FOG_AT = 46.0          # distance at which everything has faded to sky

# box_faces() order: top, front(-y), back(+y), left, right.
_FRONT_FACE, _BACK_FACE = 1, 2

# How much white is mixed into the face a figure is turned toward. A tint,
# not a repaint: replacing the face outright drowned the hue that carries
# identity, and identity is the channel that was already unreliable.
FACING_TINT = 0.5


def project(p):
    x, y, z = p
    y = max(y, 0.05)
    return (CX + F * x / y, CY - F * (z - CAM_Z) / y)


def fog(rgb, depth, k=0.88):
    """Fade toward the horizon colour with distance."""
    t = min(1.0, max(0.0, (depth - 2.0) / FOG_AT)) * k
    return tuple(int(c * (1 - t) + s * t) for c, s in zip(rgb, SKY))


def shade(rgb, k):
    return tuple(int(min(255, max(0, c * k))) for c in rgb)


def box_faces(cx, cy, w, d, h, z0=0.0):
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = cy - d / 2, cy + d / 2
    z1 = z0 + h
    c = {
        "000": (x0, y0, z0), "100": (x1, y0, z0), "110": (x1, y1, z0), "010": (x0, y1, z0),
        "001": (x0, y0, z1), "101": (x1, y0, z1), "111": (x1, y1, z1), "011": (x0, y1, z1),
    }
    return [
        ([c["001"], c["101"], c["111"], c["011"]], 1.00),
        ([c["000"], c["100"], c["101"], c["001"]], 0.82),
        ([c["010"], c["110"], c["111"], c["011"]], 0.66),
        ([c["000"], c["010"], c["011"], c["001"]], 0.58),
        ([c["100"], c["110"], c["111"], c["101"]], 0.74),
    ]


# --- cast: colour = character ---------------------------------------------
#
# v3 gives each proxy the character's real proportions. In v2 every actor was
# an identical 0.55 x 0.40 x 1.80 capsule differing only in hue, so the model
# had no geometric reason to bind a coloured box to a named person — and the
# behaviours arrived as a set with the mapping onto characters re-rolled
# between generations. A short slight figure and a tall broad one are told
# apart by shape, which is a far harder signal than a colour the prompt
# merely asserts.
ELEMENTS = [
    # woman in the raincoat: short, narrow
    dict(name="red",    rgb=(214,  52,  48), size=(0.44, 0.34, 1.62),
         at=lambda t: (-3.2 + 6.4 * t, 6.5), facing=0.0),
    # police officer: tall, broad shoulders
    dict(name="blue",   rgb=( 46,  92, 214), size=(0.68, 0.44, 1.88),
         at=lambda t: (0.2, 15.0), facing=180.0),
    # man in the work jacket: mid build — shifted clear of the lamppost
    dict(name="green",  rgb=( 54, 158,  72), size=(0.55, 0.40, 1.75),
         at=lambda t: (2.3, 19.0 - 9.5 * t), facing=180.0),
    # parked taxi: a prop, not a person
    dict(name="yellow", rgb=(226, 184,  44), size=(1.30, 2.60, 0.85),
         at=lambda t: (-3.6, 9.0), facing=None),   # a prop has no facing
]

# --- environment: grey = not cast ------------------------------------------
KERB_X = 5.0
BUILDINGS = [
    (sx * (KERB_X + 2.2 + (i % 2) * 1.1), 5.0 + i * 4.6, 4.0, 4.4, 7.0 + (i * 2.7) % 9.0)
    for sx in (-1, 1) for i in range(10)
]
# A lamppost, not a block. v2 put a 1.2m-wide box at x=2.0 and walked the
# green actor down x=1.9 — their footprints overlapped, so he passed straight
# through a solid object. A previz whose whole job is describing physical
# space must not contain a physical impossibility. The post sits on the
# camera -> green-at-19m sightline, so he starts occluded and steps out from
# behind it, with 0.45m of clearance he never crosses.
OCCLUDER = (1.30, 12.0, 0.25, 0.25, 4.0)
LAMP_HEAD = (1.30, 12.0, 0.70, 0.30, 0.18)


def env_faces():
    out = []
    # road
    out.append((999.0, [project((-KERB_X, FOG_AT + 8, 0)), project((KERB_X, FOG_AT + 8, 0)),
                        project((KERB_X, 1.2, 0)), project((-KERB_X, 1.2, 0))], ROAD))
    # kerbs + pavement, both sides
    for sx in (-1, 1):
        out.append((998.0, [project((sx * KERB_X, FOG_AT + 8, 0.14)), project((sx * 14, FOG_AT + 8, 0.14)),
                            project((sx * 14, 1.2, 0.14)), project((sx * KERB_X, 1.2, 0.14))], KERB))
    # centre-line dashes: converging parallels, the strongest depth cue there is
    y = 3.0
    while y < FOG_AT:
        out.append((900 - y, [project((-0.09, y + 1.9, 0.01)), project((0.09, y + 1.9, 0.01)),
                              project((0.09, y, 0.01)), project((-0.09, y, 0.01))], fog(PAINT, y)))
        y += 3.8
    # building masses
    for cx, cy, w, d, h in BUILDINGS:
        for quad, k in box_faces(cx, cy, w, d, h):
            depth = float(np.mean([p[1] for p in quad]))
            out.append((depth, [project(p) for p in quad], fog(shade(BUILD, k), depth)))
    # mid-ground occluder: post plus lamp head, so it reads as street furniture
    for cx, cy, w, d, h in (OCCLUDER,):
        for quad, k in box_faces(cx, cy, w, d, h):
            depth = float(np.mean([p[1] for p in quad]))
            out.append((depth, [project(p) for p in quad], fog(shade(KERB, k), depth)))
    cx, cy, w, d, h = LAMP_HEAD
    for quad, k in box_faces(cx, cy, w, d, h, z0=OCCLUDER[4] - 0.1):
        depth = float(np.mean([p[1] for p in quad]))
        out.append((depth, [project(p) for p in quad], fog(shade(PAINT, k), depth)))
    return out


ENV = None


def render(t):
    global ENV
    if ENV is None:
        ENV = env_faces()
    img = Image.new("RGB", (W, H), SKY)
    dr = ImageDraw.Draw(img)

    faces = list(ENV)
    for el in ELEMENTS:
        x, y = el["at"](t)
        w, d, h = el["size"]
        faces.append((y + 0.4, [project((x - w, y - d, 0.02)), project((x + w, y - d, 0.02)),
                                project((x + w, y + d, 0.02)), project((x - w, y + d, 0.02))],
                      fog(shade(ROAD, 0.86), y)))
        # Face 1 is the box's -y side. Marking it lets the render read which
        # way a figure is turned: a flat monolith says where someone stands
        # and nothing about where they look.
        for index, (quad, k) in enumerate(box_faces(x, y, w, d, h)):
            depth = float(np.mean([p[1] for p in quad]))
            rgb = el["rgb"]
            facing = el.get("facing")
            marked = (index == _FRONT_FACE and facing == 0.0) or (
                index == _BACK_FACE and facing == 180.0
            )
            if marked:
                rgb = tuple(int(c + (255 - c) * FACING_TINT) for c in rgb)
            faces.append((depth, [project(p) for p in quad], fog(shade(rgb, k), depth, k=0.55)))

    for _, pts, col in sorted(faces, key=lambda f: -f[0]):
        dr.polygon(pts, fill=col)
    return img


if __name__ == "__main__":
    import sys, os
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    n = int(FPS * SECS)
    for i in range(n):
        render(i / (n - 1)).save(f"{out}/f_{i:04d}.png")
    print(f"{n} frames -> {out}")
