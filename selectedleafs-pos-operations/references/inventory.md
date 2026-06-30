# Inventory — Bestandsprotokoll ablegen

Bestandsprotokoll aus Telegram herunterladen, Partner identifizieren, komprimieren/umbenennen und in Google Drive ablegen. Diese reference ist **selbsttragend** — sie trägt alle Mechanik, die die Kette braucht, inline (Download, OCR, Store-Match, Upload), ohne Sprung in eine andere Domänen-reference. Gegenüber der Restock-Domäne **reduziert**: kein Sorten-/Vein-Parsing, kein Neu-vs-aufgefüllt, kein `product_list`-Write-back, **kein** öffentlicher City-Channel-Post. Inventory legt ausschließlich ab und meldet Status ins interne Topic.

## 1. Eingang & Reihenfolge

Du bekommst ein PDF aus dem Topic „Bestandsprotokolle" (`registry.md §3`, `message_thread_id: 34`) in die Sandbox (Schritt 1). Dann **in dieser Reihenfolge**:

1. **Download (§2)** — PDF referenzbasiert in die Sandbox holen, dann Seiten für OCR rendern.
2. **Minimal-Parsen (§3)** — nur Empfängerblock (Store) und Datum lesen, **nicht** die Artikeltabelle.
3. **Store-Match (§4)** — OCR-Name → `liftr_store`-Metaobjekt, Stadt auflösen.
4. **Mehrdeutig? (§5)** → Rückfrage ins Topic, abbrechen. Sonst weiter.
5. **Idempotenz-Check (§6)** — Zielordner via `ensure_folder_path` + `list_files` auf `{datum}.pdf`; existiert sie → Rückfrage ins Topic, **kein Upload**, abbrechen.
6. **Komprimieren + umbenennen (§7)**.
7. **In Drive ablegen (§8)**.
8. **Status** ins Topic (§9).

Kein Sorten-Schritt, kein Channel-Post, kein Write-back — die Kette endet mit der Drive-Ablage.

---

## 2. PDF in die Sandbox holen + rendern (Schritt 1, Referenz-Pfad)

Bestandsprotokolle sind unterschriebene Scans (~0,5–1 MB, kein Text-Layer) — das **Inline-base64-Budget** des Agenten reicht nicht, `download_file` (Bytes als base64 durch den Kontext) ist daher **nicht** der Weg. Referenz-Pfad:

1. **Referenz holen** — `create_download_url` mit der `file_id` des PDF-Anhangs (aus `document.file_id` des eingehenden Updates, **nicht** die `message_id`). Der Bot-Token bleibt serverseitig; das Tool lädt die Datei serverseitig von Telegram, legt die Bytes in R2 ab und gibt JSON zurück: `{ url, key, file_name, mime_type, size, expires_in }`. `url` ist eine **token-freie, kurzlebige** presigned GET-URL.
2. **Bytes direkt ziehen** — die `url` per `curl -o` in die Sandbox; die Bytes laufen **nicht** durch den Agenten-Kontext. Zügig nach dem Call ausführen — die URL läuft nach `expires_in` Sekunden ab.

```bash
# Agent-Sandbox (Code-Execution)
curl -s -o "<eingangs-pdf>" "<url>"
# Danach prüfen: Datei > 0 Byte und valides PDF, bevor du weitermachst.
```

**Egress:** Der Presign-Host des R2-Buckets (`<account-id>.r2.cloudflarestorage.com`) muss in den **Allowed-Hosts** des Environments stehen, sonst `curl`-Netzwerkfehler. Build-time in die Agent-Config (`global-agent-framework`), **nicht** hier hardcoden.

**Fail-closed:** Keine `url` zurück, oder `curl` liefert Non-2xx / 0-Byte → Abbruch, Fehler-Status ins Topic (§9), **kein** Retry, **kein** base64-Fallback über `download_file`.

**Seiten rendern (OCR-Pflichtpfad — kein Textextraktions-Versuch).** Scans haben keinen Text-Layer; `tesseract` kann PDF **nicht** direkt lesen (`"Pdf reading is not supported"`) → immer auf gerenderte Bilder. Die tesseract-Engine ist im Base-Image, das deutsche Sprachpaket kommt als pip-Paket `tessdata.fast-deu` (kein apt — in der Managed-Agents-Beta nicht provisioniert). Den tessdata-Ordner nicht blind aus `tessdata.data_path()` nehmen, sondern den Kandidaten finden, der `deu.traineddata` enthält:

