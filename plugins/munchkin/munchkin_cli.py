# Munchkin CLI Module
# ===================
# Command-line interface for Munchkin plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from munchkin_scraper import (
    MunchkinCard, MunchkinDeck,
    get_cards_from_munchkin_ccg,
    get_cards_from_fandom_wiki,
    create_collection_from_cards,
    save_collection_to_file
)
from munchkin_api import (
    process_munchkin_cards_batch,
    get_collection_cards,
    search_munchkin_cards
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.command()
@click.option('--mode', '-m', default='cards',
              type=click.Choice(['cards', 'collection', 'search']),
              help='What to fetch: cards, collection, or search')
@click.option('--source', '-s', default='ccg',
              type=click.Choice(['ccg', 'fandom', 'collection', 'all']),
              help='Data source to use')
@click.option('--card-type', '-t', default='all',
              type=click.Choice(['all', 'door', 'treasure']),
              help='Card type to filter by')
@click.option('--num-cards', '-n', default=20,
              help='Number of cards to fetch')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-collection', '-c', default='game/decklist/munchkin_collection.txt',
              help='File to save card collection')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from Munchkin databases')
@click.option('--card-name', default=None,
              help='Specific card name to search for')
@click.option('--collection-url', default=None,
              help='Specific collection URL to process')
def main(mode, source, card_type, num_cards, output_dir, save_collection, fetch_images, card_name, collection_url):
    """
    Munchkin Scraper Plugin

    Processes Munchkin card collections and data from various sources.
    Note: Munchkin is a humorous dungeon-crawling card game, not a competitive TCG.

    Examples:
        # Get cards from Munchkin CCG database
        python munchkin_cli.py --source ccg --card-type door --num-cards 10

        # Fetch images for card collection
        python munchkin_cli.py --mode collection --fetch-images

        # Search for specific card
        python munchkin_cli.py --card-name "Potion of General Studliness"
    """
    print("Munchkin Scraper Plugin")
    print("="*50)
    print("Humorous dungeon-crawling card game by Steve Jackson Games!")

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
        found_cards = search_munchkin_cards(card_name)
        all_cards.extend(found_cards)
        print(f"Found {len(found_cards)} matching cards")
    else:
        # Get cards based on mode and source
        if mode == 'cards':
            print(f"🔍 Getting {card_type} cards from {source}...")

            if source in ['ccg', 'all']:
                ccg_cards = get_cards_from_munchkin_ccg(card_type, num_cards)
                all_cards.extend(ccg_cards)

            if source in ['fandom', 'all']:
                fandom_cards = get_cards_from_fandom_wiki(card_type, num_cards)
                all_cards.extend(fandom_cards)

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
    collection_name = f"Munchkin Collection ({len(all_cards)} cards)"
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
        processed = process_munchkin_cards_batch(all_cards, output_dir)
        print(f"✅ Downloaded {processed} card images to {output_dir}")

    # -----------------------------
    # Completion Summary
    # -----------------------------
    print("\n🎉 MUNCHKIN PLUGIN COMPLETE")
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
    print("Kick down the door and grab the loot!")
# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    main()
