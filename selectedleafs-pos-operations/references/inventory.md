# Inventory — Bestandsprotokoll ablegen

Bestandsprotokoll aus Telegram herunterladen, Partner identifizieren, komprimieren/umbenennen und in Google Drive ablegen. Geerbt von der Restock-Kette (`restock.md` §1.1 Download, §2.1/§2.5 Store-Match, §6 Drive-Ablage), aber **reduziert**: kein Sorten-/Vein-Parsing, kein Neu-vs-aufgefüllt, kein `product_list`-Write-back, **kein** öffentlicher City-Channel-Post. Inventory legt ausschließlich ab und meldet Status ins interne Topic.

## 1. Eingang & Reihenfolge

Du bekommst ein PDF aus dem Topic „Bestandsprotokolle" (`registry.md §3`, `message_thread_id: 34`) in die Sandbox (Schritt 1). Dann **in dieser Reihenfolge**:

1. **Download (§2)** — PDF referenzbasiert in die Sandbox holen, identisch zu `restock.md` §1.1.
2. **Minimal-Parsen (§3)** — nur Empfängerblock (Store) und Datum lesen, **nicht** die Artikeltabelle.
3. **Store-Match (§4)** — OCR-Name → `liftr_store`-Metaobjekt, identisch zu `restock.md` §2.5.
4. **Mehrdeutig? (§5)** → Rückfrage ins Topic, abbrechen. Sonst weiter.
5. **Idempotenz-Check (§6)** — Zielordner via `ensure_folder_path` + `list_files` auf `{datum}.pdf`; existiert sie → Rückfrage ins Topic, **kein Upload**, abbrechen.
6. **Komprimieren + umbenennen (§7)**.
7. **In Drive ablegen (§8)**.
8. **Status** ins Topic (§9).

Kein Sorten-Schritt, kein Channel-Post, kein Write-back — die Kette endet mit der Drive-Ablage.

---

## 2. PDF in die Sandbox holen (Schritt 1, Referenz-Pfad)

Identisch zu `restock.md` §1.1 — Bestandsprotokolle sind ebenfalls Scans, das Inline-base64-Budget reicht nicht. Referenz-Pfad:

1. **Referenz holen** — `create_download_url` mit der `file_id` des PDF-Anhangs (aus `document.file_id` des eingehenden Updates, **nicht** die `message_id`). Liefert `{ url, key, file_name, mime_type, size, expires_in }`, `url` ist eine token-freie, kurzlebige presigned GET-URL.
2. **Bytes direkt ziehen** — `url` per `curl -o` in die Sandbox; die Bytes laufen **nicht** durch den Agenten-Kontext. Zügig nach dem Call ausführen — die URL läuft nach `expires_in` Sekunden ab.

Seiten danach **einmal** rendern (pymupdf, Graustufe, `OCR_W` breit) für die OCR — wie `restock.md` §1.1, Schritte 2–3. Diese gerenderten `/tmp/page_*.png` sind die Basis für §7 (Komprimierung) — kein zweites Rendern dort.

---

## 3. Minimal-Parsen — nur Empfängerblock + Datum

**Bewusster Unterschied zu Restock:** Die Artikeltabelle (Pos./Artikelnummer/SOLL-Bestand/IST-Bestand) wird **nicht** ausgewertet — sie ist der eigentliche Beleginhalt fürs Archiv, nicht Input für eine Entscheidung. OCR/Lesefokus beschränkt sich auf zwei Felder:

### 3.1 Store = Empfänger/Kommissionär — nie der Absender

Identisches Layout zu Restock (`restock.md` §2.1): Auf dem Beleg stehen zwei Adressen — Absender = selectedleafs.com (ignorieren), Empfänger = der Partner-Store. Verifiziere über die Unterschriftszeile: Store bei „… als Kommissionär", selectedleafs bei „… als Kommittent". Bei Konflikt zwischen Empfängerblock und Kommissionär-Zeile → Kommissionär-Zeile gewinnt, sonst (uneindeutig) §5.

### 3.2 Datum

Oben auf Seite 1 im Format `TT.MM.JJJJ` (z. B. `16.06.2026`) → normalisiere zu `JJJJ-MM-TT` (`2026-06-16`). Das ist das **Protokolldatum**, nicht das Verarbeitungsdatum. Fehlt/uneindeutig → §5.

### 3.3 Kunden-Nr. — nicht verwendet

Bestandsprotokolle tragen eine „Kunden-Nr." (z. B. `10034`) im Kopf. Diese ist **partner-konstant**, nicht protokoll-eindeutig, und liegt **nicht** im `liftr_store`-Metaobjekt. Sie wird hier **weder für den Match noch für den Dateinamen** verwendet (§4/§7) — eine Lesepflicht weniger, eine Fehlerquelle weniger.

---

## 4. Store → Metaobjekt-Match → Stadt (identisch zu Restock)

