#!/usr/bin/env python3
"""csv_cleaner.py - Clean and normalize CSV files. Zero dependencies.

Usage:
    python csv_cleaner.py data.csv --strip --dedupe --out clean.csv
    python csv_cleaner.py data.csv --drop-empty-rows --delim ";"
"""
import argparse, csv, sys

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(newline="")  # avoid doubled CRLF on Windows
    ap = argparse.ArgumentParser(description="Clean/normalize a CSV file.")
    ap.add_argument("input")
    ap.add_argument("--out", help="output file (default: stdout)")
    ap.add_argument("--delim", default=",", help="delimiter (default: comma)")
    ap.add_argument("--strip", action="store_true", help="trim whitespace from every cell")
    ap.add_argument("--dedupe", action="store_true", help="drop duplicate rows")
    ap.add_argument("--drop-empty-rows", action="store_true")
    ap.add_argument("--fill-empty", default=None, help="replace empty cells with this value")
    args = ap.parse_args()

    out_fh = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
    seen, kept, dropped = set(), 0, 0

    with open(args.input, newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh, delimiter=args.delim)
        writer = csv.writer(out_fh, delimiter=args.delim)
        for row in reader:
            if args.strip:
                row = [cell.strip() for cell in row]
            if args.drop_empty_rows and all(cell == "" for cell in row):
                dropped += 1
                continue
            if args.fill_empty is not None:
                row = [cell if cell != "" else args.fill_empty for cell in row]
            if args.dedupe:
                key = tuple(row)
                if key in seen:
                    dropped += 1
                    continue
                seen.add(key)
            writer.writerow(row)
            kept += 1

    if args.out:
        out_fh.close()
        print(f"Wrote {kept} rows to {args.out} (dropped {dropped}).", file=sys.stderr)
    else:
        print(f"# kept {kept}, dropped {dropped}", file=sys.stderr)

if __name__ == "__main__":
    main()
