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

- **FDN** - Foundations Beginner Box (10 decks)
  - ✅ Individual files created (8 regular + 2 tutorial)
  - ⏳ Needs: Card type organization via `batch_reformat.py`
  - Source: `raw/FDN-HTML-DECKLISTS.txt`
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

## Scryfall API Card Data

### Overview
When querying the Scryfall API for card information, the API returns comprehensive card objects with numerous fields. **However, for this project, we only extract and cache the `type_line` field** to determine card type categorization.

### Core Card Fields (Available but Not Cached)

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Unique ID for this card in Scryfall's database |
| `oracle_id` | UUID | Yes | Unique ID for this card's oracle identity (consistent across reprints) |
| `name` | String | No | The name of this card |
| `lang` | String | No | Language code for this printing |
| `layout` | String | No | Code for this card's layout |
| `arena_id` | Integer | Yes | This card's Arena ID, if any |
| `mtgo_id` | Integer | Yes | This card's Magic Online ID (Catalog ID), if any |
| `mtgo_foil_id` | Integer | Yes | Foil Magic Online ID, if any |
| `multiverse_ids` | Array | Yes | Multiverse IDs on Gatherer, if any |
| `tcgplayer_id` | Integer | Yes | TCGplayer API product ID |
| `cardmarket_id` | Integer | Yes | Cardmarket API product ID |
| `scryfall_uri` | URI | No | Link to card's permapage on Scryfall |
| `uri` | URI | No | Link to this card object on Scryfall's API |
| `prints_search_uri` | URI | No | Link to paginate all reprints for this card |
| `rulings_uri` | URI | No | Link to this card's rulings list |

### Gameplay Fields (Available but Not Cached)

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `type_line` | String | No | **⭐ USED: Type line of card (e.g., "Creature — Human Wizard")** |
| `mana_cost` | String | Yes | Mana cost (empty string if absent) |
| `cmc` | Decimal | No | Mana value (converted mana cost) |
| `colors` | Array | Yes | Card's colors |
| `color_identity` | Array | No | Card's color identity |
| `color_indicator` | Array | Yes | Colors in color indicator, if any |
| `oracle_text` | String | Yes | Oracle text for this card |
| `power` | String | Yes | Power value (may be non-numeric like *) |
| `toughness` | String | Yes | Toughness value (may be non-numeric) |
| `defense` | String | Yes | Defense value, if any |
| `loyalty` | String | Yes | Loyalty value (may be non-numeric like X) |
| `keywords` | Array | No | Keywords used (e.g., 'Flying', 'Haste') |
| `legalities` | Object | No | Legality across formats (legal/not_legal/restricted/banned) |
| `reserved` | Boolean | No | True if on Reserved List |
| `edhrec_rank` | Integer | Yes | Overall rank/popularity on EDHREC |
| `penny_rank` | Integer | Yes | Rank/popularity on Penny Dreadful |
| `produced_mana` | Array | Yes | Colors of mana this card could produce |
| `card_faces` | Array | Yes | Array of Card Face objects for multifaced cards |
| `all_parts` | Array | Yes | Related Card Objects, if closely related to other cards |

### Our Simplified Caching Strategy

**What We Cache:**
```json
{
  "Card Name": "Simplified Type Category"
}
```

**Example:**
```json
{
  "Vendilion Clique": "Creatures",
  "Lightning Bolt": "Instants",
  "Sol Ring": "Artifacts"
}
```

**Type Categories:**
- `Creatures` - All creature cards (including Artifact Creatures, Enchantment Creatures)
- `Sorceries` - Sorcery cards
- `Instants` - Instant cards
- `Artifacts` - Artifact cards (excluding Artifact Creatures)
- `Enchantments` - Enchantment cards (excluding Enchantment Creatures)
- `Planeswalkers` - Planeswalker cards
- `Lands` - Land cards
- `Special` - Placeholder cards (e.g., "Random rare or mythic rare")
- `Unknown` - When lookup fails or card not found

**Why Simplified?**
1. **Minimal cache size**: 2,508 cards = ~70KB (vs several MB with full data)
2. **Single purpose**: Only need type categorization for deck formatting
3. **Fast lookups**: Simple key-value structure
4. **Scryfall compliance**: Cached locally per their 24hr+ recommendation
5. **Persistent**: Cache never expires (JumpStart decks don't change after release)

**Extraction Logic:**
```python
# From type_line: "Legendary Creature — Faerie Wizard"
# Extract: "Creatures"

# Multi-type cards use rightmost type:
# "Artifact Creature — Golem" → "Creatures" (not Artifacts)
# "Enchantment Creature — God" → "Creatures" (not Enchantments)
```

### API Compliance

**Rate Limiting:**
- ✅ 100ms delay between requests (meets Scryfall's 50-100ms guideline)
- ✅ Shared cache across all operations (85% API call reduction)
- ✅ No excessive requests (cache prevents redundant queries)

**Caching Policy:**
- ✅ Persistent local cache (exceeds 24hr minimum recommendation)
- ✅ Stored in `etc/parsing-scripts/card_type_cache.json`
- ✅ Includes Scryfall attribution in cache file

**Attribution:**
- Cache file includes comments noting data source and terms
- README.md documents Scryfall API usage
- Not affiliated with or endorsed by Scryfall

**Reference:**
- Scryfall API Documentation: https://scryfall.com/docs/api
- Rate Limiting Guidelines: https://scryfall.com/docs/api#rate-limits-and-good-citizenship

## Parsing Scripts

Located in `etc/parsing-scripts/` - See `etc/parsing-scripts/README.md` for detailed documentation.

### Core Scripts
- **`batch_reformat.py`** - ⭐ Primary tool for formatting deck lists with Scryfall API
  - Shared cache across decks (85% fewer API calls)
  - Normalizes basic land variants ("Above the Clouds Island" → "Island")
  - Organizes cards by type with headers

- **`parse_deck_list_format.py`** - Generic parser for `<deck-list>` HTML format
  - Used for: J25, ONE, MOM, LTR, J22, CLU, TLB, FDN
  - Removes bracketed IDs and special land notations

- **`parse_h2_ul_format.py`** - Generic parser for `<h2><ul>` HTML format
  - Used for: BRO, DMU
  - Removes bracketed IDs and special land notations

- **`parse_legacy_format.py`** - Generic parser for `<legacy>` HTML format
  - Used for: JMP
  - Removes bracketed IDs while preserving special land names

- **`parse_fdn_tutorial.py`** - FDN tutorial deck extractor
  - Extracts Cats and Vampires tutorial decks from HTML tables
  - Used for: FDN

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
