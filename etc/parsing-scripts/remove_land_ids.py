#!/usr/bin/env python3
"""
Remove special basic land IDs from TLA deck lists.

Removes bracketed IDs like [2t8d3N5Gn1ecBNsDqjQuJe] from basic land entries.

Usage:
    python remove_land_ids.py [--dry-run]
"""

import os
import sys
import re
from pathlib import Path

TLA_DIR = Path(__file__).parent.parent / "TLA"


def remove_land_ids_from_file(file_path, dry_run=False):
    """
    Remove bracketed IDs from basic land entries in a file.

    Examples:
        "6 Plains [2t8d3N5Gn1ecBNsDqjQuJe]" → "6 Plains"
        "1 Plains Appa [6rlws0Y9bsjCxQpb7zzpYk]" → "1 Plains Appa"
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    modified = False
    new_lines = []

    for line in lines:
        # Remove bracketed IDs (pattern: [alphanumeric string])
        new_line = re.sub(r'\s+\[[a-zA-Z0-9]+\]', '', line)

        if new_line != line:
            modified = True
            if dry_run:
                print(f"  {line.rstrip()} → {new_line.rstrip()}")

        new_lines.append(new_line)

    if modified:
        if not dry_run:
            with open(file_path, 'w') as f:
                f.writelines(new_lines)
        return True

    return False


def remove_land_ids(dry_run=False):
    """
    Remove land IDs from all TLA deck files.
    """
    if not TLA_DIR.exists():
        print(f"Error: Directory not found: {TLA_DIR}", file=sys.stderr)
        return 1

    files = sorted(TLA_DIR.glob("*.txt"))
    modified_count = 0

    for file_path in files:
        filename = file_path.name

        if dry_run:
            print(f"\n{filename}:")

        if remove_land_ids_from_file(file_path, dry_run):
            modified_count += 1
            if not dry_run:
                print(f"✓ Modified: {filename}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Modified {modified_count} files")
    return 0


def main():
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("=== DRY RUN MODE - No files will be changed ===\n")

    return remove_land_ids(dry_run)


if __name__ == "__main__":
    sys.exit(main())
