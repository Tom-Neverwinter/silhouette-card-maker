# Star Realms TCG CLI Module
# ============================
# Command-line interface for Star Realms TCG plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from sr_scraper import (
    StarRealmsCard, StarRealmsDeck,
    get_cards_from_official_gallery,
    get_cards_from_boardgamegeek,
    get_cards_from_tier_list,
    create_collection_from_cards,
    save_collection_to_file,
    process_starrealms_cards_batch
)
from sr_api import (
    search_starrealms_cards,
    get_collection_cards,
    create_collection_from_cards as api_create_collection,
    process_starrealms_cards_batch as api_process_cards,
    fetch_card_image,
    save_collection_to_json,
    load_collection_from_json,
    get_tournament_decks
)

# -----------------------------
# Command Line Interface
# -----------------------------
@click.group()
def cli():
    """Star Realms TCG Scraper Plugin"""
    pass

@cli.command()
@click.option('--source', '-s', default='official',
              type=click.Choice(['official', 'boardgamegeek', 'tierlist', 'all']),
              help='Data source to use for card scraping')
@click.option('--card-type', '-t', default='all',
              type=click.Choice(['all', 'ship', 'base', 'outpost']),
              help='Card type to filter by')
@click.option('--max-cards', '-n', default=50,
              help='Maximum number of cards to scrape')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-collection', '-c', default=None,
              help='Name of collection to save cards to')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from available sources')
def scrape(source, card_type, max_cards, output_dir, save_collection, fetch_images):
    """
    Scrape Star Realms cards from various sources.

    Examples:
    \b
    # Scrape cards from official gallery
    python sr_cli.py scrape --source official --max-cards 25

    # Scrape all cards from all sources with images
    python sr_cli.py scrape --source all --fetch-images --save-collection "My Collection"
    """
    click.echo(f"Scraping Star Realms cards from {source}...")

    all_cards = []

    if source == 'official' or source == 'all':
        click.echo("Fetching from official card gallery...")
        official_cards = get_cards_from_official_gallery(card_type, max_cards)
        all_cards.extend(official_cards)
        click.echo(f"Found {len(official_cards)} cards from official gallery")

    if source == 'boardgamegeek' or source == 'all':
        click.echo("Fetching from BoardGameGeek...")
        bgg_cards = get_cards_from_boardgamegeek(card_type, max_cards)
        all_cards.extend(bgg_cards)
        click.echo(f"Found {len(bgg_cards)} cards from BoardGameGeek")

    if source == 'tierlist' or source == 'all':
        click.echo("Fetching from tier lists...")
        tier_cards = get_cards_from_tier_list(card_type, max_cards)
        all_cards.extend(tier_cards)
        click.echo(f"Found {len(tier_cards)} cards from tier lists")

    if not all_cards:
        click.echo("No cards found from any source.")
        return

    click.echo(f"\nTotal cards scraped: {len(all_cards)}")

    # Save collection if specified
    if save_collection:
        collection = create_collection_from_cards(all_cards, save_collection)
        save_collection_to_file(collection, f"game/decklist/{save_collection.replace(' ', '_')}.txt")
        click.echo(f"Saved collection '{save_collection}' with {len(all_cards)} cards")

    # Fetch images if requested
    if fetch_images:
        click.echo(f"\nFetching images to {output_dir}...")
        processed = process_starrealms_cards_batch(all_cards, output_dir)
        click.echo(f"Successfully processed {processed} card images")

    click.echo("Scraping completed!")


@cli.command()
@click.option('--collection-name', '-c', required=True,
              help='Name of the collection to fetch cards for')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--fetch-images/--no-fetch-images', default=True,
              help='Fetch card images for the collection')
def collection(collection_name, output_dir, fetch_images):
    """
    Process a specific Star Realms card collection.

    Examples:
    \b
    # Process a collection and fetch images
    python sr_cli.py collection --collection-name "Competitive Deck" --fetch-images
    """
    click.echo(f"Processing collection: {collection_name}")

    # Get cards for the collection
    cards = get_collection_cards(collection_name)

    if not cards:
        click.echo(f"No cards found for collection '{collection_name}'")
        return

    click.echo(f"Found {len(cards)} cards in collection '{collection_name}'")

    # Display collection info
    for card in cards:
        click.echo(f"  {card.name} ({card.card_type}) - {card.faction}")

    # Fetch images if requested
    if fetch_images:
        click.echo(f"\nFetching images to {output_dir}...")
        processed = process_starrealms_cards_batch(cards, output_dir)
        click.echo(f"Successfully processed {processed} card images")

    click.echo("Collection processing completed!")


@cli.command()
@click.argument('card_name')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--fetch-images/--no-fetch-images', default=True,
              help='Fetch card images for found cards')
