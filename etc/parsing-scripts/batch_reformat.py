#!/usr/bin/env python3
"""
Batch reformat JumpStart deck lists to standard format with card type organization.

This script processes multiple deck files in one run, maintaining a shared cache
across all decks to minimize Scryfall API calls.

Usage:
    # Build cache only (no reformatting):
    python batch_reformat.py etc/J25/ etc/TLA/ etc/J22/ --build-cache-only --save-cache

    # Reformat using existing cache:
    python batch_reformat.py etc/J25/ --load-cache

    # Both at once:
    python batch_reformat.py etc/J25/ --save-cache

Options:
    --build-cache-only  Build/rebuild cache from deck files without reformatting
    --dry-run           Preview changes without modifying files
    --save-cache        Save card data cache to disk after processing
    --load-cache        Load existing cache from disk before processing
"""

import sys
import time
import re
import json
import requests
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Scryfall API endpoint
SCRYFALL_API = "https://api.scryfall.com/cards/named"

# Rate limiting: Match Discord bot's rate limiting: 100ms
REQUEST_DELAY = 100 / 1000  # 100ms between requests

# Card type categories in order
TYPE_ORDER = [
    "Creatures",
    "Sorceries",
    "Instants",
    "Artifacts",
    "Enchantments",
    "Planeswalkers",
    "Lands"
]

# Cache for card data (shared across all decks)
# Structure: { "Card Name": { "type": "Creatures", "mana_cost": "{1}{U}{U}", ... } }
card_cache: Dict[str, Dict] = {}
cache_file = Path(__file__).parent / "card_type_cache.json"


def load_cache_from_disk():
    """Load card data cache from disk if it exists."""
    global card_cache
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)

        # Filter out comment fields that start with underscore
        card_cache = {k: v for k, v in cache_data.items() if not k.startswith('_')}

        # Handle legacy cache format (string values instead of objects)
        for card_name, card_data in list(card_cache.items()):
            if isinstance(card_data, str):
                # Legacy format: convert to new object format
                card_cache[card_name] = {"type": card_data}

        print(f"Loaded {len(card_cache)} cards from cache file", file=sys.stderr)


def save_cache_to_disk(verbose: bool = True):
    """
    Save card data cache to disk for future runs.

    Args:
        verbose: If True, print save confirmation (default: True)
    """
    # Add attribution at the top
    output_cache = {
        "_comment": "Card data derived from Scryfall API (https://scryfall.com). Contains type categories and gameplay data for deck formatting and Discord display. Not affiliated with or endorsed by Scryfall.",
        "_scryfall_api": "https://scryfall.com/docs/api",
        "_license": "Data extracted from Scryfall under their API terms of service",
        "_cache_version": "2.0",
        "_fields": "type, type_line, mana_cost, cmc, colors, power, toughness, rarity"
    }

    # Add card data (sorted for consistency)
    for card_name in sorted(card_cache.keys()):
        output_cache[card_name] = card_cache[card_name]

    # Write atomically by writing to temp file first, then renaming
    temp_file = cache_file.with_suffix('.json.tmp')
    with open(temp_file, 'w') as f:
        json.dump(output_cache, f, indent=2, sort_keys=False)

    # Atomic rename
    temp_file.replace(cache_file)

    if verbose:
        print(f"💾 Saved {len(card_cache)} cards to cache file: {cache_file}", file=sys.stderr)


def normalize_basic_land(card_name: str) -> str:
    """
    Normalize special basic land variants to standard names.

    Examples:
        "Above the Clouds Island" -> "Island"
        "Full-art stained-glass Plains" -> "Plains"
        "Traditional foil Mountain" -> "Mountain"
        "Thriving Isle" -> "Thriving Isle" (not a basic land)
        "Tropical Island" -> "Tropical Island" (dual land, keep as-is)
    """
    basic_lands = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest']

    # Exact match - already a basic land
    if card_name in basic_lands:
        return card_name

    # Known dual lands and special lands (NOT basic land variants)
    dual_lands = {
        'Tropical Island', 'Volcanic Island', 'Underground Sea', 'Badlands', 'Bayou',
        'Plateau', 'Savannah', 'Scrubland', 'Taiga', 'Tundra',
        'Thriving Isle', 'Thriving Heath', 'Thriving Bluff', 'Thriving Moor', 'Thriving Grove'
    }

    if card_name in dual_lands:
        return card_name

    # Known prefixes for special basic land variants
    special_prefixes = [
        'Full-art stained-glass',
        'Traditional foil',
        'Snow-Covered'
    ]

    # Check for known special prefixes
    for prefix in special_prefixes:
        for basic in basic_lands:
            if card_name == f"{prefix} {basic}":
                return basic

    # Check if it matches pattern "[Theme Name] [Basic Land]"
    # This handles JumpStart special basics like "Above the Clouds Island"
    for basic in basic_lands:
        if card_name.endswith(f" {basic}"):
            # It's a JumpStart theme basic land variant
            return basic

    return card_name


