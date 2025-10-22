# Middle Earth CCG CLI Module
# =============================
# Command-line interface for Middle Earth CCG plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from meccg_api import (
    search_meccg_cards,
    process_meccg_cards_batch,
    get_character_cards,
    get_faction_cards,
    get_region_cards,
    get_card_type_cards
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.command()
@click.option('--search', '-s', default=None,
              help='Search for cards by name or character')
@click.option('--character', '-c', default=None,
              help='Get all cards for a specific character')
@click.option('--faction', '-f', default=None,
              type=click.Choice(['Free Peoples', 'Shadow', 'Neutral']),
              help='Get all cards from a specific faction')
@click.option('--region', '-r', default=None,
              help='Get all cards from a specific region')
@click.option('--type', '-t', default=None,
              type=click.Choice(['Character', 'Location', 'Item', 'Event', 'Hazard', 'Resource']),
              help='Get all cards of a specific type')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-collection', '-d', default='game/decklist/meccg_collection.txt',
              help='File to save card collection')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from Middle Earth CCG databases')
@click.option('--max-results', '-m', default=20,
              help='Maximum number of results to return')
def main(search, character, faction, region, type, output_dir, save_collection, fetch_images, max_results):
    """
    Middle Earth CCG Plugin

    Search and fetch cards from the Middle Earth CCG.
    Features characters and locations from J.R.R. Tolkien's beloved works.

    Examples:
        # Search for specific cards
        python meccg_cli.py --search "Gandalf" --max-results 10

        # Get all cards for a character
        python meccg_cli.py --character "Aragorn" --fetch-images

        # Get all Free Peoples faction cards
        python meccg_cli.py --faction "Free Peoples" --max-results 50

        # Search by region
        python meccg_cli.py --region "Shire" --max-results 25

        # Search by card type
        python meccg_cli.py --type "Character" --max-results 30
    """
    print("Middle Earth CCG Plugin")
    print("="*50)
    print("One Ring to rule them all! Search for your favorite Middle Earth characters!")

    all_cards = []

    # Handle different search types
    if search:
        print(f"🔍 Searching for: {search}")
        cards = search_meccg_cards(search)
        all_cards.extend(cards[:max_results])
        
    elif character:
        print(f"👤 Getting cards for character: {character}")
        cards = get_character_cards(character)
        all_cards.extend(cards[:max_results])
        
    elif faction:
        print(f"⚔️ Getting {faction} faction cards")
        cards = get_faction_cards(faction)
        all_cards.extend(cards[:max_results])
        
    elif region:
        print(f"🗺️ Getting cards from region: {region}")
        cards = get_region_cards(region)
        all_cards.extend(cards[:max_results])
        
    elif type:
        print(f"📜 Getting {type} cards")
        cards = get_card_type_cards(type)
        all_cards.extend(cards[:max_results])
        
    else:
        print("❌ Please specify a search term, character, faction, region, or type")
        return

    print(f"\n📊 Found {len(all_cards)} cards")

    if not all_cards:
        print("❌ No cards found. Try a different search term.")
        return

    # Display results
    print(f"\n🎯 Results:")
    for i, card in enumerate(all_cards, 1):
        print(f"  {i}. {card.name}")
        if card.character:
            print(f"     Character: {card.character}")
        print(f"     Faction: {card.faction} | Type: {card.card_type}")
        if card.region:
            print(f"     Region: {card.region}")
        if card.mind is not None and card.body is not None:
            print(f"     Stats: Mind {card.mind}, Body {card.body}")
        if card.corruption > 0:
            print(f"     Corruption: {card.corruption}")
        print()

    # Save collection
    if save_collection:
        print(f"💾 Saving collection to: {save_collection}")
        os.makedirs(os.path.dirname(save_collection), exist_ok=True)
        
        with open(save_collection, 'w', encoding='utf-8') as f:
            f.write(f"Middle Earth CCG Collection\n")
            f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Cards: {len(all_cards)}\n")
            f.write("="*50 + "\n\n")
            
            for card in all_cards:
                f.write(f"Card: {card.name}\n")
                if card.character:
                    f.write(f"Character: {card.character}\n")
                f.write(f"Set: {card.set_code} | Number: {card.card_number}\n")
                f.write(f"Rarity: {card.rarity} | Type: {card.card_type}\n")
                f.write(f"Faction: {card.faction}")
                if card.region:
                    f.write(f" | Region: {card.region}")
                f.write(f"\n")
                if card.mind is not None and card.body is not None:
                    f.write(f"Stats: Mind {card.mind}, Body {card.body}\n")
                if card.corruption > 0:
                    f.write(f"Corruption: {card.corruption}\n")
                if card.description:
                    f.write(f"Description: {card.description}\n")
                f.write("\n" + "-"*30 + "\n\n")

    # Fetch images if requested
    if fetch_images:
        print(f"\n🖼️  Fetching card images...")
        
        # Convert cards to batch format
        cards_list = [(1, card.name) for card in all_cards]
        
        # Ask for confirmation for large downloads
        if len(cards_list) > 20:
            if not click.confirm(f"Download {len(cards_list)} card images?", default=False):
                print("Skipping image download.")
                return

        # Process cards in batches
        processed = process_meccg_cards_batch(cards_list, output_dir)
        print(f"✅ Downloaded {processed} card images to {output_dir}")

    # Completion summary
    print(f"\n🎉 MIDDLE EARTH CCG PLUGIN COMPLETE")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Cards found: {len(all_cards)}")
    print(f"   • Collection saved to: {save_collection}")

    if fetch_images:
        print(f"   • Card images downloaded: {processed}")
        print(f"   • Images saved to: {output_dir}")

    print("\n✅ Ready for card creation!")
    print("May the Fellowship be with you!")


# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    main()