```python
# Agent-Sandbox: 1) tessdata-Ordner robust bestimmen
import tessdata, os, sys
def tessdata_dir():
    for c in (tessdata.data_path(), os.path.join(sys.prefix, "share", "tessdata"),
              "/usr/local/share/tessdata", "/usr/share/tessdata"):
        if os.path.exists(os.path.join(c, "deu.traineddata")):
            return c
    raise RuntimeError("deu.traineddata nicht gefunden")

# 2) Seiten EINMAL rendern (pymupdf, Graustufe). NIE tesseract auf die PDF.
import fitz, glob
OCR_W = 2480                               # feste Zielbreite ~300 dpi A4
doc = fitz.open("<eingangs-pdf>")
for i, page in enumerate(doc):
    zoom = OCR_W / page.rect.width         # feste Zielbreite, NICHT dpi=
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    pix.save(f"/tmp/page_{i:03d}.png")     # bleibt auf Platte → §7 nutzt dieselben Seiten, KEIN 2. Render

# 3) OCR auf den gerenderten Seiten:
import pytesseract
from PIL import Image
ocr_text = "\n".join(
    pytesseract.image_to_string(Image.open(p), lang="deu",
        config=f'--tessdata-dir "{tessdata_dir()}"')
    for p in sorted(glob.glob("/tmp/page_*.png"))
)
```

**Ein Render für beides:** `OCR_W` (~300 dpi) für die Texterkennung; die Komprimierung (§7) skaliert **genau diese PNGs** herunter, öffnet das PDF nicht erneut. Bekannte OCR-Artefakte auf diesen Belegen (kompensieren, kein §5-Auslöser): `selectedieafs`→`selectedleafs` (l/i-Vertauschung, für die Store-Zuordnung ohnehin irrelevant, da Absender). Liefert OCR an entscheidungsrelevanter Stelle (Store-Name, Datum) nur unsicheren Text → §5, **rate nichts**. Parsing-Budget: in **einem** Block extrahieren, höchstens **einmal** die Regex nachrichten, keine iterative Debug-Schleife.

---

## 3. Minimal-Parsen — nur Empfängerblock + Datum

**Bewusster Unterschied zu Restock:** Die Artikeltabelle (Pos./Artikelnummer/SOLL-Bestand/IST-Bestand) wird **nicht** ausgewertet — sie ist der eigentliche Beleginhalt fürs Archiv, nicht Input für eine Entscheidung. OCR/Lesefokus beschränkt sich auf zwei Felder:

### 3.1 Store = Empfänger/Kommissionär — nie der Absender

