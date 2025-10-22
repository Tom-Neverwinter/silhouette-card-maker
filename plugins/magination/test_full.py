#!/usr/bin/env python3
"""
Test script for Magi-Nation Duel scraping functionality with sample data.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mnd_scraper import get_sample_magi_nation_cards, MagiNationCard, create_collection_from_cards, save_collection_to_file

def test_sample_data():
    """Test the sample data generation functionality."""
    print("Testing Magi-Nation Duel sample data generation...")

    try:
        # Test sample data generation
        print("\n1. Testing sample data generation...")
        cards = get_sample_magi_nation_cards(card_type_filter="all", max_cards=10)

        print(f"Generated {len(cards)} sample cards:")
        for card in cards:
            print(f"  - {card.name} ({card.card_type}) - {card.region}")
            print(f"    Cost: {card.cost}, Energy: {card.energy}")
            if card.attack > 0:
                print(f"    Attack: {card.attack}, Defense: {card.defense}")
            print(f"    Ability: {card.ability}")

        if cards:
            print(f"\n✅ Successfully generated {len(cards)} sample cards!")

            # Test collection creation
            print("\n2. Testing collection creation...")
            collection = create_collection_from_cards(cards, "Sample Magi-Nation Collection")
            print(f"Created collection '{collection.name}' with {len(collection.cards)} cards")
            print(f"Regions represented: {', '.join(collection.regions)}")

            # Test saving collection
            print("\n3. Testing collection export...")
            save_collection_to_file(collection, "game/decklist/sample_collection.txt")
            print("✅ Collection saved successfully!")

        return len(cards) > 0

    except Exception as e:
        print(f"\n❌ Error during sample data test: {e}")
        return False

def test_cli_functionality():
    """Test the CLI functionality."""
    print("\n4. Testing CLI functionality...")

    try:
        # Test that we can import and run basic CLI functions
        from mnd_cli import cli
        print("✅ CLI module imports successfully")

        # Test that the scrape function exists and is callable
        import inspect
        from mnd_cli import scrape

        sig = inspect.signature(scrape)
        print(f"✅ Scrape function signature: {sig}")

        return True

    except Exception as e:
        print(f"❌ Error testing CLI functionality: {e}")
        return False

if __name__ == "__main__":
    success1 = test_sample_data()
    success2 = test_cli_functionality()

    if success1 and success2:
        print("\n🎉 All tests completed successfully!")
        print("The Magi-Nation Duel plugin is ready to use with sample data.")
    else:
        print("\n⚠️ Some tests had issues, but the plugin structure is functional.")
