---
name: selectedleafs-figma
description: "Regeln für alle selectedleafs-Figma-Dateien (Core, Product, Print, Sales App, künftig Shop): Variablen-Architektur Palette → Color Scheme → Kontext, Bindungsregel, Modi (Layout-Formate, White/Forest/Cream) mit Modus-Regel, Namens- und Seitenschema, Changelog, Governance, Audit R1–R6, Figma-MCP-Lehren und Font-Awesome-Icon-Pipeline. IMMER laden, bevor in einer selectedleafs-Figma-Datei etwas gebaut, geändert, umgebunden, geprüft oder veröffentlicht wird, auch ohne das Wort Skill. Trigger u. a.: Figma, Core-Library, Variablen, Tokens, Rollen, color/scheme, color/global, Palette, Farbmodus, Color Scheme, Layout-Modus, DIN A4, Text Styles, Changelog, INDEX, Components-Seite, Library veröffentlichen oder annehmen, alte Kopie, Audit, Icons, Font Awesome, use_figma in Core, Print, Product oder Sales App. Abgrenzung: Druckvorlagen → figma-onlineprinters, Demos/Artifacts → selectedleafs-brand, Plugin-API → figma-use."
metadata:
  version: "1.0.0"
---

# selectedleafs-figma

Die eine Quelle der Figma-Regeln für selectedleafs. Gilt in allen Projekten. Werte (Farben, Größen, Abstände, Radien) stehen in den Variablen und Text Styles der Dateien, nicht hier. Hier stehen die Muster, Regeln und Konventionen, die über alle Chats hinweg gelten.

## Abgrenzung

| Aufgabe | Skill |
|---|---|
| Regeln, Variablen, Struktur, Audit in selectedleafs-Figma-Dateien | dieser |
| Onlineprinters-Druckvorlagen (Dielines, Print-Template-Components) | figma-onlineprinters (Prozess; bei Konflikt gewinnt dieser Skill) |
| React-/HTML-Demos und Artifacts im Markenlook | selectedleafs-brand |
| Plugin-API und `use_figma`-Aufrufe | figma-use (vor jedem `use_figma` laden) |

## Dateien und Hierarchie

| Datei | Schicht | Inhalt | fileKey (nur für Tools) |
|---|---|---|---|
| Core | 1 | Library: Logos, Icons, Typography, File Meta; Variablen und Text Styles nur im Panel | `klq8Vd9FAzzWzKGNri9naw` |
| Product | 2 | Product Labels, Pouch Renderings | `kg9czL1RUVaeIatW5coer2` |
| Print | 3 | Druck: Components und Outputs | `IPEk40v01EMVITXst3UPOT` |
| Sales App | 3 | Vertriebler-App: Components und Screens | `1o41LEjMxSp0aHNOgVcOQJ` |
| Shop | 3 | geplant, startet auf der aktuellen Core-Version | – |

- Konsum nur abwärts: Core → Product → Print · Shop · Sales App. Gleichrangige Dateien binden sich nie gegenseitig. Was zwei Dateien brauchen, liegt eine Schicht tiefer (Single Source of Truth).
- **Core führt.** Farb-, Größen- und Schrift-Tokens entstehen in Core. Das Shopify-Theme (LIFTR) zieht nach; weichen Theme und Core ab, wird das Theme angepasst. Code-Namen in Core nennen die Theme-Variablen.
- Eine Marke. Die Dateien dienen nur selectedleafs, es gibt keine Marken-Achse.
- Seiten je Datei: `INDEX` · `01 · …` bis `NN · …` · `_SANDBOX`. Print, Shop und Sales App veröffentlichen nur `01 · Components` (Frames Primitives, Composed, Templates).

## Bindungsregel

Drei Ebenen:
- **Palette** — Rohwerte, ein Modus, verborgen, ohne Farb-Scopes. Veröffentlicht sind nur `font-family/*` (für die Text Styles).
- **Rollen** (`Color Scheme`) — Fläche, Inhalt, Akzent, Zustände, `color/global/*`, Overlay, Deckkraft. Werte nur als Alias auf die Palette.
- **Kontext** — `Layout`, `Variety`, `Price Tier`, `Employee`.

**Ebenen binden nur Rollen oder Kontext — nie die Palette, nie feste Werte.** Typografie nur über Text Styles. Festgelegte Ausnahmen stehen in `references/audit.md`.

- Neue Rolle nur, wenn das Theme sie hat oder als geplante Theme-Rolle aufnimmt **und** mindestens eine Datei sie braucht. Keine Tokens je Baustein. Ein neuer Rohwert kommt in die Palette, gebunden wird die Rolle.
- Pflichtangaben je Variable: Scopes (nie `ALL_SCOPES`, außer boolesche Variablen), Beschreibung, Code-Name, wo das Theme eine CSS-Variable hat.

## Modi