Auf dem Beleg stehen **zwei** Adressen — Absender = selectedleafs.com (eigene Anschrift, oft „Fischerstr. 7 · 30167 Hannover", **ignorieren**) und Empfänger = der Partner-Store (Kommissionär). Verifiziere über die Unterschriftszeile auf der letzten Seite: der Store steht bei „… als Kommissionär", selectedleafs bei „… als Kommittent". Bei Konflikt zwischen Empfängerblock und Kommissionär-Zeile → Kommissionär-Zeile gewinnt, sonst (uneindeutig) §5. Achtung: Der Store-Name kann selbst „Hannover" enthalten und der Absender steht ebenfalls in Hannover — beide Hannover-Vorkommen sind irrelevant für die Stadt (die kommt aus dem Metaobjekt, §4).

### 3.2 Datum

Oben auf Seite 1 im Format `TT.MM.JJJJ` (z. B. `16.06.2026`) → normalisiere zu `JJJJ-MM-TT` (`2026-06-16`). Das ist das **Protokolldatum**, nicht das Verarbeitungsdatum. Fehlt/uneindeutig → §5.

### 3.3 Kunden-Nr. — nicht verwendet

Bestandsprotokolle tragen eine „Kunden-Nr." (z. B. `10034`) im Kopf. Diese ist **partner-konstant**, nicht protokoll-eindeutig, und liegt **nicht** im `liftr_store`-Metaobjekt. Sie wird hier **weder für den Match noch für den Dateinamen** verwendet (§4/§7) — eine Lesepflicht weniger, eine Fehlerquelle weniger.

---

## 4. Store → Metaobjekt-Match → Stadt

Store-Match in zwei Stufen (Name-Match, kein gespeichertes Mapping) — schlank statt Voll-Dump aller Store-Felder:

**1a Match-Stufe (nur `id` + `name`):** Per `graphql_query` alle `liftr_store`-Metaobjekte mit *nur diesen zwei Feldern* holen und **über die Standard-Seitengröße (50) hinaus paginieren** (Cursor / `pageInfo.hasNextPage`, bis ein eindeutiger Match steht oder alle Seiten durch sind) — sonst sind Stores ab dem 51. unauffindbar und würden fälschlich als „kein Match" (§5) behandelt. Den OCR-Store-Namen (§3.1) **OCR-tolerant** gegen diese Namensliste matchen → genau eine Store-`id`. **Kein** serverseitiger `display_name`-Filter (gegen OCR-Abweichungen zu fragil).

```graphql
query($cursor: String) {
  metaobjects(type: "liftr_store", first: 50, after: $cursor) {
    edges { node { id name: field(key: "name") { value } } }
    pageInfo { hasNextPage endCursor }
  }
}
```

**1b Detail-Stufe (nur der Treffer, nur die nötigen Felder):** Für die gematchte `id` genau drei Felder holen — `name`, `postal_code`, `city`→`name` (die city-Referenz im selben Query zum Klartext aufgelöst). **Nicht** benötigt (anders als die Restock-Domäne): `district`, `product_list`, `google_place` — Inventory postet nicht öffentlich, braucht also weder Maps-Link noch Sortiments-Liste:

```graphql
query($id: ID!) {
  metaobject(id: $id) {
    name:        field(key: "name")        { value }
    postal_code: field(key: "postal_code") { value }
    city:        field(key: "city") { reference { ... on Metaobject { name: field(key: "name") { value } } } }
  }
}
```

**Nie** `fields { key value }` über alle Stores ziehen (= alle ~25 Felder inkl. JSON-Blobs — der Token-Fresser, den die zwei Stufen ersetzen).

**Stadt kommt aus dem Metaobjekt, nicht aus der Belegadresse (Wunstorf-Regel):** Ein Store kann physisch z. B. in Wunstorf liegen, aber redaktionell der Hannover-Page zugeordnet sein — dann ist die maßgebliche Stadt **Hannover**. Lies die zugewiesene Stadt aus dem `city`-Feld, **nicht** die Postanschrift. Die Belegstadt dient nur als Plausi-Check (weicht sie stark ab, ist das ein Signal, aber das Metaobjekt gewinnt). Nur wenn **kein eindeutiger Store-Match** existiert oder dem Store **keine Stadt** zugeordnet ist → §5.

Dieselbe aufgelöste Stadt benutzt du in §8 für den Drive-Pfad.

---

## 5. Mehrdeutigkeit → Abbruch (verbindlich)

**Ist Store oder Stadt nicht eindeutig bestimmbar, legst du NICHTS ab.** Rückfrage ins Topic „Bestandsprotokolle" + Kette abbrechen. Adressierung → §9. Auslöser:

- Store-Name matcht **null oder mehrere** `liftr_store`-Metaobjekte.
- Gematchter Store hat **keine** zugewiesene Stadt.
- **Datum** fehlt oder ist unlesbar (ohne es kein Dateiname/Idempotenz-Schlüssel).
- Empfänger/Kommissionär-Block unlesbar.

Rückfrage knapp und konkret, z. B.: „Bestandsprotokoll vom 16.06.2026: Store ‚Spätkauf Hannover' matcht 2 Metaobjekte. Welcher? Verarbeitung pausiert."

---

## 6. Idempotenz — jedes Protokoll genau einmal

**Schlüssel = Datum, im Kontext des Store-Ordners.** Der Store-Ordner trägt den Partner bereits eindeutig (§8); die Kunden-Nr. wäre darin redundant (§3.3). Eine Kunden-Nr.-konstante Kennung würde zudem fälschlich *jedes* Protokoll desselben Stores als „bereits verarbeitet" werten — Datum ist der korrekte, tatsächlich pro-Beleg variierende Schlüssel.

1. Ziel-Ordner in Drive bestimmen — `ensure_folder_path` (§8) liefert die Zielordner-`id`.
2. In diesem Ordner per `list_files` prüfen, ob bereits `{JJJJ-MM-TT}.pdf` (§3.2) liegt.
3. **Existiert sie → kein Upload, abbrechen.** Rückfrage/Hinweis ins Topic: „Bestandsprotokoll `2026-06-16` für Spätkauf Hannover liegt bereits vor — kein Upload. Bei zwei Protokollen am selben Tag bitte manuell prüfen." Bewusst **Rückfrage statt stillem Überspringen**: Ein doppelter Eingang könnte ein versehentliches Re-Upload sein (dann harmlos) — oder eine echte zweite Zählung desselben Stores am selben Tag (dann würde ein stiller Skip sie verschlucken). Da das System beide Fälle nicht unterscheiden kann, entscheidet der Mensch.

Restrisiko (bekannt, akzeptiert): zwei *echte* Bestandsprotokolle desselben Stores am selben Kalendertag kollidieren auf denselben Dateinamen — das landet als Rückfrage beim Menschen, nicht als Datenverlust.

---

## 7. Komprimieren + Umbenennen (Schritt 4)

Im **Agent-Sandbox (Code-Execution, nicht lokal, kein VPS)**.

**Zieldateiname:** Der Ordnerpfad (§8) trägt bereits Stadt + Store — der Dateiname ist daher nur das Datum:
```
{JJJJ-MM-TT}.pdf
```
Beispiel: `2026-06-16.pdf`

**Komprimierung — höhere Qualität als bei reinen Druckbelegen:** Das Bestandsprotokoll *ist* primär die handschriftliche Zählung (IST-Bestand-Spalte) — die Archivqualität muss die Handschrift lesbar erhalten (1500 px / q80, nicht die für gedruckten Text ausreichenden 1240 px / q75):

```python
# Agent-Sandbox (Code-Execution) — Archiv aus den §2-Seiten, KEIN zweites fitz.open()/Rendern
import fitz, glob, io
from PIL import Image
ARCH_W, Q = 1500, 80                       # höher als Restock (1240/75) — Handschrift-Erhalt
out = fitz.open(); A4 = fitz.paper_rect("a4")
for p in sorted(glob.glob("/tmp/page_*.png")):       # die in §2 gerenderten OCR-Seiten
    img = Image.open(p)
    img = img.resize((ARCH_W, round(img.height * ARCH_W / img.width)))
    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=Q)
    npage = out.new_page(width=A4.width, height=A4.height)
    npage.insert_image(npage.rect, stream=buf.getvalue())
out.save("2026-06-16.pdf", deflate=True, garbage=4)
```
- **Render-Sharing:** die in §2 gerenderten `/tmp/page_*.png` werden hier nur herunterskaliert — kein zweites Öffnen/Rendern des PDFs.
- **1500 px / q80** ist der Standard hier — wenn handschriftliche Ziffern dennoch unscharf wirken, weiter hochgehen statt weiter komprimieren.
- `pymupdf` ist auch hier der einzige Pfad (Scans, eingebettete Flate-Bilder — `pikepdf` bringt 0 % Kompression).

Verifiziere nach der Komprimierung, dass die Datei > 0 Byte und valide ist, bevor du sie hochlädst.

---

## 8. Drive-Ablage (Schritt 5)

**Ordnerstruktur:**
```
<Bestandsprotokolle-Wurzel>/{city.name}/{postal_code} {store.name}/
```
- Wurzel = `registry.md §2`, Ablage-Domäne „Inventory / Bestandsprotokolle". Build-time in die Agent-Config, **nicht** hier hardcoden — `registry.md` ist die Quelle.
- Segmente 1:1 aus den `liftr_store`-Metaobjekt-Feldern (§4), **keine Slugifizierung** (Großschreibung, Leerzeichen, Umlaute `ä ö ü ß` sind in Drive zulässig und gewollt).
- `ensure_folder_path` mit `parentFolderId` = Inventory-Wurzel, `segments = [ "{city.name}", "{postal_code} {store.name}" ]`. Das Tool legt fehlende Segmente an und nutzt vorhandene wieder (mkdir-p, idempotent; serverseitig NFC-normalisiert). Rückgabe `{ id, name, created[] }`; `id` ist der Zielordner (für Ablage **und** den Idempotenz-Check §6).

**Egress:** Der Upload-Host (typisch `www.googleapis.com`, kommt im Rückgabe-Feld `uploadUrl`) muss in den Allowed-Hosts des Environments stehen. Fehlt er → Upload-Netzwerkfehler → Abbruch (§9), kein Retry.

**Upload-Ablauf (zweistufig, resumable):**
1. **Erst komprimieren (§7), dann Session holen.** Die Session ist an die bei Eröffnung deklarierte `sizeBytes` gebunden — ändert sich die Dateigröße danach, ist die Session ungültig (jeder PUT → HTTP 400). Also: erst komprimieren, Endgröße feststellen, dann Session eröffnen.
2. **Session holen** — `create_upload_session` mit `name`, `mimeType: "application/pdf"`, `sizeBytes` (exakte Byte-Zahl der finalen PDF, z. B. `os.path.getsize()`) und `parentFolderId` (Zielordner-ID aus `ensure_folder_path`). Gibt `{ uploadUrl, name, parentFolderId }` zurück.
3. **Bytes finalisierend hochladen** — die `uploadUrl` ist eine resumable Session. Ein Single-`PUT` finalisiert sie **nur** mit dem Header `Content-Range: bytes 0-(N-1)/N` (N = exakte Byte-Zahl, identisch zur deklarierten `sizeBytes`). **Ohne `Content-Range` hält Google die Session offen und antwortet HTTP 308 (Resume Incomplete) — die Datei wird NICHT committet.** Erfolg ist **ausschließlich 200 oder 201**.

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
# 308 = NICHT finalisiert (Content-Range fehlte/Teil-Upload) → wie Non-2xx: Abbruch + Fehler-Status (§9).
```

**HTTP 400** ist fast immer ein `sizeBytes`-Mismatch (Datei nach Session-Eröffnung verändert) → neue Session mit korrekter `sizeBytes`, nicht dieselbe erneut verwenden. Die 256-KB-Chunk-Grenze ist **kein** hartes Datei-Limit.

**Fail-closed:** `uploadUrl` fehlt oder PUT liefert Non-2xx (**inkl. 308 = nicht finalisiert**) → Abbruch, keine Drive-Ablage, Fehler-Status ins Topic (§9). Die lokale `/tmp`-Datei beweist die Ablage **nicht** — Bestätigung ist allein der 2xx-Status (optional härtbar via `list_files` auf den finalen Dateinamen).

Beispiel-Ablage (Ergebnis):
```
…/Bestandsprotokolle/Hannover/30159 Spätkauf Hannover/2026-06-16.pdf
```

---

## 9. Status-Rückmeldung ins Topic (Schritt 6, kompakt)

Genau **eine** knappe Status-Zeile ins Topic „Bestandsprotokolle" (`registry.md §3`, `message_thread_id: 34`):

| Ausgang | Status (Beispiel) |
|---|---|
| Erfolg | „✅ Bestandsprotokoll `2026-06-16` — Spätkauf Hannover (Hannover): in Drive abgelegt." |
| Bereits vorhanden (§6) | „⚠️ Bestandsprotokoll `2026-06-16` für Spätkauf Hannover liegt bereits vor — kein Upload. Bitte prüfen." |
| Mehrdeutig (§5) | „⚠️ <konkrete Rückfrage>. Verarbeitung pausiert." |
| Upload-Fehler (§8) | „❌ Bestandsprotokoll `2026-06-16` — Spätkauf Hannover: Upload fehlgeschlagen. Bitte erneut versuchen." |

**Adressierung:**

```
post_message(
  chat_id           = <Operations-Chat chat_id aus registry.md §3>,        # -1003918922935
  message_thread_id = <„Bestandsprotokolle" thread aus registry.md §3>,    # 34
  text              = "<Status-Zeile>",
  parse_mode        = "HTML"
)
```

Beide Werte kommen aus `registry.md §3` — **nie hier hardcoden**. Fehlt `message_thread_id`, landet die Zeile im General-Topic statt beim Bestandsprotokoll-Eingang.

**Kein City-Channel-Post in dieser Kette** — Status bleibt ausschließlich im internen Operations-Topic. Der `pos-inventory`-Agent erhält dementsprechend kein Posting-Recht auf City-Channels (Least-Privilege, `global-agent-framework`).
