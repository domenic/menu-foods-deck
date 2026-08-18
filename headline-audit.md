# Menu Foods headline audit

> Generated design review: this report does not modify an Anki collection, card template, or source food record.

## Rendering proposal

Each card retains structured facts internally but renders one compact sentence-like answer. Bold is a fast visual recognition cue, not a universal grading contract; the learner decides which facts count. The headline has no terminal period, and semicolons are the only separators between the bold cue and normal-weight origin, language, or caveats. Existing long-form details remain below the image and are not included here.

The proposed ordering is shape first for pasta; animal/form/preparation for meat; texture/style/milk for cheese; and plain-English identity/preparation for other menu traps. The draft preserves the semantic content of the current headline except where an audit note explicitly calls out a clarification.

Cards audited: 212. Substantive rendering changes: 149. Capitalization/punctuation only: 63. Density flags: 0. Animal-first meat check: 72/72.

## Recognition collisions

These cards intentionally or potentially share the same bold recognition cue. Language and origin may still distinguish them in the unbolded context; each group should be reviewed before implementation.

- `coppa`, `capocollo`: **Pig; dry-cured neck or shoulder**
- `boudin noir`, `morcilla`: **Usually pig; blood sausage**
- `manzo`, `bœuf`: **Cow; beef**
- `vitello`, `veau`: **Young cow (calf); veal**
- `maiale`, `porc`: **Pig; pork**
- `agnello`, `agneau`: **Young sheep; lamb**
- `anatra`, `canard`: **Duck**
- `coniglio`, `lapin`: **Rabbit**
- `crescenza`, `stracchino`: **Soft, mild, creamy cheese**
- `gorgonzola`, `stilton`: **Blue cheese**
- `beaufort`, `comté`, `gruyère`: **Firm, nutty cheese**
- `brillat-savarin`, `saint-andré`: **Very rich, soft, triple-cream cheese**
- `époisses`, `munster`: **Soft, pungent, washed-rind cheese**

### Exact rendered-answer collisions

These remain identical even after including the unbolded context. Synonym pairs may be acceptable; distinct cheeses need either a better differentiator or an explicit decision that the distinction is outside this deck’s learning goal.

- `coppa`, `capocollo`: **Pig; dry-cured neck or shoulder**
- `crescenza`, `stracchino`: **Soft, mild, creamy cheese**; Italian; cow’s milk
- `brillat-savarin`, `saint-andré`: **Very rich, soft, triple-cream cheese**; French
- `époisses`, `munster`: **Soft, pungent, washed-rind cheese**; French; cow’s milk

## Before/after review

Each category is collapsed by default. Formatting-only cards are counted separately and hidden in a nested list rather than repeated as nearly identical table rows.

<details>
<summary><strong>Pasta</strong>; 7 substantive; 52 formatting-only</summary>

| Term | Current headline | Proposed rendering | Audit note |
| --- | --- | --- | --- |
| busiate | long, tightly twisted Sicilian pasta | **Long, tightly twisted pasta**; Sicilian | Moves regional origin to context; no food facts dropped. |
| fileja | long, narrow Calabrian corkscrews | **Long, narrow corkscrews**; Calabrian | Moves regional origin to context; no food facts dropped. |
| fregola | small toasted Sardinian pasta balls | **Small toasted pasta balls**; Sardinian | Moves regional origin to context; no food facts dropped. |
| malloreddus | small ridged Sardinian pasta shells | **Small ridged pasta shells**; Sardinian | Moves regional origin to context; no food facts dropped. |
| pici | thick, hand-rolled Tuscan spaghetti | **Thick, hand-rolled spaghetti**; Tuscan | Moves regional origin to context; no food facts dropped. |
| scialatielli | short, thick, flat ribbons from Campania | **Short, thick, flat ribbons**; from Campania | Moves regional origin to context; no food facts dropped. |
| trofie | short, thin, hand-twisted Ligurian pasta | **Short, thin, hand-twisted pasta**; Ligurian | Moves regional origin to context; no food facts dropped. |

<details>
<summary>Formatting-only cards (52)</summary>

