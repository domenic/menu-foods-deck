import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";

import { foods } from "./foods.mjs";

const ankiConnectURL = process.env.ANKI_CONNECT_URL ?? "http://127.0.0.1:8765";
const modelName = "Menu Food Recognition";
const parentDeck = "Menu Foods";
const wikipediaCachePath = new URL("./wikipedia-cache.json", import.meta.url);
const recognitionPath = new URL("./recognition.json", import.meta.url);
const recognitionByTerm = new Map(Object.entries(JSON.parse(await readFile(recognitionPath, "utf8"))));

const categories = {
  pasta: { deck: parentDeck, label: "Pasta" },
  meat: { deck: parentDeck, label: "Meat & charcuterie" },
  cheese: { deck: parentDeck, label: "Cheese" },
  other: { deck: parentDeck, label: "Other menu trap" },
};

const obsoleteSubdecks = [
  `${parentDeck}::Pasta`,
  `${parentDeck}::Meat & charcuterie`,
  `${parentDeck}::Cheese`,
  `${parentDeck}::Other menu traps`,
];

const frontTemplate = `<div class="term">{{Term}}</div>`;

const backTemplate = `{{FrontSide}}
<hr id="answer">
<div class="category">{{Category}}</div>
<div class="headline">{{Headline}}</div>
{{#Image}}<div class="food-image">{{Image}}</div>{{/Image}}
{{#Details}}
<section class="extra">
  <h2>Extra context <span>— not part of the answer</span></h2>
  <div>{{Details}}</div>
</section>
{{/Details}}
<footer>{{Reference}}{{#ImageCredit}}<span aria-hidden="true"> · </span>{{ImageCredit}}{{/ImageCredit}}</footer>`;

const styling = `
.card {
  --background: #fffaf2;
  --text: #211d18;
  --muted: #6f665d;
  --accent: #a23f2c;
  --panel: #f3eadc;
  background: var(--background);
  color: var(--text);
  font-family: ui-rounded, "Avenir Next", Avenir, system-ui, sans-serif;
  font-size: 20px;
  line-height: 1.45;
  margin: 0 auto;
  max-width: 760px;
  padding: 32px 22px;
  text-align: center;
}

.card.nightMode,
.card.night_mode,
.nightMode .card,
.night_mode .card {
  --background: #211d18;
  --text: #fffaf2;
  --muted: #c6baac;
  --accent: #f39a7f;
  --panel: #332b24;
}

.term {
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(2.2rem, 9vw, 3.7rem);
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.05;
  overflow-wrap: anywhere;
}

#answer {
  border: 0;
  border-top: 1px solid rgb(128 105 86 / 35%);
  margin: 28px auto 20px;
  width: min(14rem, 60%);
}

.category {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  margin-bottom: 7px;
  text-transform: uppercase;
}

.headline {
  font-size: clamp(1.25rem, 4vw, 1.65rem);
  font-weight: 500;
  line-height: 1.25;
  margin: 0 auto 22px;
  max-width: 34rem;
}

.headline strong {
  font-weight: 800;
}

.food-image img {
  background: var(--panel);
  border-radius: 14px;
  box-shadow: 0 8px 26px rgb(42 28 18 / 15%);
  height: auto;
  max-height: 380px;
  max-width: 100%;
  object-fit: contain;
}

.extra {
  background: var(--panel);
  border-radius: 12px;
  color: var(--text);
  margin: 24px 0 16px;
  padding: 17px 20px 19px;
  text-align: left;
}

.extra h2 {
  color: var(--muted);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}

.extra h2 span {
  font-weight: 500;
  letter-spacing: 0;
  text-transform: none;
}

footer {
  color: var(--muted);
  font-size: 0.72rem;
  margin-top: 16px;
}

a {
  color: var(--accent);
}

@media (min-width: 700px) {
  .card {
    box-sizing: border-box;
    font-size: 18px;
    line-height: 1.35;
    padding: 10px 18px 18px;
  }

  .term {
    font-size: clamp(2rem, 5vw, 3.25rem);
  }

  #answer {
    margin: 16px auto 10px;
  }

  .category {
    margin-bottom: 4px;
  }

  .headline {
    margin-bottom: 12px;
  }

  .food-image {
    line-height: 0;
  }

  .food-image img {
    max-height: min(300px, 34vh);
    max-width: min(100%, 640px);
  }

  .extra {
    font-size: 0.9rem;
    line-height: 1.35;
    margin: 14px 0 8px;
    padding: 12px 16px 14px;
  }

  .extra h2 {
    margin-bottom: 4px;
  }

  footer {
    margin-top: 8px;
  }
}
`;

