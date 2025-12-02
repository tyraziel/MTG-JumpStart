#!/usr/bin/env python3
"""
Parser for <h2> + <ul><li> format HTML (used by DMU, BRO)

Usage:
    python parse_h2_ul_format.py <html_file> <output_dir>

Example:
    python parse_h2_ul_format.py ../../raw/BRO-HTML-DECKLISTS.txt ../../etc/BRO
"""

import re
import os
import sys

def clean_card_line(line):
    """Clean up card lines, removing special land notations, bracketed IDs, and theme cards."""
    line = line.strip()

    # Skip theme description cards
    if 'theme description card' in line.lower():
        return None

    # Remove leading "1 " if present (handle inconsistent formatting)
    # But preserve actual quantities
    line = re.sub(r'^<li>\s*', '', line)
    line = re.sub(r'\s*</li>$', '', line)

    # Remove bracketed IDs (e.g., "6 Plains [2t8d3N5Gn1ecBNsDqjQuJe]" -> "6 Plains")
    line = re.sub(r'\s+\[[a-zA-Z0-9]+\]', '', line)

    # Handle special land notations
    # "2 Traditional foil Plains" -> "2 Plains"
    # "1 Full-art stained-glass Forest" -> "1 Forest"
    basic_lands = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest']
    for land in basic_lands:
        if land in line:
            # Extract quantity and land name only
            match = re.match(r'^(\d+)\s+.*?(' + land + r').*$', line)
            if match:
                quantity = match.group(1)
                return f"{quantity} {land}"

    return line if line else None

def parse_html(html_content, output_dir):
    """Parse h2/ul format HTML and create deck files."""

    # Extract decks: <h2>Theme Name</h2> followed by <ul>...</ul>
    deck_pattern = r'<h2>([^<]+)</h2>\s*<ul>(.*?)</ul>'

    decks = re.findall(deck_pattern, html_content, re.DOTALL)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    deck_count = 0
    unique_themes = set()

    for deck_title, deck_content in decks:
        deck_title = deck_title.strip()

        # Parse card lines from <li> tags
        li_pattern = r'<li>([^<]+)</li>'
        card_lines = re.findall(li_pattern, deck_content)

        # Clean up the deck list
        lines = []
        for line in card_lines:
            cleaned = clean_card_line(line)
            if cleaned:
                lines.append(cleaned)

        # Create filename using standard format
        # "Infantry 1" -> "INFANTRY (1).txt"
        # "Coalition Corps" -> "COALITION CORPS.txt"
        filename = deck_title.upper()

        # Convert "Name 1" to "NAME (1)"
        filename = re.sub(r'\s+(\d+)$', r' (\1)', filename)

        # Track base theme
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
        print("Usage: python parse_h2_ul_format.py <html_file> <output_dir>")
        sys.exit(1)

    html_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(html_file, 'r') as f:
        html_content = f.read()

    parse_html(html_content, output_dir)
