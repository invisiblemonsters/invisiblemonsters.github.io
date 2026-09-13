#!/usr/bin/env python3
"""api_client.py - Minimal REST client with retries, backoff, and simple pagination.

Usage:
    python api_client.py GET  https://api.example.com/items -H "Authorization: Bearer TOKEN"
    python api_client.py POST https://api.example.com/items --body '{"name": "demo"}'
    python api_client.py GET  https://api.example.com/items --page-param page --pages 5 --out all.json
"""
import argparse, json, sys, time, urllib.error, urllib.request

def do_request(method, url, headers, body, timeout, retries, backoff):
    data = body.encode("utf-8") if body else None
    last_error = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, method=method.upper())
        for key, value in headers.items():
            req.add_header(key, value)
        if data and "Content-Type" not in headers:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code < 500 and exc.code != 429:
                raise
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        if attempt < retries:
            wait = backoff * (2 ** attempt)
            print(f"retry {attempt + 1}/{retries} in {wait:.1f}s ({last_error})", file=sys.stderr)
            time.sleep(wait)
    raise last_error

def extract_list(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "items", "results", "records"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return None

def main():
    ap = argparse.ArgumentParser(description="REST client with retries + pagination.")
    ap.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    ap.add_argument("url")
    ap.add_argument("-H", "--header", action="append", default=[], help='header, e.g. -H "Authorization: Bearer x"')
    ap.add_argument("--body", help="request body (JSON string, or @path/to/file.json)")
    ap.add_argument("--out", help="save response body to this file")
    ap.add_argument("--timeout", type=float, default=30)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--backoff", type=float, default=1.0)
    ap.add_argument("--page-param", help="query param to paginate on, e.g. page")
    ap.add_argument("--start-page", type=int, default=1)
    ap.add_argument("--pages", type=int, default=1, help="number of pages to fetch (with --page-param)")
    args = ap.parse_args()

    headers = {}
    for item in args.header:
        if ":" in item:
            key, _, value = item.partition(":")
            headers[key.strip()] = value.strip()

    body = args.body
    if body and body.startswith("@"):
        body = open(body[1:], encoding="utf-8").read()

    if args.page_param and args.pages > 1:
        merged = []
        for offset in range(args.pages):
            page = args.start_page + offset
            sep = "&" if "?" in args.url else "?"
            page_url = f"{args.url}{sep}{args.page_param}={page}"
            status, text = do_request(args.method, page_url, headers, body, args.timeout, args.retries, args.backoff)
            print(f"page {page}: HTTP {status}", file=sys.stderr)
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                sys.exit(f"page {page} did not return JSON")
            chunk = extract_list(payload)
            if not chunk:
                break
            merged.extend(chunk)
        rendered = json.dumps(merged, indent=2, ensure_ascii=False)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(rendered)
            print(f"Saved {len(merged)} items to {args.out}")
        else:
            print(rendered[:4000])
    else:
        status, text = do_request(args.method, args.url, headers, body, args.timeout, args.retries, args.backoff)
        print(f"HTTP {status}")
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"Saved {len(text)} bytes to {args.out}")
        else:
            print(text[:4000])

if __name__ == "__main__":
    main()
