import { writeFile } from "node:fs/promises";

import { foods } from "./foods.mjs";

const proposals = new Map([
  // Meat and charcuterie.
  ["salumi", { core: "Usually pig; cured-meat assortment.", context: "Italian" }],
  ["salame", { core: "Usually pig; cured sausage.", context: "Italian" }],
  ["salsiccia", { core: "Usually pig; sausage.", context: "Italian" }],
  ["soppressata", { core: "Usually pig; coarse, dry-cured salami.", context: "Italian" }],
  ["finocchiona", { core: "Pig; fennel-flavored salami.", context: "Tuscan" }],
  ["mortadella", { core: "Pig; large, mild, cooked sausage." }],
  ["prosciutto", { core: "Pig; dry-cured ham; usually thinly sliced.", context: "Italian; usually means crudo on English menus" }],
  ["prosciutto crudo", { core: "Pig; uncooked, unsmoked, dry-cured ham.", context: "Italian; usually thinly sliced" }],
  ["prosciutto cotto", { core: "Pig; cooked ham.", context: "Italian" }],
  ["speck", { core: "Pig; smoked, dry-cured ham.", context: "South Tyrolean" }],
  ["coppa", { core: "Pig; dry-cured neck or shoulder." }],
  ["capocollo", { core: "Pig; dry-cured neck or shoulder." }],
  ["capicola", { core: "Pig; cured neck or shoulder.", context: "Italian-American name" }],
  ["pancetta", { core: "Pig; salt-cured belly; Italian bacon." }],
  ["guanciale", { core: "Pig; salt-cured cheek or jowl." }],
  ["lardo", { core: "Pig; seasoned, cured back fat." }],
  ["bresaola", { core: "Cow; air-dried, salted beef; thinly sliced." }],
  ["culatello", { core: "Pig; dry-cured, boneless ham." }],
  ["’nduja", { core: "Pig; soft, spicy, spreadable sausage.", context: "Calabrian" }],
  ["cotechino", { core: "Pig; rich, cooked sausage." }],
  ["zampone", { core: "Pig; trotter stuffed with pork sausage." }],
  ["porchetta", { core: "Pig; herb-seasoned roast pork.", context: "Italian" }],
  ["lonza", { core: "Pig; cured or roasted loin." }],
  ["jambon", { core: "Pig; ham.", context: "French" }],
  ["saucisson", { core: "Usually pig; thick, dry-cured sausage.", context: "French" }],
  ["andouille", { core: "Pig; smoked sausage.", context: "style varies by country" }],
  ["andouillette", { core: "Pig; coarse intestine sausage.", context: "French" }],
  ["boudin noir", { core: "Usually pig; blood sausage.", context: "French" }],
  ["boudin blanc", { core: "Animal varies; white sausage without blood.", context: "French; often pig, young cow, or poultry" }],
  ["rillettes", { core: "Animal varies; shredded meat spread.", context: "often pig" }],
  ["pâté", { core: "Animal varies; seasoned meat paste; often liver." }],
  ["terrine", { core: "Animal varies; coarse pâté or layered meat loaf; served cold." }],
  ["lardons", { core: "Pig; small strips or cubes of fatty bacon." }],
  ["confit", { core: "Often duck; slowly cooked and preserved in fat." }],
  ["jamón serrano", { core: "Pig; dry-cured ham.", context: "Spanish" }],
  ["jamón ibérico", { core: "Iberian pig; premium dry-cured ham.", context: "Spanish" }],
  ["chorizo", { core: "Pig; highly seasoned sausage; often paprika-red.", context: "Spanish" }],
  ["morcilla", { core: "Usually pig; blood sausage.", context: "Spanish" }],
  ["sobrasada", { core: "Pig; soft, spreadable, paprika-seasoned sausage.", context: "Spanish" }],
  ["lomo", { core: "Pig; cured tenderloin.", context: "Spanish" }],
  ["manzo", { core: "Cow; beef.", context: "Italian" }],
  ["vitello", { core: "Young cow (calf); veal.", context: "Italian" }],
  ["maiale", { core: "Pig; pork.", context: "Italian" }],
  ["cinghiale", { core: "Wild boar.", context: "Italian" }],
  ["agnello", { core: "Young sheep; lamb.", context: "Italian" }],
  ["capretto", { core: "Young goat; kid.", context: "Italian" }],
  ["anatra", { core: "Duck.", context: "Italian" }],
  ["coniglio", { core: "Rabbit.", context: "Italian" }],
  ["cervo", { core: "Deer; venison.", context: "Italian" }],
  ["faraona", { core: "Guinea fowl.", context: "Italian" }],
  ["bœuf", { core: "Cow; beef.", context: "French" }],
  ["veau", { core: "Young cow (calf); veal.", context: "French" }],
  ["porc", { core: "Pig; pork.", context: "French" }],
  ["agneau", { core: "Young sheep; lamb.", context: "French" }],
  ["canard", { core: "Duck.", context: "French" }],
  ["lapin", { core: "Rabbit.", context: "French" }],
  ["chevreuil", { core: "Roe deer; venison.", context: "French" }],
  ["filet mignon", { core: "Cow; tenderloin steak; small and very tender." }],
  ["entrecôte", { core: "Cow; rib steak; similar to ribeye.", context: "French" }],
  ["onglet", { core: "Cow; hanger steak.", context: "French" }],
  ["bavette", { core: "Cow; flank-style steak.", context: "French" }],
  ["côte de bœuf", { core: "Cow; thick, bone-in rib steak.", context: "French" }],
  ["bistecca", { core: "Usually cow; steak.", context: "Italian" }],
  ["tagliata", { core: "Usually cow; sliced, grilled steak.", context: "Italian" }],
  ["carpaccio", { core: "Meat or fish; paper-thin; raw." }],
  ["osso buco", { core: "Young cow; cross-cut shank; braised with its marrow bone." }],
  ["braciola", { core: "Animal varies; rolled or grilled meat slice.", context: "Italian; meaning varies by region" }],
  ["animelle", { core: "Usually young cow or young sheep; sweetbreads (glands).", context: "Italian" }],
  ["trippa", { core: "Animal varies; tripe; edible stomach lining.", context: "Italian" }],
  ["midollo", { core: "Animal varies; bone marrow.", context: "Italian" }],
  ["ris de veau", { core: "Young cow; sweetbreads.", context: "French; despite the name, not rice" }],
  ["foie gras", { core: "Duck or goose; fatty liver." }],

  // Cheese.
  ["asiago", { core: "Mild when young; firm when aged.", context: "Italian; cow’s milk" }],
  ["bel paese", { core: "Mild, semi-soft cheese.", context: "Italian; cow’s milk" }],
  ["burrata", { core: "Fresh mozzarella pouch filled with cream and curds." }],
  ["caciocavallo", { core: "Firm, stretched-curd cheese.", context: "Southern Italian" }],
  ["caciotta", { core: "Mild, semi-soft farmhouse cheese.", context: "Italian" }],
  ["crescenza", { core: "Soft, mild, creamy cheese.", context: "Italian; cow’s milk" }],
  ["fontina", { core: "Nutty, semi-soft cheese.", context: "From the Alps; cow’s milk" }],
  ["gorgonzola", { core: "Blue cheese.", context: "Italian; cow’s milk" }],
  ["grana padano", { core: "Hard, granular cheese.", context: "Italian; cow’s milk" }],
  ["mascarpone", { core: "Very rich, mild cream cheese.", context: "Italian" }],
  ["montasio", { core: "Firm cheese.", context: "Italian; from the Alps; cow’s milk" }],
  ["mozzarella", { core: "Mild, fresh, stretched-curd cheese." }],
  ["mozzarella di bufala", { core: "Fresh mozzarella made from water-buffalo milk." }],
  ["parmigiano reggiano", { core: "Hard, granular, aged cheese.", context: "Italian; cow’s milk" }],
  ["pecorino", { core: "Sheep’s-milk cheese; a broad family.", context: "Italian" }],
  ["pecorino romano", { core: "Hard, salty sheep’s-milk cheese.", context: "Italian" }],
  ["provolone", { core: "Semi-hard, stretched-curd cheese.", context: "Italian; cow’s milk" }],
  ["ricotta", { core: "Mild, fresh whey cheese with a soft, grainy texture." }],
  ["ricotta salata", { core: "Salted, pressed, aged ricotta for slicing or grating." }],
  ["robiola", { core: "Soft, creamy cheese.", context: "Northern Italian" }],
  ["scamorza", { core: "Semi-soft, pear-shaped, stretched-curd cheese; often smoked." }],
  ["stracchino", { core: "Soft, mild, creamy cheese.", context: "Italian; cow’s milk" }],
  ["taleggio", { core: "Soft, washed-rind cheese.", context: "Italian; cow’s milk" }],
  ["toma", { core: "Semi-soft cheese; milk and style vary.", context: "Alpine-style family" }],
  ["sottocenere", { core: "Semi-soft cheese aged under ash.", context: "Italian; cow’s milk" }],
  ["beaufort", { core: "Firm, nutty cheese.", context: "French; from the Alps; cow’s milk" }],
  ["brie", { core: "Soft, creamy, bloomy-rind cheese.", context: "French; cow’s milk" }],
  ["brillat-savarin", { core: "Very rich, soft, triple-cream cheese.", context: "French" }],
  ["camembert", { core: "Soft, earthy, bloomy-rind cheese.", context: "French; cow’s milk" }],
  ["cantal", { core: "Firm, earthy cheese.", context: "French; cow’s milk" }],
  ["chèvre", { core: "Goat cheese; not one specific style.", context: "French term" }],
  ["comté", { core: "Firm, nutty cheese.", context: "French; Alpine-style; cow’s milk" }],
  ["époisses", { core: "Soft, pungent, washed-rind cheese.", context: "French; cow’s milk" }],
  ["gruyère", { core: "Firm, nutty cheese.", context: "Swiss; Alpine-style; cow’s milk" }],
  ["mimolette", { core: "Firm, orange cheese.", context: "French; cow’s milk" }],
  ["morbier", { core: "Semi-soft cheese marked by a dark ash line.", context: "French" }],
  ["munster", { core: "Soft, pungent, washed-rind cheese.", context: "French; cow’s milk" }],
  ["neufchâtel", { core: "Soft, bloomy-rind cheese.", context: "French; cow’s milk" }],
  ["ossau-iraty", { core: "Firm, nutty sheep’s-milk cheese.", context: "French Basque" }],
  ["pont-l’évêque", { core: "Soft, aromatic, washed-rind cheese.", context: "French; cow’s milk" }],
  ["raclette", { core: "Melting cheese; also the melted-cheese dish.", context: "Alpine-style; cow’s milk" }],
  ["reblochon", { core: "Soft, nutty cheese.", context: "French; from the Alps; cow’s milk" }],
  ["roquefort", { core: "Tangy blue sheep’s-milk cheese.", context: "French" }],
  ["saint-andré", { core: "Very rich, soft, triple-cream cheese.", context: "French" }],
  ["saint-nectaire", { core: "Semi-soft, earthy cheese.", context: "French; cow’s milk" }],
  ["tomme", { core: "Rustic round cheese; not one specific style.", context: "French/Swiss term" }],
  ["triple crème", { core: "Very rich, soft cheese with extra cream added." }],
  ["valençay", { core: "Soft, ash-coated, pyramid-shaped goat cheese.", context: "French" }],
  ["feta", { core: "Salty, crumbly, brined cheese.", context: "usually sheep’s milk; Greek" }],
  ["halloumi", { core: "Firm, brined cheese that holds its shape when grilled.", context: "Cypriot" }],
  ["manchego", { core: "Firm sheep’s-milk cheese.", context: "Spanish" }],
  ["cotija", { core: "Salty, crumbly cheese.", context: "Mexican; cow’s milk" }],
  ["queso fresco", { core: "Mild, fresh, crumbly cheese.", context: "Latin American" }],
  ["quesillo", { core: "Stringy, stretched-curd cheese; Oaxaca cheese.", context: "Mexican" }],
  ["labneh", { core: "Thick, tangy strained yogurt served like a soft cheese." }],
  ["gouda", { core: "Mild when young; caramel-like when aged.", context: "Dutch; cow’s milk" }],
  ["havarti", { core: "Mild, buttery, semi-soft cheese.", context: "Danish; cow’s milk" }],
  ["stilton", { core: "Blue cheese.", context: "English; cow’s milk" }],

  // Other menu traps.
  ["pepperoncini", { core: "Mild, tangy pickled chili peppers.", context: "not meat" }],
  ["peperoncino", { core: "Chili pepper, usually hot.", context: "Italian" }],
  ["peperoni", { core: "Bell peppers.", context: "Italian plural; not pepperoni sausage" }],
  ["giardiniera", { core: "Pickled mixed vegetables.", context: "Italian style" }],
  ["mostarda", { core: "Candied fruit in mustard-flavored syrup.", context: "Northern Italian" }],
  ["bottarga", { core: "Salt-cured fish roe.", context: "usually grated or thinly sliced" }],
  ["acciughe", { core: "Anchovies.", context: "Italian" }],
  ["baccalà", { core: "Salt-cured cod.", context: "Italian" }],
  ["polpo", { core: "Octopus.", context: "Italian" }],
  ["seppia", { core: "Cuttlefish.", context: "Italian" }],
  ["cozze", { core: "Mussels.", context: "Italian" }],
  ["vongole", { core: "Clams.", context: "Italian" }],
  ["scampi", { core: "Small, lobster-like crustaceans.", context: "usage varies by country" }],
  ["carciofi", { core: "Artichokes.", context: "Italian" }],
  ["radicchio", { core: "Bitter red-leaf chicory." }],
  ["rapini", { core: "Bitter leafy green; broccoli rabe." }],
  ["puntarelle", { core: "Crisp, slightly bitter shoots of Catalonian chicory." }],
  ["cavolo nero", { core: "Dark leafy Tuscan cabbage; Italian kale." }],
  ["cipollini", { core: "Small, flat, mildly sweet onions.", context: "Italian" }],
  ["cornichons", { core: "Tiny, tart pickled cucumbers.", context: "French" }],
  ["gremolata", { core: "Chopped parsley, lemon zest, and garlic garnish." }],
  ["tapenade", { core: "Savory olive spread.", context: "Provençal" }],
  ["caponata", { core: "Sweet-and-sour eggplant relish.", context: "Sicilian" }],
]);

