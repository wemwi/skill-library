---
name: liftr-notification
description: "Integration guide for the LIFTR notification system (api.notification.js + ui.notification.js). Covers the global liftrNotification API, Popover-based UI component, priority queue, stagger dispatch, event-based usage, and coordinate-based click detection. Use whenever triggering notifications from modules, integrating cart/form feedback, implementing staggered notification sequences, styling notification items, or debugging notification visibility issues. Triggers on any mention of liftrNotification, notification, toast, alert, success message, error message, feedback message, or any user-facing status message within the LIFTR ecosystem."
---

# liftr-notification — LIFTR Notification System

**Version:** 2.0.1
**Source:** `api.notification.js` + `ui.notification.js`
**Global:** `window.liftrNotification`
**UI Component:** `<liftr-notifications>`

---

## 1. Quick Reference

```javascript
liftrNotification.success('Erfolg', 'Produkt wurde hinzugefuegt');
liftrNotification.error('Fehler', 'Etwas ist schief gelaufen');
liftrNotification.info('Info', 'Kostenloser Versand ab 40 EUR');
liftrNotification.warning('Achtung', 'Nur noch 2 auf Lager');

// With options
liftrNotification.success('OK', 'Gespeichert', { duration: 3000, priority: 8 });

// Control
const id = liftrNotification.success('Test', 'Message');
liftrNotification.dismiss(id);
liftrNotification.dismissAll();
```

---

## 2. Installation

### HTML (Liquid)

```liquid
{%- comment -%} popover="manual" is REQUIRED for Top Layer placement {%- endcomment -%}
<liftr-notifications
  liftr-id="notifications"
  popover="manual"
></liftr-notifications>
```

**CRITICAL:** `popover="manual"` is required. Without it, notifications won't appear above modal dialogs.

### JavaScript

```javascript
import './api.notification.js';  // Auto-registers window.liftrNotification
import './ui.notification.js';
```

---

## 3. API Methods

### Notification Types

| Method | Color | Usage |
|--------|-------|-------|
| `success(title, message?, options?)` | Green | Operation completed |
| `error(title, message?, options?)` | Red | Operation failed |
| `info(title, message?, options?)` | Blue | Information |
| `warning(title, message?, options?)` | Orange | Attention needed |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `duration` | number | 4000 | Auto-dismiss in ms (0 = persistent) |
| `priority` | number | 5 | Queue priority (higher = shown first) |

### Programmatic Control

```javascript
const id = liftrNotification.success('Test', 'Message');
liftrNotification.dismiss(id);     // Dismiss specific
liftrNotification.dismissAll();    // Dismiss all + clear queue
```

### Types Import

```javascript
import { TYPES } from './api.notification.js';
TYPES.SUCCESS  // 'success'
TYPES.ERROR    // 'error'
TYPES.INFO     // 'info'
TYPES.WARNING  // 'warning'
```

---

## 4. Event-Based Usage

When the component isn't mounted yet, use events:

```javascript
import { emit } from './core.liftr.js';

emit('liftr:notification:show', {
  type: 'success',
  title: 'Erfolg',
  message: 'Gespeichert',
  duration: 4000,
  priority: 5
});
```

### Listening

```javascript
import { on } from './core.liftr.js';

on('liftr:notification:shown', (e) => {
  const { id, type, title, message } = e.detail;
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
| `persistent` | No auto-dismiss (duration: 0) |
| `success` / `error` / `info` / `warning` | Type styling |

### Roles

| Role | Element | Description |
|------|---------|-------------|
| `notification-item` | div | Individual notification |
| `notification-icon` | span | Type icon |
| `notification-content` | div | Text wrapper |
| `notification-title` | strong | Title |
| `notification-message` | span | Message |
| `notification-close` | button | Dismiss button |

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
[liftr-role~="notification-item"][liftr-state~="persistent"] { }
```

### Custom Properties

| Property | Description |
|----------|-------------|
| `--set-duration-exit` | Exit animation duration (read by JS) |
| `--notification-duration` | Auto-dismiss countdown (set by JS per item) |

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
  liftrNotification.success('Hinzugefuegt',
    `${item.product_title} wurde zum Warenkorb hinzugefuegt`);
});

// Error handling
on('liftr:shop:error', (e) => {
  liftrNotification.error('Fehler', e.detail.error.message);
});

// Form submission
try {
  await submitForm(form);
  liftrNotification.success('Gesendet', 'Vielen Dank fuer deine Nachricht');
} catch (error) {
  liftrNotification.error('Fehler', error.message);
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

- Container: `aria-live="polite"` (add in HTML)
- Each notification: `role="alert"`
- Close buttons: `aria-label="Schliessen"`