function escapeHTML(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function validateRecognitionData() {
  const foodTerms = new Set(foods.map(food => food.term));
  const missingTerms = foods.filter(food => !recognitionByTerm.has(food.term)).map(food => food.term);
  const extraTerms = [...recognitionByTerm.keys()].filter(term => !foodTerms.has(term));
  const malformedTerms = [];
  for (const [term, recognition] of recognitionByTerm) {
    if (!Array.isArray(recognition.core) || recognition.core.length === 0 || !Array.isArray(recognition.context) || [...recognition.core, ...recognition.context].some(part => typeof part !== "string" || part.length === 0 || /[;.!?]$/u.test(part))) {
      malformedTerms.push(term);
    }
  }
  if (missingTerms.length || extraTerms.length || malformedTerms.length) {
    throw new Error(`Invalid recognition data: missing=${missingTerms.join(", ") || "none"}; extra=${extraTerms.join(", ") || "none"}; malformed=${malformedTerms.join(", ") || "none"}`);
  }
}

function recognitionHTML(food) {
  const recognition = recognitionByTerm.get(food.term);
  const core = recognition.core.map(escapeHTML).join("; ");
  const context = recognition.context.map(escapeHTML);
  return `<strong>${core}</strong>${context.length === 0 ? "" : `; ${context.join("; ")}`}`;
}

validateRecognitionData();

function cleanWikipediaExtract(extract) {
  return extract
    // Wikipedia's plain-text API can strip pronunciation templates while leaving their labels and punctuation behind.
    .replaceAll(/\b(?:also\s+)?(?:UK|US|English)(?:\s+also)?(?::)?\s*(?=[,;)])/gi, "")
    .replaceAll(/\(\s*(?:[,;]\s*)+/g, "(")
    .replaceAll(/\s*[,;]\s*\)/g, ")")
    .replaceAll(/,\s*;/g, ";")
    .replaceAll(/;\s*,/g, ";")
    .replaceAll(/,\s*,/g, ",")
    .replaceAll(/\(\s*\)/g, "")
    .replaceAll(/\s+([,;:.])/g, "$1")
    .replaceAll(/\s+\)/g, ")")
    .replaceAll(/\s+/g, " ")
    .trim();
}

function firstTwoSentences(extract) {
  const clean = cleanWikipediaExtract(extract);
  if (!clean) {
    return "";
  }

  const segments = [...new Intl.Segmenter("en", { granularity: "sentence" }).segment(clean)];
  const firstTwo = segments.slice(0, 2).map(({ segment }) => segment.trim()).join(" ");
  if (firstTwo.length <= 620) {
    return firstTwo;
  }

  const shortened = firstTwo.slice(0, 617);
  const lastSpace = shortened.lastIndexOf(" ");
  return `${shortened.slice(0, lastSpace)}…`;
}

function chunks(values, size) {
  const result = [];
  for (let index = 0; index < values.length; index += size) {
    result.push(values.slice(index, index + size));
  }
  return result;
}

async function fetchJSON(url, options = undefined) {
  for (let attempt = 0; attempt < 5; ++attempt) {
    const response = await fetch(url, {
      ...options,
      headers: {
        "User-Agent": "menu-foods-deck/1.0 (https://github.com/domenic/menu-foods-deck)",
        ...options?.headers,
      },
    });
    if (response.ok) {
      return response.json();
    }
    if (response.status !== 429 || attempt === 4) {
      throw new Error(`${response.status} ${response.statusText} for ${url}`);
    }
    const retryAfterSeconds = Number(response.headers.get("retry-after")) || 1 + attempt;
    await new Promise(resolve => setTimeout(resolve, retryAfterSeconds * 1000));
  }
}

async function loadWikipediaPages() {
  const requestedTitles = [...new Set(foods.map(({ wiki }) => wiki))];
  let result = new Map();
  try {
    const cachedPages = JSON.parse(await readFile(wikipediaCachePath, "utf8"));
    result = new Map(cachedPages);
  } catch (error) {
    if (error.code !== "ENOENT") {
      throw error;
    }
  }

  const titlesToFetch = requestedTitles.filter(title => !result.has(title));
  if (!titlesToFetch.length) {
    return applyImageTitleOverrides(result);
  }

  for (const titleChunk of chunks(titlesToFetch, 20)) {
    const url = new URL("https://en.wikipedia.org/w/api.php");
    url.search = new URLSearchParams({
      action: "query",
      format: "json",
      formatversion: "2",
      origin: "*",
      redirects: "1",
      prop: "extracts|info|pageimages",
      exintro: "1",
      exlimit: "max",
      explaintext: "1",
      inprop: "url",
      piprop: "thumbnail|name",
      pilimit: "max",
      pithumbsize: "640",
      titles: titleChunk.join("|"),
    });

    const data = await fetchJSON(url);
    const aliases = new Map();
    for (const { from, to } of [...(data.query.normalized ?? []), ...(data.query.redirects ?? [])]) {
      aliases.set(from, to);
    }
    const pagesByTitle = new Map(data.query.pages.map(page => [page.title, page]));

    for (const requestedTitle of titleChunk) {
      let resolvedTitle = requestedTitle;
      for (let index = 0; index < 4 && aliases.has(resolvedTitle); ++index) {
        resolvedTitle = aliases.get(resolvedTitle);
      }
      result.set(requestedTitle, pagesByTitle.get(resolvedTitle));
    }
    await new Promise(resolve => setTimeout(resolve, 250));
  }

  const pagesWithoutImages = titlesToFetch
    .map(title => [title, result.get(title)])
    .filter(([, page]) => page && !page.missing && !page.thumbnail?.source);
  await runWithConcurrency(pagesWithoutImages, 2, async ([title, page]) => {
    const food = foods.find(candidate => candidate.wiki === title);
    const image = await loadCommonsImage(food?.imageQuery ?? title, food?.imageTitle);
    if (image) {
      page.thumbnail = { source: image.source };
      page.pageimage = image.filename;
      page.imageCreditURL = image.creditURL;
      page.fallbackImageTitle = image.title;
    }
  });

  await writeFile(wikipediaCachePath, `${JSON.stringify([...result], undefined, 2)}\n`);

  return applyImageTitleOverrides(result);
}

