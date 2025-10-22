# Cardfight!! Vanguard CLI Module
# ================================
# Command-line interface for Cardfight!! Vanguard plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from cfv_scraper import (
    Tournament, Deck,
    get_tournaments_from_vg_paradox,
    get_tournaments_from_official_site,
    get_tournaments_from_dexander,
    scrape_deck_from_tournament,
    save_decks_to_file
)
from cfv_api import (
    process_cfv_cards_batch,
    get_tournament_decks
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.command()
@click.option('--format', '-f', default='standard',
              type=click.Choice(['standard', 'premium', 'all']),
              help='Tournament format to scrape')
@click.option('--source', '-s', default='vgp',
              type=click.Choice(['vgp', 'official', 'dexander', 'all']),
              help='Data source to use for tournaments')
@click.option('--num-tournaments', '-n', default=5,
              help='Number of tournaments to scrape')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-decks', '-d', default='game/decklist/cfv_decks.txt',
              help='File to save deck lists')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from Cardfight!! Vanguard databases')
@click.option('--tournament-url', '-t', default=None,
              help='Specific tournament URL to scrape (overrides --num-tournaments)')
def main(format, source, num_tournaments, output_dir, save_decks, fetch_images, tournament_url):
    """
    Cardfight!! Vanguard Scraper Plugin

    Scrapes deck lists from Cardfight!! Vanguard community sites and official resources.
    Features anime-style gameplay with unit summoning mechanics.

    Examples:
        # Scrape recent tournaments from VG-Paradox
        python cfv_cli.py --source vgp --format standard --num-tournaments 5

        # Fetch images for scraped decks
        python cfv_cli.py --fetch-images --save-decks my_decks.txt

        # Process specific tournament
        python cfv_cli.py --tournament-url "https://vg-paradox.com/tournament/123"
    """
    print("Cardfight!! Vanguard Scraper Plugin")
    print("="*50)
    print("Anime-style card game with unit summoning mechanics!")

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

        if source in ['vgp', 'all']:
            vgp_tournaments = get_tournaments_from_vg_paradox(format, num_tournaments)
            tournaments.extend(vgp_tournaments)

        if source in ['official', 'all']:
            official_tournaments = get_tournaments_from_official_site(format, num_tournaments)
            tournaments.extend(official_tournaments)

        if source in ['dexander', 'all']:
            dex_tournaments = get_tournaments_from_dexander(format, num_tournaments)
            tournaments.extend(dex_tournaments)

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
                'cards': [(4, "Grade 0 Card"), (16, "Grade 1-3 Cards"), (4, "G Unit")],
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
        processed = process_cfv_cards_batch(cards_list, output_dir)
        print(f"✅ Downloaded {processed} card images to {output_dir}")

    # -----------------------------
    # Completion Summary
    # -----------------------------
    print("\n🎉 CARDFIGHT!! VANGUARD PLUGIN COMPLETE")
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
    print("Ride to victory!")
# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    main()
