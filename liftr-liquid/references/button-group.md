# Button Group — Theme Block

Horizontale Button-Gruppe (Primary + optionaler Secondary) als Theme Block. Jeder Button kann unabhängig als primary, secondary oder link gestylt werden. Nutzt shared `.button` und `.button-group` Components aus `core.components-critical.css`.

---

## 1. Was ist Button Group?

Ein Theme Block (`/blocks/button-group.liquid`) mit zwei Button-Slots:

| Element | Default-Style | CSS-Klasse | Merchant-sichtbar |
|---------|--------------|------------|-------------------|
| Primary Button | primary (kein Modifier) | `.button` + `fx-hover-primary` | Ja (Label + Link) |
| Secondary Button | secondary | `.button.is-secondary` | Ja (Label + Link, optional) |

Jeder Slot kann über `button_*_style` umgestylt werden auf: `primary`, `secondary`, `link`.

**Kernprinzip:** Keine eigenen CSS-Klassen für Button-Styles — nutzt ausschließlich shared `.button` Modifiers aus `core.components-critical.css`.

---

## 2. Consumption — Section einbinden

### Schema

```json
{
  "blocks": [
    { "type": "button-group" }
  ]
}
```

### Liquid (content_for)

```liquid
{% content_for 'block', type: 'button-group', id: 'button-group' %}
```

### Preset-Konfiguration

```json
{
  "presets": [
    {
      "name": "t:sections.spotlight_header.name",
      "blocks": [
        {
          "type": "button-group",
          "settings": {
            "button_primary_label": "t:sections.spotlight_header.default.button_primary_label",
            "button_primary_link": "/collections/all",
            "button_secondary_style": "link",
            "button_secondary_label": "t:sections.spotlight_header.default.button_secondary_label"
          }
        }
      ]
    }
  ]
}
```

---

## 3. CSS API — Layout Override

Die Section steuert Layout über CSS Custom Properties auf `.button-group`:

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `--button-group--gap` | `space--small` | Abstand zwischen Buttons |
| `--button-group--margin` | `space--large` | margin-top (Abstand zum vorherigen Element) |
| `--button-group--alignment` | `center` | justify-content (left, center, right) |
| `--button-group--width` | `auto` | Breite der Button-Gruppe |
| `--button-group--max-width` | `unset` | Max-Breite |

### Override-Beispiel (Section CSS)

```css
/* section.spotlight-header.css */
.spotlight-header_component .button-group {
  --button-group--alignment: center;
  --button-group--margin: var(--space--xlarge);
}

/* section.faqs.css -- linksbündig */
.faqs_component .button-group {
  --button-group--alignment: flex-start;
  --button-group--margin: var(--space--medium);
}
```

### Automatischer Gap-Override

Das CSS enthält einen eingebauten Override: wenn ein `.button.is-link` oder `.button.is-text` vorhanden ist, wird `--button-group--gap` automatisch auf `space--large` erhöht (Link-Buttons brauchen mehr visuellen Abstand).

---

## 4. Color Override — Nested Shared Component Pattern

Button Group nutzt **nicht** das `custom-colors` Snippet. Stattdessen: scoped `{% style %}` Block mit `#{{ block.id }}` Targeting.

**Grund:** Drei unabhängige Override-Targets (primary, secondary, link) — `custom-colors` kann nur ein Scope bedienen.

### Selektoren

| Target | Selektor |
|--------|----------|
| Primary-styled Button | `#{{ block.id }} .button:not(.is-secondary):not(.is-link)` |
| Secondary-styled Button | `#{{ block.id }} .button.is-secondary` |
| Link-styled Button | `#{{ block.id }} .button.is-link` |

### Blank-Guard

Jeder Override ist in eine `!= blank` Prüfung gewrapped — leere Shopify Color-Pickers erzeugen keinen Output:

```liquid
{%- if block.settings.button_primary_color != blank -%}
  background-color: {{ block.settings.button_primary_color }};
{%- endif -%}
```

---

## 5. CSS Mapping

| Setting ID | Effekt auf HTML |
|------------|----------------|
| `button_primary_style: primary` | `.button fx-hover-primary` (kein Modifier) |
| `button_primary_style: secondary` | `.button.is-secondary` |
| `button_primary_style: link` | `.button.is-link` |
| `button_secondary_style` | Analog zu primary |

Die Style-Zuordnung geschieht per `case/when` im Liquid Head — nicht im CSS.

---

## 6. Merchant Settings

| Setting | Type | Default | Sichtbarkeit |
|---------|------|---------|-------------|
| `color_mode` | select | `auto` | Immer |
| `button_primary_color` | color | — | Nur bei `color_mode == custom` |
| `button_primary_text` | color | — | Nur bei `color_mode == custom` |
| `button_secondary_color` | color | — | Nur bei `color_mode == custom` |
| `button_secondary_text` | color | — | Nur bei `color_mode == custom` |
| `link_color` | color | — | Nur bei `color_mode == custom` |
| `button_primary_style` | select | `primary` | Immer |
| `button_primary_label` | text | Translation | Immer |
| `button_primary_link` | url | — | Immer |
| `button_secondary_style` | select | `secondary` | Immer |
| `button_secondary_label` | text | — | Immer |
| `button_secondary_link` | url | — | Immer |

**Hinweis:** Secondary Button erscheint nur wenn `button_secondary_label` gesetzt ist — kein Toggle nötig.

---

## 7. Unterschied zu Heading Group

| Aspekt | Heading Group | Button Group |
|--------|--------------|-------------|
| Color Override | `custom-colors` Snippet | Scoped `{% style %}` |
| CSS | `core.components-critical.css` (Block-Layout) | shared `.button` / `.button-group` in `core.components-critical.css` |
| CSS API Owner | `.heading-group_component` | `.button-group` (shared) |
| Modifier-System | `heading-style-*`, `text-size-*` | `.is-secondary`, `.is-link` (shared) |

---

## 8. Checkliste — Neue Section mit Button Group

- [ ] Schema: `{ "type": "button-group" }` in blocks Array
- [ ] Preset: `button_primary_label` + `button_primary_link` mit sinnvollen Defaults
- [ ] Preset: `button_secondary_style` passend wählen (oft `link` für leichtere Optik)
- [ ] CSS: Layout-Override via `--button-group--alignment`, `--button-group--margin`
- [ ] CSS: `--button-group--gap` nur überschreiben wenn Section-spezifisch nötig (Link-Override greift automatisch)
- [ ] Keine `.button`-Styles in Section CSS duplizieren — shared Components regeln das
- [ ] Heading Group + Button Group zusammen? → Button Group als zweiter Block nach Heading Group im Preset

---

## 9. Dependencies

| Dependency | Typ | Zweck |
|------------|-----|-------|
| `core.components-critical.css` | CSS | `.button`, `.button-group`, Modifiers |
| `core.fx.css` | CSS | `fx-hover-primary` Hover-Effekt |
