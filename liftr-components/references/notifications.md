# Notifications — LIFTR Notification System

**Source:** `api.notification.js` + `ui.notifications.js`
**Global:** `window.liftrNotification`
**UI Component:** `<liftr-notifications>` (module `NAME = 'notification'` → events `liftr:notification:*`)

---

## 1. Quick Reference

```javascript
liftrNotification.success('Produkt wurde hinzugefügt');
liftrNotification.error('Etwas ist schiefgelaufen');
liftrNotification.info('Kostenloser Versand ab 40 EUR');
liftrNotification.warning('Nur noch 2 auf Lager');

// With options
liftrNotification.success('Gespeichert', { duration: 3000, priority: 8 });

// Control
const id = liftrNotification.success('Test');
liftrNotification.dismiss(id);
liftrNotification.dismissAll();
```

One text per notification: `ui.notifications.js` removed the `message` parameter (BREAKING) and renders
only the title. Signature for all four types: `(title, options?)`.

---

## 2. Installation

Already part of the theme — do not add it again:

- `snippets/core.liftr.liquid` renders the container once:

```liquid
<liftr-notifications
  popover="manual"
  role="log"
  aria-label="{{ 'global.aria.notifications' | t }}"
  aria-live="polite"
  aria-relevant="additions"
></liftr-notifications>
```

- `snippets/core.head.liquid` loads `ui.notifications.js`; modules import the API via `import { liftrNotification, TYPES } from 'api.notification';` (also registers `window.liftrNotification`).

**CRITICAL:** `popover="manual"` is required. Without it, notifications won't appear above modal dialogs.

---

## 3. API Methods

### Notification Types

| Method | Color | Usage |
|--------|-------|-------|
| `success(title, options?)` | Green | Operation completed |
| `error(title, options?)` | Red | Operation failed |
| `info(title, options?)` | Blue | Information |
| `warning(title, options?)` | Orange | Attention needed |

Theme status: the wrappers in `api.notification.js` for `error`/`info`/`warning` still declare
`(title, message, options)` and forward the second argument as options — so `(title, options)` works when
the component is mounted, but the event fallback (before mount) drops the options.

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `duration` | number | 4000 (`defaultDuration`) | Auto-dismiss in ms (0 = persistent → `liftr-persist` attribute) |
| `priority` | number | 5 | Queue priority (higher = shown first) |

`DURATIONS` (`SHORT` 2000, `NORMAL` 3000, `LONG` 5000) and `TYPES` are exported from `api.notification`.

### Programmatic Control

```javascript
const id = liftrNotification.success('Test', 'Message');
liftrNotification.dismiss(id);     // Dismiss specific
liftrNotification.dismissAll();    // Dismiss all + clear queue
```

### Types Import

```javascript
import { TYPES, DURATIONS } from 'api.notification';
TYPES.SUCCESS  // 'success'
TYPES.ERROR    // 'error'
TYPES.INFO     // 'info'
TYPES.WARNING  // 'warning'
```

---

## 4. Event-Based Usage

When the component isn't mounted yet, use events:

```javascript
import { emit } from 'core.liftr';

emit('liftr:notification:show', {
  type: 'success',
  title: 'Gespeichert',
  duration: 4000,
  priority: 5
});
```

### Listening

```javascript
import { on } from 'core.liftr';

on('liftr:notification:shown', (e) => {
  const { id, type, title } = e.detail;
});

on('liftr:notification:dismissed', (e) => {
  const { id } = e.detail;
});
```

---

## 5. Sequential Dispatch (Stagger)

Multiple notifications from the same operation MUST be staggered. Simultaneous dispatch causes overlapping animations.

**Stagger value:** `FX.PROPERTIES.NOTIFICATION_STAGGER` (CSS SSOT)

### Pattern

```javascript
const stagger = this.getCssDuration(FX.PROPERTIES.NOTIFICATION_STAGGER, 200);

for (let i = 0; i < pending.length; i++) {
  const { type, title } = pending[i];
  timeoutIds.push(
    setTimeout(() => this.#notify(type, title), stagger * (i + 1))
  );
}
```

### Anti-Patterns

