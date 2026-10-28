# Heading Group — Theme Block

Wiederverwendbare Text-Gruppe (Pre-Heading + Heading + Description) als Theme Block. Wird über `content_for` in Sections eingebunden. Layout-Steuerung liegt vollständig beim Consumer (Section CSS), Appearance beim Block selbst.

---

## 1. Was ist Heading Group?

Ein Theme Block (`/blocks/heading-group.liquid`) mit drei Elementen:

| Element | HTML-Tag | Merchant-sichtbar | CSS-Klasse |
|---------|----------|-------------------|------------|
| Pre-Heading | Konfigurierbar (span, p, h1–h6) | Ja (versteckbar) | `.heading-group_pre-heading` |
| Heading | Konfigurierbar (h1–h6) | Ja | `.heading-group_heading` |
| Description | `<div>` (richtext) | Ja (versteckbar) | `.heading-group_text` |

**Kernprinzip:** Der Block kennt seine Breite nicht — er füllt seinen Container. Die Section steuert Layout (über die CSS API, Parent Override → `css-system.md`, liftr-foundation), der Block steuert Appearance.

---

## 2. Consumption — Section einbinden

### Schema

```json
{
  "blocks": [
    { "type": "heading-group" }
  ]
}
```

### Liquid (content_for)

```liquid
{% content_for 'block', type: 'heading-group', id: 'heading-group' %}
```

### Preset-Konfiguration (Developer API)

Die HTML-Tags sind über `visible_if: "{{ false }}"` vor dem Merchant versteckt. Der Developer steuert sie im Section-Preset:

```json
{
  "presets": [
    {
      "name": "t:sections.faqs.name",
      "blocks": [
        {
          "type": "heading-group",
          "settings": {
            "pre_heading_tag": "span",
            "heading_tag": "h3",
            "heading_style": "h2",
            "content_pre_heading": "t:sections.faqs.default.content_pre_heading",
            "content_heading": "t:sections.faqs.default.content_heading"
          }
        }
      ]
    }
  ]
}
```

### Tag-Empfehlungen pro Context

| Section | pre_heading_tag | heading_tag | Begründung |
|---------|----------------|-------------|------------|
| Spotlight Header | `h1` | `h2` | Primärer Page-Heading |
| FAQs | `span` | `h3` | Untergeordnet, kein SEO-Heading nötig |
| Store List | `span` | `h2` | Section-Level Heading |
| Featured Products | `span` | `h2` | Section-Level Heading |
| Product Detail | `span` | `h3` | Unterhalb Product Title (h1) |

**Regel:** Nur **eine** Section pro Page darf `pre_heading_tag: h1` setzen. Heading-Hierarchie muss seitenübergreifend stimmen.

---

## 3. CSS API — Layout Override

Die Section steuert Layout über CSS Custom Properties auf `.heading-group_component`:

| Variable | Typ | Default | Beschreibung |
|----------|-----|---------|-------------|
| `--heading-group--alignment` | Layout | `center` | text-align (left, center, right) |
| `--heading-group--max-width` | Layout | `none` | Max-Breite der Text-Spalte |
| `--heading-group--gap` | Layout | `space--small` | Abstand zwischen Elementen |
| `--heading-group--margin-inline` | Layout | `0` | Horizontale Positionierung |

### Override-Beispiel (Section CSS)

```css
/* section.faqs.css */
.faqs_component .heading-group_component {
  --heading-group--alignment: left;
  --heading-group--max-width: 48rem;
  --heading-group--margin-inline: 0;
}

/* section.spotlight-header.css -- zentriert */
.spotlight-header_component .heading-group_component {
  --heading-group--alignment: center;
  --heading-group--max-width: 42rem;
  --heading-group--margin-inline: auto;
}
```

**Wichtig:** Keine Layout-Properties direkt auf `.heading-group_component` setzen (kein `max-width`, `margin` etc. ohne die CSS API). Die API-Variablen haben Inline Fallbacks — ohne Override gelten die Defaults.

---

## 4. CSS API — Farb-Override

| Variable | Typ | Fallback Target |
|----------|-----|----------------|
| `--heading-group--text` | Farbe | `color-scheme--text` |
| `--heading-group--accent` | Farbe | `color-scheme--accent` |

