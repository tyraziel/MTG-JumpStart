#!/usr/bin/env python3
"""
Rename TLA files to match standard naming convention.

Changes:
- ADEPT-1.txt → ADEPT (1).txt
- ADEPT-2.txt → ADEPT (2).txt
- AANG.txt → AANG.txt (no change, already correct)

Usage:
    python rename_tla_files.py [--dry-run]
"""

import os
import sys
import re
from pathlib import Path

TLA_DIR = Path(__file__).parent.parent / "TLA"


def rename_tla_files(dry_run=False):
    """
    Rename TLA files from hyphen format to parentheses format.
    """
    if not TLA_DIR.exists():
        print(f"Error: Directory not found: {TLA_DIR}", file=sys.stderr)
        return 1

    files = sorted(TLA_DIR.glob("*.txt"))
    renamed_count = 0

    for file_path in files:
        filename = file_path.name

        # Check if file has hyphen-number pattern
        match = re.match(r'^(.+)-(\d+)\.txt$', filename)

        if match:
            theme_name = match.group(1)
            variant_num = match.group(2)
            new_filename = f"{theme_name} ({variant_num}).txt"
            new_path = file_path.parent / new_filename

            if dry_run:
                print(f"Would rename: {filename} → {new_filename}")
            else:
                file_path.rename(new_path)
                print(f"Renamed: {filename} → {new_filename}")

            renamed_count += 1
        else:
            # File already in correct format
            if dry_run:
                print(f"OK: {filename}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Renamed {renamed_count} files")
    return 0


def main():
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("=== DRY RUN MODE - No files will be changed ===\n")

    return rename_tla_files(dry_run)


if __name__ == "__main__":
    sys.exit(main())
