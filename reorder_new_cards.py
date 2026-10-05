"""Puts the deck's unstudied cards in an Anki collection into the current study
order, through the AnkiConnect add-on.

Importing a package gives newly added cards their study-order positions, but
leaves the positions of cards that were already waiting unchanged, and those
drift as releases change the order. This sets every new card's position to its
place in the current order. Cards that now come before ones you've already
studied move to the front of the queue. Run it after importing; without
`--apply`, it only reports what it would change.
"""

import argparse
import html
import json
import urllib.request

import build_deck


def ankiconnect(url, action, **params):
    request = urllib.request.Request(
        url,
        json.dumps({"action": action, "version": 6, "params": params}).encode(),
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.load(response)
    if result["error"]:
        raise RuntimeError(f"{action}: {result['error']}")
    return result["result"]


def study_positions(cards):
    """Maps each card's term, as the note's Term field holds it, to its position."""
    return {
        html.escape(card["term"]): position
        for position, card in enumerate(build_deck.study_order(cards))
    }


def plan_moves(new_cards, positions):
    """Returns (card ID, term, old position, new position) for every new card
    whose position differs from its study-order position."""
    moves = []
    for card in new_cards:
        term = card["fields"]["Term"]["value"]
        target = positions.get(term)
        if target is not None and card["due"] != target:
            moves.append((card["cardId"], term, card["due"], target))
    return moves


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--url", default="http://localhost:8765", help="AnkiConnect URL"
    )
    parser.add_argument("--deck", help="deck name (default: the package's)")
    parser.add_argument("--apply", action="store_true", help="change the collection")
    args = parser.parse_args()

    data = build_deck.validate_data(build_deck.load_data())
    positions = study_positions(data["cards"])
    deck = args.deck or data["deck"]["name"]
    query = f'"deck:{deck}" is:new "note:{data["deck"]["model"]["name"]}"'
    card_ids = ankiconnect(args.url, "findCards", query=query)
    new_cards = ankiconnect(args.url, "cardsInfo", cards=card_ids)
    unknown = sorted(
        card["fields"]["Term"]["value"]
        for card in new_cards
        if card["fields"]["Term"]["value"] not in positions
    )
    moves = plan_moves(new_cards, positions)

    print(f"{len(new_cards)} new cards; {len(moves)} need a new position.")
    if unknown:
        print(f"Not in this deck's data, left alone: {', '.join(unknown)}")
    upcoming = sorted(
        (
            positions.get(card["fields"]["Term"]["value"], card["due"]),
            card["fields"]["Term"]["value"],
        )
        for card in new_cards
    )
    print("New cards will come in this order:")
    for _, term in upcoming[:15]:
        print(f"  {html.unescape(term)}")
    if len(upcoming) > 15:
        print(f"  … and {len(upcoming) - 15} more")

    if not args.apply:
        print("Dry run; rerun with --apply to change the collection.")
        return
    actions = [
        {
            "action": "setSpecificValueOfCard",
            "version": 6,
            "params": {"card": card_id, "keys": ["due"], "newValues": [target]},
        }
        for card_id, _, _, target in moves
    ]
    for start in range(0, len(actions), 100):
        results = ankiconnect(args.url, "multi", actions=actions[start : start + 100])
        failed = [r for r in results if r["error"] or r["result"] != [True]]
        if failed:
            raise RuntimeError(f"AnkiConnect couldn't set some positions: {failed[:3]}")
    print(f"Moved {len(moves)} cards.")


if __name__ == "__main__":
    main()
