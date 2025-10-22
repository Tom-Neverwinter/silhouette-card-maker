# Fluxx Plugin - GUI Integration
# ==============================
# Entry point for GUI-based Fluxx card processing

import os
import sys
import requests
from typing import List, Dict, Optional

# Import our plugin modules
from fluxx_scraper import FluxxCard, FluxxDeck, save_collection_to_file
from fluxx_api import process_fluxx_cards_batch

def process_fluxx_cards(
    mode: str = "cards",
    num_cards: int = 20,
    output_dir: str = "game/front",
    save_collection_path: str = "game/decklist/fluxx_collection.txt",
    fetch_images: bool = False,
    card_name: Optional[str] = None,
    collection_url: Optional[str] = None,
    data_source: str = "looney"
) -> Dict[str, any]:
    """
    Main entry point for Fluxx processing via GUI.

    Args:
        mode: What to fetch ('cards', 'collection', 'search')
        num_cards: Number of cards to process
        output_dir: Directory for card images
        save_collection_path: File path for collection output
        fetch_images: Whether to download card images
        card_name: Specific card name to search for (optional)
        collection_url: Specific collection URL (optional)
        data_source: Source for card data ('looney', 'boardgamegeek', 'all')

    Returns:
        Dictionary with processing results and statistics
    """
    print("🎲 Fluxx Plugin - GUI Mode")
    print("=" * 50)
    print("The card game where the rules keep changing!")

    from fluxx_scraper import get_cards_from_looney_labs, get_cards_from_boardgamegeek
    from fluxx_api import get_collection_cards, search_fluxx_cards

    results = {
        'success': False,
        'mode': mode,
        'cards_processed': 0,
        'images_downloaded': 0,
        'errors': []
    }

    try:
        all_cards = []

        if collection_url:
            # Process specific collection
            print(f"Processing collection: {collection_url}")
            collection_cards = get_collection_cards(collection_url)
            all_cards.extend(collection_cards)
            results['cards_processed'] = len(collection_cards)
        elif card_name:
            # Search for specific card
            print(f"Searching for card: {card_name}")
            found_cards = search_fluxx_cards(card_name)
            all_cards.extend(found_cards)
            results['cards_processed'] = len(found_cards)
        else:
            # Get cards based on mode and source
            if mode == 'cards':
                print(f"Getting {num_cards} cards from {data_source}...")

                if data_source in ['looney', 'all']:
                    looney_cards = get_cards_from_looney_labs("all", num_cards)
                    all_cards.extend(looney_cards)

                if data_source in ['boardgamegeek', 'all']:
                    bgg_cards = get_cards_from_boardgamegeek("all", num_cards)
                    all_cards.extend(bgg_cards)

                results['cards_processed'] = len(all_cards)

        if not all_cards:
            results['errors'].append("No cards found")
            return results

        # Save collection data
        os.makedirs(os.path.dirname(save_collection_path), exist_ok=True)

        # Create collection from cards
        collection_name = f"Fluxx Collection ({len(all_cards)} cards)"
        collection = FluxxDeck(
            name=collection_name,
            cards=all_cards,
            player="GUI User",
            id=f"gui_collection_{hash(str(all_cards))[:8]}"
        )
        save_collection_to_file(collection, save_collection_path)

        # Fetch images if requested
        if fetch_images:
            print("Fetching card images...")

            if all_cards:
                images_downloaded = process_fluxx_cards_batch(all_cards, output_dir)
                results['images_downloaded'] = images_downloaded

        results['success'] = True
        print("✅ Fluxx processing complete!")

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
    Get list of available data sources for Fluxx.

    Returns:
        List of source names
    """
    return ["looney", "boardgamegeek", "all"]


def validate_collection_url(url: str) -> bool:
    """
    Validate if a Fluxx collection URL is accessible.

    Args:
        url: Collection URL to validate

    Returns:
        True if URL is valid and accessible
    """
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200 and ('looneylabs' in url.lower() or 'fluxx' in url.lower())
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
        'name': 'Fluxx',
        'version': '1.0.0',
        'description': 'Process Fluxx card collections - the game where rules constantly change',
        'author': 'Silhouette Card Maker Team',
        'supported_modes': get_available_modes(),
        'available_sources': get_available_sources(),
        'has_image_support': True,
        'gui_integration': True,
        'notes': 'Card game where win conditions and rules change as you play'
    }


# Example GUI usage
if __name__ == '__main__':
    # Demo of GUI integration
    print("Fluxx Plugin - GUI Integration Demo")
    print("=" * 50)

    # Example parameters (would come from GUI)
    results = process_fluxx_cards(
        mode="cards",
        num_cards=10,
        data_source="looney",
        fetch_images=True
    )

    print(f"\nResults: {results}")
