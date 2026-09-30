import argparse
import hashlib
import heapq
import html
import itertools
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
MODEL_FIELDS = [
    {"name": "Term", "id": 6064286510114836544},
    {"name": "Headline", "id": 7562720696105355688},
    {"name": "Image", "id": 4862974160591875216},
    {"name": "Details", "id": 5184221410199971603},
    {"name": "Reference", "id": 2960379663213147101},
    {"name": "Image Credit", "id": 4601177655232819196},
    {"name": "Category", "id": 3547631925314965014},
]
MODEL_TEMPLATE_ID = 1746720810477752110
CONCEPT = "concept"

LINK_FIELDS = ["profile", "kind_of", "translates", "compare"]
PROFILE_SHAPES = {"text", "single", "range", "list", "stages"}
VOCABULARY_PATH = ROOT / "vocabulary.yaml"


def word_pattern(words, wildcards=False):
    """Matches any of the words or phrases as whole words, ignoring case, also
    within hyphenated compounds ("washed" in "washed-rind"). With `wildcards`,
    `*` in a word matches any run of word characters."""
    alternatives = []
    for word in sorted(words, key=len, reverse=True):
        escaped = re.escape(word)
        if wildcards:
            escaped = escaped.replace(r"\*", r"[\w’'-]+")
        alternatives.append(escaped)
    return re.compile(rf"(?<!\w)(?:{'|'.join(alternatives)})(?!\w)", re.IGNORECASE)


def load_vocabulary(path=VOCABULARY_PATH):
    """Loads the deck's house style from `vocabulary.yaml`."""
    with path.open(encoding="utf-8") as file:
        vocabulary = YAML(typ="safe").load(file)
    for category, spec in vocabulary["categories"].items():
        for name, row in (spec.get("profile") or {}).items():
            if row.get("shape") not in PROFILE_SHAPES:
                raise ValueError(
                    f"{path.name}: {category} profile row {name} has unknown shape"
                )
            if row["shape"] == "list" and "joiner" not in row:
                raise ValueError(
                    f"{path.name}: {category} profile row {name} needs a joiner"
                )
        for group in spec.get("jargon", []):
            if group not in vocabulary["jargon"]:
                raise ValueError(
                    f"{path.name}: {category} names unknown jargon {group}"
                )
    return vocabulary


class Category:
    """A category's settings from `vocabulary.yaml`."""

    def __init__(self, spec, jargon):
        self.label = spec["label"]
        self.term_label = spec["term_label"]
        self.profile_rows = {
            name: {**row, "vocabulary": row.get("words") or {}}
            for name, row in (spec.get("profile") or {}).items()
        }
        self.required_rows = [
            name for name, row in self.profile_rows.items() if row.get("required")
        ]
        self.headline_noun = spec.get("headline_noun")
        self.headline_order = [
            (entry["kind"], word_pattern(entry["words"], wildcards=True))
            for entry in spec.get("headline_order", [])
        ]
        self.headline_lead = spec.get("headline_lead")
        self.jargon = {
            card: word_pattern(words)
            for group in spec.get("jargon", [])
            for card, words in (jargon[group] or {}).items()
        }


