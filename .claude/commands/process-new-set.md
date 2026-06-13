Process a new JumpStart set from raw HTML deck lists through to fully generated JSON files.

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

4. Create the set directory and parse the HTML:
   ```bash
   mkdir -p etc/<SET>
   cd etc/parsing-scripts
   python parse_deck_list_format.py ../../raw/<SET>-HTML-DECKLISTS.txt ../../etc/<SET>
   ```

5. Reformat deck lists and build card type cache:
   ```bash
   python batch_reformat.py ../<SET>/ --load-cache --save-cache
   ```

6. Backfill token data for any new cards:
   ```bash
   python add_token_data.py
   python update_token_keywords.py
   ```

7. Generate all JSON files:
   ```bash
   python generate_json_decks.py ../<SET>/
   python generate_combined_json.py
   python generate_token_index.py
   ```

8. Spot-check the output:
   - Verify deck count looks right: `ls etc/<SET>/*.json | wc -l`
   - Check a sample deck JSON has correct card types, tokens, etc.
   - Confirm the token index updated: check `etc/jumpstart-token-index.json` metadata

9. Report a summary:
   - How many decks were parsed
   - Any cards that came back as Unknown type (need manual cache fixes)
   - Any new tokens found
   - Whether unofficial_tokens need to be manually added for any cards

## Notes

- If the HTML format is unrecognized, paste a sample to the user and ask how to proceed — a new parser script may be needed
- New sets must also be added to `SETS` and `SET_NAMES` in `generate_token_index.py` and `generate_combined_json.py` before the token index and combined JSON will include them
- The `--load-cache` flag on `batch_reformat.py` is critical — it reuses cached data for reprints and basic lands, reducing API calls dramatically
- Scryfall rate limit: default 250ms between calls, adjustable with `--delay MS`
- `add_token_data.py` and `update_token_keywords.py` save every 25 cards — safe to interrupt and resume
