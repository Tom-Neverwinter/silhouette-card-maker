# Force of Will TCG Plugin
# ========================
# Plugin for fetching Force of Will Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process Force of Will TCG decks from official sources and community sites. Note that Force of Will has a smaller competitive scene compared to other TCGs.

## Features
- **Tournament Scraping:** Extract deck lists from official Force of Will sites and Library of Will
- **Multiple Data Sources:** Support for official site and community resources
- **Card Image Fetching:** Framework for downloading card images (implementation needed)
- **Batch Processing:** Handle multiple tournaments and decks efficiently

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
python fow_cli.py --source official --format standard --num-tournaments 5

# Fetch images for scraped decks
python fow_cli.py --fetch-images --save-decks my_decks.txt

# Process specific tournament
python fow_cli.py --tournament-url "https://fowtcg.com/tournament/123"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for data source and format preferences
2. Scrape deck data from available sources
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **Official Site:** http://www.fowtcg.com/ - Primary tournament and event information
- **Library of Will:** https://www.fowlibrary.com/ - Community tournament deck lists
- **Community Resources:** Reddit (r/FoWtcg) and other community sites

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Tournament discovery framework
- ✅ Multiple data source support
- 🔄 Image fetching (placeholder - needs card database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Limitations
- **Smaller Community:** Force of Will has a smaller competitive scene than MTG/Pokemon
- **Limited Data:** Fewer tournaments and deck resources compared to major TCGs
- **Maintenance:** Community sites may change structure more frequently

## Future Enhancements
- Integration with Force of Will card databases
- Advanced tournament result parsing
- Community-driven deck list aggregation
- Card collection management features

## Technical Notes
- Uses web scraping for tournament data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "force-of-will" tag.

Note: Due to the smaller size of the Force of Will community, data availability may be more limited compared to larger TCGs like Magic: The Gathering or Pokémon.
