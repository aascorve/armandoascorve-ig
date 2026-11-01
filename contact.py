"""Write numbered contact sheets per source folder so frames can be reviewed and picked by index."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from sources import SOURCES, photos

OUT = Path(__file__).resolve().parent / "contact"
CELL, COLS, PER_SHEET = 300, 6, 30


def sheet(key, chunk, start, n):
    rows = (len(chunk) + COLS - 1) // COLS
    canvas = Image.new("RGB", (COLS * CELL, rows * (CELL + 24)), "white")
    draw = ImageDraw.Draw(canvas)
    for i, path in enumerate(chunk):
        try:
            img = Image.open(path)
            img.draft("RGB", (CELL * 2, CELL * 2))
            img = ImageOps.exif_transpose(img).convert("RGB")
            img.thumbnail((CELL - 8, CELL - 8))
        except Exception as error:  # unreadable file: leave the cell blank, note it
            print(f"skip {path.name}: {error}", file=sys.stderr)
            continue
        x, y = (i % COLS) * CELL, (i // COLS) * (CELL + 24)
        canvas.paste(img, (x + (CELL - img.width) // 2, y + (CELL - img.height) // 2))
        draw.text((x + 6, y + CELL + 4), f"{start + i}  {path.name[:30]}", fill="black")
    dst = OUT / f"{key}-{n}.jpg"
    canvas.save(dst, quality=80)
    return dst


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for key in (sys.argv[1:] or SOURCES):
        items = photos(key)
        for n, start in enumerate(range(0, len(items), PER_SHEET), 1):
            print(sheet(key, items[start:start + PER_SHEET], start, n))
