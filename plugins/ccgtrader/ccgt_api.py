# Universal CCG API Module for CCGTrader.net
# ===========================================
# This module provides API functions for the universal CCG scraper

import os
import sys
import requests
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from ccgt_scraper import UniversalCard, UniversalGame, UniversalCollection

# -----------------------------
# Card Data Management
# -----------------------------
def search_universal_cards(card_name: str, games_filter=None, max_results=50) -> List[UniversalCard]:
    """
    Search for cards across multiple CCGs.

    Args:
        card_name: Name to search for
        games_filter: Optional list of game names to limit search to
        max_results: Maximum number of results to return

    Returns:
        List of matching UniversalCard objects
    """
    print(f"Searching for '{card_name}' across CCGTrader.net...")

    # For demo purposes, return sample cards that match the search
    # In a real implementation, this would call the scraper functions

    sample_cards = []

    # Simulate finding cards in different games
    popular_games = [
        "Magic: The Gathering", "Pokémon", "Yu-Gi-Oh!", "Digimon",
        "Dragon Ball Super", "One Piece", "My Hero Academia"
    ]

    if games_filter:
        popular_games = [g for g in popular_games if g in games_filter]

    card_counter = 0
    for game in popular_games:
        if card_counter >= max_results:
            break

        # Create sample cards that match the search
        for i in range(2):  # 2 cards per game
            if card_counter >= max_results:
                break

            card = UniversalCard(
                name=f"{card_name} - {game} Version {i+1}",
                game=game,
                set_name=f"{game} Base Set",
                set_code="BASE",
                card_number=f"{card_counter+1:03d}",
                rarity=["Common", "Uncommon", "Rare"][card_counter % 3],
                card_type="Creature" if i == 0 else "Spell",
                cost=2 + (card_counter % 3),
                attack=1 + (card_counter % 3) if i == 0 else None,
                defense=card_counter % 2 if i == 0 else None,
                description=f"Sample card matching '{card_name}' from {game}",
                image_url=f"https://example.com/cards/{game.lower().replace(' ', '_')}_{card_counter+1}.png"
            )
            sample_cards.append(card)
            card_counter += 1

    return sample_cards