VOCABULARY = load_vocabulary()
CATEGORIES = {
    name: Category(spec, VOCABULARY["jargon"])
    for name, spec in VOCABULARY["categories"].items()
}
BANNED_JARGON = word_pattern(VOCABULARY["banned"])
REFERENCE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
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
    seen_ids = set()
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

        card_id = card.get("id", term)
        if not isinstance(card_id, str) or not card_id:
            errors.append(f"{term}: id must be a nonempty string when present")
        elif card_id in seen_ids:
            errors.append(f"duplicate card id: {card_id}")
        else:
            seen_ids.add(card_id)

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
        # Text written for the deck uses typographic quotes; Wikipedia extracts,
        # which track their source, stay verbatim.
        authored = [term, *core, *context]
        if isinstance(details, str) and not (card.get("source") or {}).get(
            "adapted_from"
        ):
            authored.append(details)
        if any(
            isinstance(text, str) and re.search(r"['\"]", text) for text in authored
        ):
            errors.append(f"{term}: use typographic quotes (’ “ ”), not straight ones")

        source = card.get("source")
        if not isinstance(source, dict):
            errors.append(f"{term}: source must be a mapping")
        else:
            if not isinstance(source.get("label"), str) or not source["label"]:
                errors.append(f"{term}: source.label must be a nonempty string")
            url = source.get("url")
            if not isinstance(url, str) or not url.startswith("https://"):
                errors.append(f"{term}: source.url must be an HTTPS URL")
            adapted_from = source.get("adapted_from")
            if adapted_from is not None and (
                not isinstance(adapted_from, str)
                or not adapted_from.startswith("https://")
            ):
                errors.append(
                    f"{term}: source.adapted_from must be an HTTPS URL when present"
                )

        kind = card.get("kind")
        if kind not in (None, CONCEPT):
            errors.append(f"{term}: kind must be {CONCEPT!r} when present")
        if "profile" in card:
            if kind == CONCEPT:
                errors.append(f"{term}: concept cards cannot have a profile")
            category = CATEGORIES.get(card.get("category"))
            rows = category.profile_rows if category else {}
            errors.extend(profile_errors(term, rows, card["profile"]))
        for field in ["kind_of", "translates"]:
            value = card.get(field)
            if value is not None and (not isinstance(value, str) or not value):
                errors.append(f"{term}: {field} must be a nonempty key when present")
        compare = card.get("compare", [])
        if not isinstance(compare, list) or not all(
            isinstance(key, str) and key for key in compare
        ):
            errors.append(f"{term}: compare must be a list of keys when present")

        image = card.get("image")
        if card.get("mirror_image") not in (None, True):
            errors.append(f"{term}: mirror_image must be true when present")
        image_from = card.get("image_from")
        if image_from is not None and (
            image is not None or not isinstance(image_from, str) or not image_from
        ):
            errors.append(f"{term}: image_from must be a key, in place of image")
        if image is None and (kind == CONCEPT or image_from is not None):
            pass
        elif not isinstance(image, str) or not image:
            errors.append(f"{term}: image must be a nonempty Commons filename")
        elif "/" in image or "\\" in image:
            errors.append(f"{term}: image must be a filename, not a path")
        elif image in seen_images:
            errors.append(f"duplicate image: {image}")
        seen_images.add(image)

    if not errors:
        errors.extend(link_errors(cards))
    if errors:
        raise ValueError("Invalid menu-food data:\n- " + "\n- ".join(errors))
    return data


def profile_rows(card):
    """Returns the profile rows of a card's category."""
    return CATEGORIES[card["category"]].profile_rows


def profile_values(spec, value):
    """Returns the vocabulary words in a profile value, or `None` if malformed."""
    shape = spec["shape"]
    if shape == "text":
        return [] if isinstance(value, str) and value else None
    if shape == "stages":
        if not isinstance(value, str):
            return None
        stages = value.partition(", ")[0].split(" or ")
        return [stage.split(" ", 1)[0] for stage in stages]
    if shape == "single":
        return [value] if isinstance(value, str) else None
    if shape == "range":
        if isinstance(value, str):
            return [value]
        if isinstance(value, list) and len(value) == 2:
            return value
        return None
    if isinstance(value, list) and value:
        return value
    return None


def profile_errors(term, rows, profile):
    if not rows:
        return [f"{term}: this category has no profile"]
    if not isinstance(profile, dict):
        return [f"{term}: profile must be a mapping"]
    errors = []
    for row, value in profile.items():
        if row not in rows:
            errors.append(f"{term}: unknown profile row {row!r}")
            continue
        words = profile_values(rows[row], value)
        if words is None:
            errors.append(f"{term}: malformed profile {row}: {value!r}")
            continue
        vocabulary = rows[row]["vocabulary"]
        for word in words:
            if word not in vocabulary:
                errors.append(f"{term}: profile {row} has unknown value {word!r}")
    return errors


