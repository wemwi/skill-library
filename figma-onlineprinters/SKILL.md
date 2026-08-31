---
name: figma-onlineprinters
description: >
  Workflow zum Übertragen, Skalieren und Dokumentieren von Onlineprinters-Druckvorlagen
  (Dielines) in Figma für selectedleafs. Nutze diesen Skill IMMER, wenn eine neue
  Onlineprinters-Druckvorlage in Figma soll, ein Dieline/Stanzkontur bereinigt werden muss
  (Beschnitt, Safe Zone, Schnittlinie, Falz, Klebelaschen behalten — Bemaßung, Maßtext und
  Bild/Badge entfernen), eine Print-Template-Component mit Slots erstellt wird, oder eine
  Component Description für ein Druckprodukt geschrieben wird. Triggert bei: Onlineprinters,
  Druckvorlage, Dieline, Stanzkontur, Druckdaten, Beschnitt/Bleed, Safe Zone, Thekenaufsteller,
  Produktdisplay, Falzflyer, Broschüre, Plakat, PDF in Figma, print template, Druck-Component.
  Gilt nur für den Onlineprinters-Print-Workflow; allgemeine Figma-Token-/Struktur-Regeln
  stehen in figma-standards.md.
---

# figma-onlineprinters

Der **Ingestion- und How-to-Workflow** für Onlineprinters-Druckvorlagen in Figma.
Verhält sich zu `figma-standards.md` wie `liftr-section` zu `liftr-css-system`:
`figma-standards.md` hält die Prinzipien (Token-Disziplin, Modes, File-Struktur, Naming),
dieser Skill hält den konkreten Prozess. Bei Konflikt gewinnt `figma-standards.md`.

**Print-File:** `IPEk40v01EMVITXst3UPOT` · **Sammelframe „Onlineprinters":** `272:41227`
(gruppiert nach Format: DIN Lang, DIN A4, DIN A2, Produktdisplays).

---

## Pipeline-Überblick & Arbeitsteilung

```
[1] PDF holen      →  manuell: von der Produktseite herunterladen
[2] PDF → SVG      →  automatisierbar (pdftocairo)
[3] Bereinigen     →  automatisierbar (Diagnose + clean_dieline.py)
[4] Specs ziehen   →  automatisierbar aus PDF-Text (+ Kopf-Werte aus Paste)
─────────────────────────────────────────────────────────────────
[5] SVG in Figma   →  MANUELL: bereinigtes SVG per Drag reinziehen
─────────────────────────────────────────────────────────────────
[6] Component bauen →  automatisierbar via use_figma (Slots, Overlay, Props, Description)
```

