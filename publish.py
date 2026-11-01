"""Publish one due, approved entry from calendar.json. Not wired to a scheduler yet.

Safety:
- Only touches an entry where approved == true. "approved" is set by Armando
  reviewing media/ + calendar.json, never by this script.
- Only posts within its time slot (slot_start <= now <= slot_start + 3h); a
  missed slot is skipped, never posted late (see immersauna-ig-autopost incident).
- Marks posted=true in calendar.json immediately after a successful call so a
  re-run never double-posts.
- Requires POSTING_ON=1 in the environment as a second, explicit switch beyond
  "approved" -- this is the one-time "you may post" Armando gives in chat.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Toronto")
MEDIA_BASE = "https://aascorve.github.io/armandoascorve-ig/media/"
SLOT_WINDOW = timedelta(hours=3)
CAL = __import__("pathlib").Path(__file__).resolve().parent / "calendar.json"


def due_entries(now):
    cal = json.loads(CAL.read_text())
    due = []
    for p in cal["feed"]:
        if not p["approved"] or p["posted"]:
            continue
        start = datetime.fromisoformat(f"{p['date']}T{p['time']}").replace(tzinfo=TZ)
        if start <= now <= start + SLOT_WINDOW:
            due.append(("feed", p))
    for s in cal["stories"]:
        if not s["approved"] or s["posted"]:
            continue
        start = datetime.fromisoformat(f"{s['date']}T{s['time']}").replace(tzinfo=TZ)
        if start <= now <= start + SLOT_WINDOW:
            due.append(("story", s))
    return cal, due


def urls_for(entry):
    from picks import PICKS
    _, names = PICKS[entry["key"]]
    n = len(names)
    tag = "story" if "idx" in entry else "feed"
    idx = [entry["idx"]] if "idx" in entry else range(n)
    return [f"{MEDIA_BASE}{entry['key']}_{tag}_{i}.jpg" for i in idx]


def main():
    if os.environ.get("POSTING_ON") != "1":
        print("POSTING_ON is not set -- refusing to post. This is the explicit switch "
              "Armando sets in chat; nothing here turns it on by itself.", file=sys.stderr)
        return 1
    now = datetime.now(TZ)
    cal, due = due_entries(now)
    if not due:
        print("nothing due right now")
        return 0
    for kind, entry in due:
        print(f"would publish {kind} {entry['key']} ({entry['date']} {entry['time']}) -- "
              "actual execute_action call intentionally not wired in yet.")
        # Next step once Armando says go: call the Windsor instagram connector's
        # create_image_post / create_carousel_post / create_video_post / create_story
        # with urls_for(entry) and entry.get("caption"), then set entry["posted"]=True
        # and CAL.write_text(json.dumps(cal, indent=2)) immediately after success.
    return 0


if __name__ == "__main__":
    sys.exit(main())