```javascript
// WRONG -- all fire simultaneously
for (const { type, title } of pending) {
  this.#notify(type, title);
}

// WRONG -- single delay, then synchronous loop
setTimeout(() => {
  for (const { type, title } of pending) {
    this.#notify(type, title);
  }
}, stagger);
```

### Cleanup

Staggered timeouts MUST be tracked and cleared on unmount:

```javascript
#flushTimeoutIds = [];

// Track
this.#flushTimeoutIds.push(
  setTimeout(() => this.#notify(type, title), stagger * (i + 1))
);

// Cleanup in unmount
for (const id of this.#flushTimeoutIds) clearTimeout(id);
this.#flushTimeoutIds = [];
```

### Sequencing with Operation Notification

```
"Menge aktualisiert"           → t+0ms    (operation, synchronous)
"Gratisversand freigeschaltet" → t+200ms  (stagger x 1)
"Gratisprobe freigeschaltet"   → t+400ms  (stagger x 2)
```

---

## 6. States and Roles

### Container States (on `<liftr-notifications>`)

| State | Description |
|-------|-------------|
| `has-items` | At least one notification visible |

### Item States (on notification-item)

| State | Description |
|-------|-------------|
| `visible` | Shown (triggers enter animation) |
| `exiting` | Dismissing (triggers exit animation) |
| `paused` | Countdown paused (hover/focus) |
| `swiping` | Swipe-to-dismiss in progress |
| `success` / `error` / `info` / `warning` | Type styling |

Persistent items (duration 0) carry the attribute `liftr-persist="true"` — not a state.

### Roles

| Role | Element | Description |
|------|---------|-------------|
| `notification-item` | div (`role="alert"`) | Individual notification (`::before` tint, `::after` countdown bar) |
| `notification-title` | strong | Text (`::before` = type icon) |
| `notification-close` | button | Dismiss button (`::before` = x icon) |

---

## 7. CSS Reference

### Selectors

```css
liftr-notifications { }
liftr-notifications:popover-open { }
liftr-notifications[liftr-state~="has-items"] { }

[liftr-role~="notification-item"] { }
[liftr-role~="notification-item"][liftr-state~="visible"] { }
[liftr-role~="notification-item"][liftr-state~="exiting"] { }
[liftr-role~="notification-item"][liftr-state~="success"] { }
[liftr-role~="notification-item"][liftr-persist] { }
```

### Custom Properties

| Property | Description |
|----------|-------------|
| `--fx-notification-exit-duration` | Exit animation duration (read by JS via `FX.PROPERTIES`) |
| `--fx-notification-stagger` | Stagger between sequential notifications (CSS SSOT, per FX set) |
| `--notification-duration` | Auto-dismiss countdown (set by JS per item) |
| `--notification-drag-x` | Swipe offset during drag (set by JS per item) |

CSS lives in `core.liftr.css` (`@layer modules`).

---

## 8. Gotchas

### Popover API Required

Component uses Popover API for Top Layer placement above modal dialogs. Without `popover="manual"`, notifications render behind modals.

### Coordinate-Based Click Detection

Due to Top Layer stacking, `e.target` is always the dialog, not the notification. The component uses `getBoundingClientRect()` coordinate matching.

### XSS Prevention

All user content is escaped via `textContent` → `innerHTML` pattern.

---

## 9. Integration Examples

```javascript
// Cart add success
on('liftr:shop:cart-added', (e) => {
  const item = e.detail.addedItems[0];
  liftrNotification.success(`${item.product_title} wurde zum Warenkorb hinzugefügt`);
});

// Error handling
on('liftr:shop:error', (e) => {
  liftrNotification.error(e.detail.error.message);
});

// Form submission
try {
  await submitForm(form);
  liftrNotification.success('Vielen Dank für deine Nachricht');
} catch (error) {
  liftrNotification.error(error.message);
}
```

### Configuration Override

```javascript
// In liftr-settings script
{
  modules: {
    notification: {
      maxVisible: 5,        // Default: 3
      defaultDuration: 5000 // Default: 4000
    }
  }
}
```

### Accessibility

- Container: `role="log"`, `aria-live="polite"`, `aria-relevant="additions"` (in `core.liftr.liquid`)
- Each notification: `role="alert"` + `aria-live="polite"` (set by JS)
- Close buttons: `aria-label` from i18n `notification.close` (set by JS)
