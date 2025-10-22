# Universal CCG CLI Module for CCGTrader.net
# ==========================================
# Command-line interface for the universal CCG scraper

import os
import sys
import click
from typing import List

# Import our custom modules
from ccgt_scraper import (
    UniversalCard, UniversalGame, UniversalCollection,
    get_games_list,
    get_game_sets,
    get_set_cards,
    search_cards_across_games,
    create_multi_game_collection,
    save_universal_collection_to_file,
    process_universal_cards_batch
)
from ccgt_api import (
    search_universal_cards,
    get_game_cards,
    get_popular_games_cards,
    create_game_collection,
    create_multi_game_collection as api_create_multi_game,
    save_universal_collection_to_json,
    load_universal_collection_from_json,
    discover_available_games,
    get_cross_game_collection
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.group()
def cli():
    """Universal CCG Scraper for CCGTrader.net"""
    pass

@cli.command()
@click.option('--max-games', '-n', default=20,
              help='Maximum number of games to list')
@click.option('--popular-only/--all-games', default=True,
              help='Show only popular games or all available games')
def games(max_games, popular_only):
    """
    List available CCGs on CCGTrader.net.

    Examples:
    \b
    # List popular games
    python ccgt_cli.py games --popular-only

    # List all available games (up to limit)
    python ccgt_cli.py games --max-games 50 --popular-only=false
    """
    click.echo(f"Fetching games from CCGTrader.net...")

    if popular_only:
        games_list = discover_available_games()[:max_games]
        click.echo(f"Popular CCGs ({len(games_list)} shown):")
    else:
        games_list = get_games_list()[:max_games]
        click.echo(f"All available CCGs ({len(games_list)} shown):")

    for game in games_list:
        click.echo(f"  {game.name}")
        if game.description:
            click.echo(f"    {game.description[:100]}...")

    click.echo(f"\nTotal: {len(games_list)} games")


@cli.command()
@click.argument('game_name')
@click.option('--max-cards', '-n', default=20,
              help='Maximum number of cards to fetch')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-collection', '-c', default=None,
              help='Name of collection to save cards to')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images for the game')
def game(game_name, max_cards, output_dir, save_collection, fetch_images):
    """
    Get cards from a specific CCG.

    Examples:
    \b
    # Get cards from Magic: The Gathering
    python ccgt_cli.py game "Magic: The Gathering" --max-cards 50

    # Get cards and fetch images
    python ccgt_cli.py game "Pokémon" --fetch-images --save-collection "Pokemon Collection"
    """
    click.echo(f"Fetching cards for {game_name}...")

    # Get cards for the game
    cards = get_game_cards(game_name, max_cards)

    if not cards:
        click.echo(f"No cards found for {game_name}")
        return

    click.echo(f"Found {len(cards)} cards for {game_name}:")

    # Display cards grouped by set
    sets = {}
    for card in cards:
        if card.set_name not in sets:
            sets[card.set_name] = []
        sets[card.set_name].append(card)

    for set_name, set_cards in sets.items():
        click.echo(f"\n{set_name} ({len(set_cards)} cards):")
        for card in set_cards[:5]:  # Show first 5 cards per set
            click.echo(f"  {card.name}")
            click.echo(f"    Type: {card.card_type}, Rarity: {card.rarity}")
            if card.cost:
                click.echo(f"    Cost: {card.cost}")
            if card.attack or card.defense:
                click.echo(f"    Attack: {card.attack}, Defense: {card.defense}")

    # Save collection if specified
    if save_collection:
        collection = create_game_collection(game_name, save_collection)
        save_universal_collection_to_file(collection, f"game/decklist/{save_collection.replace(' ', '_')}.txt")
        click.echo(f"\nSaved collection '{save_collection}' with {len(cards)} cards")

    # Fetch images if requested
    if fetch_images:
        click.echo(f"\nFetching images to {output_dir}...")
        processed = process_universal_cards_batch(cards, output_dir)
        click.echo(f"Successfully processed {processed} card images")

    click.echo("\nGame scraping completed!")


@cli.command()
@click.argument('card_name')
@click.option('--games', '-g', multiple=True,
              help='Specific games to search in (can specify multiple)')
@click.option('--max-results', '-n', default=20,
              help='Maximum number of results to return')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-collection', '-c', default=None,
              help='Name of collection to save found cards to')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images for found cards')
