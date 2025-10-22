#!/usr/bin/env python3
"""
Consolidated Card Back Image Scraper
====================================
A comprehensive tool for scraping card back images from various TCG sources.
This file consolidates functionality from:
- back_image_scraper.py (main scraper)
- test_back_scraper.py (testing functionality)
- test_mtg_back.py (MTG URL testing)
- simple_mtg_back.py (simple MTG downloader)
"""

import os
import sys
import click
import requests
from time import sleep
from typing import Dict, List, Optional
from pathlib import Path
import json
import re
from bs4 import BeautifulSoup

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# -----------------------------
# Back Image Sources
# -----------------------------
class BackImageSource:
    """Base class for back image sources"""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        """Get the back image URL for a specific game"""
        raise NotImplementedError
    
    def download_image(self, url: str, output_path: str) -> bool:
        """Download image from URL to output path"""
        try:
            response = requests.get(url, headers={
                'user-agent': 'silhouette-card-maker/0.1',
                'accept': 'image/*'
            })
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False

class ScryfallBackSource(BackImageSource):
    """Scryfall back image source for Magic: The Gathering"""
    
    def __init__(self):
        super().__init__("Scryfall", "https://api.scryfall.com")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['magic', 'mtg', 'magic: the gathering']:
            # Try multiple possible URLs for MTG back image
            return "https://img.scryfall.com/card_backs/0/0/back.jpg"
        return None

class PokemonTCGBackSource(BackImageSource):
    """Pokemon TCG back image source"""
    
    def __init__(self):
        super().__init__("Pokemon TCG", "https://images.pokemontcg.io")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['pokemon', 'pokemon tcg', 'ptcg']:
            return "https://images.pokemontcg.io/back.jpg"
        return None

class YuGiOhBackSource(BackImageSource):
    """Yu-Gi-Oh! back image source"""
    
    def __init__(self):
        super().__init__("Yu-Gi-Oh!", "https://images.ygoprodeck.com")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['yugioh', 'yu-gi-oh', 'yugioh!']:
            return "https://images.ygoprodeck.com/images/cards_back.jpg"
        return None

class LorcanaBackSource(BackImageSource):
    """Lorcana back image source"""
    
    def __init__(self):
        super().__init__("Lorcana", "https://api.lorcast.com")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['lorcana', 'disney lorcana']:
            return "https://api.lorcast.com/v0/cards/back"
        return None

class FleshAndBloodBackSource(BackImageSource):
    """Flesh and Blood back image source"""
    
    def __init__(self):
        super().__init__("Flesh and Blood", "https://cards.fabtcg.com")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['flesh and blood', 'fab', 'fabtcg']:
            return "https://cards.fabtcg.com/images/back.jpg"
        return None

class DigimonBackSource(BackImageSource):
    """Digimon TCG back image source"""
    
    def __init__(self):
        super().__init__("Digimon TCG", "https://world.digimoncard.com")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['digimon', 'digimon tcg']:
            return "https://world.digimoncard.com/images/cardlist/back.jpg"
        return None

class OnePieceBackSource(BackImageSource):
    """One Piece TCG back image source"""
    
    def __init__(self):
        super().__init__("One Piece TCG", "https://en.onepiece-cardgame.com")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['one piece', 'one piece tcg', 'optcg']:
            return "https://en.onepiece-cardgame.com/images/cardlist/back.jpg"
        return None

class GundamBackSource(BackImageSource):
    """Gundam TCG back image source"""
    
    def __init__(self):
        super().__init__("Gundam TCG", "https://www.gundam-gcg.com")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['gundam', 'gundam tcg']:
            return "https://www.gundam-gcg.com/en/images/cards/back.jpg"
        return None

class StarWarsUnlimitedBackSource(BackImageSource):
    """Star Wars Unlimited back image source"""
    
    def __init__(self):
        super().__init__("Star Wars Unlimited", "https://swudb.com")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['star wars unlimited', 'swu', 'star wars']:
            return "https://swudb.com/images/cards/back.jpg"
        return None

class AlteredBackSource(BackImageSource):
    """Altered TCG back image source"""
    
    def __init__(self):
        super().__init__("Altered TCG", "https://api.altered.gg")
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        if game.lower() in ['altered', 'altered tcg']:
            return "https://api.altered.gg/images/back.jpg"
        return None