function applyImageTitleOverrides(pages) {
  for (const food of foods.filter(({ imageTitle }) => imageTitle)) {
    const page = pages.get(food.wiki);
    if (!page) {
      continue;
    }
    const filename = food.imageTitle.replace(/^File:/, "");
    const source = new URL("https://commons.wikimedia.org/w/thumb.php");
    source.searchParams.set("f", filename);
    source.searchParams.set("width", "640");
    page.thumbnail = { source: source.toString() };
    page.pageimage = filename;
    page.imageCreditURL = `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(filename.replaceAll(" ", "_"))}`;
    page.fallbackImageTitle = food.imageTitle;
  }
  return pages;
}

async function loadCommonsImage(query, exactTitle = undefined) {
  const url = new URL("https://commons.wikimedia.org/w/api.php");
  const params = {
    action: "query",
    format: "json",
    formatversion: "2",
    origin: "*",
    prop: "imageinfo",
    iiprop: "url|mime",
    iiurlwidth: "640",
  };
  if (exactTitle) {
    params.titles = exactTitle;
  } else {
    Object.assign(params, {
      generator: "search",
      gsrsearch: query,
      gsrnamespace: "6",
      gsrlimit: "10",
    });
  }
  url.search = new URLSearchParams(params);
  const data = await fetchJSON(url);
  const candidates = (data.query?.pages ?? [])
    .map(page => ({ page, info: page.imageinfo?.[0] }))
    .filter(({ info }) => ["image/jpeg", "image/png", "image/webp"].includes(info?.mime))
    .filter(({ page }) => !/\b(logo|icon|map|diagram|poster|package|packaging)\b/i.test(page.title));
  const selected = candidates[0];
  if (!selected) {
    return undefined;
  }
  return {
    title: selected.page.title,
    filename: selected.page.title.replace(/^File:/, ""),
    source: selected.info.thumburl ?? selected.info.url,
    creditURL: selected.info.descriptionurl,
  };
}

async function invoke(action, params = {}) {
  const response = await fetch(ankiConnectURL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, version: 6, params }),
  });
  if (!response.ok) {
    throw new Error(`AnkiConnect returned HTTP ${response.status} for ${action}`);
  }
  const body = await response.json();
  if (body.error !== null) {
    throw new Error(`AnkiConnect ${action}: ${body.error}`);
  }
  return body.result;
}

function mediaStem(title) {
  const slug = title
    .normalize("NFKD")
    .replaceAll(/[^a-zA-Z0-9]+/g, "_")
    .replaceAll(/^_+|_+$/g, "")
    .toLowerCase()
    .slice(0, 70);
  const suffix = createHash("sha256").update(title).digest("hex").slice(0, 8);
  return `menu_food_${slug}_${suffix}`;
}

function extensionFor(contentType, url) {
  const extensions = new Map([
    ["image/jpeg", "jpg"],
    ["image/png", "png"],
    ["image/gif", "gif"],
    ["image/webp", "webp"],
  ]);
  if (extensions.has(contentType)) {
    return extensions.get(contentType);
  }
  const match = new URL(url).pathname.match(/\.(jpe?g|png|gif|webp)(?:\/|$)/i);
  return match?.[1].toLowerCase().replace("jpeg", "jpg") ?? "jpg";
}

function officialThumbnailURL(page) {
  const host = page.thumbnail.source.includes("/wikipedia/en/") ? "en.wikipedia.org" : "commons.wikimedia.org";
  const url = new URL(`https://${host}/w/thumb.php`);
  url.searchParams.set("f", page.pageimage);
  url.searchParams.set("width", "640");
  return url.toString();
}

function imageSpecForFood(food, pages) {
  if (!food.cardImageTitle) {
    return { key: food.wiki, page: pages.get(food.wiki) };
  }
  const filename = food.cardImageTitle.replace(/^File:/, "");
  const source = new URL("https://commons.wikimedia.org/w/thumb.php");
  source.searchParams.set("f", filename);
  source.searchParams.set("width", "640");
  return {
    key: food.cardImageTitle,
    page: {
      thumbnail: { source: source.toString() },
      pageimage: filename,
      imageCreditURL: `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(filename.replaceAll(" ", "_"))}`,
    },
  };
}

