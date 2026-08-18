import re
import unittest

import build_deck
import wikipedia_descriptions

CARDS = build_deck.validate_data(build_deck.load_data())["cards"]


class DeckDataTests(unittest.TestCase):
    def test_every_meat_cue_leads_with_its_animal(self):
        animal_leads = {
            "Animal varies",
            "Cow",
            "Deer",
            "Duck",
            "Duck or goose",
            "Guinea fowl",
            "Iberian pig",
            "Meat or fish",
            "Often duck",
            "Pig",
            "Rabbit",
            "Roe deer",
            "Usually cow",
            "Usually pig",
            "Usually young cow or young sheep",
            "Wild boar",
            "Young cow",
            "Young cow (calf)",
            "Young goat",
            "Young sheep",
        }
        for card in CARDS:
            if card["category"] == "meat":
                self.assertIn(card["answer"]["core"][0], animal_leads, card["term"])

    def test_cheese_core_vocabulary_policy(self):
        milk_identity_terms = {
            "mozzarella di bufala",
            "pecorino",
            "pecorino romano",
            "chèvre",
        }
        animal_milk = re.compile(
            r"\b(?:cow|sheep|goat|buffalo|water-buffalo)[’'s-]*(?:milk|cheese)\b",
            re.IGNORECASE,
        )
        context_only = re.compile(
            r"\b(?:aromatic|bloomy-rind|strong-smelling|washed-rind)\b",
            re.IGNORECASE,
        )
        for card in CARDS:
            if card["category"] != "cheese":
                continue
            core = "; ".join(card["answer"]["core"])
            if animal_milk.search(core):
                self.assertIn(card["term"], milk_identity_terms)
            self.assertIsNone(context_only.search(core), card["term"])

    def test_recognition_html_bolds_core_and_escapes_fragments(self):
        self.assertEqual(
            build_deck.recognition_html(
                {
                    "core": ["Animal & preparation", "crucial trait"],
                    "context": ["optional <context>"],
                }
            ),
            "<strong>Animal &amp; preparation; crucial trait</strong>; optional &lt;context&gt;",
        )

    def test_image_signatures_override_bad_server_mime_types(self):
        self.assertEqual(
            build_deck.extension_for_content(
                b"\xff\xd8\xffexample", "application/x-www-form-urlencoded"
            ),
            "jpg",
        )

    def test_wikipedia_description_cleanup(self):
        self.assertEqual(
            wikipedia_descriptions.clean_extract(
                "Feta ( FET-ə; English: ,) is cheese. It is brined. Third sentence."
            ),
            "Feta (FET-ə) is cheese. It is brined. Third sentence.",
        )

    def test_description_updates_preserve_other_cards(self):
        source = """schema: 1
cards:
  - term: alpha
    details: >-
      Old alpha.
    details_source: https://en.wikipedia.org/w/index.php?oldid=1
    reference:
      url: https://en.wikipedia.org/wiki/Alpha
  - term: beta
    details: >-
      Leave beta alone.
    reference:
      url: https://example.com/beta
  - term: gamma
    details: >-
      Keep gamma's wrapping and text.
    details_source: https://en.wikipedia.org/w/index.php?oldid=3
    reference:
      url: https://en.wikipedia.org/wiki/Gamma
"""
        updated = wikipedia_descriptions.update_yaml_text(
            source,
            {
                "alpha": {
                    "details": "New alpha.",
                    "host": "en.wikipedia.org",
                    "revision": 2,
                },
                "gamma": {
                    "details": None,
                    "host": "en.wikipedia.org",
                    "revision": 4,
                },
            },
        )
        self.assertIn("      New alpha.\n", updated)
        self.assertIn(
            "details_source: https://en.wikipedia.org/w/index.php?oldid=2", updated
        )
        self.assertIn("      Leave beta alone.\n", updated)
        self.assertIn("      Keep gamma's wrapping and text.\n", updated)
        self.assertIn(
            "details_source: https://en.wikipedia.org/w/index.php?oldid=4", updated
        )

    def test_description_update_round_trip_preserves_unchanged_yaml(self):
        source = build_deck.DATA_PATH.read_text(encoding="utf-8")
        self.assertEqual(wikipedia_descriptions.update_yaml_text(source, {}), source)

    def test_bulk_description_updates_exclude_unchanged_cards(self):
        cards = [
            {"term": "alpha", "details": "Same ( alpha)."},
            {"term": "beta", "details": "Old beta."},
        ]
        pages = {
            "alpha": {
                "details": "Same (alpha).",
                "host": "en.wikipedia.org",
                "source_revision": 1,
                "revision": 2,
            },
            "beta": {
                "details": "New beta.",
                "host": "en.wikipedia.org",
                "source_revision": 2,
                "revision": 3,
            },
        }
        updates = wikipedia_descriptions.pending_updates(cards, pages)
        self.assertEqual(set(updates), {"alpha", "beta"})
        self.assertIsNone(updates["alpha"]["details"])
        self.assertEqual(updates["beta"]["details"], "New beta.")


if __name__ == "__main__":
    unittest.main()
