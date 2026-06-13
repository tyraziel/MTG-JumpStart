Process a new JumpStart set from raw HTML deck lists through to fully generated JSON files.

## Before You Start — Check Scryfall Rate Limits

**Always verify the current limits before running API scripts:**
https://scryfall.com/docs/api/rate-limits

As of the last update, `/cards/named` is hard-limited to **2 requests/second (500ms)**. The default delay in all scripts is **1000ms** (double the hard limit). Do not lower `--delay` below 500ms, and check the link above in case limits have changed.

## Steps

1. Ask the user for the **set code** (e.g. MSH) and **set name** (e.g. "Marvel Super Heroes") if not already provided as arguments.

2. Confirm the raw HTML file exists at `raw/<SET>-HTML-DECKLISTS.txt`. If not, remind the user to save the Wizards deck list page HTML there first.

3. Identify the HTML format by inspecting the file:
   ```bash
   head -40 raw/<SET>-HTML-DECKLISTS.txt
   ```
   - `<deck-list deck-title="...">` → use `parse_deck_list_format.py` (most common recent sets)
   - `<h2>Name</h2><ul><li>...` → use `parse_h2_ul_format.py` (BRO, DMU)
   - `<legacy>Title:` → use `parse_legacy_format.py` (JMP only)
   - HTML tables → use `parse_fdn_tutorial.py` or a new parser may be needed

4. Add the new set to `SETS` and `SET_NAMES` in both `generate_combined_json.py` and `generate_token_index.py` before generating JSON, or those files won't include the new set.

5. Create the set directory and parse the HTML:
   ```bash
   mkdir -p etc/<SET>
   cd etc/parsing-scripts
   python parse_deck_list_format.py ../../raw/<SET>-HTML-DECKLISTS.txt ../../etc/<SET>
   ```

6. Reformat deck lists and build card type cache:  **[hits Scryfall API]**
   ```bash
   python batch_reformat.py ../<SET>/ --load-cache --save-cache
   ```
   The `--load-cache` flag is critical — it reuses cached data for reprints and basic lands, reducing API calls dramatically.

7. Backfill token data for any new cards:  **[hits Scryfall API]**
   ```bash
   python add_token_data.py
   python update_token_keywords.py
   ```
   Both scripts save every 25 cards — safe to interrupt and resume.

8. After the API steps finish, check for any Unknown entries (cards that errored and weren't cached):
   ```bash
   python manage_unknowns.py --list
   ```
   If any are listed, fix the root cause (usually a card name mismatch) then run `--remove` and re-run `batch_reformat.py` for just that set.

9. Generate all JSON files:  **[no API — reads from cache only]**
   ```bash
   python generate_json_decks.py ../<SET>/
   python generate_combined_json.py
   python generate_token_index.py
   ```

10. Spot-check the output:
    - Verify deck count: `ls etc/<SET>/*.json | wc -l`
    - Check a sample deck JSON has correct card types, tokens, etc.
    - Confirm the token index updated: check `etc/jumpstart-token-index.json` metadata

11. Report a summary:
    - How many decks were parsed
    - Any cards that came back as Unknown type (need manual cache fixes)
    - Any new tokens found
    - Whether `unofficial_tokens` need to be manually added for any cards (tokens created by card text with no official printed token card)

## Notes

- If the HTML format is unrecognized, paste a sample to the user and ask how to proceed — a new parser script may be needed
- `add_token_data.py` and `update_token_keywords.py` both save every 25 cards — safe to interrupt and resume
- Transient API errors (400, 429, timeout) are NOT cached — they will be retried on the next run
- 429 rate-limit errors trigger automatic backoff and retry — if you see many, wait a few minutes and restart