def card_key(card):
    """Returns the stable key that links and note GUIDs use for a card."""
    return card.get("id", card["term"])


def index_cards(cards):
    return {card_key(card): card for card in cards}


def card_texts(card):
    answer = card.get("answer", {})
    return [
        *answer.get("core", []),
        *answer.get("context", []),
        card.get("details", ""),
    ]


def text_references(card):
    return [
        match.group(1)
        for text in card_texts(card)
        for match in REFERENCE.finditer(text)
    ]


def merged_profile(card, cards_by_key):
    """Returns a card's profile, filling in rows it omits from its `kind_of` parent."""
    if "profile" not in card:
        return None
    profile = {}
    if (parent := cards_by_key.get(card.get("kind_of"))) is not None:
        profile = dict(merged_profile(parent, cards_by_key) or {})
    return {**profile, **card["profile"]}


def profile_links(profile, rows):
    links = []
    for row, value in (profile or {}).items():
        vocabulary = rows[row]["vocabulary"]
        for word in profile_values(rows[row], value):
            if (link := vocabulary.get(word)) is not None and link not in links:
                links.append(link)
    return links


def dependencies(card, cards_by_key):
    """Returns the keys of the cards a card builds on, to be studied before it."""
    links = [
        *([card["kind_of"]] if "kind_of" in card else []),
        *([card["translates"]] if "translates" in card else []),
        *profile_links(merged_profile(card, cards_by_key), profile_rows(card)),
        *text_references(card),
    ]
    return [link for link in dict.fromkeys(links) if link != card_key(card)]


def prerequisites(card, cards_by_key):
    """Returns every key a card builds on, directly or through other cards."""
    found = set()
    pending = dependencies(card, cards_by_key)
    while pending:
        key = pending.pop()
        if key not in found and key in cards_by_key:
            found.add(key)
            pending.extend(dependencies(cards_by_key[key], cards_by_key))
    return found


def is_reworked(card):
    """Returns whether a card follows the concept-card conventions, rather than
    predating them."""
    return (
        card.get("kind") == CONCEPT
        or any(field in card for field in LINK_FIELDS)
        or bool(text_references(card))
    )


def base_term(card):
    """Returns a card's term without any disambiguating suffix, like "(cheese)"."""
    return re.sub(r"\s*\(.*\)$", "", card["term"])


def mention_names(card):
    """Returns the ways prose names a card: its term's slash-separated
    alternatives, without any disambiguating suffix."""
    return [re.sub(r"\s*\(.*\)$", "", name) for name in card["term"].split(" / ")]


def mention_pattern(names):
    """Matches any of the names in prose, longest first, allowing a plural "s"."""
    alternatives = "|".join(
        re.escape(name) for name in sorted(names, key=len, reverse=True)
    )
    return re.compile(rf"(?<![\w-])(?:{alternatives})s?(?![\w-])", re.IGNORECASE)


def linked_mentions(card, cards_by_key):
    """Matches the prose mentions of every card that a card links."""
    keys = [*dependencies(card, cards_by_key), *card.get("compare", [])]
    names = {name for key in keys for name in mention_names(cards_by_key[key])}
    return mention_pattern(names) if names else None


