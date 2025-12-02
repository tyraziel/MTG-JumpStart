# JumpStart Deck List Parsing Scripts

Scripts for extracting and formatting MTG JumpStart deck lists from official Wizards HTML sources.

## Quick Start Workflow

### Step 1: Get HTML Source
Download HTML from official Wizards pages and save to `raw/`:

```bash
# Example URLs:
# J25: https://magic.wizards.com/en/news/announcements/jumpstart-2025-booster-themes
# ONE: https://magic.wizards.com/en/news/announcements/phyrexia-all-will-be-one-jumpstart-booster-card-lists
# Save as: raw/SET-HTML-DECKLISTS.txt
```

### Step 2: Parse HTML → Raw Deck Lists
Extract deck lists from HTML using the appropriate parser:

```bash
cd etc/parsing-scripts

# For <deck-list> format (J25, ONE, MOM, LTR, J22, CLU, TLB, FND):
python parse_deck_list_format.py ../../raw/ONE-HTML-DECKLISTS.txt ../../etc/ONE

# For <h2><ul> format (BRO, DMU):
python parse_h2_ul_format.py ../../raw/BRO-HTML-DECKLISTS.txt ../../etc/BRO

# For <legacy> format (JMP):
python parse_legacy_format.py ../../raw/JMP-HTML-DECKLISTS.txt ../../etc/JMP
```

**Output:** Raw unsorted deck lists in `etc/SET/` (one card per line, no type organization)

### Step 3: Reformat Deck Lists → Organized by Card Type
Use `batch_reformat.py` to query Scryfall and organize cards by type:

```bash
# First run (builds cache):
python batch_reformat.py ../../etc/ONE/ --save-cache

# Subsequent runs (uses cache):
python batch_reformat.py ../../etc/BRO/ --load-cache --save-cache

# Multiple sets at once:
python batch_reformat.py ../../etc/ONE/ ../../etc/BRO/ ../../etc/DMU/ --load-cache --save-cache

# Dry run (preview without modifying files):
python batch_reformat.py ../../etc/J25/ --dry-run --load-cache
```

**Output:** Formatted deck lists with card type headers:
```
DECK NAME
//Creatures (7)
1 Creature One
2 Creature Two
//Sorceries (2)
1 Sorcery Name
//Lands (9)
7 Island
2 Plains
```

## Core Scripts (Essential)

### `batch_reformat.py` ⭐ **Primary Tool**
Batch reformats deck lists with Scryfall API integration and shared caching.

**Features:**
- Shared cache across all decks (85% fewer API calls)
- Persistent cache in `card_type_cache.json`
- Organizes cards by type (Creatures, Sorceries, Instants, Artifacts, Enchantments, Lands)
- Normalizes special basic lands ("Above the Clouds Island" → "Island")
- Handles multi-type cards correctly (Artifact Creature → Creatures)
- Respects Scryfall rate limiting (100ms between requests)

**Usage:**
```bash
python batch_reformat.py <deck_dir>... [options]

Options:
  --dry-run       Preview changes without modifying files
  --save-cache    Save cache to card_type_cache.json after run
  --load-cache    Load cache from card_type_cache.json before run
```

**Examples:**
```bash
# Format one set, build cache
python batch_reformat.py ../../etc/J25/ --save-cache

# Format multiple sets with cache
python batch_reformat.py ../../etc/ONE/ ../../etc/BRO/ --load-cache --save-cache

# Preview changes
python batch_reformat.py ../../etc/TLA/ --dry-run --load-cache
```

**Efficiency:**
- Without cache: ~2,835 API calls for 189 decks
- With cache: ~400-500 API calls (85% reduction)

### `parse_deck_list_format.py`
Parses `<deck-list deck-title="...">` HTML format.

**Used for:** J25, ONE, MOM, LTR, J22, CLU, TLB, FND

**Usage:**
```bash
python parse_deck_list_format.py <html_file> <output_dir>
```

**Example:**
```bash
python parse_deck_list_format.py ../../raw/ONE-HTML-DECKLISTS.txt ../../etc/ONE
```

**Features:**
- Extracts deck name from `deck-title` attribute
- Handles variant numbering: "Theme Name 1" → "THEME NAME (1).txt"
- Cleans special land notations
- Removes theme description cards

### `parse_h2_ul_format.py`
Parses `<h2>Deck Name</h2><ul><li>cards</li></ul>` HTML format.

**Used for:** BRO, DMU

**Usage:**
```bash
python parse_h2_ul_format.py <html_file> <output_dir>
```

**Example:**
```bash
python parse_h2_ul_format.py ../../raw/DMU-HTML-DECKLISTS.txt ../../etc/DMU
```

**Features:**
- Handles inconsistent quantity formatting
- Cleans "Full-art stained-glass" and "Traditional foil" land prefixes
- Converts "Name 1" to "NAME (1)" format

### `parse_legacy_format.py`
Parses `<deck-list><legacy>Title: ...` HTML format.

**Used for:** JMP

**Usage:**
```bash
python parse_legacy_format.py <html_file> <output_dir>
```

**Example:**
```bash
python parse_legacy_format.py ../../raw/JMP-HTML-DECKLISTS.txt ../../etc/JMP
```

**Features:**
- Extracts title from "Title:" line
- Preserves special basic land names (e.g., "Above the Clouds Island")
- Skips "Format: Legacy" metadata lines

