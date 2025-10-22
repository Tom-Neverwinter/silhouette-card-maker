# Grand Archive Scraper Module
# ============================
# This module handles web scraping of Grand Archive tournaments and decks

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
    Represents a Grand Archive tournament with all relevant metadata.

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
    Represents a Grand Archive deck with cards and metadata.

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
def get_tournaments_from_ga_tournament_reports(format_filter="all", max_tournaments=10):
    """
    Scrape Grand Archive tournaments from GA Tournament Reports.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Grand Archive tournaments from GA Tournament Reports...")

    try:
        # GA Tournament Reports main page
        url = 'https://gatr.carrd.co/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament listings (simplified - would need site-specific parsing)
        tournament_links = tree.xpath('//a[contains(@href, "/tournaments/")]/@href')

        for link in tournament_links[:max_tournaments]:
            full_link = 'https://gatr.carrd.co' + link
            print(f"Found tournament: {full_link}")

            # Create tournament object (would need actual parsing)
            tournament = Tournament(
                name=f"Grand Archive Tournament {len(tournaments) + 1}",
                date="2024-01-01",  # Would extract from page
                format=format_filter if format_filter != "all" else "standard",
                entries="Unknown",
                region="international",
                id=f"gatr_tourney_{len(tournaments) + 1}",
                link=full_link
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping GA Tournament Reports: {e}")
        return []


def get_tournaments_from_tcg_architect(format_filter="all", max_tournaments=10):
    """
    Scrape Grand Archive tournaments from TCG Architect.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Grand Archive tournaments from TCG Architect...")

    try:
        # TCG Architect Grand Archive tournaments page
        url = 'https://tcgarchitect.com/grand-archive/tournaments'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament listings (simplified)
        tournament_cards = tree.xpath('//div[contains(@class, "tournament-card")]')

        for card in tournament_cards[:max_tournaments]:
            # Extract tournament info (would need actual parsing logic)
            tournament_name = f"GA Tournament {len(tournaments) + 1}"

            tournament = Tournament(
                name=tournament_name,
                date="2024-01-01",  # Would extract from page
                format=format_filter if format_filter != "all" else "standard",
                entries="Unknown",
                region="international",
                id=f"tcga_tourney_{len(tournaments) + 1}",
                link=url
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping TCG Architect: {e}")
        return []


def get_tournaments_from_luxera_map(format_filter="all", max_tournaments=10):
    """
    Scrape Grand Archive tournaments from Luxera's Map.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Grand Archive tournaments from Luxera's Map...")

    try:
        # Luxera's Map tournament primer page
        url = 'https://luxerasmap.com/articles/grand-archive-tournament-primer/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament mentions (simplified)
        tournament_sections = tree.xpath('//h3[contains(text(), "tournament") or contains(text(), "Tournament")]')

        for section in tournament_sections[:max_tournaments]:
            title = section.text_content().strip()
            print(f"Found tournament mention: {title}")

            tournament = Tournament(
                name=title,
                date="2024-01-01",  # Would extract from content
                format=format_filter if format_filter != "all" else "standard",
                entries="Unknown",
                region="international",
                id=f"lux_tourney_{len(tournaments) + 1}",
                link=url
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping Luxera's Map: {e}")
        return []


# -----------------------------
# Deck Scraping Functions
# -----------------------------
def scrape_deck_from_tournament(tournament: Tournament) -> List[Deck]:
    """
    Scrape all decks from a Grand Archive tournament page.

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
                (1, "Champion Card"),
                (40, "Material Card"),
                (15, "Action Card"),
                (5, "Ally Card")
            ]

            deck = Deck(deck_name, tournament.format, cards, player, tournament.id)
            decks.append(deck)

        return decks

    except Exception as e:
        print(f"Error scraping tournament {tournament.name}: {e}")
        return []


def scrape_single_deck(deck_url: str, tournament: Tournament) -> Optional[Deck]:
    """
    Scrape a single Grand Archive deck from its page.

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
        deck_name = "Grand Archive Deck"
        player = "Unknown Player"

        # Mock card list for demo
        cards = [
            (1, "Champion Card"),
            (40, "Material Card"),
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
    Save Grand Archive deck data to a human-readable text file.

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

    print(f"Saved {len(decks)} Grand Archive decks to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images(cards: List[tuple], output_dir: str):
    """
    Placeholder for Grand Archive card image fetching.

    Args:
        cards: List of (quantity, card_name) tuples
        output_dir: Directory to save images
    """
    print("Card image fetching for Grand Archive not yet implemented.")
    print("Would integrate with Grand Archive card databases or official resources.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for quantity, card_name in cards:
        print(f"Would fetch image for: {card_name} ({quantity}x)")

    return len(cards)  # Return number of cards processed
