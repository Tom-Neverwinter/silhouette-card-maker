# Dragon Ball Super TCG Plugin
# ============================
# Plugin for fetching Dragon Ball Super Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process Dragon Ball Super TCG decks from various online sources and download card images.

## Features
- **Tournament Scraping:** Extract deck lists from DBS-DeckPlanet and tournament sites
- **Card Image Fetching:** Download official card images from Bandai databases
- **Multiple Formats:** Support for Standard format (with expansion potential)
- **Batch Processing:** Handle multiple decks and tournaments efficiently

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Scrape recent tournaments and save decks
python dragon_ball_cli.py --format standard --num-tournaments 5

# Fetch images for scraped decks
python dragon_ball_cli.py --fetch-images --save-decks my_decks.txt

# Process specific tournament
python dragon_ball_cli.py --tournament-url "https://example.com/tournament"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for tournament/format preferences
2. Scrape deck data from online sources
3. Optionally download card images
4. Save results for card creation

## Data Sources
- **DBS-DeckPlanet:** Primary source for deck building and sharing
- **Bandai Official Site:** Official card database and images
- **Tournament Sites:** Various competitive play result aggregators

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Tournament discovery framework
- ✅ Deck parsing framework
- 🔄 Image fetching (placeholder - needs official API integration)
- 🔄 Full site scraping (framework ready for implementation)

## Future Enhancements
- Integration with official Bandai card database API
- Advanced tournament result parsing
- Card collection management
- Competitive meta analysis

## Technical Notes
- Uses web scraping for tournament data (respectful rate limiting implemented)
- Images sourced from official Bandai databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins (Pokemon, MTG, etc.)

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "dragon-ball-super" tag.
