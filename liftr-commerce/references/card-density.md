# LIFTR Card Density System

**Normatives Framework** für konsistentes Density-Verhalten über alle Card-Typen.

**Prerequisite:** `card-architecture.md` (Golden Ratio, margin-based spacing, Layouts, Density Scaling Priority, Selector Strategy, Min-Width Floor).

**Zweck:** Wenn verschiedene Card-Typen auf derselben Seite stehen, sollen sie bei gleicher Breite dieselben Density-Entscheidungen treffen — gleiche Spacing-Stufen, gleiche Visibility-Logik, gleiche Font-Reduktion. Dieses System ist die verbindliche Referenz dafür.

---

## Element-Taxonomie (P1–P4)

Jedes Element einer Card bekommt eine Prioritätsstufe. Die Stufe bestimmt, ab welcher Density-Range es ausgeblendet wird.

| Prio | Name | Regel | Sichtbar bis |
|------|------|-------|-------------|
| **P1** | Identität | Macht die Card erkennbar. Ohne P1 ist sie sinnlos. | Immer |
| **P2** | Entscheidung | Hilft bei Bewertung oder Auswahl. | Bis D2, weg ab D3 |
| **P3** | Kontext | Ergänzende Info. Nicht entscheidungskritisch. | Bis D1, weg ab D2 |
| **P4** | Komfort | Nice-to-have bei genug Platz. | Weg ab D1 |

### Regeln

1. **Media/Bild = immer P1.** Wird nie ausgeblendet. Bei D3: Margin reduziert (`--space--xxsmall`).
2. **Badges auf Bild** (position: absolute über Media): **P3-exempt.** Sie belegen keinen vertikalen Platz im Content-Bereich. Ausgeblendet erst bei D3, wenn sie zu viel Image verdecken.
3. **Innerhalb einer Prio-Stufe:** Das platzintensivere Element geht zuerst.
4. **Self-contained Children** (z.B. store-info, rating) verwalten ihre interne Density selbst. Card-Density steuert nur **ob** das Kind sichtbar ist — nie **wie** es sich darstellt.
5. **Rating hat Sonderstatus:** P2, aber wird bei Product Cards **nie vollständig ausgeblendet** (Social Proof > Platz). Stattdessen shrink via CSS API (`--rating--icon-size` etc.) bevor Removal in Betracht kommt.

### Referenz-Mapping

**Product Card:**

| Element | Prio | Notizen |
|---------|------|---------|
| Image | P1 | |
| Titel | P1 | Font shrinks D2, Floor D3 |
| Preis (inkl. Compare, Unit) | P1 | Swap body→footer bei D2-b-H / D3-V |
| ATC Button | P1 | |
| Rating | P2★ | Nie hidden — shrink via CSS API bei D2-b-H |
| Description | P3a | Geht zuerst (platzintensiver) |
| Stock Indicator | P3b | |
| Badges (auf Bild) | P3-exempt | Hidden bei D3 |

**Store Card:**

| Element | Prio | Notizen |
|---------|------|---------|
| Image | P1 | |
| Name | P1 | Font shrinks D2, Floor D3 |
| Rating | P2 | Shrink bei D2, hidden bei extremem D3 |
| Store Info (Opening, Adresse, Distanz) | P2 | Self-contained CQs. Hidden bei D3. |
| Actions (Route, Phone) | P3a | Erreichbar über Panel |
| Highlights (Badge-Scroll) | P3b | |
| District | P4 | |

---

## Density-Ranges (D0–D3)

**Ranges, nicht einzelne Breakpoints.** Jede Range enthält 1–3 CQ-Steps. Die Steps innerhalb einer Range folgen der Density Scaling Priority (`card-architecture.md`): Spacing → Redundant Info → Actions → Font → Partial Content → Whole Components.

### D0 — Normal

Alles sichtbar, Standard-Tokens.

| Property | Wert |
|----------|------|
| Sichtbar | P1 + P2 + P3 + P4 |
| Body margin | `--space--small` |
| Body gap | `--space--small` (Product) / `--space--xsmall` (Store) |
| Image margin | `--space--xsmall` |
| Titel font | `--font-size--large` |
| Description | `--text-clamp: 2` (vertikal) / `1` (horizontal) |

### D1 — Compact

