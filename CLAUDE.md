# MTG JumpStart Deck List Documentation

## Repository Purpose
This repository contains structured JumpStart deck lists for various MTG JumpStart sets, organized by set code.

## Deck List Format Standard

### File Naming Convention

**Format:**
- **Single variant themes**: `THEME NAME.txt` (no parentheses, no number)
  - Example: `BASRI.txt`, `LILIANA.txt`, `CHANDRA.txt`
- **Multiple variant themes**: `THEME NAME (#).txt` (space, then parentheses with number)
  - Example: `FAERIES (1).txt`, `FAERIES (2).txt`, `ABOVE THE CLOUDS (1).txt`, `ABOVE THE CLOUDS (2).txt`

**Rules:**
- Theme names are UPPERCASE
- Spaces between words (not hyphens or underscores)
- Variant numbers in parentheses with space before: ` (1)`, ` (2)`, etc.
- If a theme has only one variant, NO parentheses or number

**Examples:**
```
✓ CORRECT:
  ANGELS (1).txt          # Multiple variants
  ANGELS (2).txt
  BASRI.txt               # Single variant
  ABOVE THE CLOUDS (1).txt

✗ INCORRECT:
  ANGELS-1.txt            # Wrong: hyphen instead of space+parens
  ANGELS(1).txt           # Wrong: no space before parens
  BASRI (1).txt           # Wrong: single variant shouldn't have number
  above-the-clouds-1.txt  # Wrong: lowercase and hyphens
```

### File Structure
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


### Card Type Categories
Standard categories in order:
1. Creatures
2. Sorceries
3. Instants
4. Artifacts
5. Enchantments
6. Lands

**Note:** Some card types may be combined (e.g., Artifact Creatures go in Creatures section, Enchantment Creatures go in Creatures section). Follow official MTG categorization where the rightmost type determines primary classification.

## Current Repository Status

### Fully Formatted Sets (Following Standard)
Sets with complete card type organization (`//Creatures`, `//Lands`, etc.):

- **JMP** - JumpStart 2020 (121 deck variants)
  - ✅ Card type organization with headers
  - ✅ Standard file naming
  - Source: `raw/JMP-HTML-DECKLISTS.txt`

- **J22** - JumpStart 2022 (121 deck variants)
  - ✅ Card type organization with headers
  - ✅ Standard file naming
  - Source: `raw/J22-HTML-DECKLISTS.txt`

- **J25** - JumpStart 2025 / Foundations (121 deck variants)
  - ✅ Card type organization with headers
  - ✅ Standard file naming
  - Source: `raw/J25-HTML-DECKLISTS.txt`

- **TLA** - Avatar: The Last Airbender (66 deck variants)
  - ✅ Card type organization with headers
  - ✅ Standard file naming (space + parentheses)
  - ✅ Special basic land IDs removed
  - Note: Parsed from discord-bot repo, not from HTML

### Raw Format (Needs Reformatting)
Sets with individual deck files but no card type organization:

- **ONE** - Phyrexia: All Will Be One (10 decks)
  - ✅ Individual files created
  - ⏳ Needs: Card type organization via `batch_reformat.py`
  - Source: `raw/ONE-HTML-DECKLISTS.txt`

- **DMU** - Dominaria United (10 decks)
  - ✅ Individual files created
  - ⏳ Needs: Card type organization via `batch_reformat.py`
  - Source: `raw/DMU-HTML-DECKLISTS.txt`

- **BRO** - Brothers' War (10 decks)
  - ✅ Individual files created
  - ⏳ Needs: Card type organization via `batch_reformat.py`
  - Source: `raw/BRO-HTML-DECKLISTS.txt`

- **MOM** - March of the Machine (10 decks)
  - ✅ Individual files created
  - ⏳ Needs: Card type organization via `batch_reformat.py`
  - Source: `raw/MOM-HTML-DECKLISTS.txt`

- **LTR** - Lord of the Rings (20 decks)
  - ✅ Individual files created
  - ⏳ Needs: Card type organization via `batch_reformat.py`
  - Source: `raw/LTR-HTML-DECKLISTS.txt`

- **CLU** - Ravnica: Clue Edition (20 decks)
  - ✅ Individual files created
  - ⏳ Needs: Card type organization via `batch_reformat.py`
  - Source: `raw/CLU-HTML-DECKLISTS.txt`

