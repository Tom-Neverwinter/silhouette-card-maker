from html import unescape
from os import path
from re import compile, sub
from time import sleep
from requests import Response, Session

from utilities import guess_extension

session = Session()

BASE_URL = 'https://universus.cards'
DECK_URL_TEMPLATE = BASE_URL + '/deck/{deck_id}'
CARD_URL_TEMPLATE = BASE_URL + '/card/{card_id}'

IMAGE_SRC_PATTERN = compile(r'src="(/cards/[^"]+\.jpg)"')
TITLE_PATTERN = compile(r'<title>([^<]*)</title>')

def request_universus(query: str, accept: str = '*/*') -> Response:
    r = session.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': accept}, timeout = 30)

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.15)

    return r

def get_universus_deck(deck_id: str) -> dict:
    # The deck page serves its raw JSON when the client does not ask for HTML
    deck = request_universus(DECK_URL_TEMPLATE.format(deck_id = deck_id), 'application/json').json()
    if not deck:
        raise ValueError(f'Deck {deck_id} not found or not public.')

    return deck

def get_card_images(card_id: int):
    """Return (name, front image URL, back image URL or None) scraped from the card page."""
    html = request_universus(CARD_URL_TEMPLATE.format(card_id = card_id), 'text/html').content.decode('utf-8', 'replace')

    sources = IMAGE_SRC_PATTERN.findall(html)
    if not sources:
        raise ValueError(f'No image found for card {card_id}.')

    front = sources[0]
    # Double-sided cards also show their back face, e.g. /cards/aot01/017B.jpg
    back = next((s for s in sources[1:] if s.endswith('B.jpg')), None)

    title = TITLE_PATTERN.search(html)
    # '<title>Reiner Braun · universus.cards</title>'
    name = unescape(title.group(1)).split('·')[0].strip() if title else ''

    return name, BASE_URL + front, BASE_URL + back if back else None

def remove_nonalphanumeric(s: str) -> str:
    return sub(r'[^\w]', '', s)

def request_image(url: str) -> bytes:
    r = request_universus(url, 'image/*')
    content_type = r.headers.get('content-type', '')
    if not content_type.startswith('image/'):
        raise ValueError(f'Expected an image from {url}, got "{content_type}".')

    return r.content

def save_copies(content: bytes, directory: str, base_name: str, quantity: int):
    extension = guess_extension(content, '.jpg')
    for counter in range(quantity):
        with open(path.join(directory, f'{base_name}{counter + 1}{extension}'), 'wb') as f:
            f.write(content)

def fetch_card(index: int, card_id: int, quantity: int, front_img_dir: str, double_sided_dir: str):
    name, front_url, back_url = get_card_images(card_id)
    base_name = f'{index}{remove_nonalphanumeric(name) or card_id}'

    save_copies(request_image(front_url), front_img_dir, base_name, quantity)

    if back_url:
        save_copies(request_image(back_url), double_sided_dir, base_name, quantity)

def get_handle_card(front_img_dir: str, double_sided_dir: str):
    def configured_fetch_card(index: int, card_id: int, quantity: int):
        fetch_card(index, card_id, quantity, front_img_dir, double_sided_dir)

    return configured_fetch_card
