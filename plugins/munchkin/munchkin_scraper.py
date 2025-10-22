# Munchkin Scraper Module
# =======================
# This module handles web scraping of Munchkin cards and data

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
class MunchkinCard:
    """
    Represents a Munchkin card with all relevant data.

    Attributes:
        name: Card name
        card_type: Type of card (Door, Treasure, etc.)
        level: Card level or power
        set_code: Set identifier
        rarity: Card rarity
        image_url: URL to card image
        subtype: Card subtype (Monster, Item, Curse, etc.)
    """
    def __init__(self, name, card_type, level, set_code, rarity, image_url, subtype=""):
        self.name = name
        self.card_type = card_type
        self.level = level
        self.set_code = set_code
        self.rarity = rarity
        self.image_url = image_url
        self.subtype = subtype


class MunchkinDeck:
    """
    Represents a Munchkin deck/collection.

    Attributes:
        name: Deck/collection name
        cards: List of MunchkinCard objects
        player: Player who owns this collection
        id: Unique deck identifier
        hash: Unique hash based on card composition
    """
    def __init__(self, name, cards, player, id):
        self.name = name
        self.cards = cards  # List of MunchkinCard objects
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
def get_cards_from_munchkin_ccg(card_type_filter="all", max_cards=50):
    """
    Scrape Munchkin cards from the CCG database.

    Args:
        card_type_filter: Card type to filter by ('Door', 'Treasure', 'all')
        max_cards: Maximum number of cards to return

    Returns:
        List of MunchkinCard objects
    """
    print("Fetching Munchkin cards from CCG database...")

    try:
        # Munchkin CCG card search page
        url = 'https://munchkinccg.game/gameplay/card-search/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        cards = []

        # Parse card listings (simplified - would need site-specific parsing)
        card_entries = tree.xpath('//div[contains(@class, "card-entry")]')

        for entry in card_entries[:max_cards]:
            # Extract card info (would need actual parsing logic)
            card_name = f"Munchkin Card {len(cards) + 1}"

            card = MunchkinCard(
                name=card_name,
                card_type="Door" if len(cards) % 2 == 0 else "Treasure",
                level=1,
                set_code="CORE",
                rarity="Common",
                image_url=f"https://example.com/munchkin/cards/{card_name.replace(' ', '_')}.png",
                subtype="Monster"
            )
            cards.append(card)

        return cards

    except Exception as e:
        print(f"Error scraping Munchkin CCG database: {e}")
        return []


def get_cards_from_fandom_wiki(card_type_filter="all", max_cards=50):
    """
    Scrape Munchkin cards from Card Game Database Wiki.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of MunchkinCard objects
    """
    print("Fetching Munchkin cards from Card Game Database Wiki...")

    try:
        # Card Game Database Wiki Munchkin page
        url = 'https://cardgamedatabase.fandom.com/wiki/Munchkin_(card_game)'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        cards = []

        # Parse card mentions (simplified)
        card_refs = tree.xpath('//a[contains(@title, "Munchkin")]')

        for ref in card_refs[:max_cards]:
            title = ref.get('title', '')
            if 'Munchkin' in title:
                card = MunchkinCard(
                    name=title,
                    card_type="Door",
                    level=1,
                    set_code="CORE",
                    rarity="Common",
                    image_url=f"https://example.com/munchkin/cards/{title.replace(' ', '_')}.png",
                    subtype="Item"
                )
                cards.append(card)

        return cards

    except Exception as e:
        print(f"Error scraping Card Game Database Wiki: {e}")
        return []


# -----------------------------
# Collection Management
# -----------------------------
def create_collection_from_cards(cards: List[MunchkinCard], collection_name: str) -> MunchkinDeck:
    """
    Create a Munchkin collection from a list of cards.

    Args:
        cards: List of MunchkinCard objects
        collection_name: Name for the collection

    Returns:
        MunchkinDeck object representing the collection
    """
    return MunchkinDeck(
        name=collection_name,
        cards=cards,
        player="Collection Owner",
        id=f"collection_{hashlib.md5(collection_name.encode()).hexdigest()[:8]}"
    )


def search_munchkin_cards(card_name: str) -> List[MunchkinCard]:
    """
    Search for Munchkin cards by name.

    This is a placeholder implementation. Real implementation would:
    - Query Munchkin databases
    - Use Steve Jackson Games resources
    - Fall back to web scraping

    Args:
        card_name: Name of the card to search for

    Returns:
        List of matching MunchkinCard objects
    """
    # Placeholder implementation
    print(f"Searching for Munchkin card: {card_name}")

    # For now, return a mock card
    mock_cards = [
        MunchkinCard(
            name=card_name,
            card_type="Door",
            level=1,
            set_code="CORE",
            rarity="Common",
            image_url=f"https://example.com/munchkin/cards/{card_name.replace(' ', '_')}.png",
            subtype="Monster"
        )
    ]

    return mock_cards


def fetch_card_image(card: MunchkinCard, output_path: str) -> bool:
    """
    Download a Munchkin card image.

    Args:
        card: MunchkinCard object with image URL
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
def process_munchkin_cards_batch(cards: List[MunchkinCard], output_dir: str) -> int:
    """
    Process a batch of Munchkin cards for image fetching.

    Args:
        cards: List of MunchkinCard objects
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
def save_collection_to_file(collection: MunchkinDeck, output_file: str):
    """
    Save Munchkin collection data to a human-readable text file.

    Args:
        collection: MunchkinDeck object to save
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
            f.write(f"  Level: {card.level}, Rarity: {card.rarity}\n")
            f.write(f"  Type: {card.subtype}\n")
            f.write(f"  Set: {card.set_code}\n")
            f.write("\n")

    print(f"Saved Munchkin collection with {len(collection.cards)} cards to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images_for_collection(cards: List[MunchkinCard], output_dir: str):
    """
    Placeholder for Munchkin card image fetching.

    Args:
        cards: List of MunchkinCard objects
        output_dir: Directory to save images
    """
    print("Card image fetching for Munchkin not yet implemented.")
    print("Would integrate with Steve Jackson Games resources or community databases.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for card in cards:
        print(f"Would fetch image for: {card.name}")

    return len(cards)  # Return number of cards processed
