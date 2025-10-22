# Star Realms Scraper Module
# ==========================
# This module handles web scraping of Star Realms cards and data

import os
import sys
import requests
import hashlib
import json
from pathlib import Path
from lxml import html
from typing import List, Dict, Optional

# -----------------------------
# Data Models
# -----------------------------
class StarRealmsCard:
    """
    Represents a Star Realms card with all relevant data.

    Attributes:
        name: Card name
        card_type: Type of card (Ship, Base, Outpost)
        faction: Card faction (Trade Federation, Blob, Star Empire, Machine Cult)
        cost: Resource cost to play
        attack: Combat attack value
        defense: Defense value
        ability: Special ability text
        set_code: Set identifier
        rarity: Card rarity
        image_url: URL to card image
    """
    def __init__(self, name, card_type, faction, cost, attack, defense, ability, set_code, rarity, image_url):
        self.name = name
        self.card_type = card_type
        self.faction = faction
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.ability = ability
        self.set_code = set_code
        self.rarity = rarity
        self.image_url = image_url


class StarRealmsDeck:
    """
    Represents a Star Realms deck/collection.

    Attributes:
        name: Deck/collection name
        cards: List of StarRealmsCard objects
        player: Player who owns this collection
        id: Unique deck identifier
        hash: Unique hash based on card composition
    """
    def __init__(self, name, cards, player, id):
        self.name = name
        self.cards = cards  # List of StarRealmsCard objects
        self.player = player
        self.id = id
        self.hash = self._generate_hash()

    def _generate_hash(self):
        """
        Generate unique hash for deck based on card list.

        Returns:
            MD5 hash string of sorted card list
        """
        card_string = ''.join([f"{card.name}" for card in sorted(self.cards, key=lambda x: x.name)])
        return hashlib.md5(card_string.encode()).hexdigest()


# -----------------------------
# Card Database Functions
# -----------------------------
def get_cards_from_official_gallery(card_type_filter="all", max_cards=50):
    """
    Scrape Star Realms cards from the official card gallery.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of StarRealmsCard objects
    """
    print("Fetching Star Realms cards from official card gallery...")

    try:
        # Official Star Realms card gallery
        url = 'https://www.starrealms.com/card-gallery/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        cards = []

        # Parse card listings (simplified - would need site-specific parsing)
        card_entries = tree.xpath('//div[contains(@class, "card")]')

        for entry in card_entries[:max_cards]:
            # Extract card info (would need actual parsing logic)
            card_name = f"Star Realms Card {len(cards) + 1}"

            card = StarRealmsCard(
                name=card_name,
                card_type="Ship" if len(cards) % 4 == 0 else "Base",
                faction=["Trade Federation", "Blob", "Star Empire", "Machine Cult"][len(cards) % 4],
                cost=2 + (len(cards) % 5),
                attack=1 + (len(cards) % 3),
                defense=0 + (len(cards) % 2),
                ability="Sample ability",
                set_code="CORE",
                rarity="Common",
                image_url=f"https://example.com/starrealms/cards/{card_name.replace(' ', '_')}.png"
            )
            cards.append(card)

        return cards

    except Exception as e:
        print(f"Error scraping official card gallery: {e}")
        return []


def get_cards_from_boardgamegeek(card_type_filter="all", max_cards=50):
    """
    Scrape Star Realms cards from BoardGameGeek complete card list.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of StarRealmsCard objects
    """
    print("Fetching Star Realms cards from BoardGameGeek...")

    try:
        # BoardGameGeek complete card list
        url = 'https://boardgamegeek.com/filepage/187387/star-realms-complete-cards-list'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        cards = []

        # Parse card data from file page (simplified)
        card_sections = tree.xpath('//div[contains(@class, "card-data")]')

        for section in card_sections[:max_cards]:
            # Extract card info (would need actual parsing)
            card = StarRealmsCard(
                name="Sample SR Card",
                card_type="Ship",
                faction="Trade Federation",
                cost=3,
                attack=2,
                defense=1,
                ability="Draw a card",
                set_code="CORE",
                rarity="Common",
                image_url="https://example.com/starrealms/cards/sample.png"
            )
            cards.append(card)

        return cards

    except Exception as e:
        print(f"Error scraping BoardGameGeek: {e}")
        return []