Vollständig identisch zu `restock.md` §2.5 1a/1b/2/3 — hier nicht dupliziert, dort nachlesen:

- **1a Match-Stufe** (nur `id`+`name`, paginiert über alle Seiten, OCR-toleranter Fuzzy-Match auf den Store-Namen aus §3.1).
- **1b Detail-Stufe** (nur der Treffer): `name`, `postal_code`, `city`→`name`. **Nicht** benötigt aus der Restock-Detail-Stufe: `district`, `product_list`, `google_place` — Inventory postet nicht öffentlich, braucht also weder Maps-Link noch Sortiments-Liste. Schlankerer Query als Restock:
  ```graphql
  query($id: ID!) {
    metaobject(id: $id) {
      name:        field(key: "name")        { value }
      postal_code: field(key: "postal_code") { value }
      city:        field(key: "city") { reference { ... on Metaobject { name: field(key: "name") { value } } } }
    }
  }
  ```
- **Stadt kommt aus dem Metaobjekt**, nicht aus der Belegadresse (Wunstorf-Regel, `restock.md` §2.5 Punkt 2/3).

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
3. **Existiert sie → kein Upload, abbrechen.** Rückfrage/Hinweis ins Topic: „Bestandsprotokoll `2026-06-16` für Spätkauf Hannover liegt bereits vor — kein Upload. Bei zwei Protokollen am selben Tag bitte manuell prüfen." (Bewusst **Rückfrage statt stillem Überspringen** — anders als Restocks §4, wo ein doppelt eingereichtes Protokoll denselben Inhalt hätte. Hier könnte eine echte zweite Zählung am selben Tag vorliegen; ein stiller Skip würde sie verschlucken.)

Restrisiko (bekannt, akzeptiert): zwei *echte* Bestandsprotokolle desselben Stores am selben Kalendertag kollidieren auf denselben Dateinamen — das landet als Rückfrage beim Menschen, nicht als Datenverlust.

---

## 7. Komprimieren + Umbenennen (Schritt 4)

Im **Agent-Sandbox (Code-Execution, nicht lokal, kein VPS)**.

**Zieldateiname:** Der Ordnerpfad (§8) trägt bereits Stadt + Store — der Dateiname ist daher nur das Datum:
```
{JJJJ-MM-TT}.pdf
```
Beispiel: `2026-06-16.pdf`

**Komprimierung — abweichend von Restocks 1240 px/q75 (vgl. Stresstest-Befund):** Das Bestandsprotokoll *ist* primär die handschriftliche Zählung (IST-Bestand-Spalte) — anders als bei Restock, wo Mengen für den Post irrelevant sind. Die Archivqualität muss die Handschrift lesbar erhalten:

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
- **Render-Sharing:** wie Restock §5 — die §2-Seiten werden hier nur herunterskaliert, kein zweites Öffnen/Rendern des PDFs.
- **1500 px / q80** ist der Standard hier (nicht der Fallback wie bei Restock) — wenn handschriftliche Ziffern dennoch unscharf wirken, weiter hochgehen statt weiter komprimieren.
- `pymupdf` ist auch hier der einzige Pfad (Scans, eingebettete Flate-Bilder — `pikepdf` bringt 0 % Kompression).

Verifiziere nach der Komprimierung, dass die Datei > 0 Byte und valide ist, bevor du sie hochlädst.

---

## 8. Drive-Ablage (Schritt 5)

Identisch zu `restock.md` §6 — Upload-Mechanik (resumable Session, `Content-Range`-Header, Erfolg ausschließlich 200/201, 308 = nicht finalisiert) **1:1 übernommen**, hier nur die domänen-eigenen Werte:

**Ordnerstruktur:**
```
<Bestandsprotokolle-Wurzel>/{city.name}/{postal_code} {store.name}/
```
- Wurzel = `registry.md §2`, Inventory-Zeile: `parentFolderId` `1YbYciT2C2NuqsZrX6ghZnOxxHag9hXwW`.
- Segmente 1:1 aus den `liftr_store`-Metaobjekt-Feldern (§4), keine Slugifizierung — wie Restock §6.
- `ensure_folder_path` mit `parentFolderId` = Inventory-Wurzel, `segments = [ "{city.name}", "{postal_code} {store.name}" ]`.

**Upload-Ablauf:** identisch zu `restock.md` §6 Schritte 1–3 (erst komprimieren → Endgröße feststellen → `create_upload_session` → finalisierender Single-PUT mit `Content-Range`). Dort nachlesen, hier nicht dupliziert.

**Fail-closed:** wie Restock — `uploadUrl` fehlt oder PUT liefert Non-2xx (inkl. 308) → Abbruch, keine Drive-Ablage, Fehler-Status ins Topic (§9). Kein stiller Weiter-Lauf ohne abgelegte PDF.

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