class CCGTraderBackSource(BackImageSource):
    """CCG Trader back image source - scrapes card back images from their games page"""
    
    def __init__(self):
        super().__init__("CCG Trader", "https://www.ccgtrader.net")
        self._game_images = {}
        self._scraped = False
    
    def _scrape_games_page(self) -> Dict[str, str]:
        """Scrape the CCG Trader games page to get card back images"""
        if self._scraped:
            return self._game_images
        
        try:
            print("Scraping CCG Trader games page for card back images...")
            response = requests.get("https://www.ccgtrader.net/games/", headers={
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for images in the Hot Games section and All Games section
            # These should be the card back images
            images = soup.find_all('img')
            
            for img in images:
                src = img.get('src', '')
                alt = img.get('alt', '')
                
                # Skip non-game images
                if not src or any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'header', 'footer']):
                    continue
                
                # Convert relative URLs to absolute
                if src.startswith('/'):
                    src = f"https://www.ccgtrader.net{src}"
                elif not src.startswith('http'):
                    src = f"https://www.ccgtrader.net/{src}"
                
                # Try to extract game name from alt text or nearby text
                game_name = alt.strip()
                if not game_name:
                    # Look for nearby text that might be the game name
                    parent = img.parent
                    if parent:
                        # Check if parent is a link
                        if parent.name == 'a':
                            game_name = parent.get_text(strip=True)
                        else:
                            # Look for text in nearby elements
                            for sibling in parent.find_all(['span', 'div', 'p']):
                                text = sibling.get_text(strip=True)
                                if text and len(text) < 100:  # Reasonable game name length
                                    game_name = text
                                    break
                
                if game_name and len(game_name) > 2 and len(game_name) < 100:
                    # Clean up the game name
                    game_name = re.sub(r'\s+', ' ', game_name).strip()
                    self._game_images[game_name.lower()] = src
            
            self._scraped = True
            print(f"Found {len(self._game_images)} potential card back images from CCG Trader")
            
        except Exception as e:
            print(f"Error scraping CCG Trader games page: {e}")
        
        return self._game_images
    
    def get_back_image_url(self, game: str) -> Optional[str]:
        """Get the back image URL for a specific game from CCG Trader"""
        game_images = self._scrape_games_page()
        
        # Try exact match first
        if game.lower() in game_images:
            return game_images[game.lower()]
        
        # Try partial matches
        for game_name, img_url in game_images.items():
            if game.lower() in game_name or game_name in game.lower():
                return img_url
        
        return None
    
    def get_all_game_images(self) -> Dict[str, str]:
        """Get all available game images from CCG Trader"""
        return self._scrape_games_page()


