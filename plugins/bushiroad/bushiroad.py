from os import path
from io import BytesIO
from requests import Response, Session
from time import sleep
from PIL import Image
from re import sub
from unicodedata import normalize, category
from enum import Enum

# Deck Log host: 'decklog-en' (English) or 'decklog' (Japanese).
# The same deck code refers to different decks on each host.
DEFAULT_HOST = 'decklog-en'
DECK_API_URL = 'https://{host}.bushiroad.com/system/app/api/view/{deck_code}'

session = Session()

class GameTitle(str, Enum):
    CARDFIGHT_VANGUARD = 'Cardfight Vanguard'
    WEISS_SCHWARZ = 'Weiss Schwarz'
    SHADOWVERSE_EVOLVE = 'Shadowverse: Evolve'
    GODZILLA = 'Godzilla'
    HOLOLIVE = 'Hololive'
    BUDDYFIGHT = 'Future Card Buddyfight'
    REBIRTH = 'Rebirth for you'
    DREAM_ORDER = 'Dream Order'
    LOVE_LIVE = 'Love Live'
    WEISS_SCHWARZ_ROSE = 'Weiss Schwarz Rose'
    PALWORLD = 'Palworld'

# Game title IDs and image hosts differ between the English and Japanese Deck Log
# (see https://decklog-en.bushiroad.com/conf/const.js and https://decklog.bushiroad.com/conf/const.js)
game_title_id_mapping = {
    'decklog-en': {
        '1': GameTitle.CARDFIGHT_VANGUARD,
        '2': GameTitle.WEISS_SCHWARZ,
        '6': GameTitle.SHADOWVERSE_EVOLVE,
        '7': GameTitle.GODZILLA,
        '8': GameTitle.HOLOLIVE,
        '9': GameTitle.PALWORLD,
    },
    'decklog': {
        '1': GameTitle.CARDFIGHT_VANGUARD,
        '2': GameTitle.WEISS_SCHWARZ,
        '3': GameTitle.BUDDYFIGHT,
        '5': GameTitle.REBIRTH,
        '6': GameTitle.SHADOWVERSE_EVOLVE,
        '8': GameTitle.DREAM_ORDER,
        '9': GameTitle.HOLOLIVE,
        '11': GameTitle.LOVE_LIVE,
        '12': GameTitle.WEISS_SCHWARZ_ROSE,
        '13': GameTitle.GODZILLA,
        '14': GameTitle.PALWORLD,
    },
}

game_image_url_mapping = {
    'decklog-en': {
        GameTitle.CARDFIGHT_VANGUARD: 'https://en.cf-vanguard.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.WEISS_SCHWARZ: 'https://en.ws-tcg.com/wordpress/wp-content/images/cardimages/{card_image}',
        GameTitle.SHADOWVERSE_EVOLVE: 'https://en.shadowverse-evolve.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.GODZILLA: 'https://en.godzilla-cardgame.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.HOLOLIVE: 'https://en.hololive-official-cardgame.com/wp-content/images/cardlist/{card_image}',
        GameTitle.PALWORLD: 'https://en.palworld-official-cardgame.com/wordpress/wp-content/images/cardlist/{card_image}',
    },
    'decklog': {
        GameTitle.CARDFIGHT_VANGUARD: 'https://cf-vanguard.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.WEISS_SCHWARZ: 'https://ws-tcg.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.SHADOWVERSE_EVOLVE: 'https://shadowverse-evolve.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.GODZILLA: 'https://godzilla-cardgame.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.HOLOLIVE: 'https://hololive-official-cardgame.com/wp-content/images/cardlist/{card_image}',
        GameTitle.BUDDYFIGHT: 'https://fc-buddyfight.com/wordpress/wp-content/images/card/{card_image}',
        GameTitle.REBIRTH: 'https://rebirth-fy.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.DREAM_ORDER: 'https://dreamorder.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.LOVE_LIVE: 'https://llofficial-cardgame.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.WEISS_SCHWARZ_ROSE: 'https://ws-rose.com/wordpress/wp-content/images/cardlist/{card_image}',
        GameTitle.PALWORLD: 'https://palworld-official-cardgame.com/wordpress/wp-content/images/cardlist/{card_image}',
    },
}

def request_bushiroad(query: str, referer: str = '') -> Response:
    if referer == '':
        r = session.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})
    else:
        r = session.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*', 'referer': referer})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def resolve_image_url(game_title: GameTitle, card_image: str, host: str = DEFAULT_HOST) -> str:
    image_url_template = game_image_url_mapping.get(host, {}).get(game_title)
    if image_url_template is None:
        raise ValueError(f'Unsupported game title: {game_title}')
    return image_url_template.format(card_image=card_image)

def fetch_decklist(deck_code: str, host: str = DEFAULT_HOST):
    if host not in game_title_id_mapping:
        raise ValueError(f'Unsupported Deck Log host: {host}')

    deck_request = request_bushiroad(DECK_API_URL.format(host=host, deck_code=deck_code), f'https://{host}.bushiroad.com/')
    json = deck_request.json()

    game_title_id = str(json.get('game_title_id'))
    game_title = game_title_id_mapping[host].get(game_title_id)
    if game_title is None:
        raise ValueError(f'Unsupported game title ID: {game_title_id}')

    main_deck = json.get('list') or []
    leader = json.get('p_list') or []
    evolve_deck = json.get('sub_list') or []
    deck = leader + main_deck + evolve_deck

    return (game_title, deck)

def prepare_card_image(card_art: bytes) -> Image.Image:
    img = Image.open(BytesIO(card_art))
    if img.height < img.width:
        img = img.rotate(-90, expand=True)
    return img

def fetch_card(
    index: int,
    quantity: int,
    name: str,
    front_url: str,
    back_url: str,
    front_img_dir: str,
    back_img_dir: str
):
    sanitized_name = sub(r'[^A-Za-z0-9 \-]+', '', ''.join(c for c in normalize('NFD', name) if category(c) != 'Mn'))

    if front_url:
        front_img = prepare_card_image(request_bushiroad(front_url).content)

        for counter in range(quantity):
            front_image_path = path.join(front_img_dir, f'{str(index)}{sanitized_name}{str(counter + 1)}.png')
            front_img.save(front_image_path)

    if back_url:
        back_img = prepare_card_image(request_bushiroad(back_url).content)

        for counter in range(quantity):
            back_image_path = path.join(back_img_dir, f'{str(index)}{sanitized_name}{str(counter + 1)}.png')
            back_img.save(back_image_path)

def get_handle_card(
    front_img_dir: str,
    back_img_dir: str
):
    def configured_fetch_card(index: int, name: str, front_url: str, back_url: str, quantity = 1):
        fetch_card(
            index,
            quantity,
            name,
            front_url,
            back_url,
            front_img_dir,
            back_img_dir
        )

    return configured_fetch_card
