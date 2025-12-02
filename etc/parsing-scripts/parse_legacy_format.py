#!/usr/bin/env python3
"""
Parser for <deck-list><legacy> format HTML (used by JMP)

Usage:
    python parse_legacy_format.py <html_file> <output_dir>

Example:
    python parse_legacy_format.py ../../raw/JMP-HTML-DECKLISTS.txt ../../etc/JMP
"""

import re
import os
import sys

def clean_card_line(line):
    """Clean up card lines, handling special Island/land names and removing bracketed IDs."""
    line = line.strip()

    # Skip empty lines and format lines
    if not line or line.startswith('Title:') or line.startswith('Format:'):
        return None

    # Remove bracketed IDs (e.g., "6 Plains [2t8d3N5Gn1ecBNsDqjQuJe]" -> "6 Plains")
    line = re.sub(r'\s+\[[a-zA-Z0-9]+\]', '', line)

    # Handle special basic land names like "Above the Clouds Island"
    # These are actual card names, keep them as-is

    return line

def parse_html(html_content, output_dir):
    """Parse legacy format HTML and create deck files."""

    # Extract all deck blocks: <deck-list><legacy>...</legacy></deck-list>
    deck_pattern = r'<deck-list><legacy>(.*?)</legacy></deck-list>'

    decks = re.findall(deck_pattern, html_content, re.DOTALL)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    deck_count = 0
    unique_themes = set()

    for deck_content in decks:
        # Extract title
        title_match = re.search(r'Title:\s*(.+)', deck_content)
        if not title_match:
            continue

        deck_title = title_match.group(1).strip()

        # Parse card lines (skip Title: and Format: lines)
        lines = []
        for line in deck_content.split('\n'):
            cleaned = clean_card_line(line)
            if cleaned:
                lines.append(cleaned)

        # Create filename using standard format
        filename = deck_title.upper()

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
        print("Usage: python parse_legacy_format.py <html_file> <output_dir>")
        sys.exit(1)

    html_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(html_file, 'r') as f:
        html_content = f.read()

    parse_html(html_content, output_dir)
