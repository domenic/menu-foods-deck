# Menu Foods Anki deck

I've often had trouble with restaurant menus. Is this foreign-language word a meat, a pasta, or a cheese? What's the difference between peperoncino and pepperoni, or tagliata and tagliatelle? Why does tartufo sometimes refer to a dessert and sometimes a pasta topping?

This deck of [Anki](https://apps.ankiweb.net/) flashcards is designed to solve my confusion once and for all. It contains over 400 cards covering meats, pastas, cheeses, seafood, vegetables, condiments, and more. It starts from the basics ("pork", "ham", "beef", "cured", "aged", "shellfish") before eventually getting into a full list of specific cheeses. Via the power of spaced repetition, I have finally stopped pulling out my phone to look up words before ordering.

**[Download the latest Menu Foods deck](https://github.com/domenic/menu-foods-deck/releases/latest/download/menu-foods.apkg)**, or [browse the release notes](https://github.com/domenic/menu-foods-deck/releases).

## Example cards

<p align="center">
  <img src="screenshots/orecchiette.png" alt="Anki answer card for orecchiette: small, ear-shaped pasta" width="360">
  <img src="screenshots/guanciale.png" alt="Anki answer card for guanciale: pig; cured jowl; Italian" width="360">
</p>
<p align="center">
  <img src="screenshots/pecorino-romano.png" alt="Anki answer card for pecorino romano: a kind of pecorino; hard, salty grating cheese" width="360">
  <img src="screenshots/peperoncino.png" alt="Anki answer card for peperoncino: small hot chili pepper, fresh or dried; Italian" width="360">
</p>

## Card design

This deck is focused on _word recognition_: the front side contains the word or concept, and the back contains the relevant details one should recall when deciding one's order. It doesn't work as well for production, i.e., looking at a food and then recalling its name. So if a friend busts out some round, orange cheese, you won't necessarily be able to say "nice mimolette!".

The cards live in one mixed `Menu Foods` deck. Category tags allow filtering if you'd prefer to just study pastas or similar. But at least for me, "is this mystery foreign word a pasta or a meat?" is important, so I suggest studying them all jumbled together.

The cards are designed to make sense to someone who knows very little about food. You might think that a card for "ham" is not necessary, but as a former vegetarian who only recently got a grip on [the Norman/Saxon split](https://grammarphobia.com/blog/2007/01/on-swine-and-pork.html), I thought it was worth reinforcing. Basic cards like "egg pasta" often contain nuggets of new information, e.g. that the pasta contains eggs entirely in place of water. Anyway, if these are too obvious for you, just mash the "Easy" button in Anki, and they'll quickly become scarce.

As part of the pedagogy, the cards are ordered so that a term's card comes before the cards that use it. Similarly, a card's back gives a dotted underline to all previously-studied terms, and repeats their contents when space permits.

You can decide how strict to be when grading yourself. My default suggestion is to require that you remember all the bolded contents, e.g., for the above "guanciale" card, press "Again" if you forget any of "pig", "cured", or "jowl", but give yourself a pass if you forget "Italian". But it's also valid to go much coarser, e.g., if you don't care much about cheeses, just recognizing that "stracchino" is a type of cheese and "whey" is part of the cheese-making process could be enough.

## Installing and updating

Import the downloaded `menu-foods.apkg` with Anki's **File → Import**. New cards come in a study order: each card comes after the cards it builds on, and the categories are interleaved, so that each is spread across the whole deck. Keep the deck's default display order for new cards ("New card gather order: Deck" and "New card sort order: Card type, then order gathered"); do not use a random order.

To update from an earlier release, first make a backup (**File → Create Backup**). Then import the new package with "Update notes" and "Update note types" set to "If newer". Your existing cards get the new text and keep their review history, and cards new to the deck join the new-card queue at their places in the study order. To see what changed, search the browser for `deck:"Menu Foods" (added:1 OR edited:1)`.

## Advanced updating

Normally, the above update procedure suffices. However, in Anki, importing a new release can't change the study index of any existing cards in your collection; it only inserts new cards. So if a previous release had cards A, B, C, D waiting to be studied, and a new release inserts X, Y between B and C, the new order will be A, B, C or X (tied), D or Y (tied), instead of the intended A, B, X, Y, C, D.

If you want to preserve the ideal as-designed study order, you can install [uv](https://docs.astral.sh/uv/) and [AnkiConnect](https://ankiweb.net/shared/info/2055492159), and run the following commands from a checkout of this repository while Anki is open:

```sh
uv run python reorder_new_cards.py           # shows what would change
uv run python reorder_new_cards.py --apply
```

This will reorder all unstudied cards to best match the new release's order, including moving new prerequsite cards for cards you've already studied to the front of the queue.

For bigger reworks, you can also delete the relevant cards and re-import the package.

## The data

[menu-foods.yaml](menu-foods.yaml) is the hand-edited card database, and
[vocabulary.yaml](vocabulary.yaml) holds the deck's house style: its categories,
each category's profile rows and words, and the word lists the build checks
against.
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
Examples belong in the context, as "like penne", so that they aren't part of
what to memorize; context starting with "like" follows the bold core after a
comma rather than a semicolon. `headline_lines: true` puts each core fragment
on its own line, for headlines that list parallel groups.
`category` is one of the categories in `vocabulary.yaml`, and becomes a
`menu-food::…` tag.
Cards normally derive their note identity from `term`; an optional `id`
preserves it when a displayed term changes, and links name cards by `id` when
they have one.

These fields connect cards:

- `kind: concept` marks a card for a term of art, like `rind` or `DOP`, rather
  than a food. Concept cards may omit `image` and get a `menu-food::concept`
  tag. Their backs list the cards they classify.
- `profile` holds a cheese's, meat's or pasta's fixed facts, using its
  category's rows and words in `vocabulary.yaml`. A profile word with a concept
  card, like `brined`, links that card.
- `kind_of` names a broader card, like `pecorino` for `pecorino romano`. The
  headline starts with "a kind of …", and the profile inherits any rows the card
  leaves out. A card with kinds may leave out the rows that differ between them.
- `translates` names what a foreign menu word means, like `fresh cheese` for
  `fresco / fresca`.
- `[[key]]` or `[[key|shown text]]` in answers and details links another card.
- `compare` links look-alike or related cards, like `camembert` for `brie`.
- `image_from` reuses another card's image, like a menu word showing what it
  means.
- `mirror_image: true` flips a card's image left to right, so that animals and
  diagrams all face the same way (left); cards borrowing the image flip too.
- `served_image` adds a second photo beside `image`, captioned as served, for a
  pasta whose `image` shows it uncooked.

Links through a profile, `kind_of`, `translates` or a reference make the linked
card a prerequisite; `compare` and `image_from` don't.

### Writing cards

- **Wording.** Prefer concrete descriptions ("tingles on your tongue") to
  evaluative or insider words ("biting", "rustic"). Name places plainly
  ("northern France"), keeping a region only when the food is named after it.
  Gloss a dish or drink mentioned in passing, or link its card. Use typographic
  apostrophes and quotes (’ “ ”), except in verbatim Wikipedia extracts.
- **Headlines.** A meat's headline starts with its animal, which the build
  writes from its profile's `animal` row ("pig; dry-cured ham"), so the
  headline itself leaves it out; its nationality goes in the context line.
  Order a cheese's adjectives before "cheese" by kind: size, shape or
  color; firmness; texture; flavor; age; origin; then kinds like `bloomy-rind`.
  When a cheese varies, say how: "mild when young; sharp when aged".
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
- a term of art from the `jargon` lists, like "whey" or "cured", in a card that
  doesn't build on the card explaining it (each category says which lists
  apply, so "young" can mean young cheese on a cheese card but not on a meat
  card);
- a `banned` vague word, like "rustic" or "mountain cheese";
- a straight apostrophe or quote in text written for the deck;
- a food card without an image;
- a profile missing a required row, or using a word its row doesn't list;
- a meat card without an `animal` row to lead its headline; and
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

Lint and format the Python, which CI checks:

```sh
uv run ruff check
uv run ruff format
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
commit and tag the result. The annotated tag's message becomes the GitHub
release notes, so write it for people using the deck: what changed, and anything
to know when updating; `--cleanup=verbatim` keeps Markdown headings, which Git
would otherwise strip as comments. For example, for a minor release with its
notes in `notes.md`:

```sh
uv version --bump minor
version=$(uv version --short)
git add pyproject.toml uv.lock
git commit -m "v$version"
git tag -a "v$version" --cleanup=verbatim -F notes.md
git push --atomic origin main "v$version"
```

`uv version --bump major` and `patch` provide the other version increments.

## Third-party material

The repository's MIT license covers the original code and original portions of
the deck data. Explanatory text and images retain their respective source terms;
every card includes source links. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.
