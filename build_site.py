"""Builds the demo website: every card, rendered as in Anki, for browsing and
flipping through in a web browser."""

import argparse
import html
import json
import re
import shutil
from pathlib import Path

import build_deck

ROOT = Path(__file__).parent
SITE_PATH = ROOT / "site"
DEFAULT_OUTPUT = ROOT / "dist" / "site"
REF = re.compile(r'<span class="ref">(.*?)</span>')
TERM_ITEM = re.compile(r"<li><b>(.*?)</b>")
EXAMPLES = re.compile(r'(<p class="examples">[^:<]+: )([^<]*)(</p>)')


def ref_targets(card, cards_by_key):
    """Maps the ways a card's text can show a linked card to that card's key."""
    targets = {}
    for key in [*build_deck.dependencies(card, cards_by_key), *card.get("compare", [])]:
        for name in [key, *build_deck.mention_names(cards_by_key[key])]:
            targets[name.casefold()] = key
    profile = build_deck.merged_profile(card, cards_by_key)
    rows = build_deck.profile_rows(card)
    for row, value in (profile or {}).items():
        vocabulary = rows[row]["vocabulary"]
        for word in build_deck.profile_values(rows[row], value):
            if (link := vocabulary.get(word)) is not None:
                targets[word.casefold()] = link
    for text in build_deck.card_texts(card):
        for match in build_deck.REFERENCE.finditer(text):
            targets[(match.group(2) or match.group(1)).casefold()] = match.group(1)
    return targets


def card_link(key, shown_html, class_name=None):
    class_attribute = f' class="{class_name}"' if class_name else ""
    href = html.escape("#" + key, quote=True)
    return f'<a{class_attribute} href="{href}">{shown_html}</a>'


def link_cards(rendered, card, cards_by_key, keys_by_term):
    """Turns a rendered card's references to other cards into links to them."""
    targets = ref_targets(card, cards_by_key)

    def ref(match):
        shown = html.unescape(match.group(1)).casefold()
        key = targets.get(shown) or targets.get(shown.removesuffix("s"))
        if key is None:
            raise ValueError(f"{card['term']}: can't tell which card {shown!r} is")
        return card_link(key, match.group(1), "ref")

    def term_item(match):
        key = keys_by_term[html.unescape(match.group(1))]
        return f"<li><b>{card_link(key, match.group(1))}</b>"

    def examples(match):
        names = ", ".join(
            card_link(keys_by_term[html.unescape(name)], name)
            for name in match.group(2).split(", ")
        )
        return match.group(1) + names + match.group(3)

    rendered = REF.sub(ref, rendered)
    rendered = TERM_ITEM.sub(term_item, rendered)
    return EXAMPLES.sub(examples, rendered)


def site_cards(cards, media):
    """Returns each card's data for the site, in study order."""
    cards_by_key = build_deck.index_cards(cards)
    backlinks = build_deck.card_backlinks(cards)
    keys_by_term = {card["term"]: build_deck.card_key(card) for card in cards}
    entries = []
    for card in build_deck.study_order(cards):
        image = build_deck.card_image(card, cards_by_key)
        sources = [
            f"media/{media[name].name}" if name else ""
            for name in [image, card.get("served_image")]
        ]
        front, back = build_deck.card_sides(card, cards_by_key, backlinks, *sources)
        owner = cards_by_key[card["image_from"]] if "image_from" in card else card
        entries.append(
            {
                "key": build_deck.card_key(card),
                "term": card["term"],
                "category": card["category"],
                "label": build_deck.category_label(card),
                "gloss": build_deck.gloss(card),
                "image": sources[0],
                "images": [source for source in sources if source],
                "mirror": bool(owner.get("mirror_image")),
                "front": front,
                "back": link_cards(back, card, cards_by_key, keys_by_term),
            }
        )
    return entries


def build_site(data, output=DEFAULT_OUTPUT, offline=False, workers=8):
    cards = data["cards"]
    media = build_deck.prepare_media(cards, offline=offline, workers=workers)
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(SITE_PATH, output)
    shutil.copy(build_deck.STYLING_PATH, output / "card.css")
    (output / "media").mkdir()
    for path in media.values():
        shutil.copy(path, output / "media" / path.name)
    site_data = {
        "categories": {
            key: category.label for key, category in build_deck.CATEGORIES.items()
        },
        "cards": site_cards(cards, media),
    }
    (output / "cards.json").write_text(
        json.dumps(site_data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return output


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--offline", action="store_true", help="build using only already-cached media"
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT, help="output directory"
    )
    parser.add_argument(
        "--workers", type=int, default=8, help="concurrent media downloads"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data = build_deck.validate_data(build_deck.load_data())
    output = build_site(
        data, output=args.output, offline=args.offline, workers=args.workers
    )
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
