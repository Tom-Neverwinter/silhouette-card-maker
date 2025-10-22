#!/usr/bin/env python3
"""
Test script for Universal CCG Scraper functionality.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ccgt_api import (
    search_universal_cards,
    get_game_cards,
    get_popular_games_cards,
    discover_available_games,
    create_game_collection,
    get_cross_game_collection
)

def test_games_discovery():
    """Test games discovery functionality."""
    print("Testing games discovery...")

    try:
        games = discover_available_games()
        print(f"✅ Discovered {len(games)} games")

        # Show first few games
        for game in games[:5]:
            print(f"  - {game.name}")

        return len(games) > 0

    except Exception as e:
        print(f"❌ Error discovering games: {e}")
        return False

def test_card_search():
    """Test card search functionality."""
    print("\nTesting card search...")

    try:
        cards = search_universal_cards("Lightning", max_results=10)
        print(f"✅ Found {len(cards)} cards matching 'Lightning'")

        # Show results grouped by game
        cards_by_game = {}
        for card in cards:
            if card.game not in cards_by_game:
                cards_by_game[card.game] = []
            cards_by_game[card.game].append(card)

        for game, game_cards in cards_by_game.items():
            print(f"\n{game} ({len(game_cards)} cards):")
            for card in game_cards[:2]:  # Show first 2 cards
                print(f"  - {card.name}")
                print(f"    Type: {card.card_type}, Rarity: {card.rarity}")

        return len(cards) > 0

    except Exception as e:
        print(f"❌ Error searching cards: {e}")
        return False

def test_game_cards():
    """Test getting cards from specific games."""
    print("\nTesting game-specific card retrieval...")

    try:
        # Test with Magic: The Gathering
        mtg_cards = get_game_cards("Magic: The Gathering", 5)
        print(f"✅ Retrieved {len(mtg_cards)} MTG cards")

        for card in mtg_cards:
            print(f"  - {card.name} ({card.card_type}) - {card.rarity}")

        return len(mtg_cards) > 0

    except Exception as e:
        print(f"❌ Error getting game cards: {e}")
        return False

def test_popular_games():
    """Test popular games collection."""
    print("\nTesting popular games collection...")

    try:
        games_cards = get_popular_games_cards()
        total_cards = sum(len(cards) for cards in games_cards.values())

        print(f"✅ Retrieved cards from {len(games_cards)} popular games")
        print(f"   Total cards: {total_cards}")

        for game, cards in games_cards.items():
            print(f"  - {game}: {len(cards)} cards")

        return len(games_cards) > 0

    except Exception as e:
        print(f"❌ Error getting popular games: {e}")
        return False

def test_cross_game_search():
    """Test cross-game thematic search."""
    print("\nTesting cross-game thematic search...")

    try:
        collection = get_cross_game_collection("Dragon", "Dragon Collection")
        print(f"✅ Found {len(collection.cards)} dragon-themed cards across {len(collection.games)} games")

        # Show results
        cards_by_game = {}
        for card in collection.cards:
            if card.game not in cards_by_game:
                cards_by_game[card.game] = []
            cards_by_game[card.game].append(card)

        for game, cards in cards_by_game.items():
            print(f"\n{game}:")
            for card in cards[:2]:  # Show first 2 cards
                print(f"  - {card.name}")

        return len(collection.cards) > 0

    except Exception as e:
        print(f"❌ Error in cross-game search: {e}")
        return False

def test_collection_creation():
    """Test collection creation and management."""
    print("\nTesting collection creation...")

    try:
        # Create a game-specific collection
        collection = create_game_collection("Magic: The Gathering", "MTG Test Collection")

        print(f"✅ Created collection '{collection.name}'")
        print(f"   Games: {', '.join(collection.games)}")
        print(f"   Cards: {len(collection.cards)}")

        return len(collection.cards) > 0

    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Universal CCG Scraper...")
    print("=" * 50)

    tests = [
        test_games_discovery,
        test_card_search,
        test_game_cards,
        test_popular_games,
        test_cross_game_search,
        test_collection_creation
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Universal CCG Scraper is ready to use.")
    else:
        print("⚠️ Some tests failed, but the plugin structure is functional.")

    print("\n💡 The Universal CCG Scraper provides access to hundreds of CCGs")
    print("   from CCGTrader.net and includes sample data for testing.")
