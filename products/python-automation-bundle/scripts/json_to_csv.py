#!/usr/bin/env python3
"""json_to_csv.py - Flatten a JSON array of objects into CSV (dot-notation keys for nesting).

Usage:
    python json_to_csv.py data.json --out data.csv
    python json_to_csv.py data.json            # print to stdout
"""
import argparse, csv, json, sys

def flatten(value, prefix="", out=None):
    out = {} if out is None else out
    if isinstance(value, dict):
        for key, child in value.items():
            flatten(child, prefix + str(key) + ".", out)
    elif isinstance(value, list):
        out[prefix[:-1] or "value"] = json.dumps(value, ensure_ascii=False)
    else:
        out[prefix[:-1] or "value"] = value
    return out

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(newline="")  # avoid doubled CRLF on Windows
    ap = argparse.ArgumentParser(description="Flatten JSON (array of objects) into CSV.")
    ap.add_argument("input")
    ap.add_argument("--out", help="output CSV (default: stdout)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        sys.exit("Input must be a JSON array of objects (or a single object).")

    rows = [flatten(item) for item in data]
    columns = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)

    out_fh = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
    writer = csv.DictWriter(out_fh, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    if args.out:
        out_fh.close()
        print(f"Wrote {len(rows)} rows x {len(columns)} columns to {args.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
