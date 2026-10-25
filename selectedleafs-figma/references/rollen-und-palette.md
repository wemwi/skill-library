# Rollen und Palette

Ebenen, Palette, Rollen und Kontext-Sammlungen in Core. Die Tabellen spiegeln Core; bei Abweichung gilt Core. Vor Änderungen an Variablen Core live lesen.

## Inhalt
1. Ebenen und Regeln
2. Modi von Color Scheme
3. Palette
4. Rollen (Color Scheme)
5. Kontext
6. Alte Namen

---

## 1. Ebenen und Regeln

| Ebene | Sammlung | Modi | Wer bindet | Werte |
|---|---|---|---|---|
| **Palette** | `Palette` | 1: `selectedleafs` | niemand außer Core-Text-Styles (Schrift) | Rohwerte; Markenslots tragen den Code-Namen |
| **Rollen** | `Color Scheme` | `White` · `Forest` · `Cream` | alle Dateien | nur Alias auf Palette (Ausnahme: `icon` → `text`, gleiche Sammlung) |
| **Kontext** | `Layout`, `Variety`, `Price Tier`, `Employee` | je Achse | alle Dateien | Farben nur Alias auf Palette; Größen/Texte direkt |

Regeln:
1. **Bindung:** Ebenen binden nur Rollen oder Kontext. Nie Palette, nie feste Werte. Ausnahmen in `audit.md`.
2. **Rollen aliasieren die Palette.** Mischfarben (Rahmen, Grau, Overlay) liegen als eigene Alpha-Stufen in der Palette, weil Figma „Alias + Deckkraft“ nicht kann. So stehen alle Rohwerte an einer Stelle.
3. **Neue Rolle nur, wenn** das Theme sie hat oder als geplante Theme-Rolle aufnimmt (TODO-044) **und** sie in mindestens einer Datei gebraucht wird. Kein Token je Baustein.
4. **Status- und Highlight-Farben sind modusfrei** (wie `--color-global--*` im Theme) und liegen trotzdem in `Color Scheme`, damit Dateien nur eine Rollen-Sammlung kennen. Jede gefüllte Rolle hat eine eigene Textfarbe `-text`. Ein Tag erzwingt deshalb keinen eigenen Farbmodus.
5. **Verläufe:** Figma-Variablen halten keine Verläufe. Grundrolle = Startfarbe bzw. Vollfarbe; `-end` (und bei Gold `-start`) nur dort anlegen, wo ein Baustein den Verlauf zeigt.
6. **Palette verborgen:** `hiddenFromPublishing` für alle Palette-Variablen außer `font-family/*` (die Text Styles aller Dateien binden sie). Farb-Scopes leer; Schriften behalten den Scope FONT_FAMILY.
7. **Palette-Namen nach Helligkeit:** `color/<farbton>/<stufe>`, Stufe = L* (CIELAB) des Werts, auf 5 gerundet; 0 = Schwarz, 100 = Weiß, wie die Töne in Material 3. Landen zwei Werte eines Farbtons auf derselben Stufe, gilt der ganzzahlige L*-Wert (z. B. `leaf/57`). Alpha-Stufen hängen die Deckkraft an: `neutral/5-a10` = Ton 5 mit 10 %, 7,5 % als `-a7-5`. Die Markenrolle steht im Code-Namen und in der Beschreibung, nicht im Namen. Rollen und Kontext behalten Wortnamen.
8. **Modus-Regel:** Eine farbige Rolle bleibt in allen Modi in derselben Farbfamilie der Palette (zweites Glied des Palette-Namens); je Modus darf nur die Stufe wechseln. Ausgenommen sind die Flächen- und Neutralrollen `background`, `card`, `grey`, `text`, `icon`, `border`, `disabled`, `disabled-text`. Vorbild: Material 3 (Rolle = gleiche Tonpalette, je Modus andere Stufe) und Apple HIG (Farben als Paar hell/dunkel, keine Umkehrung).
9. **Beschreibungen** in Figma auf Englisch, ohne `&quot;`.

---

## 2. Modi von Color Scheme

| Modus | Fläche | Theme-Farbschema |
|---|---|---|
| **White** (Standard, erste Stelle) | Weiß | `background-1` |
| **Forest** | Forest #1A3C33 | Schema mit Forest-Hintergrund |
| **Cream** (Print) | Creme #F0E2C0 | noch keins (Theme `.page-header`-Override); Figma führt |

Alle drei heißen nach der Farbe der Fläche. Cream ist eine Kopie von White mit eigener Fläche, weißer Karte und dunklem Gold (Abschnitt 4).

