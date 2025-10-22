# Cardfight!! Vanguard Scraper Module
# ===================================
# This module handles web scraping of Cardfight!! Vanguard tournaments and decks

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
    Represents a Cardfight!! Vanguard tournament with all relevant metadata.

    Attributes:
        name: Tournament name
        date: Tournament date (YYYY-MM-DD format)
        format: Game format (Standard, V-Premium, etc.)
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
    Represents a Cardfight!! Vanguard deck with cards and metadata.

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
def get_tournaments_from_vg_paradox(format_filter="all", max_tournaments=10):
    """
    Scrape Cardfight!! Vanguard tournaments from VG-Paradox.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Cardfight!! Vanguard tournaments from VG-Paradox...")

    try:
        # VG-Paradox main site
        url = 'https://vg-paradox.com/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament listings (simplified - would need site-specific parsing)
        # This is a placeholder structure - real implementation would parse the actual site
        tournament_links = tree.xpath('//a[contains(@href, "/tournaments/")]/@href')

        for link in tournament_links[:max_tournaments]:
            full_link = 'https://vg-paradox.com' + link
            print(f"Found tournament: {full_link}")

            # Create tournament object (would need actual parsing)
            tournament = Tournament(
                name=f"Vanguard Tournament {len(tournaments) + 1}",
                date="2024-01-01",  # Would extract from page
                format=format_filter if format_filter != "all" else "standard",
                entries="Unknown",
                region="international",
                id=f"vgp_tourney_{len(tournaments) + 1}",
                link=full_link
            )
            tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping VG-Paradox: {e}")
        return []


def get_tournaments_from_official_site(format_filter="all", max_tournaments=10):
    """
    Scrape Cardfight!! Vanguard tournaments from official site.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Cardfight!! Vanguard tournaments from official site...")

    try:
        # Official Cardfight!! Vanguard deck recipe page
        url = 'https://en.cf-vanguard.com/deckrecipe/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament sections (simplified)
        tournament_cards = tree.xpath('//div[contains(@class, "deck-card")]')

        for card in tournament_cards[:max_tournaments]:
            # Extract tournament info (would need actual parsing logic)
            tournament_name = f"Official Tournament {len(tournaments) + 1}"

            tournament = Tournament(
                name=tournament_name,
                date="2024-01-01",  # Would extract from page
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


def get_tournaments_from_dexander(format_filter="all", max_tournaments=10):
    """
    Scrape Cardfight!! Vanguard tournaments from Dexander.blog.

    Args:
        format_filter: Game format to filter by
        max_tournaments: Maximum number of tournaments to return

    Returns:
        List of Tournament objects
    """
    print("Fetching Cardfight!! Vanguard tournaments from Dexander.blog...")

    try:
        # Dexander.blog tournament page
        url = 'https://dexander.blog/'
        page = requests.get(url)
        tree = html.fromstring(page.content)

        tournaments = []

        # Parse tournament articles (simplified)
        articles = tree.xpath('//article')

        for article in articles[:max_tournaments]:
            title_elem = article.xpath('.//h2/a')
            if title_elem:
                title = title_elem[0].text_content().strip()
                link = title_elem[0].get('href')

                tournament = Tournament(
                    name=title,
                    date="2024-01-01",  # Would extract from article
                    format=format_filter if format_filter != "all" else "standard",
                    entries="Unknown",
                    region="international",
                    id=f"dex_tourney_{len(tournaments) + 1}",
                    link=link
                )
                tournaments.append(tournament)

        return tournaments

    except Exception as e:
        print(f"Error scraping Dexander.blog: {e}")
        return []


# -----------------------------
# Deck Scraping Functions
# -----------------------------
def scrape_deck_from_tournament(tournament: Tournament) -> List[Deck]:
    """
    Scrape all decks from a Cardfight!! Vanguard tournament page.

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
                (4, "Grade 0 Card"),
                (12, "Grade 1 Card"),
                (8, "Grade 2 Card"),
                (8, "Grade 3 Card"),
                (4, "G Unit Card")
            ]

            deck = Deck(deck_name, tournament.format, cards, player, tournament.id)
            decks.append(deck)

        return decks

    except Exception as e:
        print(f"Error scraping tournament {tournament.name}: {e}")
        return []


def scrape_single_deck(deck_url: str, tournament: Tournament) -> Optional[Deck]:
    """
    Scrape a single Cardfight!! Vanguard deck from its page.

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
        deck_name = "Cardfight!! Vanguard Deck"
        player = "Unknown Player"

        # Mock card list for demo
        cards = [
            (4, "Starting Vanguard"),
            (16, "Grade 0 Cards"),
            (12, "Grade 1 Cards"),
            (8, "Grade 2 Cards"),
            (4, "Grade 3 Cards")
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
    Save Cardfight!! Vanguard deck data to a human-readable text file.

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

    print(f"Saved {len(decks)} Cardfight!! Vanguard decks to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images(cards: List[tuple], output_dir: str):
    """
    Placeholder for Cardfight!! Vanguard card image fetching.

    Args:
        cards: List of (quantity, card_name) tuples
        output_dir: Directory to save images
    """
    print("Card image fetching for Cardfight!! Vanguard not yet implemented.")
    print("Would integrate with Cardfight!! Vanguard card databases or Bushiroad resources.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for quantity, card_name in cards:
        print(f"Would fetch image for: {card_name} ({quantity}x)")

    return len(cards)  # Return number of cards processed