- **FND** - Foundations Beginner Box (10 decks)
  - ✅ Individual files created (8 regular + 2 tutorial)
  - ⏳ Needs: Card type organization via `batch_reformat.py`
  - Source: `raw/FND-HTML-DECKLISTS.txt`
  - Note: Tutorial decks (Cats, Vampires) parsed from HTML tables

- **TLB** - Avatar TLA Beginner Box (10 decks)
  - ✅ Individual files created
  - ⏳ Needs: Card type organization via `batch_reformat.py`
  - Source: `raw/TLB-HTML-DECKLISTS.txt`

### Comparison Directories (Can be removed)
- **J22-new** - Regenerated J22 files from HTML (for comparison with existing)
- **JMP-new** - Regenerated JMP files from HTML (for comparison with existing)

### Consolidated Files
Legacy single-file deck lists in `etc/`:
- `JumpStart 2020 Paper Deck Lists All.txt`
- `JumpStart 2022 Deck Lists All.txt`
- `JumpStart DMU Paper Deck Lists All.txt`
- `JumpStart ONE Paper Deck Lists All.txt`

## Card Type Identification Strategy

### Option 1: Scryfall API (Recommended)
**API Endpoint:** `https://api.scryfall.com/cards/named?exact=[card-name]`

**Response Fields:**
- `type_line`: Full card type (e.g., "Legendary Creature — Faerie Wizard")
- `colors`: Color identity
- `mana_cost`: Mana cost
- `cmc`: Converted mana cost

**Example:**
```bash
curl "https://api.scryfall.com/cards/named?exact=Vendilion+Clique"
```

**Rate Limiting:**
- Scryfall requests 50-100ms delay between requests
- Use bulk data downloads for large datasets
- Implement exponential backoff for errors

**Parsing Card Types from type_line:**
- "Creature" → `//Creatures`
- "Sorcery" → `//Sorceries`
- "Instant" → `//Instants`
- "Artifact" → `//Artifacts` (unless "Artifact Creature")
- "Enchantment" → `//Enchantments` (unless "Enchantment Creature")
- "Land" → `//Lands`
- "Planeswalker" → `//Planeswalkers`

**Multi-type Cards:**
- "Artifact Creature" → `//Creatures`
- "Enchantment Creature" → `//Creatures`
- Use rightmost type for primary classification

### Option 2: Manual Classification
- Requires MTG knowledge to identify each card's type
- Time-consuming but works offline
- Claude has partial MTG knowledge (good for common cards, incomplete for newer/obscure cards)

### Option 3: Hybrid Approach
- Use Claude's knowledge for common cards
- Query Scryfall for uncertain cards
- Maintain a local cache of card types

### Implementation
A Python script `etc/parsing-scripts/reformat_deck.py` can be created to:
1. Read unformatted deck lists
2. Query Scryfall API for each unique card
3. Organize cards by type
4. Output formatted deck list following the standard template

## Parsing Scripts

Located in `etc/parsing-scripts/` - See `etc/parsing-scripts/README.md` for detailed documentation.

### Core Scripts
- **`batch_reformat.py`** - ⭐ Primary tool for formatting deck lists with Scryfall API
  - Shared cache across decks (85% fewer API calls)
  - Normalizes basic land variants ("Above the Clouds Island" → "Island")
  - Organizes cards by type with headers

- **`parse_deck_list_format.py`** - Generic parser for `<deck-list>` HTML format
  - Used for: J25, ONE, MOM, LTR, J22, CLU, TLB, FND
  - Removes bracketed IDs and special land notations

- **`parse_h2_ul_format.py`** - Generic parser for `<h2><ul>` HTML format
  - Used for: BRO, DMU
  - Removes bracketed IDs and special land notations

- **`parse_legacy_format.py`** - Generic parser for `<legacy>` HTML format
  - Used for: JMP
  - Removes bracketed IDs while preserving special land names

- **`parse_fnd_tutorial.py`** - FND tutorial deck extractor
  - Extracts Cats and Vampires tutorial decks from HTML tables
  - Used for: FND

### Workflow
See `etc/parsing-scripts/README.md` for complete walkthrough:
1. Get HTML from Wizards pages → save to `raw/`
2. Parse HTML → extract deck lists to `etc/SET/`
3. Reformat → organize by card type with `batch_reformat.py`

## Notes for AI Development

- When reformatting deck lists, preserve exact card names (case-sensitive, including special characters)
- JumpStart decks are always 20 cards total
- Basic lands may have special IDs or art indicators - preserve these
- Some themes have multiple variants (1, 2, 3, 4) - ensure variant numbering is correct
- Maintain consistent spacing and formatting across all files
