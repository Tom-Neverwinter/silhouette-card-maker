# Weiß Schwarz Plugin - GUI Integration
# =====================================
# Entry point for GUI-based Weiß Schwarz deck processing

import os
import sys
import requests
from typing import List, Dict, Optional

# Import our plugin modules
from ws_scraper import Tournament, Deck, save_decks_to_file
from ws_api import process_ws_cards_batch, parse_deck_from_url, search_ws_cards

def process_weiss_schwarz_decks(
    format_type: str = "standard",
    num_tournaments: int = 3,
    output_dir: str = "game/front",
    save_decks_path: str = "game/decklist/ws_decks.txt",
    fetch_images: bool = False,
    tournament_url: Optional[str] = None,
    data_source: str = "weissteatime",
    deck_url: Optional[str] = None,
    search_card: Optional[str] = None
) -> Dict[str, any]:
    """
    Main entry point for Weiß Schwarz processing via GUI.

    Args:
        format_type: Tournament format ('standard', 'all')
        num_tournaments: Number of tournaments to process
        output_dir: Directory for card images
        save_decks_path: File path for deck list output
        fetch_images: Whether to download card images
        tournament_url: Specific tournament URL (optional)
        data_source: Source for tournament data ('weissteatime', 'official', 'both')
        deck_url: Parse a specific deck from EncoreDecks or DeckLog URL
        search_card: Search for a specific card by name

    Returns:
        Dictionary with processing results and statistics
    """
    print("🎭 Weiß Schwarz Plugin - GUI Mode")
    print("=" * 50)
    print("Massive anime crossovers: Attack on Titan, Fate, Re:Zero, and more!")

    from ws_scraper import get_tournaments_from_weissteatime, get_tournaments_from_official_site
    from ws_api import get_tournament_decks

    results = {
        'success': False,
        'tournaments_processed': 0,
        'decks_found': 0,
        'images_downloaded': 0,
        'errors': []
    }

    try:
        all_decks = []

        # Handle deck URL parsing
        if deck_url:
            print(f"🔍 Parsing deck from URL: {deck_url}")
            deck_data = parse_deck_from_url(deck_url)
            if deck_data:
                deck = Deck(
                    name=deck_data['name'],
                    format=deck_data['format'],
                    cards=deck_data['cards'],
                    player=deck_data['player'],
                    tournament_id="url_parsed"
                )
                all_decks.append(deck)
                results['decks_found'] = 1
                print(f"✅ Successfully parsed deck: {deck_data['name']}")
            else:
                results['errors'].append("Failed to parse deck from URL")
                return results

        # Handle card search
        elif search_card:
            print(f"🔍 Searching for card: {search_card}")
            cards = search_ws_cards(search_card)
            if cards:
                print(f"✅ Found {len(cards)} matching cards:")
                for i, card in enumerate(cards, 1):
                    print(f"  {i}. {card.name} ({card.set_code}) - {card.rarity}")
                results['success'] = True
                results['cards_found'] = len(cards)
            else:
                results['errors'].append("No cards found")
            return results

        elif tournament_url:
            # Process specific tournament
            print(f"Processing tournament: {tournament_url}")
            tournament_decks = get_tournament_decks(tournament_url)
            all_decks.extend(tournament_decks)
            results['tournaments_processed'] = 1
        else:
            # Process multiple tournaments from selected sources
            print(f"Discovering {format_type} tournaments from {data_source}...")

            tournaments = []

            if data_source in ['weissteatime', 'both']:
                wtt_tournaments = get_tournaments_from_weissteatime(format_type, num_tournaments)
                tournaments.extend(wtt_tournaments)

            if data_source in ['official', 'both']:
                official_tournaments = get_tournaments_from_official_site(format_type, num_tournaments)
                tournaments.extend(official_tournaments)

            if not tournaments:
                results['errors'].append("No tournaments found from selected sources")
                return results

            results['tournaments_processed'] = len(tournaments)

            # Process each tournament (demo mode)
            for tournament in tournaments[:2]:  # Limit for GUI responsiveness
                print(f"Processing: {tournament.name}")
                # For demo, create sample decks
                sample_deck = type('Deck', (), {
                    'name': f"Sample WS Deck - {tournament.name}",
                    'format': tournament.format,
                    'cards': [(4, "Level 0 Card"), (50, "Level 1-3 Cards"), (4, "Climax Card")],
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
                images_downloaded = process_ws_cards_batch(cards_list, output_dir)
                results['images_downloaded'] = images_downloaded

        results['success'] = True
        print("✅ Weiß Schwarz processing complete!")

        return results

    except Exception as e:
        results['errors'].append(f"Processing error: {str(e)}")
        print(f"❌ Error: {e}")
        return results


def get_available_formats() -> List[str]:
    """
    Get list of available Weiß Schwarz formats.

    Returns:
        List of supported format names
    """
    return ["standard", "all"]


def get_available_sources() -> List[str]:
    """
    Get list of available data sources for Weiß Schwarz.

    Returns:
        List of source names
    """
    return ["weissteatime", "official", "both"]


def validate_tournament_url(url: str) -> bool:
    """
    Validate if a Weiß Schwarz tournament URL is accessible.

    Args:
        url: Tournament URL to validate

    Returns:
        True if URL is valid and accessible
    """
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200 and ('weissteatime' in url.lower() or 'ws-tcg' in url.lower())
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
        'name': 'Weiß Schwarz',
        'version': '1.0.0',
        'description': 'Process Weiß Schwarz decks with massive anime crossovers',
        'author': 'Silhouette Card Maker Team',
        'supported_formats': get_available_formats(),
        'available_sources': get_available_sources(),
        'has_image_support': True,
        'gui_integration': True,
        'notes': 'Features Attack on Titan, Fate/stay night, Re:Zero, and many more anime series'
    }


# Example GUI usage
if __name__ == '__main__':
    # Demo of GUI integration
    print("Weiß Schwarz Plugin - GUI Integration Demo")
    print("=" * 50)

    # Example parameters (would come from GUI)
    results = process_weiss_schwarz_decks(
        format_type="standard",
        num_tournaments=2,
        data_source="weissteatime",
        fetch_images=True
    )

    print(f"\nResults: {results}")