def search(card_name, games, max_results, output_dir, save_collection, fetch_images):
    """
    Search for cards across multiple CCGs.

    Examples:
    \b
    # Search for cards named "Lightning" across all games
    python ccgt_cli.py search "Lightning"

    # Search in specific games only
    python ccgt_cli.py search "Dragon" --games "Magic: The Gathering" --games "Pokémon"

    # Search and save results
    python ccgt_cli.py search "Bolt" --save-collection "Bolt Collection" --fetch-images
    """
    click.echo(f"Searching for '{card_name}' across CCGs...")

    games_filter = list(games) if games else None

    # Search for cards
    cards = search_universal_cards(card_name, games_filter, max_results)

    if not cards:
        click.echo(f"No cards found matching '{card_name}'")
        return

    click.echo(f"Found {len(cards)} cards matching '{card_name}':")

    # Group cards by game
    cards_by_game = {}
    for card in cards:
        if card.game not in cards_by_game:
            cards_by_game[card.game] = []
        cards_by_game[card.game].append(card)

    for game, game_cards in cards_by_game.items():
        click.echo(f"\n{game} ({len(game_cards)} cards):")
        for card in game_cards:
            click.echo(f"  {card.name}")
            click.echo(f"    Set: {card.set_name}, Rarity: {card.rarity}")
            if card.card_type:
                click.echo(f"    Type: {card.card_type}")
            if card.cost:
                click.echo(f"    Cost: {card.cost}")

    # Save collection if specified
    if save_collection:
        collection = api_create_multi_game(card_name, save_collection, games_filter)
        save_universal_collection_to_file(collection, f"game/decklist/{save_collection.replace(' ', '_')}.txt")
        click.echo(f"\nSaved collection '{save_collection}' with {len(cards)} cards")

    # Fetch images if requested
    if fetch_images:
        click.echo(f"\nFetching images to {output_dir}...")
        processed = process_universal_cards_batch(cards, output_dir)
        click.echo(f"Successfully processed {processed} card images")

    click.echo("\nSearch completed!")


@cli.command()
@click.option('--input-file', '-i', required=True,
              help='JSON file to load collection from')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--fetch-images/--no-fetch-images', default=True,
              help='Fetch card images for loaded collection')
def load_collection(input_file, output_dir, fetch_images):
    """
    Load a universal CCG collection from JSON file.

    Examples:
    \b
    # Load collection from JSON file
    python ccgt_cli.py load-collection --input-file "my_collection.json"

    # Load and fetch images
    python ccgt_cli.py load-collection --input-file "my_collection.json" --fetch-images
    """
    click.echo(f"Loading collection from: {input_file}")

    try:
        # Load collection from JSON
        collection = load_universal_collection_from_json(input_file)

        click.echo(f"Loaded collection '{collection.name}' with {len(collection.cards)} cards")
        click.echo(f"Games: {', '.join(collection.games)}")

        # Display cards grouped by game
        cards_by_game = {}
        for card in collection.cards:
            if card.game not in cards_by_game:
                cards_by_game[card.game] = []
            cards_by_game[card.game].append(card)

        click.echo("\nCards in collection:")
        for game, cards in cards_by_game.items():
            click.echo(f"\n{game} ({len(cards)} cards):")
            for card in cards[:3]:  # Show first 3 cards per game
                click.echo(f"  {card.name} - {card.set_name}")

        # Fetch images if requested
        if fetch_images:
            click.echo(f"\nFetching images to {output_dir}...")
            processed = process_universal_cards_batch(collection.cards, output_dir)
            click.echo(f"Successfully processed {processed} card images")

        click.echo("Collection loading completed!")

    except FileNotFoundError:
        click.echo(f"Error: File '{input_file}' not found")
    except json.JSONDecodeError:
        click.echo(f"Error: Invalid JSON file '{input_file}'")
    except Exception as e:
        click.echo(f"Error loading collection: {e}")


@cli.command()
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--collection-name', '-c', default='Popular CCGs Collection',
              help='Name for the collection')
@click.option('--num-cards-per-game', '-n', default=10,
              help='Number of cards to get from each popular game')
