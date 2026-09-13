#!/usr/bin/env python3
"""backup_rotator.py - Timestamped zip backups with automatic rotation.

Usage:
    python backup_rotator.py create --dir ~/project --dest ~/backups --keep 7
    python backup_rotator.py list --dest ~/backups
    python backup_rotator.py restore --zip ~/backups/project_20260913-120000.zip --to ~/restore
"""
import argparse, datetime, glob, os, zipfile

def backup_name(directory):
    return os.path.basename(os.path.abspath(directory))

def main():
    ap = argparse.ArgumentParser(description="Zip backups with rotation.")
    sub = ap.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--dir", required=True)
    create.add_argument("--dest", required=True)
    create.add_argument("--keep", type=int, default=7, help="keep the N newest backups (default 7)")

    listing = sub.add_parser("list")
    listing.add_argument("--dest", required=True)

    restore = sub.add_parser("restore")
    restore.add_argument("--zip", required=True)
    restore.add_argument("--to", required=True)

    args = ap.parse_args()

    if args.command == "create":
        os.makedirs(args.dest, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        label = backup_name(args.dir)
        target = os.path.join(args.dest, f"{label}_{stamp}.zip")
        count = 0
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, names in os.walk(args.dir):
                for name in names:
                    path = os.path.join(root, name)
                    arcname = os.path.relpath(path, os.path.dirname(os.path.abspath(args.dir)))
                    zf.write(path, arcname)
                    count += 1
        print(f"Created {target} ({count} files, {os.path.getsize(target) / 1048576:.2f} MB)")
        existing = sorted(glob.glob(os.path.join(args.dest, f"{label}_*.zip")))
        for old in existing[:-args.keep]:
            os.remove(old)
            print("pruned:", old)

    elif args.command == "list":
        for path in sorted(glob.glob(os.path.join(args.dest, "*.zip"))):
            size = os.path.getsize(path) / 1048576
            print(f"{os.path.basename(path)}  ({size:.2f} MB)")
        print()

    elif args.command == "restore":
        os.makedirs(args.to, exist_ok=True)
        with zipfile.ZipFile(args.zip) as zf:
            zf.extractall(args.to)
            print(f"Extracted {len(zf.namelist())} files to {args.to}")

if __name__ == "__main__":
    main()
