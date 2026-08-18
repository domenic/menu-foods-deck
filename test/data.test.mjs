import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { foods } from "../foods.mjs";

const recognition = JSON.parse(await readFile(new URL("../recognition.json", import.meta.url), "utf8"));
const wikipediaPages = new Map(JSON.parse(await readFile(new URL("../wikipedia-cache.json", import.meta.url), "utf8")));

const expectedCategoryCounts = {
  pasta: 59,
  meat: 72,
  cheese: 58,
  other: 23,
};

test("the deck has the expected size and category balance", () => {
  assert.equal(foods.length, 212);
  assert.deepEqual(
    Object.fromEntries(Object.keys(expectedCategoryCounts).map(category => [
      category,
      foods.filter(food => food.category === category).length,
    ])),
    expectedCategoryCounts,
  );
});

test("food records have unique terms and complete source fields", () => {
  const terms = foods.map(food => food.term);
  assert.equal(new Set(terms).size, terms.length);

  for (const food of foods) {
    assert.ok(Object.hasOwn(expectedCategoryCounts, food.category), `${food.term} has an unknown category`);
    for (const field of ["term", "headline", "wiki"]) {
      assert.equal(typeof food[field], "string", `${food.term} has a non-string ${field}`);
      assert.notEqual(food[field].length, 0, `${food.term} has an empty ${field}`);
    }
    assert.ok(food.referenceURL === undefined || food.details !== undefined, `${food.term} has a custom reference without custom details`);
    assert.ok(food.referenceLabel === undefined || food.referenceURL !== undefined, `${food.term} has a custom reference label without a URL`);
  }
});

test("structured recognition data covers every term exactly once", () => {
  assert.deepEqual(Object.keys(recognition).sort(), foods.map(food => food.term).sort());

  for (const [term, answer] of Object.entries(recognition)) {
    assert.ok(Array.isArray(answer.core) && answer.core.length > 0, `${term} needs at least one bold cue`);
    assert.ok(Array.isArray(answer.context), `${term} needs a context array`);
    for (const fragment of [...answer.core, ...answer.context]) {
      assert.equal(typeof fragment, "string", `${term} has a non-string recognition fragment`);
      assert.notEqual(fragment.length, 0, `${term} has an empty recognition fragment`);
      assert.doesNotMatch(fragment, /[;.!?]$/u, `${term} has forbidden terminal punctuation`);
    }
  }
});

test("every meat recognition cue leads with its animal", () => {
  const animalLead = /^(?:Animal varies|Cow|Deer|Duck(?: or goose)?|Guinea fowl|Iberian pig|Meat or fish|Often duck|Pig|Rabbit|Roe deer|Usually cow|Usually pig|Usually young cow or young sheep|Wild boar|Young cow(?: \(calf\))?|Young goat|Young sheep)$/u;
  for (const food of foods.filter(food => food.category === "meat")) {
    assert.match(recognition[food.term].core[0], animalLead, `${food.term} does not lead with an animal`);
  }
});

test("cheese cores reserve milk types for identity terms and avoid rind jargon", () => {
  const milkIdentityTerms = new Set(["mozzarella di bufala", "pecorino", "pecorino romano", "chèvre"]);
  const animalMilk = /\b(?:cow|sheep|goat|buffalo|water-buffalo)[’'s-]*(?:milk|cheese)\b/iu;
  const contextOnlyVocabulary = /\b(?:aromatic|bloomy-rind|strong-smelling|washed-rind)\b/iu;

  for (const food of foods.filter(food => food.category === "cheese")) {
    const core = recognition[food.term].core.join("; ");
    if (animalMilk.test(core)) {
      assert.ok(milkIdentityTerms.has(food.term), `${food.term} puts a non-identity milk type in its bold cue`);
    }
    assert.doesNotMatch(core, contextOnlyVocabulary, `${food.term} puts context-only cheese vocabulary in its bold cue`);
  }
});

test("every card has a distinct effective image source", () => {
  const imageKeys = foods.map(food => food.cardImageTitle ?? food.wiki);
  assert.equal(new Set(imageKeys).size, imageKeys.length);
});

test("the checked-in Wikipedia cache covers every source page", () => {
  for (const food of foods) {
    const page = wikipediaPages.get(food.wiki);
    assert.ok(page && !page.missing, `${food.term} is missing its Wikipedia page`);
    assert.equal(typeof page.extract, "string", `${food.term} is missing its Wikipedia extract`);
    assert.ok(page.thumbnail?.source, `${food.term} is missing its Wikipedia image`);
    assert.ok(page.fullurl, `${food.term} is missing its Wikipedia URL`);
  }
});
