#!/usr/bin/env python3
"""
Batch reformat JumpStart deck lists to standard format with card type organization.

This script processes multiple deck files in one run, maintaining a shared cache
across all decks to minimize Scryfall API calls.

Usage:
    python batch_reformat.py etc/J25/ [--dry-run] [--save-cache]
    python batch_reformat.py etc/TLA/ etc/J25/ [--dry-run]

Options:
    --dry-run       Preview changes without modifying files
    --save-cache    Save card type cache to disk for future runs
    --load-cache    Load existing cache from disk before processing
"""

import sys
import time
import re
import json
import requests
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

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

# Cache for card type lookups (shared across all decks)
card_cache: Dict[str, str] = {}
cache_file = Path(__file__).parent / "card_type_cache.json"


def load_cache_from_disk():
    """Load card type cache from disk if it exists."""
    global card_cache
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            card_cache = json.load(f)
        print(f"Loaded {len(card_cache)} cards from cache file", file=sys.stderr)


def save_cache_to_disk():
    """Save card type cache to disk for future runs."""
    with open(cache_file, 'w') as f:
        json.dump(card_cache, f, indent=2, sort_keys=True)
    print(f"\nSaved {len(card_cache)} cards to cache file: {cache_file}", file=sys.stderr)


def parse_card_line(line: str) -> Tuple[int, str, str]:
    """
    Parse a card line to extract quantity, card name, and any suffix (like IDs).

    Examples:
        "1 Vendilion Clique" -> (1, "Vendilion Clique", "")
        "Aang, Airbending Master" -> (1, "Aang, Airbending Master", "")
        "6 Plains [abc123]" -> (6, "Plains", "[abc123]")

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

    return (quantity, card_name, suffix)


def get_card_type(card_name: str) -> str:
    """
    Query Scryfall API for card type information.

    Returns the primary card type category (Creatures, Sorceries, etc.)
    """
    # Check cache first
    if card_name in card_cache:
        return card_cache[card_name]

    # Skip special placeholder cards
    if "Random" in card_name and "rare" in card_name.lower():
        card_cache[card_name] = "Special"
        return "Special"

    # Query Scryfall
    try:
        time.sleep(REQUEST_DELAY)  # Rate limiting
        response = requests.get(SCRYFALL_API, params={"exact": card_name}, timeout=10)
        response.raise_for_status()

        data = response.json()
        type_line = data.get("type_line", "")

        # Determine primary type
        card_type = classify_card_type(type_line)
        card_cache[card_name] = card_type

        print(f"✓ {card_name}: {type_line} -> {card_type}", file=sys.stderr)
        return card_type

    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching {card_name}: {e}", file=sys.stderr)
        card_cache[card_name] = "Unknown"
        return "Unknown"


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
        if line.strip().startswith('//'):
            continue

        quantity, card_name, suffix = parse_card_line(line)

        if not card_name:
            continue

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


def process_directory(directory: Path, dry_run: bool = False):
    """
    Process all .txt files in a directory.
    """
    deck_files = sorted(directory.glob("*.txt"))

    if not deck_files:
        print(f"No .txt files found in {directory}", file=sys.stderr)
        return

    print(f"\nProcessing {len(deck_files)} decks in {directory}...", file=sys.stderr)

    modified_count = 0
    for deck_file in deck_files:
        try:
            if reformat_deck(deck_file, dry_run):
                modified_count += 1
                status = "[DRY RUN] Would modify" if dry_run else "Modified"
                print(f"{status}: {deck_file.name}", file=sys.stderr)
        except Exception as e:
            print(f"ERROR processing {deck_file.name}: {e}", file=sys.stderr)

    print(f"\n{directory.name}: {modified_count}/{len(deck_files)} files {'would be ' if dry_run else ''}modified", file=sys.stderr)


def main():
    # Parse arguments
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
    dry_run = "--dry-run" in sys.argv
    save_cache = "--save-cache" in sys.argv
    load_cache = "--load-cache" in sys.argv

    if not args:
        print("Usage: python batch_reformat.py <directory> [<directory>...] [--dry-run] [--save-cache] [--load-cache]", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  python batch_reformat.py etc/J25/ etc/TLA/ --load-cache --save-cache", file=sys.stderr)
        return 1

    if dry_run:
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

        process_directory(directory, dry_run)

    # Save cache if requested
    if save_cache and not dry_run:
        save_cache_to_disk()

    print(f"\n✓ Complete! Cache contains {len(card_cache)} unique cards", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
