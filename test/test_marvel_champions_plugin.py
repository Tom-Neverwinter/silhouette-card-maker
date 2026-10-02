"""
Tests for the Marvel Champions: The Card Game plugin.
Tests deck format parsing and image fetching from MarvelCDB.
"""
import json
import os
import shutil
import tempfile
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
import requests
from PIL import Image

from plugins.marvel_champions import api
from plugins.marvel_champions.deck_formats import DeckFormat, DECK_URL_PATTERN, handle_slots, parse_deck
from plugins.marvel_champions.api import fetch_card_json, fetch_marvelcdb_deck, get_handle_card


# --- Unit Tests ---

class TestDeckFormatEnum:
    """Test the DeckFormat enum values."""

    def test_marvelcdb_json_format_value(self):
        assert DeckFormat.MARVELCDB_JSON.value == 'marvelcdb_json'

    def test_marvelcdb_url_format_value(self):
        assert DeckFormat.MARVELCDB_URL.value == 'marvelcdb_url'


class TestDeckURLPattern:
    """Test MarvelCDB deck URL pattern matching."""

    def test_deck_url_matches(self):
        match = DECK_URL_PATTERN.match("https://marvelcdb.com/deck/view/12345")
        assert match is not None
        assert match.group(1) == "deck"
        assert match.group(2) == "12345"

    def test_decklist_url_with_slug_matches(self):
        match = DECK_URL_PATTERN.match("https://marvelcdb.com/decklist/view/67432/ant-rapment-1.0")
        assert match is not None
        assert match.group(1) == "decklist"
        assert match.group(2) == "67432"

    def test_rejects_invalid_urls(self):
        assert not DECK_URL_PATTERN.match("")
        assert not DECK_URL_PATTERN.match("12345")
        assert not DECK_URL_PATTERN.match("https://arkhamdb.com/deck/view/12345")
        assert not DECK_URL_PATTERN.match("https://marvelcdb.com/card/01001a")


class TestHandleSlots:
    """Test slot/hero expansion into handle_card calls."""

    def test_hero_and_slots_are_all_handled(self):
        data = {"hero_code": "01001a", "slots": {"01002": 1, "01074": 2}}

        seen = []
        handle_slots(data, lambda index, code, quantity: seen.append((code, quantity)))

        assert dict(seen) == {"01001a": 1, "01002": 1, "01074": 2}
        assert len(seen) == 3

    def test_missing_hero_code_is_skipped(self):
        seen = []
        handle_slots({"slots": {"01002": 1}}, lambda index, code, quantity: seen.append((code, quantity)))

        assert seen == [("01002", 1)]

    def test_errors_from_handle_card_are_collected_not_raised(self):
        def failing_handle_card(index, code, quantity):
            if code == "01002":
                raise ValueError("boom")

        handle_slots({"slots": {"01002": 1, "01003": 1}}, failing_handle_card)


class TestParseDeck:
    """Test format dispatch (no network)."""

    def test_parse_deck_dispatches_to_json_parser(self):
        deck_text = json.dumps({"hero_code": "01001a", "slots": {"01002": 1}})

        seen = []
        parse_deck(deck_text, DeckFormat.MARVELCDB_JSON, lambda index, code, quantity: seen.append(code))

        assert seen == ["01002", "01001a"]

    def test_url_parser_fetches_decklist(self):
        with patch("plugins.marvel_champions.deck_formats.fetch_marvelcdb_deck",
                   return_value={"hero_code": "01040a", "slots": {"01041": 1}}) as mock_fetch:
            seen = []
            parse_deck("https://marvelcdb.com/decklist/view/1/starter-1.0", DeckFormat.MARVELCDB_URL,
                       lambda index, code, quantity: seen.append(code))

        mock_fetch.assert_called_once_with("1", True)
        assert seen == ["01041", "01040a"]

    def test_invalid_url_does_not_fetch(self):
        with patch("plugins.marvel_champions.deck_formats.fetch_marvelcdb_deck") as mock_fetch:
            parse_deck("https://example.com/deck/view/1", DeckFormat.MARVELCDB_URL, lambda *args: None)

        mock_fetch.assert_not_called()

    def test_unrecognized_format_raises(self):
        with pytest.raises(ValueError):
            parse_deck("{}", "not_a_real_format", lambda *args: None)


def _png_bytes(width, height):
    buf = BytesIO()
    Image.new("RGB", (width, height)).save(buf, format="PNG")
    return buf.getvalue()


