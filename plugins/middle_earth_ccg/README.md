# Middle Earth CCG Plugin
# ========================
# Plugin for fetching Middle Earth CCG cards and images

## Overview
This plugin allows the Silhouette Card Maker to process Middle Earth CCG decks and fetch card images. Middle Earth CCG is a classic collectible card game based on J.R.R. Tolkien's The Lord of the Rings and The Hobbit, published by Iron Crown Enterprises (ICE).

## Unique Features
- **Tolkien Universe:** Play with characters from The Lord of the Rings and The Hobbit
- **Fellowship System:** Build your fellowship of heroes
- **Corruption System:** Manage the influence of the One Ring
- **Location Cards:** Iconic Middle Earth locations and regions
- **Character Cards:** Heroes, villains, and supporting characters
- **Classic Fantasy:** Based on the beloved Tolkien works

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Search for Middle Earth CCG cards
python meccg_cli.py --search "Gandalf" --max-results 20

# Search by faction
python meccg_cli.py --faction "Free Peoples" --max-results 30

# Search by region
python meccg_cli.py --region "Shire" --max-results 25

# Search by card type
python meccg_cli.py --type "Character" --max-results 25
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Browse available Middle Earth CCG cards
2. Search for specific characters, factions, or regions
3. Create collections from different sets
4. Fetch high-quality card images

## Data Sources
- **CCGTrader.net**: https://www.ccgtrader.net/games/middle-earth-ccg - Comprehensive card database
- **Community Resources**: Fan-maintained card databases
- **ICE Archives**: Historical card data from Iron Crown Enterprises

## Current Status
- ✅ Basic plugin structure implemented
- ✅ CCGTrader integration ready
- ✅ Faction-based search functionality
- ✅ Region-based filtering
- 🔄 Image fetching (framework ready for implementation)
- 🔄 Set-specific card filtering

## Supported Characters
Middle Earth CCG features cards from:
- **The Fellowship**: Frodo, Sam, Merry, Pippin, Gandalf, Aragorn, Legolas, Gimli, Boromir
- **The Hobbit**: Bilbo, Thorin, Bard, Smaug
- **Villains**: Sauron, Saruman, Nazgûl, Orcs, Trolls
- **Supporting Characters**: Arwen, Éowyn, Faramir, Gollum
- **Other Characters**: Tom Bombadil, Treebeard, Balrog, Shelob
- And many more!

## Game Mechanics
- **Fellowship System:** Build your fellowship of heroes
- **Corruption System:** Manage the influence of the One Ring
- **Character Cards:** Heroes, villains, and supporting characters
- **Location Cards:** Middle Earth locations and regions
- **Item Cards:** Weapons, armor, and magical items
- **Event Cards:** Major story moments and battles
- **Hazard Cards:** Dangers and obstacles

## Card Types
- **Character Cards:** Heroes, villains, and supporting characters
- **Location Cards:** Middle Earth locations and regions
- **Item Cards:** Weapons, armor, and magical items
- **Event Cards:** Major story moments and battles
- **Hazard Cards:** Dangers and obstacles
- **Resource Cards:** Items and abilities that help your fellowship

## Factions
- **Free Peoples:** Heroes and allies (Gandalf, Aragorn, etc.)
- **Shadow:** Villains and minions (Sauron, Nazgûl, etc.)
- **Neutral:** Characters that can work with either side

## Regions
- **The Shire**: Hobbit homeland
- **Rivendell**: Elven sanctuary
- **Lothlórien**: Golden Wood
- **Mordor**: Dark Lord's realm
- **Isengard**: Saruman's stronghold
- **Rohan**: Horse-lords' kingdom
- **Gondor**: Kingdom of men
- **Mirkwood**: Dark forest
- **Misty Mountains**: Mountain range

## Future Enhancements
- Integration with official Middle Earth CCG databases
- Advanced faction filtering
- Character relationship mapping
- Tournament deck analysis
- Set-specific card filtering
- Ring corruption mechanics

## Technical Notes
- Uses CCGTrader.net for card data (respectful rate limiting implemented)
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins for consistency
- Supports both English and foreign language sets

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "middle-earth-ccg" tag.

Note: Middle Earth CCG is a licensed product. This plugin is for personal use and playtesting only.
