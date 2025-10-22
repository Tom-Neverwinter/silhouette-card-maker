# Union Arena TCG Scraper Module
# ==============================
# This module handles web scraping of Union Arena tournaments and decks

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
    Represents a Union Arena tournament with all relevant metadata.

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
    Represents a Union Arena deck with cards and metadata.

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
def get_tournaments_from_ua_meta(format_filter="all", max_tournaments=10):
    """
    Scrape Union Arena tournaments from UA Meta site.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Union Arena tournaments from UA Meta...")

    try:
        # UA Meta deck lists page
        url = 'https://www.uasgmeta.com/uadecklists'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament listings (simplified - would need site-specific parsing)
        # This is a placeholder structure - real implementation would parse the actual site
        tournament_links = tree.xpath('//a[contains(@href, "/decklists/")]/@href')

        for link in tournament_links[:max_tournaments]:
            full_link = 'https://www.uasgmeta.com' + link
            print(f"Found tournament: {full_link}")

            # Create tournament object (would need actual parsing)
            tournament = Tournament(
                name=f"Union Arena Tournament {len(tournaments) + 1}",
                date="2024-01-01",  # Would extract from page
                format=format_filter if format_filter != "all" else "standard",
                entries="Unknown",
                region="singapore",  # UA Meta is Singapore-based
                id=f"ua_tourney_{len(tournaments) + 1}",
                link=full_link
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping UA Meta: {e}")
        return []


def get_tournaments_from_community(format_filter="all", max_tournaments=10):
    """
    Scrape Union Arena tournaments from community sources.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Union Arena tournaments from community sources...")

    try:
        # Joseph Writer Anderson's blog with tournament results
        url = 'https://www.josephwriteranderson.com/blog/the-best-union-arena-tcg-decks-right-now'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament mentions (simplified)
        # Real implementation would extract actual tournament data
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
                id=f"community_tourney_{len(tournaments) + 1}",
                link=url
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping community sources: {e}")
        return []


# -----------------------------
# Deck Scraping Functions
# -----------------------------
def scrape_deck_from_tournament(tournament: Tournament) -> List[Deck]:
    """
    Scrape all decks from a Union Arena tournament page.

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

        # Parse deck sections (simplified - would need site-specific parsing)
        deck_sections = tree.xpath('//div[contains(@class, "deck")]')

        for section in deck_sections[:8]:  # Top 8 decks
            # Extract deck info (would need actual parsing logic)
            deck_name = f"Deck from {tournament.name}"
            player = "Unknown Player"

            # Mock card list for demo (would parse actual cards)
            cards = [
                (4, "Character Card"),
                (50, "Deck Card"),
                (10, "Event Card")
            ]

            deck = Deck(deck_name, tournament.format, cards, player, tournament.id)
            decks.append(deck)

        return decks

    except Exception as e:
        print(f"Error scraping tournament {tournament.name}: {e}")
        return []


def scrape_single_deck(deck_url: str, tournament: Tournament) -> Optional[Deck]:
    """
    Scrape a single Union Arena deck from its page.

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
        deck_name = "Union Arena Deck"
        player = "Unknown Player"

        # Mock card list for demo
        cards = [
            (1, "Leader Card"),
            (50, "Deck Card"),
            (10, "Event Card")
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
    Save Union Arena deck data to a human-readable text file.

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

    print(f"Saved {len(decks)} Union Arena decks to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images(cards: List[tuple], output_dir: str):
    """
    Placeholder for Union Arena card image fetching.

    Args:
        cards: List of (quantity, card_name) tuples
        output_dir: Directory to save images
    """
    print("Card image fetching for Union Arena not yet implemented.")
    print("Would integrate with Union Arena card databases or Bandai resources.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for quantity, card_name in cards:
        print(f"Would fetch image for: {card_name} ({quantity}x)")

    return len(cards)  # Return number of cards processed
