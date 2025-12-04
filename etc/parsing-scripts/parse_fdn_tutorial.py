#!/usr/bin/env python3
"""
Parse FND (Foundations Beginner Box) tutorial decks from HTML tables.

The tutorial decks (Cats and Vampires) are in a different format than regular
deck-list tags - they're in ordered tables showing the draw order for teaching.

Usage:
    python parse_fnd_tutorial.py ../../raw/FND-HTML-DECKLISTS.txt ../../etc/FND
"""

import re
import sys
from collections import Counter

def parse_tutorial_deck(html_content, deck_name):
    """Extract a tutorial deck from HTML table format."""

    # Find the section for this deck
    pattern = rf'<div[^>]*>{deck_name}</div>.*?</table>'
    match = re.search(pattern, html_content, re.DOTALL)

    if not match:
        print(f"Warning: Could not find {deck_name} tutorial deck")
        return []

    section = match.group(0)

    # Extract all card names from auto-card tags
    card_pattern = r'<auto-card[^>]*>([^<]+)</auto-card>'
    cards = re.findall(card_pattern, section)

    # Clean up card names (remove extra spaces)
    cards = [card.strip() for card in cards]

    # Count occurrences
    card_counts = Counter(cards)

    # Build deck list
    deck_list = []
    for card, count in sorted(card_counts.items()):
        if count == 1:
            deck_list.append(card)
        else:
            deck_list.append(f"{count} {card}")

    return deck_list

def main():
    if len(sys.argv) != 3:
        print("Usage: python parse_fnd_tutorial.py <html_file> <output_dir>")
        sys.exit(1)

    html_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(html_file, 'r') as f:
        html_content = f.read()

    # Parse both tutorial decks
    tutorial_decks = ['Cats', 'Vampires']

    for deck_name in tutorial_decks:
        cards = parse_tutorial_deck(html_content, deck_name)

        if cards:
            # Write deck file
            filename = f"{deck_name.upper()}.txt"
            filepath = f"{output_dir}/{filename}"

            with open(filepath, 'w') as f:
                # First line: deck name
                f.write(deck_name.upper() + '\n')
                # Then the card list
                for card in cards:
                    f.write(card + '\n')

            print(f"Created: {filename} ({len(cards)} unique cards)")

    print(f"\nTotal tutorial decks: {len(tutorial_decks)}")

if __name__ == '__main__':
    main()
