"""
Tests for the UniVersus plugin.
Tests deck format parsing and image fetching from universus.cards.
"""
import json
import os
import shutil
import tempfile
import pytest
from PIL import Image

from plugins.universus.deck_formats import (
    DeckFormat,
    parse_deck,
    parse_universus_json,
    parse_universus_url,
    extract_universus_cards,
)
from plugins.universus.universus import get_card_images, get_universus_deck, get_handle_card


DECK_ID = 'e4c57177-8a10-40e6-9786-0cbf35268bd9'

# Trimmed deck JSON as served by https://universus.cards/deck/{id}
DECK_JSON = json.dumps({
    '_id': DECK_ID,
    'name': 'Ives Kailub (Reiner Braun)',
    'format': 'Standard',
    'cards': [[10405, 1, 1], [10943, 1, 0], [10897, 3, 0], [11927, 0, 1]],
    'maybeboard': [],
    'startingCharacter': 10943,
})


def collect(parsed_cards):
    def collect_card(index, card_id, quantity):
        parsed_cards.append({'index': index, 'card_id': card_id, 'quantity': quantity})
    return collect_card


# --- Unit Tests for Deck Format Parsing ---

class TestUniversusJsonFormat:
    """Test universus.cards deck JSON parsing."""

    def test_parse_universus_json(self):
        parsed_cards = []
        parse_universus_json(DECK_JSON, collect(parsed_cards))

        assert [(c['card_id'], c['quantity']) for c in parsed_cards] == [
            (10943, 1),  # starting character first
            (10405, 2),  # mainboard + sideboard
            (10897, 3),
            (11927, 1),  # sideboard only
        ]
        assert [c['index'] for c in parsed_cards] == [1, 2, 3, 4]

    def test_starting_character_added_when_missing(self):
        deck = {'cards': [[10897, 3, 0]], 'startingCharacter': 10943}
        assert extract_universus_cards(deck) == [(10943, 1), (10897, 3)]

    def test_parse_deck_dispatch(self):
        parsed_cards = []
        parse_deck(DECK_JSON, DeckFormat.UNIVERSUS_JSON, collect(parsed_cards))
        assert len(parsed_cards) == 4


class TestUniversusUrlFormat:
    """Test universus.cards deck URL parsing without network access."""

    def test_parse_universus_url(self, monkeypatch):
        requested = []
        def fake_get_deck(deck_id):
            requested.append(deck_id)
            return json.loads(DECK_JSON)
        monkeypatch.setattr('plugins.universus.deck_formats.get_universus_deck', fake_get_deck)

        parsed_cards = []
        parse_universus_url(f'https://universus.cards/deck/{DECK_ID}\nnot a url', collect(parsed_cards))

        assert requested == [DECK_ID]
        assert parsed_cards[0]['card_id'] == 10943
        assert len(parsed_cards) == 4


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestUniversusAPI:
    """Test universus.cards requests."""

    def test_get_deck(self):
        deck = get_universus_deck(DECK_ID)
        assert deck['startingCharacter'] == 10943
        assert len(deck['cards']) > 0

    def test_get_card_images_double_sided(self):
        name, front, back = get_card_images(10943)
        assert name == 'Reiner Braun'
        assert front.endswith('/cards/aot01/017.jpg')
        assert back.endswith('/cards/aot01/017B.jpg')


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        front_dir = tempfile.mkdtemp()
        double_sided_dir = tempfile.mkdtemp()
        yield front_dir, double_sided_dir
        shutil.rmtree(front_dir)
        shutil.rmtree(double_sided_dir)

    def test_fetch_double_sided_with_quantity(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs

        deck_text = json.dumps({'cards': [[10405, 1, 1]], 'startingCharacter': 10943})
        parse_deck(deck_text, DeckFormat.UNIVERSUS_JSON, get_handle_card(front_dir, double_sided_dir))

        assert sorted(os.listdir(front_dir)) == ['1ReinerBraun1.jpg', '2GenkaisGuidance1.jpg', '2GenkaisGuidance2.jpg']
        assert os.listdir(double_sided_dir) == ['1ReinerBraun1.jpg']

        for directory in temp_dirs:
            for f in os.listdir(directory):
                with Image.open(os.path.join(directory, f)) as img:
                    img.verify()
