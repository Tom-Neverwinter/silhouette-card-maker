from re import compile
from enum import Enum
from typing import Callable, Tuple

card_data_tuple = Tuple[str, str, int] # name, card code, quantity

# Card codes look like FB01-001, FS01-03, or FP-001, optionally with a parallel suffix like _p1
CARD_CODE = r'[A-Z]+\d*-\d+(?:_p\d+)?'

def parse_deck_helper(
        deck_text: str,
        handle_card: Callable,
        is_card_line: Callable[[str], bool],
        extract_card_data: Callable[[str], card_data_tuple],
    ) -> None:
    error_lines = []

    index = 0

    for line in deck_text.strip().split('\n'):
        line = line.strip()
        if is_card_line(line):
            index = index + 1

            name, card_code, quantity = extract_card_data(line)

            parts = [f'Index: {index}', f'quantity: {quantity}', f'card code: {card_code}']
            if name: parts.append(f'name: {name}')
            print(', '.join(parts))
            try:
                handle_card(index, card_code, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))
        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_fusionworld(deck_text: str, handle_card: Callable):
    # '{quantity} {card code}', also accepts '{quantity}x{card code}', '{quantity} x {card code}',
    # and an optional trailing card name
    pattern = compile(rf'^(\d+)\s*[xX]?\s*({CARD_CODE})(?:\s+(.*))?$')

    def is_fusionworld_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_fusionworld_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        quantity = int(match.group(1))
        card_code = match.group(2)
        name = (match.group(3) or '').strip()

        return (name, card_code, quantity)

    parse_deck_helper(deck_text, handle_card, is_fusionworld_line, extract_fusionworld_card_data)

class DeckFormat(str, Enum):
    FUSIONWORLD = 'fusionworld'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable):
    if format == DeckFormat.FUSIONWORLD:
        parse_fusionworld(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')