---

## 3. Palette

Sammlung `Palette`, ein Modus, verborgen bis auf `font-family/*`. L* zur Kontrolle mit einer Nachkommastelle. Scopes: Farben, Deckkraft und Unschärfe leer, Schriften FONT_FAMILY.

| Name | Wert | L* | Code-Name | Beschreibung |
|---|---|--:|---|---|
| `font-family/heading` | Lora | – | `var(--font-family--heading)` | Überschriften; nur Text Styles binden |
| `font-family/body` | DM Sans | – | `var(--font-family--regular)` | Fließtext; nur Text Styles binden |
| `color/forest/25` | #1A3C33 | 22,6 | `var(--brand--primary)` | Forest, Markenfarbe primär |
| `color/forest/30` | #1E4D42 | 29,4 | `var(--brand--secondary)` | Forest hell, Karten auf Forest |
| `color/gold/75` | #D4AD5A | 72,6 | – | Gold hell, Verlaufsstart Bestseller/Rating |
| `color/gold/65` | #B8923A | 62,6 | `var(--brand--primary-accent)` | Gold, Markenakzent |
| `color/gold/50` | #96751E | 51,0 | – | Gold dunkel, Verlaufsende |
| `color/leaf/95` | #EDF3E9 | 95,2 | – | Blattgrün 12 % auf Weiß (gemischt), Auswahlfläche hell |
| `color/leaf/60` | #6C9C4A | 59,4 | `var(--brand--secondary-accent)` | Blattgrün, Aktion und Erfolg |
| `color/leaf/55` | #609142 | 55,2 | – | Blattgrün dunkel, Verlaufsende |
| `color/leaf/30` | #2E5439 | 32,3 | – | Blattgrün 25 % auf Forest (gemischt), Auswahlfläche dunkel |
| `color/cream/90` | #F0E2C0 | 90,2 | – | Creme (Markenfarbe sekundär, 2. Eintrag) |
| `color/sage/70` | #93B389 | 69,6 | – | Salbei (Neu, Aktion) |
| `color/sage/60` | #7A9C6F | 60,8 | – | Salbei dunkel |
| `color/red/45` | #C2403A | 46,2 | – | Zinnober (Fehler, Sale) |
| `color/red/40` | #A8332C | 39,4 | – | Zinnober dunkel |
| `color/amber/60` | #D4842A | 62,2 | – | Amber (Warnung) |
| `color/amber/55` | #B66E1F | 53,2 | – | Amber dunkel |
| `color/petrol/45` | #44707D | 44,7 | – | Petrol (Info) |
| `color/petrol/35` | #355A66 | 36,0 | – | Petrol dunkel |
| `color/neutral/100` | #FFFFFF | 100,0 | – | Weiß |
| `color/neutral/95` | #F5F5F5 | 96,5 | – | Hellgrau (Karten auf Weiß) |
| `color/neutral/5` | #121212 | 5,5 | – | Fast-Schwarz (Text auf Weiß) |
| `color/neutral/0` | #000000 | 0,0 | – | Schwarz (Overlay-Basis) |
| `color/neutral/5-a7-5` | #121212, 7,5 % | – | – | Grau-Fläche auf Weiß (Theme: text 7,5 %) |
| `color/neutral/5-a10` | #121212, 10 % | – | – | Rahmen auf Weiß (Theme: text 10 %) |
| `color/neutral/5-a40` | #121212, 40 % | – | – | deaktivierter Inhalt auf Weiß |
| `color/neutral/100-a7-5` | #FFFFFF, 7,5 % | – | – | Grau-Fläche auf Forest |
| `color/neutral/100-a10` | #FFFFFF, 10 % | – | – | Rahmen auf Forest |
| `color/neutral/100-a40` | #FFFFFF, 40 % | – | – | deaktivierter Inhalt auf Forest |
| `color/neutral/0-a60` | #000000, 60 % | – | – | Overlay |
| `color/purple/40` · `/15` | #6E4AA6 · #2E2150 | 39,5 · 16,7 | – | Sorte Special Tea |
| `color/olive/80` · `/45` | #BDD188 · #4F6E2C | 80,8 · 42,8 | – | Sorte Green Tea |
| `color/slate/35` · `/10` | #4A565E · #1A2024 | 35,8 · 11,8 | – | Sorte Black Tea |
| `color/brown/45` · `/25` | #97623B · #4E3220 | 46,5 · 23,7 | – | Sorte Special Herbs |
| `opacity/80` · `/60` · `/40` | 80 · 60 · 40 | – | – | Deckkraft-Stufen |
| `blur/8` | 8 | – | – | Unschärfe (Figma-Radius) für das Overlay |

