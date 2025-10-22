# Magi-Nation Duel TCG API Module
# ================================
# This module handles Magi-Nation Duel card data and image fetching

import os
import sys
import requests
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from mnd_scraper import MagiNationCard, MagiNationDeck

# -----------------------------
# Card Data Management
# -----------------------------
def search_magi_nation_cards(card_name: str) -> List[MagiNationCard]:
    """
    Search for Magi-Nation Duel cards by name.

    This implementation integrates with multiple data sources:
    - Magi-Nation Central wiki
    - Magi-Nation.com database
    - Community resources

    Args:
        card_name: Name of the card to search for

    Returns:
        List of matching MagiNationCard objects
    """
    print(f"Searching for Magi-Nation Duel card: {card_name}")

    cards = []

    # Search Magi-Nation Central
    try:
        central_cards = search_cards_from_central(card_name)
        cards.extend(central_cards)
    except Exception as e:
        print(f"Error searching Magi-Nation Central: {e}")

    # Search Magi-Nation.com if no results
    if not cards:
        try:
            official_cards = search_cards_from_official(card_name)
            cards.extend(official_cards)
        except Exception as e:
            print(f"Error searching official site: {e}")

    # Search community resources if still no results
    if not cards:
        try:
            community_cards = search_cards_from_community(card_name)
            cards.extend(community_cards)
        except Exception as e:
            print(f"Error searching community resources: {e}")

    return cards


def search_cards_from_central(card_name: str) -> List[MagiNationCard]:
    """
    Search for cards in the Magi-Nation Central wiki.

    Args:
        card_name: Name to search for

    Returns:
        List of matching MagiNationCard objects
    """
    cards = []

    try:
        # Magi-Nation Central search
        url = f'https://maginationcentral.com/wiki/index.php?search={card_name}'
        page = requests.get(url)
        from lxml import html
        tree = html.fromstring(page.content)

        # Look for card pages in search results
        search_results = tree.xpath('//div[contains(@class, "search-results")]//a')

        for result in search_results:
            title = result.text_content().strip()
            href = result.get('href', '')

            if card_name.lower() in title.lower() and 'Card:' in href:
                # Extract card info from page (simplified)
                card = MagiNationCard(
                    name=title,
                    card_type="Creature",
                    region="Arderial",
                    cost=3,
                    energy=0,
                    attack=2,
                    defense=1,
                    ability="Card from Central wiki",
                    set_code="BASE",
                    rarity="Common",
                    image_url=f"https://maginationcentral.com/wiki/images/cards/{title.replace(' ', '_')}.png"
                )
                cards.append(card)

    except Exception as e:
        print(f"Error searching Magi-Nation Central: {e}")

    return cards


def search_cards_from_official(card_name: str) -> List[MagiNationCard]:
    """
    Search for cards in official Magi-Nation.com database.

    Args:
        card_name: Name to search for

    Returns:
        List of matching MagiNationCard objects
    """
    cards = []

    try:
        # Magi-Nation.com search
        url = f'https://www.magi-nation.com/search?q={card_name}'
        page = requests.get(url)
        from lxml import html
        tree = html.fromstring(page.content)

        # Parse search results (simplified)
        card_results = tree.xpath('//div[contains(@class, "card-result")]')

        for result in card_results:
            card_name_elem = result.xpath('.//h3/text()')
            if card_name_elem:
                name = card_name_elem[0].strip()
                card = MagiNationCard(
                    name=name,
                    card_type="Magi",
                    region="Cald",
                    cost=0,
                    energy=15,
                    attack=0,
                    defense=0,
                    ability="Official database card",
                    set_code="BASE",
                    rarity="Rare",
                    image_url=f"https://www.magi-nation.com/images/cards/{name.replace(' ', '_')}.jpg"
                )
                cards.append(card)

    except Exception as e:
        print(f"Error searching official site: {e}")

    return cards


def search_cards_from_community(card_name: str) -> List[MagiNationCard]:
    """
    Search for cards in community resources and wikis.

    Args:
        card_name: Name to search for

    Returns:
        List of matching MagiNationCard objects
    """
    cards = []

    try:
        # Magi-Nation wiki search
        url = f'https://magination.fandom.com/wiki/Special:Search?query={card_name}'
        page = requests.get(url)
        from lxml import html
        tree = html.fromstring(page.content)

        # Look for card mentions in wiki
        card_mentions = tree.xpath('//a[contains(@title, "card")] | //strong')

        for mention in card_mentions:
            text = mention.text_content().strip()
            if card_name.lower() in text.lower() and len(text) < 50:
                card = MagiNationCard(
                    name=text,
                    card_type="Spell",
                    region="Naroom",
                    cost=2,
                    energy=0,
                    attack=0,
                    defense=0,
                    ability="Community wiki card",
                    set_code="BASE",
                    rarity="Uncommon",
                    image_url=f"https://magination.fandom.com/wiki/images/cards/{text.replace(' ', '_')}.png"
                )
                cards.append(card)

    except Exception as e:
        print(f"Error searching community resources: {e}")

    return cards


