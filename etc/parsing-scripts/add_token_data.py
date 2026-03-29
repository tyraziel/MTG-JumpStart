#!/usr/bin/env python3
"""
add_token_data.py - Backfill token data into the card type cache.

Scans card_type_cache.json for any card missing the 'tokens' key and
re-queries Scryfall to fetch token data from all_parts. Safe to run
multiple times — skips cards that already have a 'tokens' key (even if
that key is an empty list, which means "confirmed no tokens").

After running this script, regenerate deck JSON files with:
    python generate_json_decks.py ../JMP/ ../J22/ ../J25/ ../TLA/ ...

Usage:
    python add_token_data.py [options]

Options:
    --delay MS    Milliseconds between Scryfall API calls (default: 250)
    --dry-run     Show what would be updated without modifying the cache
    --limit N     Only process first N uncached cards (useful for testing)
    --verbose     Print each card even if it has no tokens

Examples:
    # Backfill all missing cards with default 250ms delay
    python add_token_data.py

    # Test with first 10 cards at 500ms delay
    python add_token_data.py --limit 10 --delay 500

    # Preview without making changes
    python add_token_data.py --dry-run --limit 20
"""

import json
import sys
import time
import requests
from pathlib import Path
from typing import Dict, List

# Cache file location (same directory as this script)
CACHE_FILE = Path(__file__).parent / "card_type_cache.json"

# Default rate limit — 250ms between Scryfall API requests.
# Scryfall asks for 50-100ms minimum; 250ms gives comfortable headroom.
REQUEST_DELAY = 250 / 1000

# In-memory cache for token details, keyed by Scryfall URI.
# Prevents fetching the same token more than once per run.
token_detail_cache: Dict[str, Dict] = {}


def fetch_token_details(token_uri: str) -> Dict:
    """
    Fetch P/T and colors for a token from Scryfall using its card URI.

    Cached by URI so each unique token is only fetched once per run,
    even if multiple cards in the set create the same token type.

    Returns a dict with: colors, power (optional), toughness (optional).
    Returns {} on any failure so callers can proceed without crashing.
    """
    if token_uri in token_detail_cache:
        return token_detail_cache[token_uri]

    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(token_uri, timeout=10)
        response.raise_for_status()
        data = response.json()

        details: Dict = {"colors": data.get("colors", [])}
        if data.get("power") is not None:
            details["power"] = data["power"]
        if data.get("toughness") is not None:
            details["toughness"] = data["toughness"]

        token_detail_cache[token_uri] = details
        return details

    except requests.exceptions.RequestException as e:
        print(f"    ✗ Error fetching token {token_uri}: {e}", file=sys.stderr)
        token_detail_cache[token_uri] = {}
        return {}


