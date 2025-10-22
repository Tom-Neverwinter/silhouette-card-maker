# Weiss Schwarz Plugin
# ===================
# Plugin for fetching Weiss Schwarz Trading Card Game decks and images

## Overview
This plugin allows the Silhouette Card Maker to process Weiß Schwarz decks from community sites and official resources. Weiß Schwarz is renowned for its massive anime crossovers, featuring characters from Attack on Titan, Fate/stay night, Re:Zero, and dozens of other popular series.

## Unique Features
- **Massive Anime Crossovers:** Play with characters from countless anime series in one game
- **Complex Gameplay:** Deep strategy with multiple card types and levels
- **International Appeal:** Very popular in Japan, growing globally
- **Massive Card Pool:** Over 20,000+ cards across numerous franchises
- **Regular Expansions:** Constant new content from various anime series

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Scrape recent tournaments from WeissTeaTime
python ws_cli.py --source weissteatime --format standard --num-tournaments 5

# Fetch images for scraped decks
python ws_cli.py --fetch-images --save-decks my_decks.txt

# Process specific tournament
python ws_cli.py --tournament-url "https://weissteatime.com/tournament/123"

# Parse a deck from EncoreDecks URL
python ws_cli.py --deck-url "https://www.encoredecks.com/deck/12345"

# Parse a deck from DeckLog URL
python ws_cli.py --deck-url "https://decklog.bushiroad.com/deck/67890"

# Search for a specific card
python ws_cli.py --search-card "Saber"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for data source and format preferences
2. Scrape deck data from WeissTeaTime and official sites
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **WeissTeaTime:** https://weissteatime.com/ - Primary tournament deck lists and meta analysis
- **Official Site:** https://en.ws-tcg.com/ - Official tournament results and deck recipes
- **EncoreDecks:** Community deck building platform (mentioned in community)
- **Reddit:** r/WeissSchwarz for community discussion and deck sharing

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Tournament discovery framework
- ✅ Multiple data source support
- ✅ Real card database integration (EncoreDecks, DeckLog)
- ✅ Deck URL parsing (EncoreDecks, DeckLog)
- ✅ Multi-source image fetching (YYT, DeckLog, EncoreDecks)
- ✅ Card search functionality
- 🔄 Full site scraping (framework ready for implementation)

## Supported Franchises
Weiß Schwarz features cards from:
- **Attack on Titan**
- **Fate/stay night** series
- **Kill la Kill**
- **Re:Zero**
- **Persona 3-5**
- **Sword Art Online**
- **KonoSuba**
- **Lucky Star**
- **The Melancholy of Haruhi Suzumiya**
- And many more!

## Game Mechanics
- **Level System:** Cards range from Level 0 to Level 3
- **Color System:** Yellow, Green, Red, Blue card colors
- **Card Types:** Characters, Events, Climax cards
- **Trigger System:** Special effects that activate during play
- **Resonance:** Card synergy mechanics

## Card Dimensions
Weiß Schwarz cards use the **Japanese standard size**:
- **Size:** 59mm x 86mm (2.32" x 3.39")
- **Compatible with:** Silhouette Card Maker's `japanese` card size
- **Paper formats:** Works with `letter`, `a4` paper sizes

## Future Enhancements
- Integration with comprehensive Weiß Schwarz card databases
- Advanced tournament result parsing from multiple sources
- Franchise filtering and collection management
- Meta analysis and deck archetype identification

## Technical Notes
- Uses web scraping for tournament data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture
- Follows same patterns as other TCG plugins

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "weiss-schwarz" tag.

Note: Weiß Schwarz has a massive card pool and complex gameplay - data sources may vary in completeness compared to more mainstream TCGs.
