import os
from io import BytesIO
from re import sub
from time import sleep

import requests
from PIL import Image

from utilities import guess_extension

API_BASE = 'https://marvelcdb.com/api/public'
IMAGE_URL_TEMPLATE = 'https://marvelcdb.com{image_path}'

session = requests.Session()

def request_marvelcdb(query: str) -> requests.Response:
    r = session.get(query, headers={'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def fetch_marvelcdb_deck(deck_id: str, is_decklist: bool) -> dict:
    key = 'decklist' if is_decklist else 'deck'
    return request_marvelcdb(f'{API_BASE}/{key}/{deck_id}.json').json()

def fetch_card_json(code: str) -> dict:
    return request_marvelcdb(f'{API_BASE}/card/{code}.json').json()

def remove_nonalphanumeric(s: str) -> str:
    return sub(r'[^\w]', '', s)

def fetch_card_image(image_path: str) -> tuple[Image.Image, str]:
    image_bytes = request_marvelcdb(IMAGE_URL_TEMPLATE.format(image_path=image_path)).content
    img = Image.open(BytesIO(image_bytes))

    # Main schemes and some side schemes are printed landscape but need to be
    # laid out portrait alongside the rest of the deck.
    if img.width > img.height:
        img = img.rotate(-90, expand=True)

    return img, guess_extension(image_bytes)

def fetch_card_art(
    index: int,
    code: str,
    quantity: int,
    front_img_dir: str,
    double_sided_dir: str,
) -> None:
    card = fetch_card_json(code)

    name = card.get('name') or code
    clean_name = remove_nonalphanumeric(name)

    print(f'Index: {index}, quantity: {quantity}, code: {code}, name: {name}')

    front_path = card.get('imagesrc')
    if not front_path:
        raise ValueError(f'No image available for card "{code}"')

    front_img, front_ext = fetch_card_image(front_path)
    for counter in range(quantity):
        front_img.save(os.path.join(front_img_dir, f'{index}{clean_name}{counter + 1}{front_ext}'))

    # Double-sided cards either carry their own back image (main schemes,
    # some villains) or link out to a separate card entry that holds it
    # (hero/alter-ego identities via linked_to_code).
    back_path = card.get('backimagesrc')
    if not back_path:
        linked_card = card.get('linked_card')
        if linked_card:
            back_path = linked_card.get('imagesrc')

    if back_path:
        back_img, back_ext = fetch_card_image(back_path)
        for counter in range(quantity):
            back_img.save(os.path.join(double_sided_dir, f'{index}{clean_name}{counter + 1}{back_ext}'))
    elif card.get('double_sided') or card.get('linked_to_code'):
        print(f'Warning: "{name}" ({code}) is double-sided but has no back image available yet.')

def get_handle_card(front_img_dir: str, double_sided_dir: str):
    def configured_fetch_card(index: int, code: str, quantity: int):
        fetch_card_art(
            index,
            code,
            quantity,
            front_img_dir,
            double_sided_dir,
        )

    return configured_fetch_card
