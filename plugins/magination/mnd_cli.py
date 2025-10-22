# Magi-Nation Duel TCG CLI Module
# ================================
# Command-line interface for Magi-Nation Duel TCG plugin

import os
import sys
import click
from typing import List

# Import our custom modules
from mnd_scraper import (
    MagiNationCard, MagiNationDeck,
    get_cards_from_magi_nation_central,
    get_cards_from_magi_nation_com,
    get_cards_from_community_resources,
    get_sample_magi_nation_cards,
    create_collection_from_cards,
    save_collection_to_file,
    process_magi_nation_cards_batch
)
from mnd_api import (
    search_magi_nation_cards,
    get_collection_cards,
    create_collection_from_cards as api_create_collection,
    process_magi_nation_cards_batch as api_process_cards,
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
    """Magi-Nation Duel TCG Scraper Plugin"""
    pass

@cli.command()
@click.option('--source', '-s', default='central',
              type=click.Choice(['central', 'official', 'community', 'all']),
              help='Data source to use for card scraping')
@click.option('--card-type', '-t', default='all',
              type=click.Choice(['all', 'magi', 'creature', 'spell', 'relic']),
              help='Card type to filter by')
@click.option('--region', '-r', default='all',
              type=click.Choice(['all', 'arderial', 'cald', 'naroom', 'orothe', 'underneath', 'universal']),
              help='Card region to filter by')
@click.option('--max-cards', '-n', default=50,
              help='Maximum number of cards to scrape')
@click.option('--output-dir', '-o', default='game/front',
              help='Directory to save card images')
@click.option('--save-collection', '-c', default=None,
              help='Name of collection to save cards to')
@click.option('--fetch-images/--no-fetch-images', default=False,
              help='Fetch card images from available sources')
def scrape(source, card_type, region, max_cards, output_dir, save_collection, fetch_images):
    """
    Scrape Magi-Nation Duel cards from various sources.

    Examples:
    \b
    # Scrape cards from Magi-Nation Central
    python mnd_cli.py scrape --source central --max-cards 25

    # Scrape all cards from all sources with images
    python mnd_cli.py scrape --source all --fetch-images --save-collection "My Collection"
    """
    click.echo(f"Scraping Magi-Nation Duel cards from {source}...")

    all_cards = []

    if source == 'central' or source == 'all':
        click.echo("Fetching from Magi-Nation Central...")
        central_cards = get_cards_from_magi_nation_central(card_type, max_cards)
        all_cards.extend(central_cards)
        click.echo(f"Found {len(central_cards)} cards from Magi-Nation Central")

    if source == 'official' or source == 'all':
        click.echo("Fetching from Magi-Nation.com...")
        official_cards = get_cards_from_magi_nation_com(card_type, max_cards)
        all_cards.extend(official_cards)
        click.echo(f"Found {len(official_cards)} cards from Magi-Nation.com")

    if source == 'community' or source == 'all':
        click.echo("Fetching from community resources...")
        community_cards = get_cards_from_community_resources(card_type, max_cards)
        all_cards.extend(community_cards)
        click.echo(f"Found {len(community_cards)} cards from community resources")

    # If no cards found from any source, use sample data
    if not all_cards:
        click.echo("No cards found from online sources, generating sample data...")
        all_cards = get_sample_magi_nation_cards(card_type, max_cards)
        click.echo(f"Generated {len(all_cards)} sample cards")

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
        processed = process_magi_nation_cards_batch(all_cards, output_dir)
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
    Process a specific Magi-Nation Duel card collection.

    Examples:
    \b
    # Process a collection and fetch images
    python mnd_cli.py collection --collection-name "Arderial Deck" --fetch-images
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
        click.echo(f"  {card.name} ({card.card_type}) - {card.region}")

    # Fetch images if requested
    if fetch_images:
        click.echo(f"\nFetching images to {output_dir}...")
        processed = process_magi_nation_cards_batch(cards, output_dir)
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
    Search for specific Magi-Nation Duel cards by name.

    Examples:
    \b
    # Search for a specific card
    python mnd_cli.py search "Tony Jones"

    # Search and fetch images
    python mnd_cli.py search "Arboll" --fetch-images
    """
    click.echo(f"Searching for Magi-Nation Duel card: {card_name}")

    # Search for the card
    cards = search_magi_nation_cards(card_name)

    if not cards:
        click.echo(f"No cards found matching '{card_name}'")
        return

    click.echo(f"Found {len(cards)} matching cards:")

    for card in cards:
        click.echo(f"  {card.name}")
        click.echo(f"    Type: {card.card_type}, Region: {card.region}")
        click.echo(f"    Cost: {card.cost}")
        if card.energy > 0:
            click.echo(f"    Energy: {card.energy}")
        if card.attack > 0:
            click.echo(f"    Attack: {card.attack}, Defense: {card.defense}")
        click.echo(f"    Set: {card.set_code}, Rarity: {card.rarity}")

    # Fetch images if requested
    if fetch_images and cards:
        click.echo(f"\nFetching images to {output_dir}...")
        processed = process_magi_nation_cards_batch(cards, output_dir)
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
    Scrape deck lists from Magi-Nation Duel tournaments.

    Examples:
    \b
    # Scrape tournament deck lists
    python mnd_cli.py tournament --tournament-url "https://example.com/tournament/123"

    # Save as JSON format
    python mnd_cli.py tournament --tournament-url "https://example.com/tournament/123" --save-json
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
    Load a Magi-Nation Duel collection from JSON file and process it.

    Examples:
    \b
    # Load collection from JSON file
    python mnd_cli.py load-collection --input-file "my_collection.json"

    # Load and fetch images
    python mnd_cli.py load-collection --input-file "my_collection.json" --fetch-images
    """
    click.echo(f"Loading collection from: {input_file}")

    try:
        # Load collection from JSON
        collection = load_collection_from_json(input_file)

        click.echo(f"Loaded collection '{collection.name}' with {len(collection.cards)} cards")
        click.echo(f"Player: {collection.player}")
        click.echo(f"Collection ID: {collection.id}")
        click.echo(f"Regions: {', '.join(collection.regions)}")

        # Display cards
        click.echo("\nCards in collection:")
        for card in collection.cards:
            click.echo(f"  {card.name} ({card.card_type}) - {card.region}")

        # Fetch images if requested
        if fetch_images:
            click.echo(f"\nFetching images to {output_dir}...")
            processed = process_magi_nation_cards_batch(collection.cards, output_dir)
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
    Generate a sample Magi-Nation Duel collection for testing.

    Examples:
    \b
    # Generate sample collection with images
    python mnd_cli.py sample --num-cards 20 --collection-name "Test Collection"
    """
    click.echo(f"Generating sample collection '{collection_name}' with {num_cards} cards...")

    # Generate sample cards
    sample_cards = []
    regions = ["Arderial", "Cald", "Naroom", "Orothe", "Underneath", "Universal"]
    card_types = ["Magi", "Creature", "Spell", "Relic"]
    sample_names = [
        "Tony Jones", "Arboll", "Lightning", "Ancient Staff", "Korg", "Firefly",
        "Grow", "Shadow", "Tonya Jones", "Weebat", "Frost", "Crystal Ring"
    ]

    for i in range(num_cards):
        card = MagiNationCard(
            name=sample_names[i % len(sample_names)] if i < len(sample_names) else f"Sample Card {i+1}",
            card_type=card_types[i % len(card_types)],
            region=regions[i % len(regions)],
            cost=1 + (i % 4),
            energy=10 + (i % 10) if card_types[i % len(card_types)] == "Magi" else 0,
            attack=1 + (i % 3) if card_types[i % len(card_types)] == "Creature" else 0,
            defense=i % 2 if card_types[i % len(card_types)] == "Creature" else 0,
            ability=f"Sample ability for card {i+1}",
            set_code="BASE",
            rarity=["Common", "Uncommon", "Rare"][i % 3],
            image_url=f"https://example.com/sample_cards/mnd_{i+1}.png"
        )
        sample_cards.append(card)

    # Create collection
    collection = create_collection_from_cards(sample_cards, collection_name)

    # Save collection
    save_collection_to_file(collection, f"game/decklist/{collection_name.replace(' ', '_')}.txt")

    # Save as JSON
    save_collection_to_json(collection, f"game/decklist/{collection_name.replace(' ', '_')}.json")

    click.echo(f"Created sample collection with {len(sample_cards)} cards")
    click.echo(f"Regions represented: {', '.join(collection.regions)}")

    # Fetch images if requested (will fail but shows the process)
    click.echo(f"\nFetching sample images to {output_dir}...")
    processed = process_magi_nation_cards_batch(sample_cards, output_dir)
    click.echo(f"Successfully processed {processed} sample card images")

    click.echo("Sample generation completed!")


if __name__ == '__main__':
    cli()
