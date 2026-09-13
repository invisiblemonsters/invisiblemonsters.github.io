#!/usr/bin/env python3
"""bulk_rename.py - Regex batch-rename files. Dry-run by default.

Usage:
    python bulk_rename.py --dir ./photos --find "IMG_(\d+)" --replace "vacation_\1"
    python bulk_rename.py --dir ./docs --find " " --replace "_" --ext .md --apply
"""
import argparse, os, re

def iter_files(directory, recurse=False):
    if recurse:
        for root, _, names in os.walk(directory):
            for name in names:
                yield os.path.join(root, name)
    else:
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                yield path

def main():
    ap = argparse.ArgumentParser(description="Batch rename with regex. Dry-run unless --apply.")
    ap.add_argument("--dir", required=True)
    ap.add_argument("--find", required=True, help="regex matched against the file name (no extension by default)")
    ap.add_argument("--replace", required=True, help="replacement text (supports \\1 groups)")
    ap.add_argument("--ext", help="only touch files with this extension, e.g. .jpg")
    ap.add_argument("--recurse", action="store_true")
    ap.add_argument("--apply", action="store_true", help="execute renames (default: dry-run)")
    args = ap.parse_args()

    pattern = re.compile(args.find)
    renamed = 0
    for path in sorted(iter_files(args.dir, args.recurse)):
        if args.ext and not path.lower().endswith(args.ext.lower()):
            continue
        folder, fname = os.path.split(path)
        stem, fext = os.path.splitext(fname)
        new_stem = pattern.sub(args.replace, stem)
        if new_stem == stem:
            continue
        new_name = new_stem + fext
        new_path = os.path.join(folder, new_name)
        print(("RENAME: " if args.apply else "DRY-RUN: ") + fname + " -> " + new_name)
        if args.apply:
            if os.path.exists(new_path):
                print("  SKIPPED (target exists)")
                continue
            os.rename(path, new_path)
            renamed += 1
    if not args.apply:
        print("\nDry-run complete. Pass --apply to execute.")
    else:
        print(f"\n{renamed} file(s) renamed.")

if __name__ == "__main__":
    main()
