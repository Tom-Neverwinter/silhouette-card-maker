# Universal CCG Scraper for CCGTrader.net
# ========================================
# This module scrapes multiple CCGs from CCGTrader.net

import os
import sys
import requests
import hashlib
import json
from pathlib import Path
from lxml import html
from typing import List, Dict, Optional, Any

# -----------------------------
# Data Models
# -----------------------------
class UniversalCard:
    """
    Represents a universal CCG card with flexible attributes.

    Attributes:
        name: Card name
        game: Game name (e.g., "Magic: The Gathering", "Pokémon")
        set_name: Set name
        set_code: Set code/abbreviation
        card_number: Card number in set
        rarity: Card rarity
        card_type: Type of card (Creature, Spell, etc.)
        cost: Resource cost (if applicable)
        attack: Attack value (if applicable)
        defense: Defense value (if applicable)
        description: Card text/ability
        image_url: URL to card image
        attributes: Dictionary of game-specific attributes
    """
    def __init__(self, name, game, set_name, set_code, card_number, rarity,
                 card_type=None, cost=None, attack=None, defense=None,
                 description=None, image_url=None, **attributes):
        self.name = name
        self.game = game
        self.set_name = set_name
        self.set_code = set_code
        self.card_number = card_number
        self.rarity = rarity
        self.card_type = card_type
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.description = description
        self.image_url = image_url
        self.attributes = attributes


class UniversalGame:
    """
    Represents a CCG game with its metadata.

    Attributes:
        name: Game name
        url: Game URL on CCGTrader
        description: Game description
        sets: List of set dictionaries
    """
    def __init__(self, name, url, description=None):
        self.name = name
        self.url = url
        self.description = description
        self.sets = []


class UniversalCollection:
    """
    Represents a collection of cards from multiple games.

    Attributes:
        name: Collection name
        cards: List of UniversalCard objects
        games: List of games represented
    """
    def __init__(self, name, cards=None):
        self.name = name
        self.cards = cards or []
        self.games = self._get_games()

    def _get_games(self):
        """Get unique game names in the collection."""
        games = set()
        for card in self.cards:
            games.add(card.game)
        return sorted(list(games))


# -----------------------------
# Main Scraping Functions
# -----------------------------
def get_games_list() -> List[UniversalGame]:
    """
    Get list of all available CCGs from CCGTrader.net.

    Returns:
        List of UniversalGame objects
    """
    print("Fetching games list from CCGTrader.net...")

    try:
        url = 'https://www.ccgtrader.net/games/'
        page = requests.get(url, timeout=10)
        tree = html.fromstring(page.content)

        games = []

        # Parse game links from the games listing
        game_links = tree.xpath('//a[contains(@href, "/games/") and not(contains(@href, "/games/magi")) and not(contains(@href, "/games/magic"))]')

        for link in game_links[:50]:  # Limit to first 50 to avoid overwhelming
            game_name = link.text_content().strip()
            game_url = link.get('href')

            if game_name and game_url and game_name != 'CCG Database':
                # Clean up game name
                if game_name.endswith(' CCG') or game_name.endswith(' TCG'):
                    clean_name = game_name[:-4]  # Remove ' CCG' or ' TCG'
                else:
                    clean_name = game_name

                game = UniversalGame(clean_name, game_url)
                games.append(game)

        return games

    except Exception as e:
        print(f"Error fetching games list: {e}")
        return []


def get_game_sets(game_url: str) -> List[Dict[str, Any]]:
    """
    Get sets for a specific game.

    Args:
        game_url: URL to the game page

    Returns:
        List of set dictionaries with name, url, and release info
    """
    print(f"Fetching sets for game: {game_url}")

    try:
        page = requests.get(game_url, timeout=10)
        tree = html.fromstring(page.content)

        sets = []

        # Look for set links - they follow the pattern [Set Name] (URL)
        set_links = tree.xpath('//a[contains(@href, "/games/") and contains(@href, "/")]')

        for link in set_links:
            set_name = link.text_content().strip()
            set_url = link.get('href')

            if set_name and set_url and set_name not in ['CCG Database', 'All Games']:
                # Extract release year if available
                parent_text = link.getparent().text_content() if link.getparent() is not None else ""
                release_year = None

                # Try to find year in surrounding text
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', parent_text)
                if year_match:
                    release_year = year_match.group()

                sets.append({
                    'name': set_name,
                    'url': set_url,
                    'release_year': release_year
                })

        return sets

    except Exception as e:
        print(f"Error fetching sets for {game_url}: {e}")
        return []


