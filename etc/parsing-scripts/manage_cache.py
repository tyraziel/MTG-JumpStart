#!/usr/bin/env python3
"""
Manage the card type cache (card_type_cache.json).

Usage:
    python manage_cache.py --list             # Show all Unknown entries
    python manage_cache.py --view             # Alias for --list
    python manage_cache.py --remove-unknowns  # Remove Unknown entries so they are retried
    python manage_cache.py                    # Show cache summary stats
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


def card_entries(data: dict) -> dict:
    return {k: v for k, v in data.items() if not k.startswith("_")}


def main():
    args = sys.argv[1:]
    do_list = "--list" in args or "--view" in args
    do_remove = "--remove-unknowns" in args

    if not args or (not do_list and not do_remove):
        # Default: summary stats
        data = load_cache()
        cards = card_entries(data)
        by_type: dict = {}
        for v in cards.values():
            t = v.get("type", "?") if isinstance(v, dict) else str(v)
            by_type[t] = by_type.get(t, 0) + 1
        print(f"Cache: {len(cards)} cards")
        for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
            print(f"  {t}: {count}")
        return 0

    data = load_cache()
    cards = card_entries(data)
    unknowns = {k: v for k, v in cards.items() if isinstance(v, dict) and v.get("type") == "Unknown"}

    if do_list:
        if not unknowns:
            print("No Unknown entries in cache.")
        else:
            print(f"{len(unknowns)} Unknown entries:")
            for name in sorted(unknowns):
                print(f"  {name}")

    if do_remove:
        if not unknowns:
            print("No Unknown entries to remove.")
            return 0
        cleaned = {k: v for k, v in data.items() if k not in unknowns}
        save_cache(cleaned)
        print(f"Removed {len(unknowns)} Unknown entries from cache.")
        for name in sorted(unknowns):
            print(f"  - {name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