- **Layout** (7 Modi): Desktop, Mobile, DIN A2, DIN A3, DIN A4, DIN A5, `DIN A6 · DIN Lang`. Print skaliert von A4 aus mit √2 je A-Stufe (Regeln in `references/standards.md` §2).
- **Color Scheme** nach der Fläche: `White` (Standard, hell), `Forest` (dunkel; ein „Dark Mode“ ist ein Frame auf Forest), `Cream` (Creme-Flächen in Print).
- Jeder oberste Rahmen setzt seine Modi explizit, auch der Rahmen einer Components-Seite (`White`).
- **Modus-Regel:** Eine farbige Rolle bleibt in allen Modi in ihrer Farbfamilie der Palette; je Modus wechselt nur die Stufe. Ausgenommen sind `background`, `card`, `grey`, `text`, `icon`, `border`, `disabled`, `disabled-text`.
- Status und Highlights (`color/global/*`) sind modusfrei. Farbige Flächen binden Fläche und `-text` und setzen keinen eigenen Modus.
- Keine Varianten für die Fläche; die Fläche kommt über den Modus. Bausteine mit fester Fläche setzen ihren Modus selbst. Modi an Exemplaren gezielt setzen, nie pauschal löschen.

## Namen

- Tokens: Slash-Hierarchie, lowercase-kebab, Singular. Rollen und Kontext mit Wortnamen nach dem Theme (`color/scheme/link` ↔ `--color-scheme--link`).
- Palette nach Helligkeit: `color/<farbton>/<stufe>`, Stufe = L* (CIELAB) auf 5 gerundet; Alpha-Stufen als Suffix (`color/neutral/5-a10`).
- Text Styles ohne `font/`-Prefix (`heading/h1`, `body/regular`).
- Seiten: Meta-Slots in CAPS (`INDEX`, `_SANDBOX`), Content-Pages `01 · Title Case`.
- Inhalte in Figma auf Englisch, Prozess-Dokumente auf Deutsch.

## Changelog

- SemVer je Datei: **MAJOR** = Umbenennen, Entfernen, Struktur (Konsumenten ziehen nach) · **MINOR** = additiv · **PATCH** = Korrektur.
- **Eine Version pro Datei und Tag**, auch bei mehreren Arbeitsschritten. Notes höchstens drei Zeilen, nur was sich für Nutzer der Datei ändert; neueste Version oben.
- Veröffentlichen und Update annehmen macht Joscha von Hand.

## Checkliste vor dem Bauen

1. figma-use laden; `create_session` mit dem fileKey der Datei.
2. Ist das letzte Core-Update in der Datei angenommen? Sonst zuerst annehmen lassen (alte Kopien, Audit R4/R5).
3. Je Seite ein eigener Aufruf mit `setCurrentPageAsync`. Variablen frisch aus einer bestehenden Bindung holen oder per `importVariableByKeyAsync` im selben Aufruf binden (`references/mcp.md`).
4. Nur Rollen und Kontext binden, Schrift über Text Styles, Größen aus `Layout`. Die Marke gewinnt: keine neuen Tokens, nur um Wireframe-Werte zu treffen.
5. Oberste Rahmen: Layout- und Color-Scheme-Modus explizit setzen.
6. Vor einem Umbau die Ausgangswerte sichern; danach Wertabgleich je Ebene, auch auf der Components-Seite und an Exemplaren in anderer Umgebung (`references/audit.md`).
7. Entwürfe mit echten Namen aus Airtable (Stores, Vertriebler), ohne nachzufragen.
8. Zum Schluss Audit R1–R5 (Core zusätzlich R6) und ein Changelog-Eintrag.
9. Rückmeldung an Joscha mit Namen (Datei, Seite, Rahmen, Baustein, Variable), nie mit Node-, Variablen- oder Datei-IDs als Referenz.

## Referenzen

- `references/standards.md` — Volltext der Regeln: Token-Disziplin, Modes und Skalierung, Naming, File-Struktur, Governance, Entscheidungsbaum, Druck. Bei Zweifel gilt der Volltext.
- `references/rollen-und-palette.md` — Ebenen-Regeln, Palette, alle Rollen mit Alias je Modus, Kontext-Sammlungen, alte Namen.
- `references/audit.md` — Audit R1–R6 und W1: Ablauf, festgelegte Ausnahmen, Wertabgleich, Ausgabe.
- `references/mcp.md` — was das Figma-MCP kann und nicht kann, Lehren aus den Umbauten.
- `references/icons.md` — Font-Awesome-Pipeline für Core › Icons.
- Herleitung und Entscheidungsprotokoll (Archiv, keine Regelquelle): Projekt „selectedleafs.com“, `claude/figma-variablen-architektur.md`.

## Pflege

Änderungen an diesem Skill nur, wenn die Library tatsächlich anders gepflegt wird als beschrieben, nicht für temporäre Zustände. Punktuelle Stände („Page X hat noch manuelle Text-Styles“) gehören in `todos.md` oder den Chat. Neue MCP-Lehren kommen in `references/mcp.md`.
