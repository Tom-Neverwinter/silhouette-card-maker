# Pokemon TCG API Module
# ======================
# This module handles interactions with the Pokemon TCG API to fetch
# card information and download card images.

import os
import sys
import requests
import json
from pathlib import Path
from typing import List, Dict, Optional

# -----------------------------
# Pokemon TCG API Integration
# -----------------------------
def fetch_card_images_pokemontcg(cards: List[tuple], output_dir: str):
    """
    Fetch card images from the official Pokemon TCG API.

    Uses the pokemontcgsdk library to search for cards and download
    their high-resolution images.

    Args:
        cards: List of tuples (quantity, card_name) to fetch
        output_dir: Directory path where images should be saved

    Note:
        Requires pokemontcgsdk library: pip install pokemontcgsdk
    """
    try:
        from pokemontcgsdk import Card
    except ImportError:
        print("Error: pokemontcgsdk library not installed.")
        print("Install with: pip install pokemontcgsdk")
        return

    print("Fetching card images from Pokemon TCG API...")

    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for quantity, card_name in cards:
        try:
            # Search for the card in Pokemon TCG database
            print(f"Searching for: {card_name}")
            results = Card.where(q=f'name:"{card_name}"')

            if results:
                # Use the first (best) match
                card = results[0]

                # Get the large image URL (fallback to small if not available)
                image_url = card.images.large if hasattr(card.images, 'large') else card.images.small

                print(f"Found card: {card.name} ({card.set.name})")

                # Download the image
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Save multiple copies based on quantity
                    for i in range(quantity):
                        # Create safe filename from card name
                        safe_name = card_name.replace(' ', '_').replace('/', '_')
                        filename = f"{safe_name}_{i+1}.png"
                        filepath = output_path / filename

                        with open(filepath, 'wb') as f:
                            f.write(response.content)

                        print(f"Downloaded: {filename}")
                else:
                    print(f"Failed to download image for {card_name}")
            else:
                print(f"Card not found in Pokemon TCG database: {card_name}")

        except Exception as e:
            print(f"Error fetching {card_name}: {e}")


def get_card_info(card_name: str) -> Optional[Dict]:
    """
    Get detailed information about a specific Pokemon card.

    Args:
        card_name: Name of the card to look up

    Returns:
        Dictionary with card information or None if not found

    Note:
        This is a helper function for future expansion - currently
        just a placeholder for card information retrieval.
    """
    try:
        from pokemontcgsdk import Card

        results = Card.where(q=f'name:"{card_name}"')
        if results:
            card = results[0]
            return {
                'name': card.name,
                'set': card.set.name,
                'number': card.number,
                'rarity': card.rarity,
                'image_url': card.images.large if hasattr(card.images, 'large') else card.images.small
            }
    except Exception as e:
        print(f"Error getting card info for {card_name}: {e}")

    return None


def validate_card_exists(card_name: str) -> bool:
    """
    Check if a card exists in the Pokemon TCG database.

    Args:
        card_name: Name of the card to validate

    Returns:
        True if card exists, False otherwise
    """
    try:
        from pokemontcgsdk import Card

        results = Card.where(q=f'name:"{card_name}"')
        return len(results) > 0
    except Exception:
        return False


# -----------------------------
# Alternative Image Sources
# -----------------------------
def fetch_card_image_from_bulbapedia(card_name: str, output_path: str) -> bool:
    """
    Alternative method to fetch card images from Bulbapedia (fallback).

    This is a placeholder for future implementation if Pokemon TCG API
    is unavailable or insufficient.

    Args:
        card_name: Name of the card to fetch
        output_path: Where to save the image file

    Returns:
        True if successful, False otherwise
    """
    # TODO: Implement Bulbapedia scraping as fallback
    print(f"Bulbapedia fallback not yet implemented for {card_name}")
    return False


def fetch_card_image_from_pokemon_com(card_name: str, output_path: str) -> bool:
    """
    Alternative method to fetch card images from official Pokemon site.

    This is a placeholder for future implementation using official
    Pokemon TCG website resources.

    Args:
        card_name: Name of the card to fetch
        output_path: Where to save the image file

    Returns:
        True if successful, False otherwise
    """
    # TODO: Implement official Pokemon TCG website scraping
    print(f"Official Pokemon site fallback not yet implemented for {card_name}")
    return False


# -----------------------------
# Batch Processing Utilities
# -----------------------------
def process_card_batch(cards: List[tuple], output_dir: str, batch_size: int = 10):
    """
    Process cards in batches to avoid API rate limits.

    Args:
        cards: List of (quantity, card_name) tuples to process
        output_dir: Directory to save images
        batch_size: Number of cards to process before taking a break

    Returns:
        Number of cards successfully processed
    """
    import time

    processed = 0
    total = len(cards)

    for i in range(0, total, batch_size):
        batch = cards[i:i + batch_size]

        print(f"Processing batch {i//batch_size + 1}/{(total-1)//batch_size + 1} ({len(batch)} cards)")

        for quantity, card_name in batch:
            # Process this card (implementation depends on chosen API)
            if validate_card_exists(card_name):
                print(f"✓ {card_name} - exists in database")
                processed += 1
            else:
                print(f"✗ {card_name} - not found")

        # Brief pause between batches to be respectful to APIs
        if i + batch_size < total:
            print("Pausing briefly between batches...")
            time.sleep(2)

    return processed


def get_unique_cards_from_decks(decks: List) -> List[tuple]:
    """
    Extract unique cards from a list of decks.

    Consolidates cards across all decks, taking the maximum quantity
    for each unique card name.

    Args:
        decks: List of Deck objects

    Returns:
        List of (max_quantity, card_name) tuples for unique cards
    """
    unique_cards = {}

    for deck in decks:
        for quantity, card_name in deck.cards:
            if card_name not in unique_cards:
                unique_cards[card_name] = quantity
            else:
                # Keep the highest quantity found for this card
                unique_cards[card_name] = max(unique_cards[card_name], quantity)

    # Return as list of tuples sorted by quantity (highest first)
    return sorted([(q, name) for name, q in unique_cards.items()], reverse=True)
