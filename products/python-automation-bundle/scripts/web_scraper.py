#!/usr/bin/env python3
"""web_scraper.py - Fetch a web page and extract its title, text, and links.

Zero dependencies. Usage:
    python web_scraper.py https://example.com
    python web_scraper.py https://example.com --links --save page.json
"""
import argparse, json, re, urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

class Extractor(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.in_title = False
        self.title_parts, self.text_parts, self.links = [], [], []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip_depth += 1
        elif tag == "title":
            self.in_title = True
        elif tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(urljoin(self.base_url, href))

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip_depth:
            self.skip_depth -= 1
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.skip_depth:
            return
        (self.title_parts if self.in_title else self.text_parts).append(data)

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (scraper/1.0)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")

def main():
    ap = argparse.ArgumentParser(description="Extract title/text/links from a web page.")
    ap.add_argument("url")
    ap.add_argument("--links", action="store_true", help="print all extracted links")
    ap.add_argument("--save", metavar="FILE", help="write results to a JSON file")
    args = ap.parse_args()

    parser = Extractor(args.url)
    parser.feed(fetch(args.url))
    text = re.sub(r"\s+", " ", " ".join(parser.text_parts)).strip()

    result = {
        "url": args.url,
        "title": " ".join(parser.title_parts).strip(),
        "text": text,
        "links": parser.links,
    }
    print("TITLE:", result["title"])
    print("TEXT:", text[:600] + ("..." if len(text) > 600 else ""))
    if args.links:
        print("\nLINKS:")
        for link in parser.links[:200]:
            print(" -", link)
    if args.save:
        with open(args.save, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
        print("\nSaved ->", args.save)

if __name__ == "__main__":
    main()