const pastaContext = new Map([
  ["busiate", "Sicilian"],
  ["fileja", "Calabrian"],
  ["fregola", "Sardinian"],
  ["malloreddus", "Sardinian"],
  ["pici", "Tuscan"],
  ["scialatielli", "from Campania"],
  ["trofie", "Ligurian"],
]);

const pastaCoreOverrides = new Map([
  ["busiate", "Long, tightly twisted pasta."],
  ["fileja", "Long, narrow corkscrews."],
  ["fregola", "Small toasted pasta balls."],
  ["malloreddus", "Small ridged pasta shells."],
  ["pici", "Thick, hand-rolled spaghetti."],
  ["scialatielli", "Short, thick, flat ribbons."],
  ["trofie", "Short, thin, hand-twisted pasta."],
  ["ziti", "Long, smooth pasta tubes."],
]);

const auditNotes = new Map([
  ["prosciutto", "Clarifies the English-menu default while preserving the broader Italian meaning in context."],
  ["prosciutto crudo", "Adds “unsmoked” from the existing reference/details so it contrasts explicitly with speck."],
  ["speck", "Makes the smoke contrast with prosciutto crudo visually immediate and adds its South Tyrolean context from the existing reference."],
  ["coppa", "Drops “whole-muscle” from the recognition cue; that anatomical detail remains in the existing extra context."],
  ["capocollo", "Drops “whole-muscle” from the recognition cue; that anatomical detail remains in the existing extra context."],
  ["boudin blanc", "Leads with “Animal varies” and preserves the common pig, young-cow, and poultry possibilities in context."],
  ["rillettes", "Leads with “Animal varies” while preserving pig as the common case in context."],
  ["vitello", "Leads with the animal and expands “young cow” to “young cow (calf)”."],
  ["veau", "Leads with the animal and expands “young cow” to “young cow (calf)”."],
  ["entrecôte", "Makes the implied beef (cow) source explicit."],
  ["ris de veau", "Moves the “not rice” mnemonic to context; the food identity remains prominent."],
  ["ziti", "Removes the nonessential habit of breaking the pasta before cooking; the existing extra context retains it."],
  ["asiago", "Leads with its age-dependent texture instead of origin or milk."],
  ["fontina", "Moves “Alpine” to context because it describes geography/style, not a dependable texture."],
  ["montasio", "Moves “Alpine” to context because it describes geography/style, not a dependable texture."],
  ["toma", "Moves “Alpine” to context because it describes geography/style, not a dependable texture."],
  ["beaufort", "Moves “Alpine” to context because it describes geography/style, not a dependable texture."],
  ["comté", "Moves the broad “Alpine-style” classification to context; Comté is geographically from the Jura."],
  ["gruyère", "Moves the broad “Alpine-style” classification to context rather than presenting it as texture."],
  ["raclette", "Moves “Alpine” to context because meltability is the more useful menu characteristic."],
  ["reblochon", "Moves “Alpine” to context because it describes geography/style, not a dependable texture."],
  ["gouda", "Leads with its age-dependent character instead of origin or milk."],
  ["tomme", "Makes explicit that this is a family/term rather than one uniform cheese."],
  ["feta", "Moves its usual milk type to context so the bold cue contains only immediately useful texture and preparation facts."],
]);

