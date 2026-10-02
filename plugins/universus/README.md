# UniVersus Plugin

This plugin reads a decklist, fetches the card images from [universus.cards](https://universus.cards), and puts the card images into the proper `game/` directories.

This plugin supports the `universus_url` and `universus_json` formats. To learn more, see [here](#formats).

The starting character is always included and listed first. Mainboard and sideboard cards are both fetched. Double-sided cards have their back faces put into `game/double_sided/`.

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is universus.cards URL (`universus_url`).

Run the script.

```sh
python plugins/universus/fetch.py game/decklist/deck.txt universus_url
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {universus_url|universus_json}

Options:
  --help  Show this message and exit.
```

## Formats

### `universus_url`

[universus.cards](https://universus.cards) deck URL format. The deck must be public. Each line can contain one deck URL.

```
https://universus.cards/deck/e4c57177-8a10-40e6-9786-0cbf35268bd9
```

You can also use the URL directly in the command line. Note the single quotes around the URL.

```sh
python plugins/universus/fetch.py 'https://universus.cards/deck/e4c57177-8a10-40e6-9786-0cbf35268bd9' universus_url
```

### `universus_json`

[universus.cards](https://universus.cards) deck JSON format, the data returned when opening a deck URL without a browser. Each entry in `cards` is `[card id, mainboard count, sideboard count]`.

```json
{
  "name": "Ives Kailub (Reiner Braun)",
  "format": "Standard",
  "cards": [[10943, 1, 0], [10405, 1, 1], [10897, 3, 0], [11927, 0, 1]],
  "startingCharacter": 10943
}
```
