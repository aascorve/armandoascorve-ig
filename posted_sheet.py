"""Contact sheet of already-posted IG covers, to avoid reposting frames."""
from pathlib import Path
from PIL import Image, ImageDraw
files = sorted(Path(".posted").glob("*.jpg"))
CELL, COLS = 220, 8
rows = (len(files) + COLS - 1) // COLS
c = Image.new("RGB", (COLS * CELL, rows * (CELL + 18)), "white"); d = ImageDraw.Draw(c)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB"); im.thumbnail((CELL - 6, CELL - 6))
    x, y = (i % COLS) * CELL, (i // COLS) * (CELL + 18)
    c.paste(im, (x + 3, y + 3)); d.text((x + 4, y + CELL), f.stem[:22], fill="black")
c.save("contact/posted.jpg", quality=80)
