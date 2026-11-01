"""Photo folders Armando cleared for the IG queue (Nov 1 2026). Joel's set and the Hinge subfolder are excluded."""
from pathlib import Path

SOURCES = {
    "heather_fam": Path("/Volumes/Elements/TheEditorialEyeWS/HeathersFam/edited"),
    "heather_fam_preview": Path("/Volumes/Elements/TheEditorialEyeWS/HeathersFam/preview/edited"),
    "anastasiia": Path("/Volumes/Elements/Anastasiia/edited"),
    "workshop": Path("/Volumes/Elements/TheEditorialEyeWS/Photos/edited"),
    "heather_toronto": Path("/Volumes/Elements/HeatherToronto/edited"),
    "nadine": Path("/Volumes/LaCie/Nadine/edited"),
    "nadine_foto": Path("/Volumes/LaCie/Nadine/FOTO/edited"),
    "nadine_studio": Path("/Volumes/LaCie/Nadine/studio/Selected"),
}
EXTS = {".jpg", ".jpeg", ".tif", ".tiff", ".png"}


def photos(key):
    folder = SOURCES[key]
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTS and not p.name.startswith("."))