def popular(output_dir, collection_name, num_cards_per_game):
    """
    Get cards from popular CCGs and create a mixed collection.

    Examples:
    \b
    # Get cards from popular games
    python ccgt_cli.py popular --num-cards-per-game 15 --collection-name "Popular Mix"
    """
    click.echo(f"Fetching cards from popular CCGs...")

    # Get cards from popular games
    games_cards = get_popular_games_cards()

    all_cards = []
    for game, cards in games_cards.items():
        click.echo(f"Found {len(cards)} cards for {game}")
        all_cards.extend(cards[:num_cards_per_game])

    click.echo(f"\nTotal cards collected: {len(all_cards)}")

    if all_cards:
        # Create collection
        collection = UniversalCollection(collection_name, all_cards)

        # Save collection
        save_universal_collection_to_file(collection, f"game/decklist/{collection_name.replace(' ', '_')}.txt")

        # Fetch images if requested
        click.echo(f"\nFetching images to {output_dir}...")
        processed = process_universal_cards_batch(all_cards, output_dir)
        click.echo(f"Successfully processed {processed} card images")

    click.echo("Popular games collection completed!")


@cli.command()
@click.argument('card_name')
@click.option('--collection-name', '-c', default=None,
              help='Name for the cross-game collection (defaults to card name)')
@click.option('--max-results', '-n', default=15,
              help='Maximum results per game')
def cross_game(card_name, collection_name, max_results):
    """
    Find similar cards across different CCGs.

    Examples:
    \b
    # Find lightning-type cards across games
    python ccgt_cli.py cross-game "Lightning"

    # Find dragon cards across games
    python ccgt_cli.py cross-game "Dragon" --collection-name "Dragon Collection"
    """
    collection_name = collection_name or f"{card_name} Variants"

    click.echo(f"Finding '{card_name}' variants across CCGs...")

    collection = get_cross_game_collection(card_name, collection_name)

    if not collection.cards:
        click.echo(f"No variants found for '{card_name}'")
        return

    click.echo(f"Found {len(collection.cards)} variants across {len(collection.games)} games:")

    # Group by game
    cards_by_game = {}
    for card in collection.cards:
        if card.game not in cards_by_game:
            cards_by_game[card.game] = []
        cards_by_game[card.game].append(card)

    for game, cards in cards_by_game.items():
        click.echo(f"\n{game}:")
        for card in cards:
            click.echo(f"  {card.name}")
            if card.card_type:
                click.echo(f"    Type: {card.card_type}")
            if card.description:
                click.echo(f"    {card.description[:50]}...")

    # Save collection
    save_universal_collection_to_file(collection, f"game/decklist/{collection_name.replace(' ', '_')}.txt")

    click.echo(f"\nSaved cross-game collection '{collection_name}'")
    click.echo("Cross-game search completed!")


@cli.command()
@click.option('--collection-name', '-c', default='Sample Universal Collection',
              help='Name for the sample collection')
@click.option('--num-games', '-n', default=3,
              help='Number of games to sample from')
@click.option('--cards-per-game', '-m', default=5,
              help='Number of cards per game')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images for sample cards')
def sample(collection_name, num_games, cards_per_game, output_dir, fetch_images):
    """
    Generate a sample collection from multiple CCGs for testing.

    Examples:
    \b
    # Generate sample collection
    python ccgt_cli.py sample --num-games 5 --cards-per-game 10

    # Generate and fetch images
    python ccgt_cli.py sample --collection-name "Test Collection" --fetch-images
    """
    click.echo(f"Generating sample collection '{collection_name}'...")

    # Get popular games
    games = discover_available_games()[:num_games]

    all_cards = []

    for game in games:
        click.echo(f"Generating {cards_per_game} cards for {game.name}...")
        cards = get_game_cards(game.name, cards_per_game)
        all_cards.extend(cards)

    if all_cards:
        # Create collection
        collection = UniversalCollection(collection_name, all_cards)

        # Save collection
        save_universal_collection_to_file(collection, f"game/decklist/{collection_name.replace(' ', '_')}.txt")

        click.echo(f"\nCreated sample collection with {len(all_cards)} cards from {len(games)} games")

        # Fetch images if requested
        if fetch_images:
            click.echo(f"\nFetching sample images to {output_dir}...")
            processed = process_universal_cards_batch(all_cards, output_dir)
            click.echo(f"Successfully processed {processed} card images")

    click.echo("Sample generation completed!")


if __name__ == '__main__':
    cli()
