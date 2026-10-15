# Editing the Menu Foods deck

The deck is built from two hand-edited files: [menu-foods.yaml](menu-foods.yaml), the cards, with a field reference in its opening comment; and [vocabulary.yaml](vocabulary.yaml), the house style, with each category's profile rows and words and the word lists that cards are checked against. `build_deck.py` validates both and writes `dist/menu-foods.apkg`.

## Writing cards

The reader knows very little about food. A card may use only plain everyday English, or terms that have their own card, linked with `[[key]]` or `[[key|shown text]]`. The build catches unlinked mentions of existing cards and listed terms of art, but not new jargon, so read new text as a newcomer would.

- **Wording.** Prefer concrete descriptions ("tingles on your tongue") to evaluative or insider words ("biting", "rustic", "savory", "rich" as a flavor). Name places plainly ("northern France"), keeping a region only when the food is named after it. Gloss a dish or drink mentioned in passing, or link its card.
- **Terms of art.** When a card needs a new term, like "simmered", add a concept card for it and list its word forms in a `jargon` group in `vocabulary.yaml`, so the build makes every card that uses it link it.
- **Headlines.** The bold core is what the reader is graded on, so it holds only what they must remember; examples go in the context, as "like penne". Meat headlines start with the animal, which the build takes from the profile; a meat family concept card writes its usual animal itself ("usually pig"). Cheese adjectives follow `headline_order` in `vocabulary.yaml`, and a cheese that varies says how ("mild when young; sharp when aged").
- **Names.** Name an adjective with its food (`young cheese`, `cured meat`), so that other categories can have their own versions. Give a word with several menu meanings one suffixed card per meaning (`stracciatella (cheese)`, `stracciatella (gelato)`). A slash joins only spelling or grammar variants (`fresco / fresca`); different names for one thing, like `quesillo` and `Oaxaca cheese`, get separate cards.
- **Images.** Every food card needs a Wikimedia Commons photo that clearly shows the food and matches the text; drop a card rather than ship it without one. Concept cards may have one too. Animals face left (`mirror_image`), and foreign words for an animal or food borrow the English card's photo (`image_from`). Pasta cards show the uncooked shape with a served dish (`served_image`).
- **Details.** Write details as original text, with the source as further reading. Some older cards' details are verbatim Wikipedia extracts, marked by `source.adapted_from`; builds never fetch text, so those change only when refreshed deliberately (below).
- **Renaming.** A note's identity comes from its `id`, or its `term` if it has none. When renaming a card that has been released, set `id` to the old term so imports update the existing note instead of adding a duplicate.

The study order is computed, not taken from the file: each card comes after the cards it links (except `compare` and `image_from`), with categories interleaved. Avoid links that would make two cards each other's prerequisites; the build reports such cycles.

## Commands

```sh
uv run python build_deck.py --check    # validate, without downloading media
uv run python -m unittest discover -s test
uv run ruff check && uv run ruff format
uv run python build_deck.py            # downloads images to .cache/media, writes dist/menu-foods.apkg
```

A package meant for importing into a collection that already has the deck must be built with `SOURCE_DATE_EPOCH=$(date +%s)`. Without it, the package carries a fixed old timestamp, and Anki's "If newer" import skips every note. CI builds use the commit's timestamp.

When one of the README's example cards changes, regenerate the screenshots with `uv run python generate_screenshots.py` (needs the Playwright CLI and its Chromium).

`uv run wikipedia_descriptions.py check` compares the verbatim Wikipedia extracts with the current articles; `update` rewrites the changed ones, for review in the diff.

`reorder_new_cards.py` puts a collection's unlearned cards into the current study order through AnkiConnect; see the README's "Advanced updating". Never change someone's live collection without their explicit go-ahead.

## Releasing

Release tags are `v` plus the version in `pyproject.toml`, which CI checks. The annotated tag's message becomes the GitHub release notes, so write it for people using the deck: what changed, and anything to know when updating. `--cleanup=verbatim` keeps its Markdown headings, which Git would otherwise strip as comments.

```sh
uv version --bump minor
version=$(uv version --short)
git add pyproject.toml uv.lock
git commit -m "v$version"
git tag -a "v$version" --cleanup=verbatim -F notes.md
git push --atomic origin main "v$version"
```
