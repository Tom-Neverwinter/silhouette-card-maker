from os import path
from requests import Response, Session
from time import sleep

from utilities import guess_extension

session = Session()

# Official card list image path; the '/' in a card number becomes '_',
# e.g. UE03BT/JJK-1-001 -> UE03BT_JJK-1-001.png (parallels add a '_p1' suffix).
CARD_ART_URL_TEMPLATE = 'https://www.unionarena-tcg.com/na/images/cardlist/card/{image_id}.png'

OUTPUT_CARD_ART_FILE_TEMPLATE = '{deck_index}{image_id}{quantity_counter}{extension}'

def request_bandai(query: str) -> Response:
    r = session.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def card_image_id(card_number: str) -> str:
    return card_number.replace('/', '_')

def fetch_card(
    index: int,
    quantity: int,
    card_number: str,
    front_img_dir: str,
):
    image_id = card_image_id(card_number)
    response = request_bandai(CARD_ART_URL_TEMPLATE.format(image_id=image_id))

    content_type = response.headers.get('content-type', '')
    if not content_type.startswith('image/'):
        raise ValueError(f'Expected an image for {card_number}, got "{content_type}"')

    card_art = response.content
    extension = guess_extension(card_art)

    # Save image based on quantity
    for counter in range(quantity):
        image_path = path.join(front_img_dir, OUTPUT_CARD_ART_FILE_TEMPLATE.format(deck_index=str(index), image_id=image_id, quantity_counter=str(counter + 1), extension=extension))

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, card_number: str, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            card_number,
            front_img_dir
        )

    return configured_fetch_card