async function runWithConcurrency(values, concurrency, callback) {
  const results = new Array(values.length);
  let nextIndex = 0;

  async function worker() {
    while (nextIndex < values.length) {
      const index = nextIndex++;
      results[index] = await callback(values[index], index);
    }
  }

  await Promise.all(Array.from({ length: concurrency }, worker));
  return results;
}

function reportWikipediaCoverage(pages) {
  const missing = [];
  const withoutExtract = [];
  const withoutImage = [];
  const malformedDetails = [];
  for (const title of new Set(foods.map(({ wiki }) => wiki))) {
    const page = pages.get(title);
    if (!page || page.missing) {
      missing.push(title);
    } else {
      if (!page.extract) {
        withoutExtract.push(title);
      }
      if (!page.thumbnail?.source) {
        withoutImage.push(title);
      }
    }
  }
  for (const food of foods) {
    const details = food.details ?? firstTwoSentences(pages.get(food.wiki)?.extract ?? "");
    if (/\(\s*\)|\(\s*[,;]/.test(details)) {
      malformedDetails.push(food.term);
    }
  }

  console.log(`Cards: ${foods.length}`);
  for (const [category, { label }] of Object.entries(categories)) {
    console.log(`  ${label}: ${foods.filter(food => food.category === category).length}`);
  }
  console.log(`Unique Wikipedia pages: ${new Set(foods.map(({ wiki }) => wiki)).size}`);
  console.log(`Structured recognition entries: ${recognitionByTerm.size}`);
  console.log(`Missing pages: ${missing.length}${missing.length ? ` — ${missing.join(", ")}` : ""}`);
  console.log(`Pages without extracts: ${withoutExtract.length}${withoutExtract.length ? ` — ${withoutExtract.join(", ")}` : ""}`);
  console.log(`Pages without images: ${withoutImage.length}${withoutImage.length ? ` — ${withoutImage.join(", ")}` : ""}`);
  console.log(`Malformed excerpts: ${malformedDetails.length}${malformedDetails.length ? ` — ${malformedDetails.join(", ")}` : ""}`);
  const fallbackImages = [...pages.entries()]
    .filter(([, page]) => page?.fallbackImageTitle)
    .map(([title, page]) => `${title} → ${page.fallbackImageTitle}`);
  if (fallbackImages.length) {
    console.log(`Commons image fallbacks: ${fallbackImages.join("; ")}`);
  }

  return { missing, withoutExtract, withoutImage, malformedDetails };
}

async function ensureModel() {
  const modelNames = await invoke("modelNames");
  if (modelNames.includes(modelName)) {
    return;
  }

  await invoke("createModel", {
    modelName,
    inOrderFields: ["Term", "Headline", "Image", "Details", "Reference", "ImageCredit", "Category"],
    css: styling,
    isCloze: false,
    cardTemplates: [{ Name: "Recognition", Front: frontTemplate, Back: backTemplate }],
  });
}

async function existingNoteKeys() {
  const noteIds = await invoke("findNotes", { query: "tag:menu-food" });
  const keys = new Set();
  for (const noteIdChunk of chunks(noteIds, 100)) {
    const notes = await invoke("notesInfo", { notes: noteIdChunk });
    for (const note of notes) {
      if (note.modelName !== modelName) {
        continue;
      }
      keys.add(`${note.fields.Category.value}\u0000${note.fields.Term.value}`);
    }
  }
  return keys;
}

async function install(pages) {
  await invoke("version");
  await ensureModel();
  for (const { deck } of Object.values(categories)) {
    await invoke("createDeck", { deck });
  }

  const existingMedia = new Set(await invoke("getMediaFilesNames", { pattern: "menu_food_*" }));
  const uniquePages = [...new Map(foods.map(food => {
    const spec = imageSpecForFood(food, pages);
    return [spec.key, spec.page];
  })).entries()];
  const imageFiles = new Map();

  let newMediaCount = 0;
  for (let index = 0; index < uniquePages.length; ++index) {
    const [title, page] = uniquePages[index];
    if (!page?.thumbnail?.source) {
      continue;
    }
    const candidateStem = mediaStem(title);
    const existingFilename = [...existingMedia].find(filename => filename.startsWith(`${candidateStem}.`));
    if (existingFilename) {
      imageFiles.set(title, existingFilename);
      continue;
    }

    const extension = extensionFor("", page.thumbnail.source);
    const filename = `${candidateStem}.${extension}`;
    let storedFilename;
    for (let attempt = 0; attempt < 12; ++attempt) {
      try {
        storedFilename = await invoke("storeMediaFile", { filename, url: officialThumbnailURL(page) });
        break;
      } catch (error) {
        if (attempt === 11) {
          throw error;
        }
        const retrySeconds = error.message.includes("429") ? 30 : Math.min(2 ** attempt, 30);
        console.log(`Media retry ${attempt + 1}/11 for ${title} in ${retrySeconds}s: ${error.message}`);
        await new Promise(resolve => setTimeout(resolve, retrySeconds * 1000));
      }
    }
    imageFiles.set(title, storedFilename);
    existingMedia.add(storedFilename);
    ++newMediaCount;
    await new Promise(resolve => setTimeout(resolve, 1500));
    if ((index + 1) % 10 === 0 || index + 1 === uniquePages.length) {
      console.log(`Media: ${index + 1}/${uniquePages.length} source pages processed.`);
    }
  }

  const existingKeys = await existingNoteKeys();
  const notes = [];
  for (const food of foods) {
    const { deck, label } = categories[food.category];
    const key = `${label}\u0000${food.term}`;
    if (existingKeys.has(key)) {
      continue;
    }

    const page = pages.get(food.wiki);
    const imageSpec = imageSpecForFood(food, pages);
    const filename = imageFiles.get(imageSpec.key);
    const articleURL = food.referenceURL ?? page?.fullurl ?? `https://en.wikipedia.org/wiki/${encodeURIComponent(food.wiki.replaceAll(" ", "_"))}`;
    const commonsURL = imageSpec.page?.imageCreditURL ?? (imageSpec.page?.pageimage
      ? `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(imageSpec.page.pageimage.replaceAll(" ", "_"))}`
      : "");
    notes.push({
      deckName: deck,
      modelName,
      fields: {
        Term: escapeHTML(food.term),
        Headline: recognitionHTML(food),
        Image: filename ? `<img src="${escapeHTML(filename)}">` : "",
        Details: escapeHTML(food.details ?? firstTwoSentences(page?.extract ?? "")),
        Reference: `<a href="${escapeHTML(articleURL)}">${escapeHTML(food.referenceLabel ?? "Wikipedia")}</a>`,
        ImageCredit: commonsURL ? `<a href="${escapeHTML(commonsURL)}">image source</a>` : "",
        Category: label,
      },
      options: { allowDuplicate: false },
      tags: ["menu-food", `menu-food::${food.category}`],
    });
  }

  let addedCount = 0;
  for (const noteChunk of chunks(notes, 80)) {
    const noteIds = await invoke("addNotes", { notes: noteChunk });
    const failures = noteIds
      .map((noteId, index) => ({ noteId, term: noteChunk[index].fields.Term }))
      .filter(({ noteId }) => noteId === null);
    if (failures.length) {
      throw new Error(`Anki rejected ${failures.length} notes: ${failures.map(({ term }) => term).join(", ")}`);
    }
    addedCount += noteIds.length;
  }

  console.log(`Stored ${newMediaCount} new media files.`);
  console.log(`Added ${addedCount} notes; ${foods.length - addedCount} already existed.`);
}

async function verifyInstallation(pages) {
  const errors = [];
  const noteIds = await invoke("findNotes", { query: "tag:menu-food" });
  const notes = [];
  for (const noteIdChunk of chunks(noteIds, 100)) {
    notes.push(...await invoke("notesInfo", { notes: noteIdChunk }));
  }

  if (notes.length !== foods.length) {
    errors.push(`expected ${foods.length} notes, found ${notes.length}`);
  }
  const expectedCounts = Object.fromEntries(Object.keys(categories).map(category => [category, foods.filter(food => food.category === category).length]));
  const actualCounts = Object.fromEntries(Object.keys(categories).map(category => [category, 0]));
  const referencedMedia = new Set();
  const cardIds = [];
  const noteDecks = new Map();

  for (const note of notes) {
    if (note.modelName !== modelName) {
      errors.push(`note ${note.noteId} uses unexpected model ${note.modelName}`);
    }
    for (const fieldName of ["Term", "Headline", "Image", "Details", "Reference", "Category"]) {
      if (!note.fields[fieldName]?.value) {
        errors.push(`note ${note.noteId} has an empty ${fieldName} field`);
      }
    }
    const category = Object.entries(categories).find(([, { label }]) => label === note.fields.Category?.value)?.[0];
    if (!category) {
      errors.push(`note ${note.noteId} has unknown category ${note.fields.Category?.value}`);
    } else {
      ++actualCounts[category];
      noteDecks.set(note.noteId, categories[category].deck);
    }
    const filename = note.fields.Image?.value.match(/<img src="([^"]+)">/)?.[1];
    if (!filename) {
      errors.push(`note ${note.noteId} has an invalid Image field`);
    } else {
      referencedMedia.add(filename);
      const food = foods.find(candidate => escapeHTML(candidate.term) === note.fields.Term.value);
      if (food) {
        const expectedStem = mediaStem(imageSpecForFood(food, new Map()).key);
        if (!filename.startsWith(`${expectedStem}.`)) {
          errors.push(`note ${note.noteId} references ${filename} instead of ${expectedStem}`);
        }
        const page = pages.get(food.wiki);
        const articleURL = food.referenceURL ?? page?.fullurl ?? `https://en.wikipedia.org/wiki/${encodeURIComponent(food.wiki.replaceAll(" ", "_"))}`;
        const expectedFields = {
          Headline: recognitionHTML(food),
          Details: escapeHTML(food.details ?? firstTwoSentences(page?.extract ?? "")),
          Reference: `<a href="${escapeHTML(articleURL)}">${escapeHTML(food.referenceLabel ?? "Wikipedia")}</a>`,
        };
        for (const [fieldName, expectedValue] of Object.entries(expectedFields)) {
          if (note.fields[fieldName].value !== expectedValue) {
            errors.push(`note ${note.noteId} has stale ${fieldName} content`);
          }
        }
      }
    }
    if (note.cards.length !== 1) {
      errors.push(`note ${note.noteId} has ${note.cards.length} cards instead of 1`);
    }
    cardIds.push(...note.cards);
  }

  for (const category of Object.keys(categories)) {
    if (actualCounts[category] !== expectedCounts[category]) {
      errors.push(`${category} has ${actualCounts[category]} notes instead of ${expectedCounts[category]}`);
    }
  }

  const cards = [];
  for (const cardIdChunk of chunks(cardIds, 100)) {
    cards.push(...await invoke("cardsInfo", { cards: cardIdChunk }));
  }
  for (const card of cards) {
    const expectedDeck = noteDecks.get(card.note);
    if (card.deckName !== expectedDeck) {
      errors.push(`card ${card.cardId} is in ${card.deckName} instead of ${expectedDeck}`);
    }
    if (!card.question.includes("class=\"term\"") || !/class="headline">\s*<strong>/u.test(card.answer)) {
      errors.push(`card ${card.cardId} did not render the expected front/back structure`);
    }
  }

  const modelStyling = await invoke("modelStyling", { modelName });
  if (!modelStyling.css.includes(".headline strong") || !modelStyling.css.includes("font-weight: 800")) {
    errors.push("note model styling does not distinguish the bold recognition cue from context");
  }

  const mediaFiles = new Set(await invoke("getMediaFilesNames", { pattern: "menu_food_*" }));
  for (const filename of referencedMedia) {
    if (!mediaFiles.has(filename)) {
      errors.push(`referenced media file ${filename} is missing`);
    }
  }

  console.log(`Verified notes: ${notes.length}`);
  console.log(`Verified cards: ${cards.length}`);
  console.log(`Verified referenced media: ${referencedMedia.size}`);
  console.log(`Category counts: ${Object.entries(actualCounts).map(([category, count]) => `${category}=${count}`).join(", ")}`);
  if (errors.length) {
    throw new Error(`Installation verification failed:\n- ${errors.join("\n- ")}`);
  }
  console.log("Installation verification passed.");
}

