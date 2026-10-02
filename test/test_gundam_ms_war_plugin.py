"""
Tests for the Gundam M.S. War plugin.
Tests deck format parsing and image fetching from the Gundam M.S. War Fandom wiki.
"""
import os
import shutil
import tempfile
import pytest
from PIL import Image

from plugins.gundam_ms_war.deck_formats import DeckFormat, parse_deck, parse_text
from plugins.gundam_ms_war.mswar_wiki import (
    FILE_NAME_PATTERN,
    get_card_image_index,
    get_handle_card,
    normalize_card_number,
)


def collect(deck_text):
    parsed_cards = []
    parse_text(deck_text, lambda index, card_number, quantity: parsed_cards.append((index, card_number, quantity)))
    return parsed_cards


# --- Unit Tests ---

class TestTextFormat:
    def test_parse_text(self):
        deck_text = """// Wing team
3 MS-001 Wing Gundam
2x PL-001 Heero Yuy
1 bf-p03
Missions: none
4 EV_023 Zero System"""

        assert collect(deck_text) == [
            (1, 'MS-001', 3),
            (2, 'PL-001', 2),
            (3, 'bf-p03', 1),
            (4, 'EV_023', 4),
        ]

    def test_rejects_other_games_numbers(self):
        assert collect("4 GD01-008 Guntank\n4 ST01-001") == []

    def test_parse_deck_dispatch(self):
        parsed_cards = []
        parse_deck("1 MS-025", DeckFormat.TEXT, lambda i, c, q: parsed_cards.append(c))
        assert parsed_cards == ['MS-025']


class TestCardNumbers:
    @pytest.mark.parametrize("raw,expected", [
        ('MS-001', 'MS-001'),
        ('ms_1', 'MS-001'),
        ('EV-23', 'EV-023'),
        ('bf-p3', 'BF-P03'),
        ('PL-P09', 'PL-P09'),
    ])
    def test_normalize(self, raw, expected):
        assert normalize_card_number(raw) == expected

    def test_normalize_invalid(self):
        with pytest.raises(ValueError):
            normalize_card_number('GD01-001')

    @pytest.mark.parametrize("file_name,expected", [
        ('MS_001_Wing_Gundam.jpg', 'MS-001'),
        ('BF_p02_St_louis,_MO.jpg', 'BF-P02'),
        ('PL-P09_Kou_Uraki_promo.jpeg', 'PL-P09'),
        ('Gp_bf-p19-heavyarmscustom.jpg', 'BF-P19'),
        ('Gundam_card_BF-p01_Atlanta,_GA_(Deathscythe).jpg', 'BF-P01'),
        ('1ms_card.jpg', None),
        ('Rulebook_01.jpg', None),
    ])
    def test_file_name_pattern(self, file_name, expected):
        match = FILE_NAME_PATTERN.match(file_name)
        assert (normalize_card_number(match.group(1) + '-' + match.group(2)) if match else None) == expected


# --- Integration Tests for Wiki and Image Fetching ---

@pytest.mark.integration
class TestWiki:
    def test_card_image_index(self):
        index = get_card_image_index()
        for card_number in ['MS-001', 'PL-001', 'EV-001', 'BF-001', 'BF-P01']:
            assert card_number in index


@pytest.mark.integration
class TestFullFetchWorkflow:
    @pytest.fixture
    def front_dir(self):
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_with_quantity(self, front_dir):
        parse_deck("2 MS-001 Wing Gundam", DeckFormat.TEXT, get_handle_card(front_dir))

        files = os.listdir(front_dir)
        assert len(files) == 2
        for f in files:
            with Image.open(os.path.join(front_dir, f)) as image:
                image.verify()
