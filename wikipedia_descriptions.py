import argparse
import difflib
import io
import json
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from collections import defaultdict

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import FoldedScalarString

import build_deck

WIKIPEDIA_HOST = re.compile(r"[a-z-]+\.wikipedia\.org")
USER_AGENT = "menu-foods-deck/1.0 (https://github.com/domenic/menu-foods-deck)"
YAML_WIDTH = 120


def chunks(values, size):
    return [values[index : index + size] for index in range(0, len(values), size)]


def parse_revision_url(url):
    parsed = urllib.parse.urlparse(url)
    old_ids = urllib.parse.parse_qs(parsed.query).get("oldid", [])
    if (
        parsed.scheme != "https"
        or not WIKIPEDIA_HOST.fullmatch(parsed.hostname or "")
        or parsed.path != "/w/index.php"
        or len(old_ids) != 1
        or not old_ids[0].isdigit()
        or int(old_ids[0]) <= 0
    ):
        raise ValueError(f"not a permanent Wikipedia revision URL: {url}")
    return parsed.hostname, int(old_ids[0])


def parse_article_url(url):
    parsed = urllib.parse.urlparse(url)
    if (
        parsed.scheme != "https"
        or not WIKIPEDIA_HOST.fullmatch(parsed.hostname or "")
        or not parsed.path.startswith("/wiki/")
    ):
        raise ValueError(f"not a Wikipedia article URL: {url}")
    title = urllib.parse.unquote(parsed.path.removeprefix("/wiki/")).replace("_", " ")
    return parsed.hostname, title


def is_wikipedia_revision_url(url):
    parsed = urllib.parse.urlparse(url)
    return bool(
        WIKIPEDIA_HOST.fullmatch(parsed.hostname or "")
        and parsed.path == "/w/index.php"
    )


def clean_extract(extract):
    cleaned = re.sub(
        r"\b(?:also\s+)?(?:UK|US|English)(?:\s+also)?(?::)?\s*(?=[,;)])",
        "",
        extract,
        flags=re.IGNORECASE,
    )
    replacements = [
        (r"\(\s*(?:[,;]\s*)+", "("),
        (r"(?:\s*[,;])+\s*\)", ")"),
        (r",\s*;", ";"),
        (r";\s*,", ";"),
        (r",\s*,", ","),
        (r"\(\s*\)", ""),
        (r"\(\s+", "("),
        (r"\s+([,;:.])", r"\1"),
        (r"\s+\)", ")"),
        (r"\s+", " "),
    ]
    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned)
    return cleaned.strip()


def candidate_details(extract):
    return textwrap.shorten(clean_extract(extract), width=620, placeholder="…")


def comparable_details(details):
    return re.sub(r"\s+", " ", re.sub(r"\(\s+", "(", details)).strip()


def fetch_json(host, parameters):
    url = f"https://{host}/w/api.php?" + urllib.parse.urlencode(parameters)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"could not query {host}: {error}") from error


def resolve_title(title, aliases):
    for _ in range(10):
        resolved = aliases.get(title)
        if resolved is None:
            return title
        title = resolved
    raise RuntimeError(f"too many Wikipedia aliases while resolving {title}")


def fetch_current_pages(cards):
    requested_by_host = defaultdict(set)
    card_sources = {}
    for card in cards:
        source = card["source"]
        host, source_revision = parse_revision_url(source["adapted_from"])
        article_host, title = parse_article_url(source["url"])
        if host != article_host:
            raise ValueError(f"{card['term']}: article and permalink hosts differ")
        requested_by_host[host].add(title)
        card_sources[card["term"]] = (host, source_revision, title)

    pages = {}
    for host, requested_titles in requested_by_host.items():
        for title_chunk in chunks(sorted(requested_titles), 20):
            response = fetch_json(
                host,
                {
                    "action": "query",
                    "format": "json",
                    "formatversion": 2,
                    "prop": "extracts|revisions",
                    "redirects": 1,
                    "exintro": 1,
                    "explaintext": 1,
                    "exsentences": 2,
                    "rvprop": "ids",
                    "titles": "|".join(title_chunk),
                },
            )
            query = response.get("query", {})
            aliases = {
                alias["from"]: alias["to"]
                for alias in [
                    *query.get("normalized", []),
                    *query.get("redirects", []),
                ]
            }
            pages_by_title = {
                page.get("title"): page for page in query.get("pages", [])
            }
            for requested_title in title_chunk:
                resolved_title = resolve_title(requested_title, aliases)
                page = pages_by_title.get(resolved_title)
                if page is None or page.get("missing"):
                    raise RuntimeError(f"Wikipedia page is missing: {requested_title}")
                revisions = page.get("revisions", [])
                if not revisions or not page.get("extract"):
                    raise RuntimeError(
                        f"Wikipedia page lacks a revision or extract: {requested_title}"
                    )
                pages[(host, requested_title)] = {
                    "revision": revisions[0]["revid"],
                    "details": candidate_details(page["extract"]),
                }

    results = {}
    for term, (host, source_revision, title) in card_sources.items():
        page = pages[(host, title)]
        results[term] = {
            **page,
            "source_revision": source_revision,
            "host": host,
        }
    return results