# -----------------------------
# Collection Management
# -----------------------------
def get_collection_cards(collection_name: str) -> List[MagiNationCard]:
    """
    Get cards for a specific collection by name.

    Args:
        collection_name: Name of the collection

    Returns:
        List of MagiNationCard objects in the collection
    """
    # This would integrate with collection storage
    # For now, return sample cards based on collection name
    sample_cards = [
        MagiNationCard("Tony Jones", "Magi", "Arderial", 0, 15, 0, 0, "Starting Magi of Arderial", "BASE", "Common", "https://example.com/tony_jones.png"),
        MagiNationCard("Arboll", "Creature", "Arderial", 3, 0, 2, 2, "Tree creature with growth abilities", "BASE", "Common", "https://example.com/arboll.png", "Tony Jones"),
        MagiNationCard("Lightning", "Spell", "Arderial", 2, 0, 0, 0, "Deal 3 damage to target creature", "BASE", "Common", "https://example.com/lightning.png"),
        MagiNationCard("Ancient Staff", "Relic", "Universal", 1, 0, 0, 0, "Add 2 energy to your Magi", "BASE", "Rare", "https://example.com/ancient_staff.png")
    ]

    return sample_cards


def create_collection_from_cards(cards: List[MagiNationCard], collection_name: str) -> MagiNationDeck:
    """
    Create a Magi-Nation Duel collection from a list of cards.

    Args:
        cards: List of MagiNationCard objects
        collection_name: Name for the collection

    Returns:
        MagiNationDeck object representing the collection
    """
    return MagiNationDeck(
        name=collection_name,
        cards=cards,
        player="Collection Owner",
        id=f"mnd_collection_{hashlib.md5(collection_name.encode()).hexdigest()[:8]}"
    )


# -----------------------------
# Batch Processing
# -----------------------------
def process_magi_nation_cards_batch(cards: List[MagiNationCard], output_dir: str) -> int:
    """
    Process a batch of Magi-Nation Duel cards for image fetching.

    Args:
        cards: List of MagiNationCard objects
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


def fetch_card_image(card: MagiNationCard, output_path: str) -> bool:
    """
    Download a Magi-Nation Duel card image.

    Args:
        card: MagiNationCard object with image URL
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
def get_tournament_decks(tournament_url: str) -> List[MagiNationDeck]:
    """
    Extract deck lists from tournament pages.

    Args:
        tournament_url: URL of the tournament page

    Returns:
        List of MagiNationDeck objects from the tournament
    """
    decks = []

    try:
        page = requests.get(tournament_url)
        from lxml import html
        tree = html.fromstring(page.content)

        # Parse tournament deck lists (would need site-specific parsing)
        deck_sections = tree.xpath('//div[contains(@class, "tournament-deck")]')

        for section in deck_sections:
            # Extract deck information (simplified)
            deck_name = section.xpath('.//h3/text()')
            if deck_name:
                deck_cards = []  # Would parse actual card list
                deck = MagiNationDeck(
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
def save_collection_to_json(collection: MagiNationDeck, output_file: str):
    """
    Save Magi-Nation Duel collection data to JSON format.

    Args:
        collection: MagiNationDeck object to save
        output_file: Path where to save the JSON file
    """
    data = {
        "name": collection.name,
        "player": collection.player,
        "id": collection.id,
        "hash": collection.hash,
        "regions": collection.regions,
        "cards": [
            {
                "name": card.name,
                "card_type": card.card_type,
                "region": card.region,
                "cost": card.cost,
                "energy": card.energy,
                "attack": card.attack,
                "defense": card.defense,
                "ability": card.ability,
                "set_code": card.set_code,
                "rarity": card.rarity,
                "image_url": card.image_url,
                "magi_name": card.magi_name
            }
            for card in collection.cards
        ]
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Saved Magi-Nation Duel collection with {len(collection.cards)} cards to {output_file}")


def load_collection_from_json(input_file: str) -> MagiNationDeck:
    """
    Load Magi-Nation Duel collection data from JSON format.

    Args:
        input_file: Path to the JSON file to load

    Returns:
        MagiNationDeck object loaded from file
    """
    with open(input_file, 'r') as f:
        data = json.load(f)

    cards = [
        MagiNationCard(
            name=card_data["name"],
            card_type=card_data["card_type"],
            region=card_data["region"],
            cost=card_data["cost"],
            energy=card_data["energy"],
            attack=card_data["attack"],
            defense=card_data["defense"],
            ability=card_data["ability"],
            set_code=card_data["set_code"],
            rarity=card_data["rarity"],
            image_url=card_data["image_url"],
            magi_name=card_data.get("magi_name")
        )
        for card_data in data["cards"]
    ]

    return MagiNationDeck(
        name=data["name"],
        cards=cards,
        player=data["player"],
        id=data["id"]
    )