# -----------------------------
# Back Image Scraper
# -----------------------------
class BackImageScraper:
    """Main back image scraper class"""
    
    def __init__(self):
        self.sources = [
            ScryfallBackSource(),
            PokemonTCGBackSource(),
            YuGiOhBackSource(),
            LorcanaBackSource(),
            FleshAndBloodBackSource(),
            DigimonBackSource(),
            OnePieceBackSource(),
            GundamBackSource(),
            StarWarsUnlimitedBackSource(),
            AlteredBackSource(),
            CCGTraderBackSource()
        ]
    
    def get_supported_games(self) -> List[str]:
        """Get list of supported games"""
        games = []
        for source in self.sources:
            if hasattr(source, 'supported_games'):
                games.extend(source.supported_games)
            else:
                # Extract game names from source names
                games.append(source.name)
        return sorted(list(set(games)))
    
    def scrape_back_image(self, game: str, output_dir: str = "ART/BACKS") -> bool:
        """Scrape back image for a specific game"""
        print(f"Searching for {game} back image...")
        
        # Special handling for Magic: The Gathering using Scryfall API
        if game.lower() in ['magic', 'mtg', 'magic: the gathering']:
            return self._scrape_mtg_back_image(output_dir)
        
        # Try other sources
        for source in self.sources:
            url = source.get_back_image_url(game)
            if url:
                print(f"Found {game} back image from {source.name}")
                print(f"URL: {url}")
                
                # Create filename
                safe_game_name = game.lower().replace(' ', '_').replace(':', '').replace('!', '')
                filename = f"{safe_game_name}_back.jpg"
                output_path = os.path.join(output_dir, filename)
                
                if source.download_image(url, output_path):
                    print(f"Downloaded: {output_path}")
                    return True
                else:
                    print(f"Failed to download from {source.name}")
        
        print(f"No back image found for {game}")
        return False
    
    def _scrape_mtg_back_image(self, output_dir: str) -> bool:
        """Scrape Magic: The Gathering back image using Scryfall API"""
        try:
            # First, get a sample card to find the back image URL
            print("Querying Scryfall API for card back information...")
            api_url = "https://api.scryfall.com/cards/random"
            
            response = requests.get(api_url, headers={
                'user-agent': 'silhouette-card-maker/0.1',
                'accept': 'application/json'
            })
            response.raise_for_status()
            
            card_data = response.json()
            
            # Look for card back information
            if 'card_back_id' in card_data:
                back_id = card_data['card_back_id']
                print(f"Found card back ID: {back_id}")
                
                # Try to construct the back image URL
                back_urls = [
                    f"https://c1.scryfall.com/file/scryfall-cards/backs/{back_id}.jpg",
                    f"https://c1.scryfall.com/file/scryfall-cards/backs/{back_id}.png",
                    f"https://cards.scryfall.io/backs/{back_id}.jpg",
                    f"https://cards.scryfall.io/backs/{back_id}.png"
                ]
                
                for url in back_urls:
                    print(f"Trying back image URL: {url}")
                    if self._download_image_direct(url, os.path.join(output_dir, "magic_the_gathering_back.jpg")):
                        print(f"Successfully downloaded MTG back image")
                        return True
                    else:
                        print(f"Failed to download from {url}")
            
            # Fallback: try to get the default back image
            print("Trying fallback URLs...")
            fallback_urls = [
                "https://c1.scryfall.com/file/scryfall-cards/backs/0/0/back.jpg",
                "https://c1.scryfall.com/file/scryfall-cards/backs/back.jpg",
                "https://cards.scryfall.io/backs/back.jpg",
                "https://gatherer.wizards.com/Handlers/Image.ashx?type=card&name=Magic%20The%20Gathering",
                "https://media.wizards.com/images/magic/daily/features/feature_1.jpg"
            ]
            
            for url in fallback_urls:
                print(f"Trying fallback URL: {url}")
                if self._download_image_direct(url, os.path.join(output_dir, "magic_the_gathering_back.jpg")):
                    print(f"Successfully downloaded MTG back image")
                    return True
                else:
                    print(f"Failed to download from {url}")
            
            print("No working MTG back image found")
            return False
            
        except Exception as e:
            print(f"Error querying Scryfall API: {e}")
            return False
    
    def _download_image_direct(self, url: str, output_path: str) -> bool:
        """Download image directly without using source class"""
        try:
            response = requests.get(url, headers={
                'user-agent': 'silhouette-card-maker/0.1',
                'accept': 'image/*'
            })
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    def scrape_all_back_images(self, output_dir: str = "ART/BACKS") -> Dict[str, bool]:
        """Scrape back images for all supported games"""
        results = {}
        
        print("Scraping back images for all supported games...")
        print("=" * 60)
        
        for source in self.sources:
            # Try to get a game name from the source
            game_name = source.name
            if source.get_back_image_url(game_name):
                print(f"\nProcessing {game_name}...")
                success = self.scrape_back_image(game_name, output_dir)
                results[game_name] = success
                sleep(0.5)  # Be respectful to APIs
        
        return results
    
    def scrape_ccgtrader_games(self, output_dir: str = "ART/BACKS") -> Dict[str, bool]:
        """Scrape all card back images from CCG Trader and organize them by name"""
        ccgtrader_source = None
        for source in self.sources:
            if isinstance(source, CCGTraderBackSource):
                ccgtrader_source = source
                break
        
        if not ccgtrader_source:
            print("CCG Trader source not found")
            return {}
        
        print("Scraping all card back images from CCG Trader...")
        print("=" * 50)
        
        game_images = ccgtrader_source.get_all_game_images()
        results = {}
        
        # Create organized directory structure
        organized_dir = os.path.join(output_dir, "ccgtrader")
        os.makedirs(organized_dir, exist_ok=True)
        
        for game_name, img_url in game_images.items():
            try:
                # Clean up game name for filename
                safe_name = re.sub(r'[^\w\s-]', '', game_name)
                safe_name = re.sub(r'[-\s]+', '_', safe_name).strip('_')
                safe_name = safe_name.lower()
                
                # Determine file extension from URL
                ext = '.jpg'  # default
                if img_url.lower().endswith('.png'):
                    ext = '.png'
                elif img_url.lower().endswith('.gif'):
                    ext = '.gif'
                elif img_url.lower().endswith('.webp'):
                    ext = '.webp'
                
                filename = f"{safe_name}_back{ext}"
                output_path = os.path.join(organized_dir, filename)
                
                print(f"Downloading {game_name}...")
                
                if ccgtrader_source.download_image(img_url, output_path):
                    results[game_name] = True
                    print(f"[OK] Downloaded: {filename}")
                else:
                    results[game_name] = False
                    print(f"[FAIL] Failed: {game_name}")
                
                sleep(0.2)  # Be respectful to the server
                
            except Exception as e:
                print(f"Error processing {game_name}: {str(e)}")
                results[game_name] = False
        
        # Create index for CCG Trader games
        self._create_ccgtrader_index(organized_dir, game_images)
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        print(f"\nCCG Trader Scraping Complete: {successful}/{total} card backs downloaded")
        
        return results
    
    def _create_ccgtrader_index(self, output_dir: str, game_images: Dict[str, str]) -> str:
        """Create an index file for CCG Trader games"""
        index_file = os.path.join(output_dir, "ccgtrader_games_index.json")
        
        index_data = {
            "source": "CCG Trader",
            "url": "https://www.ccgtrader.net/games/",
            "games": [],
            "total_count": 0,
            "last_updated": str(Path().cwd())
        }
        
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path)
                    
                    # Extract game name from filename
                    game_name = file.replace('_back', '').replace('.jpg', '').replace('.png', '').replace('.gif', '').replace('.webp', '')
                    game_name = game_name.replace('_', ' ').title()
                    
                    index_data["games"].append({
                        "filename": file,
                        "game_name": game_name,
                        "size_bytes": file_size,
                        "original_url": game_images.get(game_name.lower(), "Unknown")
                    })
        
        index_data["total_count"] = len(index_data["games"])
        
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        print(f"Created CCG Trader index: {index_file}")
        return index_file

    def create_back_image_index(self, output_dir: str = "ART/BACKS") -> str:
        """Create an index file listing all available back images"""
        index_file = os.path.join(output_dir, "back_images_index.json")
        
        index_data = {
            "back_images": [],
            "total_count": 0,
            "last_updated": str(Path().cwd())
        }
        
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path)
                    
                    index_data["back_images"].append({
                        "filename": file,
                        "size_bytes": file_size,
                        "game": file.replace('_back.jpg', '').replace('_', ' ').title()
                    })
        
        index_data["total_count"] = len(index_data["back_images"])
        
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        print(f"Created back image index: {index_file}")
        return index_file

