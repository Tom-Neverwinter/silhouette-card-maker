# Universus Scraper Module
# ========================
# This module handles web scraping of Universus tournaments and decks

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
    Represents a Universus tournament with all relevant metadata.

    Attributes:
        name: Tournament name
        date: Tournament date (YYYY-MM-DD format)
        format: Game format
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
    Represents a Universus deck with cards and metadata.

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
def get_tournaments_from_universus_cards(format_filter="all", max_tournaments=10):
    """
    Scrape Universus tournaments from universus.cards.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Universus tournaments from universus.cards...")

    try:
        # universus.cards tournament page
        url = 'https://universus.cards/decks/tournament'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament listings (simplified - would need site-specific parsing)
        tournament_cards = tree.xpath('//div[contains(@class, "tournament-card")]')

        for card in tournament_cards[:max_tournaments]:
            # Extract tournament info (would need actual parsing logic)
            tournament_name = f"Universus Tournament {len(tournaments) + 1}"

            tournament = Tournament(
                name=tournament_name,
                date="2024-01-01",  # Would extract from page
                format=format_filter if format_filter != "all" else "standard",
                entries="Unknown",
                region="international",
                id=f"uc_tourney_{len(tournaments) + 1}",
                link=url
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping universus.cards: {e}")
        return []


def get_tournaments_from_uvs_ultra(format_filter="all", max_tournaments=10):
    """
    Scrape Universus tournaments from UVS Ultra.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Universus tournaments from UVS Ultra...")

    try:
        # UVS Ultra main site
        url = 'https://uvsultra.online/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament sections (simplified)
        tournament_links = tree.xpath('//a[contains(@href, "/tournaments/")]/@href')

        for link in tournament_links[:max_tournaments]:
            full_link = 'https://uvsultra.online' + link
            print(f"Found tournament: {full_link}")

            tournament = Tournament(
                name=f"UVS Tournament {len(tournaments) + 1}",
                date="2024-01-01",  # Would extract from page
                format=format_filter if format_filter != "all" else "standard",
                entries="Unknown",
                region="international",
                id=f"uvs_tourney_{len(tournaments) + 1}",
                link=full_link
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping UVS Ultra: {e}")
        return []


def get_tournaments_from_official_site(format_filter="all", max_tournaments=10):
    """
    Scrape Universus tournaments from official site.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Universus tournaments from official site...")

    try:
        # Official Universus cards page
        url = 'https://uvsgames.com/universus/cards/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse any tournament mentions (simplified)
        tournament_refs = tree.xpath('//div[contains(@class, "tournament")]')

        for ref in tournament_refs[:max_tournaments]:
            tournament_name = f"Official Tournament {len(tournaments) + 1}"

            tournament = Tournament(
                name=tournament_name,
                date="2024-01-01",  # Would extract from content
                format=format_filter if format_filter != "all" else "standard",
                entries="Unknown",
                region="international",
                id=f"official_tourney_{len(tournaments) + 1}",
                link=url
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping official site: {e}")
        return []


# -----------------------------
# Deck Scraping Functions
# -----------------------------
def scrape_deck_from_tournament(tournament: Tournament) -> List[Deck]:
    """
    Scrape all decks from a Universus tournament page.

    Args:
        tournament: Tournament object with link

    Returns:
        List of Deck objects from this tournament
    """
    print(f"Scraping decks from: {tournament.name}")

    try:
        page = requests.get(tournament.link)
        tree = html.fromstring(page.content)

        decks = []

        # Parse deck listings (simplified - would need site-specific parsing)
        deck_references = tree.xpath('//div[contains(@class, "deck-list")]')

        for ref in deck_references[:8]:  # Top 8 decks
            # Extract deck info (would need actual parsing)
            deck_name = f"Deck from {tournament.name}"
            player = "Unknown Player"

            # Mock card list for demo (would parse actual cards)
            cards = [
                (1, "Character Card"),
                (50, "Foundation Card"),
                (15, "Action Card"),
                (10, "Asset Card")
            ]

            deck = Deck(deck_name, tournament.format, cards, player, tournament.id)
            decks.append(deck)

        return decks

    except Exception as e:
        print(f"Error scraping tournament {tournament.name}: {e}")
        return []


def scrape_single_deck(deck_url: str, tournament: Tournament) -> Optional[Deck]:
    """
    Scrape a single Universus deck from its page.

    Args:
        deck_url: URL to deck page
        tournament: Tournament object

    Returns:
        Deck object or None if scraping fails
    """
    try:
        page = requests.get(deck_url)
        tree = html.fromstring(page.content)

        # Extract deck metadata (simplified)
        deck_name = "Universus Deck"
        player = "Unknown Player"

        # Mock card list for demo
        cards = [
            (1, "Character Card"),
            (50, "Foundation Card"),
            (15, "Action Card")
        ]

        return Deck(deck_name, tournament.format, cards, player, tournament.id)

    except Exception as e:
        print(f"Error scraping deck {deck_url}: {e}")
        return None


# -----------------------------
# Data Export Functions
# -----------------------------
def save_decks_to_file(decks: List[Deck], output_file: str):
    """
    Save Universus deck data to a human-readable text file.

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

    print(f"Saved {len(decks)} Universus decks to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images(cards: List[tuple], output_dir: str):
    """
    Placeholder for Universus card image fetching.

    Args:
        cards: List of (quantity, card_name) tuples
        output_dir: Directory to save images
    """
    print("Card image fetching for Universus not yet implemented.")
    print("Would integrate with Universus card databases or UVS Games resources.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for quantity, card_name in cards:
        print(f"Would fetch image for: {card_name} ({quantity}x)")

    return len(cards)  # Return number of cards processed
