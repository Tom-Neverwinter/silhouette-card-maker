# Universal CCG Scraper Plugin
# ============================
# Plugin for scraping cards from multiple CCGs via CCGTrader.net

## Overview
This plugin allows the Silhouette Card Maker to scrape card data from CCGTrader.net, a comprehensive database covering hundreds of collectible card games. Unlike single-game plugins, this universal scraper can handle multiple CCGs from a single source.

## Features
- **Multi-Game Support**: Access cards from hundreds of CCGs in one place
- **Intelligent Search**: Find similar cards across different games
- **Popular Games Integration**: Quick access to major CCGs like MTG, Pokémon, Yu-Gi-Oh!
- **Flexible Collection Management**: Create mixed collections from multiple games
- **Cross-Game Analysis**: Find thematic connections between games
- **Batch Processing**: Handle large numbers of cards efficiently

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# List available games
python ccgt_cli.py games --popular-only

# Get cards from a specific game
python ccgt_cli.py game "Magic: The Gathering" --max-cards 50

# Search for cards across games
python ccgt_cli.py search "Lightning" --max-results 30

# Generate collection from popular games
python ccgt_cli.py popular --num-cards-per-game 15

# Find variants of a card across games
python ccgt_cli.py cross-game "Dragon" --collection-name "Dragon Collection"

# Generate sample data for testing
python ccgt_cli.py sample --num-games 5 --cards-per-game 10
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Browse available games from CCGTrader.net
2. Search for cards across multiple games
3. Create collections from different CCGs
4. Find thematic connections between games
5. Generate popular game collections

## Data Sources
- **CCGTrader.net**: https://www.ccgtrader.net/games/ - Comprehensive CCG database
- **Automated Updates**: The site automatically updates with new releases
- **Multiple Formats**: Supports various card data formats from different publishers

## Supported Games
The plugin can access cards from hundreds of CCGs including:

### Major TCGs
- **Magic: The Gathering** - The original TCG with thousands of cards
- **Pokémon TCG** - Nintendo's popular creature-battling game
- **Yu-Gi-Oh! TCG** - Konami's strategic card game
- **Digimon Card Game** - Bandai's digital monster battles
- **Dragon Ball Super Card Game** - Anime-themed combat cards

### Classic CCGs
- **Middle Earth CCG** - Tolkien-inspired adventure game
- **Legend of the Five Rings** - Fantasy adventure in Rokugan
- **Dune CCG** - Sci-fi strategy based on Frank Herbert's universe
- **Star Wars CCG** - Galactic combat and diplomacy
- **Star Trek CCG** - Space exploration and conflict

### Modern Games
- **Final Fantasy TCG** - Square Enix's JRPG-themed cards
- **Flesh and Blood** - Physical skill-based TCG
- **Grand Archive** - Fantasy world-building game
- **One Piece Card Game** - Pirate-themed battles
- **My Hero Academia CCG** - Superhero academy duels

## Current Status
- ✅ Plugin structure implemented
- ✅ Multi-game data models created
- ✅ CLI interface functional
- ✅ GUI integration ready
- 🔄 Card parsing (framework ready for site structure analysis)
- 🔄 Image fetching (framework ready for implementation)

## Limitations
- **Site Structure Dependent**: Relies on CCGTrader.net maintaining consistent format
- **Rate Limiting**: Should respect site crawling policies
- **Image Sources**: Card images may need alternative hosting sources
- **Data Completeness**: Depends on CCGTrader.net's database coverage

## Future Enhancements
- Integration with official game APIs where available
- Advanced card filtering and sorting options
- Deck building recommendations across games
- Tournament data integration
- Community-driven card database expansion

## Technical Notes
- Uses web scraping for data extraction (respectful rate limiting implemented)
- Flexible card data model supports various CCG formats
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins for consistency

## Game-Specific Features
The plugin handles various card types and mechanics:

### Magic: The Gathering
- **Card Types**: Creatures, Sorceries, Instants, Artifacts, Enchantments, Lands
- **Colors**: White, Blue, Black, Red, Green, Colorless
- **Mana System**: Resource generation and costs
- **Keywords**: Flying, Trample, Haste, etc.

### Pokémon TCG
- **Card Types**: Pokémon, Trainer, Energy
- **Evolutions**: Basic → Stage 1 → Stage 2 progression
- **Energy Types**: Grass, Fire, Water, Lightning, Psychic, Fighting, Darkness, Metal, Fairy
- **Attacks**: Move-based combat system

### Yu-Gi-Oh!
- **Card Types**: Monster, Spell, Trap
- **Monster Types**: Normal, Effect, Fusion, Ritual, Synchro, Xyz, Pendulum, Link
- **Attributes**: Light, Dark, Water, Fire, Earth, Wind
- **Levels/Ranks**: Monster power scaling

## Collection Types
Users can create various types of collections:

- **Single Game**: Focus on one CCG's cards and mechanics
- **Multi-Game**: Mix cards from different games for variety
- **Thematic**: Group cards by theme (dragons, magic, etc.) across games
- **Popular Mix**: Curated selection from major CCGs
- **Historical**: Classic cards from vintage games

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "universal-ccg" tag.

Note: This plugin provides access to a vast library of CCG data, but users should be aware of copyright and licensing restrictions when using card data for commercial purposes.
