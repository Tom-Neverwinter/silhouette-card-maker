# Pokemon TCG CLI Module
# ======================
# This module provides the command-line interface for the Pokemon TCG
# plugin, coordinating scraping, API calls, and user interaction.

import os
import sys
import click
from typing import List

# Import our custom modules
from pokemon_scraper import (
    Tournament, Deck,
    get_sanctioned_tournaments,
    get_unsanctioned_tournaments,
    scrape_deck_from_tournament,
    save_decks_to_file
)
from pokemon_api import (
    fetch_card_images_pokemontcg,
    get_unique_cards_from_decks
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.command()
@click.option('--format', '-f', default='standard',
              type=click.Choice(['standard', 'expanded', 'all']),
              help='Tournament format to scrape')
@click.option('--sanctioned/--unsanctioned', default=True,
              help='Scrape sanctioned or unsanctioned tournaments')
@click.option('--num-tournaments', '-n', default=5,
              help='Number of tournaments to scrape (-1 for all)')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-decks', '-s', default='game/decklist/scraped_decks.txt',
              help='File to save deck lists')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from Pokemon TCG API')
def main(format, sanctioned, num_tournaments, output_dir, save_decks, fetch_images):
    """
    Pokemon TCG LimitlessTCG Scraper Plugin

    Scrapes deck lists from LimitlessTCG and optionally fetches card images
    from the Pokemon TCG API. Supports both sanctioned (official) and
    unsanctioned (online) tournaments.

    Examples:
        # Scrape 5 standard sanctioned tournaments
        python pokemon_cli.py --sanctioned --format standard --num-tournaments 5

        # Scrape all expanded unsanctioned tournaments and fetch images
        python pokemon_cli.py --unsanctioned --format expanded --fetch-images

        # Scrape 10 tournaments of any format
        python pokemon_cli.py --num-tournaments 10 --format all
    """
    print("Pokemon TCG LimitlessTCG Scraper Plugin")
    print("="*50)

    # -----------------------------
    # Tournament Discovery Phase
    # -----------------------------
    print("🔍 DISCOVERING TOURNAMENTS")
    print("-" * 30)

    # Get tournaments based on user preferences
    if sanctioned:
        print(f"Fetching sanctioned {format} tournaments...")
        tournaments = get_sanctioned_tournaments(format, num_tournaments)
    else:
        print(f"Fetching unsanctioned {format} tournaments...")
        tournaments = get_unsanctioned_tournaments(format, num_tournaments)

    print(f"\n✅ Found {len(tournaments)} tournaments")

    if not tournaments:
        print("❌ No tournaments found. Exiting.")
        return

    # Show tournament summary
    for i, tournament in enumerate(tournaments, 1):
        print(f"  {i}. {tournament.name} ({tournament.date}) - {tournament.entries} players")

    # -----------------------------
    # Deck Scraping Phase
    # -----------------------------
    print("\n📋 SCRAPING DECKS")
    print("-" * 30)

    all_decks = []
    for tournament in tournaments:
        print(f"\nProcessing: {tournament.name}")
        decks = scrape_deck_from_tournament(tournament)
        all_decks.extend(decks)
        print(f"  Found {len(decks)} decks")

    print(f"\n✅ Scraped {len(all_decks)} total decks")

    if not all_decks:
        print("❌ No decks found. Exiting.")
        return

    # -----------------------------
    # Data Export Phase
    # -----------------------------
    print("\n💾 SAVING DATA")
    print("-" * 30)

    # Create output directory for deck files
    os.makedirs(os.path.dirname(save_decks), exist_ok=True)

    # Save deck lists to text file
    save_decks_to_file(all_decks, save_decks)

    # -----------------------------
    # Image Fetching Phase (Optional)
    # -----------------------------
    if fetch_images and all_decks:
        print("\n🖼️  FETCHING CARD IMAGES")
        print("-" * 30)

        # Get unique cards across all decks (consolidate quantities)
        unique_cards = get_unique_cards_from_decks(all_decks)

        print(f"Found {len(unique_cards)} unique cards")

        # Ask for confirmation for large image downloads
        if len(unique_cards) > 50:
            print(f"\n⚠️  This will download {len(unique_cards)} card images.")
            if not click.confirm("Continue with image download?", default=False):
                print("Skipping image download.")
                return

        # Fetch card images using Pokemon TCG API
        cards_list = [(q, name) for q, name in unique_cards]
        fetch_card_images_pokemontcg(cards_list, output_dir)

        print("✅ Image fetching complete!")

    # -----------------------------
    # Completion Summary
    # -----------------------------
    print("\n🎉 PLUGIN EXECUTION COMPLETE")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Tournaments processed: {len(tournaments)}")
    print(f"   • Decks scraped: {len(all_decks)}")
    print(f"   • Deck data saved to: {save_decks}")

    if fetch_images:
        unique_count = len(get_unique_cards_from_decks(all_decks))
        print(f"   • Card images downloaded: {unique_count}")
        print(f"   • Images saved to: {output_dir}")

    print("
✅ Done! Ready for card creation."
# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    # Run the CLI when this script is executed directly
    main()
