# Figma Standards — selectedleafs (Volltext)

Werte (konkrete Farben, Größen, Abstände, Radien) stehen in den Variables und Text Styles der Files selbst. Diese Datei enthält ausschließlich die Patterns, Regeln und Konventionen, die über mehrere Chats hinweg konsistent gelten müssen. Rollen und Palette im Einzelnen: `rollen-und-palette.md`. Audit und Ausnahmen: `audit.md`.

## Inhalt
1. Token Discipline
2. Modes-System
3. Naming Conventions
4. File-Structure
5. Governance
6. Decision Tree: Variable vs Style vs Component
7. Druck und Source of Truth

---

## 1. Token Discipline

- **Variables** für jeden Wert mit semantischer Bedeutung: Color, Size, Spacing, Radius, Proportion.
- **Drei Ebenen, eine Bindungsregel:**
  - **Palette** — Rohwerte (Farben nach Farbton und Helligkeit, Schriften, Deckkraft, Unschärfe), ein Modus, für Konsumenten verborgen und ohne Farb-Scopes.
  - **Rollen** (`Color Scheme`) — Fläche, Inhalt, Akzent, Zustände, Status/Highlights (`color/global/*` mit eigener `-text`-Farbe), Overlay, Deckkraft. Werte nur als Alias auf die Palette.
  - **Kontext** — `Layout`, `Variety`, `Price Tier`, `Employee`; Farben nur als Alias auf die Palette.
  - **Ebenen binden nur Rollen oder Kontext — nie die Palette, nie feste Werte.** Ausnahmen stehen in `audit.md` (R1, festgelegte Ausnahmen) und werden dort gepflegt.
- **Text Styles** für Typografie — `font-family`, `size`, `weight`, `line-height`, `letter-spacing` immer als Style, niemals als manueller fontName-Override.
- **Cross-File-Bindings sind Pflicht.** Print- und Shop-Components müssen an Core-Variables und -Styles binden (nicht an lokale Werte). Ohne diese Disziplin funktioniert weder Re-Branding noch Cross-Konsum sauber.
- **Pflichtangaben je Variable:** Scopes (nur die Felder, für die sie gedacht ist; nie `ALL_SCOPES`; Ausnahme: boolesche Variablen wie `effect/glow` haben in Figma keine Scopes und bleiben bei `ALL_SCOPES`, Ausnahme in R6), eine Beschreibung (Rolle + Quelle im Theme) und, wo das Theme eine CSS-Variable hat, der Code-Name (WEB, z. B. `var(--brand--primary)`). Verläufe aus dem Theme werden in Einzelfarben zerlegt, weil Figma-Variablen keine Verläufe halten; die Beschreibung nennt die Theme-Einstellung.
- **Neue Rolle nur, wenn** das Theme sie hat oder als geplante Theme-Rolle aufnimmt (todos.md TODO-044 im Projekt selectedleafs.com) **und** sie in mindestens einer Datei gebraucht wird. Keine Tokens je Baustein.
- **Verboten** in produktiven Frames: Hex-Codes direkt im Layer, magische Pixel-Zahlen ohne Token-Bezug, ad-hoc Font-Properties.
- **Erlaubte Ausnahmen** (dokumentieren, wenn nicht selbsterklärend):
  - Pill-Radius `9999` als magic constant (Variable wäre Overhead).
  - Page `_SANDBOX` (Sandbox — Token-Disziplin gilt dort nicht).
  - Explizite Overrides mit kurzer Begründung im Layer-Namen oder Page-Header.

---

## 2. Modes-System

Die `Layout`-Collection nutzt Modes statt Duplicate Variants. Ein Frame bindet sich an eine Mode, alle Tokens passen sich an. **Modes leben im Core-File** als Variable-Collection-Modes; Product, Print und Shop konsumieren sie per Mode-Switch auf Frame-Ebene.

**7 Modes:**

- **Desktop** — Bildschirm-Frames Desktop-Viewport: Theme-Sync (Desktop), Desktop-Mockups, Component-Library.
- **Mobile** — Bildschirm-Frames Mobile-Viewport: Mobile-Theme-Sync, Mobile-Mockups, Touch-Komponenten.
- **DIN A2** — Print A2: Poster, Großformat-Layouts.
- **DIN A3** — Print A3: Großseiten, Mid-Format-Layouts.
- **DIN A4** — Print A4: Katalog-Innenseiten, Datenblätter, Formulare.
- **DIN A5** — Print A5: Halbseiten-Formate, kompakte Datenblätter, Beilagen.
- **DIN A6 · DIN Lang** — Print DIN Lang: Flyer, Falzformate.

