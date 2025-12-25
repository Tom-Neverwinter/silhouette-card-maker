import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add src directory to path
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir / 'src'))
sys.path.append(str(root_dir / 'plugins' / 'ccgtrader'))

try:
    from ccgt_scraper import get_games_list
except ImportError:
    print("Warning: Could not import ccgt_scraper. CCGTrader games will not be indexed.")
    get_games_list = lambda: []

GAMES_INDEX_PATH = root_dir / 'data' / 'games_index.json'

def scan_specialized_plugins() -> Dict[str, str]:
    """
    Scans the plugins directory for specialized plugins.
    Returns a dict of {game_name: plugin_folder_name}
    """
    plugins_dir = root_dir / 'plugins'
    specialized_games = {}

    if not plugins_dir.exists():
        return specialized_games

    for item in plugins_dir.iterdir():
        if item.is_dir() and item.name != 'ccgtrader' and not item.name.startswith('.'):
            # Heuristic: Use the folder name as the game name, formatted nicely
            # Or look for a manifest/README. 
            # For now, simple formatting:
            game_name = item.name.replace('_', ' ').title()
            
            # Check for specific overrides or metadata if needed
            # For now, just map folder name to game name
            specialized_games[game_name] = item.name

    return specialized_games

def update_game_index():
    """
    Updates the master game index by merging specialized plugins and CCGTrader games.
    """
    print("Updating Game Registry...")
    
    # 1. Get Specialized Plugins
    specialized_plugins = scan_specialized_plugins()
    print(f"Found {len(specialized_plugins)} specialized plugins.")

    # 2. Get CCGTrader Games
    try:
        ccgt_games = get_games_list()
        print(f"Found {len(ccgt_games)} games from CCGTrader.")
    except Exception as e:
        print(f"Error fetching CCGTrader games: {e}")
        ccgt_games = []

    # 3. Merge
    # Structure: { "Game Name": { "plugin": "folder_name", "url": "optional_url" } }
    game_registry = {}

    # Add CCGTrader games first (as base)
    for game in ccgt_games:
        game_registry[game.name] = {
            "plugin": "ccgtrader",
            "url": game.url,
            "type": "universal"
        }

    # Overwrite with specialized plugins
    for game_name, plugin_folder in specialized_plugins.items():
        # If the game already exists (from CCGTrader), we update it to use the specialized plugin
        # We try to match loosely to catch "Pokemon" vs "Pokemon TCG"
        
        match_found = False
        for existing_name in list(game_registry.keys()):
            if game_name.lower() in existing_name.lower() or existing_name.lower() in game_name.lower():
                game_registry[existing_name]["plugin"] = plugin_folder
                game_registry[existing_name]["type"] = "specialized"
                match_found = True
                # We keep the existing name from CCGTrader as it's likely the "official" one
                break
        
        if not match_found:
            game_registry[game_name] = {
                "plugin": plugin_folder,
                "url": None,
                "type": "specialized"
            }

    # 4. Save
    GAMES_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Sort by name
    sorted_registry = dict(sorted(game_registry.items()))
    
    with open(GAMES_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted_registry, f, indent=4)

    print(f"Game Registry updated. Total games: {len(sorted_registry)}")
    print(f"Index saved to: {GAMES_INDEX_PATH}")

def get_game_plugin(game_name: str) -> Dict[str, Any]:
    """
    Retrieves plugin info for a specific game.
    """
    if not GAMES_INDEX_PATH.exists():
        update_game_index()

    with open(GAMES_INDEX_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    return registry.get(game_name)

if __name__ == "__main__":
    update_game_index()
