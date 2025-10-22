# Dragon Ball Super TCG Scraper Module
# =====================================
# This module handles web scraping of Dragon Ball Super TCG tournaments and decks
# from DBS-DeckPlanet and other sources

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
class Tournament:
    """
    Represents a Dragon Ball Super TCG tournament with all relevant metadata.

    Attributes:
        name: Tournament name
        date: Tournament date (YYYY-MM-DD format)
        format: Game format ('standard', 'expanded', etc.)
        entries: Number of participants
        region: Geographic region
        id: Unique tournament identifier
        link: URL to tournament page
    """
    def __init__(self, name, date, format, entries, region, id, link):
        self.name = name
        self.date = date
        self.format = format
        self.entries = entries
        self.region = region
        self.id = id
        self.link = link


class Deck:
    """
    Represents a Dragon Ball Super TCG deck with cards and metadata.

    Attributes:
        name: Deck name/title
        format: Game format this deck is for
        cards: List of (quantity, card_name) tuples
        player: Player who used this deck
        tournament_id: ID of the tournament this deck came from
        hash: Unique hash based on card composition
    """
    def __init__(self, name, format, cards, player, tournament_id):
        self.name = name
        self.format = format
        self.cards = cards  # List of tuples: (quantity, card_name)
        self.player = player
        self.tournament_id = tournament_id
        self.hash = self._generate_hash()

    def _generate_hash(self):
        """
        Generate unique hash for deck based on card list.

        This creates a consistent identifier for decks with the same cards,
        regardless of card order.

        Returns:
            MD5 hash string of sorted card list
        """
        card_string = ''.join([f"{q}{n}" for q, n in sorted(self.cards)])
        return hashlib.md5(card_string.encode()).hexdigest()


# -----------------------------
# Tournament Scraping Functions
# -----------------------------
def get_tournaments_from_deckplanet(format_filter="all", max_tournaments=10):
    """
    Scrape Dragon Ball Super tournaments from DBS-DeckPlanet.

    Args:
        format_filter: 'standard', 'expanded', or 'all' to filter by format
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Dragon Ball Super tournaments from DBS-DeckPlanet...")

    try:
        # Main tournaments/decks page
        url = 'https://www.dbs-deckplanet.com/decks'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Look for deck listings that might contain tournament info
        # This is a simplified approach - may need refinement based on actual site structure
        deck_links = tree.xpath('//a[contains(@href, "/decks/")]/@href')

        for link in deck_links[:max_tournaments]:
            full_link = 'https://www.dbs-deckplanet.com' + link
            print(f"Found potential tournament: {full_link}")

            # Create a basic tournament object (may need refinement)
            tournament = Tournament(
                name=f"DBS Tournament {len(tournaments) + 1}",
                date="2024-01-01",  # Placeholder - would need to extract from page
                format=format_filter if format_filter != "all" else "standard",
                entries="Unknown",
                region="online",
                id=f"tourney_{len(tournaments) + 1}",
                link=full_link
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping DBS-DeckPlanet: {e}")
        return []


def scrape_deck_from_url(deck_url: str) -> Optional[Deck]:
    """
    Scrape a single Dragon Ball Super deck from its URL.

    Args:
        deck_url: Direct URL to the deck page

    Returns:
        Deck object with card data, or None if scraping fails
    """
    try:
        page = requests.get(deck_url)
        tree = html.fromstring(page.content)

        # Extract deck metadata (simplified - would need site-specific parsing)
        deck_name = tree.xpath('//h1/text()')[0].strip() if tree.xpath('//h1/text()') else "Unknown Deck"

        # For now, create a placeholder deck
        # Real implementation would parse the actual card list from the page
        cards = [
            (4, "Son Goku"),
            (4, "Vegeta"),
            (20, "Energy Card"),
            (10, "Battle Card")
        ]

        return Deck(deck_name, "standard", cards, "Unknown Player", "tournament_1")

    except Exception as e:
        print(f"Error scraping deck {deck_url}: {e}")
        return None


# -----------------------------
# Data Export Functions
# -----------------------------
def save_decks_to_file(decks: List[Deck], output_file: str):
    """
    Save deck data to a human-readable text file.

    Args:
        decks: List of Deck objects to save
        output_file: Path where to save the file
    """
    with open(output_file, 'w') as f:
        for deck in decks:
            f.write(f"Deck: {deck.name}\n")
            f.write(f"Player: {deck.player}\n")
            f.write(f"Format: {deck.format}\n")
            f.write(f"Tournament ID: {deck.tournament_id}\n")
            f.write(f"Hash: {deck.hash}\n")
            f.write(f"\nCards:\n")
            for quantity, card_name in deck.cards:
                f.write(f"{quantity}x {card_name}\n")
            f.write("\n" + "="*50 + "\n\n")

    print(f"Saved {len(decks)} decks to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images(cards: List[tuple], output_dir: str):
    """
    Placeholder for Dragon Ball Super card image fetching.

    Args:
        cards: List of (quantity, card_name) tuples
        output_dir: Directory to save images
    """
    print("Card image fetching for Dragon Ball Super not yet implemented.")
    print("Would integrate with official Bandai card database or scraping.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for quantity, card_name in cards:
        print(f"Would fetch image for: {card_name} ({quantity}x)")

    return len(cards)  # Return number of cards processed