**Skalierungs-Regel (Print):**

Basis ist **DIN A4** (primäres Deliverable). Die Skalierungs-Einheit ist **√2 pro A-Stufe** (ISO 216): jeder Mode = `A4 × (√2)ⁿ`, n = Stufenabstand zu A4.

| Mode | n | Faktor |
|---|--:|--:|
| DIN A2 | +2 | 2,000 |
| DIN A3 | +1 | 1,414 |
| **DIN A4** | 0 | 1,000 (Basis) |
| **DIN A5** | −1 | 0,707 |
| DIN Lang (≈ A6) | −2 | 0,500 |
| A7 | −3 | 0,354 |

- **Geometrische Gruppe** (`spacing`, `border-radius`, `border-width`, `proportion`) skaliert rein geometrisch: Wert = `A4 × (√2)ⁿ`, gerundet.
- **Optische Gruppe** (`font/*`, `icon/*`, `info box/margin`): Nur beim **Verkleinern** (Formate < A4) gilt ein eigener flacherer Ramp mit Legibility-Floor statt reinem √2 — sonst wird Body bei A6/A7 unleserlich und Icons verschwinden. Der Ramp ist pro Untergruppe eigenständig; Faktoren gemessen an DIN Lang (A6-Sprosse): Headings ≈ 0,58 · Body ≈ 0,70 · Icons + info box ≈ 0,707. Zwischenstufen werden als geometrisches Mittel der Nachbarsprossen abgeleitet (A5 = √(A6-Faktor)). Beim **Vergrößern** (Formate > A4, z.B. A3/A2) reines √2 für alle Gruppen, da kein Floor-Problem.
- **Konstanten** ausgenommen: `frame` (Design-Referenz) und `border-radius/full` (Pill).
- **DIN Lang** belegt layout-seitig die A6-Sprosse (×0,5). Seine Seitenproportion (1:2,1) ist nicht die A-Reihe — der Skalierungsfaktor wird nur geliehen, nicht die Geometrie.
- Neuen Mode hinzufügen = Faktor an der Sprosse einsetzen, Layout-Tokens aus dem A4-Wert ableiten, optische Tokens über den Gruppen-Ramp interpolieren. Prüfkriterium: jeder Wert liegt monoton zwischen den beiden Nachbar-Sprossen.

**Frame & Web:**
- Mode-Switch ersetzt jede Form von Duplicate Frame oder Format-Variant.
- Print-Modes folgen dem Figma-Standard `1pt = 1px` (72 DPI Referenz). Der PDF-Export trägt damit automatisch die korrekte physische Seitengröße (A4-Frame 595 × 842 px → 210 × 297 mm). Druckauflösung kommt aus hochauflösenden Quellbildern, nicht aus der Frame-Größe.
- Web-Skalierung (Desktop/Mobile) folgt der Source of Truth in `assets/core.base.css` (clamp 320–1440). Desktop-Mode entspricht dem Upper-Bound, Mobile-Mode dem Lower-Bound — nicht aus Print abgeleitet.

**Welcher Mode für welchen Frame:**
- Component-Library, Web-Mockups, Theme-Sync → Desktop oder Mobile (je nach Viewport-Target).
- Katalog/Datenblatt → DIN A4. Großseite/Mid-Format → DIN A3. Poster → DIN A2. Flyer/Falz → DIN Lang.

