# Fluxx CLI Module
# ================
# Command-line interface for Fluxx plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from fluxx_scraper import (
    FluxxCard, FluxxDeck,
    get_cards_from_looney_labs,
    get_cards_from_boardgamegeek,
    create_collection_from_cards,
    save_collection_to_file
)
from fluxx_api import (
    process_fluxx_cards_batch,
    get_collection_cards,
    search_fluxx_cards
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.command()
@click.option('--mode', '-m', default='cards',
              type=click.Choice(['cards', 'collection', 'search']),
              help='What to fetch: cards, collection, or search')
@click.option('--source', '-s', default='looney',
              type=click.Choice(['looney', 'boardgamegeek', 'all']),
              help='Data source to use')
@click.option('--card-type', '-t', default='all',
              type=click.Choice(['all', 'keeper', 'goal', 'action', 'rule', 'creeper']),
              help='Card type to filter by')
@click.option('--num-cards', '-n', default=20,
              help='Number of cards to fetch')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-collection', '-c', default='game/decklist/fluxx_collection.txt',
              help='File to save card collection')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from Fluxx databases')
@click.option('--card-name', default=None,
              help='Specific card name to search for')
@click.option('--collection-url', default=None,
              help='Specific collection URL to process')
def main(mode, source, card_type, num_cards, output_dir, save_collection, fetch_images, card_name, collection_url):
    """
    Fluxx Scraper Plugin

    Processes Fluxx card collections and data from various sources.
    Note: Fluxx is a rule-changing card game where win conditions constantly change.

    Examples:
        # Get cards from Looney Labs
        python fluxx_cli.py --source looney --card-type keeper --num-cards 10

        # Fetch images for card collection
        python fluxx_cli.py --mode collection --fetch-images

        # Search for specific card
        python fluxx_cli.py --card-name "The Brain"
    """
    print("Fluxx Scraper Plugin")
    print("="*50)
    print("The card game where the rules keep changing!")

    all_cards = []

    if collection_url:
        # Process specific collection
        print(f"🔍 Processing collection: {collection_url}")
        collection_cards = get_collection_cards(collection_url)
        all_cards.extend(collection_cards)
        print(f"Found {len(collection_cards)} cards")
    elif card_name:
        # Search for specific card
        print(f"🔍 Searching for card: {card_name}")
        found_cards = search_fluxx_cards(card_name)
        all_cards.extend(found_cards)
        print(f"Found {len(found_cards)} matching cards")
    else:
        # Get cards based on mode and source
        if mode == 'cards':
            print(f"🔍 Getting {card_type} cards from {source}...")

            if source in ['looney', 'all']:
                looney_cards = get_cards_from_looney_labs(card_type, num_cards)
                all_cards.extend(looney_cards)

            if source in ['boardgamegeek', 'all']:
                bgg_cards = get_cards_from_boardgamegeek(card_type, num_cards)
                all_cards.extend(bgg_cards)

        print(f"✅ Found {len(all_cards)} cards")

    if not all_cards:
        print("❌ No cards found. Exiting.")
        return

    # -----------------------------
    # Save Collection Data
    # -----------------------------
    print("\n💾 Saving collection data...")
    os.makedirs(os.path.dirname(save_collection), exist_ok=True)

    # Create collection from cards
    collection_name = f"Fluxx Collection ({len(all_cards)} cards)"
    collection = create_collection_from_cards(all_cards, collection_name)
    save_collection_to_file(collection, save_collection)

    # -----------------------------
    # Image Fetching (Optional)
    # -----------------------------
    if fetch_images:
        print("\n🖼️  Fetching card images...")

        print(f"Found {len(all_cards)} cards")

        # Ask for confirmation for large downloads
        if len(all_cards) > 50:
            if not click.confirm(f"Download {len(all_cards)} card images?", default=False):
                print("Skipping image download.")
                return

        # Process cards in batches
        processed = process_fluxx_cards_batch(all_cards, output_dir)
        print(f"✅ Downloaded {processed} card images to {output_dir}")

    # -----------------------------
    # Completion Summary
    # -----------------------------
    print("\n🎉 FLUXX PLUGIN COMPLETE")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Mode: {mode}")
    print(f"   • Source: {source}")
    print(f"   • Cards processed: {len(all_cards)}")
    print(f"   • Collection saved to: {save_collection}")

    if fetch_images:
        print(f"   • Card images downloaded: {processed}")
        print(f"   • Images saved to: {output_dir}")

    print("\n✅ Ready for card creation!")
    print("The rules will keep changing!")
# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    main()
