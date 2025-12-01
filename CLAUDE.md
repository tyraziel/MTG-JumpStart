# MTG JumpStart Deck List Documentation

## Repository Purpose
This repository contains structured JumpStart deck lists for various MTG JumpStart sets, organized by set code.

## Deck List Format Standard

### File Naming Convention
- Files named as: `THEME-NAME (variant#).txt`
- Example: `FAERIES (1).txt`, `DISCARDING (2).txt`

### File Structure
```
THEME-NAME (variant#)
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

### Template File
See `etc/J22/AAA_TEMPLATE` for the standard template structure.

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
- **JMP** - JumpStart 2020 (121 deck variants)
  - Individual files with card type organization
  - Format: `//Creatures (X)` style headers
- **J22** - JumpStart 2022 (121 deck variants)
  - Individual files with card type organization
  - Has template file: `AAA_TEMPLATE`

### Needs Reformatting (No Card Type Organization)
- **TLA** - Avatar: The Last Airbender (68 deck variants)
  - Current format: Simple card list, one card per line
  - Missing: Card type organization, quantity prefixes
  - Has: Special basic land IDs (e.g., `[2t8d3N5Gn1ecBNsDqjQuJe]`)

- **ONE** - Phyrexia: All Will Be One (10 individual deck files)
  - Current format: Simple card list with quantities
  - Missing: Card type organization
  - Has: "Random rare or mythic rare" placeholder cards

- **DMU** - Dominaria United JumpStart (10 individual deck files)
  - Current format: Simple card list with quantities
  - Missing: Card type organization
  - Includes: Special foil and promo notations

- **BRO** - Brothers' War JumpStart
  - **Only has consolidated file**: `JumpStart BRO Paper Deck Lists All.txt`
  - No individual deck files yet
  - Missing: Card type organization
  - Needs: Splitting into individual files + reformatting

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

Located in `etc/parsing-scripts/`:
- `parse_j25.py` - Parser for Foundations JumpStart (J25)
- `parse_tla.py` - Parser for Avatar: The Last Airbender (TLA)
- `README.md` - Documentation for parsing scripts

## Tasks TODO

### Immediate
- [ ] Verify DMU, BRO, ONE deck lists follow standard format
- [ ] Reformat TLA deck lists to match JMP/J22 standard
- [ ] Determine strategy for card type identification (API vs manual)
- [ ] Handle special basic land IDs in TLA properly

### Future
- [ ] Add missing sets: FDN (Foundations), MOM (March of the Machine), LTR (Lord of the Rings)
- [ ] Create consolidated deck list files for all sets
- [ ] Add parsing/formatting scripts for future sets
- [ ] Create validation script to check deck format consistency

## Notes for AI Development

- When reformatting deck lists, preserve exact card names (case-sensitive, including special characters)
- JumpStart decks are always 20 cards total
- Basic lands may have special IDs or art indicators - preserve these
- Some themes have multiple variants (1, 2, 3, 4) - ensure variant numbering is correct
- Maintain consistent spacing and formatting across all files
