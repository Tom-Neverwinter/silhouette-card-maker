from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from lxml import html

class CardScraper(ABC):
    """
    Abstract base class for all card scrapers to ensure uniformity.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _get_tree(self, url: str):
        """Helper to get lxml tree from URL."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return html.fromstring(response.content)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    @abstractmethod
    def get_games_list(self) -> List[Dict[str, str]]:
        """
        Get list of supported games.
        Returns: List of dicts with 'name' and 'url'.
        """
        pass

    @abstractmethod
    def get_game_sets(self, game_url: str) -> List[Dict[str, Any]]:
        """
        Get list of sets for a game.
        Returns: List of dicts with 'name', 'url', etc.
        """
        pass

    @abstractmethod
    def get_set_cards(self, set_url: str) -> List[Dict[str, Any]]:
        """
        Get list of cards for a set.
        Returns: List of dicts with 'name', 'image_url', 'rarity', etc.
        """
        pass

    def download_image(self, url: str, output_path: str) -> bool:
        """
        Download an image to the specified path.
        """
        try:
            response = self.session.get(url, stream=True, timeout=15)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
            return False
        except Exception as e:
            print(f"Error downloading image {url}: {e}")
            return False
