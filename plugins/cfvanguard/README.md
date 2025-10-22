# Cardfight!! Vanguard Plugin
# ============================
# Plugin for fetching Cardfight!! Vanguard Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process Cardfight!! Vanguard decks from community sites and official resources. Cardfight!! Vanguard is an anime-style card game featuring unit summoning mechanics and has been active since 2011.

## Unique Features
- **Anime-Style Gameplay:** Unit summoning and combat mechanics
- **Grade System:** Cards range from Grade 0 to Grade 4 with different roles
- **Clan System:** Multiple factions with unique playstyles
- **G Units:** Generation break mechanics for advanced strategies
- **Long History:** Established game with extensive card pool

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Scrape recent tournaments from VG-Paradox
python cfv_cli.py --source vgp --format standard --num-tournaments 5

# Fetch images for scraped decks
python cfv_cli.py --fetch-images --save-decks my_decks.txt

# Process specific tournament
python cfv_cli.py --tournament-url "https://vg-paradox.com/tournament/123"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for data source and format preferences
2. Scrape deck data from VG-Paradox, official sites, and Dexander.blog
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **VG-Paradox:** https://vg-paradox.com/ - Tournament data, deck lists, and meta analysis
- **Official Site:** https://en.cf-vanguard.com/ - Official tournament results and deck recipes
- **Dexander.blog:** https://dexander.blog/ - Tournament winning deck lists since 2011
- **Reddit:** r/cardfightvanguard for community discussion and deck sharing

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Tournament discovery framework
- ✅ Multiple data source support
- 🔄 Image fetching (placeholder - needs database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Game Mechanics
- **Grade System:** Grade 0 (triggers), Grade 1-3 (units), Grade 4 (G units)
- **Clan Affiliations:** Royal Paladin, Shadow Paladin, Gold Paladin, etc.
- **Ride System:** Evolving your vanguard unit during the game
- **Generation Break:** G unit mechanics for advanced plays
- **Trigger System:** Chance effects that activate during drive checks

## Supported Formats
- **Standard:** Current competitive format
- **Premium:** Includes older card sets
- **All:** Both formats combined

## Future Enhancements
- Integration with comprehensive Cardfight!! Vanguard card databases
- Advanced tournament result parsing from multiple sources
- Clan filtering and archetype identification
- Meta analysis and deck tier recommendations

## Technical Notes
- Uses web scraping for tournament data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "cardfight-vanguard" tag.

Note: Cardfight!! Vanguard has experienced some competitive challenges recently - data availability may vary compared to more active TCGs.