def parse_card_line(line: str) -> Tuple[int, str, str]:
    """
    Parse a card line to extract quantity, card name, and any suffix (like IDs).

    Examples:
        "1 Vendilion Clique" -> (1, "Vendilion Clique", "")
        "Aang, Airbending Master" -> (1, "Aang, Airbending Master", "")
        "6 Plains [abc123]" -> (6, "Plains", "[abc123]")
        "1 Above the Clouds Island" -> (1, "Island", "")

    Returns:
        (quantity, card_name, suffix)
    """
    line = line.strip()
    if not line:
        return (0, "", "")

    # Check for special suffixes in brackets
    suffix = ""
    if "[" in line and "]" in line:
        match = re.search(r'\[(.*?)\]', line)
        if match:
            suffix = f"[{match.group(1)}]"
            line = line[:match.start()].strip()

    # Try to parse quantity
    parts = line.split(None, 1)
    if len(parts) == 2 and parts[0].isdigit():
        quantity = int(parts[0])
        card_name = parts[1].strip()
    else:
        quantity = 1
        card_name = line.strip()

    # Normalize basic land variants
    card_name = normalize_basic_land(card_name)

    return (quantity, card_name, suffix)


def classify_card_type(type_line: str) -> str:
    """
    Classify a card based on its type_line.

    Multi-type cards use rightmost type for primary classification:
    - "Artifact Creature" -> Creatures
    - "Enchantment Creature" -> Creatures
    - "Legendary Creature" -> Creatures
    """
    type_line_lower = type_line.lower()

    # Check in order of specificity (more specific first)
    if "creature" in type_line_lower:
        return "Creatures"
    elif "planeswalker" in type_line_lower:
        return "Planeswalkers"
    elif "sorcery" in type_line_lower:
        return "Sorceries"
    elif "instant" in type_line_lower:
        return "Instants"
    elif "artifact" in type_line_lower:
        return "Artifacts"
    elif "enchantment" in type_line_lower:
        return "Enchantments"
    elif "land" in type_line_lower:
        return "Lands"
    else:
        return "Unknown"