`acini di pepe`, `agnolotti`, `anelli`, `bigoli`, `bucatini`, `calamarata`, `campanelle`, `cannelloni`, `capellini`, `cappellacci`, `cappelletti`, `casarecce`, `cavatappi`, `cavatelli`, `conchiglie`, `corzetti`, `ditalini`, `farfalle`, `fettuccine`, `fusilli`, `garganelli`, `gemelli`, `gnocchi`, `lasagne`, `linguine`, `lumache`, `mafaldine`, `manicotti`, `mezze maniche`, `orecchiette`, `orzo`, `paccheri`, `pappardelle`, `passatelli`, `pastina`, `penne`, `pizzoccheri`, `radiatori`, `ravioli`, `rigatoni`, `rotelle`, `rotini`, `spaghetti`, `spaghettini`, `strozzapreti`, `tagliatelle`, `tagliolini`, `tonnarelli`, `tortellini`, `tortelloni`, `vermicelli`, `ziti`

</details>

</details>

<details>
<summary><strong>Meat and charcuterie</strong>; 72 substantive; 0 formatting-only</summary>

| Term | Current headline | Proposed rendering | Audit note |
| --- | --- | --- | --- |
| salumi | Italian cured-meat assortment, usually pork (pig) | **Usually pig; cured-meat assortment**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| salame | Italian cured sausage, usually pork (pig) | **Usually pig; cured sausage**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| salsiccia | Italian sausage, usually pork (pig) | **Usually pig; sausage**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| soppressata | coarse Italian dry-cured salami, usually pork (pig) | **Usually pig; coarse, dry-cured salami**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| finocchiona | Tuscan pork (pig) salami flavored with fennel | **Pig; fennel-flavored salami**; Tuscan | Moves contextual facts after semicolons; food facts preserved. |
| mortadella | large, mild cooked pork (pig) sausage | **Pig; large, mild, cooked sausage** | Reorders or clarifies the same food facts. |
| prosciutto | Italian ham (pig), usually thin-sliced and dry-cured | **Pig; dry-cured ham; usually thinly sliced**; Italian; usually means crudo on English menus | Clarifies the English-menu default while preserving the broader Italian meaning in context. |
| prosciutto crudo | uncooked dry-cured Italian ham (pig) | **Pig; uncooked, unsmoked, dry-cured ham**; Italian; usually thinly sliced | Adds “unsmoked” from the existing reference/details so it contrasts explicitly with speck. |
| prosciutto cotto | cooked Italian ham (pig) | **Pig; cooked ham**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| speck | smoked, dry-cured ham (pig) | **Pig; smoked, dry-cured ham**; South Tyrolean | Makes the smoke contrast with prosciutto crudo visually immediate and adds its South Tyrolean context from the existing reference. |
| coppa | dry-cured whole-muscle pork (pig) neck or shoulder | **Pig; dry-cured neck or shoulder** | Drops “whole-muscle” from the recognition cue; that anatomical detail remains in the existing extra context. |
| capocollo | dry-cured whole-muscle pork (pig) neck or shoulder | **Pig; dry-cured neck or shoulder** | Drops “whole-muscle” from the recognition cue; that anatomical detail remains in the existing extra context. |
| capicola | Italian-American name for cured pork (pig) neck or shoulder | **Pig; cured neck or shoulder**; Italian-American name | Moves contextual facts after semicolons; food facts preserved. |
| pancetta | salt-cured pork (pig) belly; Italian bacon (pig) | **Pig; salt-cured belly; Italian bacon** | Reorders or clarifies the same food facts. |
| guanciale | salt-cured pork (pig) cheek or jowl | **Pig; salt-cured cheek or jowl** | Reorders or clarifies the same food facts. |
| lardo | seasoned, cured pork (pig) back fat | **Pig; seasoned, cured back fat** | Reorders or clarifies the same food facts. |
| bresaola | thin-sliced air-dried salted beef (cow) | **Cow; air-dried, salted beef; thinly sliced** | Reorders or clarifies the same food facts. |
| culatello | dry-cured boneless ham (pig) | **Pig; dry-cured, boneless ham** | Reorders or clarifies the same food facts. |
| ’nduja | soft, spicy, spreadable Calabrian pork (pig) sausage | **Pig; soft, spicy, spreadable sausage**; Calabrian | Moves contextual facts after semicolons; food facts preserved. |
| cotechino | rich cooked pork (pig) sausage | **Pig; rich, cooked sausage** | Reorders or clarifies the same food facts. |
| zampone | stuffed pig’s trotter filled with pork (pig) sausage | **Pig; trotter stuffed with pork sausage** | Reorders or clarifies the same food facts. |
| porchetta | herb-seasoned Italian roast pork (pig) | **Pig; herb-seasoned roast pork**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| lonza | cured or roasted pork (pig) loin | **Pig; cured or roasted loin** | Reorders or clarifies the same food facts. |
| jambon | French: ham (pig) | **Pig; ham**; French | Moves contextual facts after semicolons; food facts preserved. |
| saucisson | thick French dry-cured sausage, usually pork (pig) | **Usually pig; thick, dry-cured sausage**; French | Moves contextual facts after semicolons; food facts preserved. |
| andouille | smoked pork (pig) sausage; style varies by country | **Pig; smoked sausage**; style varies by country | Moves contextual facts after semicolons; food facts preserved. |
| andouillette | coarse French sausage made from pork (pig) intestine | **Pig; coarse intestine sausage**; French | Moves contextual facts after semicolons; food facts preserved. |
| boudin noir | French blood sausage, usually pork (pig) | **Usually pig; blood sausage**; French | Moves contextual facts after semicolons; food facts preserved. |
| boudin blanc | French white sausage without blood; often pork (pig), veal (young cow), or poultry | **Animal varies; white sausage without blood**; French; often pig, young cow, or poultry | Leads with “Animal varies” and preserves the common pig, young-cow, and poultry possibilities in context. |
| rillettes | shredded meat spread; often pork (pig), but animal varies | **Animal varies; shredded meat spread**; often pig | Leads with “Animal varies” while preserving pig as the common case in context. |
| pâté | seasoned meat paste, often made with liver | **Animal varies; seasoned meat paste; often liver** | Reorders or clarifies the same food facts. |
| terrine | coarse pâté or layered meat loaf served cold | **Animal varies; coarse pâté or layered meat loaf; served cold** | Reorders or clarifies the same food facts. |
| lardons | small strips or cubes of fatty bacon (pig) | **Pig; small strips or cubes of fatty bacon** | Reorders or clarifies the same food facts. |
| confit | meat slowly cooked and preserved in fat, often duck | **Often duck; slowly cooked and preserved in fat** | Reorders or clarifies the same food facts. |
| jamón serrano | Spanish dry-cured ham (pig) | **Pig; dry-cured ham**; Spanish | Moves contextual facts after semicolons; food facts preserved. |
| jamón ibérico | premium Spanish dry-cured ham (Iberian pig) | **Iberian pig; premium dry-cured ham**; Spanish | Moves contextual facts after semicolons; food facts preserved. |
| chorizo | highly seasoned pork (pig) sausage; often paprika-red | **Pig; highly seasoned sausage; often paprika-red**; Spanish | Moves contextual facts after semicolons; food facts preserved. |
| morcilla | Spanish blood sausage, usually pork (pig) | **Usually pig; blood sausage**; Spanish | Moves contextual facts after semicolons; food facts preserved. |
| sobrasada | soft, spreadable paprika-seasoned pork (pig) sausage | **Pig; soft, spreadable, paprika-seasoned sausage**; Spanish | Moves contextual facts after semicolons; food facts preserved. |
| lomo | Spanish cured pork (pig) tenderloin | **Pig; cured tenderloin**; Spanish | Moves contextual facts after semicolons; food facts preserved. |
| manzo | Italian: beef (cow) | **Cow; beef**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| vitello | Italian: veal (young cow) | **Young cow (calf); veal**; Italian | Leads with the animal and expands “young cow” to “young cow (calf)”. |
| maiale | Italian: pork (pig) | **Pig; pork**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| cinghiale | Italian: wild boar | **Wild boar**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| agnello | Italian: lamb (young sheep) | **Young sheep; lamb**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| capretto | Italian: kid (young goat) | **Young goat; kid**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| anatra | Italian: duck | **Duck**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| coniglio | Italian: rabbit | **Rabbit**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| cervo | Italian: venison (deer) | **Deer; venison**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| faraona | Italian: guinea fowl | **Guinea fowl**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| bœuf | French: beef (cow) | **Cow; beef**; French | Moves contextual facts after semicolons; food facts preserved. |
| veau | French: veal (young cow) | **Young cow (calf); veal**; French | Leads with the animal and expands “young cow” to “young cow (calf)”. |
| porc | French: pork (pig) | **Pig; pork**; French | Moves contextual facts after semicolons; food facts preserved. |
| agneau | French: lamb (young sheep) | **Young sheep; lamb**; French | Moves contextual facts after semicolons; food facts preserved. |
| canard | French: duck | **Duck**; French | Moves contextual facts after semicolons; food facts preserved. |
| lapin | French: rabbit | **Rabbit**; French | Moves contextual facts after semicolons; food facts preserved. |
| chevreuil | French: venison (roe deer) | **Roe deer; venison**; French | Moves contextual facts after semicolons; food facts preserved. |
| filet mignon | small, very tender beef (cow) tenderloin steak | **Cow; tenderloin steak; small and very tender** | Reorders or clarifies the same food facts. |
| entrecôte | French rib steak, broadly similar to ribeye | **Cow; rib steak; similar to ribeye**; French | Makes the implied beef (cow) source explicit. |
| onglet | French: beef (cow) hanger steak | **Cow; hanger steak**; French | Moves contextual facts after semicolons; food facts preserved. |
| bavette | French: flank-style beef (cow) steak | **Cow; flank-style steak**; French | Moves contextual facts after semicolons; food facts preserved. |
| côte de bœuf | thick bone-in beef (cow) rib steak | **Cow; thick, bone-in rib steak**; French | Moves contextual facts after semicolons; food facts preserved. |
| bistecca | Italian: steak, usually beef (cow) | **Usually cow; steak**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| tagliata | sliced grilled steak, usually beef (cow) | **Usually cow; sliced, grilled steak**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| carpaccio | paper-thin raw meat or fish | **Meat or fish; paper-thin; raw** | Reorders or clarifies the same food facts. |
| osso buco | cross-cut veal (young cow) shank braised with its marrow bone | **Young cow; cross-cut shank; braised with its marrow bone** | Reorders or clarifies the same food facts. |
| braciola | Italian rolled or grilled slice of meat; regional meanings vary | **Animal varies; rolled or grilled meat slice**; Italian; meaning varies by region | Moves contextual facts after semicolons; food facts preserved. |
| animelle | Italian: sweetbreads, usually calf (young cow) or lamb (young sheep) glands | **Usually young cow or young sheep; sweetbreads (glands)**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| trippa | Italian: tripe; edible stomach lining | **Animal varies; tripe; edible stomach lining**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| midollo | Italian: bone marrow | **Animal varies; bone marrow**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| ris de veau | French: veal (young cow) sweetbreads, not rice | **Young cow; sweetbreads**; French; despite the name, not rice | Moves the “not rice” mnemonic to context; the food identity remains prominent. |
| foie gras | fatty duck or goose liver | **Duck or goose; fatty liver** | Reorders or clarifies the same food facts. |

