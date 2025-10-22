# Star Realms TCG API Module
# ============================
# This module handles Star Realms card data and image fetching

import os
import sys
import requests
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from sr_scraper import StarRealmsCard, StarRealmsDeck

# -----------------------------
# Card Data Management
# -----------------------------
def search_starrealms_cards(card_name: str) -> List[StarRealmsCard]:
    """
    Search for Star Realms cards by name.

    This implementation integrates with multiple data sources:
    - Official card gallery
    - BoardGameGeek database
    - Community tier lists

    Args:
        card_name: Name of the card to search for

    Returns:
        List of matching StarRealmsCard objects
    """
    print(f"Searching for Star Realms card: {card_name}")

    cards = []

    # Search official gallery
    try:
        official_cards = search_cards_from_official_gallery(card_name)
        cards.extend(official_cards)
    except Exception as e:
        print(f"Error searching official gallery: {e}")

    # Search BoardGameGeek if no results from official
    if not cards:
        try:
            bgg_cards = search_cards_from_boardgamegeek(card_name)
            cards.extend(bgg_cards)
        except Exception as e:
            print(f"Error searching BoardGameGeek: {e}")

    # Search tier lists if still no results
    if not cards:
        try:
            tier_cards = search_cards_from_tier_lists(card_name)
            cards.extend(tier_cards)
        except Exception as e:
            print(f"Error searching tier lists: {e}")

    return cards


def search_cards_from_official_gallery(card_name: str) -> List[StarRealmsCard]:
    """
    Search for cards in the official Star Realms card gallery.

    Args:
        card_name: Name to search for

    Returns:
        List of matching StarRealmsCard objects
    """
    cards = []

    try:
        # Official Star Realms card gallery
        url = 'https://www.starrealms.com/card-gallery/'
        page = requests.get(url)
        from lxml import html
        tree = html.fromstring(page.content)

        # Look for card names in the gallery
        card_elements = tree.xpath('//div[contains(@class, "card")]')

        for element in card_elements:
            name_element = element.xpath('.//h3/text() | .//h4/text() | .//span/text()')
            if name_element:
                name = name_element[0].strip()
                if card_name.lower() in name.lower():
                    # Extract additional card info (simplified)
                    card = StarRealmsCard(
                        name=name,
                        card_type="Ship",  # Would need proper parsing
                        faction="Trade Federation",  # Would need proper parsing
                        cost=3,
                        attack=2,
                        defense=1,
                        ability="Card ability",  # Would need proper parsing
                        set_code="CORE",
                        rarity="Common",
                        image_url=f"https://www.starrealms.com/wp-content/uploads/cards/{name.replace(' ', '_')}.jpg"
                    )
                    cards.append(card)

    except Exception as e:
        print(f"Error searching official gallery: {e}")

    return cards


def search_cards_from_boardgamegeek(card_name: str) -> List[StarRealmsCard]:
    """
    Search for cards in BoardGameGeek database.

    Args:
        card_name: Name to search for

    Returns:
        List of matching StarRealmsCard objects
    """
    cards = []

    try:
        # BoardGameGeek search
        url = f'https://boardgamegeek.com/geeksearch.php?action=search&objecttype=thing&q={card_name}&B1=Go'
        page = requests.get(url)
        from lxml import html
        tree = html.fromstring(page.content)

        # Parse search results (simplified)
        search_results = tree.xpath('//div[contains(@class, "search-results")]')

        for result in search_results:
            title_element = result.xpath('.//a/text()')
            if title_element and card_name.lower() in title_element[0].lower():
                card = StarRealmsCard(
                    name=title_element[0].strip(),
                    card_type="Ship",
                    faction="Trade Federation",
                    cost=3,
                    attack=2,
                    defense=1,
                    ability="BGG listed card",
                    set_code="CORE",
                    rarity="Common",
                    image_url=f"https://example.com/bgg/cards/{card_name.replace(' ', '_')}.png"
                )
                cards.append(card)

    except Exception as e:
        print(f"Error searching BoardGameGeek: {e}")

    return cards


def search_cards_from_tier_lists(card_name: str) -> List[StarRealmsCard]:
    """
    Search for cards in community tier lists.

    Args:
        card_name: Name to search for

    Returns:
        List of matching StarRealmsCard objects
    """
    cards = []

    try:
        # MegaHaulin tier list
        url = 'https://megahaulin.com/2021/10/06/star-realms-card-tier-list-newest-version-added-command-deck-ships-tech/'
        page = requests.get(url)
        from lxml import html
        tree = html.fromstring(page.content)

        # Look for card mentions in tier list
        card_mentions = tree.xpath('//strong | //b | //a')

        for mention in card_mentions:
            text = mention.text_content().strip()
            if card_name.lower() in text.lower() and len(text) < 50:  # Avoid long text matches
                card = StarRealmsCard(
                    name=text,
                    card_type="Ship",
                    faction="Trade Federation",
                    cost=3,
                    attack=2,
                    defense=1,
                    ability="Tier list card",
                    set_code="CORE",
                    rarity="Common",
                    image_url=f"https://example.com/tierlist/cards/{text.replace(' ', '_')}.png"
                )
                cards.append(card)

    except Exception as e:
        print(f"Error searching tier lists: {e}")

    return cards


