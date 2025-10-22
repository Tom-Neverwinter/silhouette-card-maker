# Star Realms TCG Plugin
# ========================
# Plugin for fetching Star Realms Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process Star Realms TCG decks from official sources and community sites. Star Realms is a fast-paced deck-building game with a dedicated competitive community.

## Features
- **Tournament Scraping:** Extract deck lists from official Star Realms sites and community resources
- **Multiple Data Sources:** Support for official card gallery, BoardGameGeek, and tier lists
- **Card Image Fetching:** Framework for downloading card images from official sources
- **Batch Processing:** Handle multiple tournaments and decks efficiently
- **Collection Management:** Create and manage Star Realms card collections

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Scrape recent cards from official card gallery
python sr_cli.py --source official --max-cards 50

# Fetch images for scraped cards
python sr_cli.py --fetch-images --output-dir game/front

# Process specific collection
python sr_cli.py --collection "My Star Realms Deck" --save-collection

# Search for specific cards
python sr_cli.py --search-card "Trade Pod"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for data source and scraping preferences
2. Scrape card data from available sources
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **Official Card Gallery:** https://www.starrealms.com/card-gallery/ - Primary card database
- **BoardGameGeek:** Complete card lists and community resources
- **Tier Lists:** Community-driven card rankings and analysis
- **Community Resources:** Reddit (r/starrealms), Discord communities, and tournament sites

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Card scraping framework from multiple sources
- ✅ Collection management system
- 🔄 Image fetching (framework ready for official API integration)
- 🔄 Tournament deck scraping (would need community site integration)

## Limitations
- **API Limitations:** No official API available, relies on web scraping
- **Image Sources:** Limited to community resources and manual sourcing
- **Maintenance:** Community sites may change structure periodically

## Future Enhancements
- Integration with official Star Realms digital platforms
- Advanced tournament result parsing from community sites
- Community-driven deck list aggregation
- Card collection management and trading features
- Integration with popular Star Realms apps and tools

## Technical Notes
- Uses web scraping for card data (respectful rate limiting implemented)
- Images sourced from official card galleries when available
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins

## Card Types
- **Ships:** Combat vessels that attack and provide trade
- **Bases:** Defensive structures that provide ongoing benefits
- **Outposts:** Powerful cards that remain in play until destroyed
- **Heroes:** Special commander cards (from Heroes expansion)

## Factions
- **Trade Federation:** Economic and trade-focused cards
- **Blob:** Aggressive, high-attack faction
- **Star Empire:** Balanced military faction
- **Machine Cult:** Technological and defensive cards

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "star-realms" tag.

Note: Star Realms has a vibrant community but fewer competitive tournaments compared to larger TCGs like Magic: The Gathering or Pokémon.
