"""Print the calendar.json entries that are due right now: approved, not yet
posted, and inside their posting slot (slot_start .. slot_start + 3h). A
missed slot is never caught up later -- it just stops showing as due.

Usage: .venv/bin/python publish.py
Prints a JSON array (possibly empty) to stdout. Prints nothing else, so the
output is always safe to parse directly.

This script only READS calendar.json and never calls Instagram. The caller
(a scheduled task session, or Armando running it by hand) is responsible for
making the actual Windsor execute_action call for each entry it prints, then
recording success with mark_posted.py.
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from picks import PICKS

TZ = ZoneInfo("America/Toronto")
MEDIA_BASE = "https://aascorve.github.io/armandoascorve-ig/media/"
SLOT_WINDOW = timedelta(hours=3)
CAL = Path(__file__).resolve().parent / "calendar.json"

ACTION_BY_TYPE = {
    "image": "create_image_post",
    "carousel": "create_carousel_post",
    "reel": "create_video_post",
}


def urls_for(key, tag, idx=None):
    _, names = PICKS[key]
    n = len(names)
    indices = [idx] if idx is not None else range(n)
    ext = "mp4" if tag == "" else "jpg"  # reels use the bare key, not key_feed_N
    if tag == "video":
        return [f"{MEDIA_BASE}{key}.mp4"]
    return [f"{MEDIA_BASE}{key}_{tag}_{i}.jpg" for i in indices]


def due_feed(cal, now):
    out = []
    for p in cal["feed"]:
        if not p["approved"] or p["posted"]:
            continue
        start = datetime.fromisoformat(f"{p['date']}T{p['time']}").replace(tzinfo=TZ)
        if not (start <= now <= start + SLOT_WINDOW):
            continue
        entry = {
            "kind": "feed", "key": p["key"], "type": p["type"],
            "windsor_action": ACTION_BY_TYPE[p["type"]],
            "caption": p["caption"] + "\n\n" + p["tags"],
            "slot": f"{p['date']} {p['time']}",
        }
        if p["type"] == "reel":
            entry["video_url"] = f"{MEDIA_BASE}{p['key']}.mp4"
            entry["cover_url"] = f"{MEDIA_BASE}{p['key']}_cover.jpg"
        elif p["type"] == "carousel":
            entry["image_urls"] = urls_for(p["key"], "feed")
        else:
            entry["image_url"] = urls_for(p["key"], "feed")[0]
        out.append(entry)
    return out


def due_stories(cal, now):
    out = []
    for s in cal["stories"]:
        if not s["approved"] or s["posted"]:
            continue
        start = datetime.fromisoformat(f"{s['date']}T{s['time']}").replace(tzinfo=TZ)
        if not (start <= now <= start + SLOT_WINDOW):
            continue
        out.append({
            "kind": "story", "key": s["key"], "idx": s["idx"],
            "windsor_action": "create_story",
            "image_url": urls_for(s["key"], "story", s["idx"])[0],
            "slot": f"{s['date']} {s['time']}",
        })
    return out


def main():
    cal = json.loads(CAL.read_text())
    now = datetime.now(TZ)
    due = due_feed(cal, now) + due_stories(cal, now)
    print(json.dumps(due, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
