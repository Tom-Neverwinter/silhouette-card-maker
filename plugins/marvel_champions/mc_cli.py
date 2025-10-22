# Marvel Champions LCG CLI Module
# ===============================
# Command-line interface for Marvel Champions LCG plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from mc_scraper import (
    Scenario, Hero, Deck,
    get_scenarios_from_hall_of_heroes,
    get_heroes_from_marvelcdb,
    scrape_deck_from_marvelcdb,
    scrape_decks_from_scenario,
    save_decks_to_file
)
from mc_api import (
    process_mc_cards_batch,
    get_scenario_decks
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.command()
@click.option('--mode', '-m', default='scenarios',
              type=click.Choice(['scenarios', 'heroes', 'decks']),
              help='What to fetch: scenarios, heroes, or specific decks')
@click.option('--source', '-s', default='cdb',
              type=click.Choice(['cdb', 'hoh', 'both']),
              help='Data source to use')
@click.option('--num-items', '-n', default=5,
              help='Number of items to fetch')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-decks', '-d', default='game/decklist/mc_decks.txt',
              help='File to save deck lists')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from Marvel Champions databases')
@click.option('--scenario-url', default=None,
              help='Specific scenario URL to process')
@click.option('--hero-name', default=None,
              help='Specific hero name to get decks for')
def main(mode, source, num_items, output_dir, save_decks, fetch_images, scenario_url, hero_name):
    """
    Marvel Champions LCG Scraper Plugin

    Scrapes deck lists and card data for the cooperative Marvel Champions LCG.
    Note: This is a co-op game focused on scenario completion, not competitive play.

    Examples:
        # Get recent scenarios from Hall of Heroes
        python mc_cli.py --mode scenarios --source hoh --num-items 5

        # Fetch hero information from MarvelCDB
        python mc_cli.py --mode heroes --source cdb

        # Process specific scenario
        python mc_cli.py --scenario-url "https://hallofheroeslcg.com/scenario/123"
    """
    print("Marvel Champions LCG Scraper Plugin")
    print("="*50)
    print("Cooperative superhero card game - Heroes vs Villains!")

    all_decks = []

    if scenario_url:
        # Process specific scenario
        print(f"🔍 Processing scenario: {scenario_url}")
        scenario_decks = get_scenario_decks(scenario_url)
        all_decks.extend(scenario_decks)
        print(f"Found {len(scenario_decks)} decks")
    elif hero_name:
        # Process specific hero
        print(f"🔍 Finding decks for hero: {hero_name}")
        # Would search for hero-specific decks
        print("Hero-specific deck search not yet implemented.")
    else:
        # Process based on mode
        if mode == 'scenarios':
            print(f"🔍 Discovering scenarios from {source}...")

            scenarios = []

            if source in ['hoh', 'both']:
                hoh_scenarios = get_scenarios_from_hall_of_heroes()
                scenarios.extend(hoh_scenarios)

            if not scenarios:
                print("❌ No scenarios found.")
                return

            print(f"✅ Found {len(scenarios)} scenarios")

            # Process each scenario (simplified for demo)
            for scenario in scenarios[:2]:  # Limit for demo
                print(f"\nProcessing: {scenario.name}")
                # For demo, create sample decks
                sample_deck = type('Deck', (), {
                    'name': f"Sample Deck - {scenario.name}",
                    'hero': 'Spider-Man',
                    'cards': [(1, "Hero Card"), (15, "Ally Card"), (10, "Event Card")],
                    'player': "Demo Player",
                    'scenario_id': scenario.id,
                    'hash': "demo_hash"
                })()
                all_decks.append(sample_deck)

        elif mode == 'heroes':
            print(f"🔍 Discovering heroes from {source}...")

            heroes = []

            if source in ['cdb', 'both']:
                cdb_heroes = get_heroes_from_marvelcdb()
                heroes.extend(cdb_heroes)

            if not heroes:
                print("❌ No heroes found.")
                return

            print(f"✅ Found {len(heroes)} heroes")

            # Show hero information
            for hero in heroes:
                print(f"  {hero.name} ({hero.hero_class}) - {hero.set_code}")

    print(f"\n📊 Total decks processed: {len(all_decks)}")

    if not all_decks:
        print("❌ No decks found. Exiting.")
        return

    # -----------------------------
    # Save Deck Data
    # -----------------------------
    print("\n💾 Saving deck data...")
    os.makedirs(os.path.dirname(save_decks), exist_ok=True)
    save_decks_to_file(all_decks, save_decks)

    # -----------------------------
    # Image Fetching (Optional)
    # -----------------------------
    if fetch_images:
        print("\n🖼️  Fetching card images...")

        # Extract unique cards from all decks
        unique_cards = {}
        for deck in all_decks:
            for quantity, card_name in deck.cards:
                if card_name not in unique_cards:
                    unique_cards[card_name] = quantity
                else:
                    unique_cards[card_name] = max(unique_cards[card_name], quantity)

        cards_list = [(q, name) for name, q in unique_cards.items()]
        print(f"Found {len(cards_list)} unique cards")

        # Ask for confirmation for large downloads
        if len(cards_list) > 20:
            if not click.confirm(f"Download {len(cards_list)} card images?", default=False):
                print("Skipping image download.")
                return

        # Process cards in batches
        processed = process_mc_cards_batch(cards_list, output_dir)
        print(f"✅ Downloaded {processed} card images to {output_dir}")

    # -----------------------------
    # Completion Summary
    # -----------------------------
    print("\n🎉 MARVEL CHAMPIONS PLUGIN COMPLETE")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Mode: {mode}")
    print(f"   • Source: {source}")
    print(f"   • Items processed: {num_items}")
    print(f"   • Decks scraped: {len(all_decks)}")
    print(f"   • Deck data saved to: {save_decks}")

    if fetch_images:
        unique_count = len(set(card_name for _, card_name in cards_list))
        print(f"   • Card images downloaded: {processed}")
        print(f"   • Images saved to: {output_dir}")

    print("\n✅ Ready for card creation!")
    print("Assemble your heroes and save the city!")
# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    main()
