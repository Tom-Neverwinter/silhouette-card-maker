# Star Realms TCG GUI Integration Module
# ========================================
# This module handles integration with the main Silhouette Card Maker GUI

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import List, Dict, Any

# Import our custom modules
from sr_scraper import (
    StarRealmsCard, StarRealmsDeck,
    get_cards_from_official_gallery,
    get_cards_from_boardgamegeek,
    get_cards_from_tier_list,
    create_collection_from_cards,
    save_collection_to_file
)
from sr_api import (
    search_starrealms_cards,
    get_collection_cards,
    process_starrealms_cards_batch,
    save_collection_to_json,
    load_collection_from_json
)

# -----------------------------
# GUI Integration Class
# -----------------------------
class StarRealmsPluginGUI:
    """
    GUI integration class for Star Realms TCG plugin.

    This class provides the interface between the main Silhouette Card Maker
    GUI and the Star Realms plugin functionality.
    """

    def __init__(self, parent_frame, plugin_manager=None):
        """
        Initialize the Star Realms plugin GUI.

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
            text="Star Realms TCG Plugin",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Create notebook for different sections
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create tabs
        self._create_scrape_tab()
        self._create_search_tab()
        self._create_collection_tab()
        self._create_settings_tab()

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

    def _create_scrape_tab(self):
        """Create the scraping tab."""
        scrape_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(scrape_frame, text="Scrape Cards")

        # Source selection
        source_frame = ttk.LabelFrame(scrape_frame, text="Data Source", padding="5")
        source_frame.pack(fill=tk.X, pady=(0, 10))

        self.scrape_source = tk.StringVar(value="official")
        sources = [
            ("Official Gallery", "official"),
            ("BoardGameGeek", "boardgamegeek"),
            ("Tier Lists", "tierlist"),
            ("All Sources", "all")
        ]

        for text, value in sources:
            rb = ttk.Radiobutton(
                source_frame,
                text=text,
                variable=self.scrape_source,
                value=value
            )
            rb.pack(anchor=tk.W)

        # Options frame
        options_frame = ttk.LabelFrame(scrape_frame, text="Options", padding="5")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # Max cards
        max_frame = ttk.Frame(options_frame)
        max_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(max_frame, text="Max Cards:").pack(side=tk.LEFT)
        self.max_cards_var = tk.StringVar(value="50")
        max_entry = ttk.Entry(max_frame, textvariable=self.max_cards_var, width=10)
        max_entry.pack(side=tk.RIGHT)

        # Card type filter
        type_frame = ttk.Frame(options_frame)
        type_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(type_frame, text="Card Type:").pack(side=tk.LEFT)
        self.card_type_var = tk.StringVar(value="all")
        type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.card_type_var,
            values=["all", "ship", "base", "outpost"],
            state="readonly",
            width=15
        )
        type_combo.pack(side=tk.RIGHT)

        # Collection name
        collection_frame = ttk.Frame(options_frame)
        collection_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(collection_frame, text="Collection Name:").pack(side=tk.LEFT)
        self.collection_name_var = tk.StringVar(value="")
        collection_entry = ttk.Entry(collection_frame, textvariable=self.collection_name_var)
        collection_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Buttons frame
        buttons_frame = ttk.Frame(scrape_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        self.scrape_btn = ttk.Button(
            buttons_frame,
            text="Start Scraping",
            command=self._start_scraping
        )
        self.scrape_btn.pack(side=tk.LEFT)

        ttk.Button(
            buttons_frame,
            text="Stop",
            command=self._stop_scraping
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Progress bar
        self.scrape_progress = ttk.Progressbar(scrape_frame, mode='indeterminate')
        self.scrape_progress.pack(fill=tk.X, pady=(10, 0))

        # Results text area
        results_frame = ttk.LabelFrame(scrape_frame, text="Results", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.scrape_results = tk.Text(results_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.scrape_results.yview)
        self.scrape_results.configure(yscrollcommand=scrollbar.set)

        self.scrape_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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

        # Search results
        results_frame = ttk.LabelFrame(search_frame, text="Search Results", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview for results
        columns = ("name", "type", "faction", "cost", "attack", "defense")
        self.search_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=10
        )

        # Define column headings
        self.search_tree.heading("name", text="Card Name")
        self.search_tree.heading("type", text="Type")
        self.search_tree.heading("faction", text="Faction")
        self.search_tree.heading("cost", text="Cost")
        self.search_tree.heading("attack", text="Attack")
        self.search_tree.heading("defense", text="Defense")

        # Set column widths
        self.search_tree.column("name", width=150)
        self.search_tree.column("type", width=80)
        self.search_tree.column("faction", width=120)
        self.search_tree.column("cost", width=50)
        self.search_tree.column("attack", width=50)
        self.search_tree.column("defense", width=60)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)

        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons for search results
        btn_frame = ttk.Frame(search_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Fetch Images",
            command=self._fetch_search_images
        ).pack(side=tk.LEFT)

        ttk.Button(
            btn_frame,
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

    def _create_settings_tab(self):
        """Create the settings tab."""
        settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(settings_frame, text="Settings")

        # Output directories
        output_frame = ttk.LabelFrame(settings_frame, text="Output Directories", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 10))

        # Card images directory
        img_dir_frame = ttk.Frame(output_frame)
        img_dir_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(img_dir_frame, text="Card Images:").pack(side=tk.LEFT)
        self.images_dir_var = tk.StringVar(value="game/front")
        images_entry = ttk.Entry(img_dir_frame, textvariable=self.images_dir_var)
        images_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        ttk.Button(
            img_dir_frame,
            text="Browse...",
            command=lambda: self._browse_directory(self.images_dir_var)
        ).pack(side=tk.RIGHT)

        # Deck lists directory
        deck_dir_frame = ttk.Frame(output_frame)
        deck_dir_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(deck_dir_frame, text="Deck Lists:").pack(side=tk.LEFT)
        self.decks_dir_var = tk.StringVar(value="game/decklist")
        decks_entry = ttk.Entry(deck_dir_frame, textvariable=self.decks_dir_var)
        decks_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        ttk.Button(
            deck_dir_frame,
            text="Browse...",
            command=lambda: self._browse_directory(self.decks_dir_var)
        ).pack(side=tk.RIGHT)

        # Scraping options
        scraping_frame = ttk.LabelFrame(settings_frame, text="Scraping Options", padding="5")
        scraping_frame.pack(fill=tk.X, pady=(0, 10))

        self.fetch_images_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            scraping_frame,
            text="Automatically fetch card images",
            variable=self.fetch_images_var
        ).pack(anchor=tk.W)

        self.save_collections_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            scraping_frame,
            text="Automatically save collections as JSON",
            variable=self.save_collections_var
        ).pack(anchor=tk.W)

        # Save settings button
        ttk.Button(
            settings_frame,
            text="Save Settings",
            command=self._save_settings
        ).pack(pady=(20, 0))

    def _browse_directory(self, var):
        """Browse for a directory."""
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)

    def _start_scraping(self):
        """Start the scraping process."""
        self.scrape_btn.config(state=tk.DISABLED)
        self.scrape_progress.start()
        self.status_var.set("Scraping cards...")

        # Run scraping in a separate thread
        thread = threading.Thread(target=self._run_scraping)
        thread.daemon = True
        thread.start()

    def _run_scraping(self):
        """Run the scraping process in a thread."""
        try:
            source = self.scrape_source.get()
            max_cards = int(self.max_cards_var.get())
            card_type = self.card_type_var.get()
            collection_name = self.collection_name_var.get()

            self._append_to_results(f"Starting scrape from {source} (max {max_cards} cards)...\n")

            all_cards = []

            if source == 'official' or source == 'all':
                self._append_to_results("Fetching from official gallery...\n")
                official_cards = get_cards_from_official_gallery(card_type, max_cards)
                all_cards.extend(official_cards)
                self._append_to_results(f"Found {len(official_cards)} cards from official gallery\n")

            if source == 'boardgamegeek' or source == 'all':
                self._append_to_results("Fetching from BoardGameGeek...\n")
                bgg_cards = get_cards_from_boardgamegeek(card_type, max_cards)
                all_cards.extend(bgg_cards)
                self._append_to_results(f"Found {len(bgg_cards)} cards from BoardGameGeek\n")

            if source == 'tierlist' or source == 'all':
                self._append_to_results("Fetching from tier lists...\n")
                tier_cards = get_cards_from_tier_list(card_type, max_cards)
                all_cards.extend(tier_cards)
                self._append_to_results(f"Found {len(tier_cards)} cards from tier lists\n")

            self.current_cards = all_cards

            if all_cards:
                self._append_to_results(f"\nTotal cards scraped: {len(all_cards)}\n")

                if collection_name:
                    collection = create_collection_from_cards(all_cards, collection_name)
                    self.current_collection = collection
                    save_collection_to_file(collection, f"game/decklist/{collection_name.replace(' ', '_')}.txt")
                    self._append_to_results(f"Saved collection '{collection_name}'\n")

                if self.fetch_images_var.get():
                    self._append_to_results(f"Fetching images to {self.images_dir_var.get()}...\n")
                    processed = process_starrealms_cards_batch(all_cards, self.images_dir_var.get())
                    self._append_to_results(f"Processed {processed} card images\n")
            else:
                self._append_to_results("No cards found from any source.\n")

        except Exception as e:
            self._append_to_results(f"Error during scraping: {str(e)}\n")
        finally:
            self._scraping_complete()

    def _scraping_complete(self):
        """Called when scraping is complete."""
        self.scrape_btn.config(state=tk.NORMAL)
        self.scrape_progress.stop()
        self.status_var.set("Ready")

    def _append_to_results(self, text):
        """Append text to the results area."""
        self.scrape_results.insert(tk.END, text)
        self.scrape_results.see(tk.END)

    def _stop_scraping(self):
        """Stop the scraping process."""
        # This would need to be implemented with proper thread management
        self._append_to_results("Scraping stopped by user.\n")
        self._scraping_complete()

    def _search_cards(self):
        """Search for cards by name."""
        card_name = self.search_var.get().strip()
        if not card_name:
            messagebox.showwarning("Warning", "Please enter a card name to search for.")
            return

        self.status_var.set(f"Searching for '{card_name}'...")

        # Clear previous results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        try:
            cards = search_starrealms_cards(card_name)

            if cards:
                for card in cards:
                    self.search_tree.insert("", tk.END, values=(
                        card.name,
                        card.card_type,
                        card.faction,
                        card.cost,
                        card.attack,
                        card.defense
                    ))
            else:
                messagebox.showinfo("No Results", f"No cards found matching '{card_name}'")

        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
        finally:
            self.status_var.set("Ready")

    def _fetch_search_images(self):
        """Fetch images for selected cards in search results."""
        selection = self.search_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select cards to fetch images for.")
            return

        # Get selected cards
        selected_cards = []
        for item in selection:
            values = self.search_tree.item(item, "values")
            # Find the corresponding card object (simplified - would need better mapping)
            card = StarRealmsCard(
                name=values[0],
                card_type=values[1],
                faction=values[2],
                cost=int(values[3]),
                attack=int(values[4]),
                defense=int(values[5]),
                ability="",
                set_code="CORE",
                rarity="Common",
                image_url=f"https://example.com/cards/{values[0].replace(' ', '_')}.png"
            )
            selected_cards.append(card)

        if selected_cards:
            processed = process_starrealms_cards_batch(selected_cards, self.images_dir_var.get())
            messagebox.showinfo("Complete", f"Processed {processed} card images")

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
                    collection = load_collection_from_json(file_path)
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
                save_collection_to_json(self.current_collection, file_path)
                messagebox.showinfo("Success", "Collection saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save collection: {str(e)}")

    def _new_collection(self):
        """Create a new collection."""
        collection_name = self.collection_name_var.get().strip()
        if not collection_name:
            messagebox.showwarning("Warning", "Please enter a collection name.")
            return

        # Create new empty collection
        self.current_collection = StarRealmsDeck(
            name=collection_name,
            cards=[],
            player="Current User",
            id=f"collection_{hash(collection_name) % 10000}"
        )

        self._display_collection_info(self.current_collection)
        self.collection_listbox.insert(tk.END, collection_name)

    def _display_collection_info(self, collection):
        """Display information about a collection."""
        info_text = f"Name: {collection.name}\n"
        info_text += f"Player: {collection.player}\n"
        info_text += f"ID: {collection.id}\n"
        info_text += f"Cards: {len(collection.cards)}\n"
        info_text += f"Hash: {collection.hash}\n"

        self.collection_info_text.delete(1.0, tk.END)
        self.collection_info_text.insert(1.0, info_text)

    def _save_settings(self):
        """Save current settings."""
        # This would save settings to a configuration file
        messagebox.showinfo("Settings", "Settings saved successfully.")

    def get_plugin_info(self):
        """Return information about this plugin."""
        return {
            "name": "Star Realms TCG",
            "version": "1.0.0",
            "description": "Plugin for Star Realms Trading Card Game deck scraping and management",
            "author": "Silhouette Card Maker Community"
        }

    def shutdown(self):
        """Called when the plugin is being shut down."""
        # Clean up any resources
        pass