</details>

<details>
<summary><strong>Cheese</strong>; 51 substantive; 7 formatting-only</summary>

| Term | Current headline | Proposed rendering | Audit note |
| --- | --- | --- | --- |
| asiago | Italian cow’s-milk cheese; mild when young, firm when aged | **Mild when young; firm when aged**; Italian; cow’s milk | Leads with its age-dependent texture instead of origin or milk. |
| bel paese | mild, semi-soft Italian cow’s-milk cheese | **Mild, semi-soft cheese**; Italian; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| caciocavallo | firm, stretched-curd southern Italian cheese | **Firm, stretched-curd cheese**; Southern Italian | Moves contextual facts after semicolons; food facts preserved. |
| caciotta | mild, semi-soft Italian farmhouse cheese | **Mild, semi-soft farmhouse cheese**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| crescenza | soft, mild, creamy Italian cow’s-milk cheese | **Soft, mild, creamy cheese**; Italian; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| fontina | nutty, semi-soft Alpine cow’s-milk cheese | **Nutty, semi-soft cheese**; From the Alps; cow’s milk | Moves “Alpine” to context because it describes geography/style, not a dependable texture. |
| gorgonzola | Italian blue cow’s-milk cheese | **Blue cheese**; Italian; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| grana padano | hard, granular Italian cow’s-milk cheese | **Hard, granular cheese**; Italian; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| mascarpone | very rich, mild Italian cream cheese | **Very rich, mild cream cheese**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| montasio | firm Alpine Italian cow’s-milk cheese | **Firm cheese**; Italian; from the Alps; cow’s milk | Moves “Alpine” to context because it describes geography/style, not a dependable texture. |
| parmigiano reggiano | hard, granular aged Italian cow’s-milk cheese | **Hard, granular, aged cheese**; Italian; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| pecorino | Italian sheep’s-milk cheese; a broad family | **Sheep’s-milk cheese; a broad family**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| pecorino romano | hard, salty Italian sheep’s-milk cheese | **Hard, salty sheep’s-milk cheese**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| provolone | semi-hard Italian stretched-curd cow’s-milk cheese | **Semi-hard, stretched-curd cheese**; Italian; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| robiola | soft, creamy northern Italian cheese | **Soft, creamy cheese**; Northern Italian | Moves contextual facts after semicolons; food facts preserved. |
| stracchino | soft, mild, creamy Italian cow’s-milk cheese | **Soft, mild, creamy cheese**; Italian; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| taleggio | soft, washed-rind Italian cow’s-milk cheese | **Soft, washed-rind cheese**; Italian; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| toma | semi-soft Alpine cheese; milk and style vary | **Semi-soft cheese; milk and style vary**; Alpine-style family | Moves “Alpine” to context because it describes geography/style, not a dependable texture. |
| sottocenere | semi-soft Italian cow’s-milk cheese aged under ash | **Semi-soft cheese aged under ash**; Italian; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| beaufort | firm, nutty French Alpine cow’s-milk cheese | **Firm, nutty cheese**; French; from the Alps; cow’s milk | Moves “Alpine” to context because it describes geography/style, not a dependable texture. |
| brie | soft, creamy French bloomy-rind cow’s-milk cheese | **Soft, creamy, bloomy-rind cheese**; French; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| brillat-savarin | very rich, soft French triple-cream cheese | **Very rich, soft, triple-cream cheese**; French | Moves contextual facts after semicolons; food facts preserved. |
| camembert | soft, earthy French bloomy-rind cow’s-milk cheese | **Soft, earthy, bloomy-rind cheese**; French; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| cantal | firm, earthy French cow’s-milk cheese | **Firm, earthy cheese**; French; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| chèvre | French: goat cheese; not one specific style | **Goat cheese; not one specific style**; French term | Moves contextual facts after semicolons; food facts preserved. |
| comté | firm, nutty French Alpine cow’s-milk cheese | **Firm, nutty cheese**; French; Alpine-style; cow’s milk | Moves the broad “Alpine-style” classification to context; Comté is geographically from the Jura. |
| époisses | soft, pungent French washed-rind cow’s-milk cheese | **Soft, pungent, washed-rind cheese**; French; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| gruyère | firm, nutty Swiss Alpine cow’s-milk cheese | **Firm, nutty cheese**; Swiss; Alpine-style; cow’s milk | Moves the broad “Alpine-style” classification to context rather than presenting it as texture. |
| mimolette | firm orange French cow’s-milk cheese | **Firm, orange cheese**; French; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| morbier | semi-soft French cheese marked by a dark ash line | **Semi-soft cheese marked by a dark ash line**; French | Moves contextual facts after semicolons; food facts preserved. |
| munster | soft, pungent French washed-rind cow’s-milk cheese | **Soft, pungent, washed-rind cheese**; French; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| neufchâtel | soft, bloomy-rind French cow’s-milk cheese | **Soft, bloomy-rind cheese**; French; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| ossau-iraty | firm, nutty French Basque sheep’s-milk cheese | **Firm, nutty sheep’s-milk cheese**; French Basque | Moves contextual facts after semicolons; food facts preserved. |
| pont-l’évêque | soft, aromatic French washed-rind cow’s-milk cheese | **Soft, aromatic, washed-rind cheese**; French; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| raclette | melting Alpine cow’s-milk cheese; also the melted-cheese dish | **Melting cheese; also the melted-cheese dish**; Alpine-style; cow’s milk | Moves “Alpine” to context because meltability is the more useful menu characteristic. |
| reblochon | soft, nutty French Alpine cow’s-milk cheese | **Soft, nutty cheese**; French; from the Alps; cow’s milk | Moves “Alpine” to context because it describes geography/style, not a dependable texture. |
| roquefort | tangy French blue sheep’s-milk cheese | **Tangy blue sheep’s-milk cheese**; French | Moves contextual facts after semicolons; food facts preserved. |
| saint-andré | very rich, soft French triple-cream cheese | **Very rich, soft, triple-cream cheese**; French | Moves contextual facts after semicolons; food facts preserved. |
| saint-nectaire | semi-soft, earthy French cow’s-milk cheese | **Semi-soft, earthy cheese**; French; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| tomme | French/Swiss term for a rustic round cheese | **Rustic round cheese; not one specific style**; French/Swiss term | Makes explicit that this is a family/term rather than one uniform cheese. |
| valençay | soft, ash-coated pyramid-shaped French goat cheese | **Soft, ash-coated, pyramid-shaped goat cheese**; French | Moves contextual facts after semicolons; food facts preserved. |
| feta | salty, crumbly Greek brined cheese, usually sheep’s milk | **Salty, crumbly, brined cheese, usually sheep’s milk**; Greek | Moves contextual facts after semicolons; food facts preserved. |
| halloumi | firm Cypriot brined cheese that holds its shape when grilled | **Firm, brined cheese that holds its shape when grilled**; Cypriot | Moves contextual facts after semicolons; food facts preserved. |
| manchego | firm Spanish sheep’s-milk cheese | **Firm sheep’s-milk cheese**; Spanish | Moves contextual facts after semicolons; food facts preserved. |
| cotija | salty, crumbly Mexican cow’s-milk cheese | **Salty, crumbly cheese**; Mexican; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| queso fresco | mild, fresh, crumbly Latin American cheese | **Mild, fresh, crumbly cheese**; Latin American | Moves contextual facts after semicolons; food facts preserved. |
| quesillo | stringy Mexican stretched-curd cheese; Oaxaca cheese | **Stringy, stretched-curd cheese; Oaxaca cheese**; Mexican | Moves contextual facts after semicolons; food facts preserved. |
| labneh | thick, tangy strained yogurt often served like soft cheese | **Thick, tangy strained yogurt served like a soft cheese** | Reorders or clarifies the same food facts. |
| gouda | Dutch cow’s-milk cheese; mild young or caramel-like when aged | **Mild when young; caramel-like when aged**; Dutch; cow’s milk | Leads with its age-dependent character instead of origin or milk. |
| havarti | mild, buttery Danish semi-soft cow’s-milk cheese | **Mild, buttery, semi-soft cheese**; Danish; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |
| stilton | English blue cow’s-milk cheese | **Blue cheese**; English; cow’s milk | Moves contextual facts after semicolons; food facts preserved. |

