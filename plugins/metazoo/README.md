# MetaZoo Plugin
# ==============
# Plugin for fetching MetaZoo Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process MetaZoo decks from community sites and official resources. MetaZoo is a cryptozoology-themed card game featuring mythical creatures, cryptids, and supernatural entities with unique aura-based gameplay.

## Unique Features
- **Cryptozoology Theme:** Features Bigfoot, Mothman, Chupacabra, and other cryptids
- **Aura System:** Five aura types (Forest, Flame, Light, Water, Dark) for synergies
- **Beastie Cards:** Creature cards with special abilities and power levels
- **Spell Cards:** Magical effects and removal options
- **Artifact Cards:** Equipment and ongoing effects
- **Niche Appeal:** Dedicated community despite smaller player base

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Scrape recent tournaments from PokeCellar
python mz_cli.py --source pokecellar --format standard --num-tournaments 5

# Fetch images for scraped decks
python mz_cli.py --fetch-images --save-decks my_decks.txt

# Process specific tournament
python mz_cli.py --tournament-url "https://tcg.pokecellar.com/tournament/123"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for data source and format preferences
2. Scrape deck data from PokeCellar, MetaversityTCG, and official sites
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **PokeCellar TCG:** https://tcg.pokecellar.com/ - Tournament reports and competitive analysis
- **MetaversityTCG:** https://metaversitytcg.com/blog/ - Tournament deck lists and coaching
- **MetaZoo HQ:** https://metazoohq.com/cards - Card set lists and information
- **Official Site:** https://www.metazoogames.com/ - Official MetaZoo Games resources
- **Reddit:** r/metazoogames for community discussion and deck sharing

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Tournament discovery framework
- ✅ Multiple data source support
- 🔄 Image fetching (placeholder - needs database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Game Mechanics
- **Beastie Cards:** Main creature cards with power levels and abilities
- **Spell Cards:** Magical effects, removal, and utility
- **Artifact Cards:** Equipment that enhances Beasties
- **Aura Cards:** Resource system with 5 aura types for synergies
- **Power Level:** Combat system based on card power values
- **Special Abilities:** Unique effects triggered by aura types and conditions

## Supported Aura Types
- **Forest:** Nature and animal themes
- **Flame:** Fire and destruction mechanics
- **Light:** Healing and protection effects
- **Water:** Control and manipulation
- **Dark:** Disruption and fear effects

## Future Enhancements
- Integration with MetaZoo HQ card database API
- Advanced tournament result parsing from multiple sources
- Aura type filtering and synergy analysis
- Cryptid collection management and theme decks

## Technical Notes
- Uses web scraping for tournament data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "metazoo" tag.

Note: MetaZoo is a niche TCG with dedicated community - data availability may be more limited compared to major TCGs like Magic: The Gathering.