Spacing tightens, P4 weg, P3 teilweise weg.

| Property | Wert |
|----------|------|
| Sichtbar | P1 + P2 + P3 (teilweise) |
| Body margin | → `--space--xsmall` |
| Body gap | → `--space--xsmall` |
| Titel font | Keine Änderung |
| Description | Clamp reduziert, dann hidden |

**Sequenz innerhalb D1:**
1. Spacing tightens (margin/padding → xsmall)
2. Description-Clamp reduziert (horizontal: 2→1)
3. Gap tightens
4. P4 hidden (District etc.)
5. Description fully hidden

### D2 — Minimal

P3 weg, Fonts schrumpfen.

| Property | Wert |
|----------|------|
| Sichtbar | P1 + P2 |
| Body gap | → `--space--xxsmall` |
| Titel font | → `--font-size--medium` |
| Rating | Shrunk via CSS API |
| P3 Elemente | Hidden (Actions, Stock, Highlights, Description) |
| Price Swap | Body → Footer (horizontal) |

### D3 — Essential

Nur P1, absolute Floors.

| Property | Wert |
|----------|------|
| Sichtbar | P1 only |
| Titel font | → `--font-size--regular` (Floor) |
| Image margin | → `--space--xxsmall` |
| Body gap | → `0px` |
| Body margin | → `--space--xxsmall` (extreme) |
| P2 Elemente | Hidden (Store-Info, ggf. Rating) |
| Badges auf Bild | Hidden |

---

## Token-Wechsel-Tabelle

Immer ein kleineres Token wählen — nie Token-Werte manipulieren. **Kein `calc()` auf Spacing-Tokens.** Wenn `calc(var(--space--xsmall)*2)` nötig scheint, wähle stattdessen `--space--small`.

### Spacing

| Property | D0 | D1 | D2 | D3 |
|----------|----|----|----|----|
| Body margin | `--space--small` | `--space--xsmall` | `--space--xsmall` | `--space--xsmall` → `--space--xxsmall`¹ |
| Body gap | `--space--small` | `--space--xsmall` | `--space--xxsmall` | `--space--xxsmall` → `0px`¹ |
| Image margin | `--space--xsmall` | `--space--xsmall` | `--space--xsmall` | `--space--xxsmall` |
| Info/Header gap | `--space--xsmall` | `--space--xsmall` | `0px` | `0px` |

¹ D3 kann 2 Steps haben: D3-a (standard floors) und D3-b (extreme floors für forced horizontal). D3-b nur wenn min-width Floor definiert ist.

### Typografie

| Property | D0 | D1 | D2 | D3 |
|----------|----|----|----|----|
| Titel | `--font-size--large` | `--font-size--large` | `--font-size--medium` | `--font-size--regular` |
| Rating Icon | base (`0.875rem`/`0.75rem`) | unchanged | `0.625rem` | `0.625rem` or hidden |
| Rating Font | `--font-size--small` | unchanged | `--font-size--tiny` | `--font-size--tiny` |

### Monotonie-Regel

Jede Property darf nur **monoton abnehmen** über die Density-Ranges. Oszillation (Wert hoch, dann runter, dann hoch) ist verboten.

```
[x]  small → xsmall → xsmall → xxsmall    (monoton)
[!]  xsmall → small → xsmall → small       (Oszillation)
```

---

## Absolute Floors

Diese Werte werden bei keiner Density unterschritten.

| Property | Floor | Begründung |
|----------|-------|------------|
| Body margin/padding | `--space--xxsmall` (0.25rem) | Absolute Untergrenze bei D3-b |
| Image margin | `--space--xxsmall` (0.25rem) | Sichtbare Trennung |
| Titel font-size | `--font-size--regular` (~0.94rem) | Darunter unleserlich |
| Touch Targets | `2.75rem` (44px) | WCAG / Apple HIG |
| Gap | `0px` erlaubt | Elemente berühren sich, bleiben lesbar |
| line-height | Nie ändern | Lesbarkeit |
| border-radius | Nie ändern | Visuelle Identität |
| Icon-Größen in Touch Targets | Nie ändern | Usability |
| Farben/Kontraste | Nie ändern | Accessibility |

---

## Trigger-Breakpoints

Zwei getrennte Breakpoint-Sätze. Horizontal reduziert **früher** (weniger Platz neben Media). Vertikal reduziert **später** (volle Breite).