function capitalize(text) {
  return `${text[0].toUpperCase()}${text.slice(1)}`;
}

function proposalFor(food) {
  if (food.category === "pasta") {
    return {
      core: pastaCoreOverrides.get(food.term) ?? capitalize(food.headline),
      context: pastaContext.get(food.term),
    };
  }

  const proposal = proposals.get(food.term);
  if (proposal === undefined) {
    throw new Error(`Missing proposal for ${food.category}/${food.term}`);
  }
  return proposal;
}

const proposedTerms = new Set(proposals.keys());
for (const food of foods) {
  if (food.category !== "pasta") {
    proposedTerms.delete(food.term);
  }
}
if (proposedTerms.size !== 0) {
  throw new Error(`Proposals exist for unknown terms: ${[...proposedTerms].join(", ")}`);
}

function withoutTerminalPunctuation(text) {
  return text.replace(/[.!?]+$/u, "");
}

const proposalsByFood = foods.map(food => {
  const proposal = proposalFor(food);
  return { ...food, ...proposal, core: withoutTerminalPunctuation(proposal.core) };
});

const animalLeadPattern = /^(?:Animal varies|Cow|Deer|Duck(?: or goose)?|Guinea fowl|Iberian pig|Meat or fish|Often duck|Pig|Rabbit|Roe deer|Usually cow|Usually pig|Usually young cow or young sheep|Wild boar|Young cow(?: \(calf\))?|Young goat|Young sheep)(?:;|$)/u;
const meatsWithoutAnimalLead = proposalsByFood.filter(food => food.category === "meat" && !animalLeadPattern.test(food.core));
if (meatsWithoutAnimalLead.length !== 0) {
  throw new Error(`Meat proposals without an animal-first cue: ${meatsWithoutAnimalLead.map(food => food.term).join(", ")}`);
}
const categoryLabels = new Map([
  ["pasta", "Pasta"],
  ["meat", "Meat and charcuterie"],
  ["cheese", "Cheese"],
  ["other", "Other menu traps"],
]);

