const { categories, cards } = await (await fetch("cards.json")).json();
const cardsByKey = new Map(cards.map((card) => [card.key, card]));

const studyCard = document.querySelector("#study-card");
const viewer = document.querySelector("#viewer");
const viewerCard = viewer.querySelector(".card");

// The card styles have a night mode, which Anki turns on with a class.
const dark = matchMedia("(prefers-color-scheme: dark)");
function applyNightMode() {
  for (const card of document.querySelectorAll(".card")) {
    card.classList.toggle("nightMode", dark.matches);
  }
}
dark.addEventListener("change", applyNightMode);
applyNightMode();

// Switching between the album and the flashcards.
const modeButtons = document.querySelectorAll("[data-mode]");
for (const button of modeButtons) {
  button.addEventListener("click", () => {
    for (const other of modeButtons) {
      const selected = other === button;
      other.setAttribute("aria-pressed", selected);
      document.getElementById(other.dataset.mode).hidden = !selected;
    }
    // Let the keyboard shortcuts work straight away.
    if (button.dataset.mode === "study") {
      studyCard.focus();
    }
  });
}

// Flashcards.
const order = document.querySelector("#order");
const studyCategory = document.querySelector("#study-category");
const progress = document.querySelector("#progress");
const previousButton = document.querySelector("#previous");
const revealButton = document.querySelector("#reveal");
const nextButton = document.querySelector("#next");
let studyCards = cards;
let position = 0;
let revealed = false;

for (const [key, label] of Object.entries(categories)) {
  studyCategory.append(new Option(label, key));
}

function shuffled(items) {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

function resetStudy() {
  const category = studyCategory.value;
  studyCards = cards.filter((card) => !category || card.category === category);
  if (order.value === "shuffled") {
    studyCards = shuffled(studyCards);
  }
  position = 0;
  showStudyCard(false);
}

// Fetching the answer's photos while the question shows keeps the card from
// shifting when it flips.
function preload(card) {
  for (const source of card?.images ?? []) {
    new Image().src = source;
  }
}

function showStudyCard(reveal) {
  const card = studyCards[position];
  if (!reveal) {
    preload(card);
    preload(studyCards[position + 1]);
  }
  revealed = reveal;
  studyCard.innerHTML = reveal ? card.back : card.front;
  studyCard.classList.toggle("revealed", reveal);
  studyCard.scrollTop = 0;
  revealButton.hidden = reveal;
  nextButton.hidden = !reveal;
  nextButton.disabled = position === studyCards.length - 1;
  previousButton.disabled = position === 0;
  progress.textContent = `${position + 1} of ${studyCards.length}`;
}

function move(offset) {
  const target = position + offset;
  if (target >= 0 && target < studyCards.length) {
    position = target;
    showStudyCard(false);
  }
}

order.addEventListener("change", resetStudy);
studyCategory.addEventListener("change", resetStudy);
revealButton.addEventListener("click", () => showStudyCard(true));
nextButton.addEventListener("click", () => move(1));
previousButton.addEventListener("click", () => move(-1));
// Flipping the card is natural on a touch screen.
studyCard.addEventListener("click", (event) => {
  if (!revealed && !event.target.closest("a")) {
    showStudyCard(true);
  }
});

document.addEventListener("keydown", (event) => {
  const flip = event.key === " " || event.key === "Enter";
  if (
    document.querySelector("#study").hidden ||
    viewer.open ||
    event.target.closest("input, select, textarea") ||
    (flip && event.target.closest("button, a")) ||
    event.altKey ||
    event.ctrlKey ||
    event.metaKey
  ) {
    return;
  }
  if (flip) {
    if (revealed) {
      move(1);
    } else {
      showStudyCard(true);
    }
  } else if (event.key === "ArrowRight") {
    move(1);
  } else if (event.key === "ArrowLeft") {
    move(-1);
  } else {
    return;
  }
  event.preventDefault();
});

resetStudy();

// The album of every card.
const search = document.querySelector("#search");
const browseCategory = document.querySelector("#browse-category");
const grid = document.querySelector("#grid");
const empty = document.querySelector("#empty");
let selectedCategory = "";

for (const [key, label] of Object.entries(categories)) {
  const button = document.createElement("button");
  button.type = "button";
  button.dataset.category = key;
  button.setAttribute("aria-pressed", "false");
  button.textContent = label;
  browseCategory.append(button);
}

function searchable(text) {
  return text
    .normalize("NFKD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();
}

const tiles = cards.map((card) => {
  const item = document.createElement("li");
  const link = document.createElement("a");
  link.href = `#${encodeURIComponent(card.key)}`;
  if (card.image) {
    const image = document.createElement("img");
    image.src = card.image;
    image.alt = "";
    image.loading = "lazy";
    image.decoding = "async";
    image.classList.toggle("mirrored", card.mirror);
    link.append(image);
  } else {
    const placeholder = document.createElement("span");
    placeholder.className = "no-image";
    placeholder.textContent = card.label;
    link.append(placeholder);
  }
  const term = document.createElement("span");
  term.className = "tile-term";
  term.textContent = card.term;
  const gloss = document.createElement("span");
  gloss.className = "tile-gloss";
  gloss.textContent = card.gloss;
  link.append(term, gloss);
  item.append(link);
  grid.append(item);
  return { item, card, text: searchable(`${card.term} ${card.gloss}`) };
});

function filterTiles() {
  const words = searchable(search.value).split(/\s+/).filter(Boolean);
  let shown = 0;
  for (const { item, card, text } of tiles) {
    const matches =
      (!selectedCategory || card.category === selectedCategory) &&
      words.every((word) => text.includes(word));
    item.hidden = !matches;
    shown += matches;
  }
  empty.hidden = shown > 0;
}

search.addEventListener("input", filterTiles);
browseCategory.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) {
    return;
  }
  selectedCategory = button.dataset.category;
  for (const other of browseCategory.querySelectorAll("button")) {
    other.setAttribute("aria-pressed", other === button);
  }
  filterTiles();
});

// The card viewer, which shows the card that the URL names, like `#guanciale`.
// Links between cards add history entries, so Back steps through the cards
// visited, and closing the viewer returns to the page entry before them.
function cardAt(url) {
  return cardsByKey.get(decodeURIComponent(new URL(url).hash.slice(1)));
}

function show(card) {
  if (!card) {
    if (viewer.open) {
      viewer.close();
    }
    return;
  }
  viewerCard.innerHTML = card.back;
  viewer.scrollTop = 0;
  if (!viewer.open) {
    viewer.showModal();
  }
}

// Navigations within the page, even to its URL without a card, stay in the
// page, without scrolling.
navigation.addEventListener("navigate", (event) => {
  const destination = new URL(event.destination.url);
  if (
    event.canIntercept &&
    event.navigationType !== "reload" &&
    destination.pathname === location.pathname
  ) {
    event.intercept({
      scroll: "manual",
      handler: () => show(cardAt(destination)),
    });
  }
});

viewer.addEventListener("close", () => {
  if (!cardAt(location.href)) {
    // The viewer closed because of a navigation to the page.
    return;
  }
  const page = navigation
    .entries()
    .slice(0, navigation.currentEntry.index)
    .findLast((entry) => !cardAt(entry.url));
  if (page) {
    navigation.traverseTo(page.key);
  } else {
    // The page was opened at a card's URL, so there's no entry to return to.
    navigation.navigate(location.pathname, { history: "replace" });
  }
});

show(cardAt(location.href));