Farben werden **nur** über das `custom-colors` Snippet gesetzt (Merchant wählt `color_mode: custom`). Consumer-Sections setzen keine Farb-Variablen direkt.

### Farb-Variablen im Block-CSS (Inline Fallback → `css-system.md`, liftr-foundation)

```css
.heading-group_pre-heading {
  color: var(--heading-group--accent, var(--color-scheme--accent));
}

.heading-group_heading {
  color: var(--heading-group--text, var(--color-scheme--text));
}
```

Wenn `custom-colors` nichts setzt → Fallback auf Color Scheme.

---

## 5. CSS Mapping

| Setting ID | CSS-Klasse auf Element |
|------------|----------------------|
| `heading_style` | `.heading-group_heading.heading-style-{h1\|h2\|h3}` |
| `text_size` | `.heading-group_text.text-size-{regular\|medium\|large}` |
| `text_lines` / `heading_lines` | `--text-clamp` per `{% style %}` auf `.heading-group_text.text-clamp` bzw. `.heading-group_heading` |

`heading-style-*` und `.text-clamp` sind in `core.base.css` definiert, das Block-Layout in `core.components-critical.css`.
Theme-Stand (main, 28.10.2026): `text-size-*`-Klassen sind nirgends definiert — `text_size` wirkt derzeit nicht (vorhanden sind `.text-small/-regular/-medium/-large` in `core.base.css`).

---

## 6. Merchant Settings

| Setting | Type | Default | Sichtbarkeit |
|---------|------|---------|-------------|
| `color_mode` | select | `auto` | Immer |
| `text` / `accent` | color | — | Nur bei `color_mode == custom` |
| `heading_style` | select | `h1` | Immer |
| `text_size` | select | `medium` | Nur wenn `hide_text == false` |
| `content_pre_heading` | text | Translation | Nur wenn `hide_pre_heading == false` |
| `content_heading` | text | Translation | Immer |
| `content_text` | richtext | Translation | Nur wenn `hide_text == false` |
| `hide_pre_heading` | checkbox | `false` | Immer (Advanced) |
| `hide_text` | checkbox | `false` | Immer (Advanced) |
| `use_text_lines` | checkbox | `true` | Nur wenn `hide_text == false` |
| `text_lines` | range 1–4 | `2` | Nur wenn `hide_text == false` UND `use_text_lines == true` |

**Developer-only** (via `visible_if: "{{ false }}"`):
| Setting | Type | Default |
|---------|------|---------|
| `pre_heading_tag` | select | `p` |
| `heading_tag` | select | `h2` |

---

## 7. Checkliste — Neue Section mit Heading Group

Wenn du eine Section erstellst die Heading Group konsumiert:

- [ ] Schema: `{ "type": "heading-group" }` in blocks Array
- [ ] Preset: `pre_heading_tag` und `heading_tag` passend zur Heading-Hierarchie setzen
- [ ] Preset: `heading_style` passend zum visuellen Gewicht setzen
- [ ] Preset: Default-Texte über Translations (`t:sections.[name].default.*`)
- [ ] CSS: Layout-Override via `--heading-group--alignment`, `--heading-group--max-width`, `--heading-group--margin-inline`
- [ ] CSS: `--heading-group--gap` nur überschreiben wenn Section-spezifisch nötig
- [ ] Heading-Hierarchie: Nur 1× `h1` pro Page, konsistente Tag-Wahl
- [ ] Keine direkten Layout-Properties auf `.heading-group_component` — nur CSS API Variablen

---

## 8. Dependencies

| Dependency | Typ | Zweck |
|------------|-----|-------|
| `core.components-critical.css` | CSS | Layout + Farb-Variablen |
| `custom-colors` | Snippet | Scoped Color Override |
| `core.base.css` | CSS | `heading-style-*`, `.text-clamp` |

---

## 9. Known Parents

| Section | Alignment | Max-Width | Besonderheit |
|---------|-----------|-----------|-------------|
| spotlight-header | center | 42rem | `pre_heading_tag: h1` |
| faqs | left | 48rem | In stacked Layout |
| store-list | left / center | varies | |
| featured-products | center | none | Volle Container-Breite |
