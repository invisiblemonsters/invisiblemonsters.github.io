#!/usr/bin/env python3
"""duplicate_finder.py - Find duplicate files by size + SHA-256 hash.

Usage:
    python duplicate_finder.py --dir ~/Pictures
    python duplicate_finder.py --dir ~/Pictures --min-size 1024 --delete
"""
import argparse, hashlib, os
from collections import defaultdict

def file_hash(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Find duplicate files by content hash.")
    ap.add_argument("--dir", required=True)
    ap.add_argument("--min-size", type=int, default=1, help="ignore files smaller than N bytes")
    ap.add_argument("--delete", action="store_true", help="delete duplicates, keeping the first copy")
    args = ap.parse_args()

    by_size = defaultdict(list)
    for root, _, names in os.walk(args.dir):
        for name in names:
            path = os.path.join(root, name)
            try:
                size = os.path.getsize(path)
            except OSError:
                continue
            if size >= args.min_size:
                by_size[size].append(path)

    duplicates, saved = [], 0
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash = defaultdict(list)
        for path in paths:
            try:
                by_hash[file_hash(path)].append(path)
            except OSError:
                continue
        for digest, group in by_hash.items():
            if len(group) > 1:
                duplicates.append((size, group))

    for size, group in sorted(duplicates, key=lambda item: -item[0]):
        print(f"\n{len(group)} copies ({size} bytes each):")
        for path in group:
            print("   ", path)
        if args.delete:
            for extra in group[1:]:
                try:
                    os.remove(extra)
                    saved += size
                    print("    DELETED:", extra)
                except OSError as exc:
                    print("    delete failed:", exc)

    if not duplicates:
        print("No duplicates found.")
    elif args.delete:
        print(f"\nReclaimed approximately {saved / 1048576:.2f} MB.")
    else:
        print("\n(dry listing - pass --delete to remove extras, first copy is kept)")

if __name__ == "__main__":
    main()