async function refreshPresentation(pages) {
  await invoke("updateModelStyling", { model: { name: modelName, css: styling } });
  const existingMedia = new Set(await invoke("getMediaFilesNames", { pattern: "menu_food_*" }));
  const imageFiles = new Map();
  for (const food of foods.filter(({ cardImageTitle }) => cardImageTitle)) {
    const spec = imageSpecForFood(food, pages);
    if (imageFiles.has(spec.key)) {
      continue;
    }
    const stem = mediaStem(spec.key);
    let filename = [...existingMedia].find(candidate => candidate.startsWith(`${stem}.`));
    if (!filename) {
      const extension = extensionFor("", spec.page.thumbnail.source);
      filename = `${stem}.${extension}`;
      filename = await invoke("storeMediaFile", {
        filename,
        url: officialThumbnailURL(spec.page),
      });
      existingMedia.add(filename);
    }
    imageFiles.set(spec.key, filename);
  }

  const noteIds = await invoke("findNotes", { query: "tag:menu-food" });
  const notes = [];
  for (const noteIdChunk of chunks(noteIds, 100)) {
    notes.push(...await invoke("notesInfo", { notes: noteIdChunk }));
  }
  const notesByTerm = new Map(notes.map(note => [note.fields.Term.value, note]));
  let updatedNotes = 0;
  for (const food of foods.filter(({ cardImageTitle }) => cardImageTitle)) {
    const note = notesByTerm.get(escapeHTML(food.term));
    if (!note) {
      throw new Error(`Could not find installed note for ${food.term}`);
    }
    const spec = imageSpecForFood(food, pages);
    const filename = imageFiles.get(spec.key);
    await invoke("updateNoteFields", {
      note: {
        id: note.noteId,
        fields: {
          Image: `<img src="${escapeHTML(filename)}">`,
          ImageCredit: `<a href="${escapeHTML(spec.page.imageCreditURL)}">image source</a>`,
        },
      },
    });
    ++updatedNotes;
  }
  console.log("Updated the note model for readable AnkiMobile night mode.");
  console.log(`Updated ${updatedNotes} prosciutto cards with serving-specific images.`);
}

