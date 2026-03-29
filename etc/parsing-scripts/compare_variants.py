#!/usr/bin/env python3
"""
compare_variants.py - Compare variant decks within a JumpStart set.

For multi-variant themes (e.g. GOBLINS (1) and GOBLINS (2)), identifies the
key differentiating cards between each variant — useful for building
spreadsheet checklists.

For single-variant themes, picks the most notable card (legendary > rare >
uncommon > common, with named characters prioritized).

Usage:
    python compare_variants.py <set_dir> [--order <order_file>]

Arguments:
    set_dir       Path to a set directory containing .json deck files (e.g. ../../etc/TLA)
    --order       Optional path to a text file with theme names, one per line,
                  to control output order. Lines match theme names case-insensitively
                  and ignore hyphens/spaces/underscores.

Examples:
    python compare_variants.py ../../etc/TLA
    python compare_variants.py ../../etc/TLA --order my_order.txt
    python compare_variants.py ../../etc/J22

Output:
    Tab-separated lines: THEME_NAME <tab> card1, card2
    Multi-variant themes show one line per variant.
    Single-variant themes show one line with their best card.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict


BASIC_LANDS = {"Island", "Mountain", "Forest", "Swamp", "Plains",
               "Snow-Covered Island", "Snow-Covered Mountain",
               "Snow-Covered Forest", "Snow-Covered Swamp", "Snow-Covered Plains"}

RARITY_RANK = {"mythic": 0, "rare": 1, "uncommon": 2, "common": 3, "": 4}


def card_priority(card):
    """Lower value = more notable/iconic card. Used for selection ranking."""
    is_legendary = "Legendary" in card.get("type_line", "")
    rarity = RARITY_RANK.get(card.get("rarity", ""), 4)
    # Named characters tend to have commas or apostrophes (e.g. "Sokka, Swordmaster")
    has_name_marker = any(c in card["name"] for c in [",", "'"])
    return (0 if is_legendary else 1, rarity, 0 if has_name_marker else 1, card["name"])


def load_deck(path):
    with open(path) as f:
        data = json.load(f)
    card_map = {}
    for c in data["cards"]:
        if c["name"] not in BASIC_LANDS and c.get("type") != "Unknown":
            card_map[c["name"]] = c
    return card_map


def pick_key_cards(unique_cards, max_cards=2):
    """Pick 2 key cards (or 3 if there are 5+ differences and top 2 are all common)."""
    unique_cards = sorted(unique_cards, key=card_priority)
    pick = unique_cards[:max_cards]
    if len(unique_cards) >= 5 and all(c.get("rarity") == "common" for c in pick):
        pick = unique_cards[:3]
    return [c["name"] for c in pick]


def normalize_theme_name(name):
    """Normalize for loose matching (case, hyphens, spaces, underscores)."""
    return re.sub(r"[-_ ]+", "", name).lower()


def analyze_set(set_dir):
    """
    Returns:
        single: dict of theme_name -> best_card_name
        multi:  dict of theme_name -> list of (variant_label, [key_card_names])
    """
    files = [f for f in os.listdir(set_dir) if f.endswith(".json")]
    themes = defaultdict(list)
    for f in files:
        if "(" in f:
            theme = f.rsplit(" (", 1)[0]
        else:
            theme = f.replace(".json", "")
        themes[theme].append(f)

    single = {}
    multi = {}

    for theme in sorted(themes.keys()):
        variants = sorted(themes[theme])

        if len(variants) == 1:
            card_map = load_deck(os.path.join(set_dir, variants[0]))
            cards = sorted(card_map.values(), key=card_priority)
            single[theme] = cards[0]["name"] if cards else ""
        else:
            decks = []
            for v in variants:
                label = v.replace(".json", "")
                card_map = load_deck(os.path.join(set_dir, v))
                decks.append((label, card_map))

            shared = set(decks[0][1].keys())
            for _, cm in decks[1:]:
                shared &= set(cm.keys())

            variant_results = []
            for label, card_map in decks:
                unique = [c for name, c in card_map.items() if name not in shared]
                key_cards = pick_key_cards(unique)
                variant_results.append((label, key_cards))

            multi[theme] = variant_results

    return single, multi


def print_results(single, multi, order=None):
    """Print results, optionally in a specified order."""

    def output_single(theme):
        card = single.get(theme, "")
        print(f"{theme}\t{card}")

    def output_multi(theme):
        for label, cards in multi[theme]:
            print(f"{label}\t{', '.join(cards)}")

    if order:
        for raw_name in order:
            norm = normalize_theme_name(raw_name)
            # Try to match against single themes
            matched_single = next(
                (t for t in single if normalize_theme_name(t) == norm), None
            )
            if matched_single:
                output_single(matched_single)
                continue
            # Try to match against multi themes
            matched_multi = next(
                (t for t in multi if normalize_theme_name(t) == norm), None
            )
            if matched_multi:
                output_multi(matched_multi)
                continue
            print(f"# WARNING: '{raw_name}' not found in set", file=sys.stderr)
    else:
        # Default: single themes first (alphabetical), then multi themes
        print("# Single-variant themes")
        for theme in sorted(single.keys()):
            output_single(theme)
        print()
        print("# Multi-variant themes")
        for theme in sorted(multi.keys()):
            output_multi(theme)


def main():
    parser = argparse.ArgumentParser(
        description="Compare variant decks within a JumpStart set."
    )
    parser.add_argument("set_dir", help="Path to set directory containing .json files")
    parser.add_argument(
        "--order",
        metavar="FILE",
        help="Text file with theme names (one per line) controlling output order",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.set_dir):
        print(f"Error: '{args.set_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    order = None
    if args.order:
        with open(args.order) as f:
            order = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    single, multi = analyze_set(args.set_dir)
    print_results(single, multi, order)


if __name__ == "__main__":
    main()
