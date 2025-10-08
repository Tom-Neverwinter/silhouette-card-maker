from os import path
from click import command, argument, Choice

from deck_formats import DeckFormat, parse_deck
from swudb  import get_handle_card

front_directory = path.join('game', 'front')
back_directory = path.join('game', 'back')
double_sided_directory = path.join('game', 'double_sided')

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))

def cli(deck_path: str, format: DeckFormat):
    if not path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()

        parse_deck(deck_text, format, get_handle_card( front_directory, back_directory ))

if __name__ == '__main__':
    cli()