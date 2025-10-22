# Magi-Nation Duel Scraper Module
# ================================
# This module handles web scraping of Magi-Nation Duel cards and data

import os
import sys
import requests
import hashlib
import json
from pathlib import Path
from lxml import html
from typing import List, Dict, Optional

# -----------------------------
# Data Models
# -----------------------------
class MagiNationCard:
    """
    Represents a Magi-Nation Duel card with all relevant data.

    Attributes:
        name: Card name
        card_type: Type of card (Magi, Creature, Spell, Relic)
        region: Card region (Arderial, Cald, Naroom, Orothe, Underneath, Universal)
        cost: Energy cost to play
        energy: Energy value (for Magi)
        attack: Combat attack value (for Creatures)
        defense: Defense value
        ability: Special ability text
        set_code: Set identifier
        rarity: Card rarity
        image_url: URL to card image
        magi_name: Associated Magi name (for Creatures/Spells)
    """
    def __init__(self, name, card_type, region, cost, energy, attack, defense, ability, set_code, rarity, image_url, magi_name=None):
        self.name = name
        self.card_type = card_type
        self.region = region
        self.cost = cost
        self.energy = energy
        self.attack = attack
        self.defense = defense
        self.ability = ability
        self.set_code = set_code
        self.rarity = rarity
        self.image_url = image_url
        self.magi_name = magi_name


class MagiNationDeck:
    """
    Represents a Magi-Nation Duel deck/collection.

    Attributes:
        name: Deck/collection name
        cards: List of MagiNationCard objects
        player: Player who owns this collection
        id: Unique deck identifier
        hash: Unique hash based on card composition
        regions: List of regions represented in the deck
    """
    def __init__(self, name, cards, player, id):
        self.name = name
        self.cards = cards  # List of MagiNationCard objects
        self.player = player
        self.id = id
        self.hash = self._generate_hash()
        self.regions = self._get_regions()

    def _generate_hash(self):
        """
        Generate unique hash for deck based on card list.

        Returns:
            MD5 hash string of sorted card list
        """
        card_string = ''.join([f"{card.name}" for card in sorted(self.cards, key=lambda x: x.name)])
        return hashlib.md5(card_string.encode()).hexdigest()

    def _get_regions(self):
        """
        Get list of unique regions in the deck.

        Returns:
            List of region names
        """
        regions = set()
        for card in self.cards:
            regions.add(card.region)
        return sorted(list(regions))


# -----------------------------
# Card Database Functions
# -----------------------------
def get_cards_from_magi_nation_central(card_type_filter="all", max_cards=50):
    """
    Scrape Magi-Nation Duel cards from Magi-Nation Central wiki.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of MagiNationCard objects
    """
    print("Fetching Magi-Nation Duel cards from Magi-Nation Central...")

    try:
        # Magi-Nation Central card database
        url = 'https://maginationcentral.com/wiki/index.php/Category:Cards'
        page = requests.get(url, timeout=10)
        tree = html.fromstring(page.content)

        cards = []

        # Parse card listings from the category page
        # Look for card links in the category listing
        card_links = tree.xpath('//div[@id="mw-pages"]//a[@title]')

        for link in card_links[:max_cards]:
            card_name = link.text_content().strip()
            card_url = link.get('href')

            if card_name and card_url:
                # Extract card info by parsing the individual card page
                card = _parse_card_from_central_page(card_name, card_url)
                if card:
                    # Apply filters
                    if card_type_filter == "all" or card.card_type.lower() == card_type_filter.lower():
                        cards.append(card)

        return cards

    except requests.exceptions.RequestException as e:
        print(f"Error scraping Magi-Nation Central (site may be unavailable): {e}")
        return []
    except Exception as e:
        print(f"Error scraping Magi-Nation Central: {e}")
        return []


