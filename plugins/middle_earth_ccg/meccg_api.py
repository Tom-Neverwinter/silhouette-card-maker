# Middle Earth CCG API Module
# =============================
# This module handles Middle Earth CCG card data and image fetching

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
class MECharacterCard:
    """
    Represents a Middle Earth CCG character card with all relevant data.

    Attributes:
        name: Card name
        character: Character name (e.g., "Gandalf", "Aragorn")
        card_number: Official card number
        set_code: Set identifier
        rarity: Card rarity
        image_url: URL to card image
        card_type: Type of card (Character, Location, Item, Event, Hazard, Resource)
        faction: Character faction (Free Peoples, Shadow, Neutral)
        region: Character's region (Shire, Rivendell, Mordor, etc.)
        corruption: Corruption value (if applicable)
        mind: Mind value
        body: Body value
        description: Card text/ability
    """
    def __init__(self, name, character, card_number, set_code, rarity, image_url, 
                 card_type="Character", faction="Free Peoples", region="", corruption=0, 
                 mind=None, body=None, description=""):
        self.name = name
        self.character = character
        self.card_number = card_number
        self.set_code = set_code
        self.rarity = rarity
        self.image_url = image_url
        self.card_type = card_type
        self.faction = faction
        self.region = region
        self.corruption = corruption
        self.mind = mind
        self.body = body
        self.description = description


def search_meccg_cards(card_name: str) -> List[MECharacterCard]:
    """
    Search for Middle Earth CCG cards by name.
    
    Integrates with CCGTrader.net to search:
    - Character names
    - Card names
    - Faction names
    - Region names

    Args:
        card_name: Name of the card to search for

    Returns:
        List of matching MECharacterCard objects
    """
    print(f"Searching for Middle Earth CCG card: {card_name}")
    
    cards = []
    
    # Try CCGTrader.net first
    ccgt_cards = search_ccgtrader_meccg(card_name)
    if ccgt_cards:
        cards.extend(ccgt_cards)
    
    # Try community sources as fallback
    if not cards:
        community_cards = search_community_meccg(card_name)
        if community_cards:
            cards.extend(community_cards)
    
    return cards