def search(card_name, output_dir, fetch_images):
    """
    Search for specific Star Realms cards by name.

    Examples:
    \b
    # Search for a specific card
    python sr_cli.py search "Trade Pod"

    # Search and fetch images
    python sr_cli.py search "Cutter" --fetch-images
    """
    click.echo(f"Searching for Star Realms card: {card_name}")

    # Search for the card
    cards = search_starrealms_cards(card_name)

    if not cards:
        click.echo(f"No cards found matching '{card_name}'")
        return

    click.echo(f"Found {len(cards)} matching cards:")

    for card in cards:
        click.echo(f"  {card.name}")
        click.echo(f"    Type: {card.card_type}, Faction: {card.faction}")
        click.echo(f"    Cost: {card.cost}, Attack: {card.attack}, Defense: {card.defense}")
        click.echo(f"    Set: {card.set_code}, Rarity: {card.rarity}")

    # Fetch images if requested
    if fetch_images and cards:
        click.echo(f"\nFetching images to {output_dir}...")
        processed = process_starrealms_cards_batch(cards, output_dir)
        click.echo(f"Successfully processed {processed} card images")

    click.echo("Search completed!")


@cli.command()
@click.option('--tournament-url', '-t', required=True,
              help='URL of the tournament page to scrape')
@click.option('--output-dir', '-o', default='game/decklist',
              help='Directory to save tournament deck files')
@click.option('--save-json/--no-save-json', default=False,
              help='Save deck data as JSON files')
def tournament(tournament_url, output_dir, save_json):
    """
    Scrape deck lists from Star Realms tournaments.

    Examples:
    \b
    # Scrape tournament deck lists
    python sr_cli.py tournament --tournament-url "https://example.com/tournament/123"

    # Save as JSON format
    python sr_cli.py tournament --tournament-url "https://example.com/tournament/123" --save-json
    """
    click.echo(f"Scraping tournament from: {tournament_url}")

    # Get tournament decks
    decks = get_tournament_decks(tournament_url)

    if not decks:
        click.echo("No decks found in tournament.")
        return

    click.echo(f"Found {len(decks)} decks in tournament:")

    for deck in decks:
        click.echo(f"  {deck.name} - {len(deck.cards)} cards")

        if save_json:
            # Save each deck as JSON
            filename = f"{output_dir}/{deck.name.replace(' ', '_')}_{deck.id}.json"
            save_collection_to_json(deck, filename)

    click.echo("Tournament scraping completed!")


@cli.command()
@click.option('--input-file', '-i', required=True,
              help='JSON file to load collection from')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--fetch-images/--no-fetch-images', default=True,
              help='Fetch card images for loaded collection')
def load_collection(input_file, output_dir, fetch_images):
    """
    Load a Star Realms collection from JSON file and process it.

    Examples:
    \b
    # Load collection from JSON file
    python sr_cli.py load-collection --input-file "my_collection.json"

    # Load and fetch images
    python sr_cli.py load-collection --input-file "my_collection.json" --fetch-images
    """
    click.echo(f"Loading collection from: {input_file}")

    try:
        # Load collection from JSON
        collection = load_collection_from_json(input_file)

        click.echo(f"Loaded collection '{collection.name}' with {len(collection.cards)} cards")
        click.echo(f"Player: {collection.player}")
        click.echo(f"Collection ID: {collection.id}")

        # Display cards
        click.echo("\nCards in collection:")
        for card in collection.cards:
            click.echo(f"  {card.name} ({card.card_type}) - {card.faction}")

        # Fetch images if requested
        if fetch_images:
            click.echo(f"\nFetching images to {output_dir}...")
            processed = process_starrealms_cards_batch(collection.cards, output_dir)
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
@click.option('--collection-name', '-c', default='Sample Collection',
              help='Name for the sample collection')
@click.option('--num-cards', '-n', default=10,
              help='Number of sample cards to generate')
def sample(output_dir, collection_name, num_cards):
    """
    Generate a sample Star Realms collection for testing.

    Examples:
    \b
    # Generate sample collection with images
    python sr_cli.py sample --num-cards 20 --collection-name "Test Collection"
    """
    click.echo(f"Generating sample collection '{collection_name}' with {num_cards} cards...")

    # Generate sample cards
    sample_cards = []
    factions = ["Trade Federation", "Blob", "Star Empire", "Machine Cult"]
    card_types = ["Ship", "Base", "Outpost"]

    for i in range(num_cards):
        card = StarRealmsCard(
            name=f"Sample Card {i+1}",
            card_type=card_types[i % len(card_types)],
            faction=factions[i % len(factions)],
            cost=2 + (i % 4),
            attack=1 + (i % 3),
            defense=i % 2,
            ability=f"Sample ability for card {i+1}",
            set_code="CORE",
            rarity="Common",
            image_url=f"https://example.com/sample_cards/card_{i+1}.png"
        )
        sample_cards.append(card)

    # Create collection
    collection = create_collection_from_cards(sample_cards, collection_name)

    # Save collection
    save_collection_to_file(collection, f"game/decklist/{collection_name.replace(' ', '_')}.txt")

    # Save as JSON
    save_collection_to_json(collection, f"game/decklist/{collection_name.replace(' ', '_')}.json")

    click.echo(f"Created sample collection with {len(sample_cards)} cards")

    # Fetch images if requested (will fail but shows the process)
    click.echo(f"\nFetching sample images to {output_dir}...")
    processed = process_starrealms_cards_batch(sample_cards, output_dir)
    click.echo(f"Successfully processed {processed} sample card images")

    click.echo("Sample generation completed!")


if __name__ == '__main__':
    cli()