def _parse_card_from_central_page(card_name: str, card_url: str) -> Optional[MagiNationCard]:
    """
    Parse individual card data from Magi-Nation Central wiki page.

    Args:
        card_name: Name of the card
        card_url: URL to the card's wiki page

    Returns:
        MagiNationCard object or None if parsing fails
    """
    try:
        full_url = f"https://maginationcentral.com{card_url}" if not card_url.startswith('http') else card_url
        page = requests.get(full_url)
        tree = html.fromstring(page.content)

        # Extract card information from the wiki page
        # Look for infobox or card data table
        infobox = tree.xpath('//table[contains(@class, "infobox")] | //div[contains(@class, "card-infobox")]')

        if not infobox:
            return None

        info = infobox[0]

        # Extract basic card info
        card_type = "Creature"  # Default
        region = "Universal"    # Default
        cost = 0
        energy = 0
        attack = 0
        defense = 0
        ability = "No ability text available"
        set_code = "BASE"
        rarity = "Common"

        # Parse card type
        type_elem = info.xpath('.//tr[th/text()="Type"]/td/text() | .//td[contains(text(), "Type")]/following-sibling::td/text()')
        if type_elem:
            card_type = type_elem[0].strip()

        # Parse region
        region_elem = info.xpath('.//tr[th/text()="Region"]/td/text() | .//td[contains(text(), "Region")]/following-sibling::td/text()')
        if region_elem:
            region = region_elem[0].strip()

        # Parse cost (energy cost to play)
        cost_elem = info.xpath('.//tr[th/text()="Cost"]/td/text() | .//td[contains(text(), "Cost")]/following-sibling::td/text()')
        if cost_elem:
            try:
                cost = int(cost_elem[0].strip())
            except:
                cost = 0

        # Parse energy (for Magi)
        energy_elem = info.xpath('.//tr[th/text()="Energy"]/td/text() | .//td[contains(text(), "Energy")]/following-sibling::td/text()')
        if energy_elem:
            try:
                energy = int(energy_elem[0].strip())
            except:
                energy = 0

        # Parse attack (for Creatures)
        attack_elem = info.xpath('.//tr[th/text()="Attack"]/td/text() | .//td[contains(text(), "Attack")]/following-sibling::td/text()')
        if attack_elem:
            try:
                attack = int(attack_elem[0].strip())
            except:
                attack = 0

        # Parse defense (for Creatures)
        defense_elem = info.xpath('.//tr[th/text()="Defense"]/td/text() | .//td[contains(text(), "Defense")]/following-sibling::td/text()')
        if defense_elem:
            try:
                defense = int(defense_elem[0].strip())
            except:
                defense = 0

        # Parse ability text
        ability_elem = info.xpath('.//tr[th/text()="Text"]/td/text() | .//td[contains(text(), "Text")]/following-sibling::td/text()')
        if ability_elem:
            ability = ability_elem[0].strip()

        # Parse set/rarity info
        set_elem = info.xpath('.//tr[th/text()="Set"]/td/text() | .//td[contains(text(), "Set")]/following-sibling::td/text()')
        if set_elem:
            set_code = set_elem[0].strip()

        rarity_elem = info.xpath('.//tr[th/text()="Rarity"]/td/text() | .//td[contains(text(), "Rarity")]/following-sibling::td/text()')
        if rarity_elem:
            rarity = rarity_elem[0].strip()

        # Generate image URL (would need actual image hosting)
        image_url = f"https://maginationcentral.com/wiki/images/cards/{card_name.replace(' ', '_')}.png"

        return MagiNationCard(
            name=card_name,
            card_type=card_type,
            region=region,
            cost=cost,
            energy=energy,
            attack=attack,
            defense=defense,
            ability=ability,
            set_code=set_code,
            rarity=rarity,
            image_url=image_url
        )

    except Exception as e:
        print(f"Error parsing card {card_name}: {e}")
        return None


