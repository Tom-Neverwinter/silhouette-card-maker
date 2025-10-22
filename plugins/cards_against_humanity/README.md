# Cards Against Humanity Plugin
# =============================
# Plugin for fetching Cards Against Humanity card collections and data

## Overview
This plugin allows the Silhouette Card Maker to process Cards Against Humanity card collections from various sources. Cards Against Humanity is a humorous party card game featuring black question cards and white answer cards with often offensive and politically incorrect content.

## Important Warning
**⚠️ CARDS AGAINST HUMANITY CONTAINS MATURE, OFFENSIVE CONTENT**
- Not suitable for all audiences
- Contains dark humor, sexual content, and politically incorrect themes
- Use only with appropriate adult audiences
- Parental discretion strongly advised

This plugin treats CAH as a card collection manager for party game purposes.

## Installation
1. Place this plugin folder in the `plugins/` directory of your Silhouette Card Maker
2. Ensure dependencies are installed:
   ```bash
   pip install requests lxml
   ```

## Usage

### Command Line
```bash
# Get cards from CAH database
python cah_cli.py --source database --card-type black --num-cards 10

# Fetch images for card collection
python cah_cli.py --mode collection --fetch-images

# Search for specific card
python cah_cli.py --card-text "Why can't I sleep at night?"
```

### GUI Integration
The plugin can be called from the main GUI through the plugin system. It will:
1. Prompt for processing mode (cards, collection, or search)
2. Fetch card data from CAH database and community sources
3. Optionally attempt to download card images
4. Save results for card creation

## Data Sources
- **Unofficial CAH Database:** https://cahdb.online/ - Comprehensive card database with content warnings
- **Community Spreadsheets:** Player-maintained card lists and expansions
- **EditionCards:** https://editioncards.com/cards-against-humanity-card-list/ - Complete card lists
- **Reddit:** r/cardsagainsthumanity for community discussion

## Current Status
- ✅ Basic plugin structure implemented
- ✅ Card collection framework (black/white card separation)
- ✅ Multiple data source support
- 🔄 Image fetching (placeholder - needs database integration)
- 🔄 Full site scraping (framework ready for implementation)

## Card Types
- **Black Cards (Questions):** Prompts that require white card answers
- **White Cards (Answers):** Humorous responses to black card questions
- **Pick Count:** Black cards specify how many white cards to play
- **Expansions:** Main game plus numerous themed expansion packs

## Game Mechanics
- **Question & Answer:** Black cards pose questions, white cards provide answers
- **Judge System:** Players take turns judging the funniest combination
- **Winning Condition:** First player to reach a certain number of "Awesome Points"
- **Offensive Content:** Game is designed to be politically incorrect and humorous

## Supported Content
- **Main Game:** 100 black cards, 500 white cards
- **Expansions:** 90+ themed expansion packs
- **Custom Cards:** Community-created cards and house rules
- **International Versions:** Localized versions in multiple languages

## Future Enhancements
- Integration with official CAH database API (if available)
- Advanced card filtering by expansion, offensiveness level
- Content warning system and age-appropriate filtering
- Collection management for multiple CAH editions

## Technical Notes
- Focuses on card collection management for party game purposes
- Uses web scraping for card data (respectful rate limiting implemented)
- Images would be sourced from official databases when available
- Maintains compatibility with existing Silhouette Card Maker architecture

## Content Warning
This plugin processes Cards Against Humanity content, which includes:
- Dark humor and offensive themes
- Sexual content and innuendo
- Politically incorrect stereotypes
- Violence and disturbing concepts

**Use only with consenting adult audiences who understand and appreciate this style of humor.**

## Support
For issues or feature requests, check the main Silhouette Card Maker repository or create an issue with the "cards-against-humanity" tag.