def link_errors(cards):
    errors = []
    cards_by_key = index_cards(cards)
    parents = {card["kind_of"] for card in cards if "kind_of" in card}
    for group in VOCABULARY["jargon"].values():
        for concept in group or {}:
            if concept not in cards_by_key:
                errors.append(f"{VOCABULARY_PATH.name}: names unknown card {concept!r}")
    # Cards whose terms can be mentioned in prose, grouped so that mentioning a
    # word with several senses, like "truffle", needs only one of them linked.
    mentionable = {}
    for card in cards:
        pattern = mention_pattern(mention_names(card))
        mentionable.setdefault(pattern.pattern, (pattern, []))[1].append(card)
    for card in cards:
        key = card_key(card)
        targets = [
            card.get("kind_of"),
            card.get("translates"),
            *card.get("compare", []),
            *text_references(card),
        ]
        for target in targets:
            if target is not None and target not in cards_by_key:
                errors.append(f"{key}: links to unknown card {target!r}")
        if "image_from" in card and "image" not in cards_by_key.get(
            card["image_from"], {}
        ):
            errors.append(f"{key}: image_from must name a card with its own image")
        category = CATEGORIES[card["category"]]
        lead = category.headline_lead
        if (
            lead
            and card.get("kind") != CONCEPT
            and not (card.get("profile") or {}).get(lead)
        ):
            errors.append(f"{key}: needs a profile {lead} row to lead its headline")
        if not is_reworked(card):
            continue
        profile = merged_profile(card, cards_by_key)
        # A card with narrower kinds may leave the rows that vary to them.
        if "profile" in card and key not in parents:
            missing = [row for row in category.required_rows if row not in profile]
            if missing:
                errors.append(f"{key}: profile lacks {', '.join(missing)}")
        for target in profile_links(profile, category.profile_rows):
            if target not in cards_by_key:
                errors.append(f"{key}: profile links to unknown card {target!r}")
        learned = prerequisites(card, cards_by_key) | {key}
        linked = learned | set(card.get("compare", []))
        # Fragments are joined so that no phrase can span two of them.
        text = "\n".join(REFERENCE.sub("", text) for text in card_texts(card))
        for concept, pattern in category.jargon.items():
            if concept not in learned and (match := pattern.search(text)):
                errors.append(
                    f"{key}: uses {match.group()!r} without building on {concept!r}"
                )
        if match := BANNED_JARGON.search(text):
            errors.append(f"{key}: uses {match.group()!r}, which is too vague")
        for pattern, senses in mentionable.values():
            if any(base_term(sense) == base_term(card) for sense in senses):
                continue  # The card's own word, or another sense of it.
            if not pattern.search(text):
                continue
            if not any(
                card_key(sense) in (learned if sense.get("kind") == CONCEPT else linked)
                for sense in senses
            ):
                terms = " or ".join(repr(sense["term"]) for sense in senses)
                errors.append(f"{key}: mentions {terms} without linking it")
        if "profile" in card and category.headline_order:
            errors.extend(headline_order_errors(card, category))
            ranged = [
                row
                for row, spec in category.profile_rows.items()
                if spec["shape"] == "range" and isinstance(profile.get(row), list)
            ]
            headline = " ".join(core_fragments(card["answer"], card.get("kind_of")))
            if ranged and not re.search(r"\bwhen\b", headline):
                errors.append(
                    f"{key}: headline must say when its {' and '.join(ranged)} varies"
                )
    if not errors:
        try:
            prerequisite_order(cards)
        except ValueError as error:
            errors.append(str(error))
    return errors


def headline_order_errors(card, category):
    """Checks that the adjectives before the category's headline noun, like
    "cheese", follow its `headline_order`."""
    order = category.headline_order
    errors = []
    for fragment in card["answer"]["core"]:
        for segment in fragment.split(";"):
            noun = re.escape(category.headline_noun)
            phrase = re.split(rf"\b{noun}\b", plain_text(segment))[0]
            found = []
            for match in re.finditer(r"[\w’'-]+(?: rich)?", phrase):
                rank = next(
                    (
                        rank
                        for rank, (_, pattern) in enumerate(order)
                        if pattern.fullmatch(match.group())
                    ),
                    None,
                )
                if rank is not None:
                    found.append((rank, match.group()))
            for (rank, word), (next_rank, next_word) in itertools.pairwise(found):
                if next_rank < rank:
                    errors.append(
                        f"{card_key(card)}: headline puts {order[next_rank][0]} "
                        f"{next_word!r} after {order[rank][0]} {word!r}"
                    )
    return errors


