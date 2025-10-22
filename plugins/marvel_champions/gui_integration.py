# Marvel Champions LCG Plugin - GUI Integration
# =============================================
# Entry point for GUI-based Marvel Champions deck processing

import os
import sys
import requests
from typing import List, Dict, Optional

# Import our plugin modules
from mc_scraper import Scenario, Hero, Deck, save_decks_to_file
from mc_api import process_mc_cards_batch

def process_marvel_champions_decks(
    mode: str = "scenarios",
    num_items: int = 3,
    output_dir: str = "game/front",
    save_decks_path: str = "game/decklist/mc_decks.txt",
    fetch_images: bool = False,
    scenario_url: Optional[str] = None,
    hero_name: Optional[str] = None,
    data_source: str = "cdb"
) -> Dict[str, any]:
    """
    Main entry point for Marvel Champions LCG processing via GUI.

    Args:
        mode: What to fetch ('scenarios', 'heroes', 'decks')
        num_items: Number of items to process
        output_dir: Directory for card images
        save_decks_path: File path for deck list output
        fetch_images: Whether to download card images
        scenario_url: Specific scenario URL (optional)
        hero_name: Specific hero name (optional)
        data_source: Source for data ('cdb', 'hoh', 'both')

    Returns:
        Dictionary with processing results and statistics
    """
    print("🦸‍♂️ Marvel Champions LCG Plugin - GUI Mode")
    print("=" * 50)
    print("Cooperative superhero card game!")

    from mc_scraper import get_scenarios_from_hall_of_heroes, get_heroes_from_marvelcdb
    from mc_api import get_scenario_decks

    results = {
        'success': False,
        'mode': mode,
        'items_processed': 0,
        'decks_found': 0,
        'images_downloaded': 0,
        'errors': []
    }

    try:
        all_decks = []

        if scenario_url:
            # Process specific scenario
            print(f"Processing scenario: {scenario_url}")
            scenario_decks = get_scenario_decks(scenario_url)
            all_decks.extend(scenario_decks)
            results['items_processed'] = 1
        elif hero_name:
            # Process specific hero
            print(f"Finding decks for hero: {hero_name}")
            # Would search for hero-specific decks
            print("Hero-specific processing not yet implemented.")
        else:
            # Process based on mode
            if mode == 'scenarios':
                print(f"Discovering scenarios from {data_source}...")

                scenarios = []

                if data_source in ['hoh', 'both']:
                    hoh_scenarios = get_scenarios_from_hall_of_heroes()
                    scenarios.extend(hoh_scenarios)

                if not scenarios:
                    results['errors'].append("No scenarios found from selected sources")
                    return results

                results['items_processed'] = len(scenarios)

                # Process each scenario (demo mode)
                for scenario in scenarios[:2]:  # Limit for GUI responsiveness
                    print(f"Processing: {scenario.name}")
                    # For demo, create sample decks
                    sample_deck = type('Deck', (), {
                        'name': f"Sample Deck - {scenario.name}",
                        'hero': 'Spider-Man',
                        'cards': [(1, "Hero Card"), (15, "Ally Card"), (10, "Event Card")],
                        'player': "GUI User",
                        'scenario_id': scenario.id,
                        'hash': "gui_demo_hash"
                    })()
                    all_decks.append(sample_deck)

            elif mode == 'heroes':
                print(f"Discovering heroes from {data_source}...")

                heroes = []

                if data_source in ['cdb', 'both']:
                    cdb_heroes = get_heroes_from_marvelcdb()
                    heroes.extend(cdb_heroes)

                if not heroes:
                    results['errors'].append("No heroes found from selected sources")
                    return results

                results['items_processed'] = len(heroes)

                # Show hero information (no decks for heroes mode)
                print(f"Found {len(heroes)} heroes:")
                for hero in heroes:
                    print(f"  {hero.name} ({hero.hero_class})")

        results['decks_found'] = len(all_decks)

        if not all_decks and mode != 'heroes':  # Heroes mode doesn't produce decks
            results['errors'].append("No decks found")
            return results

        # Save deck data (if we have decks)
        if all_decks:
            os.makedirs(os.path.dirname(save_decks_path), exist_ok=True)
            save_decks_to_file(all_decks, save_decks_path)

        # Fetch images if requested and we have cards
        if fetch_images and all_decks:
            print("Fetching card images...")
            # Extract unique cards
            unique_cards = {}
            for deck in all_decks:
                for quantity, card_name in deck.cards:
                    unique_cards[card_name] = max(unique_cards.get(card_name, 0), quantity)

            cards_list = [(q, name) for name, q in unique_cards.items()]

            if cards_list:
                images_downloaded = process_mc_cards_batch(cards_list, output_dir)
                results['images_downloaded'] = images_downloaded

        results['success'] = True
        print("✅ Marvel Champions processing complete!")

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
    return ["scenarios", "heroes", "decks"]


def get_available_sources() -> List[str]:
    """
    Get list of available data sources.

    Returns:
        List of source names
    """
    return ["cdb", "hoh", "both"]


def validate_scenario_url(url: str) -> bool:
    """
    Validate if a Marvel Champions scenario URL is accessible.

    Args:
        url: Scenario URL to validate

    Returns:
        True if URL is valid and accessible
    """
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200 and ('hallofheroes' in url.lower() or 'marvel' in url.lower())
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
        'name': 'Marvel Champions LCG',
        'version': '1.0.0',
        'description': 'Process Marvel Champions LCG decks for cooperative play',
        'author': 'Silhouette Card Maker Team',
        'supported_modes': get_available_modes(),
        'available_sources': get_available_sources(),
        'has_image_support': True,
        'gui_integration': True,
        'notes': 'Cooperative game - focuses on scenarios rather than competitive play'
    }


# Example GUI usage
if __name__ == '__main__':
    # Demo of GUI integration
    print("Marvel Champions Plugin - GUI Integration Demo")
    print("=" * 50)

    # Example parameters (would come from GUI)
    results = process_marvel_champions_decks(
        mode="scenarios",
        num_items=2,
        data_source="hoh",
        fetch_images=True
    )

    print(f"\nResults: {results}")
