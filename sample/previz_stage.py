"""Render a colour-coded staging previz.

Two rules the renderer enforces, because they are what the generative model
reads back:

  colour  = cast.  A saturated hue marks a character or a hero prop, and the
            prompt says who each hue is.
  grey    = environment.  Road, kerbs, buildings, street furniture.  Never
            cast, only there to make space legible.

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
ELEMENTS = [
    dict(name="red",    rgb=(214,  52,  48), size=(0.55, 0.40, 1.80),
         at=lambda t: (-3.2 + 6.4 * t, 6.5)),
    dict(name="blue",   rgb=( 46,  92, 214), size=(0.55, 0.40, 1.78),
         at=lambda t: (0.2, 15.0)),
    dict(name="green",  rgb=( 54, 158,  72), size=(0.55, 0.40, 1.82),
         at=lambda t: (1.9, 19.0 - 9.5 * t)),
    dict(name="yellow", rgb=(226, 184,  44), size=(1.30, 2.60, 0.85),
         at=lambda t: (-3.6, 9.0)),
]

# --- environment: grey = not cast ------------------------------------------
KERB_X = 5.0
BUILDINGS = [
    (sx * (KERB_X + 2.2 + (i % 2) * 1.1), 5.0 + i * 4.6, 4.0, 4.4, 7.0 + (i * 2.7) % 9.0)
    for sx in (-1, 1) for i in range(10)
]
OCCLUDER = (2.0, 12.0, 1.2, 0.8, 1.15)     # green passes behind, then in front


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
    # mid-ground occluder
    cx, cy, w, d, h = OCCLUDER
    for quad, k in box_faces(cx, cy, w, d, h):
        depth = float(np.mean([p[1] for p in quad]))
        out.append((depth, [project(p) for p in quad], fog(shade(KERB, k), depth)))
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
        for quad, k in box_faces(x, y, w, d, h):
            depth = float(np.mean([p[1] for p in quad]))
            faces.append((depth, [project(p) for p in quad], fog(shade(el["rgb"], k), depth, k=0.55)))

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