def prerequisite_order(cards):
    """Orders cards so each follows the cards it builds on, otherwise keeping data
    order. Raises on a dependency cycle."""
    cards_by_key = index_cards(cards)
    ordered = []
    state = {}

    def visit(card, path):
        key = card_key(card)
        if state.get(key) == "done":
            return
        if state.get(key) == "visiting":
            raise ValueError("dependency cycle: " + " → ".join([*path, key]))
        state[key] = "visiting"
        for dependency in dependencies(card, cards_by_key):
            visit(cards_by_key[dependency], [*path, key])
        state[key] = "done"
        ordered.append(card)

    for card in cards:
        visit(card, [])
    return ordered


def study_order(cards):
    """Orders cards for studying: each after the cards it builds on, with the
    categories interleaved so that each is spread evenly across the whole deck.

    Among the cards whose prerequisites are all placed, the next card comes from
    the category that is furthest behind its share; within a category, cards keep
    their prerequisite order."""
    cards_by_key = index_cards(cards)
    base = prerequisite_order(cards)
    rank = {card_key(card): index for index, card in enumerate(base)}
    waiting = {card_key(card): set(dependencies(card, cards_by_key)) for card in base}
    dependents = {key: [] for key in waiting}
    for key, needs in waiting.items():
        for need in needs:
            dependents[need].append(key)
    totals = {}
    for card in base:
        totals[card["category"]] = totals.get(card["category"], 0) + 1
    placed = dict.fromkeys(totals, 0)
    ready = {category: [] for category in totals}
    for card in base:
        if not waiting[card_key(card)]:
            heapq.heappush(ready[card["category"]], rank[card_key(card)])
    ordered = []
    while len(ordered) < len(base):
        category = min(
            (category for category, heap in ready.items() if heap),
            key=lambda category: (
                placed[category] / totals[category],
                ready[category][0],
            ),
        )
        card = base[heapq.heappop(ready[category])]
        ordered.append(card)
        placed[category] += 1
        for dependent in dependents[card_key(card)]:
            waiting[dependent].discard(card_key(card))
            if not waiting[dependent]:
                heapq.heappush(
                    ready[cards_by_key[dependent]["category"]], rank[dependent]
                )
    return ordered


def text_html(text, mentions=None):
    """Escapes text, rendering `[[key]]` and `[[key|shown text]]` references, and
    marking prose matching `mentions` the same way."""

    def plain_html(plain):
        if mentions is None:
            return html.escape(plain)
        return "".join(
            f'<span class="ref">{html.escape(piece)}</span>'
            if index % 2
            else html.escape(piece)
            for index, piece in enumerate(
                re.split(f"({mentions.pattern})", plain, flags=re.IGNORECASE)
            )
        )

    parts = []
    position = 0
    for match in REFERENCE.finditer(text):
        parts.append(plain_html(text[position : match.start()]))
        shown = match.group(2) or match.group(1)
        parts.append(f'<span class="ref">{html.escape(shown)}</span>')
        position = match.end()
    parts.append(plain_html(text[position:]))
    return "".join(parts)


def plain_text(text):
    return REFERENCE.sub(lambda match: match.group(2) or match.group(1), text)


def core_fragments(answer, kind_of=None):
    return [*([f"a kind of [[{kind_of}]]"] if kind_of else []), *answer["core"]]


def natural_join(words, joiner):
    """Joins words with `joiner`, writing "a, b or c" rather than "a or b or c"."""
    if joiner.strip() in ("or", "and") and len(words) > 2:
        return ", ".join(words[:-1]) + joiner + words[-1]
    return joiner.join(words)


def headline_lead(card):
    """Returns the profile value that leads a card's headline, like its animal."""
    row = CATEGORIES[card["category"]].headline_lead
    value = (card.get("profile") or {}).get(row) if row else None
    if not value:
        return None
    return natural_join(value, " or ") if isinstance(value, list) else value


def headline_fragments(card):
    lead = headline_lead(card)
    return [
        *([lead] if lead else []),
        *core_fragments(card["answer"], card.get("kind_of")),
    ]