<details>
<summary>Formatting-only cards (7)</summary>

`burrata`, `mozzarella`, `mozzarella di bufala`, `ricotta`, `ricotta salata`, `scamorza`, `triple crème`

</details>

</details>

<details>
<summary><strong>Other menu traps</strong>; 19 substantive; 4 formatting-only</summary>

| Term | Current headline | Proposed rendering | Audit note |
| --- | --- | --- | --- |
| pepperoncini | mild, tangy pickled chili peppers—not meat | **Mild, tangy pickled chili peppers**; not meat | Moves contextual facts after semicolons; food facts preserved. |
| peperoncino | Italian: chili pepper, usually a hot one | **Chili pepper, usually hot**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| peperoni | Italian plural for bell peppers—not pepperoni sausage | **Bell peppers**; Italian plural; not pepperoni sausage | Moves contextual facts after semicolons; food facts preserved. |
| giardiniera | Italian-style pickled mixed vegetables | **Pickled mixed vegetables**; Italian style | Moves contextual facts after semicolons; food facts preserved. |
| mostarda | northern Italian candied fruit in mustard-flavored syrup | **Candied fruit in mustard-flavored syrup**; Northern Italian | Moves contextual facts after semicolons; food facts preserved. |
| bottarga | salt-cured fish roe, usually grated or thin-sliced | **Salt-cured fish roe**; usually grated or thinly sliced | Moves contextual facts after semicolons; food facts preserved. |
| acciughe | Italian: anchovies | **Anchovies**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| baccalà | Italian: salt-cured cod | **Salt-cured cod**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| polpo | Italian: octopus | **Octopus**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| seppia | Italian: cuttlefish | **Cuttlefish**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| cozze | Italian: mussels | **Mussels**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| vongole | Italian: clams | **Clams**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| scampi | small lobster-like crustaceans; usage varies by country | **Small, lobster-like crustaceans**; usage varies by country | Moves contextual facts after semicolons; food facts preserved. |
| carciofi | Italian: artichokes | **Artichokes**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| cavolo nero | Italian kale; dark leafy Tuscan cabbage | **Dark leafy Tuscan cabbage; Italian kale** | Reorders or clarifies the same food facts. |
| cipollini | small, flat, mildly sweet Italian onions | **Small, flat, mildly sweet onions**; Italian | Moves contextual facts after semicolons; food facts preserved. |
| cornichons | tiny tart French pickled cucumbers | **Tiny, tart pickled cucumbers**; French | Moves contextual facts after semicolons; food facts preserved. |
| tapenade | savory Provençal olive spread | **Savory olive spread**; Provençal | Moves contextual facts after semicolons; food facts preserved. |
| caponata | Sicilian sweet-and-sour eggplant relish | **Sweet-and-sour eggplant relish**; Sicilian | Moves contextual facts after semicolons; food facts preserved. |

<details>
<summary>Formatting-only cards (4)</summary>

`radicchio`, `rapini`, `puntarelle`, `gremolata`

</details>

</details>
