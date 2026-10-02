"""
Tests for the Union Arena plugin.
Tests deck format parsing and image fetching from the official card list.
"""
import os
import shutil
import tempfile
import pytest
from PIL import Image

from plugins.union_arena.deck_formats import DeckFormat, parse_deck, parse_exburst, parse_text
from plugins.union_arena.union_arena import CARD_ART_URL_TEMPLATE, card_image_id, request_bandai, get_handle_card


def collect(parser, deck_text):
    parsed_cards = []
    parser(deck_text, lambda index, card_number, quantity: parsed_cards.append((index, card_number, quantity)))
    return parsed_cards


# --- Unit Tests for Deck Format Parsing ---

class TestExburstFormat:
    """Test ExBurst format parsing."""

    def test_parse_exburst(self):
        deck_text = """4 x UE03BT/JJK-1-001
2 x UEX02BT/JJK-2-045
1 x UE03BT/JJK-1-005_p1"""

        assert collect(parse_exburst, deck_text) == [
            (1, 'UE03BT/JJK-1-001', 4),
            (2, 'UEX02BT/JJK-2-045', 2),
            (3, 'UE03BT/JJK-1-005_p1', 1),
        ]

    def test_skips_non_card_lines(self):
        deck_text = """Main Deck
4 x UE03BT/JJK-1-001

4 UE03BT/JJK-1-002"""

        assert collect(parse_exburst, deck_text) == [(1, 'UE03BT/JJK-1-001', 4)]


class TestTextFormat:
    """Test plain text format parsing."""

    def test_parse_text(self):
        deck_text = """4 UE03BT/JJK-1-001 Yuji Itadori
3 UE03BT/JJK-1-002"""

        assert collect(parse_text, deck_text) == [
            (1, 'UE03BT/JJK-1-001', 4),
            (2, 'UE03BT/JJK-1-002', 3),
        ]


class TestParseDeck:
    def test_dispatch(self):
        assert collect(lambda t, h: parse_deck(t, DeckFormat.EXBURST, h), '4 x UE03BT/JJK-1-001') == [(1, 'UE03BT/JJK-1-001', 4)]
        assert collect(lambda t, h: parse_deck(t, DeckFormat.TEXT, h), '4 UE03BT/JJK-1-001') == [(1, 'UE03BT/JJK-1-001', 4)]

    def test_card_image_id(self):
        assert card_image_id('UE03BT/JJK-1-005_p1') == 'UE03BT_JJK-1-005_p1'


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestUnionArenaAPI:
    """Test the official Union Arena card image server."""

    def test_image_availability(self):
        response = request_bandai(CARD_ART_URL_TEMPLATE.format(image_id='UE03BT_JJK-1-001'))
        assert response.status_code == 200
        assert response.headers['content-type'].startswith('image/')


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def front_dir(self):
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_with_quantity(self, front_dir):
        parse_deck('2 x UE03BT/JJK-1-001', DeckFormat.EXBURST, get_handle_card(front_dir))

        files = sorted(os.listdir(front_dir))
        assert files == ['1UE03BT_JJK-1-0011.png', '1UE03BT_JJK-1-0012.png']
        for f in files:
            with Image.open(os.path.join(front_dir, f)) as image:
                image.verify()
