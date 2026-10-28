---
name: liftr-snippet
description: Guide for creating reusable Liquid snippets in the LIFTR theme. Covers the self-contained component principle (modifiers on component root, never parent), parameter system with defaults, Guard Contract documentation, Liquid file structure (Parameters → Data → Guards → CSS → HTML), and docblock format. Use whenever creating a new snippet, adding parameters or variants to an existing snippet, reviewing snippet code, or deciding whether something should be a snippet vs. a block. For CSS architecture see liftr-css-system. For block creation see liftr-block.
---

# LIFTR Snippet Guide

**Output:** `snippets/[name].liquid` — optionally `assets/snippet.[name].css` for large snippets (>50 lines CSS)

---

## When Snippet vs. Block?

```
Is it configured by the merchant in the editor?
  → YES: Block (has schema, settings, editor UI)

Is it a reusable code component called via {% render %}?
  → YES: Snippet

Does it have 6+ visual parameters and complex configuration?
  → Consider: Block might be better (schema settings are more merchant-friendly)
```

Snippets are code-level building blocks. No schema, no editor — only `{% render %}` with parameters. Blocks are editor-level building blocks with settings UI.

---

## Self-Contained Components

**Snippets carry their own styling. No parent may control a snippet's appearance through its own selectors.** For the full principle, anti-patterns and correct patterns → DESIGN_PRINCIPLES.md (Section 10).

### When a Snippet Needs Parameters

| Snippet has... | Parameter? | Example |
|----------------|-----------|---------|
| Visual variants (card/plain) | Yes `design` | `design: 'card'` |
| Layout variants (horizontal/vertical) | Yes `layout` | `layout: 'horizontal'` |
| Size variants (small/medium/large) | Yes `size` | `size: 'small'` |
| Only one look | No | No parameter needed |

**Guideline:** If a snippet accumulates more than 5-6 parameters, reconsider whether it should be a block instead. Blocks have labeled settings in the editor — more manageable than a long `{% render %}` line.

### Parent Override via CSS Variables

Parents may set CSS variables to fine-tune a snippet (opt-in with fallback). This is NOT parent styling — it's the Parent Override pattern from liftr-css-system:

```css
/* Parent sets variable */
.section_component .card_component {
  --card--gap: var(--space--large);
}

/* Snippet consumes with Inline Fallback */
.card_component {
  gap: var(--card--gap, var(--space--medium));
}
```

The difference: CSS variables are opt-in (fallback exists). Parent selectors on snippet internals are forbidden.

---

## Liquid File Structure

```
Docblock
PARAMETERS & DEFAULTS
DATA
GUARDS
CSS
HTML OUTPUT
```

No SECTION HEADER — snippets do not load their own CSS or JS. The parent (section or block) is responsible for asset loading.

### Docblock

```liquid
{% comment %}
  ============================================================================
  SNIPPET: [name]
  ============================================================================
  [Brief description of what the snippet does]

  Parameters:
    product        {Product}  Shopify product object - required
    design         {String}   Design variant (card|plain) - default: 'plain'
    layout         {String}   Layout variant (vertical|horizontal) - default: 'vertical'
    size           {String}   Size variant (small|medium|large) - default: 'medium'
    show_price     {Boolean}  Show price - default: true

  Guard Contract:
    No external guard needed — snippet handles blank checks internally.
    OR: Caller is responsible for the `is_custom` guard.

  Usage:
    {% render '[name]' %}
    {% render '[name]', product: product, design: 'card' %}

  Dependencies:
    CSS: core.components.css
    Snippets: [if any]
  ============================================================================
{% endcomment %}
```

**Docblock fields:**

| Field | Required | Purpose |
|-------|----------|---------|
| Parameters | ✅ | All parameters with type, description, default |
| Guard Contract | ✅ | Who handles blank/validation checks |
| Usage | ✅ | Example `{% render %}` calls |
| Dependencies | ✅ | CSS file, other snippets |
| Features | Optional | Only if non-obvious capabilities |

