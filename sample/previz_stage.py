"""Render a colour-coded staging previz: several actors, distinct marks.

Deliberately crude — flat-shaded boxes on a ground plane, one saturated hue
per element — because the point is to carry STRUCTURE (who is where, who
moves how) into the generation, not to look like anything.

Camera is locked off, so any motion in the result comes from the staging.
"""
import numpy as np
from PIL import Image, ImageDraw

W, H, FPS, SECS = 854, 480, 24, 5.0
LENS_MM, SENSOR_MM = 28.0, 36.0
F = W * LENS_MM / SENSOR_MM
CAM_Z = 1.55                       # eye height
CX, CY = W / 2.0, H / 2.0

SKY    = (188, 192, 198)
GROUND = (206, 208, 212)

def project(p):
    x, y, z = p
    y = max(y, 0.05)
    return (CX + F * x / y, CY - F * (z - CAM_Z) / y)

def box_faces(cx, cy, w, d, h):
    """8 corners -> 6 quads of an axis-aligned box standing on z=0."""
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = cy - d / 2, cy + d / 2
    z0, z1 = 0.0, h
    c = {
        "000": (x0, y0, z0), "100": (x1, y0, z0), "110": (x1, y1, z0), "010": (x0, y1, z0),
        "001": (x0, y0, z1), "101": (x1, y0, z1), "111": (x1, y1, z1), "011": (x0, y1, z1),
    }
    return [
        ([c["001"], c["101"], c["111"], c["011"]], 1.00),   # top
        ([c["000"], c["100"], c["101"], c["001"]], 0.82),   # front (toward camera)
        ([c["010"], c["110"], c["111"], c["011"]], 0.66),   # back
        ([c["000"], c["010"], c["011"], c["001"]], 0.58),   # left
        ([c["100"], c["110"], c["111"], c["101"]], 0.74),   # right
    ]

def shade(rgb, k):
    return tuple(int(min(255, max(0, c * k))) for c in rgb)

# --- the staging -----------------------------------------------------------
# Each element: colour, size, and a position function of normalised time.
ELEMENTS = [
    # RED actor: crosses screen-left -> screen-right, midground
    dict(name="red",    rgb=(214,  52,  48), size=(0.55, 0.40, 1.80),
         at=lambda t: (-3.2 + 6.4 * t, 6.5)),
    # BLUE actor: stands still, centre background
    dict(name="blue",   rgb=( 46,  92, 214), size=(0.55, 0.40, 1.78),
         at=lambda t: (0.2, 15.0)),
    # GREEN actor: walks toward camera
    dict(name="green",  rgb=( 54, 158,  72), size=(0.55, 0.40, 1.82),
         at=lambda t: (1.9, 19.0 - 9.5 * t)),
    # YELLOW prop: low static block, foreground left (a car-sized mark)
    dict(name="yellow", rgb=(226, 184,  44), size=(1.30, 2.60, 0.85),
         at=lambda t: (-3.6, 9.0)),
]

def render(t):
    img = Image.new("RGB", (W, H), SKY)
    dr = ImageDraw.Draw(img)
    # ground plane
    dr.polygon([project((-60, 60, 0)), project((60, 60, 0)),
                project((60, 1.2, 0)), project((-60, 1.2, 0))], fill=GROUND)

    faces = []
    for el in ELEMENTS:
        x, y = el["at"](t)
        w, d, h = el["size"]
        # contact shadow, so ground position reads
        faces.append((y + 0.4, [project((x - w, y - d, 0)), project((x + w, y - d, 0)),
                                project((x + w, y + d, 0)), project((x - w, y + d, 0))],
                      shade(GROUND, 0.90)))
        for quad, k in box_faces(x, y, w, d, h):
            depth = float(np.mean([p[1] for p in quad]))
            faces.append((depth, [project(p) for p in quad], shade(el["rgb"], k)))

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
