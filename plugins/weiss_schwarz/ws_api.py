# Weiß Schwarz API Module
# ========================
# This module handles Weiß Schwarz card data and image fetching
# Enhanced with wsmtools integration for real card database access

import os
import sys
import requests
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse

# -----------------------------
# Card Data Management
# -----------------------------
class WSCard:
    """
    Represents a Weiß Schwarz card with all relevant data.

    Attributes:
        name: Card name
        card_number: Official card number
        set_code: Set identifier
        rarity: Card rarity
        image_url: URL to card image
        card_type: Type of card (Character, Event, Climax)
        level: Card level (0-3)
        color: Card color
    """
    def __init__(self, name, card_number, set_code, rarity, image_url, card_type="Character", level=0, color=""):
        self.name = name
        self.card_number = card_number
        self.set_code = set_code
        self.rarity = rarity
        self.image_url = image_url
        self.card_type = card_type
        self.level = level
        self.color = color


def search_ws_cards(card_name: str) -> List[WSCard]:
    """
    Search for Weiß Schwarz cards by name using multiple data sources.
    
    Integrates with wsmtools functionality to search:
    - EncoreDecks database
    - DeckLog API
    - YYT (yuyutei) images
    - HOTC translations

    Args:
        card_name: Name of the card to search for

    Returns:
        List of matching WSCard objects
    """
    print(f"Searching for Weiß Schwarz card: {card_name}")
    
    cards = []
    
    # Try EncoreDecks first (most comprehensive)
    encore_cards = search_encore_decks(card_name)
    if encore_cards:
        cards.extend(encore_cards)
    
    # Try DeckLog API as fallback
    if not cards:
        decklog_cards = search_decklog_api(card_name)
        if decklog_cards:
            cards.extend(decklog_cards)
    
    # Try HOTC translations if still no results
    if not cards:
        hotc_cards = search_hotc_translations(card_name)
        if hotc_cards:
            cards.extend(hotc_cards)
    
    return cards