def get_cards_from_tier_list(card_type_filter="all", max_cards=50):
    """
    Scrape Star Realms cards from community tier lists.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of StarRealmsCard objects
    """
    print("Fetching Star Realms cards from community tier lists...")

    try:
        # MegaHaulin tier list
        url = 'https://megahaulin.com/2021/10/06/star-realms-card-tier-list-newest-version-added-command-deck-ships-tech/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        cards = []

        # Parse tier list mentions (simplified)
        card_mentions = tree.xpath('//strong[contains(text(), "Card")]')

        for mention in card_mentions[:max_cards]:
            card_name = mention.text_content().strip()
            if "Card" in card_name:
                card = StarRealmsCard(
                    name=card_name.replace(" Card", ""),
                    card_type="Ship",
                    faction="Trade Federation",
                    cost=3,
                    attack=2,
                    defense=1,
                    ability="Tier list card",
                    set_code="CORE",
                    rarity="Common",
                    image_url=f"https://example.com/starrealms/cards/{card_name.replace(' ', '_')}.png"
                )
                cards.append(card)

        return cards

    except Exception as e:
        print(f"Error scraping tier list: {e}")
        return []


# -----------------------------
# Collection Management
# -----------------------------
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


def search_starrealms_cards(card_name: str) -> List[StarRealmsCard]:
    """
    Search for Star Realms cards by name.

    This is a placeholder implementation. Real implementation would:
    - Query Star Realms databases
    - Use official card databases
    - Fall back to web scraping

    Args:
        card_name: Name of the card to search for

    Returns:
        List of matching StarRealmsCard objects
    """
    # Placeholder implementation
    print(f"Searching for Star Realms card: {card_name}")

    # For now, return a mock card
    mock_cards = [
        StarRealmsCard(
            name=card_name,
            card_type="Ship" if "Ship" in card_name else "Base",
            faction=["Trade Federation", "Blob", "Star Empire", "Machine Cult"][hash(card_name) % 4],
            cost=2 + (hash(card_name) % 4),
            attack=1 + (hash(card_name) % 3),
            defense=0 + (hash(card_name) % 2),
            ability=f"Ability of {card_name}",
            set_code="CORE",
            rarity="Common",
            image_url=f"https://example.com/starrealms/cards/{card_name.replace(' ', '_')}.png"
        )
    ]

    return mock_cards


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


# -----------------------------
# Collection Export
# -----------------------------
def save_collection_to_file(collection: StarRealmsDeck, output_file: str):
    """
    Save Star Realms collection data to a human-readable text file.

    Args:
        collection: StarRealmsDeck object to save
        output_file: Path where to save the file
    """
    with open(output_file, 'w') as f:
        f.write(f"Collection: {collection.name}\n")
        f.write(f"Player: {collection.player}\n")
        f.write(f"Collection ID: {collection.id}\n")
        f.write(f"Hash: {collection.hash}\n")
        f.write(f"\nCards ({len(collection.cards)} total):\n")
        f.write("-" * 50 + "\n")

        for card in collection.cards:
            f.write(f"{card.name} ({card.card_type})\n")
            f.write(f"  Faction: {card.faction}, Cost: {card.cost}\n")
            f.write(f"  Attack: {card.attack}, Defense: {card.defense}\n")
            f.write(f"  Set: {card.set_code}, Rarity: {card.rarity}\n")
            f.write(f"  Ability: {card.ability}\n\n")

    print(f"Saved Star Realms collection with {len(collection.cards)} cards to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images_for_collection(cards: List[StarRealmsCard], output_dir: str):
    """
    Placeholder for Star Realms card image fetching.

    Args:
        cards: List of StarRealmsCard objects
        output_dir: Directory to save images
    """
    print("Card image fetching for Star Realms not yet implemented.")
    print("Would integrate with Star Realms card databases or White Wizard Games resources.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for card in cards:
        print(f"Would fetch image for: {card.name}")

    return len(cards)  # Return number of cards processed
