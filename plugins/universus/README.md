# Universus Plugin
# ================
# Plugin for fetching Universus Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process Universus decks from community sites and official resources. Universus is an anime crossover card game featuring characters from My Hero Academia, Cowboy Bebop, and Yu Yu Hakusho in a single cohesive game.

## Unique Features
- **Anime Crossover:** Characters from multiple popular anime series in one game
- **Character-Based Gameplay:** Focus on character cards with unique abilities
- **Foundation System:** Resource cards that power character abilities
- **Action/Asset Cards:** Support cards that enhance character performance
- **Established History:** Released around 2006 with dedicated community

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Scrape recent tournaments from universus.cards
python uvs_cli.py --source universus_cards --format standard --num-tournaments 5

# Fetch images for scraped decks
python uvs_cli.py --fetch-images --save-decks my_decks.txt

# Process specific tournament
python uvs_cli.py --tournament-url "https://universus.cards/tournament/123"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for data source and format preferences
2. Scrape deck data from universus.cards, UVS Ultra, and official sites
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **universus.cards:** https://universus.cards/ - Primary deck builder and tournament site
- **UVS Ultra:** https://uvsultra.online/ - Community tournament and deck site
- **Official Site:** https://uvsgames.com/ - Official Universus card database
- **Reddit:** r/universus for community discussion and deck sharing

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Tournament discovery framework
- ✅ Multiple data source support
- 🔄 Image fetching (placeholder - needs database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Supported Franchises
Universus features cards from:
- **My Hero Academia** - UA High School heroes and villains
- **Cowboy Bebop** - Bounty hunters and space adventures
- **Yu Yu Hakusho** - Spirit detectives and demon fighters
- And more anime crossovers!

## Game Mechanics
- **Character Cards:** Main gameplay pieces with unique abilities
- **Foundation Cards:** Resource system that powers characters
- **Action Cards:** Instant effects and triggers
- **Asset Cards:** Equipment and enhancements for characters
- **Franchise Synergies:** Cross-franchise card interactions

## Future Enhancements
- Integration with UVS Games official card database API
- Advanced tournament result parsing from multiple sources
- Franchise filtering and character collection management
- Meta analysis and deck archetype recommendations

## Technical Notes
- Uses web scraping for tournament data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "universus" tag.

Note: Universus has a smaller but dedicated community - data availability may be more limited compared to major TCGs like Magic: The Gathering.
