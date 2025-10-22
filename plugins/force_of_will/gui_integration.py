# Force of Will TCG Plugin - GUI Integration
# ==========================================
# Entry point for GUI-based Force of Will deck processing

import os
import sys
import requests
from typing import List, Dict, Optional

# Import our plugin modules
from fow_scraper import Tournament, Deck, save_decks_to_file
from fow_api import process_fow_cards_batch

def process_force_of_will_decks(
    format_type: str = "standard",
    num_tournaments: int = 3,
    output_dir: str = "game/front",
    save_decks_path: str = "game/decklist/fow_decks.txt",
    fetch_images: bool = False,
    tournament_url: Optional[str] = None,
    data_source: str = "official"
) -> Dict[str, any]:
    """
    Main entry point for Force of Will TCG processing via GUI.

    Args:
        format_type: Tournament format ('standard', 'all')
        num_tournaments: Number of tournaments to process
        output_dir: Directory for card images
        save_decks_path: File path for deck list output
        fetch_images: Whether to download card images
        tournament_url: Specific tournament URL (optional)
        data_source: Source for tournament data ('official', 'library', 'both')

    Returns:
        Dictionary with processing results and statistics
    """
    print("⚔️ Force of Will TCG Plugin - GUI Mode")
    print("=" * 50)
    print("Note: Force of Will has a smaller competitive scene.")

    from fow_scraper import get_tournaments_from_official_site, get_tournaments_from_library_of_will
    from fow_api import get_tournament_decks

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

            if data_source in ['official', 'both']:
                official_tournaments = get_tournaments_from_official_site(format_type, num_tournaments)
                tournaments.extend(official_tournaments)

            if data_source in ['library', 'both']:
                library_tournaments = get_tournaments_from_library_of_will(format_type, num_tournaments)
                tournaments.extend(library_tournaments)

            if not tournaments:
                results['errors'].append("No tournaments found from selected sources")
                return results

            results['tournaments_processed'] = len(tournaments)

            # Process each tournament (demo mode)
            for tournament in tournaments[:2]:  # Limit for GUI responsiveness
                print(f"Processing: {tournament.name}")
                # For demo, create sample decks
                sample_deck = type('Deck', (), {
                    'name': f"Sample FoW Deck - {tournament.name}",
                    'format': tournament.format,
                    'cards': [(1, "Ruler Card"), (20, "Magic Stone"), (15, "Resonator Card")],
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
                images_downloaded = process_fow_cards_batch(cards_list, output_dir)
                results['images_downloaded'] = images_downloaded

        results['success'] = True
        print("✅ Force of Will processing complete!")

        return results

    except Exception as e:
        results['errors'].append(f"Processing error: {str(e)}")
        print(f"❌ Error: {e}")
        return results


def get_available_formats() -> List[str]:
    """
    Get list of available Force of Will formats.

    Returns:
        List of supported format names
    """
    return ["standard", "all"]


def get_available_sources() -> List[str]:
    """
    Get list of available data sources for Force of Will.

    Returns:
        List of source names
    """
    return ["official", "library", "both"]


def validate_tournament_url(url: str) -> bool:
    """
    Validate if a Force of Will tournament URL is accessible.

    Args:
        url: Tournament URL to validate

    Returns:
        True if URL is valid and accessible
    """
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200 and 'fowtcg' in url.lower()
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
        'name': 'Force of Will TCG',
        'version': '1.0.0',
        'description': 'Process Force of Will TCG decks and tournaments',
        'author': 'Silhouette Card Maker Team',
        'supported_formats': get_available_formats(),
        'available_sources': get_available_sources(),
        'has_image_support': True,
        'gui_integration': True,
        'notes': 'Smaller competitive scene compared to other TCGs'
    }


# Example GUI usage
if __name__ == '__main__':
    # Demo of GUI integration
    print("Force of Will Plugin - GUI Integration Demo")
    print("=" * 50)

    # Example parameters (would come from GUI)
    results = process_force_of_will_decks(
        format_type="standard",
        num_tournaments=2,
        data_source="official",
        fetch_images=True
    )

    print(f"\nResults: {results}")
