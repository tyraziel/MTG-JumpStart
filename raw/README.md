# Raw Source Data

This directory contains source HTML from official Wizards of the Coast pages, used for parsing JumpStart deck lists.

## File Naming Convention

Files are named `{SET}-HTML-DECKLISTS.txt` and contain the raw HTML saved from the Wizards deck list page for that set.

## Files

| File | Set | Source URL |
|------|-----|------------|
| `JMP-HTML-DECKLISTS.txt` | JumpStart 2020 | https://magic.wizards.com/en/articles/archive/feature/jumpstart-decklists-2020-06-18 |
| `J22-HTML-DECKLISTS.txt` | JumpStart 2022 | https://magic.wizards.com/en/news/feature/jumpstart-2022-booster-themes-and-card-lists |
| `J25-HTML-DECKLISTS.txt` | JumpStart Foundations | https://magic.wizards.com/en/news/announcements/foundations-jumpstart-booster-themes |
| `DMU-HTML-DECKLISTS.txt` | Dominaria United | https://magic.wizards.com/en/articles/archive/news/dominaria-united-jumpstart-booster-contents-2022-08-31 |
| `BRO-HTML-DECKLISTS.txt` | The Brothers' War | https://magic.wizards.com/en/news/feature/the-brothers-war-jumpstart-booster-contents |
| `ONE-HTML-DECKLISTS.txt` | Phyrexia: All Will Be One | https://magic.wizards.com/en/news/announcements/phyrexia-all-will-be-one-jumpstart-booster-themes-and-card-lists |
| `MOM-HTML-DECKLISTS.txt` | March of the Machine | https://magic.wizards.com/en/news/announcements/march-of-the-machine-jumpstart-booster-themes-and-card-lists |
| `LTR-HTML-DECKLISTS.txt` | The Lord of the Rings | https://magic.wizards.com/en/news/announcements/the-lord-of-the-rings-tales-of-middle-earth-jumpstart-booster-contents |
| `CLU-HTML-DECKLISTS.txt` | Ravnica: Clue Edition | https://magic.wizards.com/en/news/announcements/ravnica-clue-edition-ravnica-cluedo-edition-booster-contents |
| `FDN-HTML-DECKLISTS.txt` | Foundations Beginner Box | https://magic.wizards.com/en/news/feature/foundations-beginner-box-contents |
| `TLB-HTML-DECKLISTS.txt` | Avatar TLA Beginner Box | https://magic.wizards.com/en/news/announcements/avatar-the-last-airbender-beginner-box-contents |
| `MSH-HTML-DECKLISTS.txt` | Marvel Super Heroes *(pending)* | https://magic.wizards.com/en/news/announcements/marvel-super-heroes-jumpstart-booster-themes |
| `MSB-HTML-DECKLISTS.txt` | Marvel Super Heroes Beginner Box *(pending)* | https://magic.wizards.com/en/news/announcements/marvel-super-heroes-beginner-box-contents |

> **Note:** TLA deck lists were sourced from the discord-bot repo rather than a Wizards HTML page, so no `TLA-HTML-DECKLISTS.txt` exists.

## Adding a New Set

1. Open the Wizards deck list page for the set
2. Save the full page HTML as `{SET}-HTML-DECKLISTS.txt` in this directory
3. Run `/process-new-set` in Claude Code to parse and process the deck lists

## Fan Content Declaration

This data is extracted from official Wizards of the Coast sources for use under the Fan Content Policy.

> MTG-JumpStart is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.
>
> https://company.wizards.com/en/legal/fancontentpolicy

## Purpose

These files are stored for:
- **Reproducibility**: Ability to re-run parsing scripts from the original source
- **Verification**: Compare parsed output against source
- **Documentation**: Clear provenance of deck list data
- **Version control**: Track if source data changes over time