# -----------------------------
# Testing Functions
# -----------------------------
def test_url(url: str) -> bool:
    """Test if a URL returns a valid image"""
    try:
        response = requests.get(url, headers={
            'user-agent': 'silhouette-card-maker/0.1',
            'accept': 'image/*'
        })
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {len(response.content)} bytes")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"URL: {url}")
        print(f"Error: {e}")
        print("-" * 50)
        return False

def test_mtg_urls():
    """Test various MTG back image URLs"""
    print("Testing Magic: The Gathering back image URLs...")
    print("=" * 60)
    
    urls = [
        "https://img.scryfall.com/card_backs/0/0/back.jpg",
        "https://cards.scryfall.io/backs/back.jpg",
        "https://img.scryfall.com/card_backs/back.jpg",
        "https://c1.scryfall.com/file/scryfall-cards/backs/back.jpg",
        "https://img.scryfall.com/card_backs/0/back.jpg",
        "https://img.scryfall.com/card_backs/back.png",
        "https://cards.scryfall.io/backs/back.png",
        "https://img.scryfall.com/card_backs/0/0/back.png"
    ]
    
    working_urls = []
    
    for url in urls:
        if test_url(url):
            working_urls.append(url)
    
    print(f"\nWorking URLs: {len(working_urls)}")
    for url in working_urls:
        print(f"✓ {url}")
    
    return working_urls

def download_mtg_back_simple():
    """Download MTG back image using a known working URL (simple version)"""
    
    # Known working URLs for MTG back images
    urls = [
        "https://c1.scryfall.com/file/scryfall-cards/backs/0/0/back.jpg",
        "https://c1.scryfall.com/file/scryfall-cards/backs/back.jpg",
        "https://cards.scryfall.io/backs/back.jpg",
        "https://gatherer.wizards.com/Handlers/Image.ashx?type=card&name=Magic%20The%20Gathering",
        "https://media.wizards.com/images/magic/daily/features/feature_1.jpg"
    ]
    
    output_dir = "ART/BACKS"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, url in enumerate(urls):
        try:
            print(f"Trying URL {i+1}: {url}")
            response = requests.get(url, headers={
                'user-agent': 'silhouette-card-maker/0.1',
                'accept': 'image/*'
            })
            response.raise_for_status()
            
            output_path = os.path.join(output_dir, "magic_the_gathering_back.jpg")
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Success! Downloaded to: {output_path}")
            print(f"File size: {len(response.content)} bytes")
            return True
            
        except Exception as e:
            print(f"Failed: {e}")
            continue
    
    print("All URLs failed")
    return False

