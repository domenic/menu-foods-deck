import re
import unittest

import build_deck
import wikipedia_descriptions

CARDS = build_deck.validate_data(build_deck.load_data())["cards"]


class DeckDataTests(unittest.TestCase):
    def test_model_schema_has_stable_ids(self):
        model = build_deck.make_model(build_deck.load_data()["deck"])
        self.assertEqual(
            [field["name"] for field in model.fields],
            [
                "Term",
                "Headline",
                "Image",
                "Details",
                "Reference",
                "Image Credit",
                "Category",
            ],
        )
        self.assertEqual(
            [field["id"] for field in model.fields],
            [
                6064286510114836544,
                7562720696105355688,
                4862974160591875216,
                5184221410199971603,
                2960379663213147101,
                4601177655232819196,
                3547631925314965014,
            ],
        )
        self.assertEqual(model.templates[0]["id"], 1746720810477752110)

    def test_card_id_preserves_guid_when_term_changes(self):
        card = next(card for card in CARDS if card.get("id") == "salame")
        model = build_deck.make_model(build_deck.load_data()["deck"])
        note = build_deck.make_note(card, model, build_deck.Path(card["image"]))

        self.assertEqual(note.fields[0], "salami / salame")
        self.assertEqual(note.guid, build_deck.genanki.guid_for("menu-food", "salame"))

    def test_every_meat_cue_leads_with_its_animal(self):
        animal_leads = {
            "animal varies",
            "cow",
            "deer",
            "duck",
            "duck or goose",
            "guinea fowl",
            "Iberian pig",
            "meat or fish",
            "often duck",
            "pig",
            "rabbit",
            "roe deer",
            "usually cow",
            "usually pig",
            "usually young cow or young sheep",
            "wild boar",
            "young cow",
            "young cow (calf)",
            "young goat",
            "young sheep",
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
            r"\b(?:cow|sheep|goat|buffalo|water-buffalo)[’'s-]*(?:milk|cheese)\b"
        )
        context_only = re.compile(
            r"\b(?:aromatic|bloomy-rind|strong-smelling|washed-rind)\b"
        )
        for card in CARDS:
            if card["category"] != "cheese" or build_deck.is_reworked(card):
                continue
            core = "; ".join(card["answer"]["core"])
            if animal_milk.search(core):
                self.assertIn(card["term"], milk_identity_terms)
            self.assertIsNone(context_only.search(core), card["term"])

    def test_reworked_cards_must_link_the_jargon_they_use(self):
        data = build_deck.load_data()
        card = next(card for card in data["cards"] if card["term"] == "whey")
        card["answer"]["core"] = ["the liquid left over from curds"]
        with self.assertRaisesRegex(
            ValueError, "whey: uses .curds. without building on .curds."
        ):
            build_deck.validate_data(data)

    def test_dependency_cycles_are_rejected(self):
        data = build_deck.load_data()
        card = next(card for card in data["cards"] if card["term"] == "curds")
        card["details"] += " See [[whey]]."
        with self.assertRaisesRegex(ValueError, "dependency cycle: .*curds"):
            build_deck.validate_data(data)

    def test_study_order_puts_prerequisites_first(self):
        order = [build_deck.card_key(card) for card in build_deck.study_order(CARDS)]
        cards_by_key = build_deck.index_cards(CARDS)
        for card in CARDS:
            key = build_deck.card_key(card)
            for dependency in build_deck.dependencies(card, cards_by_key):
                self.assertLess(order.index(dependency), order.index(key), key)

    def test_kind_of_inherits_and_overrides_the_parent_profile(self):
        cards_by_key = build_deck.index_cards(CARDS)
        profile = build_deck.merged_profile(
            cards_by_key["mozzarella di bufala"], cards_by_key
        )
        self.assertEqual(profile["milk"], ["water buffalo"])
        self.assertEqual(profile["family"], "stretched-curd")

    def test_reworked_details_render_profile_glosses_and_references(self):
        cards_by_key = build_deck.index_cards(CARDS)
        backlinks = build_deck.card_backlinks(CARDS)
        burrata = build_deck.details_html(
            cards_by_key["burrata"], cards_by_key, backlinks.get("burrata", {})
        )
        self.assertIn(
            "<dt>rind</dt><dd>none</dd>",
            burrata,
        )
        self.assertIn(
            '<span class="ref">stretched-curd</span> <span class="gloss">(',
            burrata,
        )
        self.assertIn("<li><b>stracciatella (cheese)</b>: ", burrata)
        self.assertIn("burrata", backlinks["stretched-curd cheese"]["examples"])

    def test_headlines_must_order_adjectives_consistently(self):
        data = build_deck.load_data()
        card = next(card for card in data["cards"] if card["term"] == "brie")
        card["answer"]["core"] = ["buttery, soft, bloomy-rind cheese"]
        with self.assertRaisesRegex(
            ValueError, "brie: headline puts firmness 'soft' after flavor 'buttery'"
        ):
            build_deck.validate_data(data)

    def test_image_from_borrows_another_cards_image(self):
        cards_by_key = build_deck.index_cards(CARDS)
        self.assertEqual(
            build_deck.card_image(cards_by_key["fresco"], cards_by_key),
            cards_by_key["fresh cheese"]["image"],
        )

    def test_prose_mentions_of_linked_cards_are_marked(self):
        cards_by_key = build_deck.index_cards(CARDS)
        fields = build_deck.note_fields(
            cards_by_key["mascarpone"],
            "",
            cards_by_key,
            build_deck.card_backlinks(CARDS),
        )
        self.assertIn('like <span class="ref">tiramisu</span>', fields[1])

    def test_text_html_renders_references(self):
        self.assertEqual(
            build_deck.text_html("a [[curds]] & [[aged cheese|aging]]"),
            'a <span class="ref">curds</span> &amp; <span class="ref">aging</span>',
        )

    def test_recognition_html_bolds_core_and_escapes_fragments(self):
        self.assertEqual(
            build_deck.recognition_html(
                {
                    "core": ["animal & preparation", "crucial trait"],
                    "context": ["optional <context>"],
                }
            ),
            "<strong>animal &amp; preparation; crucial trait</strong>; optional &lt;context&gt;",
        )

    def test_source_html_renders_yaml_literally(self):
        self.assertEqual(
            build_deck.source_html(
                {
                    "label": "Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Feta",
                    "adapted_from": "https://en.wikipedia.org/w/index.php?oldid=123&x=1",
                }
            ),
            '<a href="https://en.wikipedia.org/wiki/Feta">Wikipedia</a> (adapted from <a href="https://en.wikipedia.org/w/index.php?oldid=123&amp;x=1">permalink</a>)',
        )
        self.assertEqual(
            build_deck.source_html(
                {
                    "label": "Other & source",
                    "url": "https://example.com/?a=1&b=2",
                }
            ),
            '<a href="https://example.com/?a=1&amp;b=2">Other &amp; source</a>',
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
    source:
      label: Wikipedia
      url: https://en.wikipedia.org/wiki/Alpha
      adapted_from: https://en.wikipedia.org/w/index.php?oldid=1
  - term: beta
    details: >-
      Leave beta alone.
    source:
      label: Example
      url: https://example.com/beta
  - term: gamma
    details: >-
      Keep gamma's wrapping and text.
    source:
      label: Wikipedia
      url: https://en.wikipedia.org/wiki/Gamma
      adapted_from: https://en.wikipedia.org/w/index.php?oldid=3
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
            "adapted_from: https://en.wikipedia.org/w/index.php?oldid=2", updated
        )
        self.assertIn("url: https://en.wikipedia.org/wiki/Alpha", updated)
        self.assertIn("      Leave beta alone.\n", updated)
        self.assertIn("      Keep gamma's wrapping and text.\n", updated)
        self.assertIn(
            "adapted_from: https://en.wikipedia.org/w/index.php?oldid=4", updated
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