**Color Scheme (zweite Mode-Collection):**
- Die Modes heißen nach der **Fläche**: `White` (Standard, erste Stelle; Shop-Schema background-1), `Forest` (Shop-Schema mit Forest-Hintergrund), `Cream` (Creme-Flächen in Print; Kopie von White mit Creme-Fläche, weißer Karte und dunklem Gold für Kontrast; kein Theme-Schema). Die alten Namen `Dark Content` / `Light Content` (Inhalt statt Fläche) gelten nicht mehr.
- **Standard-Mode ist `White`** (hell, wie das Theme). Jeder oberste Rahmen einer Page setzt seinen Mode trotzdem explizit, damit eine spätere Änderung der Mode-Reihenfolge nichts verschiebt. Auch der Rahmen einer Components-Seite steht auf `White`: Bausteine ohne eigene Fläche zeigen dort ihre Rollen sonst auf dem hellen Canvas in der falschen Fläche.
- **Farbrollen gelten gleich für Theme und Apps:**
  - Aus dem Shop-Schema (`color/scheme/*`): `background`, `card`, `text`, `accent` (nur noch dekorativ), `link`, `border`, `grey`, `button-primary(-text)`, `button-secondary(-text)`.
  - Gemeinsame Rollen, die das Theme bei der Überarbeitung übernimmt: `active` (aktiver Zustand von Navigation und Datenmarken; Gold in allen Modi), `selection` (Auswahlring und Haken), `selection-tint` (Fläche einer gewählten Auswahl), `focus` (Fokusring), `disabled(-text)`, `accent-secondary` (dekoratives Blattgrün), `accent-text` und `accent-secondary-text` (Text und Icons auf den Akzentflächen, weiß).
  - **Status und Highlights sind modusfrei** (`color/global/success · warning · error · info · sale · new · promotion · bestseller · rating`), jede gefüllte Rolle mit eigener Textfarbe `-text` und, wo ein Baustein den Verlauf zeigt, `-end`. Farbige Flächen (Tags, Badges, Status-Pills) binden Fläche und Text an diese Rollen und setzen **keinen** eigenen Mode.
  - `color/global/overlay` (Schwarz 60 %) immer zusammen mit Hintergrund-Unschärfe an `blur/overlay`; Deckkraft über `opacity/subtle · muted · faint`.
  - `icon` für Icons und Logos, gleich `text`. Textebenen binden an `text`, nie an `icon`.
- **Modus-Regel:** Eine farbige Rolle bleibt in allen Modi in derselben Farbfamilie der Palette (zweites Glied des Palette-Namens, z. B. `forest`, `leaf`, `gold`); je Modus darf nur die Helligkeitsstufe wechseln, etwa für Kontrast auf der Fläche. Ausgenommen sind die Flächen- und Neutralrollen `background`, `card`, `grey`, `text`, `icon`, `border`, `disabled`, `disabled-text`, weil sie den Modus ausmachen. So bauen auch Material 3 und Apple Hell/Dunkel auf (gleiche Farbe, andere Stufe; Dunkel ist keine Umkehrung). Geprüft im Audit (R6, `audit.md`).
- Ein „Dark Mode“ in Web oder App ist ein Frame auf `Forest`.
- **Keine Varianten für die Fläche.** Bausteine bekommen ihre Fläche über den Mode, nicht über eine Variante wie „Theme“. Varianten nur für eine echte Wahl auf derselben Fläche, benannt nach dem, was sie wählen (Print: `Accent = Primary · Secondary`, `Style = Solid · Soft`, `Surface = Background · Card`).
- **Bausteine mit fester Fläche setzen ihren Mode selbst.** Eine Rolle ist modusabhängig, die Palette nicht: Ein Baustein, dessen Fläche überall Forest sein muss (z. B. Schrittmarker, Zitat-Box), setzt `Forest` am Baustein, statt sich auf die Umgebung zu verlassen. Beim Umbinden immer auch die Exemplare in anderer Umgebung prüfen.
- Exemplare erben den Mode ihres Bausteins. Wird ein geerbter Mode am Exemplar gelöscht, fällt das Exemplar auf den Mode seiner Umgebung zurück. Modes an Exemplaren deshalb gezielt setzen, nie pauschal löschen.

---

## 3. Naming Conventions

- **Slash-Hierarchie**: `namespace/category/variant` — Beispiele: `spacing/medium`, `color/scheme/text`, `heading/h1`.
- **Lowercase-kebab** durchgehend in Tokens. Keine CamelCase, keine Underscores, keine Leerzeichen in Token-Namen.
- **Singular** für Token-Werte (`color/forest/25`, `border-radius/small`); **Plural** für Sammlungen und Page-Namen (`Product Labels`, `Variables`).
- **Page-Naming — Hybrid-Schema:**
  - **Meta-Slots** in `CAPS` ohne Nummer und ohne Trennzeichen: `INDEX`, `_SANDBOX`. Optional weitere Meta-Slots (`GUIDELINES`, `CONTRIBUTORS`, `LICENSING`) in derselben Form.
  - **Content-Pages** mit Nummer + Middle Dot + Title Case: `01 · Logos`, `02 · Icons`, `03 · Typography`.
  - `_SANDBOX` behält den führenden Underscore als Marker "kein Production-Content".
