# Cards Against Humanity Scraper Module
# =====================================
# This module handles Cards Against Humanity card collections and data

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
class CAHCard:
    """
    Represents a Cards Against Humanity card with all relevant data.

    Attributes:
        text: Card text/content
        card_type: Type of card (Black/Question or White/Answer)
        expansion: Expansion set this card belongs to
        pick_count: For black cards, how many white cards to pick
        image_url: URL to card image (if available)
        offensive_level: Content warning level
    """
    def __init__(self, text, card_type, expansion, pick_count=1, image_url="", offensive_level="medium"):
        self.text = text
        self.card_type = card_type  # "Black" or "White"
        self.expansion = expansion
        self.pick_count = pick_count
        self.image_url = image_url
        self.offensive_level = offensive_level


class CAHCollection:
    """
    Represents a Cards Against Humanity card collection.

    Attributes:
        name: Collection name
        black_cards: List of black (question) cards
        white_cards: List of white (answer) cards
        player: Player who owns this collection
        id: Unique collection identifier
        hash: Unique hash based on card composition
    """
    def __init__(self, name, black_cards, white_cards, player, id):
        self.name = name
        self.black_cards = black_cards  # List of CAHCard objects (black cards)
        self.white_cards = white_cards  # List of CAHCard objects (white cards)
        self.player = player
        self.id = id
        self.hash = self._generate_hash()

    def _generate_hash(self):
        """
        Generate unique hash for collection based on card lists.

        Returns:
            MD5 hash string of sorted card lists
        """
        black_text = ''.join([card.text for card in sorted(self.black_cards, key=lambda x: x.text)])
        white_text = ''.join([card.text for card in sorted(self.white_cards, key=lambda x: x.text)])
        return hashlib.md5((black_text + white_text).encode()).hexdigest()


# -----------------------------
# Card Database Functions
# -----------------------------
def get_cards_from_cah_database(card_type_filter="all", max_cards=50):
    """
    Scrape Cards Against Humanity cards from the unofficial database.

    Args:
        card_type_filter: Card type to filter by ('black', 'white', 'all')
        max_cards: Maximum number of cards to return

    Returns:
        List of CAHCard objects
    """
    print("Fetching Cards Against Humanity cards from CAH database...")

    try:
        # Unofficial CAH Database
        url = 'https://cahdb.online/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        cards = []

        # Parse card listings (simplified - would need site-specific parsing)
        card_entries = tree.xpath('//div[contains(@class, "card")]')

        for entry in card_entries[:max_cards]:
            # Extract card info (would need actual parsing logic)
            card_text = f"Sample CAH Card {len(cards) + 1}"

            card = CAHCard(
                text=card_text,
                card_type="Black" if len(cards) % 3 == 0 else "White",
                expansion="Main Game",
                pick_count=1 if "Black" in card_type_filter or card_type_filter == "all" else 0,
                image_url=f"https://example.com/cah/cards/{card_text.replace(' ', '_')}.png"
            )
            cards.append(card)

        return cards

    except Exception as e:
        print(f"Error scraping CAH database: {e}")
        return []


def get_cards_from_community_spreadsheet(card_type_filter="all", max_cards=50):
    """
    Scrape Cards Against Humanity cards from community spreadsheets.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of CAHCard objects
    """
    print("Fetching Cards Against Humanity cards from community sources...")

    try:
        # Community spreadsheet data (would need to parse CSV/Excel)
        # For demo, return sample cards
        cards = []

        # Sample black cards
        black_cards_text = [
            "Why can't I sleep at night?",
            "I got 99 problems but ____ ain't one.",
            "What's a girl's best friend?",
            "____. High five, bro."
        ]

        # Sample white cards
        white_cards_text = [
            "Being a dick to children.",
            "Boobs.",
            "A windmill full of corpses.",
            "Flying sex snakes.",
            "The Jews."
        ]

        for i, text in enumerate(black_cards_text):
            card = CAHCard(
                text=text,
                card_type="Black",
                expansion="Main Game",
                pick_count=1,
                offensive_level="high"
            )
            cards.append(card)

        for i, text in enumerate(white_cards_text):
            card = CAHCard(
                text=text,
                card_type="White",
                expansion="Main Game",
                pick_count=0,
                offensive_level="high"
            )
            cards.append(card)

        return cards[:max_cards]

    except Exception as e:
        print(f"Error getting community cards: {e}")
        return []


