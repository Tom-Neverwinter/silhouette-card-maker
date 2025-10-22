# Magi-Nation Duel TCG Plugin
# ============================
# Plugin for fetching Magi-Nation Duel Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process Magi-Nation Duel TCG decks from official sources and community sites. Magi-Nation Duel is a strategic card game where players are Magi commanding creatures and casting spells from six different regions.

## Features
- **Multi-Source Scraping:** Extract card data from Magi-Nation Central, official sites, and community resources
- **Regional Focus:** Support for all six regions (Arderial, Cald, Naroom, Orothe, Underneath, Universal)
- **Card Type Support:** Magi, Creatures, Spells, and Relics
- **Collection Management:** Create and manage Magi-Nation Duel card collections
- **Tournament Integration:** Framework for tournament deck extraction
- **Image Fetching:** Support for card image downloads

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Scrape cards from Magi-Nation Central
python mnd_cli.py scrape --source central --max-cards 50

# Search for specific cards
python mnd_cli.py search "Tony Jones"

# Process a collection with regional focus
python mnd_cli.py collection --collection-name "Arderial Deck" --fetch-images

# Generate sample collection for testing
python mnd_cli.py sample --num-cards 20 --collection-name "Test Collection"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for data source and regional preferences
2. Scrape card data from available sources
3. Organize cards by region and type
4. Optionally attempt to download card images
5. Save results for card creation

## Data Sources
- **Magi-Nation Central:** https://maginationcentral.com/wiki/ - Primary card database and community wiki
- **Official Site:** https://www.magi-nation.com/ - Official card information and game resources
- **Community Resources:** Magi-Nation fandom wiki and community sites
- **Regional Databases:** Individual region-specific resources

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Multi-source scraping framework
- ✅ Regional card organization
- ✅ Collection management system
- 🔄 Image fetching (framework ready for database integration)
- 🔄 Tournament deck scraping (would need community site integration)

## Limitations
- **API Limitations:** No official API available, relies on web scraping
- **Image Sources:** Limited to community resources and manual sourcing
- **Maintenance:** Community sites may change structure periodically

## Future Enhancements
- Integration with official Magi-Nation digital platforms
- Advanced tournament result parsing from community sites
- Regional deck building recommendations
- Card collection management and trading features
- Integration with popular Magi-Nation apps and tools

## Card Types
- **Magi:** Player characters that command creatures and cast spells
- **Creatures:** Monsters that fight for the Magi (have attack/defense values)
- **Spells:** Magical effects that can be cast for various effects
- **Relics:** Artifacts with special powers and ongoing effects

## Regions
- **Arderial:** Forest and growth-focused region
- **Cald:** Fire and destruction-focused region
- **Naroom:** Peaceful and defensive region
- **Orothe:** Ancient and mystical region
- **Underneath:** Dark and shadow-focused region
- **Universal:** Cards that can be used by any region

## Game Mechanics
- **Energy System:** Magi have energy pools used to summon creatures and cast spells
- **Regional Themes:** Each region has unique creatures and spells
- **Deck Construction:** Players build decks around specific Magi and regions
- **Tournament Play:** Competitive scene with organized tournaments

## Technical Notes
- Uses web scraping for card data (respectful rate limiting implemented)
- Organizes cards by region for easy deck building
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins

## Collection Management
Collections can be:
- **Region-Specific:** Focus on a single region's cards and themes
- **Multi-Region:** Combine cards from multiple regions for diverse strategies
- **Magi-Focused:** Built around specific Magi and their abilities
- **Competitive:** Tournament-ready decks with optimal card selections

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "magi-nation-duel" tag.

Note: Magi-Nation Duel has a dedicated community but fewer competitive tournaments compared to larger TCGs like Magic: The Gathering or Pokémon.