---

## 4. Rollen (Color Scheme)

Werte: **White / Forest** (Cream in Klammern; nicht genannte Rollen haben in Cream den White-Wert). „alle“ = gleicher Alias in allen Modi.

**Fläche, Inhalt, Rahmen**

| Name | Alias White / Forest (Cream) | Scopes | Code-Name | Beschreibung |
|---|---|---|---|---|
| `color/scheme/background` | neutral/100 / forest/25 (cream/90) | Rahmen-, Formfüllung | `var(--color-scheme--background)` | Grundfläche des Bereichs |
| `color/scheme/card` | neutral/95 / forest/30 (neutral/100) | Rahmen-, Formfüllung | `var(--color-scheme--card)` | Karten, Eingabefelder, Kacheln |
| `color/scheme/grey` | neutral/5-a7-5 / neutral/100-a7-5 | Rahmen-, Formfüllung | `var(--color-scheme--grey)` | zurückhaltende Fläche (Theme: text 7,5 %) |
| `color/scheme/text` | neutral/5 / neutral/100 (neutral/5) | Text, Form, Kontur | `var(--color-scheme--text)` | Inhalt: Text, Icons |
| `color/scheme/icon` | → `color/scheme/text` (alle) | Form, Kontur | `var(--color-scheme--text)` | Icons und Logos; Core-Icons hängen daran |
| `color/scheme/accent` | gold/65 / gold/65 (gold/50) | Text, Form, Rahmen-, Formfüllung, Kontur | `var(--color-scheme--accent)` | dekorativer Markenakzent (Vorzeile, Tabellenkopf, Linie) |
| `color/scheme/link` | gold/65 / gold/65 (gold/50) | Text, Form, Kontur | `var(--color-scheme--link)` | Links und Text-Buttons, auch Icon im Link |
| `color/scheme/accent-text` | neutral/100 (alle) | Text, Form, Kontur | geplant `var(--color-scheme--accent-text)` | Text und Icons auf `accent` (Labels, Price Tier, Callout) |
| `color/scheme/accent-secondary-text` | neutral/100 (alle) | Text, Form, Kontur | geplant `var(--color-scheme--accent-secondary-text)` | Text und Icons auf `accent-secondary` |
| `color/scheme/border` | neutral/5-a10 / neutral/100-a10 | Kontur, Rahmen-, Formfüllung | `var(--color-scheme--border)` | Rahmen und Trennlinien (Theme: text 10 %, auch als Fläche) |

**Buttons**

| Name | Alias | Scopes | Code-Name |
|---|---|---|---|
| `color/scheme/button-primary` | leaf/60 (alle) | Rahmen-, Formfüllung | `var(--color-scheme--button-primary)` |
| `color/scheme/button-primary-text` | neutral/100 (alle) | Text, Form, Kontur | `var(--color-scheme--button-primary-text)` |
| `color/scheme/button-secondary` | neutral/100 (alle) | Rahmen-, Formfüllung | `var(--color-scheme--button-secondary)` |
| `color/scheme/button-secondary-text` | leaf/60 (alle) | Text, Form, Kontur | `var(--color-scheme--button-secondary-text)` |

**Zustände** (geplante Theme-Rollen, TODO-044)

| Name | Alias White / Forest | Scopes | Code-Name | Beschreibung |
|---|---|---|---|---|
| `color/scheme/active` | gold/65 (alle) | Text, Form, Rahmen-, Formfüllung, Kontur | `var(--color-scheme--active)` | aktiver Tab, Datenmarken (Bestandsbalken), Zähler, Aktion in einer gewählten Zeile. Umschalter und Zeitraum-Auswahl bleiben neutral (`text`) |
| `color/scheme/selection` | leaf/60 (alle) | Form, Kontur, Rahmenfüllung | `var(--color-scheme--selection)` | Auswahlring und Haken |
| `color/scheme/selection-tint` | leaf/95 / leaf/30 | Rahmen-, Formfüllung | `var(--color-scheme--selection-tint)` | Fläche einer gewählten Auswahl |
| `color/scheme/focus` | leaf/60 (alle) | Kontur | `var(--color-scheme--focus)` | Fokusring (Theme heute transparent) |
| `color/scheme/disabled` | neutral/5-a10 / neutral/100-a10 | Rahmen-, Formfüllung | `var(--color-scheme--disabled)` | Fläche deaktivierter Felder und Buttons |
| `color/scheme/disabled-text` | neutral/5-a40 / neutral/100-a40 | Text, Form, Kontur | `var(--color-scheme--disabled-text)` | deaktivierter Inhalt |
| `color/scheme/accent-secondary` | leaf/60 (alle) | Text, Form, Rahmen-, Formfüllung, Kontur | `var(--color-scheme--accent-secondary)` | dekoratives Blattgrün: Labels, Rahmen, Flaggen (Print) |