def get_cards_from_magi_nation_com(card_type_filter="all", max_cards=50):
    """
    Scrape Magi-Nation Duel cards from Magi-Nation.com card database.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of MagiNationCard objects
    """
    print("Fetching Magi-Nation Duel cards from Magi-Nation.com...")

    try:
        # Magi-Nation.com card database
        url = 'https://www.magi-nation.com/cards/'
        page = requests.get(url, timeout=10)
        tree = html.fromstring(page.content)

        cards = []

        # Parse card data from database (simplified)
        card_sections = tree.xpath('//div[contains(@class, "card-data")] | //tr[contains(@class, "card-row")]')

        for section in card_sections[:max_cards]:
            # Extract card info (would need actual parsing)
            card_name_elem = section.xpath('.//td[1]/text() | .//h3/text() | .//a/text()')
            if card_name_elem:
                card_name = card_name_elem[0].strip()

                card = MagiNationCard(
                    name=card_name,
                    card_type="Magi",
                    region="Arderial",
                    cost=0,
                    energy=15,
                    attack=0,
                    defense=0,
                    ability="Starting Magi",
                    set_code="BASE",
                    rarity="Common",
                    image_url=f"https://www.magi-nation.com/images/cards/{card_name.replace(' ', '_')}.jpg"
                )

                if card_type_filter == "all" or card.card_type.lower() == card_type_filter.lower():
                    cards.append(card)

        return cards

    except requests.exceptions.RequestException as e:
        print(f"Error scraping Magi-Nation.com (site may be unavailable): {e}")
        return []
    except Exception as e:
        print(f"Error scraping Magi-Nation.com: {e}")
        return []


def get_cards_from_community_resources(card_type_filter="all", max_cards=50):
    """
    Scrape Magi-Nation Duel cards from community resources and wikis.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of MagiNationCard objects
    """
    print("Fetching Magi-Nation Duel cards from community resources...")

    try:
        # Community wiki or resource site
        url = 'https://magination.fandom.com/wiki/Magi-Nation_Duel_Cards'
        page = requests.get(url, timeout=10)
        tree = html.fromstring(page.content)

        cards = []

        # Parse card mentions from wiki (simplified)
        card_mentions = tree.xpath('//a[@title and contains(@href, "Card:")] | //strong | //b')

        for mention in card_mentions[:max_cards]:
            text = mention.text_content().strip()
            href = mention.get('href', '')

            # Skip if it's not a card link or too short
            if len(text) > 3 and ('Card:' in href or 'cards' in text.lower()):
                card_name = text.replace(' Card', '').replace(' cards', '').strip()

                card = MagiNationCard(
                    name=card_name,
                    card_type="Creature",
                    region="Naroom",
                    cost=3,
                    energy=0,
                    attack=2,
                    defense=1,
                    ability="Community resource card",
                    set_code="BASE",
                    rarity="Common",
                    image_url=f"https://magination.fandom.com/wiki/images/cards/{card_name.replace(' ', '_')}.png"
                )

                if card_type_filter == "all" or card.card_type.lower() == card_type_filter.lower():
                    cards.append(card)

        return cards

    except requests.exceptions.RequestException as e:
        print(f"Error scraping community resources (site may be unavailable): {e}")
        return []
    except Exception as e:
        print(f"Error scraping community resources: {e}")
        return []


# -----------------------------
# Collection Management
# -----------------------------
def create_collection_from_cards(cards: List[MagiNationCard], collection_name: str) -> MagiNationDeck:
    """
    Create a Magi-Nation Duel collection from a list of cards.

    Args:
        cards: List of MagiNationCard objects
        collection_name: Name for the collection

    Returns:
        MagiNationDeck object representing the collection
    """
    return MagiNationDeck(
        name=collection_name,
        cards=cards,
        player="Collection Owner",
        id=f"mnd_collection_{hashlib.md5(collection_name.encode()).hexdigest()[:8]}"
    )


def search_magi_nation_cards(card_name: str) -> List[MagiNationCard]:
    """
    Search for Magi-Nation Duel cards by name.

    This implementation uses multiple data sources:
    - Magi-Nation Central wiki
    - Magi-Nation.com database
    - Community resources

    Args:
        card_name: Name of the card to search for

    Returns:
        List of matching MagiNationCard objects
    """
    print(f"Searching for Magi-Nation Duel card: {card_name}")

    cards = []

    # Search Magi-Nation Central
    try:
        central_cards = _search_cards_in_central(card_name)
        cards.extend(central_cards)
    except Exception as e:
        print(f"Error searching Magi-Nation Central: {e}")

    # Search community resources if no results
    if not cards:
        try:
            community_cards = _search_cards_in_community(card_name)
            cards.extend(community_cards)
        except Exception as e:
            print(f"Error searching community resources: {e}")

    return cards


