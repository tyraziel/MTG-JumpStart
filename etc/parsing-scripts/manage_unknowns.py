#!/usr/bin/env python3
"""
View and remove Unknown entries from the card type cache.

Cards cached as Unknown are ones that failed a Scryfall lookup (e.g. network
error, rate limit). They won't be retried unless removed from the cache first.

Usage:
    python manage_unknowns.py           # list Unknown entries (default)
    python manage_unknowns.py --list    # same as above
    python manage_unknowns.py --remove  # remove Unknown entries so they are retried
"""

import sys
import json
from pathlib import Path

cache_file = Path(__file__).parent / "card_type_cache.json"


def load_cache() -> dict:
    if not cache_file.exists():
        print(f"Cache file not found: {cache_file}", file=sys.stderr)
        sys.exit(1)
    with open(cache_file) as f:
        return json.load(f)


def save_cache(data: dict):
    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)


def get_unknowns(data: dict) -> dict:
    return {
        k: v for k, v in data.items()
        if not k.startswith("_") and isinstance(v, dict) and v.get("type") == "Unknown"
    }


def main():
    args = sys.argv[1:]
    do_remove = "--remove" in args

    data = load_cache()
    unknowns = get_unknowns(data)

    if not unknowns:
        print("No Unknown entries in cache.")
        return 0

    print(f"{len(unknowns)} Unknown entries:")
    for name in sorted(unknowns):
        print(f"  {name}")

    if do_remove:
        cleaned = {k: v for k, v in data.items() if k not in unknowns}
        save_cache(cleaned)
        print(f"\nRemoved {len(unknowns)} entries.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