- **Skalen** primär als Wort-Stufen (`xsmall/small/medium/large/xlarge`). Numerische Skalen nur wenn die Skala >5 Stufen hat oder bereits in der CSS-Source numerisch ist.
- **Palette numerisch nach Helligkeit:** `color/<farbton>/<stufe>`, Stufe = L* (CIELAB) des Werts auf 5 gerundet, 0 = Schwarz, 100 = Weiß (wie die Töne in Material 3). Landen zwei Werte eines Farbtons auf derselben Stufe, gilt der ganzzahlige L*-Wert. Alpha-Stufen hängen die Deckkraft an: `color/neutral/5-a10` = Ton 5 mit 10 %, 7,5 % als `-a7-5`. Rollen und Kontext behalten Wortnamen.
- **Namen folgen dem Theme**, wo das Theme die Rolle kennt (`color/scheme/link` ↔ `--color-scheme--link`, `color/global/sale` ↔ `--color-global--sale`). Palette-Einträge tragen den Theme-Markenslot als Code-Name (`color/gold/65` ↔ `--brand--primary-accent`), nicht im Namen.
- **Beispiele aus den Collections:**
  - Palette: `color/forest/25`, `color/gold/65`, `color/leaf/60`, `color/neutral/5-a10`, `opacity/80`, `blur/8`, `font-family/heading`.
  - Color Scheme: `color/scheme/text`, `color/scheme/active`, `color/global/success-text`, `color/global/overlay`, `opacity/subtle`.
  - Layout: `spacing/medium`, `icon/regular`, `border-radius/full`, `border-width/regular`, `proportion/golden/minor`.
  - Variety: `color/variety/light`, `color/variety/dark`.
  - Typografie (Text Styles): `heading/h1`, `body/regular`, `label/caption`. Text Styles nutzen bewusst **keinen** `font/`-Prefix — die Gruppierung ergibt sich aus dem Style-Typ selbst.
  - Product Labels: `label/vein/white`, `label/tier/select`.
- Diese Konvention gilt **File-übergreifend** — Tokens in Core und ihre Konsumenten in Product/Print/Shop folgen demselben Schema.
- **Sprache: Englisch** für alle Inhalte innerhalb der Figma-Files — Page-Namen, TOC-Descriptions, Changelog-Einträge, Component Descriptions, Frame-Namen. Die Token-Sprache ist bereits durchgängig Englisch; In-File-Dokumentation folgt derselben Sprache, weil die Files als Design-System-Referenz für Entwickler dienen. Prozess-Dokumente außerhalb von Figma (dieser Skill, todos.md etc.) bleiben Deutsch.

---

## 4. File-Structure

selectedleafs nutzt **4 Files** in einer Dependency-Hierarchie. Jeder File hat eigene Master-Verantwortung; Cross-Bindings zwischen gleichrangigen Files (Print ↔ Shop) sind verboten.

### 4.1 Architektur

```
LAYER 1: Core                      (Brand-Identität — reine Component Library)
   Logos · Icons · Typography · File Meta
   + Variables (Panel) · Text Styles (Panel)
                       ↓
LAYER 2: Product                   (Brand-Produkt-Träger)
   Product Labels · Pouch Renderings
                       ↓
LAYER 3a: Print                    LAYER 3b: Shop
   Components + Outputs               Components + Outputs
```

Print und Shop konsumieren beide Core und Product. Sie binden sich nicht gegenseitig.

Die Sales App ist ein weiterer Output-File auf Layer 3 neben Print und Shop (nach §5.5): Sie konsumiert Core und Product und bindet weder Print noch Shop.

**Core als reine Component Library:** Core enthält ausschließlich publishable Components auf dem Canvas. Variables und Text Styles werden über die Figma-Panels verwaltet — keine Swatch-Pages, keine Specimen-Pages, keine Token-Dokumentation auf dem Canvas. Jede Content-Page in Core ist eine Component-Kategorie, die Consumer (Print/Shop/Product) über das Assets-Panel browsen.

