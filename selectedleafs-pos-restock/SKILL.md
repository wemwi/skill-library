---
name: selectedleafs-pos-restock
metadata:
  version: "1.5.0"
description: "Runtime-Anleitung an den Managed Agent pos-restock zum Auswerten EINES selectedleafs-Übergabeprotokolls (Kommissionsware-Beleg, PDF) und Ablegen in Google Drive. Liefert die operative Tiefe für Protokoll-Parsing (Store, Stadt, Sorten, neu vs. aufgefüllt), Idempotenz, PDF-Komprimierung/Umbenennung und Drive-Ablage. IMMER laden, sobald der Agent ein Übergabeprotokoll aus dem Topic Protokoll-Eingang verarbeitet — auch wenn das Wort Skill nicht fällt. Triggers on: Übergabeprotokoll, Protokoll-Eingang, pos-restock, Kommissionsware, Kommissionär, Lieferschein parsen, Restock-Beleg auswerten, Store aus Beleg ableiten, Sorten neu vs aufgefüllt, Protokoll in Drive ablegen, Protokollnummer, UL-Nummer. Nachrichtenformat und City→Channel liegen NICHT hier (→ selectedleafs-telegram)."
---

# selectedleafs POS-Restock — Übergabeprotokoll auswerten & ablegen

Operative Anleitung **an dich, den Agenten `pos-restock`**, für den Kern deiner Kette: das Protokoll-PDF in die Sandbox holen (Schritt 1), ein Übergabeprotokoll auswerten (Schritt 2), das PDF komprimieren/umbenennen (Schritt 4) und in Google Drive ablegen (Schritt 5). Du verarbeitest **genau ein Protokoll pro Lauf**.

