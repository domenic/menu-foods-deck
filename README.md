# Menu Foods Anki deck

An Anki deck for recognizing unfamiliar food words on restaurant menus. It
focuses on identification, not language production: seeing the bare term should
be enough to recall what kind of food it is and the characteristics that matter
most when ordering.

The source currently contains 212 cards:

- 59 pasta shapes and pasta-adjacent dumplings
- 72 meats, cuts, and charcuterie terms
- 58 cheeses
- 23 other easily misclassified menu terms

All cards live in one mixed `Menu Foods` deck. Category tags make filtering
possible without giving away whether an unknown word is a pasta, meat, cheese,
or something else during review.

## Card design

The front is only the menu term. The back contains:

- a compact, sentence-like recognition headline;
- a representative image;
- short non-graded context from Wikipedia or another linked source; and
- links to the article and image source.

The headline is backed by structured data in `recognition.json`. Crucial facts
are bold and come first; context follows in normal weight. Semicolons are the
only separators. For example:

> **Pig; uncooked, unsmoked, dry-cured ham**; Italian; usually thinly sliced

Bold is a fast recognition cue, not a universal grading contract. A learner can
decide that cheese texture or a meat's animal source matters while treating
country, region, or cut location as useful but ungraded context.

## Requirements

- [Node.js](https://nodejs.org/) 22.17 or newer
- [Anki](https://apps.ankiweb.net/) desktop
- [AnkiConnect](https://github.com/ankicommunity/anki-desktop-addon-connect),
  add-on code `2055492159`

Anki must be running for commands that use AnkiConnect. Initial installation
also needs internet access to download card images from Wikimedia Commons.

## Validate the sources

Install no npm dependencies; there are none. Run the offline source tests with:

```sh
npm test
```

Run the full data and cached-source validation with:

```sh
npm run validate
```

This default validation mode does not contact or change Anki. The checked-in
Wikipedia cache makes it reproducible without routine network access; missing
cache records are fetched from Wikipedia and written back to the cache.

## Install into Anki

With Anki running and AnkiConnect installed:

```sh
node build.mjs --install
```

The installer creates the `Menu Foods` deck and `Menu Food Recognition` note
type if needed, downloads missing media, adds missing notes idempotently,
assigns a dedicated randomized options preset, and verifies the result.

AnkiConnect defaults to `http://127.0.0.1:8765`. To target another machine,
provide its endpoint explicitly:

```sh
ANKI_CONNECT_URL=http://computer-name:8765 node build.mjs --install
```

Review that URL carefully before using a write mode. The program prints the
target endpoint before contacting Anki.

## Maintenance commands

`node build.mjs --help` shows the complete list. The important distinction is:

- `--verify` audits the installed notes, cards, fields, model styling, deck
  placement, and referenced media without writing to Anki.
- `--install` adds missing notes and media.
- `--refresh-headlines` updates all recognition headlines and their styling.
- `--refresh-content` updates headlines, details, references, and explicitly
  selected card images.
- `--refresh-presentation` updates styling and explicitly selected images.
- `--mix` assigns fully random new-card gathering and sorting.
- `--flatten` moves the 212 tagged cards into the single parent deck, then
  removes only the known empty legacy category subdecks.

Every write mode performs a full verification afterward. None of the commands
invoke Anki sync; syncing is intentionally left to the user.

## Editing the deck

Food terms and source/image overrides live in `foods.mjs`. Structured headline
proposals live in `headline-audit.mjs`. After editing them, regenerate the
machine-readable headlines and review report with:

```sh
npm run generate
```

This rewrites `recognition.json` and `headline-audit.md`. The audit records
recognition collisions, information-density flags, and a category-by-category
before/after review. Run `npm test` and `npm run validate` before applying the
changes to Anki.

## Third-party material

The repository's MIT license covers the original code and deck data. Cached
Wikipedia extracts and Wikimedia metadata remain under their respective source
terms, and downloaded images retain the license shown on each linked Commons
file page. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

## License

MIT — see [LICENSE](LICENSE).