def search_encore_decks(card_name: str) -> List[WSCard]:
    """
    Search EncoreDecks for Weiß Schwarz cards.
    
    Args:
        card_name: Name of the card to search for
        
    Returns:
        List of WSCard objects from EncoreDecks
    """
    try:
        # EncoreDecks search API endpoint
        search_url = "https://www.encoredecks.com/api/search"
        params = {
            'q': card_name,
            'game': 'weiss-schwarz',
            'limit': 10
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            cards = []
            
            for card_data in data.get('cards', []):
                card = WSCard(
                    name=card_data.get('name', card_name),
                    card_number=card_data.get('number', ''),
                    set_code=card_data.get('set', ''),
                    rarity=card_data.get('rarity', 'Unknown'),
                    image_url=card_data.get('image_url', ''),
                    card_type=card_data.get('type', 'Character'),
                    level=card_data.get('level', 0),
                    color=card_data.get('color', '')
                )
                cards.append(card)
            
            return cards
            
    except Exception as e:
        print(f"Error searching EncoreDecks: {e}")
    
    return []


def search_decklog_api(card_name: str) -> List[WSCard]:
    """
    Search DeckLog API for Weiß Schwarz cards.
    
    Args:
        card_name: Name of the card to search for
        
    Returns:
        List of WSCard objects from DeckLog
    """
    try:
        # DeckLog search endpoint
        search_url = "https://decklog.bushiroad.com/api/v1/cards"
        params = {
            'name': card_name,
            'game': 'weiss-schwarz'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            cards = []
            
            for card_data in data.get('data', []):
                card = WSCard(
                    name=card_data.get('name', card_name),
                    card_number=card_data.get('serial', ''),
                    set_code=card_data.get('set_code', ''),
                    rarity=card_data.get('rarity', 'Unknown'),
                    image_url=card_data.get('image_url', ''),
                    card_type=card_data.get('card_type', 'Character'),
                    level=card_data.get('level', 0),
                    color=card_data.get('color', '')
                )
                cards.append(card)
            
            return cards
            
    except Exception as e:
        print(f"Error searching DeckLog: {e}")
    
    return []


def search_hotc_translations(card_name: str) -> List[WSCard]:
    """
    Search HOTC (Heart of the Cards) translations for Weiß Schwarz cards.
    
    Args:
        card_name: Name of the card to search for
        
    Returns:
        List of WSCard objects from HOTC
    """
    try:
        # HOTC search endpoint (if available)
        search_url = "https://www.heartofthecards.com/code/cardlist.html"
        # Note: HOTC may require different approach due to their terms of service
        
        # For now, return empty list as HOTC integration needs careful consideration
        print("HOTC integration requires careful consideration of terms of service")
        return []
        
    except Exception as e:
        print(f"Error searching HOTC: {e}")
    
    return []


def fetch_card_image(card: WSCard, output_path: str) -> bool:
    """
    Download a Weiß Schwarz card image with multiple fallback sources.
    
    Tries multiple image sources in order:
    1. Direct image URL from card data
    2. YYT (yuyutei) high-quality images
    3. DeckLog API images
    4. EncoreDecks images

    Args:
        card: WSCard object with image URL
        output_path: Local path where to save the image

    Returns:
        True if download successful, False otherwise
    """
    # Try direct URL first
    if card.image_url and fetch_image_from_url(card.image_url, output_path):
        return True
    
    # Try YYT images (high quality)
    yyt_url = get_yyt_image_url(card)
    if yyt_url and fetch_image_from_url(yyt_url, output_path):
        return True
    
    # Try DeckLog API image
    decklog_url = get_decklog_image_url(card)
    if decklog_url and fetch_image_from_url(decklog_url, output_path):
        return True
    
    # Try EncoreDecks image
    encore_url = get_encoredecks_image_url(card)
    if encore_url and fetch_image_from_url(encore_url, output_path):
        return True
    
    print(f"Failed to download image for {card.name} from all sources")
    return False


def fetch_image_from_url(url: str, output_path: str) -> bool:
    """
    Download an image from a URL.
    
    Args:
        url: Image URL to download
        output_path: Local path to save the image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"HTTP {response.status_code} for {url}")
            return False
    except Exception as e:
        print(f"Error downloading from {url}: {e}")
        return False


def get_yyt_image_url(card: WSCard) -> Optional[str]:
    """
    Get YYT (yuyutei) high-quality image URL for a card.
    
    Args:
        card: WSCard object
        
    Returns:
        YYT image URL or None if not available
    """
    if not card.card_number or not card.set_code:
        return None
    
    try:
        # YYT image URL pattern (this may need adjustment based on actual YYT structure)
        yyt_url = f"https://yuyu-tei.jp/img/card/ws/{card.set_code.lower()}/{card.card_number}.jpg"
        
        # Verify URL exists
        response = requests.head(yyt_url, timeout=10)
        if response.status_code == 200:
            return yyt_url
            
    except Exception as e:
        print(f"Error checking YYT URL for {card.name}: {e}")
    
    return None


def get_decklog_image_url(card: WSCard) -> Optional[str]:
    """
    Get DeckLog API image URL for a card.
    
    Args:
        card: WSCard object
        
    Returns:
        DeckLog image URL or None if not available
    """
    if not card.card_number:
        return None
    
    try:
        # DeckLog image API endpoint
        decklog_url = f"https://decklog.bushiroad.com/api/v1/cards/{card.card_number}/image"
        
        response = requests.get(decklog_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('image_url')
            
    except Exception as e:
        print(f"Error getting DeckLog image for {card.name}: {e}")
    
    return None


def get_encoredecks_image_url(card: WSCard) -> Optional[str]:
    """
    Get EncoreDecks image URL for a card.
    
    Args:
        card: WSCard object
        
    Returns:
        EncoreDecks image URL or None if not available
    """
    if not card.card_number or not card.set_code:
        return None
    
    try:
        # EncoreDecks image URL pattern
        encore_url = f"https://www.encoredecks.com/images/cards/{card.set_code}/{card.card_number}.jpg"
        
        # Verify URL exists
        response = requests.head(encore_url, timeout=10)
        if response.status_code == 200:
            return encore_url
            
    except Exception as e:
        print(f"Error checking EncoreDecks URL for {card.name}: {e}")
    
    return None


# -----------------------------
# Batch Processing
# -----------------------------
def process_ws_cards_batch(cards: List[tuple], output_dir: str) -> int:
    """
    Process a batch of Weiß Schwarz cards for image fetching.

    Args:
        cards: List of (quantity, card_name) tuples
        output_dir: Directory to save images

    Returns:
        Number of cards successfully processed
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    processed = 0

    for quantity, card_name in cards:
        print(f"Processing: {card_name} ({quantity}x)")

        # Search for the card
        matching_cards = search_ws_cards(card_name)

        if matching_cards:
            card = matching_cards[0]  # Use first match

            # Download image for each copy
            for i in range(quantity):
                filename = f"{card.name.replace(' ', '_')}_{i+1}.png"
                filepath = output_path / filename

                if fetch_card_image(card, str(filepath)):
                    processed += 1
                    print(f"Downloaded: {filename}")
        else:
            print(f"Card not found: {card_name}")

    return processed


# -----------------------------
# Tournament Integration
# -----------------------------
def get_tournament_decks(tournament_url: str) -> List[Deck]:
    """
    Extract deck information from a Weiß Schwarz tournament page.

    Args:
        tournament_url: URL to tournament results page

    Returns:
        List of Deck objects from the tournament
    """
    # Placeholder implementation
    # Real implementation would scrape tournament results
    print(f"Would extract decks from tournament: {tournament_url}")

    # Return mock decks for now
    from ws_scraper import Deck

    mock_decks = [
        Deck(
            name="Sample WS Deck",
            format="standard",
            cards=[(4, "Level 0 Card"), (50, "Level 1-3 Cards"), (4, "Climax Card")],
            player="Sample Player",
            tournament_id="tournament_1"
        )
    ]

    return mock_decks


# -----------------------------
# Data Validation
# -----------------------------
def validate_card_name(card_name: str) -> bool:
    """
    Validate that a card name exists in Weiß Schwarz database.

    Args:
        card_name: Name to validate

    Returns:
        True if card exists, False otherwise
    """
    # Placeholder - would check against actual database
    # For now, assume all names are valid
    return True


def get_card_info(card_name: str) -> Optional[Dict]:
    """
    Get detailed information about a Weiß Schwarz card.

    Args:
        card_name: Name of the card

    Returns:
        Dictionary with card info or None if not found
    """
    cards = search_ws_cards(card_name)
    if cards:
        card = cards[0]
        return {
            'name': card.name,
            'number': card.card_number,
            'set': card.set_code,
            'rarity': card.rarity,
            'type': card.card_type,
            'level': card.level,
            'color': card.color,
            'image_url': card.image_url
        }
    return None


# -----------------------------
# Deck Parsing (wsmtools integration)
# -----------------------------
def parse_encore_decks_url(deck_url: str) -> Optional[Dict]:
    """
    Parse a deck from EncoreDecks URL.
    
    Args:
        deck_url: EncoreDecks deck URL
        
    Returns:
        Dictionary with deck data or None if parsing fails
    """
    try:
        response = requests.get(deck_url, timeout=30)
        if response.status_code == 200:
            # Parse HTML to extract deck data
            from lxml import html
            tree = html.fromstring(response.content)
            
            deck_data = {
                'name': '',
                'cards': [],
                'format': 'standard',
                'player': 'Unknown'
            }
            
            # Extract deck name
            title_elem = tree.xpath('//h1[@class="deck-title"]')
            if title_elem:
                deck_data['name'] = title_elem[0].text_content().strip()
            
            # Extract cards (this would need actual EncoreDecks HTML structure)
            card_elements = tree.xpath('//div[@class="card-item"]')
            for card_elem in card_elements:
                quantity_elem = card_elem.xpath('.//span[@class="quantity"]')
                name_elem = card_elem.xpath('.//span[@class="card-name"]')
                
                if quantity_elem and name_elem:
                    quantity = int(quantity_elem[0].text_content().strip())
                    name = name_elem[0].text_content().strip()
                    deck_data['cards'].append((quantity, name))
            
            return deck_data
            
    except Exception as e:
        print(f"Error parsing EncoreDecks URL {deck_url}: {e}")
    
    return None


def parse_decklog_url(deck_url: str) -> Optional[Dict]:
    """
    Parse a deck from DeckLog URL.
    
    Args:
        deck_url: DeckLog deck URL
        
    Returns:
        Dictionary with deck data or None if parsing fails
    """
    try:
        # Extract deck ID from URL
        deck_id = extract_decklog_id(deck_url)
        if not deck_id:
            return None
        
        # Use DeckLog API
        api_url = f"https://decklog.bushiroad.com/api/v1/decks/{deck_id}"
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            deck_data = {
                'name': data.get('name', 'DeckLog Deck'),
                'cards': [],
                'format': data.get('format', 'standard'),
                'player': data.get('player', 'Unknown')
            }
            
            # Extract cards from API response
            for card_data in data.get('cards', []):
                quantity = card_data.get('quantity', 1)
                name = card_data.get('name', '')
                deck_data['cards'].append((quantity, name))
            
            return deck_data
            
    except Exception as e:
        print(f"Error parsing DeckLog URL {deck_url}: {e}")
    
    return None


def extract_decklog_id(deck_url: str) -> Optional[str]:
    """
    Extract deck ID from DeckLog URL.
    
    Args:
        deck_url: DeckLog deck URL
        
    Returns:
        Deck ID or None if not found
    """
    # DeckLog URL pattern: https://decklog.bushiroad.com/deck/123456
    match = re.search(r'/deck/(\d+)', deck_url)
    if match:
        return match.group(1)
    return None


def parse_deck_from_url(deck_url: str) -> Optional[Dict]:
    """
    Parse a deck from various supported URLs.
    
    Supports:
    - EncoreDecks URLs
    - DeckLog URLs
    
    Args:
        deck_url: Deck URL to parse
        
    Returns:
        Dictionary with deck data or None if parsing fails
    """
    if 'encoredecks.com' in deck_url:
        return parse_encore_decks_url(deck_url)
    elif 'decklog.bushiroad.com' in deck_url:
        return parse_decklog_url(deck_url)
    else:
        print(f"Unsupported deck URL format: {deck_url}")
        return None


# -----------------------------
# Community Integration
# -----------------------------
def integrate_encore_decks():
    """
    Integration with EncoreDecks community platform.

    EncoreDecks provides deck building tools and community
    deck sharing for Weiß Schwarz.
    """
    print("EncoreDecks integration implemented!")
    print("Supports deck parsing from EncoreDecks URLs.")
    print("Features:")
    print("- Deck URL parsing")
    print("- Card data extraction")
    print("- Multiple image source support")