### `parse_fnd_tutorial.py`
Extracts tutorial decks from FND Beginner Box HTML tables.

**Used for:** FND (Cats and Vampires tutorial decks)

**Usage:**
```bash
python parse_fnd_tutorial.py <html_file> <output_dir>
```

**Example:**
```bash
python parse_fnd_tutorial.py ../../raw/FND-HTML-DECKLISTS.txt ../../etc/FND
```

**Features:**
- Parses ordered HTML tables (tutorial draw order)
- Counts card quantities automatically
- Outputs standard deck list format

## File Naming Convention

All deck list files follow this standard:

**Single variant themes:**
- `THEME NAME.txt` (no parentheses, no number)
- Examples: `BASRI.txt`, `LILIANA.txt`, `ELDRAZI.txt`

**Multiple variant themes:**
- `THEME NAME (1).txt` (space, then parentheses with number)
- Examples: `ANGELS (1).txt`, `ANGELS (2).txt`, `FAERIES (1).txt`

**Rules:**
- Theme names are UPPERCASE
- Spaces between words (not hyphens or underscores)
- Variant numbers in parentheses with space before: ` (1)`, ` (2)`, etc.
- If a theme has only one variant, NO parentheses or number

## Deck List Format Standard

After reformatting with `batch_reformat.py`, files have this structure:

```
THEME NAME (#)
//Creatures (X)
[quantity] [card name]
[quantity] [card name]
//Sorceries (X)
[quantity] [card name]
//Instants (X)
[quantity] [card name]
//Artifacts (X)
[quantity] [card name]
//Enchantments (X)
[quantity] [card name]
//Lands (X)
[quantity] [card name]
```

**Card type order:** Creatures, Sorceries, Instants, Artifacts, Enchantments, Lands, Planeswalkers

**Multi-type cards:** Classified by rightmost type (Artifact Creature → Creatures)

## Special Handling

### Basic Land Normalization
`batch_reformat.py` automatically normalizes basic land variants:

```
"Above the Clouds Island"          → "Island"
"Full-art stained-glass Plains"    → "Plains"
"Traditional foil Mountain"        → "Mountain"
"Snow-Covered Forest"              → "Forest"
```

Preserves dual lands and special lands:
```
"Tropical Island"   → "Tropical Island" (kept)
"Thriving Isle"     → "Thriving Isle" (kept)
```

### Placeholder Cards
Cards like "Random rare or mythic rare" are automatically categorized as "Special" type.

## Requirements

**Python:** 3.6+

**Dependencies:**
```bash
pip install -r requirements.txt
```

Required packages:
- `requests` (for Scryfall API queries)

## Typical Workflow Example

Import and format a new JumpStart set (e.g., Khans):

```bash
# 1. Save HTML from Wizards page
curl "https://magic.wizards.com/..." > raw/KHN-HTML-DECKLISTS.txt

# 2. Identify HTML format by checking the file
head -20 raw/KHN-HTML-DECKLISTS.txt

# 3. Parse using appropriate parser (assume deck-list format)
cd etc/parsing-scripts
python parse_deck_list_format.py ../../raw/KHN-HTML-DECKLISTS.txt ../../etc/KHN

# 4. Format with Scryfall (use cache from previous runs)
python batch_reformat.py ../../etc/KHN/ --load-cache --save-cache

# 5. Verify output
ls -l ../../etc/KHN/
head -20 ../../etc/KHN/"THEME NAME (1).txt"
```

## Cache Management

**Location:** `etc/parsing-scripts/card_type_cache.json`

**Cache operations:**
```bash
# Save cache after run
python batch_reformat.py ../../etc/J25/ --save-cache

# Load existing cache
python batch_reformat.py ../../etc/TLA/ --load-cache

# Load and save (recommended)
python batch_reformat.py ../../etc/ONE/ --load-cache --save-cache

# Delete cache (force fresh queries)
rm card_type_cache.json
```

**Cache benefits:**
- Reusable across sets (basic lands, common cards)
- Persistent across sessions
- Dramatically reduces Scryfall API calls
- Speeds up formatting by ~85%

## Set Status

### Fully Formatted (Standard Format)
- **JMP** - JumpStart 2020 (121 decks)
- **J22** - JumpStart 2022 (121 decks)

### Raw Format (Needs Reformatting)
Run `batch_reformat.py` on these:
- **J25** - JumpStart 2025 / Foundations (121 decks)
- **TLA** - Avatar: The Last Airbender (68 decks)
- **ONE** - Phyrexia: All Will Be One (10 decks)
- **DMU** - Dominaria United (10 decks)
- **BRO** - Brothers' War (10 decks)
- **MOM** - March of the Machine (10 decks)
- **LTR** - Lord of the Rings (20 decks)
- **CLU** - Ravnica: Clue Edition (20 decks)
- **FND** - Foundations Beginner Box (8 decks)
- **TLB** - Avatar TLA Beginner Box (10 decks)

## Troubleshooting

**Scryfall rate limiting:**
- Script respects 100ms delay between requests
- Use cache to minimize API calls
- Wait if you see connection errors

**Proxy errors:**
- Network environment may block Scryfall
- Use `--load-cache` to work offline
- Pre-build cache in different environment

**Unknown card types:**
- Check `card_type_cache.json` for "Unknown" entries
- Manually verify card names on Scryfall
- May be typos or unreleased cards

## Attribution

Created with Claude Code [Sonnet 4.5]
For MTG JumpStart deck list management