def _search_cards_in_central(card_name: str) -> List[MagiNationCard]:
    """
    Search for cards in Magi-Nation Central wiki.

    Args:
        card_name: Name to search for

    Returns:
        List of matching MagiNationCard objects
    """
    cards = []

    try:
        # Search using the wiki's search functionality
        search_url = f'https://maginationcentral.com/wiki/index.php?search={card_name}&title=Special%3ASearch'
        page = requests.get(search_url)
        tree = html.fromstring(page.content)

        # Look for card links in search results
        card_links = tree.xpath('//div[@class="searchresults"]//a | //ul[@class="mw-search-results"]//a')

        for link in card_links:
            title = link.text_content().strip()
            href = link.get('href', '')

            if card_name.lower() in title.lower() and 'index.php' in href:
                # Try to parse the card page
                card = _parse_card_from_central_page(title, href)
                if card:
                    cards.append(card)

    except Exception as e:
        print(f"Error searching Magi-Nation Central: {e}")

    return cards


def _search_cards_in_community(card_name: str) -> List[MagiNationCard]:
    """
    Search for cards in community resources.

    Args:
        card_name: Name to search for

    Returns:
        List of matching MagiNationCard objects
    """
    cards = []

    try:
        # Search Magi-Nation fandom wiki
        search_url = f'https://magination.fandom.com/wiki/Special:Search?query={card_name}'
        page = requests.get(search_url)
        tree = html.fromstring(page.content)

        # Look for card mentions
        card_mentions = tree.xpath('//a[contains(@href, "Card:")] | //strong | //b')

        for mention in card_mentions:
            text = mention.text_content().strip()
            if card_name.lower() in text.lower() and len(text) > 3:
                card = MagiNationCard(
                    name=text,
                    card_type="Creature",
                    region="Naroom",
                    cost=3,
                    energy=0,
                    attack=2,
                    defense=1,
                    ability="Community resource card",
                    set_code="BASE",
                    rarity="Common",
                    image_url=f"https://magination.fandom.com/wiki/images/cards/{text.replace(' ', '_')}.png"
                )
                cards.append(card)

    except Exception as e:
        print(f"Error searching community resources: {e}")

    return cards


def fetch_card_image(card: MagiNationCard, output_path: str) -> bool:
    """
    Download a Magi-Nation Duel card image.

    Args:
        card: MagiNationCard object with image URL
        output_path: Local path where to save the image

    Returns:
        True if download successful, False otherwise
    """
    try:
        response = requests.get(card.image_url)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to download image for {card.name}")
            return False
    except Exception as e:
        print(f"Error downloading image for {card.name}: {e}")
        return False


