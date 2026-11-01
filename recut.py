"""Re-cut workshop reels for IG: drop the shared title card, open on a hook line.

Reuses the cached graded shots and music settings from reels-2026/work/render.py
(read-only), so the cut, grade and beat grid match the originals.

Usage: .venv/bin/python recut.py [reel_id ...]
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "media"
RENDER = Path("/Volumes/Elements/reels-2026/work/render.py")
HOOK_FONT = "/Library/Fonts/Archivo-SemiBold.ttf"
KICKER_FONT = "/Library/Fonts/Archivo-Medium.ttf"
HOOK_END = 3.2  # seconds the hook stays on screen

# reel id -> (output key, shot order as indexes into the original list, kicker, hook lines)
RECUTS = {
    "09-the-photographer": (
        "r09_photographer", [1, 0, *range(2, 20)],
        "WHAT I TEACH FIRST",
        ["Stop taking pictures.", "Start directing them."],
    ),
    "05-the-editorial": (
        "r05_editorial", list(range(15)),
        "RACK TO FINAL FRAME",
        ["How an editorial look", "gets built in 30 seconds"],
    ),
}


def load_render():
    spec = importlib.util.spec_from_file_location("reel_render", RENDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-1500:]}")


def esc(text):
    return text.replace("\\", "\\\\").replace("'", "’").replace(":", "\\:").replace(",", "\\,")


def hook_filters(kicker, lines):
    alpha = f"if(lt(t,{HOOK_END}),1,if(lt(t,{HOOK_END}+0.4),1-(t-{HOOK_END})/0.4,0))"
    parts = [
        f"drawtext=fontfile='{KICKER_FONT}':text='{esc(kicker)}':fontsize=30:fontcolor=white@0.85:"
        f"x=(w-text_w)/2:y=h*0.14:alpha='{alpha}':shadowcolor=black@0.6:shadowy=2"
    ]
    for i, line in enumerate(lines):
        parts.append(
            f"drawtext=fontfile='{HOOK_FONT}':text='{esc(line)}':fontsize=68:fontcolor=white:"
            f"box=1:boxcolor=black@0.62:boxborderw=18:x=(w-text_w)/2:y=h*0.14+70+{i * 108}:alpha='{alpha}'"
        )
    return ",".join(parts)


def recut(render, rid):
    key, order, kicker, lines = RECUTS[rid]
    reel = render.REELS[rid]
    shot_dir = Path(render.WORK) / "shots" / rid
    shots = [shot_dir / f"{i:02d}_{reel['shots'][i][0]}.mp4" for i in order]
    missing = [s.name for s in shots if not s.exists()]
    if missing:
        raise FileNotFoundError(f"{rid}: cached shots missing {missing}; run render.py {rid} first")

    frames = render.shot_frames(reel)
    total = sum(frames[i] for i in order) / render.FPS
    OUT.mkdir(exist_ok=True)
    listing = OUT / f".{key}-list.txt"
    listing.write_text("".join(f"file '{s}'\n" for s in shots))
    vf = (f"{hook_filters(kicker, lines)},noise=alls=5:allf=t,vignette=angle=PI/5.5,"
          f"fade=t=out:st={total - 1.2:.3f}:d=1.2,format=yuv420p")
    af = (f"afade=t=in:st=0:d=0.15,afade=t=out:st={total - 1.8:.3f}:d=1.8,"
          f"loudnorm=I=-14:TP=-1.5:LRA=11")
    dst = OUT / f"{key}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-ss", f"{reel['start']:.3f}", "-i", f"{render.MUSIC}/{reel['music']}",
         "-map", "0:v", "-map", "1:a", "-t", f"{total:.3f}", "-vf", vf, "-af", af,
         "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-profile:v", "high",
         "-pix_fmt", "yuv420p", "-r", str(render.FPS), "-c:a", "aac", "-b:a", "192k",
         "-ar", "48000", "-movflags", "+faststart", str(dst)])
    listing.unlink()
    run(["ffmpeg", "-v", "error", "-y", "-ss", "0.6", "-i", str(dst), "-frames:v", "1",
         "-q:v", "3", str(OUT / f"{key}_cover.jpg")])
    return dst, total


if __name__ == "__main__":
    render = load_render()
    for rid in sys.argv[1:] or RECUTS:
        dst, total = recut(render, rid)
        print(f"{dst.name}: {total:.1f}s, {dst.stat().st_size / 1e6:.1f} MB")
