# Raw Source Data

This directory contains source HTML/data from official Wizards of the Coast pages, used for parsing JumpStart deck lists.

## Files

### J25-deck-lists.html
- **Source**: https://magic.wizards.com/en/news/announcements/jumpstart-2025-booster-themes
- **Accessed**: 2025-12-01
- **Description**: JumpStart 2025 (Foundations) deck lists HTML source
- **Used by**: `etc/parsing-scripts/parse_j25.py`

### TLA-deck-lists.html (if needed)
- **Source**: https://magic.wizards.com/en/news/announcements/avatar-the-last-airbender-jumpstart-booster-themes
- **Description**: Avatar: The Last Airbender deck lists HTML source
- **Used by**: `etc/parsing-scripts/parse_tla.py`

## Fan Content Declaration

This data is extracted from official Wizards of the Coast sources for use under the Fan Content Policy.

> MTG-JumpStart is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.
>
> https://company.wizards.com/en/legal/fancontentpolicy

## Purpose

These files are stored for:
- **Reproducibility**: Ability to re-run parsing scripts
- **Verification**: Compare parsed output against source
- **Documentation**: Clear provenance of deck list data
- **Version control**: Track if source data changes over time

## Usage

These raw files are inputs to the parsing scripts in `etc/parsing-scripts/`. The scripts extract the deck list data and create individual formatted deck files in the appropriate `etc/{SET}/` directories.
