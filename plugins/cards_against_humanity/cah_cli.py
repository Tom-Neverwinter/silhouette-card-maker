# Cards Against Humanity CLI Module
# =================================
# Command-line interface for Cards Against Humanity plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from cah_scraper import (
    CAHCard, CAHCollection,
    get_cards_from_cah_database,
    get_cards_from_community_spreadsheet,
    create_collection_from_cards,
    save_collection_to_file
)
from cah_api import (
    process_cah_cards_batch,
    get_collection_cards,
    search_cah_cards
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.command()
@click.option('--mode', '-m', default='cards',
              type=click.Choice(['cards', 'collection', 'search']),
              help='What to fetch: cards, collection, or search')
@click.option('--source', '-s', default='database',
              type=click.Choice(['database', 'community', 'all']),
              help='Data source to use')
@click.option('--card-type', '-t', default='all',
              type=click.Choice(['all', 'black', 'white']),
              help='Card type to filter by')
@click.option('--num-cards', '-n', default=20,
              help='Number of cards to fetch')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-collection', '-c', default='game/decklist/cah_collection.txt',
              help='File to save card collection')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from CAH databases')
@click.option('--card-text', default=None,
              help='Specific card text to search for')
@click.option('--collection-url', default=None,
              help='Specific collection URL to process')
def main(mode, source, card_type, num_cards, output_dir, save_collection, fetch_images, card_text, collection_url):
    """
    Cards Against Humanity Scraper Plugin

    Processes Cards Against Humanity card collections and data from various sources.
    Note: CAH contains mature, offensive content - use with appropriate audiences.

    Examples:
        # Get cards from CAH database
        python cah_cli.py --source database --card-type black --num-cards 10

        # Fetch images for card collection
        python cah_cli.py --mode collection --fetch-images

        # Search for specific card
        python cah_cli.py --card-text "Why can't I sleep at night?"
    """
    print("Cards Against Humanity Scraper Plugin")
    print("="*50)
    print("⚠️  WARNING: Contains mature, offensive content")
    print("Use only with appropriate audiences!")

    all_black_cards = []
    all_white_cards = []

    if collection_url:
        # Process specific collection
        print(f"🔍 Processing collection: {collection_url}")
        black_cards, white_cards = get_collection_cards(collection_url)
        all_black_cards.extend(black_cards)
        all_white_cards.extend(white_cards)
        print(f"Found {len(black_cards)} black cards and {len(white_cards)} white cards")
    elif card_text:
        # Search for specific card
        print(f"🔍 Searching for card: {card_text}")
        found_cards = search_cah_cards(card_text)
        # Separate by card type
        for card in found_cards:
            if card.card_type == "Black":
                all_black_cards.append(card)
            else:
                all_white_cards.append(card)
        print(f"Found {len(found_cards)} matching cards")
    else:
        # Get cards based on mode and source
        if mode == 'cards':
            print(f"🔍 Getting {card_type} cards from {source}...")

            if source in ['database', 'all']:
                db_cards = get_cards_from_cah_database(card_type, num_cards)
                # Separate by card type
                for card in db_cards:
                    if card.card_type == "Black":
                        all_black_cards.append(card)
                    else:
                        all_white_cards.append(card)

            if source in ['community', 'all']:
                community_cards = get_cards_from_community_spreadsheet(card_type, num_cards)
                # Separate by card type
                for card in community_cards:
                    if card.card_type == "Black":
                        all_black_cards.append(card)
                    else:
                        all_white_cards.append(card)

        print(f"✅ Found {len(all_black_cards)} black cards and {len(all_white_cards)} white cards")

    if not all_black_cards and not all_white_cards:
        print("❌ No cards found. Exiting.")
        return

    # -----------------------------
    # Save Collection Data
    # -----------------------------
    print("\n💾 Saving collection data...")
    os.makedirs(os.path.dirname(save_collection), exist_ok=True)

    # Create collection from cards
    collection_name = f"CAH Collection ({len(all_black_cards)} black, {len(all_white_cards)} white cards)"
    collection = create_collection_from_cards(all_black_cards, all_white_cards, collection_name)
    save_collection_to_file(collection, save_collection)

    # -----------------------------
    # Image Fetching (Optional)
    # -----------------------------
    if fetch_images:
        print("\n🖼️  Fetching card images...")

        all_cards = all_black_cards + all_white_cards
        print(f"Found {len(all_cards)} cards")

        # Ask for confirmation for large downloads
        if len(all_cards) > 50:
            if not click.confirm(f"Download {len(all_cards)} card images?", default=False):
                print("Skipping image download.")
                return

        # Process cards in batches
        processed = process_cah_cards_batch(all_cards, output_dir)
        print(f"✅ Downloaded {processed} card images to {output_dir}")

    # -----------------------------
    # Completion Summary
    # -----------------------------
    print("\n🎉 CARDS AGAINST HUMANITY PLUGIN COMPLETE")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Mode: {mode}")
    print(f"   • Source: {source}")
    print(f"   • Black cards: {len(all_black_cards)}")
    print(f"   • White cards: {len(all_white_cards)}")
    print(f"   • Collection saved to: {save_collection}")

    if fetch_images:
        total_cards = len(all_black_cards) + len(all_white_cards)
        print(f"   • Card images downloaded: {processed}")
        print(f"   • Images saved to: {output_dir}")

    print("\n✅ Ready for card creation!")
    print("⚠️  Remember: CAH contains mature content!")
# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    main()