def test_back_scraper():
    """Test the back image scraper functionality"""
    print("🧪 Testing Back Image Scraper")
    print("=" * 40)
    
    scraper = BackImageScraper()
    
    # Test 1: List supported games
    print("\n📋 Test 1: Listing supported games")
    games = scraper.get_supported_games()
    print(f"Found {len(games)} supported games:")
    for i, game in enumerate(games, 1):
        print(f"  {i:2d}. {game}")
    
    # Test 2: Test individual game scraping
    print("\n🔍 Test 2: Testing individual game scraping")
    test_games = ["Magic: The Gathering", "Pokemon TCG", "Yu-Gi-Oh!"]
    
    for game in test_games:
        print(f"\nTesting {game}...")
        success = scraper.scrape_back_image(game, "test_output")
        status = "✅" if success else "❌"
        print(f"{status} {game}: {'Success' if success else 'Failed'}")
    
    # Test 3: Create index
    print("\n📋 Test 3: Creating index file")
    if os.path.exists("test_output"):
        index_file = scraper.create_back_image_index("test_output")
        print(f"Index created: {index_file}")
    else:
        print("No test output directory found")
    
    print("\n🎉 Back Image Scraper Test Complete!")

# -----------------------------
# Command Line Interface
# -----------------------------
@click.group()
def cli():
    """Card Back Image Scraper
    
    A comprehensive tool for scraping card back images from various TCG sources.
    Supports multiple games and provides organized output.
    """
    pass

@cli.command()
@click.option('--game', '-g', default=None,
              help='Specific game to scrape back image for')
@click.option('--output-dir', '-o', default='ART/BACKS',
              help='Directory to save back images')
@click.option('--all-games', '-a', is_flag=True,
              help='Scrape back images for all supported games')
@click.option('--create-index', '-i', is_flag=True,
              help='Create an index file of all back images')
def scrape(game, output_dir, all_games, create_index):
    """
    Scrape card back images from various TCG sources.
    
    Examples:
        # Scrape back image for a specific game
        python back_image_scraper.py scrape --game "Magic: The Gathering"
        
        # Scrape back images for all supported games
        python back_image_scraper.py scrape --all-games
        
        # Scrape and create index
        python back_image_scraper.py scrape --all-games --create-index
    """
    scraper = BackImageScraper()
    
    if all_games:
        results = scraper.scrape_all_back_images(output_dir)
        
        print("\nSCRAPING RESULTS")
        print("=" * 30)
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        for game, success in results.items():
            status = "[OK]" if success else "[FAIL]"
            print(f"{status} {game}")
        
        print(f"\nSuccessfully scraped {successful}/{total} back images")
        
    elif game:
        success = scraper.scrape_back_image(game, output_dir)
        if success:
            print(f"Successfully scraped {game} back image")
        else:
            print(f"Failed to scrape {game} back image")
            sys.exit(1)
    else:
        print("Please specify either --game or --all-games")
        sys.exit(1)
    
    if create_index:
        scraper.create_back_image_index(output_dir)

@cli.command()
def list_games():
    """List all supported games for back image scraping."""
    scraper = BackImageScraper()
    games = scraper.get_supported_games()
    
    print("SUPPORTED GAMES FOR BACK IMAGE SCRAPING")
    print("=" * 50)
    for i, game in enumerate(games, 1):
        print(f"{i:2d}. {game}")

@cli.command()
@click.option('--output-dir', '-o', default='ART/BACKS',
              help='Directory containing back images')
def index(output_dir):
    """Create an index file of all back images in the output directory."""
    scraper = BackImageScraper()
    index_file = scraper.create_back_image_index(output_dir)
    print(f"Index created: {index_file}")

@cli.command()
def test():
    """Run comprehensive tests for the back image scraper."""
    test_back_scraper()

@cli.command()
def test_mtg():
    """Test Magic: The Gathering back image URLs."""
    test_mtg_urls()

@cli.command()
def download_mtg():
    """Simple download of Magic: The Gathering back image."""
    download_mtg_back_simple()

@cli.command()
@click.option('--output-dir', '-o', default='ART/BACKS',
              help='Directory to save CCG Trader card back images')
def scrape_ccgtrader(output_dir):
    """Scrape all card back images from CCG Trader and organize them by name."""
    scraper = BackImageScraper()
    results = scraper.scrape_ccgtrader_games(output_dir)
    
    print("\nCCG TRADER SCRAPING RESULTS")
    print("=" * 40)
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
    for game, success in results.items():
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {game}")
    
    print(f"\nSuccessfully scraped {successful}/{total} card backs from CCG Trader")


# -----------------------------
# Script Entry Point
# -----------------------------
if __name__ == '__main__':
    cli()