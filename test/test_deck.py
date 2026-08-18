import re
import unittest

import genanki

import build_deck

DATA = build_deck.validate_data(build_deck.load_data())
CARDS = DATA["cards"]
CARDS_BY_TERM = {card["term"]: card for card in CARDS}


class DeckDataTests(unittest.TestCase):
    def test_expected_size_and_category_balance(self):
        self.assertEqual(len(CARDS), 212)
        self.assertEqual(
            {
                category: sum(card["category"] == category for card in CARDS)
                for category in build_deck.CATEGORIES
            },
            {"pasta": 59, "meat": 72, "cheese": 58, "other": 23},
        )

    def test_terms_images_and_guids_are_unique(self):
        self.assertEqual(len({card["term"] for card in CARDS}), len(CARDS))
        self.assertEqual(len({card["image"] for card in CARDS}), len(CARDS))
        self.assertEqual(
            len({genanki.guid_for("menu-food", card["term"]) for card in CARDS}),
            len(CARDS),
        )

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

    def test_representative_renderings(self):
        self.assertEqual(
            build_deck.recognition_html(CARDS_BY_TERM["feta"]["answer"]),
            "<strong>Salty, crumbly, brined cheese</strong>; usually sheep’s milk; Greek",
        )
        self.assertEqual(
            build_deck.recognition_html(CARDS_BY_TERM["prosciutto crudo"]["answer"]),
            "<strong>Pig; uncooked, unsmoked, dry-cured ham</strong>; Italian; usually thinly sliced",
        )
        self.assertEqual(
            build_deck.recognition_html(CARDS_BY_TERM["ziti"]["answer"]),
            "<strong>Long, smooth pasta tubes</strong>",
        )

    def test_model_retains_compact_desktop_and_night_mode_styles(self):
        model = build_deck.make_model(DATA["deck"])
        self.assertIn(".headline strong", model.css)
        self.assertIn("max-height: min(300px, 34vh)", model.css)
        self.assertIn(".nightMode", model.css)

    def test_image_signatures_override_bad_server_mime_types(self):
        self.assertEqual(
            build_deck.extension_for_content(
                b"\xff\xd8\xffexample", "application/x-www-form-urlencoded"
            ),
            "jpg",
        )


if __name__ == "__main__":
    unittest.main()
