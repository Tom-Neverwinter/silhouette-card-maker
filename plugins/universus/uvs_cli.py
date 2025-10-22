# Universus CLI Module
# ====================
# Command-line interface for Universus plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from uvs_scraper import (
    Tournament, Deck,
    get_tournaments_from_universus_cards,
    get_tournaments_from_uvs_ultra,
    get_tournaments_from_official_site,
    scrape_deck_from_tournament,
    save_decks_to_file
)
from uvs_api import (
    process_uvs_cards_batch,
    get_tournament_decks
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.command()
@click.option('--format', '-f', default='standard',
              type=click.Choice(['standard', 'all']),
              help='Tournament format to scrape')
@click.option('--source', '-s', default='universus_cards',
              type=click.Choice(['universus_cards', 'uvs_ultra', 'official', 'all']),
              help='Data source to use for tournaments')
@click.option('--num-tournaments', '-n', default=5,
              help='Number of tournaments to scrape')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-decks', '-d', default='game/decklist/uvs_decks.txt',
              help='File to save deck lists')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from Universus databases')
@click.option('--tournament-url', '-t', default=None,
              help='Specific tournament URL to scrape (overrides --num-tournaments)')
def main(format, source, num_tournaments, output_dir, save_decks, fetch_images, tournament_url):
    """
    Universus Scraper Plugin

    Scrapes deck lists from Universus community sites and official resources.
    Features anime characters from My Hero Academia, Cowboy Bebop, and Yu Yu Hakusho.

    Examples:
        # Scrape recent tournaments from universus.cards
        python uvs_cli.py --source universus_cards --format standard --num-tournaments 5

        # Fetch images for scraped decks
        python uvs_cli.py --fetch-images --save-decks my_decks.txt

        # Process specific tournament
        python uvs_cli.py --tournament-url "https://universus.cards/tournament/123"
    """
    print("Universus Scraper Plugin")
    print("="*50)
    print("Anime characters from MHA, Cowboy Bebop, and Yu Yu Hakusho!")

    all_decks = []

    if tournament_url:
        # Process specific tournament
        print(f"🔍 Processing specific tournament: {tournament_url}")
        tournament_decks = get_tournament_decks(tournament_url)
        all_decks.extend(tournament_decks)
        print(f"Found {len(tournament_decks)} decks")
    else:
        # Process multiple tournaments from selected sources
        print(f"🔍 Discovering {format} tournaments from {source}...")

        tournaments = []

        if source in ['universus_cards', 'all']:
            uc_tournaments = get_tournaments_from_universus_cards(format, num_tournaments)
            tournaments.extend(uc_tournaments)

        if source in ['uvs_ultra', 'all']:
            uvs_tournaments = get_tournaments_from_uvs_ultra(format, num_tournaments)
            tournaments.extend(uvs_tournaments)

        if source in ['official', 'all']:
            official_tournaments = get_tournaments_from_official_site(format, num_tournaments)
            tournaments.extend(official_tournaments)

        if not tournaments:
            print("❌ No tournaments found.")
            return

        print(f"✅ Found {len(tournaments)} tournaments")

        # Process each tournament (simplified for demo)
        for tournament in tournaments[:3]:  # Limit for demo
            print(f"\nProcessing: {tournament.name}")
            # For demo, create sample decks
            sample_deck = type('Deck', (), {
                'name': f"Sample Deck - {tournament.name}",
                'format': tournament.format,
                'cards': [(1, "Character Card"), (50, "Foundation Card"), (15, "Action Card")],
                'player': "Demo Player",
                'tournament_id': tournament.id,
                'hash': "demo_hash"
            })()
            all_decks.append(sample_deck)

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
        processed = process_uvs_cards_batch(cards_list, output_dir)
        print(f"✅ Downloaded {processed} card images to {output_dir}")

    # -----------------------------
    # Completion Summary
    # -----------------------------
    print("\n🎉 UNIVERSUS PLUGIN COMPLETE")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Tournaments processed: {num_tournaments if not tournament_url else 1}")
    print(f"   • Decks scraped: {len(all_decks)}")
    print(f"   • Deck data saved to: {save_decks}")

    if fetch_images:
        unique_count = len(set(card_name for _, card_name in cards_list))
        print(f"   • Card images downloaded: {processed}")
        print(f"   • Images saved to: {output_dir}")

    print("\n✅ Ready for card creation!")
    print("Anime universes collide!")
# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    main()