# -----------------------------
# Batch Processing
# -----------------------------
def process_magi_nation_cards_batch(cards: List[MagiNationCard], output_dir: str) -> int:
    """
    Process a batch of Magi-Nation Duel cards for image fetching.

    Args:
        cards: List of MagiNationCard objects
        output_dir: Directory to save images

    Returns:
        Number of cards successfully processed
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    processed = 0

    for card in cards:
        print(f"Processing: {card.name}")

        # Download image
        filename = f"{card.name.replace(' ', '_')}.png"
        filepath = output_path / filename

        if fetch_card_image(card, str(filepath)):
            processed += 1
            print(f"Downloaded: {filename}")

    return processed


# -----------------------------
# Collection Export
# -----------------------------
def save_collection_to_file(collection: MagiNationDeck, output_file: str):
    """
    Save Magi-Nation Duel collection data to a human-readable text file.

    Args:
        collection: MagiNationDeck object to save
        output_file: Path where to save the file
    """
    with open(output_file, 'w') as f:
        f.write(f"Collection: {collection.name}\n")
        f.write(f"Player: {collection.player}\n")
        f.write(f"Collection ID: {collection.id}\n")
        f.write(f"Hash: {collection.hash}\n")
        f.write(f"Regions: {', '.join(collection.regions)}\n")
        f.write(f"\nCards ({len(collection.cards)} total):\n")
        f.write("-" * 60 + "\n")

        for card in collection.cards:
            f.write(f"{card.name} ({card.card_type})\n")
            f.write(f"  Region: {card.region}, Cost: {card.cost}")
            if card.energy > 0:
                f.write(f", Energy: {card.energy}")
            f.write("\n")
            if card.attack > 0:
                f.write(f"  Attack: {card.attack}, Defense: {card.defense}\n")
            f.write(f"  Set: {card.set_code}, Rarity: {card.rarity}\n")
            f.write(f"  Ability: {card.ability}\n\n")

    print(f"Saved Magi-Nation Duel collection with {len(collection.cards)} cards to {output_file}")


# -----------------------------
# Card Image Fetching (Placeholder)
# -----------------------------
def fetch_card_images_for_collection(cards: List[MagiNationCard], output_dir: str):
    """
    Placeholder for Magi-Nation Duel card image fetching.

    Args:
        cards: List of MagiNationCard objects
        output_dir: Directory to save images
    """
    print("Card image fetching for Magi-Nation Duel not yet implemented.")
    print("Would integrate with Magi-Nation card databases or community resources.")

    # Placeholder implementation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for card in cards:
        print(f"Would fetch image for: {card.name}")

    return len(cards)  # Return number of cards processed


# -----------------------------
# Sample Data Generation
# -----------------------------
def get_sample_magi_nation_cards(card_type_filter="all", max_cards=50):
    """
    Generate sample Magi-Nation Duel cards for testing and demonstration.

    Args:
        card_type_filter: Card type to filter by
        max_cards: Maximum number of cards to return

    Returns:
        List of MagiNationCard objects
    """
    print("Generating sample Magi-Nation Duel cards for testing...")

    regions = ["Arderial", "Cald", "Naroom", "Orothe", "Underneath", "Universal"]
    card_types = ["Magi", "Creature", "Spell", "Relic"]
    sample_names = {
        "Magi": ["Tony Jones", "Korg", "Gia", "Strag", "Yaki", "Poad", "Tonya Jones", "Bazha"],
        "Creature": ["Arboll", "Firefly", "Weebat", "Plith", "Diabolo", "Xyx", "Shadow", "Grow"],
        "Spell": ["Lightning", "Frost", "Grow", "Shadow", "Dream", "Nightmare", "Heal", "Energy"],
        "Relic": ["Ancient Staff", "Crystal Ring", "Dream Stone", "Nightmare Stone", "Staff of Power"]
    }

    cards = []

    for i in range(min(max_cards, 50)):  # Limit to reasonable number
        card_type = card_types[i % len(card_types)]
        region = regions[i % len(regions)]

        # Get appropriate name for card type
        type_names = sample_names.get(card_type, [f"Sample {card_type} {i+1}"])
        name = type_names[i % len(type_names)]

        # Set attributes based on card type
        if card_type == "Magi":
            cost, energy, attack, defense = 0, 15 + (i % 5), 0, 0
        elif card_type == "Creature":
            cost, energy, attack, defense = 2 + (i % 4), 0, 1 + (i % 3), i % 2
        elif card_type == "Spell":
            cost, energy, attack, defense = 1 + (i % 3), 0, 0, 0
        else:  # Relic
            cost, energy, attack, defense = 1 + (i % 2), 0, 0, 0

        ability = f"Sample {card_type.lower()} ability for {name}"
        rarity = ["Common", "Uncommon", "Rare"][i % 3]

        card = MagiNationCard(
            name=name,
            card_type=card_type,
            region=region,
            cost=cost,
            energy=energy,
            attack=attack,
            defense=defense,
            ability=ability,
            set_code="BASE",
            rarity=rarity,
            image_url=f"https://example.com/magination/cards/{name.replace(' ', '_')}.png"
        )

        if card_type_filter == "all" or card.card_type.lower() == card_type_filter.lower():
            cards.append(card)

    return cards
