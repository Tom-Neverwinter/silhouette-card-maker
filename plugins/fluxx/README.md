# Fluxx Plugin
# ============
# Plugin for fetching Fluxx card collections and data

## Overview
This plugin allows the Silhouette Card Maker to process Fluxx card collections from various sources. Fluxx is a unique card game by Looney Labs where the rules and win conditions constantly change as cards are played.

## Important Note
**Fluxx is NOT a traditional trading card game (TCG) like Magic: The Gathering or Pokémon.** It is a standalone card game with ever-changing rules:

- **Rules Change:** Cards modify how the game is played (Draw 2, Play 3, etc.)
- **Win Conditions Change:** Goals determine how to win and change constantly
- **No Fixed Strategy:** The game evolves as you play
- **Humorous Theme:** Light-hearted gameplay with funny card effects

This plugin treats Fluxx as a card collection manager focusing on the unique rule-changing mechanics.

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Get cards from Looney Labs
python fluxx_cli.py --source looney --card-type keeper --num-cards 10

# Fetch images for card collection
python fluxx_cli.py --mode collection --fetch-images

# Search for specific card
python fluxx_cli.py --card-name "The Brain"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for processing mode (cards, collection, or search)
2. Fetch card data from Looney Labs and BoardGameGeek
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **Looney Labs:** https://www.looneylabs.com/games/fluxx - Official Fluxx game site
- **BoardGameGeek:** https://boardgamegeek.com/boardgame/258/fluxx - Comprehensive game information
- **Wikipedia:** https://en.wikipedia.org/wiki/Fluxx - Game overview and history
- **RuleBook Wiki:** https://rulebook.fandom.com/wiki/Fluxx - Detailed rules and card information

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Card collection framework
- ✅ Multiple data source support
- 🔄 Image fetching (placeholder - needs database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Card Types
- **Keeper Cards:** Items, people, or concepts you collect
- **Goal Cards:** Win conditions that change during play
- **Action Cards:** One-time effects and card manipulation
- **New Rule Cards:** Change how the game is played
- **Creeper Cards:** Negative cards that hinder players

## Game Mechanics
- **Dynamic Rules:** Rules change as New Rule cards are played
- **Changing Goals:** Win conditions evolve throughout the game
- **Hand Limit:** Players can only hold a certain number of cards
- **Play Limit:** Players can only play a certain number of cards per turn
- **Keeper Collection:** Players collect Keepers to match Goal requirements

## Supported Editions
- **Core Fluxx:** Original game with basic mechanics
- **Themed Versions:** Batman, Monty Python, Star Trek, and many more
- **Expansions:** Add new cards and mechanics to existing games
- **Promo Cards:** Special cards from conventions and events

## Future Enhancements
- Integration with Looney Labs official card database API
- Advanced card filtering by type, edition, and effects
- Rule change tracking and game state simulation
- Collection management for multiple Fluxx editions

## Technical Notes
- Focuses on card collection management for rule-changing gameplay
- Uses web scraping for card data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "fluxx" tag.

Note: Fluxx is a casual, rule-changing card game - this plugin focuses on card collection rather than competitive tournament data.