async function refreshHeadlines() {
  await invoke("updateModelStyling", { model: { name: modelName, css: styling } });
  const noteIds = await invoke("findNotes", { query: "tag:menu-food" });
  const notes = [];
  for (const noteIdChunk of chunks(noteIds, 100)) {
    notes.push(...await invoke("notesInfo", { notes: noteIdChunk }));
  }
  const notesByTerm = new Map(notes.map(note => [note.fields.Term.value, note]));
  let updatedNotes = 0;
  for (const food of foods) {
    const note = notesByTerm.get(escapeHTML(food.term));
    if (!note) {
      throw new Error(`Could not find installed note for ${food.term}`);
    }
    const headline = recognitionHTML(food);
    if (note.fields.Headline.value === headline) {
      continue;
    }
    await invoke("updateNoteFields", {
      note: {
        id: note.noteId,
        fields: { Headline: headline },
      },
    });
    ++updatedNotes;
  }
  console.log(`Updated ${updatedNotes} structured recognition headlines and their styling.`);
}

async function refreshContent(pages) {
  const existingMedia = new Set(await invoke("getMediaFilesNames", { pattern: "menu_food_*" }));
  const imageFiles = new Map();
  for (const food of foods.filter(({ cardImageTitle }) => cardImageTitle)) {
    const spec = imageSpecForFood(food, pages);
    if (imageFiles.has(spec.key)) {
      continue;
    }
    const stem = mediaStem(spec.key);
    let filename = [...existingMedia].find(candidate => candidate.startsWith(`${stem}.`));
    if (!filename) {
      const extension = extensionFor("", spec.page.thumbnail.source);
      filename = `${stem}.${extension}`;
      filename = await invoke("storeMediaFile", {
        filename,
        url: officialThumbnailURL(spec.page),
      });
      existingMedia.add(filename);
    }
    imageFiles.set(spec.key, filename);
  }

  const noteIds = await invoke("findNotes", { query: "tag:menu-food" });
  const notes = [];
  for (const noteIdChunk of chunks(noteIds, 100)) {
    notes.push(...await invoke("notesInfo", { notes: noteIdChunk }));
  }
  const notesByTerm = new Map(notes.map(note => [note.fields.Term.value, note]));
  let updatedNotes = 0;
  for (const food of foods) {
    const note = notesByTerm.get(escapeHTML(food.term));
    if (!note) {
      throw new Error(`Could not find installed note for ${food.term}`);
    }
    const page = pages.get(food.wiki);
    const articleURL = food.referenceURL ?? page?.fullurl ?? `https://en.wikipedia.org/wiki/${encodeURIComponent(food.wiki.replaceAll(" ", "_"))}`;
    const fields = {
      Headline: recognitionHTML(food),
      Details: escapeHTML(food.details ?? firstTwoSentences(page?.extract ?? "")),
      Reference: `<a href="${escapeHTML(articleURL)}">${escapeHTML(food.referenceLabel ?? "Wikipedia")}</a>`,
    };
    if (food.cardImageTitle) {
      const spec = imageSpecForFood(food, pages);
      const filename = imageFiles.get(spec.key);
      fields.Image = `<img src="${escapeHTML(filename)}">`;
      fields.ImageCredit = `<a href="${escapeHTML(spec.page.imageCreditURL)}">image source</a>`;
    }
    if (Object.entries(fields).every(([fieldName, value]) => note.fields[fieldName].value === value)) {
      continue;
    }
    await invoke("updateNoteFields", { note: { id: note.noteId, fields } });
    ++updatedNotes;
  }
  console.log(`Updated content on ${updatedNotes} changed cards.`);
}