### 4.2 Page-Schema pro File

Jeder File folgt dem gleichen strukturellen Slot-Schema. Meta-Slots in CAPS (kein Trennzeichen), Content-Pages nummeriert mit Middle Dot:

| Slot | Pflicht | Inhalt |
|---|---|---|
| `INDEX` | ✅ | Navigations-Page. Enthält den File-Cover-Frame (Thumbnail-Instanz aus Core). |
| `01..NN · [Inhalt]` | ✅ | Content-Pages, durchnummeriert, beschreibend benannt |
| `_SANDBOX` | ✅ | Sandbox — kein Library-Publish, keine Token-Disziplin |

**INDEX-Regeln:**
- **TOC-Einträge** sind immer als interne Hyperlinks (`type: NODE`) zu den jeweiligen Content-Pages gesetzt. Bei jeder Änderung an der Page-Struktur (neue Page, Umbenennung, Löschung) werden TOC-Links mitgepflegt.
- **Status-Variant** spiegelt den aktuellen File-Zustand — Umschaltung über die Component-Property `Status` (Draft → Active → Legacy), nicht über Text-Override.
- **Changelog-Versionierung** folgt schlankem SemVer (`MAJOR.MINOR.PATCH`), unabhängig pro File:
  - **MAJOR** — Breaking Change: Component, Token oder Variable umbenannt/entfernt, Struktur geändert — Consumer (Product/Print/Shop) müssen ihre Bindings, Code oder Doku anfassen. Hinweis: Umbenennen bricht in Figma keine Bindungen (Verknüpfung über die ID); es zählt trotzdem als MAJOR, weil Namen in Code, Doku und Skills nachgezogen werden müssen. Echte Brüche sind Löschen, Verschieben in eine andere Collection und Typwechsel.
  - **MINOR** — additiv, non-breaking: neuer Mode, neue Component, neue Variable, neue Page.
  - **PATCH** — Korrektur ohne neue Fähigkeit: Wert-Fix an bestehenden Tokens, Tippfehler, Doku-Korrektur.
  - Startversion pro File: `v1.0`. Jeder `Changelog Entry` = Version-Pill + Date + ≥1 `Changelog Note`; mehrere unabhängige Änderungen am selben Tag werden als mehrere Notes unter einer Version gebündelt, keine künstliche Versionstrennung pro Note. **Eine Version pro File und Tag**, auch bei mehreren Arbeitsschritten. Notes kurz halten: höchstens drei Zeilen, nur was sich für Nutzer des Files ändert; Herleitung und Details gehören ins Konzept, nicht ins Changelog.
  - Neueste Version steht oben (Keep-a-Changelog-Reihenfolge) — analog zur Commit-/Release-Konvention in `global-git-conventions`, hier aber manuell gepflegt statt automatisiert, weil Figma-Changes nicht durch release-please laufen.

### 4.3 Page-Belegung — Source of Truth ist der File-INDEX

Jeder File folgt dem Schema aus §4.2 (`INDEX` + nummerierte Content-Pages + `_SANDBOX`). Die **konkrete, aktuelle Page-Belegung pro File wird hier bewusst nicht gelistet** — sie ist in der ToC des jeweiligen File-`INDEX` gepflegt und dort die einzige Source of Truth. Eine zweite Liste in diesem Doc würde nur driften (Umbenennungen, Reorder, neue Output-Typen landen im File, nicht hier).

**Wer die Pages eines Files braucht, öffnet dessen `INDEX`.** Die ToC-Einträge sind interne NODE-Links auf die Content-Pages (§4.2).

Zwei Belegungs-Prinzipien, die über die reine Liste hinausgehen und stabil gelten:

- **Core ist consumer-focused.** Jede Content-Page ist eine Kategorie im Assets-Panel; Page-Namen beschreiben, was Consumer dort finden (Logos, Icons, Typography, File Meta), nicht dass es „Components" sind — in Core ist alles eine Component.
- **Variables und Text Styles** leben ausschließlich in den Figma-Panels, nie als Canvas-Page.

