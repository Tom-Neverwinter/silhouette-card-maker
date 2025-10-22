# Cards Against Humanity Plugin - GUI Integration
# ===============================================
# Entry point for GUI-based Cards Against Humanity card processing

import os
import sys
import requests
from typing import List, Dict, Optional

# Import our plugin modules
from cah_scraper import CAHCard, CAHCollection, save_collection_to_file
from cah_api import process_cah_cards_batch

def process_cards_against_humanity(
    mode: str = "cards",
    num_cards: int = 20,
    output_dir: str = "game/front",
    save_collection_path: str = "game/decklist/cah_collection.txt",
    fetch_images: bool = False,
    card_text: Optional[str] = None,
    collection_url: Optional[str] = None,
    data_source: str = "database"
) -> Dict[str, any]:
    """
    Main entry point for Cards Against Humanity processing via GUI.

    Args:
        mode: What to fetch ('cards', 'collection', 'search')
        num_cards: Number of cards to process
        output_dir: Directory for card images
        save_collection_path: File path for collection output
        fetch_images: Whether to download card images
        card_text: Specific card text to search for (optional)
        collection_url: Specific collection URL (optional)
        data_source: Source for card data ('database', 'community', 'all')

    Returns:
        Dictionary with processing results and statistics
    """
    print("🎭 Cards Against Humanity Plugin - GUI Mode")
    print("=" * 50)
    print("⚠️  WARNING: Contains mature, offensive content")

    from cah_scraper import get_cards_from_cah_database, get_cards_from_community_spreadsheet
    from cah_api import get_collection_cards, search_cah_cards

    results = {
        'success': False,
        'mode': mode,
        'black_cards_processed': 0,
        'white_cards_processed': 0,
        'images_downloaded': 0,
        'errors': []
    }

    try:
        black_cards = []
        white_cards = []

        if collection_url:
            # Process specific collection
            print(f"Processing collection: {collection_url}")
            collection_black, collection_white = get_collection_cards(collection_url)
            black_cards.extend(collection_black)
            white_cards.extend(collection_white)
            results['black_cards_processed'] = len(collection_black)
            results['white_cards_processed'] = len(collection_white)
        elif card_text:
            # Search for specific card
            print(f"Searching for card: {card_text}")
            found_cards = search_cah_cards(card_text)
            # Separate by card type
            for card in found_cards:
                if card.card_type == "Black":
                    black_cards.append(card)
                    results['black_cards_processed'] += 1
                else:
                    white_cards.append(card)
                    results['white_cards_processed'] += 1
        else:
            # Get cards based on mode and source
            if mode == 'cards':
                print(f"Getting {num_cards} cards from {data_source}...")

                if data_source in ['database', 'all']:
                    db_cards = get_cards_from_cah_database("all", num_cards)
                    # Separate by card type
                    for card in db_cards:
                        if card.card_type == "Black":
                            black_cards.append(card)
                        else:
                            white_cards.append(card)

                if data_source in ['community', 'all']:
                    community_cards = get_cards_from_community_spreadsheet("all", num_cards)
                    # Separate by card type
                    for card in community_cards:
                        if card.card_type == "Black":
                            black_cards.append(card)
                        else:
                            white_cards.append(card)

                results['black_cards_processed'] = len(black_cards)
                results['white_cards_processed'] = len(white_cards)

        if not black_cards and not white_cards:
            results['errors'].append("No cards found")
            return results

        # Save collection data
        os.makedirs(os.path.dirname(save_collection_path), exist_ok=True)

        # Create collection from cards
        collection_name = f"CAH Collection ({len(black_cards)} black, {len(white_cards)} white cards)"
        collection = CAHCollection(
            name=collection_name,
            black_cards=black_cards,
            white_cards=white_cards,
            player="GUI User",
            id=f"gui_collection_{hash(str(black_cards + white_cards))[:8]}"
        )
        save_collection_to_file(collection, save_collection_path)

        # Fetch images if requested
        if fetch_images:
            print("Fetching card images...")

            all_cards = black_cards + white_cards
            if all_cards:
                images_downloaded = process_cah_cards_batch(all_cards, output_dir)
                results['images_downloaded'] = images_downloaded

        results['success'] = True
        print("✅ Cards Against Humanity processing complete!")

        return results

    except Exception as e:
        results['errors'].append(f"Processing error: {str(e)}")
        print(f"❌ Error: {e}")
        return results


def get_available_modes() -> List[str]:
    """
    Get list of available processing modes.

    Returns:
        List of mode names
    """
    return ["cards", "collection", "search"]


def get_available_sources() -> List[str]:
    """
    Get list of available data sources for Cards Against Humanity.

    Returns:
        List of source names
    """
    return ["database", "community", "all"]


def validate_collection_url(url: str) -> bool:
    """
    Validate if a Cards Against Humanity collection URL is accessible.

    Args:
        url: Collection URL to validate

    Returns:
        True if URL is valid and accessible
    """
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200 and ('cah' in url.lower() or 'cardsagainst' in url.lower())
    except:
        return False


# GUI Integration Helper
def get_plugin_info() -> Dict[str, any]:
    """
    Get plugin metadata for GUI integration.

    Returns:
        Dictionary with plugin information
    """
    return {
        'name': 'Cards Against Humanity',
        'version': '1.0.0',
        'description': 'Process Cards Against Humanity card collections - humorous party game',
        'author': 'Silhouette Card Maker Team',
        'supported_modes': get_available_modes(),
        'available_sources': get_available_sources(),
        'has_image_support': True,
        'gui_integration': True,
        'notes': '⚠️ Contains mature, offensive content - use with appropriate audiences only'
    }


# Example GUI usage
if __name__ == '__main__':
    # Demo of GUI integration
    print("Cards Against Humanity Plugin - GUI Integration Demo")
    print("=" * 50)

    # Example parameters (would come from GUI)
    results = process_cards_against_humanity(
        mode="cards",
        num_cards=10,
        data_source="database",
        fetch_images=True
    )

    print(f"\nResults: {results}")