**Parameter documentation rules:**
- Every parameter has a type: `{String}`, `{Boolean}`, `{Product}`, `{Image}`, `{Number}`
- Every parameter has either `default: [value]` or `required`
- Allowed values listed inline: `(card|plain|full)`

### Parameters & Defaults

```liquid
{%- liquid

  # ============================================================================
  # PARAMETERS & DEFAULTS
  # ============================================================================

  assign design = design | default: 'plain'
  assign layout = layout | default: 'vertical'
  assign show_price = show_price | default: true

-%}
```

**Every parameter gets a default.** The snippet must be renderable with `{% render '[name]' %}` alone — no required parameters except data objects (product, article, etc.).

### Data

Derived values computed from parameters:

```liquid
  # ============================================================================
  # DATA
  # ============================================================================

  assign css_design = design | prepend: 'is-'
  assign css_layout = layout | prepend: 'is-'
```

For snippets rendered in loops that need unique IDs (forms, aria-labelledby):

```liquid
  assign id_item = id_parent | append: '-' | append: index
```

Only add the ID system when the snippet needs it (forms, accessibility references) — not by default.

### Guards

```liquid
  # ============================================================================
  # GUARDS
  # ============================================================================

  assign has_image = false
  if product.featured_image != blank
    assign has_image = true
  endif
```

**Guard Contract:** The docblock states who handles checks.
- "No external guard needed" → Snippet checks internally, caller just renders
- "Caller is responsible for `is_custom`" → Caller wraps in `{% if is_custom %}`, snippet trusts the data

### CSS (derived classes)

```liquid
  # ============================================================================
  # CSS
  # ============================================================================

  assign css_classes = '[name]_component'
  if design != 'plain'
    assign css_classes = css_classes | append: ' is-' | append: design
  endif
  assign css_classes = css_classes | append: ' is-' | append: layout
```

### HTML Output

```liquid
{% comment %} ================================================================
   HTML OUTPUT
   ================================================================ {% endcomment %}

<div class="{{ css_classes }}">

  {%- if has_image -%}
    <div class="[name]_media">
      {{ product.featured_image | image_url: width: 600 | image_tag }}
    </div>
  {%- endif -%}

  <div class="[name]_body">
    <h3 class="[name]_title">{{ product.title }}</h3>
    {%- if show_price -%}
      <span class="[name]_price">{{ product.price | money }}</span>
    {%- endif -%}
  </div>

</div>
```

---

## CSS

Snippet CSS lives in `core.components.css` (shared UI) or `snippet.[name].css` (>50 lines).

Modifiers always on `_component` root, never on parent:

```css
/* Base */
.card_component {
  display: flex;
  flex-direction: column;
  gap: var(--gap--medium);
}

/* Design variant */
.card_component.is-card {
  background: var(--card--background, var(--color-scheme--card));
  border-radius: var(--border-radius--medium);
  padding: var(--space--medium);
}

/* Layout variant */
.card_component.is-horizontal {
  flex-direction: row;
}

/* Modifier-Children */
.card_component.is-horizontal {
  .card_media { flex: 0 0 40%; }
}
```

For full CSS patterns → liftr-css-system skill.

---

## Checklist

### Structure
- [ ] Docblock with Parameters, Guard Contract, Usage, Dependencies?
- [ ] All parameters have defaults (except data objects)?
- [ ] Guard Contract documented and implemented?
- [ ] Liquid subsections in order: Parameters → Data → Guards → CSS → HTML?

### Self-Contained
- [ ] All visual variants as parameters (design, layout, size)?
- [ ] Modifier classes on `_component` root, never parent?
- [ ] CSS selectors start with `.snippet_component.is-*`, not `.parent.is-* .snippet_*`?
- [ ] No more than 5-6 parameters? (If more → consider block instead)

### CSS
- [ ] CSS in `core.components.css` or `snippet.[name].css`?
- [ ] Snippet does NOT load its own assets (parent responsibility)?
- [ ] Parent Override only via CSS variables with Inline Fallback?