class TestFetchCardArt:
    """Test fetch_card_art with mocked MarvelCDB responses."""

    def _run(self, tmp_path, card, image_bytes):
        front_dir = tmp_path / "front"
        double_sided_dir = tmp_path / "double_sided"
        front_dir.mkdir()
        double_sided_dir.mkdir()

        with patch.object(api, "fetch_card_json", return_value=card), \
             patch.object(api, "request_marvelcdb") as mock_request:
            mock_request.return_value = MagicMock(content=image_bytes)
            api.fetch_card_art(3, card["code"], 2, str(front_dir), str(double_sided_dir))

        return sorted(os.listdir(front_dir)), sorted(os.listdir(double_sided_dir)), front_dir

    def test_hero_back_comes_from_linked_card(self, tmp_path):
        card = {
            "code": "01001a",
            "name": "Spider-Man",
            "imagesrc": "/bundles/cards/01001a.png",
            "linked_to_code": "01001b",
            "linked_card": {"imagesrc": "/bundles/cards/01001b.png"},
        }
        front, back, _ = self._run(tmp_path, card, _png_bytes(30, 40))

        assert front == ["3SpiderMan1.png", "3SpiderMan2.png"]
        assert back == front

    def test_landscape_card_is_rotated(self, tmp_path):
        card = {"code": "01097", "name": "The Break-In!", "imagesrc": "/bundles/cards/01097.png"}
        front, back, front_dir = self._run(tmp_path, card, _png_bytes(40, 30))

        assert back == []
        with Image.open(front_dir / front[0]) as img:
            assert img.height > img.width

    def test_warns_when_double_sided_but_no_back(self, tmp_path, capsys):
        card = {"code": "99001", "name": "New Scheme", "imagesrc": "/x.png", "double_sided": True}
        _, back, _ = self._run(tmp_path, card, _png_bytes(30, 40))

        assert back == []
        assert "no back image available yet" in capsys.readouterr().out.lower()

    def test_missing_image_raises(self, tmp_path):
        with pytest.raises(ValueError):
            self._run(tmp_path, {"code": "99002", "name": "Ghost"}, b"")


# --- Integration Tests ---

@pytest.mark.integration
class TestMarvelCDBAPI:
    """Test MarvelCDB public API requests."""

    def test_hero_card_links_to_alter_ego(self):
        card = fetch_card_json("01001a")
        assert card.get("imagesrc")
        assert card.get("linked_to_code") == "01001b"
        assert card.get("linked_card", {}).get("imagesrc")

    def test_main_scheme_has_back_image(self):
        card = fetch_card_json("01097")
        assert card.get("double_sided") is True
        assert card.get("backimagesrc")

    def test_private_deck_url_is_not_reachable(self):
        # Private decks redirect to the login page rather than returning an
        # HTTP error, so the JSON parse itself is what fails. The login page is
        # occasionally slow/flaky and errors instead, which is also fine here.
        with pytest.raises((json.JSONDecodeError, requests.HTTPError)):
            fetch_marvelcdb_deck("99999999", is_decklist=False)


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

    def test_fetch_deck_from_marvelcdb_json(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs

        deck_text = json.dumps({"hero_code": "01001a", "slots": {"01002": 1, "01074": 2}})
        parse_deck(deck_text, DeckFormat.MARVELCDB_JSON, get_handle_card(front_dir, double_sided_dir))

        # 01002 (1) + 01074 (2 copies) + hero (1) = 4 front images
        assert len(os.listdir(front_dir)) == 4
        # The hero's alter-ego back.
        assert len(os.listdir(double_sided_dir)) == 1

    def test_fetch_deck_from_marvelcdb_decklist_url(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs

        parse_deck("https://marvelcdb.com/decklist/view/1", DeckFormat.MARVELCDB_URL,
                   get_handle_card(front_dir, double_sided_dir))

        front_files = os.listdir(front_dir)
        assert len(front_files) >= 40
        for f in front_files:
            with Image.open(os.path.join(front_dir, f)) as img:
                img.verify()
        assert len(os.listdir(double_sided_dir)) >= 1

    def test_fetch_deck_from_marvelcdb_personal_deck_url(self, temp_dirs):
        """Personal deck URL (/deck/view/<id>) with public sharing enabled."""
        front_dir, double_sided_dir = temp_dirs

        parse_deck("https://marvelcdb.com/deck/view/1", DeckFormat.MARVELCDB_URL,
                   get_handle_card(front_dir, double_sided_dir))

        assert len(os.listdir(front_dir)) >= 1
        assert len(os.listdir(double_sided_dir)) >= 1

    def test_landscape_main_scheme_is_rotated_to_portrait(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs

        get_handle_card(front_dir, double_sided_dir)(1, "01097", 1)

        for directory in (front_dir, double_sided_dir):
            files = os.listdir(directory)
            assert len(files) == 1
            with Image.open(os.path.join(directory, files[0])) as img:
                assert img.height > img.width
