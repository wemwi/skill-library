---
name: selectedleafs-pos-restock
description: "Runtime-Anleitung an den Managed Agent pos-restock zum Auswerten EINES selectedleafs-Übergabeprotokolls (Kommissionsware-Beleg, PDF) und Ablegen in Google Drive. Liefert die operative Tiefe für Protokoll-Parsing (Store, Stadt, Sorten, neu vs. aufgefüllt), Idempotenz, PDF-Komprimierung/Umbenennung und Drive-Ablage. IMMER laden, sobald der Agent ein Übergabeprotokoll aus dem Topic Protokoll-Eingang verarbeitet — auch wenn das Wort Skill nicht fällt. Triggers on: Übergabeprotokoll, Protokoll-Eingang, pos-restock, Kommissionsware, Kommissionär, Lieferschein parsen, Restock-Beleg auswerten, Store aus Beleg ableiten, Sorten neu vs aufgefüllt, Protokoll in Drive ablegen, Protokollnummer, UL-Nummer. Nachrichtenformat und City→Channel liegen NICHT hier (→ selectedleafs-telegram)."
---

# selectedleafs POS-Restock — Übergabeprotokoll auswerten & ablegen

Operative Anleitung **an dich, den Agenten `pos-restock`**, für den Kern deiner Kette: ein Übergabeprotokoll auswerten (Schritt 2), das PDF komprimieren/umbenennen (Schritt 4) und in Google Drive ablegen (Schritt 5). Du verarbeitest **genau ein Protokoll pro Lauf**.

**Scope:** Schritt 2, 4, 5 deiner Kette. Schritt 1 (PDF laden), 3 (Posten), 6 (Status) führst du laut System-Prompt aus — dieser Skill ergänzt die Tiefe, dupliziert den System-Prompt nicht.

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

Protokolle sind **immer unterschriebene Scans** (Foto/Schräglage, Knickkanten, kein Text-Layer). Darum ist **OCR der Pflichtpfad, kein Fallback** — kein vorheriger Textextraktions-Versuch: leichte Vorverarbeitung (Graustufen, bei Bedarf Deskew/Kontrast), dann `tesseract -l deu`. `tesseract` inkl. deutschem Sprachpaket ist in der Env **vorinstalliert — nicht prüfen, nicht installieren**. Liefert OCR an einer entscheidungsrelevanten Stelle nur unsicheren Text (Store, Protokollnummer, Sorte), behandle das als Mehrdeutigkeit (§3) — **rate nichts**. Strain-Lesungen werden zusätzlich gegen den 9-Strain-Index gefuzzt (§2.4), damit OCR-Rauschen nicht jede Sorte zur Rückfrage macht.

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

1. Ziel-Ordner in Drive bestimmen (§6).
2. Prüfen, ob dort bereits eine Datei mit Endung `_<protokoll_nr>.pdf` liegt.
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

**Komprimierung — Protokolle sind Scans (bildlastig), darum Ghostscript-Downsampling:**

```bash
# Agent-Sandbox (Code-Execution)
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile="2026-06-17_UL-10033-1.pdf" \
   "<eingangs-pdf>"
```
- `/ebook` (~150 dpi) ist der Default — Beleg bleibt gut lesbar, Größe deutlich kleiner. Nur wenn das Ergebnis unlesbar würde, auf `/printer` (~300 dpi) hochgehen; `/screen` (~72 dpi) nur bei reinen Textbelegen.
- Da Protokolle **immer Scans** sind (unterschrieben, kein Text-Layer), ist Ghostscript der **einzige** Pfad — keinen digitalen pikepdf-Sonderfall versuchen.

Verifiziere nach der Komprimierung, dass die Datei > 0 Byte und valide ist, bevor du sie hochlädst.

---

## 6. Drive-Ablage (Schritt 5)

Über das Google-Drive-Tool. **Ordnerstruktur (B3):**
```
<Übergabeprotokolle-Wurzel>/{stadt}/{store-slug}/
```
- `{stadt}` = aufgelöste Metaobjekt-Stadt (§2.5), `{store-slug}` = aus dem gematchten Metaobjekt-Namen, **nicht** aus dem rohen Belegtext (stabil). Beide slugifiziert: lowercase, Umlaute falten (`ä→ae ö→oe ü→ue ß→ss`), Nicht-Alphanumerik → `-`, Mehrfach-`-` zusammenfassen. So bleiben Ablage und Channel deckungsgleich.
- Fehlt der Stadt- oder Store-Ordner, **anlegen** (mkdir-p-Semantik), dann die umbenannte PDF hineinlegen.
- Die **Wurzel/Folder-ID** ist Agent-Config (build-time, `global-agent-framework`) — nicht hier hardcoden.

Beispiel-Ablage:
```
…/Übergabeprotokolle/Hannover/spaetkauf-hannover/2026-06-17_UL-10033-1.pdf
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
| 2026-06-25 | Rename `selectedleafs-pos-documentation` → `selectedleafs-pos-restock` (topic-scoped, näher am Restock-Zweck). Inhaltlich unverändert ggü. v1.1.0. Frontmatter-Name + H1 angepasst, keine sonstigen Selbstreferenzen. Achtung: erzeugt ein neues Skill — alte Installation manuell entfernen, Agent neu attachen. Cross-Verweise in anderen Skills (`selectedleafs-telegram`, `global-agent-framework`) ggf. nachziehen. |
| 2026-06-25 | v1.1.0 — Write-back ergänzt (neue §8): nach erfolgreichem 🌿-Post wird die neue Sorte an `product_list` des Stores angehängt (append-only, idempotent, Remove bleibt manuell); §1-Reihenfolge um den Write-back-Schritt erweitert, §7-Status quittiert ihn. OCR von Fallback auf **Pflichtpfad** umgestellt (Protokolle sind immer unterschriebene Scans → `tesseract -l deu` + leichte Vorverarbeitung, vorinstalliert, nicht prüfen/installieren); Textextraktions-Vorstufe und pikepdf-Digital-Zweig (§5) entfernt. Strain-Auflösung von exaktem Index-Vergleich auf **OCR-toleranten Fuzzy-Match** gegen den 9-Strain-Index umgestellt (§2.4), nur unauflösbar/mehrdeutig → §3. `liftr_store`-Match paginiert jetzt über 50 Stores hinaus (Cursor, §2.5). |
| 2026-06-24 | v1.0.0 — Initial. Parsing (Store=Kommissionär, Protokollnr `UL-…`, Sorte nur mit Tier·Vein-Subzeile, Größen-Dedupe), Stadt aus Metaobjekt (Wunstorf-Regel), neu vs. aufgefüllt via `product_list`, Übergabe-Payload (Buckets). Vollautomatisch, Abbruch+Rückfrage bei Mehrdeutigkeit. Idempotenz via Protokollnr im Dateinamen (Drive-Existenz-Check). Naming = Datum + Protokollnr (Stadt/Store stecken im B3-Pfad, nicht doppelt im Namen), Drive B3 ({stadt}/{store-slug}). Komprimierung Ghostscript `/ebook` (Scan) bzw. pikepdf (digital). Format/Channel → `selectedleafs-telegram`. |