const coreCollisions = [...Map.groupBy(proposalsByFood, food => food.core.toLocaleLowerCase())]
  .map(([, matches]) => matches)
  .filter(matches => matches.length > 1);

const exactRenderingCollisions = [...Map.groupBy(proposalsByFood, food => `${food.core.toLocaleLowerCase()}\n${food.context?.toLocaleLowerCase() ?? ""}`)]
  .map(([, matches]) => matches)
  .filter(matches => matches.length > 1);

function wordCount(text) {
  return text.match(/[\p{L}\p{N}]+/gu)?.length ?? 0;
}

const denseProposals = proposalsByFood.filter(food => wordCount(food.core) > 12 || wordCount(food.context ?? "") > 10);

function renderProposal(food) {
  return `**${food.core}**${food.context === undefined ? "" : `; ${food.context}`}`;
}

function semanticTokens(text) {
  return text.toLocaleLowerCase().match(/[\p{L}\p{N}]+/gu)?.join(" ") ?? "";
}

function isFormattingOnly(food) {
  return food.context === undefined && semanticTokens(food.headline) === semanticTokens(food.core);
}

const formattingOnlyFoods = proposalsByFood.filter(isFormattingOnly);
const substantiveFoods = proposalsByFood.filter(food => !isFormattingOnly(food));
const recognitionData = Object.fromEntries(proposalsByFood.map(food => [
  food.term,
  {
    core: food.core.split("; "),
    context: food.context?.split("; ") ?? [],
  },
]));