**Scope:** Schritt 1, 2, 4, 5 deiner Kette. Schritt 3 (Posten) und 6 (Status) führst du laut System-Prompt aus. Auch für Schritt 1 gilt das Muster von §5/§6: der **System-Prompt triggert** (es liegt ein PDF im Topic „Protokoll-Eingang" bereit), dieser Skill liefert nur die **Tiefe des Tool-Calls** (§1.1) — er dupliziert den System-Prompt nicht und entscheidet nicht über den Auslöser.

**Abgrenzung — was NICHT hier steht:**
- **Restock-Nachrichtenformat + City→Channel-Zuordnung** → `selectedleafs-telegram` (§5 Templates, §10 Auslöser). Du lieferst nur Stadt + Sorten-Buckets; das Rendern und der Channel laufen dort.
- **Managed-Agents-/Console-Mechanik** (Config, Tools, Deploy) → `global-agent-framework` (build-time).
- **Store-Daten** → Shopify MCP: `listMetaobjects(type: "liftr_store")`.

**Verhältnis zu telegram §10:** Dort ist die Protokoll-Verarbeitung *halb-manuell mit Review* beschrieben. **Du läufst vollautomatisch** und postest ohne Vorab-Bestätigung — der Mensch-im-Loop ist hier durch den harten Abbruch bei Unklarheit (§3) ersetzt. Bei Mehrdeutigkeit postest du nie öffentlich, sondern stellst eine Rückfrage im Topic „Protokoll-Eingang" und brichst ab.

---

## 1. Eingang & Reihenfolge

Du bekommst ein PDF aus dem Topic „Protokoll-Eingang" in die Sandbox (Schritt 1). Dann **in dieser Reihenfolge**:

1. **Idempotenz-Check zuerst (§4)** — schon verarbeitet? → abbrechen, bevor du irgendetwas postest oder ablegst.
2. **Parsen (§2)** — Store, Stadt, Sorten, neu vs. aufgefüllt.
3. **Mehrdeutig? (§3)** → Rückfrage im Topic, abbrechen. Sonst weiter.
4. **Posten** — Stadt + Sorten-Buckets an den Telegram-Schritt übergeben (Format/Channel → `selectedleafs-telegram`).
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
# Agent-Sandbox: tessdata-Ordner robust bestimmen
import tessdata, os, sys
def tessdata_dir():
    for c in (tessdata.data_path(), os.path.join(sys.prefix, "share", "tessdata"),
              "/usr/local/share/tessdata", "/usr/share/tessdata"):
        if os.path.exists(os.path.join(c, "deu.traineddata")):
            return c
    raise RuntimeError("deu.traineddata nicht gefunden")
# pytesseract.image_to_string(img, lang="deu", config=f'--tessdata-dir "{tessdata_dir()}"')
```

Liefert OCR an einer entscheidungsrelevanten Stelle nur unsicheren Text (Store, Protokollnummer, Sorte), behandle das als Mehrdeutigkeit (§3) — **rate nichts**. Strain-Lesungen werden zusätzlich gegen den 9-Strain-Index gefuzzt (§2.4), damit OCR-Rauschen nicht jede Sorte zur Rückfrage macht.

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

`Menge`, `Gewicht`, `MHD` sind für den Post **irrelevant** (Verfügbarkeit ist binär — telegram §6). Nur Strain + Vein zählen.

### 2.4 Strain + Vein extrahieren, Größen dedupen

Je verkaufbarer Position:
- **Strain** = fette Produktzeile **ohne Größen-Suffix** (`25g`/`50g`/`100g` …). „Indo Fusion 25g" → „Indo Fusion".
- **Vein** = das Wort vor „Kratom" in der Subzeile. „€ · White Kratom" → White.
- **Dedupe über Größen:** dieselbe Strain+Vein-Kombination aus mehreren Positionen (z. B. „Indo Fusion 25g" + „Indo Fusion 50g") kollabiert zu **einer** Sorte „Indo Fusion (White)".

**Fuzzy-Match gegen den kanonischen 9-Strain-Index (telegram §5):** Den OCR-Strain **nicht wörtlich übernehmen**, sondern auf den nächstgelegenen Index-Eintrag mappen (OCR-tolerant, z. B. „lndo Fuslon" → „Indo Fusion", „Borneo Blizz" → „Borneo Bliss"). Liegt der beste Treffer klar über der Ähnlichkeitsschwelle → **diesen kanonischen Namen verwenden** (nicht den rohen OCR-Text). Bleibt der beste Treffer mehrdeutig (zwei Index-Einträge ähnlich nah) oder unter der Schwelle (kein plausibler Match → mutmaßlich echte Katalog-Neuheit oder unlesbar) → **nicht öffentlich raten**, sondern §3 (Rückfrage). Der Index selbst (Sortierung/Tier) lebt in telegram — hier nur Auflösung + Plausibilisierung.

### 2.5 Store → Metaobjekt-Match → Stadt & Channel (Wunstorf-Regel)

1. Store-Name (§2.1) gegen `listMetaobjects(type: "liftr_store")` matchen (Name-Match, kein gespeichertes Mapping). **Über die Standard-Seitengröße (50) hinaus paginieren** (Cursor / `pageInfo.hasNextPage`, Seite für Seite, bis ein eindeutiger Match steht oder alle Seiten durch sind) — sonst sind Stores ab dem 51. unauffindbar und würden fälschlich als „kein Match" (§3) behandelt.
2. **Stadt/Channel kommt aus dem Metaobjekt, nicht aus der Belegadresse.** Ein Store kann physisch z. B. in Wunstorf liegen, aber redaktionell der Hannover-Page/dem Hannover-Channel zugeordnet sein — dann ist die maßgebliche Stadt **Hannover**. Lies die zugewiesene Stadt aus dem Store-Metaobjekt (Stadt-/`district`-Zuordnung), **nicht** die Postanschrift.
3. Die Belegstadt dient nur als **Plausi-Check**: weicht sie stark von der Metaobjekt-Stadt ab, ist das ein Signal, aber das Metaobjekt gewinnt. Nur wenn **kein eindeutiger Store-Match** existiert oder dem Store **keine Stadt** zugeordnet ist → §3.

Dieselbe aufgelöste Stadt benutzt du in §6 für den Drive-Pfad — so bleiben Channel und Ablage konsistent.

### 2.6 Neu vs. aufgefüllt (pro Sorte, via `product_list`)

Pro deduplizierter Sorte gegen die `product_list` des **gematchten Stores** prüfen:
- Strain **in** `product_list` → **aufgefüllt** (📦 Restock).
- Strain **nicht in** `product_list` → **neue Sorte** (🌿).

Die Entscheidung ist **pro Sorte**: ein Protokoll kann gleichzeitig aufgefüllte und neue Sorten enthalten → zwei Buckets.

### 2.7 Was dieser Skill liefert (Übergabe-Payload)

Du übergibst an den Telegram-Schritt (Format/Channel → `selectedleafs-telegram` §5/§10) **strukturierte Daten, keinen fertigen Text**:

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

**Komprimierung — Protokolle sind Scans (bildlastig), Downsampling via `pymupdf` (reines pip-Wheel, kein apt/Ghostscript):**

```python
# Agent-Sandbox (Code-Execution)
import fitz  # pymupdf
TARGET_W, Q = 1240, 75                 # ~150 dpi A4, Graustufe; Fallback 1500/q80
doc = fitz.open("<eingangs-pdf>"); out = fitz.open()
A4 = fitz.paper_rect("a4")
for page in doc:
    zoom = TARGET_W / page.rect.width  # MediaBox liegt in Scan-pt vor → feste Zielbreite, NICHT dpi=
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    npage = out.new_page(width=A4.width, height=A4.height)
    npage.insert_image(npage.rect, stream=pix.tobytes("jpeg", jpg_quality=Q))
out.save("2026-06-17_UL-10033-1.pdf", deflate=True, garbage=4)
```
- **Feste Zielbreite, nicht `dpi=`:** Die Scan-Seite hat eine MediaBox in Scan-Punkten (das Bild sitzt als 72-dpi-Vollseite drin), darum skaliert `get_pixmap(dpi=…)` ins Leere. Über `zoom = TARGET_W / page.rect.width` triffst du verlässlich die Zielbreite.
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

1. **Session holen** — `create_upload_session` mit `name`, `mimeType: "application/pdf"`, `sizeBytes` (optional, aus Datei-Metadaten) und `parentFolderId` (Zielordner-ID). Gibt `{ uploadUrl, name, parentFolderId }` zurück.
2. **Bytes direkt hochladen** — HTTP `PUT` aus der Sandbox an die `uploadUrl`, Datei-Bytes als Body. Die Session-URL trägt ihre eigene Autorisierung; kein zusätzliches Google-Credential nötig.

```bash
# Agent-Sandbox (Code-Execution)
curl -s -o /dev/null -w "%{http_code}" \
  -X PUT \
  --data-binary @"<komprimierte-pdf>" \
  "<uploadUrl>"
# Erwarteter HTTP-Status: 200 oder 201 → Erfolg
# Jeder andere Status → Abbruch + Fehler-Status ins Topic (§7)
```

**Fail-closed:** Gibt `create_upload_session` keinen `uploadUrl` zurück (Fehler, Netzwerkproblem), oder liefert der PUT einen Non-2xx-Status → Abbruch, keine Drive-Ablage, Fehler-Status ins Topic. Kein stiller Weiter-Lauf ohne abgelegte PDF.

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

Keine Sorten-/Mengen-Details öffentlich in den City-Channel schreiben, die nicht aus dem Telegram-Format (§5) stammen — der Status bleibt im Topic.

Wurden **neue Sorten** gepostet, den Write-back (§8) in derselben Zeile kurz quittieren, z. B.: „✅ `UL-10040-1` — Kiosk Linden (Hannover): 0 aufgefüllt, 1 neu (Sortiment ergänzt). Gepostet + in Drive abgelegt."

---

## 8. Write-back: neue Sorten in `product_list` (nach dem Post)

Läuft als **Schritt 5 in §1, direkt nach dem erfolgreichen 🌿-Post** (Schritt 4) und betrifft **nur den `neue_sorten`-Bucket**. Zweck: Eine erstmals gelieferte Sorte wird ins Sortiment des Stores aufgenommen, damit dieselbe Sorte beim **nächsten** Protokoll korrekt als 📦 (aufgefüllt) statt erneut als 🌿 erkannt wird (§2.6). Ohne Write-back bliebe jede neue Sorte dauerhaft „neu".

**Regeln:**
- **Nur anhängen, nie entfernen.** Du fügst jede tatsächlich gepostete neue Sorte zur `product_list` des gematchten Store-Metaobjekts hinzu. Das Auslisten ausverkaufter Sorten macht der Mensch **manuell** — der Agent löscht nie aus `product_list`.
- **Idempotent, kein Clobbern.** Vor dem Anhängen prüfen, ob die Sorte schon enthalten ist (sollte sie nicht, sonst wäre sie 📦 gewesen); bestehende Einträge nie überschreiben, nur ergänzen.
- **Repräsentation deckungsgleich mit der Leseseite (§2.6).** In genau der Form anhängen, in der `product_list` Sorten führt, damit Lese- (§2.6) und Schreibseite konsistent bleiben — sonst zählt dieselbe Sorte beim nächsten Lauf wieder als neu.
- **Nur bei erfolgreichem Post.** Schlägt der 🌿-Post fehl, **kein** Write-back — sonst meldete `product_list` eine Sorte als geführt, die nie announced wurde.
- **Tool / Permission ist build-time.** Der Write-back ist eine **Mutation** aufs Metaobjekt; das read-only `graphql_query` reicht dafür nicht. Tool-Oberfläche, Least-Privilege und Bestätigungs-Policy regelt `global-agent-framework` — dieser Skill beschreibt nur das **Verhalten**, nicht die Tool-Mechanik.

**Bewusste Folge fürs Typing:** Nimmt der Mensch eine ausverkaufte Sorte später aus `product_list` und sie wird erneut geliefert, postet der Agent sie wieder als 🌿 „Neue Sorte" (nicht 📦). Das ist laut telegram-SSOT korrekt (Trigger = Membership in `product_list`) und braucht **keinen** „kennen-wir-schon"-Sonderfall. Wer das Framing später glätten will, müsste eine separate Historie führen — bewusst nicht Teil dieser Kette.

---

## Changelog

| Datum | Änderung |
|-------|----------|
| 2026-06-29 | v1.5.0 — Auf die neuen MCP-Tools umgestellt. **§1.1 (neu) Download auf Referenz-Pfad:** Inline-base64 `download_file` → `create_download_url` (lädt serverseitig von Telegram nach R2, Bot-Token bleibt am Worker, gibt eine token-freie presigned GET-URL zurück; per `curl -o` in die Sandbox, läuft nicht durch den Agenten-Kontext). Egress-Voraussetzung ergänzt (`<account-id>.r2.cloudflarestorage.com` in Allowed-Hosts, build-time). Fail-closed bei fehlender `url`/Non-2xx, kein base64-Fallback. Scope zieht Schritt 1 in die „Tiefe" (System-Prompt triggert, Skill liefert den Tool-Call) — Spiegel zur Upload-Seite §6. **§6 Drive-Ablage:** manuelle `list_files`+`create_folder`-Ordnerschleife durch **einen** `ensure_folder_path`-Call ersetzt (mkdir-p für `{city.name}`/`{postal_code} {store.name}`); NFC-Normalisierung + Dedup laufen jetzt serverseitig im Tool → der manuelle NFC-Wiederfind-Hinweis entfällt, Rückgabe-`id` ist der Zielordner. **§4:** Ordner-Bestimmung zeigt auf `ensure_folder_path`; der `list_files`-Existenz-Check fürs `_<protokoll_nr>.pdf` (Idempotenz) bleibt. Tool-Kontrakte aus telegram-mcp 4.2.1 + google-drive-mcp `main` übernommen (nicht geraten). |
| 2026-06-27 | v1.4.0 — Kompression von Ghostscript auf **`pymupdf`** (reines pip-Wheel) umgestellt (§5): in der Managed-Agents-Beta wird die deklarierte **apt**-Paketzeile nicht provisioniert (pip greift, apt nicht — in zwei Envs reproduziert), darum gs/apt komplett raus. `pymupdf` rendert PDF→Bild selbst (kein poppler/`pdf2image`); feste Zielbreite **1240 px / Graustufe / JPEG q75** statt `dpi=` (MediaBox liegt in Scan-pt vor → `dpi=` skaliert ins Leere), ~5,3 MB → ~0,3 MB, OCR am realen Beleg verifiziert (Kerndaten + Umlaute); Fallback 1500/q80. `pikepdf` verworfen (rührt Flate-Scan-Bilder nicht an, 0 %). §1: deutsches Sprachpaket nicht mehr „apt-vorinstalliert", sondern pip-Paket **`tessdata.fast-deu`**; tessdata-Pfad über Fallback-Finder + `--tessdata-dir`, weil `tessdata.data_path()` (=`sys.prefix/share/tessdata`) im Container neben dem echten Ort (`/usr/local/share/tessdata`) liegen kann. tesseract-Engine bleibt Base-Image. |
| 2026-06-27 | v1.3.0 — §6 Drive-Ordnernamen von slugifiziert auf Klartext aus Metaobjekt-Feldern umgestellt: `{stadt}/{store-slug}` → `{city.name}/{postal_code} {store.name}` (z. B. `Hannover/30159 Spätkauf Hannover`). Slugifizierung (lowercase, Umlaut-Faltung, `-`-Ersetzung) entfällt — Großschreibung, Leerzeichen und Umlaute sind in Drive zulässig; einzige Anforderung bleibt Determinismus aus stabiler Quelle (Metaobjekt-`name`/`postal_code`, nie OCR/Belegtext). NFC-Normalisierung beim Ordner-Wiederfinden ergänzt; expliziter Hinweis, dass `create_folder` nicht dedupliziert (vorher `list_files`). Idempotenz (§4, Schlüssel = Protokollnummer) und Dateiname (§5) unberührt. |
| 2026-06-26 | v1.2.0 — §6 Drive-Ablage auf Referenz-Upload umgestellt: statt Inline-base64 (`upload_file`) jetzt zweistufig via `create_upload_session` (Session-URL holen) + `curl PUT` (Bytes direkt aus Sandbox zu Google, läuft nicht durch Agenten-Kontext). Egress-Voraussetzung ergänzt (Upload-Host muss in Allowed-Hosts des Environments, einmalig via Test-Session ablesen). Fail-closed bei Non-2xx oder fehlendem `uploadUrl`. Hintergrund: ~916 KB PDF ergibt ~1,2M Zeichen base64 — sprengt das Argument-Budget des Agenten; war Root Cause des Kettenabbruchs. |
| 2026-06-25 | Rename `selectedleafs-pos-documentation` → `selectedleafs-pos-restock` (topic-scoped, näher am Restock-Zweck). Inhaltlich unverändert ggü. v1.1.0. Frontmatter-Name + H1 angepasst, keine sonstigen Selbstreferenzen. Achtung: erzeugt ein neues Skill — alte Installation manuell entfernen, Agent neu attachen. Cross-Verweise in anderen Skills (`selectedleafs-telegram`, `global-agent-framework`) ggf. nachziehen. |
| 2026-06-25 | v1.1.0 — Write-back ergänzt (neue §8): nach erfolgreichem 🌿-Post wird die neue Sorte an `product_list` des Stores angehängt (append-only, idempotent, Remove bleibt manuell); §1-Reihenfolge um den Write-back-Schritt erweitert, §7-Status quittiert ihn. OCR von Fallback auf **Pflichtpfad** umgestellt (Protokolle sind immer unterschriebene Scans → `tesseract -l deu` + leichte Vorverarbeitung, vorinstalliert, nicht prüfen/installieren); Textextraktions-Vorstufe und pikepdf-Digital-Zweig (§5) entfernt. Strain-Auflösung von exaktem Index-Vergleich auf **OCR-toleranten Fuzzy-Match** gegen den 9-Strain-Index umgestellt (§2.4), nur unauflösbar/mehrdeutig → §3. `liftr_store`-Match paginiert jetzt über 50 Stores hinaus (Cursor, §2.5). |
| 2026-06-24 | v1.0.0 — Initial. Parsing (Store=Kommissionär, Protokollnr `UL-…`, Sorte nur mit Tier·Vein-Subzeile, Größen-Dedupe), Stadt aus Metaobjekt (Wunstorf-Regel), neu vs. aufgefüllt via `product_list`, Übergabe-Payload (Buckets). Vollautomatisch, Abbruch+Rückfrage bei Mehrdeutigkeit. Idempotenz via Protokollnr im Dateinamen (Drive-Existenz-Check). Naming = Datum + Protokollnr (Stadt/Store stecken im B3-Pfad, nicht doppelt im Namen), Drive B3 ({stadt}/{store-slug}). Komprimierung Ghostscript `/ebook` (Scan) bzw. pikepdf (digital). Format/Channel → `selectedleafs-telegram`. |