> Wird ein File neu gebootstrappt, geben das Schema (§4.2) und die Wachstums-Regeln (§5.4) die Struktur vor — eine feste Vorlage-Liste ist dafür nicht nötig.

### 4.4 Library-Publish-Asymmetrie

Nicht alle Pages werden als Figma Library published. Meta-Slots und Output-Pages konsumieren, sind aber selbst kein Library-Content:

| File | Was wird published |
|---|---|
| **Core** | Alle Content-Pages (`01 · Logos` bis `04 · File Meta`) |
| **Product** | Alle Content-Pages (`01 · Product Labels` bis `02 · Pouch Renderings`) |
| **Print** | **Nur** `01 · Components`. Output-Pages (02–06) konsumieren, publishen nicht. |
| **Shop** | **Nur** `01 · Components`. Output-Pages (02–04) konsumieren, publishen nicht. |
| **Sales App** | **Nur** `01 · Components`. Screen-Pages konsumieren, publishen nicht. |

`INDEX` und `_SANDBOX` werden in keinem File published.

### 4.5 Components-Strukturierung (Print & Shop)

Die Component-Pages in Print und Shop (`01 · Components`) enthalten Master auf unterschiedlichen Komplexitätsebenen. Strukturierung über drei benannte Frames innerhalb der Page (keine Sub-Pages, keine eigenen Pages — vgl. §5.6):

```
01 · Components
├── Primitives     – kleinste wiederverwendbare Bausteine
├── Composed       – aus Primitives zusammengesetzte Module
└── Templates      – output-spezifische Layout-Skelette
```

**Core nutzt dieses Schema nicht.** Core organisiert Components über consumer-focused Category-Pages (Logos, Icons, Typography, File Meta) statt über eine einzelne Components-Page mit Frames.

**Abgrenzung der drei Ebenen:**

| Ebene | Definition | Beispiele Print | Beispiele Shop |
|---|---|---|---|
| **Primitives** | Nicht weiter sinnvoll zerlegbar. Bestehen aus Tokens, Text Styles, ggf. einer Form. | Info Box, Price Tier, List Item, Stats, Stat Box, Paragraph, Content Row, QR Code | Buttons, Tags, Pills, Brush Stroke, Heading Bar, Check List Item |
| **Composed** | Aus Primitives zusammengesetzt, aber noch generisch und mehrfach kombinierbar. | Icon Row, Highlight Box, Headline + Text, List | Info Card, Mood Card, Origin Card, Review Card, Product Card |
| **Templates** | Output-spezifisches Layout-Skelett, das eine ganze Druckseite oder Sektion strukturiert. | Vein-Seitenlayout, Produktseiten-Layout, Katalog-Cover, Preisliste-Header, Flyer-Master (Wickelfalz), Sticker-Template, POS-Template | Marketing-Banner-Skelett, Product-Detail-Section, Category-Card-Layout |

**Faustregel Template vs. Output:**

- **Mehrfache Instanz** im Output → **Master in Templates** (z.B. Vein-Seitenlayout wird 9× verwendet).
- **Einmalige Verwendung** → direkt im Output-File ohne Master (z.B. Katalog-Backcover, nur einmal existent).

**Bilder und SVG-Assets** folgen derselben Primitives-/Composed-Logik:

- **Wird 3+ Mal in einem File konsumiert** → Component in `01 · Components / Primitives` (z.B. wiederkehrende Print-Textur, Marketing-Bild für mehrere Banner)
- **Cross-File-Konsum** (Print + Shop) → eine Schicht tiefer in Product oder Core (gilt automatisch via §5.2 Single Source of Truth)
- **1–2 Mal verwendet** → direkt im Frame eingebettet, kein Master
- **Logos, Icons, Product Labels, Pouch Renderings** → bleiben in den dedizierten Core- und Product-Pages

Keine eigene "Bildverwaltungs-Page" — sonst werden Library-Files träge.

**Skalierung:** Wenn ein Frame (z.B. Templates) so umfangreich wird, dass er nicht mehr überblickbar ist, splitten in **Geschwister-Pages**:

```
01 · Primitives & Composed
02 · Templates
03 · Katalog A4         (Output-Pages wandern weiter)
...
```

Erst splitten, wenn der Schmerz real ist — nicht prophylaktisch.

---

## 5. Governance