def fetch_card_tokens(card_name: str) -> List[Dict]:
    """
    Query Scryfall for a card and extract tokens from all_parts.

    Returns a list of token dicts (may be empty if card creates no tokens).
    Returns None on API failure so the caller can skip updating the entry.
    """
    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(
            "https://api.scryfall.com/cards/named",
            params={"exact": card_name},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        tokens = []
        for part in data.get("all_parts", []):
            if part.get("component") == "token":
                token_info: Dict = {
                    "name": part.get("name", ""),
                    "type_line": part.get("type_line", ""),
                }
                token_uri = part.get("uri", "")
                if token_uri:
                    details = fetch_token_details(token_uri)
                    if details.get("colors") is not None:
                        token_info["colors"] = details["colors"]
                    if details.get("power") is not None:
                        token_info["power"] = details["power"]
                    if details.get("toughness") is not None:
                        token_info["toughness"] = details["toughness"]
                tokens.append(token_info)

        return tokens

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching {card_name}: {e}", file=sys.stderr)
        return None


def main():
    global REQUEST_DELAY

    # Parse CLI args
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    verbose = "--verbose" in args
    limit = None
    delay_ms = None

    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                print(f"Error: --limit requires an integer, got '{args[i+1]}'", file=sys.stderr)
                return 1
            i += 2
        elif args[i] == "--delay" and i + 1 < len(args):
            try:
                delay_ms = int(args[i + 1])
            except ValueError:
                print(f"Error: --delay requires an integer (milliseconds), got '{args[i+1]}'", file=sys.stderr)
                return 1
            i += 2
        else:
            i += 1

    if delay_ms is not None:
        REQUEST_DELAY = delay_ms / 1000
        print(f"Scryfall delay: {delay_ms}ms between requests")
    else:
        print(f"Scryfall delay: {int(REQUEST_DELAY * 1000)}ms between requests (default)")

    if dry_run:
        print("DRY RUN — cache will not be modified\n")

    # Load cache
    if not CACHE_FILE.exists():
        print(f"Error: Cache file not found: {CACHE_FILE}", file=sys.stderr)
        return 1

    with open(CACHE_FILE) as f:
        cache_data = json.load(f)

    # Separate metadata from card entries
    meta = {k: v for k, v in cache_data.items() if k.startswith("_")}
    cache = {k: v for k, v in cache_data.items() if not k.startswith("_")}

    # Separate cards into: skip (have skip_reason), needs_update (missing tokens key)
    skip_entries = [(name, data) for name, data in cache.items()
                    if isinstance(data, dict) and "skip_reason" in data]
    needs_update = [name for name, data in cache.items()
                    if isinstance(data, dict) and "tokens" not in data
                    and "skip_reason" not in data]

    total = len(needs_update)
    already_done = len(cache) - total - len(skip_entries)
    print(f"Cache: {len(cache)} cards total")
    print(f"  Already have token data: {already_done}")
    print(f"  Skipped (skip_reason):   {len(skip_entries)}")
    print(f"  Need token data:         {total}")

    if verbose and skip_entries:
        print("\n  Skipped entries:")
        for name, data in sorted(skip_entries):
            print(f"    [skip:{data['skip_reason']}] {name}")

    if total == 0:
        print("\nAll cards already have token data. Nothing to do.")
        return 0

    if limit:
        needs_update = needs_update[:limit]
        print(f"  Processing first {limit} (--limit)\n")
    else:
        print()

    # Estimate time
    # Each card = 1 API call + potentially N token detail calls
    # Rough estimate: 1.5 calls per card on average
    est_seconds = total * REQUEST_DELAY * 1.5
    est_minutes = est_seconds / 60
    print(f"Estimated time for all {total} cards: ~{est_minutes:.0f} min "
          f"({int(REQUEST_DELAY * 1000)}ms/call, ~1.5 calls/card avg)\n")

    # Process cards
    updated = 0
    skipped = 0
    tokens_found_count = 0

    for idx, card_name in enumerate(needs_update, 1):
        print(f"[{idx}/{len(needs_update)}] {card_name}", end="", flush=True)

        tokens = fetch_card_tokens(card_name)

        if tokens is None:
            # API failure — leave key absent so it can be retried next run
            print(f"  ✗ API error — will retry on next run")
            skipped += 1
            continue

        token_note = f"  → {len(tokens)} token(s): {[t['name'] for t in tokens]}" if tokens else ""
        if tokens or verbose:
            print(token_note or "  (no tokens)")
        else:
            print()  # newline

        if not dry_run:
            cache[card_name]["tokens"] = tokens
            updated += 1
            if tokens:
                tokens_found_count += 1

            # Save incrementally every 25 cards to preserve progress
            if updated % 25 == 0:
                _save_cache(meta, cache)
                print(f"  [checkpoint] Saved cache ({updated} updated so far)")

    # Final save
    if not dry_run and updated > 0:
        _save_cache(meta, cache)
        print(f"\nSaved cache with {updated} updated entries.")

    print(f"\nDone.")
    print(f"  Updated:      {updated}")
    print(f"  With tokens:  {tokens_found_count}")
    print(f"  API errors:   {skipped} (will retry on next run)")
    print(f"  Skipped:      {len(skip_entries)} (have skip_reason — use --verbose to list)")
    if dry_run:
        print("  (dry run — nothing written)")

    return 0


def _save_cache(meta: Dict, cache: Dict):
    """Write updated cache atomically."""
    # Update version/fields metadata
    output = dict(meta)
    output["_cache_version"] = "2.1"
    output["_fields"] = "type, type_line, mana_cost, cmc, colors, power, toughness, rarity, tokens"
    for name in sorted(cache.keys()):
        output[name] = cache[name]

    temp = CACHE_FILE.with_suffix(".json.tmp")
    with open(temp, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    temp.replace(CACHE_FILE)


if __name__ == "__main__":
    sys.exit(main())