async function flattenDeck() {
  const cardIds = await invoke("findCards", { query: "tag:menu-food" });
  const cards = [];
  for (const cardIdChunk of chunks(cardIds, 100)) {
    cards.push(...await invoke("cardsInfo", { cards: cardIdChunk }));
  }
  const allowedDecks = new Set([parentDeck, ...obsoleteSubdecks]);
  const unexpectedCards = cards.filter(card => !allowedDecks.has(card.deckName));
  if (unexpectedCards.length) {
    throw new Error(`Refusing to move cards from unexpected decks: ${[...new Set(unexpectedCards.map(card => card.deckName))].join(", ")}`);
  }
  if (cards.length !== foods.length) {
    throw new Error(`Refusing to flatten: expected ${foods.length} menu-food cards, found ${cards.length}`);
  }

  await invoke("changeDeck", { cards: cardIds, deck: parentDeck });
  const movedCards = [];
  for (const cardIdChunk of chunks(cardIds, 100)) {
    movedCards.push(...await invoke("cardsInfo", { cards: cardIdChunk }));
  }
  const misplacedCards = movedCards.filter(card => card.deckName !== parentDeck);
  if (misplacedCards.length) {
    throw new Error(`${misplacedCards.length} cards did not move to ${parentDeck}`);
  }

  const nonemptySubdecks = [];
  for (const subdeck of obsoleteSubdecks) {
    const subdeckCards = await invoke("findCards", { query: `deck:\"${subdeck}\"` });
    if (subdeckCards.length) {
      nonemptySubdecks.push(`${subdeck} (${subdeckCards.length} cards)`);
    }
  }
  if (nonemptySubdecks.length) {
    throw new Error(`Refusing to delete nonempty subdecks: ${nonemptySubdecks.join(", ")}`);
  }
  await invoke("deleteDecks", { decks: obsoleteSubdecks, cardsToo: true });

  const remainingDecks = await invoke("deckNames");
  const remainingSubdecks = obsoleteSubdecks.filter(deck => remainingDecks.includes(deck));
  if (remainingSubdecks.length) {
    throw new Error(`Empty subdecks remain: ${remainingSubdecks.join(", ")}`);
  }
  console.log(`Moved ${movedCards.length} cards into the single ${parentDeck} deck.`);
  console.log("Deleted the four empty category subdecks; category tags were preserved.");
}

