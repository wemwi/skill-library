# selectedleafs POS-Restock — Übergabeprotokoll auswerten & ablegen

Operative Anleitung **an dich, den Agenten `pos-restock`**, für den Kern deiner Kette: das Protokoll-PDF in die Sandbox holen (Schritt 1), ein Übergabeprotokoll auswerten (Schritt 2), das PDF komprimieren/umbenennen (Schritt 4) und in Google Drive ablegen (Schritt 5). Du verarbeitest **genau ein Protokoll pro Lauf**.

**Scope:** Schritt 1, 2, 4, 5 deiner Kette. Schritt 3 (Posten) und 6 (Status) führst du laut System-Prompt aus. Auch für Schritt 1 gilt das Muster von §5/§6: der **System-Prompt triggert** (es liegt ein PDF im Topic „Protokoll-Eingang" bereit), dieser Skill liefert nur die **Tiefe des Tool-Calls** (§1.1) — er dupliziert den System-Prompt nicht und entscheidet nicht über den Auslöser.

**Abgrenzung — was NICHT hier steht:**
- **Restock-Nachrichtenformat** → Sektion „Restock-Post-Templates" am Ende dieser reference (📦/🌿 + kanonischer Index). **City→Channel-Ableitung** → `telegram.md` §2.1. Du lieferst nur Stadt + Sorten-Buckets; das Rendern (lokal) und die Channel-Auflösung laufen dort.
- **Managed-Agents-/Console-Mechanik** (Config, Tools, Deploy) → `global-agent-framework` (build-time).
- **Store-Daten** → Shopify MCP (`graphql_query`), zweistufig & feldselektiv (§2.5) — nie ein Voll-Dump aller Store-Felder.

**Vollautomatik (kein Review-Schritt):** **Du läufst vollautomatisch** und postest ohne Vorab-Bestätigung — der Mensch-im-Loop ist hier durch den harten Abbruch bei Unklarheit (§3) ersetzt. Bei Mehrdeutigkeit postest du nie öffentlich, sondern stellst eine Rückfrage im Topic „Protokoll-Eingang" und brichst ab.

---

## 1. Eingang & Reihenfolge

Du bekommst ein PDF aus dem Topic „Protokoll-Eingang" in die Sandbox (Schritt 1). Dann **in dieser Reihenfolge**:

1. **Parsen (§2)** — Store, Stadt, Sorten, neu vs. aufgefüllt; dabei `protokoll_nr` (§2.2) und Store-Metaobjekt (§2.5) auflösen.
2. **Mehrdeutig? (§3)** → Rückfrage im Topic, abbrechen. Sonst weiter.
3. **Idempotenz-Check (§4)** — Zielordner via `ensure_folder_path` (§6) + `list_files` auf `_<protokoll_nr>.pdf`; existiert sie → abbrechen. **Dieser Check läuft zwingend VOR jedem Post/Ablegen.** Er steht hier (nicht ganz oben), weil er `protokoll_nr` + Store-Match aus Schritt 1 braucht — vorher ist der Zielordner nicht bestimmbar.
4. **Posten** — Stadt + Sorten-Buckets rendern (Templates → Sektion „Restock-Post-Templates" am Ende; Channel → `telegram.md` §2.1).
5. **Write-back (§8)** — gepostete **neue Sorten (🌿)** nach erfolgreichem Post an die `product_list` des Stores anhängen.
6. **Komprimieren + umbenennen (§5)**, dann **in Drive ablegen (§6)**.
7. **Status** ins Topic (§7).

### 1.1 PDF in die Sandbox holen (Schritt 1, Referenz-Pfad)

Das Protokoll kommt als Telegram-Dokument im Topic „Protokoll-Eingang" an. Protokolle sind Scans (~0,5–1 MB) — das **Inline-base64-Budget** des Agenten reicht dafür nicht, `download_file` (gibt die Bytes als base64 durch den Kontext zurück) ist daher **nicht** der Weg. Stattdessen der Referenz-Pfad, spiegelbildlich zur Upload-Seite (§6):

1. **Referenz holen** — `create_download_url` mit der `file_id` des PDF-Anhangs (aus dem eingehenden Update, `document.file_id` — **nicht** die `message_id`). Der Bot-Token bleibt serverseitig; das Tool lädt die Datei serverseitig von Telegram, legt die Bytes in R2 ab und gibt JSON zurück: `{ url, key, file_name, mime_type, size, expires_in }`. `url` ist eine **token-freie, kurzlebige** presigned GET-URL.
2. **Bytes direkt ziehen** — die `url` per `curl -o` in die Sandbox holen; die Bytes laufen **nicht** durch den Agenten-Kontext. Zügig nach dem Call ausführen — die URL läuft nach `expires_in` Sekunden ab.

```bash
# Agent-Sandbox (Code-Execution)
curl -s -o "<eingangs-pdf>" "<url>"
# Danach prüfen: Datei > 0 Byte und valides PDF, bevor du weitermachst (§2).
```

**Voraussetzung (Egress):** Der Presign-Host des R2-Buckets — `<account-id>.r2.cloudflarestorage.com` — muss in den **Allowed-Hosts** des Environments stehen, sonst schlägt `curl` mit Netzwerkfehler fehl. Den Host build-time eintragen (Agent-Config, `global-agent-framework`), **nicht** hier hardcoden; er steckt im `url`-Feld der Tool-Antwort.

**Fail-closed:** Gibt `create_download_url` keine `url` zurück (Fehler/Netzwerkproblem) oder liefert `curl` einen Non-2xx-Status bzw. eine 0-Byte-Datei → Abbruch, Fehler-Status ins Topic (§7), **kein** Retry und **kein** base64-Fallback über `download_file` (würde den Kontext sprengen — genau die Ursache, die der Referenz-Pfad behebt).

Protokolle sind **immer unterschriebene Scans** (Foto/Schräglage, Knickkanten, kein Text-Layer). Darum ist **OCR der Pflichtpfad, kein Fallback** — kein vorheriger Textextraktions-Versuch: leichte Vorverarbeitung (Graustufen, bei Bedarf Deskew/Kontrast), dann `tesseract` mit `lang="deu"`. Die **tesseract-Engine** ist im Base-Image der Env vorhanden; das **deutsche Sprachpaket** kommt deklarativ als pip-Paket `tessdata.fast-deu` (kein apt, kein File-Mount — in der Managed-Agents-Beta wird die apt-Paketzeile nicht provisioniert, deshalb nicht über apt installieren). Den tessdata-Ordner **nicht** blind aus `tessdata.data_path()` nehmen — das liefert `sys.prefix/share/tessdata` und liegt im Container ggf. neben dem echten Ort (`/usr/local/share/tessdata`); stattdessen den Kandidaten finden, der `deu.traineddata` enthält, und ihn via `--tessdata-dir` übergeben:

```python
# Agent-Sandbox: 1) tessdata-Ordner robust bestimmen
import tessdata, os, sys
def tessdata_dir():
    for c in (tessdata.data_path(), os.path.join(sys.prefix, "share", "tessdata"),
              "/usr/local/share/tessdata", "/usr/share/tessdata"):
        if os.path.exists(os.path.join(c, "deu.traineddata")):
            return c
    raise RuntimeError("deu.traineddata nicht gefunden")

# 2) Seiten EINMAL rendern (pymupdf). tesseract kann PDF NICHT lesen
#    ("Pdf reading is not supported") → immer auf gerenderte Bilder, NIE auf die PDF-Datei.
import fitz, glob
OCR_W = 2480                               # feste Zielbreite ~300 dpi A4 für zuverlässige OCR
doc = fitz.open("<eingangs-pdf>")
for i, page in enumerate(doc):
    zoom = OCR_W / page.rect.width         # MediaBox liegt in Scan-pt vor → feste Zielbreite, NICHT dpi=
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    pix.save(f"/tmp/page_{i:03d}.png")     # bleibt auf Platte → §5 nutzt dieselben Seiten, KEIN 2. Render

# 3) OCR auf den gerenderten Seiten (nie tesseract auf die PDF):
import pytesseract
from PIL import Image
ocr_text = "\n".join(
    pytesseract.image_to_string(Image.open(p), lang="deu",
        config=f'--tessdata-dir "{tessdata_dir()}"')
    for p in sorted(glob.glob("/tmp/page_*.png"))
)
```

**Ein Render für beides.** Der Schritt oben rendert die Seiten **einmal** hochauflösend (`OCR_W`, ~300 dpi) für die Texterkennung und legt sie als `/tmp/page_*.png` ab. Die Komprimierung (§5) skaliert **genau diese PNGs** auf die Archivbreite herunter — sie öffnet das PDF nicht erneut und rendert nicht ein zweites Mal. Bewusst `OCR_W` > Archivbreite: OCR braucht die höhere Auflösung, das Archiv nicht (Downscale ist verlustarm).

Liefert OCR an einer entscheidungsrelevanten Stelle nur unsicheren Text (Store, Protokollnummer, Sorte), behandle das als Mehrdeutigkeit (§3) — **rate nichts**. Strain-Lesungen werden zusätzlich gegen den 9-Strain-Index gefuzzt (§2.4), damit OCR-Rauschen nicht jede Sorte zur Rückfrage macht.

**Bekannte OCR-Artefakte auf diesen Belegen** (keine §3-Auslöser, einfach kompensieren):
- `selectedieafs` → `selectedleafs` (l/i-Vertauschung, Scan-Rauschen — für die Store-Zuordnung irrelevant).
- `»-` vor dem Vein: Die Tier-Subzeile beginnt im Scan oft mit `€ »-` statt `€ ·` — das Vein-Muster daher **nicht** auf den Punkt `·` festnageln, sondern auf das Vein-Wort direkt vor `Kratom` matchen: `re.search(r"(White|Green|Red)\s+Kratom", zeile, re.IGNORECASE)` — funktioniert unabhängig vom Trennzeichen davor.
- Mojibake `\xc2\xbb` (= `»`) und `\xe2\x82\xac` (= `€`) in raw bytes: beim Vein-Match auf den Unicode-String (nach `utf-8`-Decode) operieren, nicht auf Byte-Rohdaten.
- `M-CM-<r` für `für` in POS-Beschreibungen: nur Werbematerial, kein Strain — schon durch §2.3 (M-Präfix-Regel) abgedeckt.

**Parsing-Budget:** Extrahiere in **einem** Block, richte bei Artefakten **höchstens einmal** die Regex nach (max. ein Inspektion-/Korrektur-Schritt). Starte keine iterative Debug-Schleife über mehrere Turns — bei anhaltender Unlesbarkeit sofort §3 (Rückfrage), statt im Kreis zu debuggen.

---

## 2. Protokoll parsen (Schritt 2)

### 2.1 Store = Empfänger / Kommissionär — nie der Absender

Auf dem Beleg stehen **zwei** Adressen:
- **Absender** = selectedleafs.com (eigene Anschrift, oft „Fischerstr. 7 · 30167 Hannover"). **Ignorieren.**
- **Empfänger** = der Partner-Store (Kommissionär), z. B. „Spätkauf Hannover, Goseriede 15, 30159 Hannover". **Das ist der Store.**

Verifiziere über die **Unterschriftszeile auf der letzten Seite**: der Store steht bei „… als Kommissionär", selectedleafs bei „… als Kommittent". Bei Konflikt zwischen Empfängerblock und Kommissionär-Zeile → Kommissionär-Zeile gewinnt, sonst (uneindeutig) §3.

> Achtung: Der Store-Name kann selbst „Hannover" enthalten und der Absender steht ebenfalls in Hannover — **beide Hannover-Vorkommen sind irrelevant für die Stadt.** Die Stadt kommt ausschließlich aus dem Metaobjekt (§2.5).

### 2.2 Protokollnummer & Datum

- **Protokollnummer:** Muster `UL-<zahl>-<zahl>` (z. B. `UL-10033-1`), steht neben „Übergabeprotokoll" auf jeder Seite. Das ist dein **Idempotenz-Schlüssel** und Teil des Dateinamens (§4/§5). Fehlt/uneindeutig → §3.
- **Datum:** oben auf Seite 1 im Format `TT.MM.JJJJ` (z. B. `17.06.2026`) → normalisiere zu `JJJJ-MM-TT` (`2026-06-17`). Das ist das **Protokolldatum**, nicht das Verarbeitungsdatum.

### 2.3 Artikel-Tabelle: was als Sorte zählt

Spalten: `Pos. | Artikelnummer | Artikelbezeichnung | Menge | Gewicht | MHD`. Die Artikelbezeichnung hat zwei Zeilen: eine **fette Produktzeile** und optional eine **Subzeile** `{Tier} · {Vein} Kratom` (Tier = `€` | `€€` | `€££`, Vein = White | Green | Red).

**Entscheidungsregel — eine Position ist nur dann eine verkaufbare Sorte, wenn sie die Tier·Vein-Subzeile hat.** Alles ohne diese Subzeile ist **kein Strain** und wird ignoriert:
- POS-Displays, Theken-Material, Werbemittel (typisch Artikel-Nr. mit **`M`-Präfix**, z. B. `M10000-001`) → ignorieren, auch wenn der Titel „White Vein Kratom" enthält.
- Verkaufbare Sorten haben numerische Strain-SKUs (z. B. `10001-002`) **plus** die Subzeile.

`Menge`, `Gewicht`, `MHD` sind für den Post **irrelevant** (Verfügbarkeit ist binär). Nur Strain + Vein zählen.

### 2.4 Strain + Vein extrahieren, Größen dedupen

Je verkaufbarer Position:
- **Strain** = fette Produktzeile **ohne Größen-Suffix** (`25g`/`50g`/`100g` …). „Indo Fusion 25g" → „Indo Fusion". Suffix robust strippen, nicht zeichenweise von Hand: `strain = re.sub(r"\s*\d+\s*g\b", "", produktzeile, flags=re.I).strip()`. `rstrip("0123456789").replace("g","")` lässt „Indo Fusion 25" stehen und zerlegt Strain-Namen, die ein `g` enthalten — nicht verwenden.
- **Vein** = das Wort vor „Kratom" in der Subzeile. „€ · White Kratom" → White.
- **Dedupe über Größen:** dieselbe Strain+Vein-Kombination aus mehreren Positionen (z. B. „Indo Fusion 25g" + „Indo Fusion 50g") kollabiert zu **einer** Sorte „Indo Fusion (White)".

**Fuzzy-Match gegen den kanonischen 9-Strain-Index (Sektion „Restock-Post-Templates" am Ende):** Den OCR-Strain **nicht wörtlich übernehmen**, sondern auf den nächstgelegenen Index-Eintrag mappen (OCR-tolerant, z. B. „lndo Fuslon" → „Indo Fusion", „Borneo Blizz" → „Borneo Bliss"). Liegt der beste Treffer klar über der Ähnlichkeitsschwelle → **diesen kanonischen Namen verwenden** (nicht den rohen OCR-Text). Bleibt der beste Treffer mehrdeutig (zwei Index-Einträge ähnlich nah) oder unter der Schwelle (kein plausibler Match → mutmaßlich echte Katalog-Neuheit oder unlesbar) → **nicht öffentlich raten**, sondern §3 (Rückfrage). Der Index selbst (Sortierung/Tier) lebt dort — hier nur Auflösung + Plausibilisierung.

### 2.5 Store → Metaobjekt-Match → Stadt & Channel (Wunstorf-Regel)

1. **Store → Metaobjekt-Match in zwei Stufen** (Name-Match, kein gespeichertes Mapping) — schlank statt Voll-Dump aller Store-Felder:
   - **1a Match-Stufe (nur `id` + `name`):** Per `graphql_query` alle `liftr_store`-Metaobjekte mit *nur diesen zwei Feldern* holen und **über die Standard-Seitengröße (50) hinaus paginieren** (Cursor / `pageInfo.hasNextPage`, bis ein eindeutiger Match steht oder alle Seiten durch sind) — sonst sind Stores ab dem 51. unauffindbar und würden fälschlich als „kein Match" (§3) behandelt. Den OCR-Store-Namen **OCR-tolerant** gegen diese Namensliste matchen (wie bei den Strains §2.4) → genau eine Store-`id`. **Kein** serverseitiger `display_name`-Filter: gegen OCR-Abweichungen zu fragil (er fände bei Tippfehlern nichts → fälschlich §3).
     ```graphql
     query($cursor: String) {
       metaobjects(type: "liftr_store", first: 50, after: $cursor) {
         edges { node { id name: field(key: "name") { value } } }
         pageInfo { hasNextPage endCursor }
       }
     }
     ```
   - **1b Detail-Stufe (nur der Treffer, nur die nötigen Felder):** Für die gematchte `id` genau die sechs Felder holen, die die Kette braucht — `name`, `postal_code`, `city`→`name`, `district`→`name`, `product_list`, `google_place`. Die city-Referenz wird **im selben Query** zum Klartext aufgelöst (kein separater Lookup). `product_list` liefert Produkt-GIDs (für §2.6). `google_place` ist ein **JSON-codierter String** (Feld-`value` per `json.loads` parsen) und liefert die Keys `id` (= place_id) + `displayName` (= name) für den `{maps_link}` der Post-Templates (Sektion „Restock-Post-Templates", Render-Regeln) — die Keys heißen im Feld **`id`/`displayName`**, **nicht** `place_id`/`name`; ein `google_place['place_id']` wirft `KeyError`. **Ohne dieses Feld kein gültiger Maps-Link**, der Post ginge sonst mit Platzhalter raus.
     ```graphql
     query($id: ID!) {
       metaobject(id: $id) {
         name:         field(key: "name")         { value }
         postal_code:  field(key: "postal_code")  { value }
         city:         field(key: "city")     { reference { ... on Metaobject { name: field(key: "name") { value } } } }
         district:     field(key: "district") { reference { ... on Metaobject { name: field(key: "name") { value } } } }
         product_list: field(key: "product_list") { value }
         google_place: field(key: "google_place") { value }
       }
     }
     ```
   - **Nie** `fields { key value }` (= alle ~25 Felder inkl. der JSON-Blobs `google_place`/`opening_hours` und der `assortment_`/`service_`/`testimonial_list`-Referenzen) über alle Stores ziehen — genau das ist der Token-Fresser, den diese zwei Stufen ersetzen (schlanke Namensliste + ein Einzelstore statt Voll-Dump).
2. **Stadt/Channel kommt aus dem Metaobjekt, nicht aus der Belegadresse.** Ein Store kann physisch z. B. in Wunstorf liegen, aber redaktionell der Hannover-Page/dem Hannover-Channel zugeordnet sein — dann ist die maßgebliche Stadt **Hannover**. Lies die zugewiesene Stadt aus dem Store-Metaobjekt (Stadt-/`district`-Zuordnung), **nicht** die Postanschrift.
3. Die Belegstadt dient nur als **Plausi-Check**: weicht sie stark von der Metaobjekt-Stadt ab, ist das ein Signal, aber das Metaobjekt gewinnt. Nur wenn **kein eindeutiger Store-Match** existiert oder dem Store **keine Stadt** zugeordnet ist → §3.

Dieselbe aufgelöste Stadt benutzt du in §6 für den Drive-Pfad — so bleiben Channel und Ablage konsistent.

### 2.6 Neu vs. aufgefüllt (pro Sorte, via `product_list`)

`product_list` enthält **Produkt-GIDs** (z. B. `gid://shopify/Product/15603432653149`), keine Klartext-Strain-Namen. Darum **in zwei Schritten**:

**Schritt A — GIDs zu Titeln auflösen (ein Query für alle):**
```graphql
query($ids: [ID!]!) {
  nodes(ids: $ids) {
    ... on Product { id title }
  }
}
```
`ids` = JSON-Parse der `product_list`-Value aus §2.5 1b (String → Array). Das ergibt eine Map `{ gid → title }`. Titel sind Klartext-Strain-Namen ohne Größensuffix (z. B. `"Indo Fusion"`).

**Schritt B — Zuordnung pro deduplizierter Sorte (§2.4):**
- Strain-Name aus OCR-Extraktion (§2.4, kanonisch) in der Titel-Map enthalten (Fuzzy-tolerant) → **aufgefüllt** (📦 Restock).
- Nicht enthalten → **neue Sorte** (🌿).

Die Entscheidung ist **pro Sorte**: ein Protokoll kann gleichzeitig aufgefüllte und neue Sorten enthalten → zwei Buckets.

**Write-back (§8) und Query-Effizienz:** `nodes(ids:)` ist batch-fähig — **ein** Query für beliebig viele GIDs, keine N-Aliase. Den Query **nicht** aufsplitten (kein `product1: product(id:), product2: product(id:), …`).

### 2.7 Was dieser Skill liefert (Übergabe-Payload)

Du übergibst an den Render-/Post-Schritt (Templates → Sektion „Restock-Post-Templates" am Ende; Channel → `telegram.md` §2.1) **strukturierte Daten, keinen fertigen Text**:

```
{
  "stadt":        "<aufgelöste Metaobjekt-Stadt>",   // bestimmt den Channel (dort)
  "store_ref":    "<liftr_store-Metaobjekt + Name>",
  "protokoll_nr": "UL-10033-1",
  "aufgefuellt":  [ {"strain": "...", "vein": "White|Green|Red"}, ... ],  // 📦
  "neue_sorten":  [ {"strain": "...", "vein": "White|Green|Red"}, ... ]   // 🌿
}
```

Leere Buckets sind erlaubt. Sind **beide** Buckets leer (nur Werbemittel/POS im Protokoll), gibt es **nichts zu posten** — kein Fehler, kein Abbruch: du überspringst Schritt 3 und legst das PDF trotzdem ab (§5/§6), Status „keine Sorten, nichts gepostet" (§7).

---

## 3. Mehrdeutigkeit → Abbruch (verbindlich)

**Ist Store oder Stadt nicht eindeutig bestimmbar, postest du NICHTS öffentlich.** Stattdessen: kurze Rückfrage ins Topic „Protokoll-Eingang" + Kette abbrechen (kein Post, keine Drive-Ablage). Auslöser:

- Store-Name matcht **null oder mehrere** `liftr_store`-Metaobjekte.
- Gematchter Store hat **keine** zugewiesene Stadt/Channel.
- **Protokollnummer** fehlt oder ist unlesbar (ohne sie keine sichere Idempotenz).
- Strain lässt sich nicht zuverlässig lesen / matcht keinen bekannten Index-Eintrag (mutmaßlicher OCR-Fehler).
- Empfänger/Kommissionär-Block unlesbar.

Rückfrage knapp und konkret halten, z. B.: „Protokoll `UL-10033-1`: Store ‚Spätkauf Hannover' matcht 2 Metaobjekte (Goseriede / Limmerstr.). Welcher? Verarbeitung pausiert." Erst nach Klärung erneut anstoßen.

---

## 4. Idempotenz — jedes Protokoll genau einmal

**Schlüssel = Protokollnummer** (`UL-10033-1`). Da der Dateiname in Drive die Nummer enthält (§5), ist der Idempotenz-Check ein Existenz-Check im Ziel-Ordner:

1. Ziel-Ordner in Drive bestimmen — `ensure_folder_path` (§6) liefert die Zielordner-`id` (idempotent; legt den Stadt/Store-Pfad bei Bedarf an, ohne zu duplizieren).
2. In diesem Ordner per `list_files` prüfen, ob bereits eine Datei mit Endung `_<protokoll_nr>.pdf` liegt.
3. **Existiert sie → abbrechen**, nicht erneut posten/ablegen. Status ins Topic: „Protokoll `UL-10033-1` bereits verarbeitet, übersprungen."

Diesen Check **vor** dem Posten ausführen (§1), damit ein doppelt eingereichtes Protokoll keinen Doppel-Post erzeugt. Kein externer State/keine DB nötig — der Drive-Ordner ist die Quelle der Wahrheit (web-only-tauglich).

---

## 5. Komprimieren + Umbenennen (Schritt 4)

Im **Agent-Sandbox (Code-Execution, nicht lokal, kein VPS)**.

**Zieldateiname:** Der Ordnerpfad (§6) trägt bereits Stadt + Store — darum bleibt der Dateiname kurz: **Datum** (Sortierung im Store-Ordner) + **Protokollnummer** (eindeutige ID / Idempotenz-Schlüssel):
```
{JJJJ-MM-TT}_{protokoll_nr}.pdf
```
- Beide Teile sind deterministisch aus dem Beleg ableitbar (§2.2) → derselbe Beleg ergibt immer denselben Namen.
- Datum als `JJJJ-MM-TT` zuerst, weil das verlässlich chronologisch sortiert (die reine UL-Nummer sortiert lexikalisch falsch an Stellen-Grenzen).

Beispiel: `2026-06-17_UL-10033-1.pdf`

**Komprimierung — die Seiten sind in §1.1 schon gerendert (`/tmp/page_*.png`, Graustufe, `OCR_W` breit). Hier nur herunterskalieren, kein zweiter Render:**

```python
# Agent-Sandbox (Code-Execution) — Archiv aus den §1.1-Seiten, KEIN zweites fitz.open()/Rendern
import fitz, glob, io
from PIL import Image
ARCH_W, Q = 1240, 75                       # ~150 dpi A4; Fallback 1500/q80
out = fitz.open(); A4 = fitz.paper_rect("a4")
for p in sorted(glob.glob("/tmp/page_*.png")):       # die in §1.1 gerenderten OCR-Seiten
    img = Image.open(p)                              # bereits Graustufe, OCR_W breit
    img = img.resize((ARCH_W, round(img.height * ARCH_W / img.width)))
    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=Q)
    npage = out.new_page(width=A4.width, height=A4.height)
    npage.insert_image(npage.rect, stream=buf.getvalue())
out.save("2026-06-17_UL-10033-1.pdf", deflate=True, garbage=4)
```
- **Render-Sharing:** §1.1 rendert das PDF einmal hochauflösend (`OCR_W`) für die OCR; hier werden exakt diese PNGs auf `ARCH_W` (1240 px) herunterskaliert. Das spart das zweite Öffnen/Rendern des PDFs — der ursprünglich teuerste, doppelt ausgeführte Schritt. Sind die PNGs (wider Erwarten) nicht vorhanden, fällt der Schritt auf `fitz.open("<eingangs-pdf>")` + Render bei `ARCH_W` zurück.
- **1240 px / Graustufe / JPEG q75** drückt einen 5-MB-Scan auf ~0,3 MB und bleibt OCR-sicher (am realen Beleg verifiziert, Kerndaten + Umlaute). Nur wenn das Ergebnis unscharf würde, auf **1500 px / q80** (~0,5 MB) hochgehen.
- Da Protokolle **immer Scans** sind, ist `pymupdf` der **einzige** Pfad — `pikepdf` rührt die eingebetteten Flate-Bilder nicht an (0 % Kompression) und ist hier nutzlos. `pymupdf` rendert PDF→Bild selbst, also wird **kein** poppler/`pdf2image` gebraucht.

Verifiziere nach der Komprimierung, dass die Datei > 0 Byte und valide ist, bevor du sie hochlädst.

---

## 6. Drive-Ablage (Schritt 5)

**Voraussetzung (Egress):** Die komprimierte PDF wird per `PUT` **direkt** aus der Sandbox zur Google-Upload-URL geschickt — die Bytes laufen nicht durch den Agenten-Kontext. Dafür muss der Upload-Host (typisch `www.googleapis.com`) in der **Egress-Allowed-Hosts-Liste** des Environments eingetragen sein. Fehlt er → Upload schlägt mit Netzwerkfehler fehl → Abbruch+Status (§7), **kein** Retry. Den genauen Host einmalig aus einer Test-Session ablesen (URL kommt im Rückgabe-Feld `uploadUrl`) und build-time ins Environment eintragen — hier nicht hardcoden.

**Ordnerstruktur (B3):**
```
<Übergabeprotokolle-Wurzel>/{city.name}/{postal_code} {store.name}/
```
- Alle Segmente kommen **1:1 aus den `liftr_store`-Metaobjekt-Feldern** des gematchten Stores (§2.5), **nie** aus dem rohen Belegtext oder OCR — das hält die Namen stabil und damit die Idempotenz (§4) intakt:
  - `{city.name}` = `name`-Feld des verknüpften city-Metaobjekts (Klartext, z. B. `Hannover`) — nicht die Belegstadt, nicht lowercase. Lies dieses Feld aktiv aus dem Metaobjekt, rate es nicht aus der Adresse.
  - `{postal_code}` = `postal_code`-Feld des Stores (z. B. `30159`), als Präfix zur Sortierung und Disambiguierung gleichnamiger Stores.
  - `{store.name}` = `name`-Feld des Stores (Klartext mit Umlauten/Leerzeichen, z. B. `Spätkauf Hannover`).
- **Keine Slugifizierung.** Großschreibung, Leerzeichen und Umlaute (`ä ö ü ß`) sind in Drive zulässig und gewollt (lesbare Ordner). Die einzige Anforderung an den Namen ist Determinismus aus stabiler Quelle (Metaobjekt-Feld) — die ist erfüllt; Groß/Klein und Umlaut sind für die Idempotenz irrelevant.
- **Ordnerpfad idempotent auflösen/anlegen — ein Call.** Statt `list_files`+`create_folder` von Hand zu kombinieren: `ensure_folder_path` mit `parentFolderId` = Übergabeprotokolle-Wurzel und `segments = [ "{city.name}", "{postal_code} {store.name}" ]`. Das Tool legt fehlende Segmente an und nutzt vorhandene wieder — **mkdir-p, idempotent**: nie ein zweiter gleichnamiger Ordner. Der Vergleich ist **serverseitig** Unicode-NFC-normalisiert (ä/ö/ü/ß sicher), exakt und case-sensitiv; gleichnamige Dateien werden ignoriert. Du musst Namen daher **nicht mehr selbst NFC-normalisieren** und keinen Existenz-Check vorschalten — das übernimmt das Tool. Rückgabe: `{ id, name, webViewLink?, created[] }`. `id` ist der **Zielordner** (für die PDF-Ablage und den Idempotenz-Check §4); `created` listet die in diesem Lauf neu angelegten Segmente (leer = Pfad existierte bereits, z. B. beim Zweitlauf).
- Die **Wurzel/Folder-ID** ist Agent-Config (build-time, `global-agent-framework`) — nicht hier hardcoden.

**Upload-Ablauf (zweistufig, Referenz-Pfad):**

Protokoll-PDFs sind Scans (~500 KB–1 MB nach Komprimierung). Das überschreitet das Inline-base64-Budget des Agenten → `upload_file` ist nicht verwendbar; stattdessen:

1. **Komprimierung abschließen (§5), dann erst Session holen.** Die Upload-Session (`create_upload_session`) ist an die bei der Eröffnung deklarierte `sizeBytes` gebunden — ändert sich die Dateigröße danach (z. B. durch nochmalige Komprimierung), ist die Session **ungültig** und jeder PUT liefert HTTP 400. Daher: **erst komprimieren, Endgröße feststellen, dann Session eröffnen** — nie umgekehrt.
2. **Session holen** — `create_upload_session` mit `name`, `mimeType: "application/pdf"`, `sizeBytes` (exakte Byte-Zahl der finalen PDF, z. B. via `os.path.getsize()`) und `parentFolderId` (Zielordner-ID). Gibt `{ uploadUrl, name, parentFolderId }` zurück.
3. **Bytes finalisierend hochladen** — Die `uploadUrl` ist eine **resumable** Session (`uploadType=resumable`). Ein Single-`PUT` finalisiert sie **nur**, wenn er den Header `Content-Range: bytes 0-(N-1)/N` trägt (N = exakte Byte-Zahl der finalen PDF, **identisch** zur deklarierten `sizeBytes`). **Ohne `Content-Range` hält Google die Session offen und antwortet HTTP 308 (Resume Incomplete) — die Datei wird dann NICHT committet.** Erfolg ist **ausschließlich 200 oder 201**; **308 ist kein Erfolg, sondern ein nicht abgeschlossener Upload** und wird wie jeder Non-2xx behandelt (Abbruch, §7). Die Session-URL trägt ihre eigene Autorisierung; kein zusätzliches Google-Credential nötig. **Die lokale `/tmp`-Datei beweist die Ablage nicht** — Bestätigung ist allein der 2xx-Status des PUT (optional härtbar via `list_files` auf den finalen Dateinamen im Zielordner).

**Häufige Fehlerursache HTTP 400:** Fast immer ein `sizeBytes`-Mismatch — die deklarierte Größe stimmt nicht mit der tatsächlichen Datei überein, weil die Datei **nach** der Session-Eröffnung noch verändert wurde. Lösung: neue Session mit korrekter `sizeBytes` (nicht dieselbe Session erneut verwenden). Die 256-KB-Chunk-Grenze (262.144 Bytes) ist **kein hartes Limit** für den Datei-Upload — sie betrifft nur die Chunk-Größe bei resumable Multi-Part-Uploads, nicht die Gesamtgröße der Datei.

```bash
# Agent-Sandbox (Code-Execution) — finalisierender Single-PUT einer resumable Session
SIZE=$(stat -c%s "<komprimierte-pdf>")   # exakt dieselbe Zahl wie sizeBytes oben
curl -s -o /dev/null -w "%{http_code}" \
  -X PUT \
  -H "Content-Length: ${SIZE}" \
  -H "Content-Range: bytes 0-$((SIZE-1))/${SIZE}" \
  --data-binary @"<komprimierte-pdf>" \
  "<uploadUrl>"
# Erfolg = ausschließlich 200 oder 201.
# 308 (Resume Incomplete) = NICHT finalisiert (Content-Range fehlte/Teil-Upload) → wie Non-2xx: Abbruch + Fehler-Status (§7).
# Jeder andere Non-2xx → ebenso Abbruch.
```

**Fail-closed:** Gibt `create_upload_session` keinen `uploadUrl` zurück (Fehler, Netzwerkproblem), oder liefert der PUT einen Non-2xx-Status (**inkl. 308 = nicht finalisiert**) → Abbruch, keine Drive-Ablage, Fehler-Status ins Topic. Kein stiller Weiter-Lauf ohne abgelegte PDF.

Beispiel-Ablage (Ergebnis):
```
…/Übergabeprotokolle/Hannover/30159 Spätkauf Hannover/2026-06-17_UL-10033-1.pdf
```

---

## 7. Status-Rückmeldung ins Topic (Schritt 6, kompakt)

Genau **eine** knappe Status-Zeile ins Topic „Protokoll-Eingang", je nach Ausgang:

| Ausgang | Status (Beispiel) |
|---|---|
| Erfolg | „✅ `UL-10033-1` — Spätkauf Hannover (Hannover): 1 aufgefüllt, 0 neu. Gepostet + in Drive abgelegt." |
| Nichts zu posten | „✅ `UL-10033-1` — nur Werbemittel/POS, keine Sorten. Kein Post, PDF abgelegt." |
| Bereits verarbeitet | „↩︎ `UL-10033-1` bereits verarbeitet, übersprungen." |
| Mehrdeutig (§3) | „⚠️ `UL-10033-1` — <konkrete Rückfrage>. Verarbeitung pausiert." |

Keine Sorten-/Mengen-Details öffentlich in den City-Channel schreiben, die nicht aus den Restock-Post-Templates stammen — der Status bleibt im Topic.

Wurden **neue Sorten** gepostet, den Write-back (§8) in derselben Zeile kurz quittieren, z. B.: „✅ `UL-10040-1` — Kiosk Linden (Hannover): 0 aufgefüllt, 1 neu (Sortiment ergänzt). Gepostet + in Drive abgelegt."

---

## 8. Write-back: neue Sorten in `product_list` (nach dem Post)

Läuft als **Schritt 5 in §1, direkt nach dem erfolgreichen 🌿-Post** (Schritt 4) und betrifft **nur den `neue_sorten`-Bucket**. Zweck: Eine erstmals gelieferte Sorte wird ins Sortiment des Stores aufgenommen, damit dieselbe Sorte beim **nächsten** Protokoll korrekt als 📦 (aufgefüllt) statt erneut als 🌿 erkannt wird (§2.6). Ohne Write-back bliebe jede neue Sorte dauerhaft „neu".

**Regeln:**
- **Nur anhängen, nie entfernen.** Du fügst jede tatsächlich gepostete neue Sorte zur `product_list` des gematchten Store-Metaobjekts hinzu. Das Auslisten ausverkaufter Sorten macht der Mensch **manuell** — der Agent löscht nie aus `product_list`.
- **Idempotent, kein Clobbern.** Vor dem Anhängen prüfen, ob die Sorte schon enthalten ist (sollte sie nicht, sonst wäre sie 📦 gewesen); bestehende Einträge nie überschreiben, nur ergänzen.
- **Repräsentation deckungsgleich mit der Leseseite (§2.6).** In genau der Form anhängen, in der `product_list` Sorten führt, damit Lese- (§2.6) und Schreibseite konsistent bleiben — sonst zählt dieselbe Sorte beim nächsten Lauf wieder als neu.
- **Mutation-Signatur: `value` ist `String!`, nicht `JSON!`.** Das Metaobject-Feld `product_list` trägt einen JSON-codierten String — das GraphQL-Schema akzeptiert den Wert als `String!`-Literal (kein `$value: JSON!`-Variable). Immer den serialisierten JSON-Array direkt inline übergeben:
  ```graphql
  mutation($id: ID!) {
    metaobjectUpdate(id: $id, metaobject: {
      fields: [{ key: "product_list", value: "["gid://shopify/Product/111","gid://shopify/Product/222"]" }]
    }) {
      metaobject { id product_list: field(key: "product_list") { value } }
      userErrors { field message }
    }
  }
  ```
  Eine Variable `$value: JSON!` erzeugt einen Type-Mismatch-Error. Den neuen GID per `products(first:5, query:"title:\"<strain-name>\"")`  ermitteln; `first:` **nicht** weglassen (sonst `"first or last must be provided"`-Error).
- **Neue Session bei Größenänderung (→ §6).** Dieser Hinweis gilt nicht direkt für den Write-back, sondern ist in §6 verankert — der Vollständigkeit halber: Write-back läuft **vor** dem Upload; die Upload-Session wird erst danach eröffnet, wenn die finale PDF-Größe feststeht.
- **Nur bei erfolgreichem Post.** Schlägt der 🌿-Post fehl, **kein** Write-back — sonst meldete `product_list` eine Sorte als geführt, die nie announced wurde.
- **Tool / Permission ist build-time.** Der Write-back ist eine **Mutation** aufs Metaobjekt; das read-only `graphql_query` reicht dafür nicht. Tool-Oberfläche, Least-Privilege und Bestätigungs-Policy regelt `global-agent-framework` — dieser Skill beschreibt nur das **Verhalten**, nicht die Tool-Mechanik.

**Bewusste Folge fürs Typing:** Nimmt der Mensch eine ausverkaufte Sorte später aus `product_list` und sie wird erneut geliefert, postet der Agent sie wieder als 🌿 „Neue Sorte" (nicht 📦). Das ist korrekt (Trigger = Membership in `product_list`) und braucht **keinen** „kennen-wir-schon"-Sonderfall. Wer das Framing später glätten will, müsste eine separate Historie führen — bewusst nicht Teil dieser Kette.

---

## Restock-Post-Templates (📦 / 🌿)

Die in §1/§2.7 erwähnte Übergabe an den „Telegram-Schritt" rendert **mit diesen Templates** — sie liegen bewusst hier, damit die Restock-Kette ohne Sprung in eine andere Domänen-reference auskommt. Das **generische** Telegram-Handwerk (Format-System, vollständige Emoji-Legende, Channel-Ableitung `kratom_<stadt>` inkl. Override, Posting-Mechanik, Pinned/Launch) steht in `references/telegram.md`; hier nur die zwei Post-Typen, die diese Kette erzeugt.

Du lieferst aus §2.7 **strukturierte Buckets** (`aufgefuellt` → 📦, `neue_sorten` → 🌿). Pro nicht-leerem Bucket genau **ein** Post in den City-Channel der aufgelösten Stadt (§2.5).

### 📦 Frisch aufgefüllt (Bucket `aufgefuellt`)

```
📦 **Frisch aufgefüllt**
{store_name} · {stadtteil}

{Strain} ({Vein}), {Strain} ({Vein}), …

[Google Maps öffnen]({maps_link})
```

- **Headline = Typ-Label** „Frisch aufgefüllt" (fett). `{store_name}` mager in der Meta-Zeile (`{store_name} · {stadtteil}`), nie fett.
- **Produkte = flache, kommagetrennte Liste**, jeder Strain mit `(Vein)` inline. Keine Vein-Gruppierung, keine Vein-Circles, kein Tier im Post.
- **Keine Menge, keine Größe** — Verfügbarkeit ist binär.
- **Sortierung: Vein (White → Green → Red), innerhalb nach Tier aufsteigend (€ → €€ → €££).** Das Tier ist nur Sort-Key und wird **nicht** angezeigt.

**Kanonischer 9-Strain-Index** (Sortier- und Plausibilisierungs-Quelle; derselbe Index, gegen den §2.4 die OCR-Lesungen fuzzt):

| Tier | White | Green | Red |
|------|-------|-------|-----|
| € | Indo Fusion | Borneo Lift | Suma Sooth |
| €€ | Suma Rush | Indo Fresh | Borneo Bliss |
| €££ | Java Spark | Bali Oasis | Bali Sunset |

Lesereihenfolge = White-Spalte oben→unten, dann Green, dann Red. Beispiel: Java Spark + Indo Fresh + Suma Sooth → „Java Spark (White), Indo Fresh (Green), Suma Sooth (Red)".

### 🌿 Neue Sorte (Bucket `neue_sorten`)

Strain ist die News, passt komplett in die Headline (kein Payload-Block). Headline-Prefix „Neu:", Vein inline `(Vein)`.

```
🌿 **Neu: {sorte} ({vein})**
{store_name} · {stadtteil}

[Google Maps öffnen]({maps_link})
```

- Bei mehreren neuen Sorten in einem Lauf: ein 🌿-Post **pro Sorte** (jede ist eine eigene News).
- Der erfolgreiche 🌿-Post ist die Bedingung für den Write-back (§8): erst posten, dann `product_list` ergänzen.

### Render-Regeln (beide Typen)

- **`parse_mode = HTML`.** Inline-Link als `<a href="…">Text</a>`; **MarkdownV2 nicht** verwenden (müsste `.`, `-`, `(`, `)` in Adressen/Maps-Links escapen → bricht ständig).
- **`{maps_link}`** = `https://www.google.com/maps/search/?api=1&query={name}&query_place_id={place_id}` aus dem `google_place`-Feld des Stores. **Reale JSON-Keys im Feld:** `id` (= `{place_id}`) und `displayName` (= `{name}`) — **nicht** `place_id`/`name`. Den `query`-Wert (`{name}` = `displayName`, enthält Leerzeichen/Umlaute) mit `urllib.parse.quote` URL-kodieren; **danach** im HTML **jedes `&` → `&amp;`**.
- **CTA** = Link-Text „Google Maps öffnen", Leerzeile davor, kein Pfeil-Präfix, keine Urgency-/„Jetzt"-Floskeln, kein roher URL, kein Underline, **Link-Preview aus**.
- **`{stadtteil}`** = `district`→`name` des Stores (GID auflösen, nicht aus PLZ raten). Ton: warm, lokaler Tipp — kein Shop-Ton.
- Posting läuft über die Telegram-Post-Tools (`post_message`); Tool-Oberfläche/Permission ist build-time (`global-agent-framework`), nicht hier.
