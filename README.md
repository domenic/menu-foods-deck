# Menu Foods Anki deck

An Anki deck for recognizing unfamiliar food words on restaurant menus. It
focuses on identification, not language production: seeing the bare term should
be enough to recall what kind of food it is and the characteristics that matter
most when ordering.

**[Download the latest Menu Foods deck](https://github.com/domenic/menu-foods-deck/releases/latest/download/menu-foods.apkg)**

The cards live in one mixed `Menu Foods` deck and cover pasta, meats and
charcuterie, seafood, vegetables, cheeses, condiments, desserts, dishes, and
other easily misclassified terms.

Category tags allow filtering if you'd prefer to just study pastas or similar.
But at least for me, "is this mystery foreign word a pasta or a meat?" is
important, so I suggest studying them all jumbled together.

## Example cards

<p align="center">
  <img src="screenshots/orecchiette.png" alt="Anki answer card for orecchiette: small ear-shaped pasta" width="360">
  <img src="screenshots/guanciale.png" alt="Anki answer card for guanciale: pig; salt-cured cheek or jowl" width="360">
</p>
<p align="center">
  <img src="screenshots/pecorino-romano.png" alt="Anki answer card for pecorino romano: a kind of pecorino; hard, salty grating cheese" width="360">
  <img src="screenshots/peperoncino.png" alt="Anki answer card for peperoncino: chili pepper, usually hot; Italian" width="360">
</p>

## How the cards teach

Every card should make sense to someone who knows little about food. So a card
may only use plain everyday English and terms that have cards of their own:
"bloomy rind", "whey", "young cheese", "DOP" and "fondue" are all cards. New
cards are ordered so that a term's card comes before the cards that use it, and
a card's back repeats the short answer of every card it links. The build
enforces as much of this as it can; see [below](#what-the-build-checks).

The cheeses, and the dishes, desserts and menu words they rely on, follow these
conventions. The other categories still use the original, simpler format of a
headline plus a Wikipedia extract.

## Card design

The front contains only the menu term. The back contains:

- a headline with the crucial facts in bold, which is what to grade yourself
  on, followed by extra context in normal weight;
- a representative image;
- for a cheese, a profile of fixed facts, most significant first: family, rind,
  firmness, texture, flavor strength, flavor, smell, milk, age, style, how it's
  made, origin and protected label;
- a short explanation;
- the answers of the cards it links, and, for a term, the cards in the deck
  that are examples of it; and
- links to the text and image sources.

Words that link another card have a dotted underline. The note model includes
compact desktop styling and readable mobile/night-mode colors. Fixed deck and
model IDs and deterministic note GUIDs ensure that successive packages identify
the same generated deck objects, so importing a new package updates cards
without losing their review history.

## The data

[menu-foods.yaml](menu-foods.yaml) is the hand-edited card database, and
[vocabulary.yaml](vocabulary.yaml) holds the deck's house style: its categories,
the words a cheese profile may use, and the word lists the build checks against.
Editing either never requires touching the Python. Here is a
cheese and a term of art it relies on, through its profile's `family` row:

```yaml
- term: feta
  category: cheese
  answer:
    core:
      - crumbly, salty, brined cheese
    context:
      - Greek
  profile:
    family: brined
    rind: none
    firmness: semi-soft
    texture: [crumbly, doesn’t melt]
    strength: medium
    flavor: [salty, tangy]
    milk: [sheep]
    age: aged at least 2 months, in brine
    origin: Greece
    label: PDO
  details: >-
    Sold in white blocks, ideally still in their salty liquid. ...
  source:
    label: Wikipedia
    url: https://en.wikipedia.org/wiki/Feta
  image: Feta_Cheese.jpg
- term: brined cheese
  category: cheese
  kind: concept
  answer:
    core:
      - stored in salt water, which keeps it moist and salty
  details: >-
    Brine is just very salty water. Brined cheeses sit in it until they're
    sold, so they have no [[rind]] and taste noticeably salty. ...
  compare:
    - feta
    - halloumi
  source:
    label: Wikipedia
    url: https://en.wikipedia.org/wiki/Brined_cheese
  image: Nabulsi cheese sold in brine.jpg
```

`answer.core` is the bold headline and `answer.context` the rest of it.
`category` is one of the categories in `vocabulary.yaml`, and becomes a
`menu-food::…` tag.
Cards normally derive their note identity from `term`; an optional `id`
preserves it when a displayed term changes, and links name cards by `id` when
they have one.

These fields connect cards:

- `kind: concept` marks a card for a term of art, like `rind` or `DOP`, rather
  than a food. Concept cards may omit `image` and get a `menu-food::concept`
  tag. Their backs list the cards they classify.
- `profile` holds a cheese's fixed facts, using the rows and words in
  `vocabulary.yaml`. A profile word with a concept card, like `brined`, links
  that card.
- `kind_of` names a broader card, like `pecorino` for `pecorino romano`. The
  headline starts with "a kind of …", and the profile inherits any rows the card
  leaves out. A card with kinds may leave out the rows that differ between them.
- `translates` names what a foreign menu word means, like `fresh cheese` for
  `fresco / fresca`.
- `[[key]]` or `[[key|shown text]]` in answers and details links another card.
- `compare` links look-alike or related cards, like `camembert` for `brie`.
- `image_from` reuses another card's image, like a menu word showing what it
  means.

Links through a profile, `kind_of`, `translates` or a reference make the linked
card a prerequisite; `compare` and `image_from` don't.

### Writing cards

- **Wording.** Prefer concrete descriptions ("tingles on your tongue") to
  evaluative or insider words ("biting", "rustic"). Name places plainly
  ("northern France"), keeping a region only when the food is named after it.
  Gloss a dish or drink mentioned in passing, or link its card.
- **Headlines.** Order adjectives before "cheese" by kind: size, shape or color;
  firmness; texture; flavor; age; origin; then kinds like `bloomy-rind`. When a
  cheese varies, say how: "mild when young; sharp when aged".
- **Names.** Name an adjective with its food (`young cheese`, `sharp cheese`),
  so other categories can have their own versions. Give a noun a `(cheese)`
  suffix only when it's ambiguous (`mold (cheese)`), and give a word with
  several menu meanings one suffixed card per meaning (`stracciatella
  (cheese)`, `stracciatella (gelato)`). A slash joins only spelling or grammar
  variants (`fresco / fresca`); different names for one thing, like `quesillo`
  and `Oaxaca cheese`, get separate cards so each is recognized on its own.
- **Images.** Every food card needs a photo that clearly shows the food and
  matches its text. A card that must go without one should be dropped.
- **Details.** Write reworked cards' details as original text, linking the
  source as further reading. The older cards' details are checked-in Wikipedia
  extracts; builds never fetch article text, so upstream edits change the deck
  only when deliberately refreshed (see [below](#refresh-wikipedia-descriptions)).

### What the build checks

Beyond the shape of each field, the build rejects (with the named lists in
`vocabulary.yaml`):

- a link to a card that doesn't exist, or a cycle of prerequisites;
- a card that mentions another card's term without linking it or one of its
  senses;
- a term of art from the `jargon` list, like "whey" or "young", in a card that
  doesn't build on the card explaining it;
- a `banned` vague word, like "rustic" or "mountain cheese";
- a food card without an image;
- a profile missing a required row, or using a word its row doesn't list; and
- a cheese headline whose adjectives break the `headline_order`, or that
  doesn't say when a range of firmness or strength applies.

## Development

### Build the deck

Install [uv](https://docs.astral.sh/uv/), then run:

```sh
uv run python build_deck.py
```

The first build downloads the explicitly selected Commons images and caches
them under `.cache/media/`, then writes `dist/menu-foods.apkg`. Import it
through Anki's normal import interface.

Later builds can prohibit network access and require a complete local cache:

```sh
uv run python build_deck.py --offline
```

The builder uses `SOURCE_DATE_EPOCH` when provided, plus sorted media and
normalized ZIP metadata, so identical source, media, and timestamps produce an
identical `.apkg` file. CI uses the source commit's timestamp, allowing later
releases to update earlier imports while keeping each release reproducible.

### Validate and test

Validate the YAML without downloading media or writing a package:

```sh
uv run python build_deck.py --check
```

Run the tests:

```sh
uv run python -m unittest discover -s test -v
```

### Regenerate screenshots

After installing the [Playwright](https://playwright.dev/) CLI and its Chromium
browser, regenerate the README card screenshots with:

```sh
playwright install chromium
uv run python generate_screenshots.py
```

### Refresh Wikipedia descriptions

Check tracked Wikipedia descriptions against the current article leads:

```sh
uv run wikipedia_descriptions.py check
```

The command reports text differences without writing anything. To refresh every
tracked description and source revision, run:

```sh
uv run wikipedia_descriptions.py update
```

Only changed cards are rewritten; review the resulting `menu-foods.yaml` diff in
Git before committing it. Descriptions without a permanent Wikipedia revision in
`source.adapted_from` are skipped by both commands.

### Publish a release

Release tags must be `v` followed by the version in `pyproject.toml`; CI rejects
mismatches. Use `uv` to update both the project metadata and lockfile, then
commit and tag the result. For example, to promote `1.0.0.dev0` to `1.0.0`:

```sh
uv version --bump stable
version=$(uv version --short)
git add pyproject.toml uv.lock
git commit -m "v$version"
git tag -a "v$version" -m "v$version"
git push --atomic origin main "v$version"
```

For later releases, `uv version --bump major`, `minor`, or `patch` provides the
corresponding version increments.

## Third-party material

The repository's MIT license covers the original code and original portions of
the deck data. Explanatory text and images retain their respective source terms;
every card includes source links. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.
