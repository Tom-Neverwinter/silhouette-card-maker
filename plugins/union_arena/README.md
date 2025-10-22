# Union Arena TCG Plugin
# ======================
# Plugin for fetching Union Arena Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process Union Arena TCG decks from community sites and meta resources. Union Arena is unique for featuring crossovers from multiple anime series in a single game.

## Features
- **Tournament Scraping:** Extract deck lists from UA Meta and community sources
- **Multiple Anime Crossovers:** Support for Hunter x Hunter, Bleach, My Hero Academia, and more
- **Card Image Fetching:** Framework for downloading card images (implementation needed)
- **Batch Processing:** Handle multiple tournaments and decks efficiently
- **Multiple Data Sources:** UA Meta site and community resources

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Scrape recent tournaments from UA Meta
python ua_cli.py --source meta --format standard --num-tournaments 5

# Fetch images for scraped decks
python ua_cli.py --fetch-images --save-decks my_decks.txt

# Process specific tournament
python ua_cli.py --tournament-url "https://uasgmeta.com/decklist/123"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for data source and format preferences
2. Scrape deck data from available sources
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **UA Meta:** https://www.uasgmeta.com/uadecklists - Tournament deck lists and meta analysis
- **exburst.dev:** https://exburst.dev/ua/ - Card database and deck builder
- **Community Blogs:** Joseph Writer Anderson and other tournament coverage
- **Reddit:** r/Union_Arena_TCG for community discussion

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Tournament discovery framework
- ✅ Multiple data source support
- 🔄 Image fetching (placeholder - needs database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Unique Features
- **Anime Crossovers:** Play with characters from multiple series in one game
- **Growing Competitive Scene:** Regular new set releases and tournaments
- **Community Driven:** Strong community support and meta analysis

## Future Enhancements
- Integration with exburst.dev card database API
- Advanced tournament result parsing from UA Meta
- Card collection management and deck builder features
- Meta analysis and tier list integration

## Technical Notes
- Uses web scraping for tournament data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "union-arena" tag.

Note: Union Arena is a growing TCG with regular content updates - check for new data sources as the community expands.