def get_card_data(card_name: str) -> Dict:
    """
    Query Scryfall API for card information and cache comprehensive data.

    Returns a dict with card data including:
    - type: Primary type category (Creatures, Instants, etc.)
    - type_line: Full type line from Scryfall
    - mana_cost: Mana cost string (e.g., "{1}{U}{U}")
    - cmc: Converted mana cost / mana value
    - colors: Array of color letters (e.g., ["U", "B"])
    - power: Power value (for creatures)
    - toughness: Toughness value (for creatures)
    - rarity: Rarity (common, uncommon, rare, mythic)
    """
    # Check cache first
    if card_name in card_cache:
        return card_cache[card_name]

    # Skip special placeholder cards
    # Matches: "Random white rare or mythic rare", "Rare or mythic rare", etc.
    card_lower = card_name.lower()
    if ("rare" in card_lower and "mythic" in card_lower) or ("rare" in card_lower and "random" in card_lower):
        card_data = {"type": "Special"}
        card_cache[card_name] = card_data
        return card_data

    # Query Scryfall
    try:
        time.sleep(REQUEST_DELAY)  # Rate limiting
        response = requests.get(SCRYFALL_API, params={"exact": card_name}, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract relevant fields
        type_line = data.get("type_line", "")
        card_type = classify_card_type(type_line)

        card_data = {
            "type": card_type,
            "type_line": type_line,
            "mana_cost": data.get("mana_cost", ""),
            "cmc": data.get("cmc", 0),
            "colors": data.get("colors", []),
            "rarity": data.get("rarity", "common")
        }

        # Add creature-specific fields
        if card_type == "Creatures":
            card_data["power"] = data.get("power")
            card_data["toughness"] = data.get("toughness")

        # Add planeswalker-specific fields
        if card_type == "Planeswalkers":
            card_data["loyalty"] = data.get("loyalty")

        card_cache[card_name] = card_data

        print(f"✓ {card_name}: {type_line} -> {card_type}", file=sys.stderr)
        return card_data

    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching {card_name}: {e}", file=sys.stderr)
        card_data = {"type": "Unknown"}
        card_cache[card_name] = card_data
        return card_data


def get_card_type(card_name: str) -> str:
    """
    Get just the card type category for a card.

    This is a convenience wrapper around get_card_data() for backward compatibility.
    """
    card_data = get_card_data(card_name)
    return card_data.get("type", "Unknown")


def reformat_deck(input_file: Path, dry_run: bool = False) -> bool:
    """
    Reformat a deck list from unformatted to standard format.

    Returns True if file was modified, False otherwise.
    """
    # Read input file
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Deck name from filename (without .txt extension)
    deck_name = input_file.stem

    # Parse cards
    cards_by_type = defaultdict(list)

    # Skip first line if it matches the deck name (already formatted files)
    start_line = 0
    if lines and lines[0].strip() == deck_name:
        start_line = 1

    for line in lines[start_line:]:
        # Skip comment lines (card type headers like //Creatures (X))
        if not line.strip().startswith('//'):
            quantity, card_name, suffix = parse_card_line(line)

            if card_name:
                card_type = get_card_type(card_name)
                # Format card line
                card_line = f"{quantity} {card_name}"
                if suffix:
                    card_line += f" {suffix}"

                # Store as tuple: (quantity, card_line)
                cards_by_type[card_type].append((quantity, card_line))

    # Build output
    output_lines = [deck_name]

    for type_name in TYPE_ORDER:
        if type_name in cards_by_type and cards_by_type[type_name]:
            # Calculate total quantity (sum of all card quantities in this type)
            total_quantity = sum(qty for qty, _ in cards_by_type[type_name])
            output_lines.append(f"//{type_name} ({total_quantity})")
            # Add just the card lines (without quantity from tuple)
            output_lines.extend(card_line for _, card_line in cards_by_type[type_name])

    # Add any unknown or special cards at the end
    for type_name in ["Special", "Unknown"]:
        if type_name in cards_by_type and cards_by_type[type_name]:
            output_lines.append(f"//{type_name}")
            output_lines.extend(card_line for _, card_line in cards_by_type[type_name])

    # Check if file would change
    output_text = "\n".join(output_lines) + "\n"
    original_text = "".join(lines)

    if output_text == original_text:
        return False  # No changes needed

    # Write output
    if not dry_run:
        with open(input_file, 'w') as f:
            f.write(output_text)

    return True


def build_cache_from_directory(directory: Path, save_incrementally: bool = True):
    """
    Build cache by scanning all cards in deck files without reformatting.

    Args:
        directory: Directory containing deck files
        save_incrementally: If True, save cache after each deck (default: True)
    """
    deck_files = sorted(directory.glob("*.txt"))

    if not deck_files:
        print(f"No .txt files found in {directory}", file=sys.stderr)
        return

    set_name = directory.name
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"SET: {set_name} - Scanning {len(deck_files)} decks", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    for idx, deck_file in enumerate(deck_files, 1):
        try:
            deck_name = deck_file.stem
            print(f"\n[{set_name}] Deck {idx}/{len(deck_files)}: {deck_name}", file=sys.stderr)

            with open(deck_file, 'r') as f:
                lines = f.readlines()

            # Count unique cards in this deck for progress
            cards_in_deck = []
            for line in lines[1:]:
                if not line.strip().startswith('//'):
                    _, card_name, _ = parse_card_line(line)
                    if card_name and card_name not in cards_in_deck:
                        cards_in_deck.append(card_name)

            # Process each unique card
            for card_idx, card_name in enumerate(cards_in_deck, 1):
                # This will query and cache the card
                get_card_data(card_name)
                print(f"  [{card_idx}/{len(cards_in_deck)}] Cached: {card_name}", file=sys.stderr)

            # Save cache after each deck to avoid losing progress
            if save_incrementally:
                save_cache_to_disk()
                print(f"  ✓ Cache saved ({len(card_cache)} total cards)", file=sys.stderr)

        except Exception as e:
            print(f"  ✗ ERROR scanning {deck_file.name}: {e}", file=sys.stderr)

    print(f"\n{set_name}: Completed {len(deck_files)} decks", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)


def process_directory(directory: Path, dry_run: bool = False, save_incrementally: bool = False):
    """
    Process all .txt files in a directory.

    Args:
        directory: Directory containing deck files
        dry_run: If True, don't modify files
        save_incrementally: If True, save cache after each deck
    """
    deck_files = sorted(directory.glob("*.txt"))

    if not deck_files:
        print(f"No .txt files found in {directory}", file=sys.stderr)
        return

    set_name = directory.name
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"SET: {set_name} - Processing {len(deck_files)} decks", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    modified_count = 0
    for idx, deck_file in enumerate(deck_files, 1):
        try:
            deck_name = deck_file.stem
            print(f"\n[{set_name}] Deck {idx}/{len(deck_files)}: {deck_name}", file=sys.stderr)

            if reformat_deck(deck_file, dry_run):
                modified_count += 1
                status = "[DRY RUN] Would modify" if dry_run else "Modified"
                print(f"  ✓ {status}", file=sys.stderr)
            else:
                print(f"  - No changes needed", file=sys.stderr)

            # Save cache incrementally if requested
            if save_incrementally and not dry_run:
                save_cache_to_disk()
                print(f"  ✓ Cache saved ({len(card_cache)} total cards)", file=sys.stderr)

        except Exception as e:
            print(f"  ✗ ERROR processing {deck_file.name}: {e}", file=sys.stderr)

    print(f"\n{set_name}: {modified_count}/{len(deck_files)} files {'would be ' if dry_run else ''}modified", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)


def main():
    # Parse arguments
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
    dry_run = "--dry-run" in sys.argv
    save_cache = "--save-cache" in sys.argv
    load_cache = "--load-cache" in sys.argv
    build_cache_only = "--build-cache-only" in sys.argv

    if not args:
        print("Usage: python batch_reformat.py <directory> [<directory>...] [options]", file=sys.stderr)
        print("\nOptions:", file=sys.stderr)
        print("  --build-cache-only  Build cache without reformatting files", file=sys.stderr)
        print("  --dry-run           Preview changes without modifying files", file=sys.stderr)
        print("  --save-cache        Save cache to disk after processing", file=sys.stderr)
        print("  --load-cache        Load existing cache before processing", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  # Build cache from all decks:", file=sys.stderr)
        print("  python batch_reformat.py ../../etc/*/ --build-cache-only --save-cache", file=sys.stderr)
        print("\n  # Reformat using cache:", file=sys.stderr)
        print("  python batch_reformat.py ../../etc/J25/ --load-cache", file=sys.stderr)
        return 1

    if build_cache_only:
        print("=== CACHE BUILD MODE - Files will not be reformatted ===\n", file=sys.stderr)
    elif dry_run:
        print("=== DRY RUN MODE - No files will be changed ===\n", file=sys.stderr)

    # Load cache if requested
    if load_cache:
        load_cache_from_disk()

    # Process each directory
    for dir_path in args:
        directory = Path(dir_path)
        if not directory.exists():
            print(f"Directory not found: {directory}", file=sys.stderr)
            continue

        if not directory.is_dir():
            print(f"Not a directory: {directory}", file=sys.stderr)
            continue

        if build_cache_only:
            # Cache building saves incrementally if --save-cache requested
            build_cache_from_directory(directory, save_incrementally=save_cache)
        else:
            # Reformatting also saves incrementally if --save-cache requested
            process_directory(directory, dry_run, save_incrementally=save_cache)

    # No final save needed - incremental saves already wrote everything when --save-cache was passed
    # If --save-cache wasn't passed, we didn't save anything (and that's intentional)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"✓ COMPLETE! Cache contains {len(card_cache)} unique cards", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