def recognition_html(answer, kind_of=None, mentions=None, lead=None):
    fragments = [*([lead] if lead else []), *core_fragments(answer, kind_of)]
    core = "; ".join(text_html(fragment, mentions) for fragment in fragments)
    context = [text_html(fragment, mentions) for fragment in answer.get("context", [])]
    return f"<strong>{core}</strong>" + (f"; {'; '.join(context)}" if context else "")


def gloss(card):
    return "; ".join(plain_text(fragment) for fragment in headline_fragments(card))


def profile_word_html(word, link, cards_by_key, suffix=""):
    """Renders a profile word, followed by any suffix, with its linked card's gloss."""
    display = html.escape(word) + html.escape(suffix)
    if link is None:
        return display
    return (
        f'<span class="ref">{html.escape(word)}</span>{html.escape(suffix)}'
        f' <span class="gloss">({html.escape(gloss(cards_by_key[link]))})</span>'
    )


def profile_html(profile, rows_spec, cards_by_key):
    rows = []
    for row, spec in rows_spec.items():
        if row not in profile:
            continue
        value = profile[row]
        vocabulary = spec.get("vocabulary", {})

        def word_html(word, suffix="", vocabulary=vocabulary):
            return profile_word_html(word, vocabulary.get(word), cards_by_key, suffix)

        if spec["shape"] == "text":
            value_html = html.escape(value)
        elif spec["shape"] == "stages":
            stages, comma, rest = value.partition(", ")
            value_html = " or ".join(
                word_html(word, space + detail)
                for word, space, detail in (
                    stage.partition(" ") for stage in stages.split(" or ")
                )
            ) + html.escape(comma + rest)
        elif spec["shape"] == "range" and isinstance(value, list):
            value_html = " to ".join(word_html(word) for word in value)
        elif spec["shape"] == "list":
            value_html = natural_join(
                [word_html(word) for word in value], spec["joiner"]
            )
        else:
            value_html = word_html(value)
        rows.append(f"<dt>{html.escape(spec['label'])}</dt><dd>{value_html}</dd>")
    return f'<dl class="profile">{"".join(rows)}</dl>'


def details_html(card, cards_by_key, backlinks):
    """Renders the details, plus any profile, glosses of linked cards and backlinks."""
    profile = merged_profile(card, cards_by_key)
    parts = []
    if profile:
        parts.append(profile_html(profile, profile_rows(card), cards_by_key))
    mentions = linked_mentions(card, cards_by_key)
    parts.append(f"<p>{text_html(card['details'], mentions)}</p>")
    glossed = set(profile_links(profile, profile_rows(card)))
    linked = [
        *(key for key in dependencies(card, cards_by_key) if key not in glossed),
        *card.get("compare", []),
    ]
    if linked:
        items = "".join(
            f"<li><b>{html.escape(cards_by_key[key]['term'])}</b>: "
            f"{html.escape(gloss(cards_by_key[key]))}</li>"
            for key in linked
        )
        parts.append(f'<ul class="terms">{items}</ul>')
    for label, names in [
        ("On menus", backlinks.get("menu_words")),
        ("Kinds in this deck", backlinks.get("kinds")),
        ("In this deck", backlinks.get("examples")),
    ]:
        if names:
            names = ", ".join(html.escape(name) for name in names)
            parts.append(f'<p class="examples">{label}: {names}</p>')
    if len(parts) == 1:
        return text_html(card["details"], mentions)
    return "".join(parts)


