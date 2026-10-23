"""Draw the app icons (saffron square + white shield with heart). Needs Pillow."""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "static"

for size in (192, 512):
    s = size / 512
    img = Image.new("RGB", (size, size), "#e8590c")
    d = ImageDraw.Draw(img)
    shield = [(256, 96), (396, 150), (384, 300), (256, 424), (128, 300), (116, 150)]
    d.polygon([(x * s, y * s) for x, y in shield], fill="#ffffff")
    # heart
    r = 38 * s
    for cx in (220, 292):
        d.ellipse([cx * s - r, 220 * s - r, cx * s + r, 220 * s + r], fill="#c92a2a")
    d.polygon([(186 * s, 240 * s), (326 * s, 240 * s), (256 * s, 330 * s)], fill="#c92a2a")
    img.save(OUT / f"icon-{size}.png")
    print("wrote", OUT / f"icon-{size}.png")
