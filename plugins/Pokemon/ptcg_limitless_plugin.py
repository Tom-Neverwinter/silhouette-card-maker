#!/usr/bin/env python3
"""
Pokemon TCG Plugin for Silhouette Card Maker
Scrapes deck lists from LimitlessTCG and fetches card images
"""

import os
import sys
import requests
import hashlib
import json
from pathlib import Path
from lxml import html
from typing import List, Dict, Optional
import click


class Tournament:
    """Represents a Pokemon TCG tournament"""
    def __init__(self, name, date, format, entries, region, id, link):
        self.name = name
        self.date = date
        self.format = format
        self.entries = entries
        self.region = region
        self.id = id
        self.link = link


class Deck:
    """Represents a Pokemon TCG deck"""
    def __init__(self, name, format, cards, player, tournament_id):
        self.name = name
        self.format = format
        self.cards = cards  # List of tuples: (quantity, card_name)
        self.player = player
        self.tournament_id = tournament_id
        self.hash = self._generate_hash()
    
    def _generate_hash(self):
        """Generate unique hash for deck based on card list"""
        card_string = ''.join([f"{q}{n}" for q, n in sorted(self.cards)])
        return hashlib.md5(card_string.encode()).hexdigest()


def get_sanctioned_tournaments(request_format="all", number_of_tourneys=-1):
    """
    Scrape sanctioned tournaments from LimitlessTCG
    
    Args:
        request_format: 'standard', 'expanded', or 'all'
        number_of_tourneys: Number of tournaments to return (-1 for all)
    
    Returns:
        List of Tournament objects
    """
    print("Fetching sanctioned tournament list...")
    
    url = 'https://limitlesstcg.com/tournaments?time=all&show=50'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    
    events = []
    index = 0
    
    for listing in tree.xpath('//table/tr/td/a'):
        if 'tournaments' in listing.get('href'):
            link = 'https://limitlesstcg.com' + listing.get('href')
            id = link.split('=')[-1]
            
            try:
                format = tree.xpath('//table//img[@class="format"]')[index].get('alt').lower()
                entries = tree.xpath('//table//td[@class="landscape-only"]/text()')[index].strip()
                region = tree.xpath('//table//img[@class="flag"]')[index].get('alt')
                date = tree.xpath('//table//tr')[index+1].get('data-date').split('T')[0]
                name = tree.xpath('//table//tr')[index+1].get('data-name')
                
                events.append(Tournament(name, date, format, entries, region, id, link))
                index += 1
            except (IndexError, AttributeError):
                continue
    
    # Filter by format
    if request_format != "all":
        events = [e for e in events if e.format == request_format]
    
    # Limit number of tournaments
    if number_of_tourneys == -1:
        number_of_tourneys = len(events)
    
    return events[:number_of_tourneys]


def get_unsanctioned_tournaments(request_format="all", number_of_tourneys=-1):
    """
    Scrape unsanctioned (online) tournaments from play.limitlesstcg.com
    
    Args:
        request_format: 'standard', 'expanded', or 'all'
        number_of_tourneys: Number of tournaments to return (-1 for all)
    
    Returns:
        List of Tournament objects
    """
    print("Fetching unsanctioned tournament list...")
    
    url = 'https://play.limitlesstcg.com/tournaments/completed?time=all&show=499&game=PTCG&format=all&type=all&page=1'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    
    events = []
    
    for listing in tree.xpath('//table[@class="striped completed-tournaments"]/tr'):
        try:
            name = str(listing.get('data-name'))
            date = str(listing.get('data-date')).split('T')[0]
            format_code = str(listing.get('data-format'))
            entries = str(listing.get('data-players'))
            region = "online"
            
            # Convert format code
            if format_code == "4":
                format = "standard"
            elif format_code == "3":
                format = "expanded"
            else:
                format = "other"
            
            events.append(Tournament(name, date, format, entries, region, '', ''))
        except (TypeError, AttributeError):
            continue
    
    # Remove empty first entry
    if events and events[0].name == 'None':
        events.pop(0)
    
    # Add IDs and links
    count = 0
    for listing in tree.xpath('//table[@class="striped completed-tournaments"]/tr/td/a[@class="date"]'):
        if count >= len(events):
            break
        id = str(listing.get('href')).split('/')[2]
        link = 'https://play.limitlesstcg.com' + str(listing.get('href'))
        events[count].id = id
        events[count].link = link
        count += 1
    
    # Filter by format
    if request_format != "all":
        events = [e for e in events if e.format == request_format]
    
    # Limit number of tournaments
    if number_of_tourneys == -1:
        number_of_tourneys = len(events)
    
    return events[:number_of_tourneys]


