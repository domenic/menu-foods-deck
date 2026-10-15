import unittest

import build_deck
import reorder_new_cards

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
        note = build_deck.make_note(
            card, model, build_deck.Path(card["image"]), build_deck.index_cards(CARDS)
        )

        self.assertEqual(note.fields[0], "salami / salame")
        self.assertEqual(note.guid, build_deck.genanki.guid_for("menu-food", "salame"))

    def test_meat_headlines_lead_with_the_profile_animal(self):
        cards_by_key = build_deck.index_cards(CARDS)
        self.assertEqual(
            build_deck.headline_fragments(cards_by_key["guanciale"])[0], "pig"
        )
        self.assertEqual(
            build_deck.headline_fragments(cards_by_key["pâté"])[0],
            "pig, duck or chicken",
        )
        data = build_deck.load_data()
        card = next(card for card in data["cards"] if card["term"] == "guanciale")
        del card["profile"]["animal"]
        with self.assertRaisesRegex(
            ValueError, "guanciale: needs a profile animal row"
        ):
            build_deck.validate_data(data)

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

    def test_study_order_interleaves_categories(self):
        first = build_deck.study_order(CARDS)[:30]
        self.assertGreaterEqual(len({card["category"] for card in first}), 5)

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

    def test_example_context_follows_the_core_after_a_comma(self):
        answer = {"core": ["hollow tubes"], "context": ["like penne", "Italian"]}
        self.assertEqual(
            build_deck.recognition_html(answer),
            "<strong>hollow tubes</strong>, like penne; Italian",
        )
        card = {"term": "tube pasta", "category": "pasta", "answer": answer}
        self.assertEqual(build_deck.gloss(card), "hollow tubes, like penne")

    def test_headline_lines_put_each_core_fragment_on_its_own_line(self):
        answer = {"core": ["-ini: smaller", "-oni: bigger"]}
        self.assertEqual(
            build_deck.recognition_html(answer, lines=True),
            "<strong>-ini: smaller<br>-oni: bigger</strong>",
        )

    def test_reordering_moves_new_cards_to_their_study_positions(self):
        positions = reorder_new_cards.study_positions(CARDS)
        self.assertLess(positions["simmered"], positions["braised meat"])
        new_cards = [
            {"cardId": 1, "due": 900, "fields": {"Term": {"value": "simmered"}}},
            {
                "cardId": 2,
                "due": positions["pasta"],
                "fields": {"Term": {"value": "pasta"}},
            },
            {"cardId": 3, "due": 5, "fields": {"Term": {"value": "not a deck card"}}},
        ]
        self.assertEqual(
            reorder_new_cards.plan_moves(new_cards, positions),
            [(1, "simmered", 900, positions["simmered"])],
        )

    def test_served_image_shows_beside_the_uncooked_one(self):
        card = {"term": "penne", "image": "Penne.jpg", "served_image": "Arrabbiata.jpg"}
        rendered = build_deck.image_html(card, "a.jpg", {}, "b.jpg")
        self.assertIn('<figure><img src="a.jpg"><figcaption>uncooked', rendered)
        self.assertIn('<figure><img src="b.jpg"><figcaption>served', rendered)
        self.assertIn("served image source", build_deck.image_credit_html(card, {}))

    def test_served_image_needs_an_image_beside_it(self):
        data = build_deck.load_data()
        card = next(card for card in data["cards"] if card["term"] == "pasta")
        card["served_image"] = "Some_dish.jpg"
        with self.assertRaisesRegex(ValueError, "pasta: served_image needs an image"):
            build_deck.validate_data(data)

    def test_prose_mentions_of_linked_cards_are_marked(self):
        cards_by_key = build_deck.index_cards(CARDS)
        fields = build_deck.note_fields(
            cards_by_key["mascarpone"],
            "",
            cards_by_key,
            build_deck.card_backlinks(CARDS),
        )
        self.assertIn('like <span class="ref">tiramisu</span>', fields[1])

    def test_authored_text_must_use_typographic_quotes(self):
        data = build_deck.load_data()
        card = next(card for card in data["cards"] if card["term"] == "brie")
        card["details"] = "It's soft."
        with self.assertRaisesRegex(ValueError, "brie: use typographic quotes"):
            build_deck.validate_data(data)

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


if __name__ == "__main__":
    unittest.main()