def get_game_cards(game_name: str, max_cards=100) -> List[UniversalCard]:
    """
    Get cards from a specific game.

    Args:
        game_name: Name of the game
        max_cards: Maximum cards to return

    Returns:
        List of UniversalCard objects for that game
    """
    print(f"Fetching cards for {game_name}...")

    # Return sample cards for the game
    sample_cards = []

    game_sets = [f"{game_name} Set 1", f"{game_name} Set 2", f"{game_name} Expansion"]

    card_counter = 0
    for set_name in game_sets:
        for i in range(min(10, max_cards // len(game_sets))):  # Distribute cards across sets
            if card_counter >= max_cards:
                break

            card = UniversalCard(
                name=f"Card {card_counter+1} from {set_name}",
                game=game_name,
                set_name=set_name,
                set_code=set_name[:3].upper(),
                card_number=f"{card_counter+1:03d}",
                rarity=["Common", "Uncommon", "Rare"][card_counter % 3],
                card_type=["Creature", "Spell", "Artifact"][card_counter % 3],
                cost=1 + (card_counter % 4),
                attack=1 + (card_counter % 3),
                defense=card_counter % 2,
                description=f"Sample card from {game_name}",
                image_url=f"https://example.com/cards/{game_name.lower().replace(' ', '_')}_{card_counter+1}.png"
            )
            sample_cards.append(card)
            card_counter += 1

    return sample_cards


def get_popular_games_cards() -> Dict[str, List[UniversalCard]]:
    """
    Get cards from popular CCGs.

    Returns:
        Dictionary mapping game names to lists of cards
    """
    popular_games = [
        "Magic: The Gathering",
        "Pokémon",
        "Yu-Gi-Oh!",
        "Digimon",
        "Dragon Ball Super"
    ]

    games_cards = {}

    for game in popular_games:
        games_cards[game] = get_game_cards(game, 20)

    return games_cards


# -----------------------------
# Collection Management
# -----------------------------
def create_game_collection(game_name: str, collection_name: str) -> UniversalCollection:
    """
    Create a collection for a specific game.

    Args:
        game_name: Name of the game
        collection_name: Name for the collection

    Returns:
        UniversalCollection object
    """
    cards = get_game_cards(game_name, 50)  # Get up to 50 cards
    return UniversalCollection(collection_name, cards)


def create_multi_game_collection(card_name: str, collection_name: str, games_list=None) -> UniversalCollection:
    """
    Create a collection from cards found across multiple games.

    Args:
        card_name: Name pattern to search for
        collection_name: Name for the collection
        games_list: Optional list of specific games to search

    Returns:
        UniversalCollection object
    """
    cards = search_universal_cards(card_name, games_list, 30)
    return UniversalCollection(collection_name, cards)


# -----------------------------
# Export Functions
# -----------------------------
def save_universal_collection_to_json(collection: UniversalCollection, output_file: str):
    """
    Save universal collection data to JSON format.

    Args:
        collection: UniversalCollection object to save
        output_file: Path where to save the JSON file
    """
    # Convert cards to dictionaries
    cards_data = []
    for card in collection.cards:
        card_dict = {
            "name": card.name,
            "game": card.game,
            "set_name": card.set_name,
            "set_code": card.set_code,
            "card_number": card.card_number,
            "rarity": card.rarity,
            "card_type": card.card_type,
            "cost": card.cost,
            "attack": card.attack,
            "defense": card.defense,
            "description": card.description,
            "image_url": card.image_url,
            "attributes": card.attributes
        }
        cards_data.append(card_dict)

    data = {
        "name": collection.name,
        "games": collection.games,
        "total_cards": len(collection.cards),
        "cards": cards_data
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Saved universal collection with {len(collection.cards)} cards to {output_file}")


def load_universal_collection_from_json(input_file: str) -> UniversalCollection:
    """
    Load universal collection data from JSON format.

    Args:
        input_file: Path to the JSON file to load

    Returns:
        UniversalCollection object loaded from file
    """
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Convert card dictionaries back to UniversalCard objects
    cards = []
    for card_data in data["cards"]:
        card = UniversalCard(
            name=card_data["name"],
            game=card_data["game"],
            set_name=card_data["set_name"],
            set_code=card_data["set_code"],
            card_number=card_data["card_number"],
            rarity=card_data["rarity"],
            card_type=card_data.get("card_type"),
            cost=card_data.get("cost"),
            attack=card_data.get("attack"),
            defense=card_data.get("defense"),
            description=card_data.get("description"),
            image_url=card_data.get("image_url"),
            **card_data.get("attributes", {})
        )
        cards.append(card)

    return UniversalCollection(data["name"], cards)


# -----------------------------
# Batch Processing
# -----------------------------
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


# -----------------------------
# Game Discovery
# -----------------------------
def discover_available_games() -> List[UniversalGame]:
    """
    Discover all available games on CCGTrader.net.

    Returns:
        List of UniversalGame objects
    """
    try:
        from ccgt_scraper import get_games_list
        return get_games_list()
    except ImportError:
        # Fallback if scraper module not available
        return [
            UniversalGame("Magic: The Gathering", "https://www.ccgtrader.net/games/magic-the-gathering-ccg"),
            UniversalGame("Pokémon", "https://www.ccgtrader.net/games/pokemon-ccg"),
            UniversalGame("Yu-Gi-Oh!", "https://www.ccgtrader.net/games/yu-gi-oh-tcg"),
            UniversalGame("Digimon", "https://www.ccgtrader.net/games/digimon-ccg"),
            UniversalGame("Dragon Ball Super", "https://www.ccgtrader.net/games/dragon-ball-super-card-game")
        ]


def get_game_info(game_name: str) -> Optional[UniversalGame]:
    """
    Get detailed information about a specific game.

    Args:
        game_name: Name of the game

    Returns:
        UniversalGame object with detailed information
    """
    games = discover_available_games()
    for game in games:
        if game.name.lower() == game_name.lower():
            return game
    return None


# -----------------------------
# Advanced Features
# -----------------------------
def get_cross_game_collection(card_name: str, collection_name: str) -> UniversalCollection:
    """
    Create a collection that finds similar cards across different games.

    Args:
        card_name: Base name to search for variants
        collection_name: Name for the collection

    Returns:
        UniversalCollection with cards from multiple games
    """
    # This would implement logic to find similar cards across games
    # For example, find "Lightning Bolt" in MTG, "Lightning" in Pokémon, etc.

    cards = search_universal_cards(card_name, max_results=20)

    # Filter to cards that are conceptually similar
    similar_cards = []
    for card in cards:
        # Simple heuristic: cards with similar names or types
        if (card_name.lower() in card.name.lower() or
            card.card_type in ["Spell", "Instant", "Energy"]):
            similar_cards.append(card)

    return UniversalCollection(collection_name, similar_cards)
