# Python Automation Scripts Bundle

10 zero-dependency Python scripts for scraping, file automation, API work, data
processing, and scheduling. Built for Python 3.8+. No `pip install` required —
everything uses the standard library only.

## What's inside

| Script | What it does |
|---|---|
| `scripts/web_scraper.py` | Fetch a page; extract title, text, and all links. Optional JSON export. |
| `scripts/bulk_rename.py` | Regex batch-rename files, with safe dry-run mode. |
| `scripts/file_organizer.py` | Sort loose files into subfolders by category or by date. |
| `scripts/duplicate_finder.py` | Find duplicate files by size + SHA-256; optionally delete extras. |
| `scripts/csv_cleaner.py` | Strip, dedupe, and normalize CSV rows. |
| `scripts/json_to_csv.py` | Flatten nested JSON into clean CSV (dot-notation columns). |
| `scripts/api_client.py` | REST client with retries, exponential backoff, and pagination merge. |
| `scripts/folder_watcher.py` | Watch a folder; move new files or run a command per file. |
| `scripts/backup_rotator.py` | Timestamped zip backups with automatic rotation. |
| `scripts/log_analyzer.py` | Log summaries: level counts + top repeated patterns. |

## Quick start

```bash
# Scrape a page and save structured output
python scripts/web_scraper.py https://example.com --links --save page.json

# Rename safely: preview first, apply second
python scripts/bulk_rename.py --dir ./photos --find "IMG_(\d+)" --replace "vacation_\1"
python scripts/bulk_rename.py --dir ./photos --find "IMG_(\d+)" --replace "vacation_\1" --apply

# Clean a spreadsheet export
python scripts/csv_cleaner.py orders.csv --strip --dedupe --out orders_clean.csv

# Back up a project, keep the last 7 zips
python scripts/backup_rotator.py create --dir ./myproject --dest ./backups --keep 7
```

Every script supports `--help` with full usage notes.

## Safety notes

- Scripts that modify files (`bulk_rename`, `file_organizer`, `duplicate_finder`) default to
  **preview/dry-run mode**. Nothing moves or deletes until you pass `--apply` / `--delete`.
- `folder_watcher --on-new` runs shell commands from the string you provide — treat it like
  any shell script and review the command before running.

## License

Purchaser may use these scripts in personal and commercial projects (including client work).
Redistribution or resale of the bundle itself is not permitted.

## Support

Something not working? Email the address you received the product from with your
transaction hash — fixes are free, forever.