async function ensureMixedDeckOptions() {
  let config = await invoke("getDeckConfig", { deck: parentDeck });
  if (!config) {
    throw new Error(`Could not read options for ${parentDeck}`);
  }
  if (config.name !== "Menu Foods — mixed") {
    const configId = await invoke("cloneDeckConfigId", {
      name: "Menu Foods — mixed",
      cloneFrom: String(config.id),
    });
    if (!configId) {
      throw new Error("Could not create a dedicated Menu Foods options preset");
    }
    const assigned = await invoke("setDeckConfigId", { decks: [parentDeck], configId });
    if (!assigned) {
      throw new Error("Could not assign the dedicated options preset to Menu Foods");
    }
    config = await invoke("getDeckConfig", { deck: parentDeck });
  }

  config.newGatherPriority = 4;
  config.newSortOrder = 4;
  const saved = await invoke("saveDeckConfig", { config });
  if (!saved) {
    throw new Error("Could not save randomized Menu Foods display order");
  }
  const verified = await invoke("getDeckConfig", { deck: parentDeck });
  if (verified.name !== "Menu Foods — mixed" || verified.newGatherPriority !== 4 || verified.newSortOrder !== 4) {
    throw new Error("Menu Foods randomized display order did not verify");
  }
  console.log(`Assigned dedicated options preset ${verified.name} (ID ${verified.id}).`);
  console.log("New-card gather order and sort order are both fully random.");
}

const modeDescriptions = new Map([
  ["--install", "add missing deck notes and media, then verify"],
  ["--verify", "read-only audit of the installed deck"],
  ["--flatten", "move tagged cards into one deck and remove empty legacy subdecks"],
  ["--mix", "assign fully-random new-card gathering and sorting"],
  ["--refresh-presentation", "update card styling and explicitly-selected images"],
  ["--refresh-headlines", "update structured recognition headlines and styling"],
  ["--refresh-content", "update headlines, details, references, and explicitly-selected images"],
]);
const args = process.argv.slice(2);
const unknownArgs = args.filter(arg => arg !== "--help" && !modeDescriptions.has(arg));
if (unknownArgs.length !== 0) {
  throw new Error(`Unknown argument${unknownArgs.length === 1 ? "" : "s"}: ${unknownArgs.join(", ")}`);
}
const requestedModes = args.filter(arg => modeDescriptions.has(arg));
if (requestedModes.length > 1) {
  throw new Error(`Choose only one mode: ${requestedModes.join(", ")}`);
}
if (args.includes("--help")) {
  console.log(`Usage: node build.mjs [mode]

With no mode, validate the source data and cached Wikipedia coverage without
contacting Anki. The available AnkiConnect modes are:

${[...modeDescriptions].map(([flag, description]) => `  ${flag.padEnd(24)} ${description}`).join("\n")}

AnkiConnect defaults to http://127.0.0.1:8765. Override it with
ANKI_CONNECT_URL. This program never invokes Anki sync.`);
  process.exit(0);
}

const mode = requestedModes[0];
const pages = await loadWikipediaPages();
const coverage = reportWikipediaCoverage(pages);
if (mode !== undefined) {
  console.log(`AnkiConnect endpoint: ${ankiConnectURL}`);
}

if (mode === "--install") {
  if (coverage.missing.length || coverage.withoutExtract.length || coverage.withoutImage.length || coverage.malformedDetails.length) {
    throw new Error("Refusing to install until every entry has a Wikipedia extract and image.");
  }
  await install(pages);
  await ensureMixedDeckOptions();
  await verifyInstallation(pages);
} else if (mode === "--verify") {
  await verifyInstallation(pages);
} else if (mode === "--flatten") {
  await flattenDeck();
  await ensureMixedDeckOptions();
  await verifyInstallation(pages);
} else if (mode === "--mix") {
  await ensureMixedDeckOptions();
  await verifyInstallation(pages);
} else if (mode === "--refresh-presentation") {
  await refreshPresentation(pages);
  await verifyInstallation(pages);
} else if (mode === "--refresh-headlines") {
  await refreshHeadlines();
  await verifyInstallation(pages);
} else if (mode === "--refresh-content") {
  await refreshContent(pages);
  await verifyInstallation(pages);
} else {
  console.log("Validation only. Pass --install to write the deck through AnkiConnect.");
}
