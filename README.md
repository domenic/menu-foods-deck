# Menu Foods Anki deck

An Anki deck for recognizing unfamiliar food words on restaurant menus. It
focuses on identification, not language production: seeing the bare term should
be enough to recall what kind of food it is and the characteristics that matter
most when ordering.

The deck currently contains 212 cards:

- 59 pasta shapes and pasta-adjacent dumplings
- 72 meats, cuts, and charcuterie terms
- 58 cheeses
- 23 other easily misclassified menu terms

All cards live in one mixed `Menu Foods` deck. Category tags make filtering
possible without giving away whether an unknown word is pasta, meat, cheese, or
something else during review.

## One source of truth

[menu-foods.yaml](menu-foods.yaml) is the only hand-edited card database. Each
entry keeps the term, category, structured answer, explanatory details,
reference, and exact Wikimedia Commons image together:

```yaml
- term: feta
  category: cheese
  answer:
    core:
      - Salty, crumbly, brined cheese
    context:
      - usually sheep’s milk
      - Greek
  details: >-
    Feta (FET-ə; Greek: φέτα [ˈfeta]) is a Greek brined white cheese made from
    sheep's milk or from a mixture of sheep and goat's milk. It is soft, with
    small or no holes, and no skin.
  reference:
    label: Wikipedia
    url: https://en.wikipedia.org/wiki/Feta
  image: Feta_Cheese.jpg
```

`answer.core` renders in bold as the fast recognition cue. Optional
`answer.context` follows in normal weight; it is useful context, not a universal
grading contract. Semicolons separate the fragments in both lists.

There are no generated headline files, historical audit tables, or executable
data modules. Downloaded media and the resulting package are ignored build
artifacts.

## Build the package

Install [uv](https://docs.astral.sh/uv/), then run:

```sh
uv sync
uv run python build_deck.py
```

The first build downloads the 212 explicitly selected Commons images and caches
them under `.cache/media/`. It writes `dist/menu-foods.apkg`, then opens the
archive and its embedded SQLite collection to verify the deck, model, stable
note GUIDs, fields, tags, cards, and bundled media.

Later builds can prohibit network access and require a complete local cache:

```sh
uv run python build_deck.py --offline
```

The builder uses a fixed package timestamp, sorted media, and normalized ZIP
metadata, so identical source and media produce an identical `.apkg` file.

## Validate and test

Validate the YAML without downloading media or writing a package:

```sh
uv run python build_deck.py --check
```

Run the source, rendering, stable-ID, image-uniqueness, and grading-policy tests:

```sh
uv run python -m unittest discover -s test -p 'test_*.py' -v
```

## Card design

The front contains only the menu term. The back contains:

- a compact headline with crucial facts bolded first;
- a representative image;
- short non-graded explanatory context; and
- links to the text and image sources.

The note model includes compact desktop styling and readable mobile/night-mode
colors. Fixed deck/model IDs and deterministic note GUIDs ensure that successive
packages identify the same generated deck objects.

The builder communicates with neither Anki nor AnkiConnect and never invokes
Anki sync. Import `dist/menu-foods.apkg` through Anki's normal import interface.

## Third-party material

The repository's MIT license covers the original code and original portions of
the deck data. Explanatory text and images retain their respective source terms;
every card includes source links. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

## License

MIT — see [LICENSE](LICENSE).
