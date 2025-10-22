#!/usr/bin/env python3
"""
Test script for Magi-Nation Duel scraping functionality.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mnd_scraper import get_cards_from_magi_nation_central, MagiNationCard

def test_scraping():
    """Test the scraping functionality."""
    print("Testing Magi-Nation Duel scraping...")

    try:
        # Test scraping from Magi-Nation Central
        print("\n1. Testing Magi-Nation Central scraping...")
        cards = get_cards_from_magi_nation_central(card_type_filter="all", max_cards=3)

        print(f"Found {len(cards)} cards:")
        for card in cards:
            print(f"  - {card.name} ({card.card_type}) - {card.region}")
            print(f"    Cost: {card.cost}, Energy: {card.energy}")
            if card.attack > 0:
                print(f"    Attack: {card.attack}, Defense: {card.defense}")
            print(f"    Ability: {card.ability}")

        if cards:
            print(f"\n✅ Successfully scraped {len(cards)} cards from Magi-Nation Central!")
        else:
            print("\n⚠️ No cards found from Magi-Nation Central")

        return len(cards) > 0

    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        return False

if __name__ == "__main__":
    success = test_scraping()
    if success:
        print("\n🎉 Scraping test completed successfully!")
    else:
        print("\n⚠️ Scraping test had issues, but plugin structure is ready.")