def card_backlinks(cards):
    """Maps concept keys to the concrete cards they classify (`examples`), cards to
    their narrower `kind_of` cards (`kinds`), and cards to the foreign menu words
    translating them (`menu_words`)."""
    cards_by_key = index_cards(cards)
    backlinks = {}
    for card in cards:
        if "translates" in card:
            entry = backlinks.setdefault(card["translates"], {})
            entry.setdefault("menu_words", []).append(card["term"])
        if card.get("kind") == CONCEPT:
            continue
        if "kind_of" in card and cards_by_key[card["kind_of"]].get("kind") != CONCEPT:
            entry = backlinks.setdefault(card["kind_of"], {})
            entry.setdefault("kinds", []).append(card["term"])
        # Only a profile or `kind_of` makes a card an example of a concept; a
        # reference in prose merely mentions it.
        classified = [
            *([card["kind_of"]] if "kind_of" in card else []),
            *profile_links(merged_profile(card, cards_by_key), profile_rows(card)),
        ]
        for link in classified:
            concept = cards_by_key[link]
            if concept.get("kind") != CONCEPT:
                continue
            # A card classified by a foreign menu word is also an example of what
            # the word means.
            for key in dict.fromkeys([link, concept.get("translates", link)]):
                terms = backlinks.setdefault(key, {}).setdefault("examples", [])
                if card["term"] not in terms:
                    terms.append(card["term"])
    return {
        key: {kind: sorted(names) for kind, names in entry.items()}
        for key, entry in backlinks.items()
    }


def source_html(source):
    link = (
        f'<a href="{html.escape(source["url"], quote=True)}">'
        f'{html.escape(source["label"])}</a>'
    )
    if adapted_from := source.get("adapted_from"):
        permalink = (
            f'<a href="{html.escape(adapted_from, quote=True)}">permalink</a>'
        )
        link += f" (adapted from {permalink})"
    return link


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
            if "image" in card
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
        fields=[field.copy() for field in MODEL_FIELDS],
        templates=[
            {
                "name": "Recognition",
                "id": MODEL_TEMPLATE_ID,
                "qfmt": front_template,
                "afmt": back_template,
            }
        ],
        css=styling,
    )


def category_label(card):
    category = CATEGORIES[card["category"]]
    return category.term_label if card.get("kind") == CONCEPT else category.label


def card_image(card, cards_by_key):
    """Returns a card's image, or the one it borrows through `image_from`."""
    if "image_from" in card:
        return cards_by_key[card["image_from"]]["image"]
    return card.get("image")


def image_html(card, image_src, cards_by_key):
    """Renders a card's image, mirrored if its owner sets `mirror_image` so that,
    say, every pig faces the same way."""
    owner = cards_by_key[card["image_from"]] if "image_from" in card else card
    mirror = ' style="transform: scaleX(-1)"' if owner.get("mirror_image") else ""
    return f'<img src="{html.escape(image_src, quote=True)}"{mirror}>'


def note_fields(card, image_src, cards_by_key, backlinks):
    """Returns the note's field values, in `MODEL_FIELDS` order."""
    image = card_image(card, cards_by_key)
    return [
        html.escape(card["term"]),
        recognition_html(
            card["answer"],
            card.get("kind_of"),
            linked_mentions(card, cards_by_key),
            headline_lead(card),
        ),
        image_html(card, image_src, cards_by_key) if image else "",
        details_html(card, cards_by_key, backlinks.get(card_key(card), {})),
        source_html(card["source"]),
        f'<a href="{html.escape(commons_file_url(image), quote=True)}">image source</a>'
        if image
        else "",
        html.escape(category_label(card)),
    ]


def make_note(card, model, media_path, cards_by_key=None, backlinks=None, due=0):
    fields = note_fields(
        card,
        media_path.name if media_path else "",
        cards_by_key or index_cards([card]),
        backlinks or {},
    )
    tags = ["menu-food", f"menu-food::{card['category']}"]
    if card.get("kind") == CONCEPT:
        tags.append("menu-food::concept")
    return genanki.Note(
        model=model,
        fields=fields,
        tags=tags,
        guid=genanki.guid_for("menu-food", card_key(card)),
        due=due,
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
    cards_by_key = index_cards(cards)
    backlinks = card_backlinks(cards)
    for due, card in enumerate(study_order(cards)):
        deck.add_note(
            make_note(
                card,
                model,
                media.get(card_image(card, cards_by_key)),
                cards_by_key,
                backlinks,
                due,
            )
        )

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
