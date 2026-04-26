#!/usr/bin/env python3
"""
update_token_keywords.py - Add keywords and oracle_id to cached token data.

Finds all cards in the cache that have tokens missing the 'keywords' field,
re-queries Scryfall for each card to retrieve token URIs from all_parts, then
fetches each token URI for keywords and oracle_id. Safe to run multiple times
— skips tokens that already have the 'keywords' field set.

After running, regenerate deck JSONs with:
    python generate_json_decks.py ../JMP/ ../J22/ ../J25/ ../TLA/ ...
And regenerate the combined JSON with:
    python generate_combined_json.py

Usage:
    python update_token_keywords.py [options]

Options:
    --delay MS    Milliseconds between Scryfall API calls (default: 250)
    --dry-run     Show what would be updated without modifying the cache
    --limit N     Only process first N cards needing update (for testing)
    --verbose     Print each token even when no keywords found

Examples:
    python update_token_keywords.py
    python update_token_keywords.py --limit 20 --verbose
    python update_token_keywords.py --dry-run
"""

import json
import sys
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional

CACHE_FILE = Path(__file__).parent / "card_type_cache.json"
SCRYFALL_NAMED = "https://api.scryfall.com/cards/named"

# 250ms default — well within Scryfall's guidelines
REQUEST_DELAY = 250 / 1000

# In-memory cache keyed by token URI to avoid re-fetching the same token
# across multiple cards (e.g. many cards create "Soldier" tokens)
token_uri_cache: Dict[str, Dict] = {}


def fetch_token_by_uri(uri: str) -> Optional[Dict]:
    """
    Fetch a token card from Scryfall by URI and extract relevant fields.
    Results cached in token_uri_cache to avoid duplicate requests.
    Returns None on failure.
    """
    if uri in token_uri_cache:
        return token_uri_cache[uri]

    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(uri, timeout=10)
        response.raise_for_status()
        data = response.json()

        details: Dict = {
            "colors": data.get("colors", []),
            "keywords": data.get("keywords", []),
        }
        if data.get("power") is not None:
            details["power"] = data["power"]
        if data.get("toughness") is not None:
            details["toughness"] = data["toughness"]
        if data.get("oracle_id"):
            details["oracle_id"] = data["oracle_id"]

        token_uri_cache[uri] = details
        return details

    except requests.exceptions.RequestException as e:
        print(f"    ✗ Error fetching token {uri}: {e}", file=sys.stderr)
        token_uri_cache[uri] = None
        return None


def fetch_card_token_parts(card_name: str) -> Optional[List[Dict]]:
    """
    Query Scryfall for a card and return token entries from all_parts,
    each with uri, name, and type_line. Returns None on API failure.
    """
    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(SCRYFALL_NAMED, params={"exact": card_name}, timeout=10)
        response.raise_for_status()
        data = response.json()

        return [
            {
                "name": part.get("name", ""),
                "type_line": part.get("type_line", ""),
                "uri": part.get("uri", ""),
            }
            for part in data.get("all_parts", [])
            if part.get("component") == "token"
        ]

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching {card_name}: {e}", file=sys.stderr)
        return None


def needs_keyword_update(tokens: List[Dict]) -> bool:
    """Return True if any token in the list is missing the 'keywords' field."""
    return any("keywords" not in t for t in tokens)


