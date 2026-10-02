---
title: 'Gundam M.S. War'
weight: 62
---

This plugin reads a decklist and puts the card images into the proper `game/` directories.

[Gundam M.S. War](https://gundammswar.fandom.com/wiki/Gundam_M.S_War) is the out-of-print Bandai America trading card game from 2001, based on *Mobile Suit Gundam Wing* (with *Endless Waltz* and *Mobile Suit Gundam* expansions). It is not the 2025 Gundam Card Game; for that, use the [Gundam plugin](../gundam).

Card images come from the fan-run [Gundam M.S. War wiki](https://gundammswar.fandom.com/wiki/Gundam_M.S_War).

This plugin supports the `text` decklist format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is `text`.

Run the script.

```sh
python plugins/gundam_ms_war/fetch.py game/decklist/deck.txt text
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {text}

Options:
  --help  Show this message and exit.
```

## Formats

### `text`

One card per line: the quantity (optionally followed by `x`), the card number, and an optional card name. Card numbers are printed on the cards: `MS` (Mobile Suit), `PL` (Pilot), `EV` (Event), and `BF` (Battlefield), with `p` for promos such as `BF-p03`. Lines that don't match are skipped.

```
3 MS-001 Wing Gundam
2 MS-003 Gundam Deathscythe
2x MS-025 Wing Gundam Zero
3 PL-001 Heero Yuy
2 PL-002 Duo Maxwell
2 EV-001 Operation Meteor
1 EV-023 Zero System
1 BF-001 Liberation Army Village
1 BF-p03 New York, NY
```

Mission cards have no individual scans on the wiki and are not supported.