Die Grenze bei [5] ist bewusst: Das bereinigte Dieline-SVG (~30 KB Vektor) lässt sich nicht
verlustfrei in den `use_figma`-Code transportieren (siehe §6 „SVG-Import"). Davor und danach
ist alles skriptbar.

---

## 1. PDF holen

- Produktseite öffnen, z. B. `…/p/produktdisplays-fuer-eine-theke-breit`, Reiter **Druckvorlagen** → PDF laden.
- Die HTML-Produktseite ist **bot-geschützt** (`web_fetch` wird geblockt). Die Druckvorlagen-**PDF**
  liegt aber auf einem offenen Media-Pfad (`…/shopdata/media/pim/printTemplates/<hash>.pdf`) und ist
  per `web_fetch` erreichbar — daraus lassen sich Maße (Text) ziehen, aber **nicht** die Vektor-Bytes
  (kommen als opaker Binär-Platzhalter zurück, und bash erreicht onlineprinters.de nicht).
- **Für die Konvertierung muss die PDF auf der Platte liegen** → die Person lädt sie in den Chat hoch
  (landet in `/mnt/user-data/uploads/`).

## 2. PDF → SVG

`pdftocairo -svg` ersetzt den Inkscape-Umweg deterministisch (echte Vektoren, kein GUI-Schritt):

```bash
pdftocairo -svg vorlage.pdf vorlage_raw.svg
```

**Skalierung — Kernregel:** Onlineprinters-PDFs sind in **Points** angelegt. `pdftocairo` schreibt
`1 pt = 1 px`, was exakt Figmas 72-DPI-Standard entspricht. → **Kein ×0,75 nötig.** Verifizieren:
SVG-Pixelmaß muss dem manuellen Figma-Symbol entsprechen (Bsp. Theke breit: PDF 2239,37 × 1530,71 pt
→ SVG 2239 × 1531 px = Symbol 2239 × 1530 px). Die ×0,75-Korrektur (96→72 DPI) greift **nur** bei
Raster-/Pixel-Importen, nicht hier.

## 3. Bereinigen

Ziel (nach Vorgabe selectedleafs): **behalten** = Beschnitt-Band, Schnittlinie, Safe Zone, Falzlinien,
Klebelaschen-Marker, rohes „A" (Richtungsangabe) sowie — **falls vorhanden — die eingekreiste Seitenzahl**
(z. B. ① / ②, der Seiten-/Vorder-Rückseiten-Marker). **Entfernen** = Bemaßungspfeile + Maßlinien, mm-Maßtexte,
Bild/Badge (Onlineprinters Foto-Platzierungs-Icon).

> **Regel Seitenzahl:** Ist im Original eine Seitenzahl vorhanden, **muss sie erhalten bleiben** — sie
> gehört zur `Direction`-Gruppe und identifiziert Druckseite bzw. Vorder-/Rückseite. Die Ziffer ist ein
> Glyph (`<use>` + `glyph-*`-Def), der Kreis ein Stroke im **Direction-Grauton** (nicht Bemaßungs-Grau).
> Der pauschale Glyph-Sweep des Cleaners (§3c) würde die Ziffer löschen → bei vorhandener Seitenzahl Ziffer
> **und** Kreis vom Entfernen ausnehmen und nach dem Reinigen prüfen, dass beide gerendert werden.

`pdftocairo` flacht alles zu Vektoren ohne semantische Layer ab. Trennung läuft daher über
**Farbe + Rolle (Fill vs. Stroke) + Mechanismus (Glyph vs. Pfad)**. Die RGB-Werte sind
**vorlagenspezifisch** — pro neuer Vorlage neu diagnostizieren, nicht die Tabelle blind übernehmen.

### 3a. Diagnose (pro Vorlage einmal)

1. **Element-Inventur:** `grep` auf `fill=`/`stroke=`-Farben, `stroke-width`, `glyph-`-IDs.
2. **Scanline:** PDF hochauflösend rendern (`pdftocairo -png -r 150`), mit PIL eine horizontale **und**
   vertikale Pixel-Linie quer durch eine Panel-Kante legen, Farbwechsel von außen nach innen ausgeben.
   Das liefert die Reihenfolge Band → Schnittlinie → Safe Zone → Innen und die echten RGB-Werte.
3. **Farb-Isolation:** Bei Zweifel je eine Farbe isoliert rendern (alles andere entfernen) oder zwei
   Kandidaten in Kontrastfarben überlagern, um innen/außen (z. B. Safe Zone vs. Schnittlinie) zu klären.
4. **In Figma (nach dem Drop) Farben verifizieren statt raten:** RGB im SVG ist nicht immer eindeutig.
   Im Zweifel die echten `strokes[0].color` / `fills[0].color` der Knoten per `use_figma` auslesen und
   per `return <string>` am Codeende direkt als Tool-Result zurückgeben (kein Umweg über temporäre
   Node-Namen + `get_metadata` nötig — siehe §6). Erst danach Rollen vergeben.

### 3b. Farb-/Rollen-Tabelle (verifiziert an „Theke breit" — pro Vorlage prüfen)

| Element | Wert | Rolle / Mechanismus | Aktion / Layer-Name |
|---|---|---|---|
| Beschnitt-Band **+ Klebelaschen + Eckmarken** | mint `#C3D8C7` | Fill | behalten → **`Bleed`** |
| Schnittlinie / Endformat-Kante | teal `#408886` | **Stroke** | behalten → **`Trim`** |
| Safe Zone (Sicherheitsfläche) | grau `#D4CDCE` | **Fill** | behalten → **`Safe Zone`** |
| Falzlinie | grau `#D4CECF` | **Stroke** | behalten → **`Fold`** |
| Schnittmarken (kleine Kanten-Ticks) | schwarz `#100F0D` | Stroke | behalten → **`Crop`** |
| Richtungsangabe „A" | grau `#AAABAF` | eigene Pfade (Fill) | behalten → **`Direction`** |
| **Seitenzahl (eingekreist, falls vorhanden)** | grau **wie „A"** (`#AAABAF`-Ton) | Ziffer = Glyph (`<use>`), Kreis = **Stroke** | behalten → **`Direction`** (Ziffer + Kreis) |
| Bemaßung (Pfeile/Linien/Köpfe) | grau ~`#949497` | beides | entfernen |
| mm-Maßtexte | `glyph-*` via `<use>` | — | entfernen |
| Bild/Badge | blau/rosa/Berg-Icon | Fill | entfernen |

**Wichtige Korrektur ggü. früheren Annahmen:** `#C3D8C7` (mint) ist **IMMER Bleed** — auch die kleinen
Klebelaschen- und Eckmarken (die früher fälschlich „Cut" hießen). Die **Falz ist grau** (`#D4CECF`),
**nicht** teal — nur die Schnittlinie (`Trim`) ist teal. Generische Annahmen („alles Graue weg",
„Schnittlinie + Falz teal") trügen → immer die echten Knotenfarben lesen (§3a Punkt 4).

**Zwei Fallen, die jede Diagnose checken muss:**
- „A" und Bemaßung sind beide grau, aber **verschiedene Töne** (`#AAABAF` vs. `~#949497`). Nicht pauschal „grau weg".
- Badge-Berg kann fast dasselbe Teal wie die Schnittlinie nutzen — Trennung über **Rolle**: Teal als *Stroke* =
  Trim (behalten), Teal als *Fill* = Badge (entfernen).

**Zweites verifiziertes Beispiel — Fensteraufkleber DIN A6 halb:**

| Element | Wert | Rolle |
|---|---|---|
| Beschnitt-Band | `#ABD0C0` Fill | behalten → `Bleed` |
| Schnittlinie | `#3F8886` Stroke | behalten → `Trim` |
| Safe Zone | `#D6CED0` Fill | behalten → `Safe Zone` |
| „A" | `#A7A5A6` Fill | behalten → `Direction` |
| Bemaßung hell | `#85868A` | entfernen |
| Bemaßung dunkel | `#231F20` | entfernen |
| Maßtext | `#15171B` | entfernen |
| ✂-Deko auf der Trim-Linie | weiß `#FFFFFF` Fill | entfernen |

**Neue Falle:** Schwarz `#231F20` ist hier **Bemaßung** — bei den Displays war Schwarz `Crop` (Schnittmarken,
§3b Tabelle oben). Die Rolle von Schwarz ist **vorlagenabhängig**, kein festes Mapping — Beleg für die
Warnung „Farben pro Vorlage real auslesen" (§8).

**Twin-Knoten:** Nach dem Import liegt fast jeder Guide doppelt vor — eine sichtbare Variante **und** ein
um 180° rotierter Stroke-Twin (Stroke-Expansion von `pdftocairo`/Figma-Import). Beide gehören zur selben
Rolle und bekommen denselben Layer-Namen (z. B. zwei Layer `Trim`). Die `get_metadata`-Koordinaten des
Twins wirken verschoben (Rotations-Artefakt), die gerenderte Position stimmt aber — über die Gruppen-bbox
gegenprüfen.

### 3c. Ausführen

`scripts/clean_dieline.py` umsetzen — die Farbkonstanten oben im Skript an die diagnostizierte Tabelle
(§3a/§3b) anpassen, dann ausführen:

```bash
python3 scripts/clean_dieline.py vorlage_raw.svg vorlage_clean.svg
```

Logik: (1) alle `<use>` + `glyph-*`-Defs entfernen (= mm-Text; „A" sind eigene Pfade und überleben),
(2) Elemente mit Bemaßungs-Grau oder Badge-Farben (inkl. Teal-als-Fill) entfernen. Alles andere bleibt.
**Ausnahme — Seitenzahl:** Ist eine Seitenzahl vorhanden (§3 Regel), ist ihre Ziffer ebenfalls ein `<use>`-Glyph
und würde von Schritt (1) gelöscht. Dann das Ziffern-Glyph (und seinen Kreis-Stroke) vom Sweep **ausnehmen** —
z. B. das betreffende `<use>`/`glyph-*` whitelisten oder die Ziffer vor dem Lauf zu einem Pfad outlinen.
Ergebnis mit `cairosvg` rendern und gegen das Original-Panel prüfen (Crop-Vergleich) — **inkl. Kontrolle, dass
eine vorhandene Seitenzahl + Kreis noch da sind.**

**Rollen als Layer-Namen (Pflichtschritt).** Der Cleaner setzt für erhaltene Guide-Elemente das `id`-Attribut
auf die Rolle (`id="Bleed"`, `id="Trim"`, `id="Safe Zone"`, `id="Direction"` usw. — Zuordnung über die
Rollen-Farbtabelle aus §3a/§3b, pro Vorlage befüllt). Figma übernimmt `id`-Attribute beim SVG-Import als
Layer-Namen → die Vektoren kommen bereits benannt in Figma an, der Umbenennungs-Durchlauf in §6 entfällt
fast vollständig. Verifiziert.

## 4. Specs ziehen

- **Aus der PDF-Textebene** (verlässlich): Beschnitt, Sicherheitsabstand, Panel-/System-Maße.
  Achtung: bei Displays gilt **10 mm Beschnitt / ≥ 3 mm Sicherheit** (umgekehrt zum Flachdruck).
- **Aus der Produktseite** (bot-gesperrt → Person kopiert rein): Kopf-Werte Datenformat / Endformat /
  Systemgröße, Artikelnummer, Farbprofile (FOGRA), Druckart (z. B. 4/0, UV), Material (Re-board).

---

## 5. SVG in Figma (manuell)

Bereinigtes SVG per Drag in die Zielseite ziehen (entspricht dem bestehenden manuellen Schritt).
Figma importiert es als **einen flachen Vektor-Frame** (alle Guides als Geschwister-Knoten darin).
Danach übernimmt `use_figma` (§6).

---

## 6. Component & Slot-Struktur (use_figma)

Zielstruktur — verifiziert an „Onlineprinters, Produktdisplay für Theke, breit":

```
COMPONENT  "Onlineprinters, {Produkt}, {Format}"   (px = pt, 1:1)
├── Slots (echte SLOT-Nodes via `component.createSlot()`, leer, benannt + exakt positioniert,
│          HINTER Print Meta im Stack) ← Artwork kommt hier rein
│     z. B. Coat Left / Coat Back / Coat Right / Coat Background / Wall / Floor / Front
└── "Print Meta"  (Boolean-Property, VORNE im Stack, locked = true)
      └── pro Panel EINE Gruppe (nach Panel benannt). Layer-Panel oben→unten:
            Direction → Bleed → Trim → Safe Zone → [Marken: Crop / Fold / Punch / Bleed-Klebelaschen] → Overlay
            (= appendChild-Folge unten→oben: Overlay → [Marken] → Safe Zone → Trim → Bleed → Direction)
            Referenz-Stack: nächste Schwester-Component derselben Produktfamilie im Sammelframe
            `272:41227` (Fallback: 456:181, DIN A4 4/4).
            (Falt-Panel → Eltern-Gruppe mit Zonen-Subgruppen, siehe Regel „Multi-Fold-Panel")
```

### Mehrseitiger Druckbogen (Falzflyer / Wickelfalz) — verifiziert an „DIN Lang Wickelfalz"

Hat das Produkt **mehrere Druckseiten** (Außen-/Innenseite eines Falzflyers), wird daraus **EINE** Component
mit pro Druckseite **einem eigenständigen Sub-Frame** als oberste Ebene. Jeder Frame ist eine separat
exportierbare Druckseite mit **eigenen Slots + eigener `Print Meta`-Gruppe**; **eine** gemeinsame Boolean-
Property `Print Meta` steuert beide.

```
COMPONENT  "Onlineprinters, Wickelfalz, DIN Lang"
├── FRAME "Außenseite"            (eine Druckseite, px = pt, 1:1)
│     ├── Slots links→rechts      Flap (Outside) / Back / Cover
│     └── "Print Meta" (locked)   Face-Gruppen links→rechts → Trim → Bleed → Overlay
│            └── Face-Gruppe       Direction → Fold → Safe Zone   (je Panel)
└── FRAME "Innenseite"
      ├── Slots links→rechts      Right / Center / Flap (Inside)
      └── "Print Meta" (locked)
```

Es gelten die Regeln unten: **Slot-Geometrie** (Bleed-Kante außen, Falzlinie innen, keine Falzmitte),
**Layer-Reihenfolge links→rechts**, **face-getrennte Safe Zones in die Face-Gruppen**, **Print Meta =
Property #1, beide Gruppen gemeinsam gebunden**. Die Falz-Lage ist außen/innen **gespiegelt** (das schmale
eingerollte Panel liegt außen links, innen rechts) — Slots/Falzen pro Seite aus der jeweiligen Vorlage
ableiten, nicht durch Kopieren spiegeln.

**Regeln (selectedleafs-spezifisch):**

- **Overlay = Frame** (Solid Weiß), Opacity an Core `opacity/subtle` gebunden — **KEINE Rectangles/Pfade.**
  Liegt als unterstes Element der Panel-Gruppe (hinter den Guides), dämpft das Slot-Artwork.
  *Importiertes Rect-Overlay konvertieren:* neuen Frame anlegen (gleiche Größe/Position), weiße Solid-Fill,
  das vorhandene `opacity`-Variable-Binding mitkopieren (`getVariableByIdAsync` → `setBoundVariable`),
  altes Rect löschen.
- **Slots = echte `SLOT`-Nodes**, NICHT benannte Frames. Anlegen via `componentNode.createSlot()`
  (liefert einen `SLOT`-Node, der sich benennen/positionieren/`resize`n lässt). `figma.createSlot` existiert
  NICHT (Zugriff *wirft*) — die Methode hängt am **Component-Node**. Slots sitzen HINTER `Print Meta` im Stack
  (das Overlay dämpft das Slot-Artwork), `Print Meta` zuletzt `appendChild`en, damit es vorne liegt.
- **Slot-Geometrie = Bleed-Abdeckung, nicht Endformat.** Jeder Slot deckt die **Bleed-Fläche** seines Panels
  ab — lückenlos und überlappungsfrei zu den Nachbar-Slots, Höhe = volle Bleed-Höhe. An **Außenkanten**
  (oben/unten + äußere Seitenkante) reicht der Slot bis zur **Bleed-Kante** (Datenformat-Rand, nicht bis Trim):
  dort wird geschnitten, randabfallendes Artwork muss in den Beschnitt laufen. An **Falzen** stoßen zwei
  benachbarte Slots an der **Falzlinie** aneinander — dort wird gefaltet, nicht geschnitten → **kein Bleed,
  keine Falzmitte-Teilung** (Falzmitte wäre nur an einer Schnittkante sinnvoll, die es zwischen Panels nicht
  gibt). Bei einer Component aus mehreren Sub-Frames ist `node.x` des Slots **parent-relativ zum Frame** →
  direkt setzen (`slot.x = relX`, z. B. `0` / Falz1 / Falz2). Nicht über `absoluteBoundingBox` mit einem
  angenommenen Frame-Absolutwert rechnen (siehe Gotcha „Slot-Koordinaten / negative Page-Koordinaten").
- **Layer-Reihenfolge links→rechts.** Slots (im Frame) **und** Face-Gruppen (in Print Meta) im Layer-Panel
  von oben nach unten in **Panel-Reihenfolge links→rechts** (linkes Panel oben). Im `children`-Array ist das
  bottom→top von rechts nach links → **rechtestes Panel zuerst `appendChild`en, linkestes zuletzt**; `Print
  Meta` als Allerletztes (liegt damit vorne/oben). Macht Layer-Panel und visuelle Anordnung deckungsgleich.
- **Slots/Container-Frames NIEMALS mit Fill.** `createSlot()` legt per Default einen weißen `SOLID`-Fill an —
  direkt nach dem Anlegen `node.fills = []` setzen. Ein gefüllter Slot zeigt im Leerzustand eine Fläche und
  verfälscht die Druckdaten. **Einzige Ausnahme: das `Overlay`** (Solid Weiß ist seine Funktion, gebunden an
  `opacity/subtle`).
- **Pro Panel EINE Gruppe** (`figma.group(nodes, parent)` — behält absolute Positionen auch beim Reparenten
  über verschiedene Parents hinweg, verifiziert). **Stack (Layer-Panel oben→unten):**
  `Direction → Bleed → Trim → Safe Zone → [Marken: Crop / Fold / Punch / Bleed-Klebelaschen] → Overlay`.
  Per `appendChild` ist das die **umgekehrte** Folge (unten→oben):
  `Overlay → [Marken] → Safe Zone → Trim → Bleed → Direction` — Overlay zuerst (unten/hinten), Direction
  zuletzt (oben/vorne). **Bleed liegt HOCH** (direkt unter Direction), NICHT über Overlay — sonst verdeckt die
  Safe-Zone-Füllung das Beschnitt-Band. Funktionale Marken (Crop/Fold/Punch/Klebelaschen) sitzen **unten**,
  zwischen Safe Zone und Overlay. **Referenz: erst im Sammelframe `272:41227` nach einer Schwester-Component
  derselben Produktfamilie suchen** (Fallback: `456:181`, DIN A4 4/4, bzw. Plakat A2) — bei jedem Build die
  nächste fertige Schwester-Component gegenlesen, nicht nur diesen Text.
- **Position NACH dem Reparenten setzen (kritisch).** `figma.group()` und das Reparenten eines *bestehenden*
  Knotens (`parent.appendChild(node)`) erhalten die absolute Lage. Bei einem **neu erstellten** Knoten
  (`createFrame`/`createSlot`) oder einem **`clone()`** wird ein vorher gesetztes `x/y` beim `appendChild` als
  *relativ* zum neuen Parent interpretiert → der Parent-Offset wird doppelt angewandt (Overlay/Klon landen
  verschoben). Regel: **erst anhängen, dann korrigieren** —
  `node.x += (zielAbsX − node.absoluteBoundingBox.x)` (analog y). Nie `x/y` vor dem `appendChild` setzen und
  auf Absolutlage vertrauen.
- **Multi-Fold-Panel** (z. B. Giebel/Wrap mit 2 Falzlinien → 3 Faces): die Stanzkontur ist EIN Kartonteil —
  Bleed/Safe/Trim bleiben **durchgehend, je 1×**. Struktur: **eine** Eltern-Guide-Gruppe (z. B. `Wrap`) mit
  `Overlay → Safe Zone → Trim → Bleed` (durchgehend, unten→oben) und darunter **Zonen-Subgruppen** (`Left`/`Center`/`Right`),
  die je die zonen-eigenen Kleinelemente halten (A, `Fold`, `Crop`, Slot-Marken). KEIN Clipping, KEINE
  geklonten/beschnittenen Pfade. Die **Slots** dagegen werden pro Face einzeln angelegt (ein Slot je Face).
  *Dies gilt für **eine durchgehende** Safe Zone über alle Faces (typisch bei einem Kartonteil/Display).*
- **Einteiliges Flachprodukt** (z. B. Aufkleber, Karten — eine Stanzkontur ohne Panel-Unterteilung, kein
  Falz): abweichend vom Mehrteiler-Muster oben gilt hier das Hausmuster — **`Print Meta` = FRAME** (nicht
  GROUP), `fills=[]`, `clipsContent=false`, locked. Der Slot heißt generisch **`Content`** (nicht
  Panel-Name), genau einer. Stack unverändert: `Direction → Bleed → Trim → Safe Zone → Overlay`.
  Verifiziert an „Onlineprinters, Fensteraufkleber, DIN A5 halb" (`648:179`).
- **Durchgehende vs. face-getrennte Safe Zone (Faustregel: so granular wie in der Vorlage).** Manche Vorlagen
  (z. B. Falzflyer) haben **pro Panel eine eigene** Safe-Zone-Fläche statt einer durchgehenden. Dann gehört
  jede Safe Zone **in ihre Face-Gruppe** (zusammen mit `Fold`/`Direction` dieses Panels) — **nicht** auf die
  Print-Meta-Eltern-Ebene. Diagnose: Safe-Zone-Flächen per Mitte gegen die Panel-/Slot-Regionen matchen, dann
  in die gleichnamige Face-Gruppe einsortieren. Nur `Bleed`/`Trim`/`Overlay` bleiben in diesem Fall durchgehend
  auf der Print-Meta-Ebene; alles Panel-Eigene (Safe Zone, Fold, Direction) lebt in der Face-Gruppe.
- **Naming (Englisch):** `Overlay`, `Bleed`, `Safe Zone`, `Trim`, `Fold`, `Crop`, `Direction`.
  Keine `Vector`/`Group`/`Clip path group`/`clip-N`-Reste — auch die inneren Knoten der Bleed-Clip-Group
  umbenennen. Hinweis-/Rollenname folgt der **Farbe**, nicht der Geometrie.
- **Farbe bestimmt Rolle** (§3b): mint `#C3D8C7` = immer `Bleed` (inkl. Klebelaschen/Eckmarken) ·
  teal `#408886` = `Trim` · grau `#D4CDCE` (Fill) = `Safe Zone` · grau `#D4CECF` (Stroke) = `Fold` ·
  schwarz `#100F0D` = `Crop` · grau `#AAABAF` = `Direction`. **Echte Farben pro Vorlage lesen, nicht raten.**
- **Twins** (sichtbar + rotierter Stroke-Twin) bekommen denselben Rollennamen (z. B. zwei `Trim`).
- Rohes „A" aus dem SVG **stehen lassen** (= `Direction`) — keine eigene Heading-Group-Component.
  **Ist eine eingekreiste Seitenzahl vorhanden, bleibt sie erhalten:** Ziffer + Kreis kommen in dieselbe
  `Direction`-Gruppe (Knoten z. B. `A`, `Circle`, `Page Number`). Der Kreis ist ein Stroke im Direction-Grauton
  (nicht Bemaßungs-Grau) — Knotenfarbe lesen, nicht raten; und prüfen, dass das Ziffern-Glyph den Cleaner
  überlebt hat (§3c Ausnahme).
- **Property „Print Meta"** (Title Case, mit Leerzeichen), Boolean, an die Visibility der Print-Meta-Gruppe
  gebunden. Rename via `componentNode.editComponentProperty(key, { name: 'Print Meta' })`.
  **Als ERSTE Property anlegen — VOR dem ersten `createSlot()`** (Property #1): die API kann die
  Property-Reihenfolge nachträglich **nicht** umsortieren, und **jeder `createSlot()` erzeugt automatisch
  eine eigene Component-Property** in Anlege-Reihenfolge. Wird `Print Meta` erst nach den Slots angelegt,
  landet es UNTER den Slot-Properties. Korrekte Reihenfolge: (1) `figma.createComponent()`,
  (2) `addComponentProperty('Print Meta','BOOLEAN',true)`, (3) erst danach pro Druckseite `createSlot()`.
  *Slots nachträglich löschen entfernt ihre Property NICHT automatisch — Orphan-Properties per
  `deleteComponentProperty(key)` aufräumen.* Bei einer Component mit **mehreren Sub-Frames**
  (mehrseitiger Druckbogen): nur **eine** `Print Meta`-Property anlegen und **beide** Print-Meta-Gruppen an
  dieselbe Property binden (ein Toggle steuert alle Seiten).
- **Print Meta = oberste Ebene + `locked = true`** (Lock erst nach allen Edits setzen).
- **Coat Background = Sonderfall:** NICHT als Template-Panel behandeln, NICHT als wiederholbares Muster
  führen. Pragmatisch als **eine** `Coat`-Gruppe (1 Overlay = das Band) lösen; sie enthält zusätzlich
  `Fold` (Falz), `Crop` und mint `Bleed`-Klebelaschen. Die mint `Bleed`-Marken dürfen im Stack **über**
  der grauen `Safe Zone`-Füllung liegen (sonst verdeckt sie sie) — bei den reinen Panels (Wall/Floor/Front)
  ist der Stack rein kanonisch. *Faltet das Band in mehrere Faces, gilt die Regel „Multi-Fold-Panel" oben:
  durchgehende Pfade in der Eltern-Gruppe, je Face eine Zonen-Subgruppe; Slots aber je Face einzeln.*
- **Decomposition:** Den gedroppten Monolith (flacher Vektor-Frame) per **Bounding-Box gegen die
  Panel-Regionen** + Farbe pro Panel zerlegen, die Knoten in die jeweilige Panel-Gruppe ziehen. Wenn der
  Monolith leer ist → Frame löschen.
- Cross-File-Bindings beachten (`figma-standards` §1): Farben/Größen an Core binden, wo möglich.

**use_figma kann das vollständig** (Plugin-API-JS): `figma.createComponent()`, benannte Frames mit
Position/Größe, `figma.group()`, `figma.createFrame()` (Overlay), `componentNode.createSlot()` (echte Slots),
`editComponentProperty(...)`, `node.locked`, `node.descriptionMarkdown`, `node.documentationLinks`. Seite über
`figma.root.children.find(p=>p.name==='_SANDBOX')` + `await figma.setCurrentPageAsync(page)` ansteuern
(`figma.currentPage=` wird nicht unterstützt; `figma.createPage()` persistiert nicht → Seiten manuell anlegen).
**Vor `figma.createComponent()` zwingend `setCurrentPageAsync(_SANDBOX)`** — sonst landet die Component auf der
gerade aktiven Page (currentPage) und muss nachträglich verschoben werden.

**Verifikation — use_figma liefert Rückgabewerte:**
- `return <string>` am Ende des Codes kommt als Tool-Result zurück — kein Umweg über temporäre
  Node-Namen nötig. Verifiziert: komplette Layout-Collection mit 36 Variablen × 7 Modes in einem Call
  als JSON gelesen. Werte (Farben, Property-Keys, IDs neuer Knoten, Flags) direkt so auslesen.
- Struktur/Positionen/Namen zusätzlich über `get_metadata` auf die Print-Meta-Gruppe lesen (günstig,
  Text). Die Gruppen-bbox muss exakt der Panel-Region entsprechen → beweist Positionstreue nach
  `figma.group`. `get_metadata`/`get_screenshot` bleiben für Struktur- und Sichtprüfung sinnvoll, sind
  aber nicht mehr der einzige Lesekanal.
- Visuelle Prüfung über `get_screenshot` mit `enableBase64Response: true` (figma.com-Asset-Domain ist im
  Sandbox-Netz blockiert).
- **Echte Slots:** `componentNode.createSlot()` legt einen `SLOT`-Node an (benennbar/positionierbar/`resize`bar)
  — das ist der richtige Weg, NICHT benannte Frames. **`figma.createSlot` existiert nicht** (Property-Zugriff
  *wirft* einen TypeError) — die Methode hängt am Component-Node, nicht am `figma`-Global. *(Frühere Annahme
  „Slots nur als Frames möglich" war falsch; per 2026-06 mit `component.createSlot()` verifiziert.)*

**SVG-Import bleibt manuell** (§5): Das ~30-KB-Dieline-SVG passt zwar unter das 50-KB-Code-Limit von
`use_figma`, müsste aber wortgetreu inline stehen — für ein Druck-Dieline zu fragil. Kein Hosting/Fetch-Pfad
verfügbar. Daher: Vektor manuell droppen, `use_figma` baut das Gerüst drumherum.

**Build-Reihenfolge:** Erst eine Proof-Component in `_SANDBOX` bauen, Panel für Panel per `get_metadata`/
Screenshot verifizieren, final Slot-Fülltest + Print-Meta-Toggle (über eine Instanz) prüfen, dann promoten.

**Promotion-Ziel:** Onlineprinters-Dielines leben im Sammelframe **`Onlineprinters`** → Sub-Frame
**`Produktdisplays`** (neben den Schwester-Displays), **nicht** im Katalog-`Templates`-Frame der Components-Page.
Ersetzen/Migration alter Versionen ist eine bewusste Entscheidung der Person (Instanzen detachen beim Löschen
des alten Masters) — nicht automatisch ersetzen.

---

## 7. Component Description (einheitliche Struktur)

Englische Labels (`figma-standards` §3: In-File-Doku ist englisch). **Source = PDF im Text;
Produktseite gehört ins native `documentationLinks`-Feld, nicht in den Fließtext.**

**Markdown:** Über `node.descriptionMarkdown` setzen (nicht das alte Plain-`description`). Figma rendert
einen Subset: `##`-Überschriften (**nur Level-2**; `#` wird zu `##` konvertiert), `**bold**`, `*italic*`,
Listen, Links, Inline-/Code-Blöcke. **Nach dem Setzen die Library einmal re-publishen** — sonst greift ein
bekannter Figma-Bug (Description erscheint veraltet/leer).

**Konventionen:** Sektionen als `##` · `**Key:** Value` · **Slots als unordered list** (ein
`-`-Bullet pro Slot) · Hinweise/Notizen *kursiv in eigener Zeile*.
**Headline-Zuordnung:** **Format** = Maße · **Print** = Druckvorbereitung (Resolution, Bleed,
Safe zone, Druckart, **Material**, Color, Fonts) · **Slots** = Figma-Nutzung · **Source** =
Herkunft. *Material* aus der Print-Zeile als eigenen Key lösen (nicht inline „… on Re-board").
*Bleed/Safe zone* sind streng genommen Geometrie, bleiben aber bewusst unter **Print**
(Druckvorbereitung — was der Drucker braucht), nicht unter Format.

```
## Format
**Data:** {W} × {H} cm
**Final:** {W} × {H} cm
**System:** {W} × {H} cm
*assembled {W} × {H} × {D} cm*            ← optional, nur aufgebaute Displays

## Print
**Resolution:** 300 dpi
**Bleed:** {N} mm all around
**Safe zone:** ≥ {N} mm to final format
**Print:** {z. B. 4/0 (front only), UV coating}
**Material:** {z. B. Re-board}            ← optional, Substrat als eigener Key
**Color:** CMYK — {FOGRA-Profile}.
*Figma is RGB — convert on export.*
**Fonts:** embed or convert to outlines.

## Slots
- {Panel-Name}
- {Panel-Name}
- … (ein Bullet pro Slot, in Stack-Reihenfolge)
*Turn "Print Meta" off before PDF export.*

## Source
**PDF:** [print template]({Druckvorlage-PDF-URL})
**Ingested:** {YYYY-MM-DD}
```

*Onlineprinters führt **keine** Artikelnummer — stabile Referenz ist der PDF-Link + die Produktseite im
`documentationLinks`-Feld. Keine `Article no.`-Zeile.*

Separat (Figma-Feld): `documentationLinks = [{ uri: "{Onlineprinters-Produktseite}" }]`

---

## 8. Gotchas

- **Vor jedem Build zuerst im Sammelframe `272:41227` nach einer fertigen Component derselben
  Produktfamilie suchen** (Layer-Reihenfolge in `Print Meta` + Property-Reihenfolge) und spiegeln. Nur wenn
  keine Schwester derselben Familie existiert, `456:181` (DIN A4 4/4, Fallback) heranziehen. Die **realen
  Components sind maßgeblich**, dieser Fließtext ist nur Beispiel/Referenz. Verifiziert: Fensteraufkleber →
  `648:179` („Onlineprinters, Fensteraufkleber, DIN A5 halb", File `IPEk40v01EMVITXst3UPOT`) statt `456:181`.
  *Allein-aus-dem-Text-Bauen hat zu mehreren Fehlbauten geführt (Bleed zu tief, Print Meta unter den
  Slot-Properties).*
- Produkt-HTML bot-gesperrt; Druckvorlagen-PDF-Media-Pfad offen. Kopf-Specs daher per Paste.
- Displays: 10 mm Beschnitt / ≥ 3 mm Sicherheit (nicht 3/10 wie beim Flachdruck).
- Figma ist RGB; CMYK/FOGRA erst beim Export/PDF-Handling relevant.
- **Farben pro Vorlage real auslesen, nicht aus der Geometrie/Tabelle raten** — Annahmen wie
  „Schnittlinie + Falz teal" oder „inneres Rechteck = Safe Zone" trügen (an „breit" war die Falz grau und
  das innere Rechteck der teale Trim neben einer separaten grauen Safe-Zone-Füllung). **Auch die Rolle einer
  Farbe ist nicht stabil:** Schwarz war bei den Displays `Crop`, beim Fensteraufkleber (`#231F20`) dagegen
  Bemaßung (§3b) — Rolle immer neu diagnostizieren, nie aus einer früheren Vorlage übernehmen.
- **`use_figma` liefert Rückgabewerte über `return <string>`** am Codeende (kommt als Tool-Result zurück) —
  Werte (Farben, Property-Keys, IDs, Flags) direkt so lesen, kein Umweg über temporäre Node-Namen nötig.
  Struktur/Position zusätzlich über `get_metadata`/`get_screenshot` verifizieren.
- **`figma.group` behält absolute Positionen** beim Reparenten (auch über Parents hinweg) — Gruppen-bbox
  als Positionsbeweis nutzen. **Aber:** neu erstellte Knoten (`createFrame`/`createSlot`) und `clone()`s
  übernehmen ein vor dem `appendChild` gesetztes `x/y` als *relativ* zum neuen Parent → Offset doppelt.
  Regel: erst `appendChild`, dann `node.x += (zielAbsX − node.absoluteBoundingBox.x)` (analog y).
- **Slot-Koordinaten / negative Page-Koordinaten (promotete Component).** Eine auf eine Page promotete
  Component kann auf **negativen** Page-Koordinaten liegen (Frame-`absoluteBoundingBox.x` < 0). `node.x` eines
  Slots ist **parent-relativ zum Frame** → beim Repositionieren **direkt** setzen (`slot.x = relX`, z. B.
  `0` / Falz1 / Falz2), **nicht** `node.x += (frameAbsX + relX − absoluteBoundingBox.x)` mit einem *angenommenen*
  `frameAbsX` (etwa `0`) rechnen. Stimmt die Absolut-Annahme nicht (negativ!), landen alle Slots um den Versatz
  daneben (DIN-Lang-Fall: +9604 px, neben der Component). Symptom: nachgelagerte Logik (z. B. Safe-Zone-Zuordnung
  per x-Überlappung) „findet nichts" — **kein Error, aber keine Wirkung**. Für rel-Berechnungen `node.x` selbst
  nehmen (parent-relativ; `Print Meta` sitzt auf `0,0` im Frame, daher sind dessen Kinder ebenfalls frame-relativ),
  nicht mit `absoluteBoundingBox` mischen.
- **Echte Slots:** `componentNode.createSlot()` → `SLOT`-Node. **`figma.createSlot()` existiert NICHT** (wirft).
  Slots sind echte Slots, keine benannten Frames. **`createSlot()` setzt per Default weißen `SOLID`-Fill →
  `fills=[]` setzen** (Slots/Container nie mit Fill; Ausnahme: Overlay).
- **`descriptionMarkdown`-Bug:** Description erscheint ggf. veraltet/fehlend, bis die Nodes neu published
  werden → nach dem Setzen Library re-publishen.
- Screenshots aus Figma-MCP: figma.com-Asset-Domain ist im Sandbox-Netz blockiert →
  `get_screenshot` mit `enableBase64Response: true`.
- `get_metadata` auf eine Symbol-Definition liefert **keine Kinder** → Komponenten-Innenstruktur via
  `get_design_context` (oder `get_metadata` auf die innere Gruppe) lesen.
- **Page-Listing-Bug:** `get_metadata` ohne `nodeId` lässt Pages aus. Workaround: `nodeId=0:1` → die
  Fehlermeldung enthält die vollständige Page-Liste.
- **CMYK-/DPI-Export (Tooling):** Figma exportiert nativ RGB. Für CMYK-PDF mit ICC-/FOGRA-Profilen,
  300-dpi-Check und Bleed/Crop-Marks gibt es das Plugin **Print for Figma** (Ben Katz, ~250k Nutzer,
  ~$12/Mt In-App): https://www.figma.com/community/plugin/874441781480244375 — deckt genau
  „Figma is RGB → convert on export" + den DPI-Check ab. **Grenzen:** kann **keine Dielines/Overprint**
  (vom Autor als geplant genannt) → die Stanzkontur bleibt unser manueller SVG-Workflow; Figma outlined
  Strokes beim PDF-Export (für unsere Guides egal, da `Print Meta` vor Export ausgeschaltet wird). Vor
  Serie immer Testdruck/Proof beim Drucker. Gehört in den **Workflow** (dieses Skill), **nicht** in die
  Component-Description/`documentationLinks`.

## Bundled

- `scripts/clean_dieline.py` — Dieline-Cleaner (role-aware, ein Lauf: entfernt alle `<use>` + glyph-Defs,
  Bemaßungs-Grau, mm-Label-Pfade, Badge-Farben inkl. Teal-als-Fill, white-filter-Gruppen; behält die
  Keep-Rollen und setzt für sie das `id`-Attribut auf den Rollennamen, siehe §3c). **Farbkonstanten oben im
  Skript (Entfernen UND `KEEP_ROLES`) sind pro Vorlage via §3a neu zu diagnostizieren** — die mitgelieferten
  Werte sind das „tief"-Beispiel; `KEEP_ROLES` ist bis auf den bereits verifizierten `Fold`-Stroke leer und
  muss pro Vorlage befüllt werden.
