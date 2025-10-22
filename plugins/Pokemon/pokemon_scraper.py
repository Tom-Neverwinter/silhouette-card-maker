# Pokemon TCG Scraper Module
# ==========================
# This module handles web scraping of Pokemon TCG tournaments and decks
# from LimitlessTCG and play.limitlesstcg.com

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
    Represents a Pokemon TCG tournament with all relevant metadata.

    Attributes:
        name: Tournament name
        date: Tournament date (YYYY-MM-DD format)
        format: Game format ('standard', 'expanded', etc.)
        entries: Number of participants
        region: Geographic region or 'online' for digital events
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
    Represents a Pokemon TCG deck with cards and metadata.

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
def get_sanctioned_tournaments(request_format="all", number_of_tourneys=-1):
    """
    Scrape sanctioned (official) tournaments from LimitlessTCG.

    Fetches tournament data from the main LimitlessTCG tournaments page,
    parsing HTML to extract tournament information.

    Args:
        request_format: 'standard', 'expanded', or 'all' to filter by format
        number_of_tourneys: Number of tournaments to return (-1 for all)

    Returns:
        List of Tournament objects
    """
    print("Fetching sanctioned tournament list...")

    # Main tournaments page URL
    url = 'https://limitlesstcg.com/tournaments?time=all&show=50'
    page = requests.get(url)
    tree = html.fromstring(page.content)

    events = []
    index = 0

    # Parse each tournament listing in the table
    for listing in tree.xpath('//table/tr/td/a'):
        if 'tournaments' in listing.get('href'):
            link = 'https://limitlesstcg.com' + listing.get('href')
            id = link.split('=')[-1]

            try:
                # Extract tournament metadata from table cells
                format = tree.xpath('//table//img[@class="format"]')[index].get('alt').lower()
                entries = tree.xpath('//table//td[@class="landscape-only"]/text()')[index].strip()
                region = tree.xpath('//table//img[@class="flag"]')[index].get('alt')
                date = tree.xpath('//table//tr')[index+1].get('data-date').split('T')[0]
                name = tree.xpath('//table//tr')[index+1].get('data-name')

                events.append(Tournament(name, date, format, entries, region, id, link))
                index += 1
            except (IndexError, AttributeError):
                # Skip malformed entries
                continue

    # Filter by format if specified
    if request_format != "all":
        events = [e for e in events if e.format == request_format]

    # Limit number of tournaments
    if number_of_tourneys == -1:
        number_of_tourneys = len(events)

    return events[:number_of_tourneys]


def get_unsanctioned_tournaments(request_format="all", number_of_tourneys=-1):
    """
    Scrape unsanctioned (online) tournaments from play.limitlesstcg.com.

    Fetches tournament data from the online tournament platform,
    which has a different structure than sanctioned events.

    Args:
        request_format: 'standard', 'expanded', or 'all' to filter by format
        number_of_tourneys: Number of tournaments to return (-1 for all)

    Returns:
        List of Tournament objects
    """
    print("Fetching unsanctioned tournament list...")

    # Online tournaments API endpoint
    url = 'https://play.limitlesstcg.com/tournaments/completed?time=all&show=499&game=PTCG&format=all&type=all&page=1'
    page = requests.get(url)
    tree = html.fromstring(page.content)

    events = []

    # Parse tournament table rows
    for listing in tree.xpath('//table[@class="striped completed-tournaments"]/tr'):
        try:
            name = str(listing.get('data-name'))
            date = str(listing.get('data-date')).split('T')[0]
            format_code = str(listing.get('data-format'))
            entries = str(listing.get('data-players'))
            region = "online"

            # Convert format codes to format names
            if format_code == "4":
                format = "standard"
            elif format_code == "3":
                format = "expanded"
            else:
                format = "other"

            events.append(Tournament(name, date, format, entries, region, '', ''))
        except (TypeError, AttributeError):
            # Skip malformed entries
            continue

    # Remove empty first entry (header row)
    if events and events[0].name == 'None':
        events.pop(0)

    # Add IDs and links from date links
    count = 0
    for listing in tree.xpath('//table[@class="striped completed-tournaments"]/tr/td/a[@class="date"]'):
        if count >= len(events):
            break
        id = str(listing.get('href')).split('/')[2]
        link = 'https://play.limitlesstcg.com' + str(listing.get('href'))
        events[count].id = id
        events[count].link = link
        count += 1

    # Filter by format if specified
    if request_format != "all":
        events = [e for e in events if e.format == request_format]

    # Limit number of tournaments
    if number_of_tourneys == -1:
        number_of_tourneys = len(events)

    return events[:number_of_tourneys]


# -----------------------------
# Deck Scraping Functions
# -----------------------------
def scrape_deck_from_tournament(tournament: Tournament) -> List[Deck]:
    """
    Scrape all decks from a tournament page.

    Visits the tournament page and extracts links to individual deck
    pages, then scrapes each deck.

    Args:
        tournament: Tournament object with link to tournament page

    Returns:
        List of Deck objects from this tournament
    """
    print(f"Scraping decks from: {tournament.name}")

    try:
        page = requests.get(tournament.link)
        tree = html.fromstring(page.content)

        decks = []

        # Find all deck links (limit to top 10 for performance)
        deck_links = tree.xpath('//a[contains(@href, "/deck/")]/@href')

        for deck_link in deck_links[:10]:  # Limit to top 10 decks
            full_link = 'https://limitlesstcg.com' + deck_link if deck_link.startswith('/') else deck_link
            deck = scrape_single_deck(full_link, tournament)
            if deck:
                decks.append(deck)

        return decks
    except Exception as e:
        print(f"Error scraping tournament {tournament.name}: {e}")
        return []


def scrape_single_deck(deck_url: str, tournament: Tournament) -> Optional[Deck]:
    """
    Scrape a single deck from its individual page.

    Parses the deck page HTML to extract deck name, player name,
    and the complete card list.

    Args:
        deck_url: Direct URL to the deck page
        tournament: Tournament object this deck belongs to

    Returns:
        Deck object with all card data, or None if scraping fails
    """
    try:
        page = requests.get(deck_url)
        tree = html.fromstring(page.content)

        # Extract deck metadata
        deck_name = tree.xpath('//h1/text()')[0].strip() if tree.xpath('//h1/text()') else "Unknown Deck"
        player = tree.xpath('//div[@class="player"]/text()')[0].strip() if tree.xpath('//div[@class="player"]/text()') else "Unknown"

        # Extract card list from deck-list div
        cards = []
        card_entries = tree.xpath('//div[@class="deck-list"]//div[@class="card"]')

        for entry in card_entries:
            quantity_text = entry.xpath('.//span[@class="quantity"]/text()')
            name_text = entry.xpath('.//span[@class="name"]/text()')

            if quantity_text and name_text:
                quantity = int(quantity_text[0].strip())
                name = name_text[0].strip()
                cards.append((quantity, name))

        return Deck(deck_name, tournament.format, cards, player, tournament.id)
    except Exception as e:
        print(f"Error scraping deck {deck_url}: {e}")
        return None


# -----------------------------
# Data Export Functions
# -----------------------------
def save_decks_to_file(decks: List[Deck], output_file: str):
    """
    Save deck data to a human-readable text file.

    Creates a formatted text file with all deck information including
    cards, players, and tournament data.

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