# -----------------------------
# Collection Management
# -----------------------------
def create_collection_from_cards(black_cards: List[CAHCard], white_cards: List[CAHCard], collection_name: str) -> CAHCollection:
    """
    Create a Cards Against Humanity collection from black and white cards.

    Args:
        black_cards: List of black (question) cards
        white_cards: List of white (answer) cards
        collection_name: Name for the collection

    Returns:
        CAHCollection object representing the collection
    """
    return CAHCollection(
        name=collection_name,
        black_cards=black_cards,
        white_cards=white_cards,
        player="Collection Owner",
        id=f"cah_collection_{hashlib.md5(collection_name.encode()).hexdigest()[:8]}"
    )


def search_cah_cards(card_text: str) -> List[CAHCard]:
    """
    Search for Cards Against Humanity cards by text.

    This is a placeholder implementation. Real implementation would:
    - Query CAH databases
    - Use community card lists
    - Fall back to web scraping

    Args:
        card_text: Text of the card to search for

    Returns:
        List of matching CAHCard objects
    """
    # Placeholder implementation
    print(f"Searching for CAH card: {card_text}")

    # For now, return a mock card
    mock_cards = [
        CAHCard(
            text=card_text,
            card_type="Black" if "?" in card_text else "White",
            expansion="Main Game",
            pick_count=1 if "?" in card_text else 0,
            offensive_level="high"
        )
    ]

    return mock_cards


def fetch_card_image(card: CAHCard, output_path: str) -> bool:
    """
    Download a Cards Against Humanity card image.

    Args:
        card: CAHCard object with image URL
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
            print(f"Failed to download image for {card.text[:50]}...")
            return False
    except Exception as e:
        print(f"Error downloading image for CAH card: {e}")
        return False


# -----------------------------
# Batch Processing
# -----------------------------
def process_cah_cards_batch(cards: List[CAHCard], output_dir: str) -> int:
    """
    Process a batch of Cards Against Humanity cards for image fetching.

    Args:
        cards: List of CAHCard objects
        output_dir: Directory to save images

    Returns:
        Number of cards successfully processed
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    processed = 0

    for card in cards:
        print(f"Processing: {card.text[:30]}...")

        # Download image
        filename = f"{card.text.replace(' ', '_').replace('?', 'question').replace('.', '')[:50]}.png"
        filepath = output_path / filename

        if fetch_card_image(card, str(filepath)):
            processed += 1
            print(f"Downloaded: {filename}")

    return processed


# -----------------------------
# Collection Export
# -----------------------------
def save_collection_to_file(collection: CAHCollection, output_file: str):
    """
    Save Cards Against Humanity collection data to a human-readable text file.

    Args:
        collection: CAHCollection object to save
        output_file: Path where to save the file
    """
    with open(output_file, 'w') as f:
        f.write(f"Collection: {collection.name}\n")
        f.write(f"Player: {collection.player}\n")
        f.write(f"Collection ID: {collection.id}\n")
        f.write(f"Hash: {collection.hash}\n")
        f.write(f"\nBlack Cards (Questions) - {len(collection.black_cards)} total:\n")
        f.write("-" * 50 + "\n")

        for card in collection.black_cards:
            f.write(f"Q: {card.text}\n")
            f.write(f"   Pick: {card.pick_count}, Expansion: {card.expansion}\n")
            f.write(f"   Offensive Level: {card.offensive_level}\n\n")

        f.write(f"\nWhite Cards (Answers) - {len(collection.white_cards)} total:\n")
        f.write("-" * 50 + "\n")

        for card in collection.white_cards:
            f.write(f"A: {card.text}\n")
            f.write(f"   Expansion: {card.expansion}\n")
            f.write(f"   Offensive Level: {card.offensive_level}\n\n")

    print(f"Saved Cards Against Humanity collection with {len(collection.black_cards)} black cards and {len(collection.white_cards)} white cards to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images_for_collection(cards: List[CAHCard], output_dir: str):
    """
    Placeholder for Cards Against Humanity card image fetching.

    Args:
        cards: List of CAHCard objects
        output_dir: Directory to save images
    """
    print("Card image fetching for Cards Against Humanity not yet implemented.")
    print("Would integrate with CAH databases or community resources.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for card in cards:
        print(f"Would fetch image for: {card.text[:30]}...")

    return len(cards)  # Return number of cards processed
