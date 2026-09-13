#!/usr/bin/env python3
"""file_organizer.py - Sort a folder's loose files into category subfolders.

Usage:
    python file_organizer.py --dir ~/Downloads          # preview
    python file_organizer.py --dir ~/Downloads --apply  # move files
    python file_organizer.py --dir ~/Downloads --by date --apply
"""
import argparse, datetime, os, shutil

CATEGORIES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".heic"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "audio": {".mp3", ".wav", ".flac", ".m4a", ".ogg"},
    "archives": {".zip", ".tar", ".gz", ".7z", ".rar", ".bz2"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".json", ".sh", ".ps1", ".go", ".rs", ".sol"},
}

def category_for(ext):
    for name, exts in CATEGORIES.items():
        if ext.lower() in exts:
            return name
    return "other"

def main():
    ap = argparse.ArgumentParser(description="Organize files into subfolders.")
    ap.add_argument("--dir", required=True)
    ap.add_argument("--by", choices=["category", "date"], default="category")
    ap.add_argument("--apply", action="store_true", help="move files (default: preview only)")
    args = ap.parse_args()

    moved = 0
    for name in sorted(os.listdir(args.dir)):
        path = os.path.join(args.dir, name)
        if not os.path.isfile(path) or name.startswith("."):
            continue
        ext = os.path.splitext(name)[1]
        if args.by == "category":
            bucket = category_for(ext)
        else:
            mtime = datetime.date.fromtimestamp(os.path.getmtime(path))
            bucket = mtime.strftime("%Y-%m")
        target_dir = os.path.join(args.dir, bucket)
        target = os.path.join(target_dir, name)
        print(("MOVE: " if args.apply else "PLAN: ") + name + " -> " + bucket + "/")
        if args.apply:
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(path, target)
            moved += 1
    print(f"\n{'(preview - pass --apply to move)' if not args.apply else str(moved) + ' file(s) moved'}")

if __name__ == "__main__":
    main()
