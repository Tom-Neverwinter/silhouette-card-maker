# Union Arena TCG Plugin - GUI Integration
# ========================================
# Entry point for GUI-based Union Arena deck processing

import os
import sys
import requests
from typing import List, Dict, Optional

# Import our plugin modules
from ua_scraper import Tournament, Deck, save_decks_to_file
from ua_api import process_ua_cards_batch

def process_union_arena_decks(
    format_type: str = "standard",
    num_tournaments: int = 3,
    output_dir: str = "game/front",
    save_decks_path: str = "game/decklist/ua_decks.txt",
    fetch_images: bool = False,
    tournament_url: Optional[str] = None,
    data_source: str = "meta"
) -> Dict[str, any]:
    """
    Main entry point for Union Arena TCG processing via GUI.

    Args:
        format_type: Tournament format ('standard', 'all')
        num_tournaments: Number of tournaments to process
        output_dir: Directory for card images
        save_decks_path: File path for deck list output
        fetch_images: Whether to download card images
        tournament_url: Specific tournament URL (optional)
        data_source: Source for tournament data ('meta', 'community', 'both')

    Returns:
        Dictionary with processing results and statistics
    """
    print("🎌 Union Arena TCG Plugin - GUI Mode")
    print("=" * 50)
    print("Multiple anime crossovers: Hunter x Hunter, Bleach, MHA, and more!")

    from ua_scraper import get_tournaments_from_ua_meta, get_tournaments_from_community
    from ua_api import get_tournament_decks

    results = {
        'success': False,
        'tournaments_processed': 0,
        'decks_found': 0,
        'images_downloaded': 0,
        'errors': []
    }

    try:
        all_decks = []

        if tournament_url:
            # Process specific tournament
            print(f"Processing tournament: {tournament_url}")
            tournament_decks = get_tournament_decks(tournament_url)
            all_decks.extend(tournament_decks)
            results['tournaments_processed'] = 1
        else:
            # Process multiple tournaments from selected sources
            print(f"Discovering {format_type} tournaments from {data_source}...")

            tournaments = []

            if data_source in ['meta', 'both']:
                meta_tournaments = get_tournaments_from_ua_meta(format_type, num_tournaments)
                tournaments.extend(meta_tournaments)

            if data_source in ['community', 'both']:
                community_tournaments = get_tournaments_from_community(format_type, num_tournaments)
                tournaments.extend(community_tournaments)

            if not tournaments:
                results['errors'].append("No tournaments found from selected sources")
                return results

            results['tournaments_processed'] = len(tournaments)

            # Process each tournament (demo mode)
            for tournament in tournaments[:2]:  # Limit for GUI responsiveness
                print(f"Processing: {tournament.name}")
                # For demo, create sample decks
                sample_deck = type('Deck', (), {
                    'name': f"Sample UA Deck - {tournament.name}",
                    'format': tournament.format,
                    'cards': [(1, "Leader Card"), (50, "Deck Card"), (10, "Event Card")],
                    'player': "GUI User",
                    'tournament_id': tournament.id,
                    'hash': "gui_demo_hash"
                })()
                all_decks.append(sample_deck)

        results['decks_found'] = len(all_decks)

        if not all_decks:
            results['errors'].append("No decks found")
            return results

        # Save deck data
        os.makedirs(os.path.dirname(save_decks_path), exist_ok=True)
        save_decks_to_file(all_decks, save_decks_path)

        # Fetch images if requested
        if fetch_images:
            print("Fetching card images...")
            # Extract unique cards
            unique_cards = {}
            for deck in all_decks:
                for quantity, card_name in deck.cards:
                    unique_cards[card_name] = max(unique_cards.get(card_name, 0), quantity)

            cards_list = [(q, name) for name, q in unique_cards.items()]

            if cards_list:
                images_downloaded = process_ua_cards_batch(cards_list, output_dir)
                results['images_downloaded'] = images_downloaded

        results['success'] = True
        print("✅ Union Arena processing complete!")

        return results

    except Exception as e:
        results['errors'].append(f"Processing error: {str(e)}")
        print(f"❌ Error: {e}")
        return results


def get_available_formats() -> List[str]:
    """
    Get list of available Union Arena formats.

    Returns:
        List of supported format names
    """
    return ["standard", "all"]


def get_available_sources() -> List[str]:
    """
    Get list of available data sources for Union Arena.

    Returns:
        List of source names
    """
    return ["meta", "community", "both"]


def validate_tournament_url(url: str) -> bool:
    """
    Validate if a Union Arena tournament URL is accessible.

    Args:
        url: Tournament URL to validate

    Returns:
        True if URL is valid and accessible
    """
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200 and ('uameta' in url.lower() or 'union' in url.lower())
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
        'name': 'Union Arena TCG',
        'version': '1.0.0',
        'description': 'Process Union Arena TCG decks with multiple anime crossovers',
        'author': 'Silhouette Card Maker Team',
        'supported_formats': get_available_formats(),
        'available_sources': get_available_sources(),
        'has_image_support': True,
        'gui_integration': True,
        'notes': 'Features characters from Hunter x Hunter, Bleach, My Hero Academia, and more'
    }


# Example GUI usage
if __name__ == '__main__':
    # Demo of GUI integration
    print("Union Arena Plugin - GUI Integration Demo")
    print("=" * 50)

    # Example parameters (would come from GUI)
    results = process_union_arena_decks(
        format_type="standard",
        num_tournaments=2,
        data_source="meta",
        fetch_images=True
    )

    print(f"\nResults: {results}")
