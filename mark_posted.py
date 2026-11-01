"""Record a successful post back into calendar.json so it never posts twice.

Usage:
  .venv/bin/python mark_posted.py feed <key> <media_id>
  .venv/bin/python mark_posted.py story <key> <idx> <media_id>
"""
import json
import sys
from pathlib import Path

CAL = Path(__file__).resolve().parent / "calendar.json"


def main(argv):
    cal = json.loads(CAL.read_text())
    kind = argv[1]
    if kind == "feed":
        key, media_id = argv[2], argv[3]
        for p in cal["feed"]:
            if p["key"] == key and not p["posted"]:
                p["posted"] = True
                p["media_id"] = media_id
                break
        else:
            print(f"no unposted feed entry with key {key!r}", file=sys.stderr)
            return 1
    elif kind == "story":
        key, idx, media_id = argv[2], int(argv[3]), argv[4]
        for s in cal["stories"]:
            if s["key"] == key and s["idx"] == idx and not s["posted"]:
                s["posted"] = True
                s["media_id"] = media_id
                break
        else:
            print(f"no unposted story entry with key {key!r} idx {idx}", file=sys.stderr)
            return 1
    else:
        print(f"unknown kind {kind!r}, expected 'feed' or 'story'", file=sys.stderr)
        return 1
    CAL.write_text(json.dumps(cal, indent=2))
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
