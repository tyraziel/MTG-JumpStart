# JumpStart Deck List Parsing Scripts

This directory contains Python scripts for parsing official Wizards of the Coast HTML pages to extract JumpStart deck lists.

## Scripts

### `rename_tla_files.py` - Rename TLA Files to Standard Format
Renames TLA deck list files from hyphen format to parentheses format.

**Usage:**
```bash
python rename_tla_files.py [--dry-run]
# Use --dry-run to preview changes without renaming
```

**Changes:**
- `ADEPT-1.txt` → `ADEPT (1).txt`
- `ADEPT-2.txt` → `ADEPT (2).txt`
- `AANG.txt` → `AANG.txt` (no change, already correct)

**Note:** This script has already been run on the TLA files. Only needed if importing new TLA files with hyphen format.

### `remove_land_ids.py` - Remove Special Basic Land IDs
Removes special bracketed IDs from basic land entries in TLA deck lists.

**Usage:**
```bash
python remove_land_ids.py [--dry-run]
# Use --dry-run to preview changes without modifying files
```

**Changes:**
- `6 Plains [2t8d3N5Gn1ecBNsDqjQuJe]` → `6 Plains`
- `1 Plains Appa [6rlws0Y9bsjCxQpb7zzpYk]` → `1 Plains Appa`
- Removes all bracketed alphanumeric IDs from land entries

**Note:** This script has already been run on the TLA files. Only needed if importing new TLA files with land IDs.

### `reformat_deck.py` - Reformat Deck Lists to Standard Format
Reformats unformatted deck lists to the standard JMP/J22 format with card type organization.

**Usage:**
```bash
python reformat_deck.py input_deck.txt [output_deck.txt]
# If output file not specified, prints to stdout
```

**Features:**
- Queries Scryfall API for card type information
- Organizes cards by type (Creatures, Sorceries, Instants, etc.)
- Preserves card quantities and special notations
- Handles multi-type cards correctly (Artifact Creature → Creatures)
- Caches card lookups to minimize API calls
- Respects Scryfall rate limiting (100ms between requests, matching Discord bot)

**Output Format:**
```
DECK NAME
//Creatures (X)
1 Card Name
2 Another Card
//Sorceries (X)
1 Sorcery Name
//Lands (X)
7 Island
```

**Requirements:**
- Python 3.6+
- `requests` library (see requirements.txt)

**Installation:**
```bash
pip install -r requirements.txt
```

### `parse_tla.py` - Avatar: The Last Airbender
Parses TLA (Avatar: The Last Airbender) JumpStart deck lists.

**Usage:**
```bash
python parse_tla.py < tla_html.txt
# or
python parse_tla.py tla_html.txt
```

**Output:**
- Creates `etc/TLA/` directory with 66 deck list files
- 46 unique themes (26 Mythic, 20 Rare with variations)
- Prints theme data ready for `jumpstartdata.py`

**Theme Structure:**
- **Mythic (M)**: Single variation themes (5 per color + 1 multicolor)
- **Rare (R)**: Double variation themes (4 per color, with -1 and -2 suffixes)

### `parse_j25.py` - JumpStart 2025 (Foundations)
Parses J25 (JumpStart 2025) deck lists from the Foundations release.

**Usage:**
```bash
python parse_j25.py < j25_html.txt
# or
python parse_j25.py j25_html.txt
```

**Output:**
- Creates `etc/J25/` directory with all deck list files
- Handles variations (1), (2), (3), (4) automatically
- J25 themes already exist in `jumpstartdata.py` (lines 148-193)

## Getting HTML Content

To use these scripts, you need to get the HTML from the official Wizards pages:

### For TLA:
1. Visit: https://magic.wizards.com/en/news/announcements/avatar-the-last-airbender-jumpstart-booster-themes
2. View page source (Ctrl+U or Cmd+Option+U)
3. Copy all `<deck-list>` sections
4. Save to `tla_html.txt`

### For J25:
1. Visit: https://magic.wizards.com/en/news/announcements/jumpstart-2025-booster-themes
2. View page source
3. Copy all `<deck-list>` sections
4. Save to `j25_html.txt`

## File Naming Conventions

The scripts automatically convert theme names to filename format:
- Uppercase all letters
- Replace spaces with dashes
- Remove apostrophes
- Keep variation numbers: `(1)` → `-1`, `(2)` → `-2`, etc.

**Examples:**
- "N'er-do-wells (1)" → `NER-DO-WELLS-1.txt`
- "At the Zoo" → `AT-THE-ZOO.txt`
- "Hei Bai (1)" → `HEI-BAI-1.txt`

## Output Format

Deck list files contain one card per line:
```
Momo, Rambunctious Rascal
Kindly Customer
Invasion Reinforcements
7 Plains
...
```

Card names with quantities and set codes are preserved as-is from the HTML.

## Integration with jumpstartdata.py

After running the parsers:
1. The deck files are created in `etc/{SET}/` directories
2. For TLA: Copy the printed theme data into `jumpstartdata.py`
3. For J25: Themes already exist, no changes needed to `jumpstartdata.py`

## Requirements

- Python 3.6+
- For `parse_tla.py` and `parse_j25.py`: No external dependencies (uses only stdlib: `re`, `os`, `sys`)
- For `reformat_deck.py`: `requests` library (install with `pip install -r requirements.txt`)

## Attribution

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0

These scripts were created with AI assistance to help manage JumpStart Discord Bot deck lists.
