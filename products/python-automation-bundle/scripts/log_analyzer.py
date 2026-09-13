#!/usr/bin/env python3
"""log_analyzer.py - Summarize logs: level counts + top repeated lines.

Usage:
    python log_analyzer.py app.log --top 10
    python log_analyzer.py logs/*.log --level ERROR
"""
import argparse, re, sys
from collections import Counter

LEVEL_RE = re.compile(r"\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b", re.IGNORECASE)
NORMALIZE_RE = re.compile(r"(0x[0-9a-fA-F]+|\b\d+\b)")

def main():
    ap = argparse.ArgumentParser(description="Summarize log files.")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--top", type=int, default=10, help="show top N repeated message patterns")
    ap.add_argument("--level", help="only analyze lines containing this level, e.g. ERROR")
    ap.add_argument("--max-line", type=int, default=160, help="truncate displayed lines")
    args = ap.parse_args()

    levels = Counter()
    patterns = Counter()
    total = 0

    for path in args.files:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    line = raw.rstrip("\n")
                    match = LEVEL_RE.search(line)
                    level = match.group(1).upper() if match else "OTHER"
                    levels[level] += 1
                    total += 1
                    if args.level and level != args.level.upper():
                        continue
                    key = NORMALIZE_RE.sub("#", line)[:args.max_line]
                    patterns[key] += 1
        except FileNotFoundError:
            print(f"skip (not found): {path}", file=sys.stderr)

    print(f"\nLines analyzed: {total}")
    print("By level:", ", ".join(f"{k}={v}" for k, v in levels.most_common()))
    print(f"\nTop {args.top} patterns" + (f" (level {args.level.upper()})" if args.level else "") + ":")
    for pattern, count in patterns.most_common(args.top):
        print(f"  [{count:>6}x] {pattern}")

if __name__ == "__main__":
    main()