def main():
    global REQUEST_DELAY

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
                print(f"Error: --delay requires an integer (ms), got '{args[i+1]}'", file=sys.stderr)
                return 1
            i += 2
        else:
            i += 1

    if delay_ms is not None:
        REQUEST_DELAY = delay_ms / 1000
        print(f"Scryfall delay: {delay_ms}ms")
    else:
        print(f"Scryfall delay: {int(REQUEST_DELAY * 1000)}ms (default)")

    if dry_run:
        print("DRY RUN — cache will not be modified\n")

    if not CACHE_FILE.exists():
        print(f"Error: Cache file not found: {CACHE_FILE}", file=sys.stderr)
        return 1

    with open(CACHE_FILE) as f:
        cache_data = json.load(f)

    meta = {k: v for k, v in cache_data.items() if k.startswith("_")}
    cache = {k: v for k, v in cache_data.items() if not k.startswith("_")}

    # Find cards that have tokens and at least one token missing 'keywords'
    needs_update = [
        name for name, data in cache.items()
        if isinstance(data, dict)
        and data.get("tokens")
        and needs_keyword_update(data["tokens"])
    ]

    already_done = sum(
        1 for data in cache.values()
        if isinstance(data, dict) and data.get("tokens")
        and not needs_keyword_update(data["tokens"])
    )

    print(f"Cards with tokens:        {len(needs_update) + already_done}")
    print(f"  Already have keywords:  {already_done}")
    print(f"  Need keyword update:    {len(needs_update)}")

    if not needs_update:
        print("\nAll token entries already have keywords. Nothing to do.")
        return 0

    if limit:
        needs_update = needs_update[:limit]
        print(f"  Processing first {limit} (--limit)\n")
    else:
        print()

    est_seconds = len(needs_update) * REQUEST_DELAY * 2  # ~2 calls per card
    print(f"Estimated time: ~{est_seconds / 60:.0f} min ({int(REQUEST_DELAY * 1000)}ms/call, ~2 calls/card avg)\n")

    updated_cards = 0
    updated_tokens = 0
    api_errors = 0

    for idx, card_name in enumerate(needs_update, 1):
        print(f"[{idx}/{len(needs_update)}] {card_name}")

        token_parts = fetch_card_token_parts(card_name)
        if token_parts is None:
            print(f"  ✗ API error — will retry on next run")
            api_errors += 1
            continue

        # Build a URI map from token name for matching
        uri_map = {p["name"]: p["uri"] for p in token_parts if p["uri"]}

        card_updated = False
        for token in cache[card_name]["tokens"]:
            if "keywords" in token:
                continue  # already done

            token_name = token["name"]
            uri = uri_map.get(token_name, "")

            if not uri:
                # URI not found in all_parts — mark as empty to avoid retrying
                token["keywords"] = []
                if verbose:
                    print(f"  {token_name}: no URI found, keywords=[]")
                card_updated = True
                continue

            details = fetch_token_by_uri(uri)
            if details is None:
                api_errors += 1
                continue

            token["keywords"] = details.get("keywords", [])
            if details.get("oracle_id") and "oracle_id" not in token:
                token["oracle_id"] = details["oracle_id"]
            # Backfill other fields if missing
            if "colors" not in token:
                token["colors"] = details.get("colors", [])
            if details.get("power") and "power" not in token:
                token["power"] = details["power"]
            if details.get("toughness") and "toughness" not in token:
                token["toughness"] = details["toughness"]

            kw_str = f"[{', '.join(token['keywords'])}]" if token["keywords"] else "(no keywords)"
            print(f"  {token_name}: keywords={kw_str}")
            card_updated = True
            updated_tokens += 1

        if card_updated:
            updated_cards += 1

        # Incremental save every 25 updated cards
        if not dry_run and updated_cards > 0 and updated_cards % 25 == 0:
            _save_cache(meta, cache)
            print(f"  [checkpoint] Saved ({updated_cards} cards updated so far)")

    if not dry_run and updated_cards > 0:
        _save_cache(meta, cache)
        print(f"\nSaved cache.")

    print(f"\nDone.")
    print(f"  Cards updated:   {updated_cards}")
    print(f"  Tokens updated:  {updated_tokens}")
    print(f"  API errors:      {api_errors}")
    if dry_run:
        print("  (dry run — nothing written)")

    return 0


def _save_cache(meta: Dict, cache: Dict):
    output = dict(meta)
    output["_cache_version"] = "2.1"
    output["_fields"] = "type, type_line, mana_cost, cmc, colors, power, toughness, rarity, tokens, skip_reason(optional)"
    for name in sorted(cache.keys()):
        output[name] = cache[name]
    temp = CACHE_FILE.with_suffix(".json.tmp")
    with open(temp, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    temp.replace(CACHE_FILE)


if __name__ == "__main__":
    sys.exit(main())
