# Dragon Ball Super Card Game Fusion World Plugin

This plugin reads a decklist, fetches the card images from the [official card list](https://www.dbs-cardgame.com/fw/en/cardlist/), and puts the card images into the proper `game/` directories.

Leader cards are double-sided, so their back (awakened) side is put into `game/double_sided/`.

This plugin supports the `fusionworld` decklist format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is `fusionworld`.

Run the script.

```sh
python plugins/dragon_ball_super_fusion_world/fetch.py game/decklist/deck.txt fusionworld
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {fusionworld}

Options:
  --help  Show this message and exit.
```

## Formats

### `fusionworld`

The deck code text copied from **Fusion World Digital** (the **Deck Code** button on the **Check Deck** screen), which is also the format used for [Limitless TCG](https://docs.limitlesstcg.com/player/decklists) decklist submissions.

```
1 FB01-001
4 FS01-03
4 FB01-005
3 FS01-04
4 FB01-014
```

Each line is a quantity followed by a card number. The quantity may also be written with an `x` (`4xFB01-005` or `4 x FB01-005`), and any text after the card number (such as the card name) is ignored. Lines that don't match, such as section headers, are skipped.

To use a parallel (alternate art) printing, add its suffix to the card number, such as `FB01-004_p1`.
