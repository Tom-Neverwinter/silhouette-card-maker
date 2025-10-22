# Munchkin Plugin
# ===============
# Plugin for fetching Munchkin card collections and data

## Overview
This plugin allows the Silhouette Card Maker to process Munchkin card collections from various sources. Munchkin is a humorous dungeon-crawling card game by Steve Jackson Games featuring monsters, treasures, and backstabbing mechanics.

## Important Note
**Munchkin is NOT a traditional trading card game (TCG) like Magic: The Gathering or Pokémon.** It is a standalone card game with a specific structure:

- **Door Cards:** Monsters, curses, and other obstacles
- **Treasure Cards:** Items, equipment, and loot
- **No Competitive Tournaments:** Focus is on casual, humorous gameplay
- **Cooperative Backstabbing:** Players help each other until it's time to betray

This plugin treats Munchkin as a card collection manager rather than a competitive TCG plugin.

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Get cards from Munchkin CCG database
python munchkin_cli.py --source ccg --num-cards 20

# Fetch images for card collection
python munchkin_cli.py --mode collection --fetch-images

# Search for specific card
python munchkin_cli.py --card-name "Potion of General Studliness"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for processing mode (cards, collection, or search)
2. Fetch card data from Munchkin CCG database and community sites
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **Munchkin CCG Database:** https://munchkinccg.game/gameplay/card-search/ - Official CCG card database
- **Card Game Database Wiki:** https://cardgamedatabase.fandom.com/wiki/Munchkin_(card_game) - Community wiki
- **BoardGameGeek:** https://boardgamegeek.com/wiki/page/Munchkin_series - Comprehensive game information
- **Steve Jackson Games:** https://www.sjgames.com/munchkin/ - Official game site

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Card collection framework
- ✅ Multiple data source support
- 🔄 Image fetching (placeholder - needs database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Card Types
- **Door Cards:** Monsters, curses, and dungeon obstacles
- **Treasure Cards:** Items, equipment, potions, and loot
- **Special Cards:** Unique cards with special effects
- **Level Cards:** Help players advance their character level

## Game Mechanics
- **Character Levels:** Players start at Level 1 and advance by killing monsters
- **Combat System:** Players vs monsters with item bonuses
- **Backstabbing:** Players can help or hinder each other
- **Winning Condition:** First player to reach Level 10 wins
- **Humorous Theme:** Game is designed for laughs and betrayal

## Future Enhancements
- Integration with Steve Jackson Games official card database
- Advanced card filtering by type, level, and rarity
- Collection management and duplicate detection
- Humorous card effect parsing and display

## Technical Notes
- Focuses on card collection management rather than competitive gameplay
- Uses web scraping for card data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "munchkin" tag.

Note: Munchkin is a casual, humorous card game - this plugin focuses on card collection rather than competitive tournament data.