def description_diff(term, old_details, new_details):
    old_lines = [f"{line}\n" for line in textwrap.wrap(old_details, width=88)]
    new_lines = [f"{line}\n" for line in textwrap.wrap(new_details, width=88)]
    return "".join(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{term} (stored)",
            tofile=f"{term} (Wikipedia now)",
        )
    )


def round_trip_yaml():
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = YAML_WIDTH
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def update_yaml_text(source, updates):
    yaml = round_trip_yaml()
    data = yaml.load(source)
    cards_by_term = {card["term"]: card for card in data["cards"]}

    for term, update in updates.items():
        card = cards_by_term[term]
        if update["details"] is not None:
            card["details"] = FoldedScalarString(update["details"])
        permalink = f"https://{update['host']}/w/index.php?oldid={update['revision']}"
        card["source"]["adapted_from"] = permalink

    output = io.StringIO()
    yaml.dump(data, output)
    return output.getvalue()


def selected_cards(data, terms):
    tracked = [
        card
        for card in data["cards"]
        if is_wikipedia_revision_url(card["source"].get("adapted_from", ""))
    ]
    if not terms:
        return tracked
    by_term = {card["term"]: card for card in tracked}
    missing = [term for term in terms if term not in by_term]
    if missing:
        raise ValueError(
            "unknown or manually maintained terms: " + ", ".join(sorted(missing))
        )
    return [by_term[term] for term in terms]


def check_descriptions(cards, pages):
    drifted = []
    unchanged_revision = 0
    unchanged_text = 0
    for card in cards:
        page = pages[card["term"]]
        if comparable_details(card["details"]) != comparable_details(page["details"]):
            drifted.append(card["term"])
            print(description_diff(card["term"], card["details"], page["details"]))
        elif page["source_revision"] == page["revision"]:
            unchanged_revision += 1
        else:
            unchanged_text += 1
    print(
        f"Checked {len(cards)} descriptions: {unchanged_revision} at the recorded "
        f"revision, {unchanged_text} with unchanged text after later revisions, "
        f"{len(drifted)} with text changes"
    )
    return drifted


def pending_updates(cards, pages):
    updates = {}
    for card in cards:
        page = pages[card["term"]]
        details_changed = comparable_details(card["details"]) != comparable_details(
            page["details"]
        )
        revision_changed = page["source_revision"] != page["revision"]
        if not details_changed and not revision_changed:
            continue
        updates[card["term"]] = {
            "details": page["details"] if details_changed else None,
            "host": page["host"],
            "revision": page["revision"],
        }
    return updates


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare checked-in descriptions with current Wikipedia leads."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="report description drift")
    check.add_argument("terms", nargs="*", help="optional terms to check")
    subparsers.add_parser(
        "update", help="update all tracked descriptions and source revisions"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data = build_deck.validate_data(build_deck.load_data())
    terms = args.terms if args.command == "check" else []
    cards = selected_cards(data, terms)
    pages = fetch_current_pages(cards)
    if args.command == "check":
        if check_descriptions(cards, pages):
            sys.exit(1)
        return

    updates = pending_updates(cards, pages)
    if not updates:
        print("All tracked Wikipedia descriptions are up to date")
        return
    changed_descriptions = [
        term for term, update in updates.items() if update["details"] is not None
    ]
    changed_revision_count = sum(
        page["source_revision"] != page["revision"] for page in pages.values()
    )
    cards_by_term = {card["term"]: card for card in cards}
    for term in changed_descriptions:
        card = cards_by_term[term]
        print(description_diff(term, card["details"], pages[term]["details"]))
    source = build_deck.DATA_PATH.read_text(encoding="utf-8")
    updated = update_yaml_text(source, updates)
    build_deck.DATA_PATH.write_text(updated, encoding="utf-8")
    print(
        f"Updated {len(updates)} cards in {build_deck.DATA_PATH}: "
        f"{len(changed_descriptions)} descriptions and "
        f"{changed_revision_count} source revisions changed"
    )


if __name__ == "__main__":
    main()
