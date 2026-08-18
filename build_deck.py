import argparse
import hashlib
import html
import os
import re
import tempfile
import time
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import genanki
from ruamel.yaml import YAML

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "menu-foods.yaml"
TEMPLATES_PATH = ROOT / "templates"
FRONT_TEMPLATE_PATH = TEMPLATES_PATH / "front.html"
BACK_TEMPLATE_PATH = TEMPLATES_PATH / "back.html"
STYLING_PATH = TEMPLATES_PATH / "style.css"
MEDIA_CACHE = ROOT / ".cache" / "media"
DEFAULT_OUTPUT = ROOT / "dist" / "menu-foods.apkg"
PACKAGE_TIMESTAMP = 1_700_000_000
CATEGORIES = {
    "pasta": "Pasta",
    "meat": "Meat & charcuterie",
    "cheese": "Cheese",
    "other": "Other menu trap",
}
YAML_SAFE = YAML(typ="safe")


def load_card_design():
    return tuple(
        path.read_text(encoding="utf-8")
        for path in [FRONT_TEMPLATE_PATH, BACK_TEMPLATE_PATH, STYLING_PATH]
    )


def load_data(path=DATA_PATH):
    with path.open(encoding="utf-8") as file:
        return YAML_SAFE.load(file)


def validate_data(data):
    errors = []
    if data.get("schema") != 1:
        errors.append("top-level schema must be 1")

    deck = data.get("deck")
    if not isinstance(deck, dict):
        errors.append("deck must be a mapping")
        deck = {}
    for path, value in [
        ("deck.id", deck.get("id")),
        (
            "deck.model.id",
            deck.get("model", {}).get("id")
            if isinstance(deck.get("model"), dict)
            else None,
        ),
    ]:
        if not isinstance(value, int) or not 0 < value < 1 << 31:
            errors.append(f"{path} must be a positive 31-bit integer")
    for path, value in [
        ("deck.name", deck.get("name")),
        (
            "deck.model.name",
            deck.get("model", {}).get("name")
            if isinstance(deck.get("model"), dict)
            else None,
        ),
    ]:
        if not isinstance(value, str) or not value:
            errors.append(f"{path} must be a nonempty string")

    cards = data.get("cards")
    if not isinstance(cards, list) or not cards:
        errors.append("cards must be a nonempty list")
        cards = []

    seen_terms = set()
    seen_images = set()
    for index, card in enumerate(cards):
        prefix = f"cards[{index}]"
        if not isinstance(card, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        term = card.get("term")
        if not isinstance(term, str) or not term:
            errors.append(f"{prefix}.term must be a nonempty string")
            term = prefix
        elif term in seen_terms:
            errors.append(f"duplicate term: {term}")
        seen_terms.add(term)

        if card.get("category") not in CATEGORIES:
            errors.append(f"{term}: unknown category {card.get('category')!r}")

        answer = card.get("answer")
        if not isinstance(answer, dict):
            errors.append(f"{term}: answer must be a mapping")
            answer = {}
        core = answer.get("core")
        context = answer.get("context", [])
        if not isinstance(core, list) or not core:
            errors.append(f"{term}: answer.core must be a nonempty list")
            core = []
        if not isinstance(context, list):
            errors.append(f"{term}: answer.context must be a list when present")
            context = []
        for fragment in [*core, *context]:
            if not isinstance(fragment, str) or not fragment:
                errors.append(f"{term}: answer fragments must be nonempty strings")
            elif re.search(r"[;.!?]$", fragment):
                errors.append(
                    f"{term}: answer fragment has terminal punctuation: {fragment!r}"
                )

        details = card.get("details")
        if not isinstance(details, str) or not details:
            errors.append(f"{term}: details must be a nonempty string")
        elif re.search(r"\(\s*(?:\)|[,;])", details):
            errors.append(f"{term}: details contain malformed empty punctuation")

        reference = card.get("reference")
        if not isinstance(reference, dict):
            errors.append(f"{term}: reference must be a mapping")
        else:
            if not isinstance(reference.get("label"), str) or not reference["label"]:
                errors.append(f"{term}: reference.label must be a nonempty string")
            url = reference.get("url")
            if not isinstance(url, str) or not url.startswith("https://"):
                errors.append(f"{term}: reference.url must be an HTTPS URL")

        image = card.get("image")
        if not isinstance(image, str) or not image:
            errors.append(f"{term}: image must be a nonempty Commons filename")
        elif "/" in image or "\\" in image:
            errors.append(f"{term}: image must be a filename, not a path")
        elif image in seen_images:
            errors.append(f"duplicate image: {image}")
        seen_images.add(image)

    if errors:
        raise ValueError("Invalid menu-food data:\n- " + "\n- ".join(errors))
    return data


def recognition_html(answer):
    core = "; ".join(html.escape(fragment) for fragment in answer["core"])
    context = [html.escape(fragment) for fragment in answer.get("context", [])]
    return f"<strong>{core}</strong>" + (f"; {'; '.join(context)}" if context else "")


def media_stem(image):
    slug = unicodedata.normalize("NFKD", image)
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", slug).strip("_").lower()[:70]
    suffix = hashlib.sha256(image.encode()).hexdigest()[:8]
    return f"menu_food_{slug}_{suffix}"


def commons_file_url(image):
    quoted = urllib.parse.quote(image.replace(" ", "_"), safe="()!,'-._~")
    return f"https://commons.wikimedia.org/wiki/File:{quoted}"


def commons_thumbnail_url(image):
    return "https://commons.wikimedia.org/w/thumb.php?" + urllib.parse.urlencode(
        {"f": image, "width": 640}
    )


def extension_for_content(content, content_type):
    signatures = [
        (b"\xff\xd8\xff", "jpg"),
        (b"\x89PNG\r\n\x1a\n", "png"),
        (b"GIF87a", "gif"),
        (b"GIF89a", "gif"),
    ]
    for signature, extension in signatures:
        if content.startswith(signature):
            return extension
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return "webp"

    mime = content_type.partition(";")[0].strip().lower()
    extensions = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
    }
    if mime not in extensions:
        raise ValueError(f"unsupported downloaded media type: {content_type}")
    return extensions[mime]