def scrape_deck_from_tournament(tournament: Tournament) -> List[Deck]:
    """
    Scrape all decks from a tournament page
    
    Args:
        tournament: Tournament object with link
    
    Returns:
        List of Deck objects
    """
    print(f"Scraping decks from: {tournament.name}")
    
    try:
        page = requests.get(tournament.link)
        tree = html.fromstring(page.content)
        
        decks = []
        
        # Find all deck links
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
    Scrape a single deck from its page
    
    Args:
        deck_url: URL to deck page
        tournament: Tournament object
    
    Returns:
        Deck object or None
    """
    try:
        page = requests.get(deck_url)
        tree = html.fromstring(page.content)
        
        # Get deck name and player
        deck_name = tree.xpath('//h1/text()')[0].strip() if tree.xpath('//h1/text()') else "Unknown Deck"
        player = tree.xpath('//div[@class="player"]/text()')[0].strip() if tree.xpath('//div[@class="player"]/text()') else "Unknown"
        
        # Get card list
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


def fetch_card_images_pokemontcg(cards: List[tuple], output_dir: str):
    """
    Fetch card images from Pokemon TCG API
    
    Args:
        cards: List of tuples (quantity, card_name)
        output_dir: Directory to save images
    """
    from pokemontcgsdk import Card
    
    print("Fetching card images from Pokemon TCG API...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for quantity, card_name in cards:
        try:
            # Search for card
            results = Card.where(q=f'name:"{card_name}"')
            
            if results:
                card = results[0]
                image_url = card.images.large if hasattr(card.images, 'large') else card.images.small
                
                # Download image
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Save multiple copies based on quantity
                    for i in range(quantity):
                        filename = f"{card_name.replace(' ', '_')}_{i+1}.png"
                        filepath = output_path / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Error fetching {card_name}: {e}")


def save_decks_to_file(decks: List[Deck], output_file: str):
    """
    Save decks to a text file in a readable format
    
    Args:
        decks: List of Deck objects
        output_file: Path to output file
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


@click.command()
@click.option('--format', '-f', default='standard', 
              type=click.Choice(['standard', 'expanded', 'all']),
              help='Tournament format to scrape')
@click.option('--sanctioned/--unsanctioned', default=True,
              help='Scrape sanctioned or unsanctioned tournaments')
@click.option('--num-tournaments', '-n', default=5,
              help='Number of tournaments to scrape (-1 for all)')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-decks', '-s', default='game/decklist/scraped_decks.txt',
              help='File to save deck lists')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from Pokemon TCG API')
def main(format, sanctioned, num_tournaments, output_dir, save_decks, fetch_images):
    """
    Pokemon TCG Plugin for Silhouette Card Maker
    
    Scrapes deck lists from LimitlessTCG and optionally fetches card images.
    """
    print("Pokemon TCG LimitlessTCG Scraper Plugin")
    print("="*50)
    
    # Get tournaments
    if sanctioned:
        tournaments = get_sanctioned_tournaments(format, num_tournaments)
    else:
        tournaments = get_unsanctioned_tournaments(format, num_tournaments)
    
    print(f"\nFound {len(tournaments)} tournaments")
    
    # Scrape decks from tournaments
    all_decks = []
    for tournament in tournaments:
        decks = scrape_deck_from_tournament(tournament)
        all_decks.extend(decks)
    
    print(f"\nScraped {len(all_decks)} total decks")
    
    # Save decks to file
    os.makedirs(os.path.dirname(save_decks), exist_ok=True)
    save_decks_to_file(all_decks, save_decks)
    
    # Fetch card images if requested
    if fetch_images and all_decks:
        print("\nFetching card images...")
        # Get unique cards across all decks
        unique_cards = {}
        for deck in all_decks:
            for quantity, card_name in deck.cards:
                if card_name not in unique_cards:
                    unique_cards[card_name] = quantity
                else:
                    unique_cards[card_name] = max(unique_cards[card_name], quantity)
        
        cards_list = [(q, name) for name, q in unique_cards.items()]
        fetch_card_images_pokemontcg(cards_list, output_dir)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
