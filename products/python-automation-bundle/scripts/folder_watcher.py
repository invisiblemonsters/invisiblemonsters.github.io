#!/usr/bin/env python3
"""folder_watcher.py - Watch a folder; move new files or run a command on them.

Usage:
    python folder_watcher.py --dir ~/inbox --move-to ~/processed
    python folder_watcher.py --dir ~/inbox --on-new "python process.py {file}" --interval 5
"""
import argparse, os, shutil, subprocess, time

def listing(directory):
    try:
        return {n for n in os.listdir(directory) if os.path.isfile(os.path.join(directory, n))}
    except FileNotFoundError:
        raise SystemExit(f"No such directory: {directory}")

def wait_until_stable(path, settle=1.0, timeout=60.0):
    """Wait until the file size stops changing (handles slow copies)."""
    last = -1
    stable_since = None
    start = time.time()
    while time.time() - start < timeout:
        size = os.path.getsize(path)
        now = time.time()
        if size == last:
            if stable_since is None:
                stable_since = now
            elif now - stable_since >= settle:
                return True
        else:
            last = size
            stable_since = None
        time.sleep(0.25)
    return False

def main():
    ap = argparse.ArgumentParser(description="Watch a folder for new files.")
    ap.add_argument("--dir", required=True, help="folder to watch")
    ap.add_argument("--move-to", help="move new files into this folder")
    ap.add_argument("--on-new", help="shell command per file; {file} is replaced with the full path")
    ap.add_argument("--interval", type=float, default=5.0, help="poll interval in seconds (default 5)")
    ap.add_argument("--existing", action="store_true", help="also process files already present at start")
    args = ap.parse_args()

    if not args.move_to and not args.on_new:
        raise SystemExit("Nothing to do: pass --move-to and/or --on-new.")
    if args.move_to:
        os.makedirs(args.move_to, exist_ok=True)

    known = set() if args.existing else listing(args.dir)
    print(f"Watching {args.dir} (Ctrl+C to stop)...")
    try:
        while True:
            current = listing(args.dir)
            for name in sorted(current - known):
                path = os.path.join(args.dir, name)
                wait_until_stable(path)
                print("new file:", path)
                if args.on_new:
                    command = args.on_new.replace("{file}", path)
                    print("  running:", command)
                    subprocess.run(command, shell=True)
                if args.move_to:
                    shutil.move(path, os.path.join(args.move_to, name))
                    print("  moved ->", args.move_to)
            known = current
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
