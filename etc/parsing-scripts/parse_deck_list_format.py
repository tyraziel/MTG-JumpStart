#!/usr/bin/env python3
"""
Generic parser for <deck-list> format HTML (used by J25, ONE, MOM, LTR, etc.)

Usage:
    python parse_deck_list_format.py <html_file> <output_dir>

Example:
    python parse_deck_list_format.py ../../raw/ONE-HTML-DECKLISTS.txt ../../etc/ONE
"""

import re
import os
import sys

def clean_card_line(line):
    """Clean up card lines, removing special land notations."""
    line = line.strip()

    # Skip theme description cards
    if 'theme description card' in line.lower():
        return None

    # Handle special land notations
    # "2 Traditional foil Plains" -> "2 Plains"
    # "1 Full-art stained-glass Forest" -> "1 Forest"
    basic_lands = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest']
    for land in basic_lands:
        if land in line:
            # Extract quantity and land name only
            match = re.match(r'^(\d+)\s+.*?' + land + r'.*$', line)
            if match:
                quantity = match.group(1)
                return f"{quantity} {land}"

    return line

def parse_html(html_content, output_dir):
    """Parse deck-list format HTML and create deck files."""

    # Extract all deck-list blocks
    deck_pattern = r'<deck-list[^>]*deck-title="([^"]+)"[^>]*>(.*?)</deck-list>'
    main_deck_pattern = r'<main-deck>(.*?)</main-deck>'

    decks = re.findall(deck_pattern, html_content, re.DOTALL)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    deck_count = 0
    unique_themes = set()

    for deck_title, deck_content in decks:
        # Extract main deck
        main_match = re.search(main_deck_pattern, deck_content, re.DOTALL)
        if not main_match:
            continue

        main_deck = main_match.group(1).strip()

        # Clean up the deck list
        lines = []
        for line in main_deck.split('\n'):
            cleaned = clean_card_line(line)
            if cleaned:
                lines.append(cleaned)

        # Create filename using standard format
        # Remove apostrophes and normalize spacing
        filename = deck_title.upper().replace("'", '')

        # Track base theme (without variation numbers)
        base_theme = re.sub(r' \(\d+\)$', '', filename)
        unique_themes.add(base_theme)

        # Write deck list file
        filepath = os.path.join(output_dir, f'{filename}.txt')
        with open(filepath, 'w') as f:
            # First line: deck name
            f.write(filename + '\n')
            # Then the card list
            for line in lines:
                f.write(line + '\n')

        deck_count += 1
        print(f"Created: {filename}.txt")

    print(f"\nTotal unique themes: {len(unique_themes)}")
    print(f"Total deck files: {deck_count}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python parse_deck_list_format.py <html_file> <output_dir>")
        sys.exit(1)

    html_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(html_file, 'r') as f:
        html_content = f.read()

    parse_html(html_content, output_dir)
