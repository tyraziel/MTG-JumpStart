Compare variant decks within a JumpStart set and output key differentiating cards, formatted as a table suitable for pasting into a spreadsheet.

## Steps

1. Ask the user which set they want to compare (e.g. TLA, J22, JMP). If they already specified it as an argument, use that.

2. Verify the set directory exists at `etc/<SET>/` and contains `.json` files.

3. Run the compare script:
   ```bash
   python etc/parsing-scripts/compare_variants.py etc/<SET>/
   ```

4. If the user wants a custom order, ask them to provide it (or check if they already did). Then create a temporary order file and re-run with `--order`.

5. Present the results as a markdown table with two columns:
   - **Theme** — the deck name/variant label
   - **Key Cards** — the 1-3 differentiating cards

   Format example:
   | Theme | Key Cards |
   |---|---|
   | AANG | Aang, Airbending Master |
   | HEI-BAI (1) | Invasion Reinforcements, Vengeful Villagers |
   | HEI-BAI (2) | Destined Confrontation, Jeong Jeong's Deserters |

## Notes

- Multi-variant themes show one row per variant with 2 key unique cards (3 if all differences are common rarity)
- Single-variant themes show one row with their single most notable card
- Card selection priority: Legendary > Rare > Uncommon > Common, with named characters (those with commas or apostrophes in the name) preferred at each tier
- The script reads `.json` files, not `.txt` files — make sure JSON files exist for the set
- If JSON files are missing, they can be generated with `generate_json_decks.py`