const lines = [
  "# Menu Foods headline audit",
  "",
  "> Generated design review: this report does not modify an Anki collection, card template, or source food record.",
  "",
  "## Rendering proposal",
  "",
  "Each card retains structured facts internally but renders one compact sentence-like answer. Bold is a fast visual recognition cue, not a universal grading contract; the learner decides which facts count. The headline has no terminal period, and semicolons are the only separators between the bold cue and normal-weight origin, language, or caveats. Existing long-form details remain below the image and are not included here.",
  "",
  "The proposed ordering is shape first for pasta; animal/form/preparation for meat; texture/style/milk for cheese; and plain-English identity/preparation for other menu traps. The draft preserves the semantic content of the current headline except where an audit note explicitly calls out a clarification.",
  "",
  `Cards audited: ${foods.length}. Substantive rendering changes: ${substantiveFoods.length}. Capitalization/punctuation only: ${formattingOnlyFoods.length}. Density flags: ${denseProposals.length}. Animal-first meat check: ${foods.filter(food => food.category === "meat").length}/${foods.filter(food => food.category === "meat").length}.`,
  "",
  "## Recognition collisions",
  "",
  "These cards intentionally or potentially share the same bold recognition cue. Language and origin may still distinguish them in the unbolded context; each group should be reviewed before implementation.",
  "",
  ...coreCollisions.map(matches => `- ${matches.map(food => `\`${food.term}\``).join(", ")}: ${renderProposal({ ...matches[0], context: undefined })}`),
  "",
  "### Exact rendered-answer collisions",
  "",
  "These remain identical even after including the unbolded context. Synonym pairs may be acceptable; distinct cheeses need either a better differentiator or an explicit decision that the distinction is outside this deck’s learning goal.",
  "",
  ...exactRenderingCollisions.map(matches => `- ${matches.map(food => `\`${food.term}\``).join(", ")}: ${renderProposal(matches[0])}`),
  "",
];

if (denseProposals.length !== 0) {
  lines.push(
    "## Density check",
    "",
    "These drafts exceed 12 words in the bold cue or 10 words in context and deserve an explicit information-overload review.",
    "",
    ...denseProposals.map(food => `- \`${food.term}\`: ${renderProposal(food)}`),
    "",
  );
}

