#!/usr/bin/env python3
"""
Reformat JumpStart deck lists to standard format with card type organization.

This script:
1. Reads an unformatted deck list (one card per line, optional quantities)
2. Queries Scryfall API for card type information
3. Organizes cards by type (Creatures, Sorceries, Instants, Artifacts, Enchantments, Lands)
4. Outputs a formatted deck list following the JMP/J22 standard

Usage:
    python reformat_deck.py input_deck.txt [output_deck.txt]

If output file is not specified, outputs to stdout.
"""

import sys
import time
import re
import requests
from collections import defaultdict
from typing import Dict, List, Tuple

# Scryfall API endpoint
SCRYFALL_API = "https://api.scryfall.com/cards/named"

# Rate limiting: Scryfall requests 50-100ms between requests
REQUEST_DELAY = 0.075  # 75ms between requests

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

# Cache for card type lookups
card_cache: Dict[str, str] = {}


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


def reformat_deck(input_file: str, output_file: str = None):
    """
    Reformat a deck list from unformatted to standard format.
    """
    # Read input file
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # First line is typically the deck name
    deck_name = lines[0].strip() if lines else "UNNAMED DECK"

    # Parse cards
    cards_by_type = defaultdict(list)

    for line in lines[1:]:
        quantity, card_name, suffix = parse_card_line(line)

        if not card_name:
            continue

        card_type = get_card_type(card_name)

        # Format card line
        card_line = f"{quantity} {card_name}"
        if suffix:
            card_line += f" {suffix}"

        cards_by_type[card_type].append(card_line)

    # Build output
    output_lines = [deck_name]

    for type_name in TYPE_ORDER:
        if type_name in cards_by_type and cards_by_type[type_name]:
            count = len(cards_by_type[type_name])
            output_lines.append(f"//{type_name} ({count})")
            output_lines.extend(cards_by_type[type_name])

    # Add any unknown or special cards at the end
    for type_name in ["Special", "Unknown"]:
        if type_name in cards_by_type and cards_by_type[type_name]:
            output_lines.append(f"//{type_name}")
            output_lines.extend(cards_by_type[type_name])

    # Output
    output_text = "\n".join(output_lines) + "\n"

    if output_file:
        with open(output_file, 'w') as f:
            f.write(output_text)
        print(f"\n✓ Reformatted deck written to {output_file}", file=sys.stderr)
    else:
        print(output_text)


def main():
    if len(sys.argv) < 2:
        print("Usage: python reformat_deck.py input_deck.txt [output_deck.txt]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    reformat_deck(input_file, output_file)


if __name__ == "__main__":
    main()