def search_ccgtrader_meccg(card_name: str) -> List[MECharacterCard]:
    """
    Search CCGTrader.net for Middle Earth CCG cards.
    
    Args:
        card_name: Name of the card to search for
        
    Returns:
        List of MECharacterCard objects from CCGTrader
    """
    try:
        # CCGTrader search API endpoint
        search_url = "https://www.ccgtrader.net/games/middle-earth-ccg/search"
        params = {
            'q': card_name,
            'game': 'middle-earth-ccg',
            'limit': 20
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            cards = []
            
            for card_data in data.get('cards', []):
                card = MECharacterCard(
                    name=card_data.get('name', card_name),
                    character=card_data.get('character', ''),
                    card_number=card_data.get('number', ''),
                    set_code=card_data.get('set', ''),
                    rarity=card_data.get('rarity', 'Unknown'),
                    image_url=card_data.get('image_url', ''),
                    card_type=card_data.get('type', 'Character'),
                    faction=card_data.get('faction', 'Free Peoples'),
                    region=card_data.get('region', ''),
                    corruption=card_data.get('corruption', 0),
                    mind=card_data.get('mind'),
                    body=card_data.get('body'),
                    description=card_data.get('description', '')
                )
                cards.append(card)
            
            return cards
            
    except Exception as e:
        print(f"Error searching CCGTrader for Middle Earth CCG: {e}")
    
    return []


def search_community_meccg(card_name: str) -> List[MECharacterCard]:
    """
    Search community Middle Earth CCG sources.
    
    Args:
        card_name: Name of the card to search for
        
    Returns:
        List of MECharacterCard objects from community sources
    """
    try:
        # Community database search (placeholder for now)
        # In a real implementation, this would search fan-maintained databases
        
        # For now, return sample data
        sample_cards = []
        
        # Sample characters based on search
        if "gandalf" in card_name.lower():
            sample_cards.append(MECharacterCard(
                name="Gandalf the Grey",
                character="Gandalf",
                card_number="001",
                set_code="ME1",
                rarity="Rare",
                image_url="",
                card_type="Character",
                faction="Free Peoples",
                region="Rivendell",
                corruption=0,
                mind=8,
                body=4,
                description="Wise wizard and guide"
            ))
        
        return sample_cards
            
    except Exception as e:
        print(f"Error searching community sources for Middle Earth CCG: {e}")
    
    return []


def fetch_card_image(card: MECharacterCard, output_path: str) -> bool:
    """
    Download a Middle Earth CCG card image with multiple fallback sources.
    
    Tries multiple image sources in order:
    1. Direct image URL from card data
    2. CCGTrader images
    3. Community image sources

    Args:
        card: MECharacterCard object with image URL
        output_path: Local path where to save the image

    Returns:
        True if download successful, False otherwise
    """
    # Try direct URL first
    if card.image_url and fetch_image_from_url(card.image_url, output_path):
        return True
    
    # Try CCGTrader images
    ccgt_url = get_ccgtrader_image_url(card)
    if ccgt_url and fetch_image_from_url(ccgt_url, output_path):
        return True
    
    # Try community images
    community_url = get_community_image_url(card)
    if community_url and fetch_image_from_url(community_url, output_path):
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


def get_ccgtrader_image_url(card: MECharacterCard) -> Optional[str]:
    """
    Get CCGTrader image URL for a card.
    
    Args:
        card: MECharacterCard object
        
    Returns:
        CCGTrader image URL or None if not available
    """
    if not card.card_number or not card.set_code:
        return None
    
    try:
        # CCGTrader image URL pattern
        ccgt_url = f"https://www.ccgtrader.net/images/cards/middle-earth-ccg/{card.set_code}/{card.card_number}.jpg"
        
        # Verify URL exists
        response = requests.head(ccgt_url, timeout=10)
        if response.status_code == 200:
            return ccgt_url
            
    except Exception as e:
        print(f"Error checking CCGTrader URL for {card.name}: {e}")
    
    return None


def get_community_image_url(card: MECharacterCard) -> Optional[str]:
    """
    Get community image URL for a card.
    
    Args:
        card: MECharacterCard object
        
    Returns:
        Community image URL or None if not available
    """
    if not card.card_number:
        return None
    
    try:
        # Community image URL pattern (placeholder)
        community_url = f"https://meccg.net/images/cards/{card.card_number}.jpg"
        
        # Verify URL exists
        response = requests.head(community_url, timeout=10)
        if response.status_code == 200:
            return community_url
            
    except Exception as e:
        print(f"Error checking community URL for {card.name}: {e}")
    
    return None


# -----------------------------
# Batch Processing
# -----------------------------
def process_meccg_cards_batch(cards: List[tuple], output_dir: str) -> int:
    """
    Process a batch of Middle Earth CCG cards for image fetching.

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
        matching_cards = search_meccg_cards(card_name)

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
# Character and Faction Functions
# -----------------------------
def get_character_cards(character_name: str) -> List[MECharacterCard]:
    """
    Get all cards for a specific Middle Earth character.
    
    Args:
        character_name: Name of the character (e.g., "Gandalf", "Aragorn")
        
    Returns:
        List of MECharacterCard objects for that character
    """
    return search_meccg_cards(character_name)


def get_faction_cards(faction: str) -> List[MECharacterCard]:
    """
    Get all cards from a specific faction.
    
    Args:
        faction: Faction name (Free Peoples, Shadow, Neutral)
        
    Returns:
        List of MECharacterCard objects from that faction
    """
    all_cards = search_meccg_cards("")  # Get all cards
    return [card for card in all_cards if card.faction.lower() == faction.lower()]


def get_region_cards(region: str) -> List[MECharacterCard]:
    """
    Get all cards from a specific region.
    
    Args:
        region: Region name (Shire, Rivendell, Mordor, etc.)
        
    Returns:
        List of MECharacterCard objects from that region
    """
    all_cards = search_meccg_cards("")  # Get all cards
    return [card for card in all_cards if card.region.lower() == region.lower()]


def get_card_type_cards(card_type: str) -> List[MECharacterCard]:
    """
    Get all cards of a specific type.
    
    Args:
        card_type: Card type (Character, Location, Item, Event, Hazard, Resource)
        
    Returns:
        List of MECharacterCard objects of that type
    """
    all_cards = search_meccg_cards("")  # Get all cards
    return [card for card in all_cards if card.card_type.lower() == card_type.lower()]


# -----------------------------
# Data Validation
# -----------------------------
def validate_card_name(card_name: str) -> bool:
    """
    Validate that a card name exists in Middle Earth CCG database.

    Args:
        card_name: Name to validate

    Returns:
        True if card exists, False otherwise
    """
    cards = search_meccg_cards(card_name)
    return len(cards) > 0


def get_card_info(card_name: str) -> Optional[Dict]:
    """
    Get detailed information about a Middle Earth CCG card.

    Args:
        card_name: Name of the card

    Returns:
        Dictionary with card info or None if not found
    """
    cards = search_meccg_cards(card_name)
    if cards:
        card = cards[0]
        return {
            'name': card.name,
            'character': card.character,
            'number': card.card_number,
            'set': card.set_code,
            'rarity': card.rarity,
            'type': card.card_type,
            'faction': card.faction,
            'region': card.region,
            'corruption': card.corruption,
            'mind': card.mind,
            'body': card.body,
            'description': card.description,
            'image_url': card.image_url
        }
    return None
