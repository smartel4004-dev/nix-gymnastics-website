#!/usr/bin/env python3
"""Add photos to a gallery (a stand-in for a CMS upload until the site moves to one).

    python3 tools/gallery_import.py <gallery-id> photo1.jpg photo2.jpg ...

Creates the gallery in _data/galleries.json if it doesn't exist (link it to a meet by
setting "event" to the meet's id, shown in the meets calendar URL: meets.html#<id>),
writes web sizes to assets/galleries/<gallery-id>/ (1600px and 640px) and appends each
photo with an empty "alt" for you to fill in. Then run: python3 build.py

Needs macOS (uses Swift + ImageIO so camera rotation is applied).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data" / "galleries.json"
RESIZE = ROOT / "tools" / "resize.swift"
SIZES = {"": (1600, "0.74"), "sm/": (640, "0.76")}


def main(gallery_id, files):
    galleries = json.loads(DATA.read_text()) if DATA.exists() else []
    gallery = next((g for g in galleries if g["id"] == gallery_id), None)
    if gallery is None:
        gallery = {"id": gallery_id, "event": "", "credit": "", "cover": "", "photos": []}
        galleries.append(gallery)
        print(f"Created gallery '{gallery_id}'. Set its \"event\" (or title/date/squad) in {DATA.name}.")
    out = ROOT / "assets" / "galleries" / gallery_id
    (out / "sm").mkdir(parents=True, exist_ok=True)
    known = {p["file"] for p in gallery["photos"]}
    for f in map(Path, files):
        name = f.stem.lower() + ".jpg"
        for sub, (edge, q) in SIZES.items():
            subprocess.run(["swift", str(RESIZE), str(f), str(out / sub / name), str(edge), q],
                           check=True, capture_output=True)
        if name not in known:
            gallery["photos"].append({"file": name, "alt": ""})
            known.add(name)
        print("added", name)
    if not gallery["cover"] and gallery["photos"]:
        gallery["cover"] = gallery["photos"][0]["file"]
    DATA.write_text(json.dumps(galleries, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