# -----------------------------
# Collection Management
# -----------------------------
def get_collection_cards(collection_name: str) -> List[StarRealmsCard]:
    """
    Get cards for a specific collection by name.

    Args:
        collection_name: Name of the collection

    Returns:
        List of StarRealmsCard objects in the collection
    """
    # This would integrate with collection storage
    # For now, return sample cards based on collection name
    sample_cards = [
        StarRealmsCard("Trade Pod", "Ship", "Trade Federation", 2, 1, 1, "Draw a card", "CORE", "Common", "https://example.com/trade_pod.png"),
        StarRealmsCard("Cutter", "Ship", "Star Empire", 2, 2, 0, "Combat ability", "CORE", "Common", "https://example.com/cutter.png"),
        StarRealmsCard("Ram", "Ship", "Blob", 3, 3, 0, "High attack", "CORE", "Common", "https://example.com/ram.png"),
        StarRealmsCard("Missile Bot", "Ship", "Machine Cult", 2, 1, 2, "Defense and attack", "CORE", "Common", "https://example.com/missile_bot.png")
    ]

    return sample_cards


def create_collection_from_cards(cards: List[StarRealmsCard], collection_name: str) -> StarRealmsDeck:
    """
    Create a Star Realms collection from a list of cards.

    Args:
        cards: List of StarRealmsCard objects
        collection_name: Name for the collection

    Returns:
        StarRealmsDeck object representing the collection
    """
    return StarRealmsDeck(
        name=collection_name,
        cards=cards,
        player="Collection Owner",
        id=f"sr_collection_{hashlib.md5(collection_name.encode()).hexdigest()[:8]}"
    )


# -----------------------------
# Batch Processing
# -----------------------------
def process_starrealms_cards_batch(cards: List[StarRealmsCard], output_dir: str) -> int:
    """
    Process a batch of Star Realms cards for image fetching.

    Args:
        cards: List of StarRealmsCard objects
        output_dir: Directory to save images

    Returns:
        Number of cards successfully processed
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    processed = 0

    for card in cards:
        print(f"Processing: {card.name}")

        # Download image
        filename = f"{card.name.replace(' ', '_')}.png"
        filepath = output_path / filename

        if fetch_card_image(card, str(filepath)):
            processed += 1
            print(f"Downloaded: {filename}")

    return processed


def fetch_card_image(card: StarRealmsCard, output_path: str) -> bool:
    """
    Download a Star Realms card image.

    Args:
        card: StarRealmsCard object with image URL
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
# Tournament Integration
# -----------------------------
def get_tournament_decks(tournament_url: str) -> List[StarRealmsDeck]:
    """
    Extract deck lists from tournament pages.

    Args:
        tournament_url: URL of the tournament page

    Returns:
        List of StarRealmsDeck objects from the tournament
    """
    decks = []

    try:
        page = requests.get(tournament_url)
        from lxml import html
        tree = html.fromstring(page.content)

        # Parse tournament deck lists (would need site-specific parsing)
        deck_sections = tree.xpath('//div[contains(@class, "deck")]')

        for section in deck_sections:
            # Extract deck information (simplified)
            deck_name = section.xpath('.//h3/text()')
            if deck_name:
                deck_cards = []  # Would parse actual card list
                deck = StarRealmsDeck(
                    name=deck_name[0].strip(),
                    cards=deck_cards,
                    player="Tournament Player",
                    id=f"tourney_deck_{hashlib.md5(tournament_url.encode()).hexdigest()[:8]}"
                )
                decks.append(deck)

    except Exception as e:
        print(f"Error fetching tournament decks: {e}")

    return decks


# -----------------------------
# Export Functions
# -----------------------------
def save_collection_to_json(collection: StarRealmsDeck, output_file: str):
    """
    Save Star Realms collection data to JSON format.

    Args:
        collection: StarRealmsDeck object to save
        output_file: Path where to save the JSON file
    """
    data = {
        "name": collection.name,
        "player": collection.player,
        "id": collection.id,
        "hash": collection.hash,
        "cards": [
            {
                "name": card.name,
                "card_type": card.card_type,
                "faction": card.faction,
                "cost": card.cost,
                "attack": card.attack,
                "defense": card.defense,
                "ability": card.ability,
                "set_code": card.set_code,
                "rarity": card.rarity,
                "image_url": card.image_url
            }
            for card in collection.cards
        ]
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Saved Star Realms collection with {len(collection.cards)} cards to {output_file}")


def load_collection_from_json(input_file: str) -> StarRealmsDeck:
    """
    Load Star Realms collection data from JSON format.

    Args:
        input_file: Path to the JSON file to load

    Returns:
        StarRealmsDeck object loaded from file
    """
    with open(input_file, 'r') as f:
        data = json.load(f)

    cards = [
        StarRealmsCard(
            name=card_data["name"],
            card_type=card_data["card_type"],
            faction=card_data["faction"],
            cost=card_data["cost"],
            attack=card_data["attack"],
            defense=card_data["defense"],
            ability=card_data["ability"],
            set_code=card_data["set_code"],
            rarity=card_data["rarity"],
            image_url=card_data["image_url"]
        )
        for card_data in data["cards"]
    ]

    return StarRealmsDeck(
        name=data["name"],
        cards=cards,
        player=data["player"],
        id=data["id"]
    )
