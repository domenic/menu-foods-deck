import html
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


def card_html(card):
    front_template, back_template, styling = build_deck.load_card_design()
    media_path = build_deck.cached_media_path(card["image"])
    if media_path is None:
        raise FileNotFoundError(
            f"media is not cached for {card['image']}; build the deck first"
        )

    fields = {
        "Term": html.escape(card["term"]),
        "Headline": build_deck.recognition_html(card["answer"]),
        "Image": f'<img src="{html.escape(media_path.as_uri(), quote=True)}">',
        "Details": html.escape(card["details"]),
        "Reference": build_deck.source_html(card["source"]),
        "Image Credit": (
            f'<a href="{html.escape(build_deck.commons_file_url(card["image"]), quote=True)}">'
            "image source</a>"
        ),
        "Category": html.escape(build_deck.CATEGORIES[card["category"]]),
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


def main():
    playwright = shutil.which("playwright")
    if playwright is None:
        raise SystemExit(
            "The Playwright CLI and its Chromium browser are required to generate screenshots."
        )

    data = build_deck.validate_data(build_deck.load_data())
    cards = {card["term"]: card for card in data["cards"]}
    OUTPUT.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as temporary:
        temporary = Path(temporary)
        for term in TERMS:
            filename = term.replace(" ", "-")
            source = temporary / f"{filename}.html"
            source.write_text(card_html(cards[term]), encoding="utf-8")
            subprocess.run(
                [
                    playwright,
                    "screenshot",
                    "--viewport-size",
                    f"{VIEWPORT[0]},{VIEWPORT[1]}",
                    "--wait-for-timeout",
                    "100",
                    source.as_uri(),
                    str(OUTPUT / f"{filename}.png"),
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