Regeln, die das System skalierbar halten — gelten bei jeder Änderung an Files, Pages oder Components.

### 5.1 Dependency-Direction

Files konsumieren nur **abwärts** in der Hierarchie:

```
Core → Product → Print
              ↘ Shop
```

- Print bindet nicht Shop, Shop bindet nicht Print.
- Wird ein Asset von beiden gebraucht → er gehört in Product oder Core.
- Zirkuläre Bindings sind verboten.

### 5.2 Single Source of Truth

Jeder Asset existiert als Master genau einmal. Wird er von 2+ Files konsumiert → er wandert in den **niedrigsten gemeinsamen File** (eine Schicht tiefer).

Beispiel: Pouch-Renderings werden vom Katalog (Print) und Shop-Produktbildern (Shop) konsumiert → Master in Product, nicht doppelt gepflegt.

### 5.3 Component-Promotion-Pfad

Components durchlaufen drei Stufen:

1. **Experiment** — in `_SANDBOX` der jeweiligen File. Kein Library-Publish, keine Token-Disziplin verpflichtend.
2. **Promotion zur Library** — wird die Component 3+ Mal gebraucht, wandert sie aus `_SANDBOX` in die entsprechende Content-Page (mit voller Token-Disziplin und Einsortierung in Primitives/Composed/Templates, siehe §4.5).
3. **Cross-Konsum-Promotion** — wird sie von einem zweiten File konsumiert, wandert sie eine Schicht tiefer (z.B. von Shop in Product).

### 5.4 Wachstum: Neue Page oder neuer File?

**Neue Page** (im bestehenden File):
- Neuer Output-Typ in existierender Domain (z.B. Visitenkarten → neue Page in Print)
- Neue Component-Familie für existierende Library (z.B. Email-Buttons → neue Page in Shop)
- Mehr Variants in bestehender Page

**Neuer File**:
- Neue Master-Domain mit eigener Verantwortung (z.B. Motion, Email-Templates, Brand Photography)
- Bestehender File überfüllt (500+ Variants oder spürbar langsam)
- Update-Frequenzen innerhalb eines Files divergieren stark
- Performance-Limit erreicht

**Anti-Pattern**: Neuer File "wegen Aufgeräumtheit" — das ist Disziplinverschiebung, kein echter Trigger.

### 5.5 Hierarchie-Einhängung neuer Files

Wenn ein neuer File entsteht, hängt er sich nach Master/Consumer-Pfad ein:

| Layer | Charakter | Beispiele |
|---|---|---|
| **Layer 2 — Brand-Master** | Cross-konsumiert von mehreren Output-Files | Brand Photography (Pflanzen-Fotografie, Lifestyle-Bilder) |
| **Layer 3/4 — Output-Channel** | Eigene Output-Form, parallel zu Print/Shop | Motion, Email-Templates, OOH-Werbung |

Niemals Cross-Binding zwischen gleichrangigen Files. Wenn das nötig wäre, gehört der gemeinsame Asset eine Schicht tiefer.

### 5.6 Sub-Pages

Figma hat keine echten Sub-Pages, nur Pages und Frames innerhalb. **Keine hierarchischen Page-Splits** wie `05.1 · Components/UI`, `05.2 · Components/Layout` — sie bringen Solo-Op-Overhead ohne Gewinn.

Wird eine Page zu groß: als **Geschwister-Page** splitten (durchnummeriert weiter), nicht als Eltern-Kind. Strukturierung innerhalb einer Page über benannte Frames (`Primitives`, `Composed`, `Templates` in Component-Pages — vgl. §4.5).

### 5.7 Versionierung

Drei unterschiedliche Ebenen — pragmatische Regel pro Ebene:

| Ebene | Bedeutung | Lösung |
|---|---|---|
| **Component-Versionierung** | "Button v1, Button v2" als parallele Masters | **Overkill.** Figma's eingebaute Version History reicht. Breaking Changes über neue Variant-Property, nicht über `v2`-Component. |
| **Branch-basierte Versionierung** | Feature-Branches in Figma (Professional/Org-Plans) | **Optional**, nicht Standard für Solo-Op. Nur wenn parallel an größeren Refactorings gearbeitet wird. |
| **Output-Versionierung** | "Katalog 2025 vs Katalog 2026" als unterschiedliche Druckläufe | **Üblich, geregelt.** Siehe unten. |

