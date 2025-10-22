# Shadowverse: Evolve Plugin
# ===========================
# Plugin for fetching Shadowverse: Evolve Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process Shadowverse: Evolve decks from community sites and official resources. Shadowverse: Evolve is the physical adaptation of the popular Shadowverse digital CCG, featuring anime art style and strategic gameplay.

## Unique Features
- **Digital-to-Physical Transition:** Popular digital CCG now in physical format
- **Anime Art Style:** Beautiful artwork matching the digital version
- **Strategic Gameplay:** Deep strategy with multiple card types and mechanics
- **Growing Competitive Scene:** Regular tournaments and expanding player base
- **Cygames Quality:** High production values from experienced developer

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Scrape recent tournaments from official site
python sve_cli.py --source official --format standard --num-tournaments 5

# Fetch images for scraped decks
python sve_cli.py --fetch-images --save-decks my_decks.txt

# Process specific tournament
python sve_cli.py --tournament-url "https://en.shadowverse-evolve.com/decks/tournament/123"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for data source and format preferences
2. Scrape deck data from official sites, Dexander.blog, and ShadowCard.io
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **Official Site:** https://en.shadowverse-evolve.com/ - Official tournament results and deck recipes
- **Dexander.blog:** https://dexander.blog/portfolio/cp02/ - Tournament winning deck lists
- **ShadowCard.io:** https://shadowcard.io/ - Database and competitive deck building
- **Reddit:** r/ShadowverseEvolve for community discussion and deck sharing

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Tournament discovery framework
- ✅ Multiple data source support
- 🔄 Image fetching (placeholder - needs database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Game Mechanics
- **Leader Cards:** Choose your class leader (Forestcraft, Swordcraft, etc.)
- **Follower Cards:** Main combat units with various abilities
- **Spell Cards:** Instant effects and removal
- **Amulet Cards:** Ongoing effects and field control
- **Evolve System:** Cards can evolve for enhanced abilities
- **Play Point System:** Resource management similar to digital version

## Supported Classes
- **Forestcraft:** Nature and animal themes
- **Swordcraft:** Knight and warrior themes
- **Runecraft:** Magic and spell themes
- **Dragoncraft:** Dragon and power themes
- **Shadowcraft:** Undead and necromancy themes
- **Bloodcraft:** Vampire and blood themes
- **Havencraft:** Angel and light themes
- **Portalcraft:** Artifact and puppet themes

## Future Enhancements
- Integration with ShadowCard.io API for comprehensive card data
- Advanced tournament result parsing from multiple sources
- Class filtering and archetype identification
- Meta analysis and deck tier recommendations

## Technical Notes
- Uses web scraping for tournament data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "shadowverse-evolve" tag.

Note: Shadowverse: Evolve is a growing physical TCG - check for new data sources as the community expands.
