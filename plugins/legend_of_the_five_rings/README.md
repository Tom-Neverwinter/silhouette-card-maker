# Legend of the Five Rings Plugin
# ================================
# Plugin for fetching Legend of the Five Rings CCG cards and images

## Overview
This plugin allows the Silhouette Card Maker to process Legend of the Five Rings CCG decks and fetch card images. Legend of the Five Rings is a classic collectible card game set in the fantasy world of Rokugan, published by Alderac Entertainment Group (AEG).

## Unique Features
- **Rokugan Universe:** Play with characters from the Emerald Empire
- **Clan System:** Choose from seven Great Clans with unique abilities
- **Honor System:** Manage honor and dishonor mechanics
- **Samurai Culture:** Experience the way of the warrior
- **Political Intrigue:** Navigate the complex court politics
- **Classic Fantasy:** Based on the beloved L5R setting

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Search for Legend of the Five Rings cards
python l5r_cli.py --search "Hida" --max-results 20

# Search by clan
python l5r_cli.py --clan "Crab" --max-results 30

# Search by card type
python l5r_cli.py --type "Character" --max-results 25

# Search by honor value
python l5r_cli.py --honor "High" --max-results 25
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Browse available Legend of the Five Rings cards
2. Search for specific characters, clans, or types
3. Create collections from different sets
4. Fetch high-quality card images

## Data Sources
- **CCGTrader.net**: https://www.ccgtrader.net/games/legend-of-the-five-rings-ccg - Comprehensive card database
- **Community Resources**: Fan-maintained card databases
- **AEG Archives**: Historical card data from Alderac Entertainment Group

## Current Status
- ✅ Basic plugin structure implemented
- ✅ CCGTrader integration ready
- ✅ Clan-based search functionality
- ✅ Honor system integration
- 🔄 Image fetching (framework ready for implementation)
- 🔄 Set-specific card filtering

## Supported Characters
Legend of the Five Rings features cards from:
- **Crab Clan**: Hida, Kaiu, Yasuki families
- **Crane Clan**: Doji, Kakita, Daidoji families
- **Dragon Clan**: Togashi, Mirumoto, Agasha families
- **Lion Clan**: Akodo, Matsu, Ikoma families
- **Mantis Clan**: Yoritomo, Tsuruchi, Moshi families
- **Phoenix Clan**: Isawa, Shiba, Asako families
- **Scorpion Clan**: Bayushi, Shosuro, Soshi families
- **Unicorn Clan**: Shinjo, Moto, Iuchi families
- And many more!

## Game Mechanics
- **Clan System:** Choose from seven Great Clans
- **Honor System:** Manage honor and dishonor
- **Character Cards:** Samurai, courtiers, and shugenja
- **Province Cards:** Locations and strongholds
- **Event Cards:** Major story moments and battles
- **Item Cards:** Weapons, armor, and magical items
- **Strategy Cards:** Tactical advantages

## Card Types
- **Character Cards:** Samurai, courtiers, and shugenja
- **Province Cards:** Locations and strongholds
- **Event Cards:** Major story moments and battles
- **Item Cards:** Weapons, armor, and magical items
- **Strategy Cards:** Tactical advantages
- **Personality Cards:** Important characters
- **Holding Cards:** Resources and support

## Great Clans
- **Crab Clan**: Defenders of the Wall, practical warriors
- **Crane Clan**: Courtiers and duelists, masters of etiquette
- **Dragon Clan**: Mystics and monks, seekers of enlightenment
- **Lion Clan**: Warriors and generals, masters of warfare
- **Mantis Clan**: Traders and sailors, masters of commerce
- **Phoenix Clan**: Shugenja and scholars, masters of magic
- **Scorpion Clan**: Spies and assassins, masters of deception
- **Unicorn Clan**: Horsemen and explorers, masters of mobility

## Honor System
- **High Honor**: Characters with high honor values
- **Low Honor**: Characters with low honor values
- **Dishonor**: Characters with negative honor values
- **Neutral**: Characters with balanced honor

## Future Enhancements
- Integration with official Legend of the Five Rings databases
- Advanced clan filtering
- Character relationship mapping
- Tournament deck analysis
- Set-specific card filtering
- Honor system mechanics

## Technical Notes
- Uses CCGTrader.net for card data (respectful rate limiting implemented)
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins for consistency
- Supports both English and foreign language sets

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "legend-of-the-five-rings" tag.

Note: Legend of the Five Rings CCG is a licensed product. This plugin is for personal use and playtesting only.