lines.push("## Before/after review", "", "Each category is collapsed by default. Formatting-only cards are counted separately and hidden in a nested list rather than repeated as nearly identical table rows.", "");

for (const [category, label] of categoryLabels) {
  const categoryFoods = proposalsByFood.filter(food => food.category === category);
  const changedFoods = categoryFoods.filter(food => !isFormattingOnly(food));
  const formattingFoods = categoryFoods.filter(isFormattingOnly);
  lines.push(
    "<details>",
    `<summary><strong>${label}</strong>; ${changedFoods.length} substantive; ${formattingFoods.length} formatting-only</summary>`,
    "",
    "| Term | Current headline | Proposed rendering | Audit note |",
    "| --- | --- | --- | --- |",
  );
  for (const food of changedFoods) {
    const note = auditNotes.get(food.term) ?? (pastaContext.has(food.term) ? "Moves regional origin to context; no food facts dropped." : food.context === undefined ? "Reorders or clarifies the same food facts." : "Moves contextual facts after semicolons; food facts preserved.");
    lines.push(`| ${food.term} | ${food.headline} | ${renderProposal(food)} | ${note} |`);
  }
  if (formattingFoods.length !== 0) {
    lines.push(
      "",
      "<details>",
      `<summary>Formatting-only cards (${formattingFoods.length})</summary>`,
      "",
      formattingFoods.map(food => `\`${food.term}\``).join(", "),
      "",
      "</details>",
    );
  }
  lines.push("", "</details>", "");
}

const outputURL = new URL("./headline-audit.md", import.meta.url);
const recognitionURL = new URL("./recognition.json", import.meta.url);
await Promise.all([
  writeFile(outputURL, `${lines.join("\n").trimEnd()}\n`),
  writeFile(recognitionURL, `${JSON.stringify(recognitionData, undefined, 2)}\n`),
]);
console.log(`Wrote ${outputURL.pathname}`);
console.log(`Wrote ${recognitionURL.pathname}`);
console.log(`Audited ${foods.length} cards.`);
console.log(`Bold-core collision groups: ${coreCollisions.length}.`);
console.log(`Exact rendered-answer collision groups: ${exactRenderingCollisions.length}.`);
console.log(`Density flags: ${denseProposals.length}.`);
