import unittest

import build_deck
import build_site

CARDS = build_deck.validate_data(build_deck.load_data())["cards"]


class SiteTests(unittest.TestCase):
    def test_every_reference_links_its_card(self):
        cards_by_key = build_deck.index_cards(CARDS)
        backlinks = build_deck.card_backlinks(CARDS)
        keys_by_term = {card["term"]: build_deck.card_key(card) for card in CARDS}
        for card in CARDS:
            _, back = build_deck.card_sides(card, cards_by_key, backlinks)
            linked = build_site.link_cards(back, card, cards_by_key, keys_by_term)
            self.assertNotIn('<span class="ref">', linked, card["term"])

    def test_references_link_by_their_shown_text(self):
        cards_by_key = build_deck.index_cards(CARDS)
        card = cards_by_key["guanciale"]
        _, back = build_deck.card_sides(
            card, cards_by_key, build_deck.card_backlinks(CARDS)
        )
        linked = build_site.link_cards(
            back,
            card,
            cards_by_key,
            {card["term"]: build_deck.card_key(card) for card in CARDS},
        )
        self.assertIn('<a class="ref" href="#cured meat">cured</a>', linked)
        self.assertIn('<li><b><a href="#pancetta">pancetta</a></b>', linked)

    def test_unknown_references_are_rejected(self):
        card = {"term": "test", "category": "dish", "details": ""}
        with self.assertRaisesRegex(ValueError, "test: can't tell which card"):
            build_site.link_cards('<span class="ref">mystery</span>', card, {}, {})


if __name__ == "__main__":
    unittest.main()
