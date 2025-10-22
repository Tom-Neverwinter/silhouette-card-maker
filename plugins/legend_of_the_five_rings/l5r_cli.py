# Legend of the Five Rings CCG CLI Module
# ========================================
# Command-line interface for Legend of the Five Rings CCG plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from l5r_api import (
    search_l5r_cards,
    process_l5r_cards_batch,
    get_character_cards,
    get_clan_cards,
    get_family_cards,
    get_honor_cards,
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
@click.option('--clan', '-l', default=None,
              type=click.Choice(['Crab', 'Crane', 'Dragon', 'Lion', 'Mantis', 'Phoenix', 'Scorpion', 'Unicorn']),
              help='Get all cards from a specific clan')
@click.option('--family', '-f', default=None,
              help='Get all cards from a specific family')
@click.option('--honor', '-h', default=None,
              type=click.Choice(['High', 'Medium', 'Low', 'Dishonor']),
              help='Get all cards with a specific honor level')
@click.option('--type', '-t', default=None,
              type=click.Choice(['Character', 'Province', 'Event', 'Item', 'Strategy', 'Personality', 'Holding']),
              help='Get all cards of a specific type')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-collection', '-d', default='game/decklist/l5r_collection.txt',
              help='File to save card collection')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from Legend of the Five Rings databases')
@click.option('--max-results', '-m', default=20,
              help='Maximum number of results to return')
def main(search, character, clan, family, honor, type, output_dir, save_collection, fetch_images, max_results):
    """
    Legend of the Five Rings CCG Plugin

    Search and fetch cards from the Legend of the Five Rings CCG.
    Features characters and clans from the fantasy world of Rokugan.

    Examples:
        # Search for specific cards
        python l5r_cli.py --search "Hida" --max-results 10

        # Get all cards for a character
        python l5r_cli.py --character "Doji" --fetch-images

        # Get all Crab Clan cards
        python l5r_cli.py --clan "Crab" --max-results 50

        # Search by family
        python l5r_cli.py --family "Hida" --max-results 25

        # Search by honor level
        python l5r_cli.py --honor "High" --max-results 30

        # Search by card type
        python l5r_cli.py --type "Character" --max-results 30
    """
    print("Legend of the Five Rings CCG Plugin")
    print("="*50)
    print("Honor is stronger than steel! Search for your favorite Rokugan characters!")

    all_cards = []

    # Handle different search types
    if search:
        print(f"🔍 Searching for: {search}")
        cards = search_l5r_cards(search)
        all_cards.extend(cards[:max_results])
        
    elif character:
        print(f"👤 Getting cards for character: {character}")
        cards = get_character_cards(character)
        all_cards.extend(cards[:max_results])
        
    elif clan:
        print(f"⚔️ Getting {clan} Clan cards")
        cards = get_clan_cards(clan)
        all_cards.extend(cards[:max_results])
        
    elif family:
        print(f"👨‍👩‍👧‍👦 Getting cards from family: {family}")
        cards = get_family_cards(family)
        all_cards.extend(cards[:max_results])
        
    elif honor:
        print(f"🎭 Getting {honor} honor cards")
        cards = get_honor_cards(honor)
        all_cards.extend(cards[:max_results])
        
    elif type:
        print(f"📜 Getting {type} cards")
        cards = get_card_type_cards(type)
        all_cards.extend(cards[:max_results])
        
    else:
        print("❌ Please specify a search term, character, clan, family, honor, or type")
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
        print(f"     Clan: {card.clan} | Type: {card.card_type}")
        if card.family:
            print(f"     Family: {card.family}")
        print(f"     Honor: {card.honor}")
        if card.force is not None and card.chi is not None:
            print(f"     Stats: Force {card.force}, Chi {card.chi}")
        print()

    # Save collection
    if save_collection:
        print(f"💾 Saving collection to: {save_collection}")
        os.makedirs(os.path.dirname(save_collection), exist_ok=True)
        
        with open(save_collection, 'w', encoding='utf-8') as f:
            f.write(f"Legend of the Five Rings CCG Collection\n")
            f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Cards: {len(all_cards)}\n")
            f.write("="*50 + "\n\n")
            
            for card in all_cards:
                f.write(f"Card: {card.name}\n")
                if card.character:
                    f.write(f"Character: {card.character}\n")
                f.write(f"Set: {card.set_code} | Number: {card.card_number}\n")
                f.write(f"Rarity: {card.rarity} | Type: {card.card_type}\n")
                f.write(f"Clan: {card.clan}")
                if card.family:
                    f.write(f" | Family: {card.family}")
                f.write(f"\n")
                f.write(f"Honor: {card.honor}")
                if card.force is not None and card.chi is not None:
                    f.write(f" | Stats: Force {card.force}, Chi {card.chi}")
                f.write(f"\n")
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
        processed = process_l5r_cards_batch(cards_list, output_dir)
        print(f"✅ Downloaded {processed} card images to {output_dir}")

    # Completion summary
    print(f"\n🎉 LEGEND OF THE FIVE RINGS PLUGIN COMPLETE")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Cards found: {len(all_cards)}")
    print(f"   • Collection saved to: {save_collection}")

    if fetch_images:
        print(f"   • Card images downloaded: {processed}")
        print(f"   • Images saved to: {output_dir}")

    print("\n✅ Ready for card creation!")
    print("May your honor never be questioned!")


# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    main()