def cached_media_path(image):
    matches = sorted(MEDIA_CACHE.glob(f"{media_stem(image)}.*"))
    if len(matches) > 1:
        raise ValueError(f"multiple cached media files for {image}: {matches}")
    if matches and matches[0].stat().st_size:
        return matches[0]
    return None


def download_image(image, offline=False):
    cached = cached_media_path(image)
    if cached:
        return cached
    if offline:
        raise FileNotFoundError(f"media is not cached for {image}")

    request = urllib.request.Request(
        commons_thumbnail_url(image),
        headers={
            "User-Agent": "menu-foods-deck/1.0 (https://github.com/domenic/menu-foods-deck)"
        },
    )
    last_error = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                content = response.read()
                extension = extension_for_content(
                    content, response.headers.get("Content-Type", "")
                )
            if not content:
                raise ValueError("downloaded image is empty")
            path = MEDIA_CACHE / f"{media_stem(image)}.{extension}"
            temporary = path.with_suffix(f".{extension}.tmp")
            temporary.write_bytes(content)
            temporary.replace(path)
            return path
        except (OSError, ValueError) as error:
            last_error = error
            if attempt != 4:
                time.sleep(2**attempt)
    raise RuntimeError(f"could not download {image}: {last_error}")


def prepare_media(cards, offline=False, workers=8):
    MEDIA_CACHE.mkdir(parents=True, exist_ok=True)
    paths = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(download_image, card["image"], offline): card["image"]
            for card in cards
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            image = futures[future]
            paths[image] = future.result()
            if completed % 25 == 0 or completed == len(futures):
                print(f"Media: {completed}/{len(futures)} ready")
    return paths


def make_model(deck_data):
    model_data = deck_data["model"]
    front_template, back_template, styling = load_card_design()
    return genanki.Model(
        model_data["id"],
        model_data["name"],
        fields=[
            {"name": "Term"},
            {"name": "Headline"},
            {"name": "Image"},
            {"name": "Details"},
            {"name": "Reference"},
            {"name": "ImageCredit"},
            {"name": "Category"},
        ],
        templates=[
            {
                "name": "Recognition",
                "qfmt": front_template,
                "afmt": back_template,
            }
        ],
        css=styling,
    )


def make_note(card, model, media_path):
    reference = card["reference"]
    image_credit = commons_file_url(card["image"])
    fields = [
        html.escape(card["term"]),
        recognition_html(card["answer"]),
        f'<img src="{html.escape(media_path.name, quote=True)}">',
        html.escape(card["details"]),
        f'<a href="{html.escape(reference["url"], quote=True)}">{html.escape(reference["label"])}</a>',
        f'<a href="{html.escape(image_credit, quote=True)}">image source</a>',
        html.escape(CATEGORIES[card["category"]]),
    ]
    return genanki.Note(
        model=model,
        fields=fields,
        tags=["menu-food", f"menu-food::{card['category']}"],
        guid=genanki.guid_for("menu-food", card["term"]),
    )


def normalize_package(path, timestamp):
    date_time = time.gmtime(timestamp)[:6]
    with zipfile.ZipFile(path) as source:
        entries = {name: source.read(name) for name in source.namelist()}
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as output:
            for name in sorted(entries):
                info = zipfile.ZipInfo(name, date_time=date_time)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                output.writestr(info, entries[name])
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def build_package(data, output=DEFAULT_OUTPUT, offline=False, workers=8):
    cards = data["cards"]
    media = prepare_media(cards, offline=offline, workers=workers)
    model = make_model(data["deck"])
    deck = genanki.Deck(data["deck"]["id"], data["deck"]["name"])
    for card in cards:
        deck.add_note(make_note(card, model, media[card["image"]]))

    output.parent.mkdir(parents=True, exist_ok=True)
    package = genanki.Package(deck)
    package.media_files = [
        str(path) for path in sorted(media.values(), key=lambda path: path.name)
    ]
    timestamp = int(os.environ.get("SOURCE_DATE_EPOCH", PACKAGE_TIMESTAMP))
    package.write_to_file(output, timestamp=timestamp)
    normalize_package(output, timestamp)
    return output


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate menu-foods.yaml and build an Anki package."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate data without downloading media or building",
    )
    parser.add_argument(
        "--offline", action="store_true", help="build using only already-cached media"
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT, help="output .apkg path"
    )
    parser.add_argument(
        "--workers", type=int, default=8, help="concurrent media downloads"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data = validate_data(load_data())
    category_counts = {
        category: sum(card["category"] == category for card in data["cards"])
        for category in CATEGORIES
    }
    print(
        f"Validated {len(data['cards'])} cards: "
        + ", ".join(
            f"{category}={count}" for category, count in category_counts.items()
        )
    )
    if args.check:
        return
    output = build_package(
        data, output=args.output, offline=args.offline, workers=args.workers
    )
    print(f"Wrote {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