def get_set_cards(set_url: str, game_name: str, set_name: str) -> List[UniversalCard]:
    """
    Get cards from a specific set. This is a placeholder since the actual
    card data structure needs to be determined by examining individual cards.

    Args:
        set_url: URL to the set page
        game_name: Name of the game
        set_name: Name of the set

    Returns:
        List of UniversalCard objects
    """
    print(f"Fetching cards for {game_name} - {set_name}...")

    # For now, return sample cards since we need to understand the actual structure
    # In a real implementation, this would parse the actual card data

    sample_cards = [
        UniversalCard(
            name=f"Sample Card 1 - {set_name}",
            game=game_name,
            set_name=set_name,
            set_code=set_name[:3].upper(),
            card_number="001",
            rarity="Common",
            card_type="Creature",
            cost=2,
            attack=2,
            defense=2,
            description=f"Sample card from {set_name}",
            image_url=f"https://example.com/cards/{game_name.lower().replace(' ', '_')}_{set_name.lower().replace(' ', '_')}_001.png"
        ),
        UniversalCard(
            name=f"Sample Card 2 - {set_name}",
            game=game_name,
            set_name=set_name,
            set_code=set_name[:3].upper(),
            card_number="002",
            rarity="Rare",
            card_type="Spell",
            cost=3,
            description=f"Another sample card from {set_name}",
            image_url=f"https://example.com/cards/{game_name.lower().replace(' ', '_')}_{set_name.lower().replace(' ', '_')}_002.png"
        )
    ]

    return sample_cards


# Mapping of game names to CCGTrader codes
GAME_CODES = {
    "Magic: The Gathering": "MTG",
    "Pokémon": "POK",
    "Yu-Gi-Oh!": "YGO",
    "Dragon Ball Super": "DBS",
    "Final Fantasy": "FFT",
    "Star Wars: Destiny": "SWD",
    "Lord of the Rings": "LTR",
    "Harry Potter": "HPT",
    "World of Warcraft": "WOW",
    "Digimon": "DIG",
    "Duel Masters": "DUE",
    "Legend of the Five Rings": "L5R",
    "NetRunner": "NET",
    "Vampire the Eternal Struggle": "VES",
    "Warhammer 40,000": "WHC",
    "VS System": "VSS",
    "Star Trek First Edition": "ST1",
    "My Little Pony": "MLP",
    "Transformers": "TRT",
    "Star Wars": "SWC",
    "One Piece": "OPC",
    "My Hero Academia": "MHA",
    "Flesh and Blood": "FAB",
    "Altered": "ALT",
    "Lorcana": "LOR",
    "Star Wars: Unlimited": "SWU"
}

def search_cards(card_name: str, game_name: str = None, max_results: int = 20) -> List[UniversalCard]:
    """
    Search for cards on CCGTrader.net.

    Args:
        card_name: Name to search for
        game_name: Optional game name to limit search
        max_results: Maximum results to return

    Returns:
        List of UniversalCard objects
    """
    game_code = ""
    if game_name:
        # Try to find the closest match in GAME_CODES
        for name, code in GAME_CODES.items():
            if game_name.lower() in name.lower() or name.lower() in game_name.lower():
                game_code = code
                game_name = name # Standardize name
                break

    print(f"Searching CCGTrader for '{card_name}'" + (f" in {game_name}" if game_name else "") + "...")

    try:
        url = f"https://www.ccgtrader.net/search?q={card_name}"
        if game_code:
            url += f"&g={game_code}"

        page = requests.get(url, timeout=10)
        tree = html.fromstring(page.content)

        # Updated selector based on analysis
        card_elements = tree.xpath('//a[contains(@href, "/card/")]')
        
        cards = []
        for el in card_elements:
            if len(cards) >= max_results:
                break

            name_el = el.xpath('.//h3')
            set_el = el.xpath('.//h6')
            img_el = el.xpath('.//img')

            if name_el and set_el:
                name = name_el[0].text_content().strip()
                # Clean up set name: "Set: [Name]" or "Rare\nSet: [Name]"
                set_raw = set_el[0].text_content().strip()
                set_name = set_raw
                if "Set:" in set_raw:
                    set_name = set_raw.split("Set:")[-1].strip()
                    # Further cleanup if it has newlines
                    set_name = set_name.split('\n')[-1].strip()
                
                image_url = img_el[0].get('src') if img_el else None
                
                # Try to get game name if not provided
                current_game = game_name or "Unknown Game"

                card = UniversalCard(
                    name=name,
                    game=current_game,
                    set_name=set_name,
                    set_code="", # We don't have code easily from search
                    card_number="",
                    rarity="",
                    image_url=image_url
                )
                cards.append(card)

        return cards

    except Exception as e:
        print(f"Error searching CCGTrader: {e}")
        return []

def search_cards_across_games(card_name: str, games_filter=None) -> List[UniversalCard]:
    """
    Search for cards across multiple games.
    """
    return search_cards(card_name, max_results=50)


