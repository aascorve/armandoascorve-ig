"""Crop Week 1 picks to IG sizes and write calendar.json. No network calls, no posting."""
import json
from pathlib import Path
from PIL import Image, ImageOps

from sources import SOURCES
from picks import PICKS

OUT = Path(__file__).resolve().parent / "media"
FEED = (1080, 1350)   # 4:5
STORY = (1080, 1920)  # 9:16


def crop_to(img, size):
    img = ImageOps.exif_transpose(img).convert("RGB")
    tw, th = size
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    img = img.resize((round(iw * scale), round(ih * scale)))
    x = (img.width - tw) // 2
    y = (img.height - th) // 2
    return img.crop((x, y, x + tw, y + th))


def export(key, size, tag):
    source_key, names = PICKS[key]
    folder = SOURCES[source_key]
    paths = []
    for i, name in enumerate(names):
        src = folder / name
        dst = OUT / f"{key}_{tag}_{i}.jpg"
        if not dst.exists():
            img = crop_to(Image.open(src), size)
            img.save(dst, quality=88)
        paths.append(dst.name)
    return paths


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    feed = {k: export(k, FEED, "feed") for k in
             ["anastasiia_carousel", "photographer_hero", "kitchen_hero", "kitchen_carousel"]}
    story = {k: export(k, STORY, "story") for k in
              ["story_anastasiia", "story_photographer", "story_kitchen"]}
    print(json.dumps({"feed": feed, "story": story}, indent=1))