### Referenz-Ranges

Ziel-Bereiche. Card-spezifische Breakpoints innerhalb der Range werden gegen Live-Content kalibriert. Abweichung ±2rem erlaubt wenn dokumentiert.

**Horizontal:**

| Übergang | Bereich | Was passiert |
|----------|---------|-------------|
| D0→D1 | ≤44rem → ≤34rem | Spacing tightens, P4 weg, Description weg |
| D1→D2 | ≤28rem → ≤26rem | P3 weg (Stock), Fonts shrink, Price Swap, Rating shrunk |
| D2→D3 | ≤21rem → ≤18rem | Badges weg, Floors, extreme spacing |

**Vertikal:**

| Übergang | Bereich | Was passiert |
|----------|---------|-------------|
| D0→D1 | ≤24rem → ≤16rem | Spacing tightens, Description weg |
| D1→D2 | ≤16rem → ≤14rem | Actions/Highlights weg, Fonts shrink |
| D2→D3 | ≤12rem → ≤8rem | Badges weg, Store-Info weg, Floors |

### Max CQ-Steps pro Range

| Range | Horizontal max | Vertikal max |
|-------|---------------|-------------|
| D1 | 3 Steps | 2 Steps |
| D2 | 2 Steps | 1 Step |
| D3 | 2 Steps | 1–2 Steps |
| **Gesamt** | **≤ 7** | **≤ 5** |

---

## Auto-Flip

Der Flip von horizontal zu vertikal ist ein **Layout-Event**, kein Density-Event. Er läuft parallel zum Density-System.

### Trigger

Auto-Flip feuert, wenn horizontal D1 keine visuelle Balance mehr hat — Content-Seite zu dünn neben Media. Typisch an der D1→D2 Grenze.

| Card | Flip-Punkt |
|------|-----------|
| Product | ≤34rem |
| Store | ≤34rem |

### Verhalten nach Flip

**Density-Reset auf D0-vertikal.** Die Card hat nach dem Flip die volle Container-Breite → fällt auf D0 zurück. Vertikale D-Stufen übernehmen von dort.

### Selektoren

> **Selektor-Tabelle → `card-architecture.md` (Selector Strategy).** 5 Patterns mit Anwendungskontext — nur dort gepflegt.

### Flip-CQ Anforderungen

Der Flip-CQ muss:
1. Layout switchen (grid → flex, aspect-ratio → unset)
2. Alle H-Density-Werte auf D0-vertikal zurücksetzen (margin, gap, padding-top, desc clamp)
3. Vertical-Body-Verhalten setzen (`justify-content: space-between`)
4. `margin-top: auto` auf info/footer zurücksetzen (`margin-top: 0`)

```css
@container (max-width: 34rem) {
  ._component.is-auto {
    display: flex;
    flex-direction: column;
    aspect-ratio: unset;
  }
  ._component.is-auto ._body {
    margin: var(--space--small);       /* Reset auf D0 */
    padding-top: 0;                    /* Vertical: kein padding-top */
    gap: var(--space--small);          /* Reset auf D0 */
    justify-content: space-between;    /* Vertical-Verhalten */
  }
  ._component.is-auto ._info { margin-top: 0; }
  ._component.is-auto .footer { margin-top: 0; }
  ._component.is-auto ._description { --text-clamp: 2; }
}
```

---

## Verbotene Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Wert-Oszillation (↑↓↑) | Unvorhersehbar, schwer debuggbar | Jede Property nimmt monoton ab |
| `calc()` auf Spacing-Tokens | Bricht das Token-System | Passendes Token wählen |
| >3 Werte pro Property | Über-optimiert, fragil | Max 3: D0, D1/D2, D3 (Ausnahme: D3-b für extreme floors) |
| Reset innerhalb einer Range | Widersprüchliche CQs | Jeder CQ setzt den finalen Wert |
| In Self-contained Children eingreifen | Verantwortungsverletzung | Card steuert Visibility, Kind steuert Internals |
| Endlos weiter reduzieren unter min-width | Layout bricht physisch | `min-width` auf forced horizontal setzen |

---

## CSS-Organisation

### Datei-Struktur