**Global (modusfrei, gleicher Alias in allen Modi)**

| Name | Alias | Scopes | Code-Name | Beschreibung |
|---|---|---|---|---|
| `color/global/success` · `-end` · `-text` | leaf/60 · leaf/55 · neutral/100 | Füllung, Kontur · Füllung · Text, Form, Kontur | `var(--color-global--success)` · – · geplant `…-success-text` | erledigt, positiv, Trend hoch |
| `color/global/warning` · `-end` · `-text` | amber/60 · amber/55 · neutral/5 | dto. | `var(--color-global--warning)` | fällig, wartet, knapp |
| `color/global/error` · `-end` · `-text` | red/45 · red/40 · neutral/100 | dto. | `var(--color-global--error)` | Problem, überfällig, leer |
| `color/global/info` · `-text` | petrol/45 · neutral/100 | dto. | `var(--color-global--info)` | Hinweis, Probezeit |
| `color/global/sale` · `-end` · `-text` | red/45 · red/40 · neutral/100 | dto. | `var(--color-global--sale)` | Badge Sale |
| `color/global/new` · `-text` | sage/70 · neutral/100 | dto. | `var(--color-global--new)` | Badge Neu |
| `color/global/promotion` · `-text` | sage/70 · neutral/100 | dto. | `var(--color-global--promotion)` | Badge Aktion |
| `color/global/bestseller` · `-text` | gold/65 · neutral/100 | dto. | `var(--color-global--bestseller)` | Badge Bestseller |
| `color/global/rating` | gold/65 | Form, Kontur | `var(--color-global--rating)` | Bewertungssterne (kein Text) |
| `color/global/overlay` | neutral/0-a60 | Rahmen-, Formfüllung | geplant `var(--color-global--overlay)` | Abdunkelung hinter Popups (Schwarz 60 %), immer mit `blur/overlay` |
| `blur/overlay` | blur/8 | Effekt (Unschärfe) | geplant `var(--blur--overlay)` | Hintergrund-Unschärfe hinter Popups |

**Deckkraft** (modusfrei)

| Name | Alias | Scopes | Code-Name | Beschreibung |
|---|---|---|---|---|
| `opacity/subtle` | opacity/80 | Deckkraft | `var(--opacity--subtle)` | Sekundärer Inhalt |
| `opacity/muted` | opacity/60 | Deckkraft | `var(--opacity--muted)` | Tertiärer Inhalt, Platzhalter |
| `opacity/faint` | opacity/40 | Deckkraft | `var(--opacity--faint)` | leer, nicht geführt, deaktiviert |

**Effekt** (boolesch)

| Name | Wert White / Forest / Cream | Scopes | Code-Name | Beschreibung |
|---|---|---|---|---|
| `effect/glow` | aus / an / aus | – (boolesche Variablen lassen sich nicht eingrenzen) | geplant | blendet die Ebene „Glow“ im Baustein Screen ein: dunkler Grund mit Schein oben und Vignette unten (Verläufe fest, W1) |

**Festgelegt**
- Overlay = Schwarz 60 % mit Hintergrund-Unschärfe 8, hell und dunkel gleich. Figma führt, das Theme übernimmt Abdunkelung und Unschärfe (TODO-044).
- Deckkraft 80/60/40: Figma führt, das Theme übernimmt die Werte (TODO-044).
- Badge-Text bleibt weiß (Neu, Aktion, Bestseller). Bekannte AA-Lücke bei kleiner fetter Schrift; weiße Schrift bräuchte eine Fläche mit L* ≤ 50.
- Cream: `accent` und `link` auf gold/50 (Kontrast auf Creme); `accent-secondary` bleibt leaf/60.
- Statusfarben bekommen keine helleren Stufen für Forest; schwächere Kontraste von Status- und Linkfarbe auf Forest sind hingenommen.

---

## 5. Kontext

**`Layout`** — Modi: Desktop, Mobile, DIN A2, DIN A3, DIN A4, DIN A5, `DIN A6 · DIN Lang`. Werte nach der √2-Regel (`standards.md` §2).

