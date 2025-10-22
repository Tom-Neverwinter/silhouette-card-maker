# Universal CCG GUI Integration Module for CCGTrader.net
# =====================================================
# This module handles integration with the main Silhouette Card Maker GUI

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import List, Dict, Any

# Import our custom modules
from ccgt_scraper import UniversalCard, UniversalGame, UniversalCollection
from ccgt_api import (
    search_universal_cards,
    get_game_cards,
    get_popular_games_cards,
    create_game_collection,
    discover_available_games,
    get_cross_game_collection
)

# -----------------------------
# GUI Integration Class
# -----------------------------
class UniversalCCGPluginGUI:
    """
    GUI integration class for Universal CCG scraper.

    This class provides the interface between the main Silhouette Card Maker
    GUI and the universal CCG scraping functionality.
    """

    def __init__(self, parent_frame, plugin_manager=None):
        """
        Initialize the Universal CCG plugin GUI.

        Args:
            parent_frame: The parent tkinter frame to embed the plugin GUI in
            plugin_manager: Reference to the main plugin manager (optional)
        """
        self.parent = parent_frame
        self.plugin_manager = plugin_manager
        self.current_cards = []
        self.current_collection = None

        self._create_gui()

    def _create_gui(self):
        """Create the main GUI components."""
        # Main container frame
        self.main_frame = ttk.Frame(self.parent, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            self.main_frame,
            text="Universal CCG Scraper (CCGTrader.net)",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Create notebook for different sections
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create tabs
        self._create_games_tab()
        self._create_search_tab()
        self._create_collection_tab()
        self._create_advanced_tab()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _create_games_tab(self):
        """Create the games browsing tab."""
        games_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(games_frame, text="Browse Games")

        # Games list
        list_frame = ttk.LabelFrame(games_frame, text="Available CCGs", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Games listbox with scrollbar
        games_listbox_frame = ttk.Frame(list_frame)
        games_listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.games_listbox = tk.Listbox(games_listbox_frame, height=15)
        games_scrollbar = ttk.Scrollbar(games_listbox_frame, orient=tk.VERTICAL, command=self.games_listbox.yview)
        self.games_listbox.configure(yscrollcommand=games_scrollbar.set)

        self.games_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        games_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Load games button
        load_games_btn = ttk.Button(
            games_frame,
            text="Load Games List",
            command=self._load_games_list
        )
        load_games_btn.pack(pady=(10, 0))

        # Game details frame
        details_frame = ttk.LabelFrame(games_frame, text="Game Details", padding="5")
        details_frame.pack(fill=tk.X, pady=(10, 0))

        self.game_details_text = tk.Text(details_frame, height=6, wrap=tk.WORD)
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.game_details_text.yview)
        self.game_details_text.configure(yscrollcommand=details_scrollbar.set)

        self.game_details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Game actions
        actions_frame = ttk.Frame(games_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            actions_frame,
            text="Get Cards",
            command=self._get_game_cards
        ).pack(side=tk.LEFT)

        ttk.Button(
            actions_frame,
            text="Add to Collection",
            command=self._add_game_to_collection
        ).pack(side=tk.LEFT, padx=(10, 0))

    def _create_search_tab(self):
        """Create the search tab."""
        search_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(search_frame, text="Search Cards")

        # Search entry
        search_entry_frame = ttk.Frame(search_frame)
        search_entry_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_entry_frame, text="Card Name:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_entry_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        search_btn = ttk.Button(
            search_entry_frame,
            text="Search",
            command=self._search_cards
        )
        search_btn.pack(side=tk.RIGHT)

        # Games filter
        filter_frame = ttk.LabelFrame(search_frame, text="Games Filter", padding="5")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        self.games_filter_var = tk.StringVar(value="All Games")
        games_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.games_filter_var,
            values=["All Games", "Magic: The Gathering", "Pokémon", "Yu-Gi-Oh!", "Digimon", "Dragon Ball Super"],
            state="readonly"
        )
        games_filter_combo.pack(fill=tk.X)

        # Search results
        results_frame = ttk.LabelFrame(search_frame, text="Search Results", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview for results
        columns = ("name", "game", "set", "type", "rarity", "cost")
        self.search_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=10
        )

        # Define column headings
        self.search_tree.heading("name", text="Card Name")
        self.search_tree.heading("game", text="Game")
        self.search_tree.heading("set", text="Set")
        self.search_tree.heading("type", text="Type")
        self.search_tree.heading("rarity", text="Rarity")
        self.search_tree.heading("cost", text="Cost")

        # Set column widths
        self.search_tree.column("name", width=200)
        self.search_tree.column("game", width=120)
        self.search_tree.column("set", width=100)
        self.search_tree.column("type", width=80)
        self.search_tree.column("rarity", width=80)
        self.search_tree.column("cost", width=50)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)

        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Search actions
        search_actions_frame = ttk.Frame(search_frame)
        search_actions_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            search_actions_frame,
            text="Fetch Images",
            command=self._fetch_search_images
        ).pack(side=tk.LEFT)

        ttk.Button(
            search_actions_frame,
            text="Add to Collection",
            command=self._add_search_to_collection
        ).pack(side=tk.LEFT, padx=(10, 0))

    def _create_collection_tab(self):
        """Create the collection management tab."""
        collection_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(collection_frame, text="Collections")

        # Collection list
        list_frame = ttk.LabelFrame(collection_frame, text="Collections", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Collection listbox
        self.collection_listbox = tk.Listbox(list_frame, height=8)
        collection_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.collection_listbox.yview)
        self.collection_listbox.configure(yscrollcommand=collection_scrollbar.set)

        self.collection_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        collection_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Collection buttons
        collection_btn_frame = ttk.Frame(collection_frame)
        collection_btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            collection_btn_frame,
            text="Load Collection",
            command=self._load_collection
        ).pack(side=tk.LEFT)

        ttk.Button(
            collection_btn_frame,
            text="Save Collection",
            command=self._save_collection
        ).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(
            collection_btn_frame,
            text="New Collection",
            command=self._new_collection
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Collection info
        info_frame = ttk.LabelFrame(collection_frame, text="Collection Info", padding="5")
        info_frame.pack(fill=tk.X, pady=(10, 0))

        self.collection_info_text = tk.Text(info_frame, height=5, wrap=tk.WORD)
        collection_info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.collection_info_text.yview)
        self.collection_info_text.configure(yscrollcommand=collection_info_scrollbar.set)

        self.collection_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        collection_info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_advanced_tab(self):
        """Create the advanced features tab."""
        advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_frame, text="Advanced")

        # Cross-game search
        cross_game_frame = ttk.LabelFrame(advanced_frame, text="Cross-Game Search", padding="5")
        cross_game_frame.pack(fill=tk.X, pady=(0, 10))

        cross_game_entry_frame = ttk.Frame(cross_game_frame)
        cross_game_entry_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(cross_game_entry_frame, text="Card Theme:").pack(side=tk.LEFT)
        self.cross_game_var = tk.StringVar()
        cross_game_entry = ttk.Entry(cross_game_entry_frame, textvariable=self.cross_game_var)
        cross_game_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        cross_game_btn = ttk.Button(
            cross_game_entry_frame,
            text="Find Variants",
            command=self._cross_game_search
        )
        cross_game_btn.pack(side=tk.RIGHT)

        # Popular games collection
        popular_frame = ttk.LabelFrame(advanced_frame, text="Popular Games Collection", padding="5")
        popular_frame.pack(fill=tk.X, pady=(0, 10))

        popular_btn_frame = ttk.Frame(popular_frame)
        popular_btn_frame.pack(fill=tk.X)

        ttk.Button(
            popular_btn_frame,
            text="Generate Popular Collection",
            command=self._generate_popular_collection
        ).pack(side=tk.LEFT)

        # Settings
        settings_frame = ttk.LabelFrame(advanced_frame, text="Settings", padding="5")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame,
            text="Automatically save collections",
            variable=self.auto_save_var
        ).pack(anchor=tk.W)

        self.fetch_images_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            settings_frame,
            text="Fetch images when available",
            variable=self.fetch_images_var
        ).pack(anchor=tk.W)

    def _load_games_list(self):
        """Load the list of available games."""
        self.status_var.set("Loading games list...")

        try:
            games = discover_available_games()

            # Clear existing items
            self.games_listbox.delete(0, tk.END)

            # Add games to listbox
            for game in games[:50]:  # Limit to first 50
                self.games_listbox.insert(tk.END, game.name)

            self.status_var.set(f"Loaded {len(games)} games")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load games: {str(e)}")
            self.status_var.set("Error loading games")

    def _get_game_cards(self):
        """Get cards for the selected game."""
        selection = self.games_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a game first.")
            return

        game_name = self.games_listbox.get(selection[0])
        self.status_var.set(f"Fetching cards for {game_name}...")

        try:
            cards = get_game_cards(game_name, 20)

            if cards:
                self.current_cards = cards
                messagebox.showinfo("Success", f"Found {len(cards)} cards for {game_name}")

                # Switch to search tab and populate results
                self.notebook.select(1)  # Switch to search tab
                self._populate_search_results(cards)
            else:
                messagebox.showinfo("No Results", f"No cards found for {game_name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get cards: {str(e)}")
        finally:
            self.status_var.set("Ready")

    def _search_cards(self):
        """Search for cards across games."""
        card_name = self.search_var.get().strip()
        if not card_name:
            messagebox.showwarning("Warning", "Please enter a card name to search for.")
            return

        self.status_var.set(f"Searching for '{card_name}'...")

        # Clear previous results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        try:
            games_filter = None
            if self.games_filter_var.get() != "All Games":
                games_filter = [self.games_filter_var.get()]

            cards = search_universal_cards(card_name, games_filter, 30)

            if cards:
                self._populate_search_results(cards)
            else:
                messagebox.showinfo("No Results", f"No cards found matching '{card_name}'")

        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
        finally:
            self.status_var.set("Ready")

    def _populate_search_results(self, cards):
        """Populate the search results treeview."""
        for card in cards:
            self.search_tree.insert("", tk.END, values=(
                card.name,
                card.game,
                card.set_name,
                card.card_type or "Unknown",
                card.rarity,
                card.cost or "N/A"
            ))

    def _fetch_search_images(self):
        """Fetch images for selected cards in search results."""
        selection = self.search_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select cards to fetch images for.")
            return

        # Get selected cards (simplified - would need better mapping)
        selected_cards = []
        for item in selection:
            values = self.search_tree.item(item, "values")
            # Create a basic card object
            card = UniversalCard(
                name=values[0],
                game=values[1],
                set_name=values[2],
                set_code="BASE",
                card_number="001",
                rarity=values[4],
                image_url=f"https://example.com/cards/{values[1].lower().replace(' ', '_')}_{values[0].lower().replace(' ', '_')}.png"
            )
            selected_cards.append(card)

        if selected_cards:
            # This would call the actual image fetching
            messagebox.showinfo("Info", f"Would fetch images for {len(selected_cards)} cards")

    def _add_search_to_collection(self):
        """Add selected search results to current collection."""
        selection = self.search_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select cards to add to collection.")
            return

        if not self.current_collection:
            messagebox.showwarning("Warning", "Please create or load a collection first.")
            return

        # This would need proper implementation to add cards to existing collection
        messagebox.showinfo("Info", "Add to collection feature would be implemented here.")

    def _load_collection(self):
        """Load a collection from file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                if file_path.endswith('.json'):
                    collection = load_universal_collection_from_json(file_path)
                else:
                    # Would need implementation for text files
                    messagebox.showinfo("Info", "Text file loading not yet implemented.")
                    return

                self.current_collection = collection
                self._display_collection_info(collection)

                # Update collection listbox
                self.collection_listbox.insert(tk.END, collection.name)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load collection: {str(e)}")

    def _save_collection(self):
        """Save current collection to file."""
        if not self.current_collection:
            messagebox.showwarning("Warning", "No collection to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                save_universal_collection_to_json(self.current_collection, file_path)
                messagebox.showinfo("Success", "Collection saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save collection: {str(e)}")

    def _new_collection(self):
        """Create a new collection."""
        collection_name = tk.simpledialog.askstring("New Collection", "Enter collection name:")
        if collection_name:
            # Create new empty collection
            self.current_collection = UniversalCollection(collection_name)
            self._display_collection_info(self.current_collection)
            self.collection_listbox.insert(tk.END, collection_name)

    def _display_collection_info(self, collection):
        """Display information about a collection."""
        info_text = f"Name: {collection.name}\n"
        info_text += f"Games: {', '.join(collection.games)}\n"
        info_text += f"Total Cards: {len(collection.cards)}\n"

        self.collection_info_text.delete(1.0, tk.END)
        self.collection_info_text.insert(1.0, info_text)

    def _cross_game_search(self):
        """Perform cross-game search for variants."""
        card_theme = self.cross_game_var.get().strip()
        if not card_theme:
            messagebox.showwarning("Warning", "Please enter a card theme to search for.")
            return

        self.status_var.set(f"Finding '{card_theme}' variants...")

        try:
            collection = get_cross_game_collection(card_theme, f"{card_theme} Variants")

            if collection.cards:
                self.current_collection = collection
                self._display_collection_info(collection)

                # Switch to collection tab
                self.notebook.select(2)

                messagebox.showinfo("Success", f"Found {len(collection.cards)} variants across {len(collection.games)} games")
            else:
                messagebox.showinfo("No Results", f"No variants found for '{card_theme}'")

        except Exception as e:
            messagebox.showerror("Error", f"Cross-game search failed: {str(e)}")
        finally:
            self.status_var.set("Ready")

    def _generate_popular_collection(self):
        """Generate a collection from popular games."""
        self.status_var.set("Generating popular games collection...")

        try:
            games_cards = get_popular_games_cards()

            all_cards = []
            for game, cards in games_cards.items():
                all_cards.extend(cards[:10])  # 10 cards per game

            if all_cards:
                collection = UniversalCollection("Popular CCGs Mix", all_cards)
                self.current_collection = collection
                self._display_collection_info(collection)

                messagebox.showinfo("Success", f"Generated collection with {len(all_cards)} cards from {len(games_cards)} games")

                # Switch to collection tab
                self.notebook.select(2)
            else:
                messagebox.showinfo("No Results", "No cards found for popular games")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate popular collection: {str(e)}")
        finally:
            self.status_var.set("Ready")

    def _add_game_to_collection(self):
        """Add selected game cards to current collection."""
        selection = self.games_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a game first.")
            return

        if not self.current_collection:
            messagebox.showwarning("Warning", "Please create or load a collection first.")
            return

        game_name = self.games_listbox.get(selection[0])

        try:
            cards = get_game_cards(game_name, 10)  # Get 10 cards

            # This would need proper implementation to add cards to existing collection
            messagebox.showinfo("Info", f"Would add {len(cards)} cards from {game_name} to collection")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get game cards: {str(e)}")

    def get_plugin_info(self):
        """Return information about this plugin."""
        return {
            "name": "Universal CCG Scraper",
            "version": "1.0.0",
            "description": "Scrapes cards from multiple CCGs via CCGTrader.net",
            "author": "Silhouette Card Maker Community"
        }

    def shutdown(self):
        """Called when the plugin is being shut down."""
        # Clean up any resources
        pass