**Output-Versionierung — Standard-Vorgehen:**

- **Aktive Version** lebt in der Output-Page (z.B. `Print/02 · Katalog A4`). Immer nur eine aktive Version pro Output.
- **Snapshots fertiger Druckläufe** über Figma's Version History benennen: `2026-Q1 · Katalog v1.0 final`, `2026-Q2 · Katalog v1.1 Reprint`. Kostet keinen Page-Slot, ist suchbar.
- **Längerfristige Archive** (z.B. wenn 2025er Katalog als Referenz gebraucht wird) → entweder benannter Version-History-Snapshot oder als Backup-Frame in `_SANDBOX` ablegen.
- **Keine reinen Archive-Files** anlegen. Die Erfahrung zeigt: Archive-Files verkrusten, werden nicht gepflegt, sammeln veraltete Bindings. Stattdessen Version History nutzen.

---

## 6. Decision Tree: Variable vs Style vs Component

| Frage | Antwort |
|---|---|
| Wert mehrfach in einem System gebraucht (Farbe, Größe, Abstand, Radius)? | **Variable** (Rolle oder Kontext; neuer Rohwert in die Palette, gebunden wird die Rolle) |
| Typografie-Set (Font + Size + Weight + LH + LS) mehrfach verwendet? | **Text Style** |
| UI-Bestandteil mehrfach komponiert (Layer + Variables + Styles zusammen, evtl. mit States)? | **Component mit Variants** |
| Wert einmalig, ohne semantische Wiederverwendung? | Direkt im Frame, **kein** Token. |
| Token gibt es noch nicht, würde aber gebraucht? | Erst Variable/Style/Component anlegen, dann verwenden. |

**Entscheidungsfälle pro Element-Typ:**
- Brand-Farbe, Spacing-Stufe, Border-Radius-Stufe → **Variable**.
- Headline H1, Body-Text, Label, Eyebrow → **Text Style**.
- Button mit Hover/Disabled-States, Card mit Vein-Variants, Price-Pill → **Component mit Variants**.
- Section-Padding, das pro Print-Format anders ist → **Layout-Variable mit Modes** (kein Duplicate).
- "Sieht-gut-aus"-Wert wie Margin 23 px → falsch. Entweder bestehende Variable nutzen oder neue anlegen.

---

## 7. Druck und Source of Truth

- **Print-Export:** Frame als PDF aus Figma exportieren → direkt bei der Druckerei hochladen. Kein Post-Processing nötig — native Frames liefern die korrekte Seitengröße. `figma_print_fix.py` nur als optionaler Fallback, falls ein *gedrucktes* Ergebnis durch Figmas Bildkompression weich wirkt.
- **Onlineprinters-Druckvorlagen (Dielines):** Ingestion (PDF → bereinigtes SVG → Skalierung → Bereinigung), Component-/Slot-Struktur und Component-Description-Schema sind im Skill `figma-onlineprinters` geregelt — dort liegt auch `clean_dieline.py`. Kurzform: point-basierte PDFs sind `1 pt = 1 px` (kein ×0,75); Source = Druckvorlage-PDF im Description-Text, Produktseite gehört ins native `documentationLinks`-Feld. Druckmaße (`bleed`, `size/data/*`) liegen in der Print-lokalen Sammlung `Onlineprinters`.
- **"Print for Figma" Plugin**: ausschließlich DIN-Presets verwenden. Custom-Format hat einen Plugin-Bug (Pixel werden 1:1 als Points geschrieben → falsche Seitengröße).
- **Source of Truth: Core führt.** Farb-, Größen- und Schrift-Tokens entstehen in Core (Variablen, Text Styles). Das Shopify-Theme (LIFTR: `assets/core.base.css`, Farbschema in `snippets/core.critical.liquid`) ist eine Übergangslösung und zieht nach (todos.md TODO-044 im Projekt selectedleafs.com); die Code-Namen in Core nennen die Theme-Variablen. Weichen Theme und Core voneinander ab, wird das Theme angepasst. Die Kopplung der Layout-Modes Desktop/Mobile an die clamp-Grenzen (§2) beschreibt den heutigen Stand; neue Werte entstehen in Core.
