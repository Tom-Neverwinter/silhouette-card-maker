# Fluxx Scraper Module
# ====================
# This module handles web scraping of Fluxx cards and data

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
class FluxxCard:
    """
    Represents a Fluxx card with all relevant data.

    Attributes:
        name: Card name
        card_type: Type of card (Keeper, Goal, Action, New Rule, Creeper)
        edition: Fluxx edition/set
        text: Card text/effect
        image_url: URL to card image
        rule_change: Whether this card changes rules
        win_condition: Whether this card creates win conditions
    """
    def __init__(self, name, card_type, edition, text, image_url, rule_change=False, win_condition=False):
        self.name = name
        self.card_type = card_type
        self.edition = edition
        self.text = text
        self.image_url = image_url
        self.rule_change = rule_change
        self.win_condition = win_condition


class FluxxDeck:
    """
    Represents a Fluxx deck/collection.

    Attributes:
        name: Deck/collection name
        cards: List of FluxxCard objects
        player: Player who owns this collection
        id: Unique deck identifier
        hash: Unique hash based on card composition
    """
    def __init__(self, name, cards, player, id):
        self.name = name
        self.cards = cards  # List of FluxxCard objects
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
def get_cards_from_looney_labs(card_type_filter="all", max_cards=50):
    """
    Scrape Fluxx cards from Looney Labs resources.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of FluxxCard objects
    """
    print("Fetching Fluxx cards from Looney Labs...")

    try:
        # Looney Labs Fluxx page
        url = 'https://www.looneylabs.com/games/fluxx'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        cards = []

        # Parse card mentions (simplified - would need site-specific parsing)
        card_refs = tree.xpath('//a[contains(@title, "Fluxx")]')

        for ref in card_refs[:max_cards]:
            title = ref.get('title', '')
            if 'Fluxx' in title:
                card = FluxxCard(
                    name=title,
                    card_type="Keeper" if "Keeper" in title else "Goal",
                    edition="Core",
                    text="Sample card text",
                    image_url=f"https://example.com/fluxx/cards/{title.replace(' ', '_')}.png",
                    rule_change=True if "Rule" in title else False,
                    win_condition=True if "Goal" in title else False
                )
                cards.append(card)

        return cards

    except Exception as e:
        print(f"Error scraping Looney Labs: {e}")
        return []


def get_cards_from_boardgamegeek(card_type_filter="all", max_cards=50):
    """
    Scrape Fluxx cards from BoardGameGeek.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of FluxxCard objects
    """
    print("Fetching Fluxx cards from BoardGameGeek...")

    try:
        # BoardGameGeek Fluxx page
        url = 'https://boardgamegeek.com/boardgame/258/fluxx'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        cards = []

        # Parse game information (simplified)
        game_sections = tree.xpath('//div[contains(@class, "game-description")]')

        for section in game_sections[:max_cards]:
            # Extract card type mentions (would need actual parsing)
            card = FluxxCard(
                name="Sample Fluxx Card",
                card_type="Action",
                edition="Core",
                text="Sample card effect",
                image_url="https://example.com/fluxx/cards/sample.png",
                rule_change=False,
                win_condition=False
            )
            cards.append(card)

        return cards

    except Exception as e:
        print(f"Error scraping BoardGameGeek: {e}")
        return []


# -----------------------------
# Collection Management
# -----------------------------
def create_collection_from_cards(cards: List[FluxxCard], collection_name: str) -> FluxxDeck:
    """
    Create a Fluxx collection from a list of cards.

    Args:
        cards: List of FluxxCard objects
        collection_name: Name for the collection

    Returns:
        FluxxDeck object representing the collection
    """
    return FluxxDeck(
        name=collection_name,
        cards=cards,
        player="Collection Owner",
        id=f"fluxx_collection_{hashlib.md5(collection_name.encode()).hexdigest()[:8]}"
    )


def search_fluxx_cards(card_name: str) -> List[FluxxCard]:
    """
    Search for Fluxx cards by name.

    This is a placeholder implementation. Real implementation would:
    - Query Fluxx databases
    - Use Looney Labs resources
    - Fall back to web scraping

    Args:
        card_name: Name of the card to search for

    Returns:
        List of matching FluxxCard objects
    """
    # Placeholder implementation
    print(f"Searching for Fluxx card: {card_name}")

    # For now, return a mock card
    # Real implementation would query actual databases
    mock_cards = [
        FluxxCard(
            name=card_name,
            card_type="Keeper" if "Keeper" in card_name else "Action",
            edition="Core",
            text=f"Effect of {card_name}",
            image_url=f"https://example.com/fluxx/cards/{card_name.replace(' ', '_')}.png",
            rule_change=True if "Rule" in card_name else False,
            win_condition=True if "Goal" in card_name else False
        )
    ]

    return mock_cards


def fetch_card_image(card: FluxxCard, output_path: str) -> bool:
    """
    Download a Fluxx card image.

    Args:
        card: FluxxCard object with image URL
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
def process_fluxx_cards_batch(cards: List[FluxxCard], output_dir: str) -> int:
    """
    Process a batch of Fluxx cards for image fetching.

    Args:
        cards: List of FluxxCard objects
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
def save_collection_to_file(collection: FluxxDeck, output_file: str):
    """
    Save Fluxx collection data to a human-readable text file.

    Args:
        collection: FluxxDeck object to save
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
            f.write(f"  Edition: {card.edition}\n")
            f.write(f"  Rule Change: {card.rule_change}\n")
            f.write(f"  Win Condition: {card.win_condition}\n")
            f.write(f"  Text: {card.text}\n")
            f.write("\n")

    print(f"Saved Fluxx collection with {len(collection.cards)} cards to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images_for_collection(cards: List[FluxxCard], output_dir: str):
    """
    Placeholder for Fluxx card image fetching.

    Args:
        cards: List of FluxxCard objects
        output_dir: Directory to save images
    """
    print("Card image fetching for Fluxx not yet implemented.")
    print("Would integrate with Looney Labs resources or community databases.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for card in cards:
        print(f"Would fetch image for: {card.name}")

    return len(cards)  # Return number of cards processed