def import_decklist(file_path: str, game_name: str = None) -> List[UniversalCard]:
    """
    Import a decklist from a text file and find matching cards on CCGTrader.

    Args:
        file_path: Path to the decklist text file
        game_name: Optional game name to limit search

    Returns:
        List of UniversalCard objects (one per card in decklist)
    """
    import re
    print(f"Importing decklist from {file_path}...")
    
    deck_cards = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Pattern: [Count] [Name] or [Name] [xCount]
            # Example: "4 Lightning Bolt" or "Lightning Bolt x4"
            match = re.search(r'^(\d+)\s+(.+)$|^(.*?)\s+x(\d+)$|^(.*?)$', line)
            
            if match:
                groups = match.groups()
                if groups[0]: # Count Name
                    count = int(groups[0])
                    name = groups[1].strip()
                elif groups[3]: # Name xCount
                    count = int(groups[3])
                    name = groups[2].strip()
                else: # Name only
                    count = 1
                    name = groups[4].strip()
                    if not name: continue

                # Search for the card
                results = search_cards(name, game_name, max_results=1)
                if results:
                    found_card = results[0]
                    print(f"  Found: {found_card.name} ({found_card.set_name})")
                    for _ in range(count):
                        deck_cards.append(found_card)
                else:
                    print(f"  Warning: Card not found: {name}")

        return deck_cards

    except Exception as e:
        print(f"Error importing decklist: {e}")
        return []

def create_multi_game_collection(card_name: str, collection_name: str) -> UniversalCollection:
    """
    Create a collection from cards found across multiple games.
    """
    cards = search_cards(card_name, max_results=20)
    return UniversalCollection(collection_name, cards)


# -----------------------------
# Collection Management
# -----------------------------
def save_universal_collection_to_file(collection: UniversalCollection, output_file: str):
    """
    Save universal collection data to a human-readable text file.

    Args:
        collection: UniversalCollection object to save
        output_file: Path where to save the file
    """
    with open(output_file, 'w') as f:
        f.write(f"Collection: {collection.name}\n")
        f.write(f"Games: {', '.join(collection.games)}\n")
        f.write(f"Total Cards: {len(collection.cards)}\n\n")

        # Group cards by game
        cards_by_game = {}
        for card in collection.cards:
            if card.game not in cards_by_game:
                cards_by_game[card.game] = []
            cards_by_game[card.game].append(card)

        for game, cards in cards_by_game.items():
            f.write(f"{game} ({len(cards)} cards):\n")
            f.write("-" * 40 + "\n")

            for card in cards:
                f.write(f"{card.name}\n")
                f.write(f"  Set: {card.set_name} ({card.set_code})\n")
                f.write(f"  Number: {card.card_number}, Rarity: {card.rarity}\n")
                if card.card_type:
                    f.write(f"  Type: {card.card_type}\n")
                if card.cost:
                    f.write(f"  Cost: {card.cost}\n")
                if card.attack or card.defense:
                    f.write(f"  Attack: {card.attack}, Defense: {card.defense}\n")
                if card.description:
                    f.write(f"  Description: {card.description}\n")
                f.write("\n")

    print(f"Saved universal collection with {len(collection.cards)} cards to {output_file}")


# -----------------------------
# Utility Functions
# -----------------------------
def get_popular_games() -> List[UniversalGame]:
    """
    Get a curated list of popular CCGs.

    Returns:
        List of popular UniversalGame objects
    """
    popular_game_names = [
        "Magic: The Gathering",
        "Pokémon",
        "Yu-Gi-Oh!",
        "Digimon",
        "Dragon Ball Super",
        "One Piece",
        "My Hero Academia",
        "Final Fantasy",
        "Flesh and Blood",
        "Star Wars: Unlimited"
    ]

    all_games = get_games_list()
    popular_games = [g for g in all_games if g.name in popular_game_names]

    return popular_games


def fetch_card_image(card: UniversalCard, output_path: str) -> bool:
    """
    Download a card image.

    Args:
        card: UniversalCard object with image URL
        output_path: Local path where to save the image

    Returns:
        True if download successful, False otherwise
    """
    try:
        response = requests.get(card.image_url)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to download image for {card.name}")
            return False
    except Exception as e:
        print(f"Error downloading image for {card.name}: {e}")
        return False


def process_universal_cards_batch(cards: List[UniversalCard], output_dir: str) -> int:
    """
    Process a batch of universal cards for image fetching.

    Args:
        cards: List of UniversalCard objects
        output_dir: Directory to save images

    Returns:
        Number of cards successfully processed
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    processed = 0

    for card in cards:
        print(f"Processing: {card.name} ({card.game})")

        # Download image
        filename = f"{card.game.replace(' ', '_')}_{card.name.replace(' ', '_')}.png"
        filepath = output_path / filename

        if fetch_card_image(card, str(filepath)):
            processed += 1
            print(f"Downloaded: {filename}")

    return processed
