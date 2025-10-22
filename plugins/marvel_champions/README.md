# Marvel Champions LCG Plugin
# ============================
# Plugin for fetching Marvel Champions Living Card Game decks and scenarios

## Overview
This plugin allows the Silhouette Card Maker to process Marvel Champions LCG decks from community sites and databases. Marvel Champions is a cooperative card game where players take on the roles of Marvel heroes to stop villains in scenario-based gameplay.

## Unique Features
- **Cooperative Gameplay:** Unlike competitive TCGs, focuses on team-based scenario completion
- **Living Card Game Format:** No random boosters - curated expansions with known contents
- **Hero vs Villain:** Players build decks around specific heroes to tackle villain scenarios
- **Scenario-Based:** Game revolves around completing scenarios rather than tournaments

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Get scenarios from Hall of Heroes
python mc_cli.py --mode scenarios --source hoh --num-items 5

# Get hero information from MarvelCDB
python mc_cli.py --mode heroes --source cdb

# Fetch images for processed decks
python mc_cli.py --fetch-images --save-decks my_decks.txt
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for processing mode (scenarios, heroes, or decks)
2. Fetch data from selected sources (MarvelCDB, Hall of Heroes)
3. Optionally download card images
4. Save results for card creation

## Data Sources
- **MarvelCDB:** https://marvelcdb.com/ - Primary deck builder and community site
- **Hall of Heroes:** https://hallofheroeslcg.com/ - Scenario database and card browser
- **CardGameDB:** http://www.cardgamedb.com/index.php/marvelchampions/ - Alternative deck builder
- **Reddit:** r/marvelchampionslcg for community discussion

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Multiple data source support
- ✅ Co-op scenario framework
- 🔄 Image fetching (placeholder - needs database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Game Mechanics
- **Heroes:** Players choose Marvel heroes (Spider-Man, Iron Man, etc.)
- **Villains:** Scenario-based challenges with unique mechanics
- **Aspects:** Hero classes (Leadership, Justice, Aggression, Protection)
- **Modular Sets:** Encounter sets that modify scenarios

## Future Enhancements
- Integration with MarvelCDB API for comprehensive deck data
- Advanced scenario parsing from Hall of Heroes
- Hero class filtering and aspect recommendations
- Scenario difficulty analysis and deck suggestions

## Technical Notes
- Focuses on cooperative play rather than competitive tournaments
- LCG format means predictable card acquisition (no randomness)
- Scenario-based gameplay requires different data structures than TCGs
- Maintains compatibility with existing Silhouette Card Maker architecture

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "marvel-champions" tag.

Note: Marvel Champions is a cooperative game - data focuses on scenario completion rather than competitive rankings.