| Gruppe | Variablen | Scopes | Code-Name |
|---|---|---|---|
| Überschriften | `font/heading/h1`–`h6` | Schriftgröße | `var(--font-size--h1)` … `h6` |
| Fließtext | `font/body/tiny`, `small`, `regular`, `medium`, `large` | Schriftgröße | `var(--font-size--tiny)` … `large` |
| Sonder | `font/other/pre`, `font/other/copyright` | Schriftgröße | – (nur Figma) |
| Abstände | `spacing/tiny` … `spacing/xxhuge` (11) | Abstand (Gap, Padding) | `var(--space--tiny)` … `xxhuge` |
| Icons | `icon/xsmall` … `icon/xlarge` (6) | Breite/Höhe | `var(--icon-size--xsmall)` … `xlarge` |
| Radien | `border-radius/small`, `medium`, `large`, `full` | Eckenradius | `var(--border-radius--small)` … `full` |
| Druck | `info box/margin` | Abstand | – |
| Referenz | `frame` | Breite/Höhe | – |
| Kontur | `border-width/regular` (A4 = 2, geometrisch skaliert; Desktop/Mobile 1) | Konturstärke | – |
| Proportion | `proportion/golden/minor` (geometrisch skaliert; Desktop/Mobile = A4-Wert) | Breite/Höhe | – |

**`Variety`** — 9 Modi (Sorten).

| Name | Werte (Alias) | Scopes |
|---|---|---|
| `color/variety/light` | Kratom (4) + Energy Tea: neutral/100 · Special Tea: purple/40 · Green Tea: olive/80 · Black Tea: slate/35 · Special Herbs: brown/45 | Füllung, Kontur, Text |
| `color/variety/dark` | Kratom + Energy Tea: neutral/100 · purple/15 · olive/45 · slate/10 · brown/25 | Füllung, Kontur, Text |

- Für Kratom und Energy Tea sind die Werte Platzhalter (Weiß). Die Etiketten-Titel bleiben fest (Ausnahme in `audit.md`). Brauchen Shop oder App Sortenfarben, die Variety-Werte aus den Etiketten-Verläufen füllen (neue Palette-Töne, Core MINOR), ohne die Etiketten anzufassen.
- Die Mengenangabe auf den Etiketten ist keine Sortenfarbe; es gibt keine Variety-Rolle dafür.

**`Price Tier`** (Modi Classic · Premium · Select): 18 Text-Variablen (`VK Netto/…`, `Provision/…`, `Gewinn/…` je Einzel/VE und 10g/25g/50g), Scope Textinhalt.

**`Employee`** (Modi Joscha · Christian): `Name`, `Phone`, `Position`, Scope Textinhalt; die Texte der Contact Box binden daran.

**Datei-lokal (Print):** `Onlineprinters` (verborgen) mit `bleed`, `size/data/width`, `size/data/height` — Maße der Druckvorlagen, im Audit erlaubt (Skill figma-onlineprinters).

---

## 6. Alte Namen

Zum Erkennen alter Kopien (Audit R4/R5), nie neu verwenden.

| Alt | Aktuell |
|---|---|
| Sammlung `Branding` | `Palette` |
| Sammlung `Color Mode` | `Color Scheme` |
| Modi `Dark Content` / `Light Content`, `Light` / `Dark` | `White` / `Forest` |
| Sammlung `Collection` (`New/Light`, `New/Dark`) | `Variety` (`color/variety/light`, `dark`) |
| Sammlungen `Format`, `Sizing` (`layout/spacing/*`, `layout/icon/*`) | `Layout` (`spacing/*`, `icon/*`) |
| `color/brand/primary`, `primary-accent`, `secondary`, `secondary-2`, `secondary-accent` | `color/forest/25`, `gold/65`, `forest/30`, `cream/90`, `leaf/60` (Palette; gebunden wird die Rolle) |
| `color/system/*`, `color/highlight/*` | `color/global/*` |
| `Text Color` | `color/scheme/icon` |
| `color/scheme/brand`, `brand-tint` | `color/scheme/active`, `selection-tint` |
| `color/brand/primary-contrast`, `secondary-contrast`, `selectedleafs/primray contrast`, `selectedleafs/secondary contrast` | `color/gold/65`, `color/leaf/60` (Palette); Ebenen binden `color/scheme/accent` bzw. `accent-secondary` |
| `opacity/subtle · muted · faint` (Palette) | `opacity/80 · 60 · 40` (Palette); `opacity/subtle · muted · faint` sind jetzt Rollen |
