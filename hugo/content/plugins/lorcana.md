---
title: 'Lorcana'
weight: 70
---

This plugin reads a decklist, automatically fetches card art from [Lorcast](https://lorcast.com) and puts them in the proper `game/` directories.

This plugin supports decklist exports from [Dreamborn.ink](https://dreamborn.ink). To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is Dreamborn (`dreamborn`).

Run the script.

```shell
python plugins/lorcana/fetch.py game/decklist/deck.txt dreamborn
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {dreamborn}

Options:
  --help  Show this message and exit.
```

## Formats

### `dreamborn`

Dreamborn format.

```
1 Elsa, Spirit of Winter
4 Magic Broom, Illuminary Keeper
4 Diablo - Obedient Raven
4 Mr. Smee, Bumbling Mate
1 Anna - True-Hearted *E*
4 Pete - Games Referee
4 Merlin, Goat
```

#### Enchanted Artwork

Dreamborn does not natively have a way to select the Enchanted artwork for cards.

You can select the Enchanted artwork by adding `*E*` at the end of the card line.

```diff
- 1 Elsa, Spirit of Winter
+ 1 Elsa, Spirit of Winter *E*
```