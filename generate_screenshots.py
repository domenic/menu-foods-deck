import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import build_deck

ROOT = Path(__file__).parent
OUTPUT = ROOT / "screenshots"
TERMS = ["orecchiette", "guanciale", "pecorino romano", "peperoncino"]
VIEWPORT = (480, 760)


def render_template(template, fields):
    def conditional(match):
        return match.group(2) if fields.get(match.group(1)) else ""

    template = re.sub(r"{{#([^}]+)}}(.*?){{/\1}}", conditional, template, flags=re.S)
    for name, value in fields.items():
        template = template.replace(f"{{{{{name}}}}}", value)
    return template


def card_html(card, cards):
    front_template, back_template, styling = build_deck.load_card_design()
    cards_by_key = build_deck.index_cards(cards)
    image_src = ""
    if image := build_deck.card_image(card, cards_by_key):
        media_path = build_deck.cached_media_path(image)
        if media_path is None:
            raise FileNotFoundError(
                f"media is not cached for {image}; build the deck first"
            )
        image_src = media_path.as_uri()

    values = build_deck.note_fields(
        card,
        image_src,
        cards_by_key,
        build_deck.card_backlinks(cards),
    )
    fields = {
        field["name"]: value for field, value in zip(build_deck.MODEL_FIELDS, values)
    }
    front = render_template(front_template, fields)
    back = render_template(back_template.replace("{{FrontSide}}", front), fields)
    return f"""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{styling}
</style>
<body class="card">{back}</body>
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render answer-side card screenshots with Playwright."
    )
    parser.add_argument(
        "terms",
        nargs="*",
        default=TERMS,
        help="terms to render (default: the README examples)",
    )
    parser.add_argument(
        "--output", type=Path, default=OUTPUT, help="screenshot directory"
    )
    parser.add_argument(
        "--full-page",
        action="store_true",
        help="capture the whole card, not the viewport",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    playwright = shutil.which("playwright")
    if playwright is None:
        raise SystemExit(
            "The Playwright CLI and its Chromium browser are required to generate screenshots."
        )

    data = build_deck.validate_data(build_deck.load_data())
    cards = {card["term"]: card for card in data["cards"]}
    args.output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temporary:
        temporary = Path(temporary)
        for term in args.terms:
            filename = re.sub(r"[^\w-]+", "-", term).strip("-")
            source = temporary / f"{filename}.html"
            source.write_text(card_html(cards[term], data["cards"]), encoding="utf-8")
            subprocess.run(
                [
                    playwright,
                    "screenshot",
                    "--viewport-size",
                    f"{VIEWPORT[0]},{VIEWPORT[1]}",
                    "--wait-for-timeout",
                    "100",
                    *(["--full-page"] if args.full_page else []),
                    source.as_uri(),
                    str(args.output / f"{filename}.png"),
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