```css
/* ── Component ── */
._component { /* D0 Base */ }
._component.is-vertical ._body { /* Vertical overrides */ }

/* ── Density — Horizontal ── */
/* -- D1 -- */
@container (max-width: ...rem) { /* :not(.is-vertical) */ }
/* -- D2 -- */
@container (max-width: ...rem) { /* .is-horizontal */ }
/* -- D3 -- */
@container (max-width: ...rem) { /* .is-horizontal */ }

/* ── Auto — CQ Flip ── */
@container (max-width: 34rem) { /* .is-auto — Flip + Reset */ }

/* ── Density — Vertical + Auto ── */
/* -- D1 -- */
@container (max-width: ...rem) { /* :not(.is-horizontal) */ }
/* -- D2 -- */
@container (max-width: ...rem) { /* :not(.is-horizontal) */ }
/* -- D3 -- */
@container (max-width: ...rem) { /* :not(.is-horizontal) */ }
```

### Kommentare

Jede Density-Range bekommt einen Block-Kommentar der die Änderungen auflistet:

```css
/*
 * D1 (≤44rem → ≤34rem): Spacing tightened, description hidden
 * D2 (≤28rem → ≤26rem): P3 hidden (stock), title → medium, price swap, rating shrunk
 * D3 (≤21rem → ≤18rem): Badges hidden, floors reached, extreme spacing
 */
```

---

## Checkliste: Neue Card

### 1. Elemente klassifizieren (P1–P4)

- [ ] Alle sichtbaren Elemente identifizieren
- [ ] P1 zuweisen (Image, Titel, Primary Action, Preis)
- [ ] P2 zuweisen (Rating, Key Info, Secondary Action)
- [ ] P3 zuweisen (Description, Badges, Supplementary)
- [ ] P4 zuweisen (District, Meta, Dekorativ)
- [ ] Im CSS-Docblock dokumentieren

### 2. Token-Shifts definieren

- [ ] D0-Tokens aus Base-Styles ableiten
- [ ] D1: Spacing eine Stufe runter, Fonts unverändert
- [ ] D2: Floor-Spacing, Fonts shrink
- [ ] D3: Absolute Floors (ggf. D3-b für extreme floors)
- [ ] Monotonie prüfen (kein Wert oszilliert)
- [ ] Floors prüfen

### 3. Breakpoints setzen

- [ ] Referenz-Ranges als Ausgangspunkt
- [ ] Gegen realen Card-Content kalibrieren (deploy + messen)
- [ ] Horizontal: max 7 CQ-Steps gesamt
- [ ] Vertikal: max 5 CQ-Steps gesamt
- [ ] Abweichungen von Referenz-Ranges dokumentieren
- [ ] Min-width Floor für forced horizontal definieren

### 4. Auto-Flip implementieren

- [ ] Flip-Punkt an D1→D2 Grenze
- [ ] Flip-CQ verwendet `.is-auto` Selektor (→ `card-architecture.md` Selector Strategy)
- [ ] Flip-CQ setzt alle H-Density-Änderungen auf D0-vertikal zurück
- [ ] Flip-CQ setzt `justify-content: space-between` + `margin-top: 0`
- [ ] V-Stufen verwenden `:not(.is-horizontal)`

### 5. Verifizieren

- [ ] Legal Constraints (Unit Price nie hidden)
- [ ] Touch Targets ≥ 44px bei allen Densities
- [ ] Self-contained Children nicht angefasst
- [ ] Kein `display` auf `[liftr-role]` Elementen
- [ ] Rating shrunk before hidden (wo anwendbar)
- [ ] Price Swap funktioniert bei D2/D3
- [ ] Min-width Floor verhindert Layout-Bruch

---

## Skill-Beziehungen

| Skill | Liefert | Dieser Skill ergänzt |
|-------|---------|---------------------|
| **`card-architecture.md`** | Golden Ratio, Margin-based, Layouts, Scaling Priority (Aktionsreihenfolge), Selector Strategy (5 Patterns), Min-Width Floor, Extension API, Price Swap | Element-Taxonomie (P1–P4), Density-Ranges (D0–D3), Token-Wechsel, Floors, Trigger-Breakpoints |
| **`css-system.md` (liftr-foundation)** | Token-Scale, CQ-Patterns, Selektor-Regeln | Density-spezifische Token-Shifts, CQ-Organisations-Pattern |
