---
name: liftr-debug
description: Systematic debugging methodology for CSS and JavaScript. Use when debugging any frontend issue, layout problem, or JavaScript error. Covers Occam's Razor principle, 5-level debug hierarchy (Existence → Reachability → Value → Timing → Interaction), CSS box model fundamentals, and "basics before hypotheses" approach. Prevents wasted time on complex theories when simple causes exist.
---

# Systematic Debugging

Universal principles for frontend debugging. Apply to CSS, JavaScript, and framework issues.

## Core Philosophy

**Occam's Razor:** The simplest explanation is usually correct.

**"Horses, not Zebras":** When you hear hoofbeats, think horses, not zebras.

**Implication:** Check fundamentals before forming complex hypotheses. A timing problem cannot be debugged if the variable doesn't exist.

## Debug Hierarchy

Work bottom-to-top. Higher levels are meaningless if lower levels fail.

```
Level 5: INTERACTION   Race conditions, module communication, memory leaks
Level 4: TIMING        Event order, async/await, lifecycle
Level 3: VALUE         Expected value/type? null vs undefined?
Level 2: REACHABILITY  Selector correct? Import path valid? Element exists?
Level 1: EXISTENCE     Does the variable/function/property exist at all?
```

## Level 1: Existence

**Question:** Does it exist?

| Symptom | Likely Cause |
|---------|--------------|
| `undefined is not a function` | Method doesn't exist |
| `X is not defined` | Import missing or renamed |
| Property returns `undefined` | Wrong property name |

**Actions:**
```javascript
console.log(typeof myFunction);      // "undefined"? → doesn't exist
console.log(Object.keys(myObject));  // list all properties
```

## Level 2: Reachability

**Question:** Can it be found/reached?

| Symptom | Likely Cause |
|---------|--------------|
| `null` returned | Selector wrong or element not in DOM |
| Import fails | Path incorrect |
| Attribute empty | Attribute on wrong element |

**Actions:**
```javascript
document.querySelector('[my-attr]');           // null? → not found
document.querySelectorAll('[my-attr]').length; // 0? → doesn't exist
element.getAttribute('my-attr');               // null? → wrong element
```

## Level 3: Value

**Question:** Is the value what you expect?

| Symptom | Likely Cause |
|---------|--------------|
| Unexpected behavior | Type mismatch (string vs boolean) |
| Fallback used | Config property undefined |
| Wrong calculation | String concatenation instead of math |

**Actions:**
```javascript
console.log(typeof value, value);  // "string" "100" vs "number" 100
console.log(value === true);       // false if value is "true" (string)
```

## Level 4: Timing

**Question:** Does it happen at the right time?

| Symptom | Likely Cause |
|---------|--------------|
| Element is null | DOM not ready yet |
| Event not received | Listener registered too late |
| Data undefined | Async not awaited |

**Actions:**
```javascript
console.log('Element:', element, 'at', performance.now());
// Compare timestamps to understand execution order
```

## Level 5: Interaction

**Question:** Do parts work correctly together?

| Symptom | Likely Cause |
|---------|--------------|
| Intermittent failures | Race condition |
| Memory grows | Cleanup forgotten |
| Double execution | Listener registered twice |

---

## CSS Fundamentals

Check these FIRST for any CSS layout issue.

### Box Sizing

```css
box-sizing: border-box;   /* width/height INCLUDES padding + border */
box-sizing: content-box;  /* width/height is CONTENT ONLY, padding added */
```

**Common trap:** `height: 100%` with `padding` and `border-box` → content area shrinks.

```css
/* Problem */
.container {
  box-sizing: border-box;
  height: 100%;           /* = 200px total */
  padding: 20px;          /* content = 160px (200 - 40) */
}

/* Fix: use content-box when height must not shrink */
.container {
  box-sizing: content-box;
  height: 100%;           /* = 200px content */
  padding: 20px;          /* total = 240px, but content stays 200px */
}
```

### Height Inheritance

`height: 100%` only works if parent has explicit height.

```css
/* FAILS - parent has no height */
.parent { }
.child { height: 100%; }  /* 100% of nothing = nothing */

/* WORKS - explicit parent height */
.parent { height: 400px; }
.child { height: 100%; }  /* = 400px */

/* WORKS - absolute positioning creates implicit height */
.parent { position: absolute; inset: 0; }
.child { height: 100%; }  /* = parent's computed height */
```

**Trap:** `flex: 1` gives computed height, but child `height: 100%` may not see it as "explicit."

### Container Queries

`container-type: size` measures **content-box**, not border-box.

```css
.container {
  container-type: size;
  height: 200px;
  padding: 20px;
}
.child {
  height: 100cqh;  /* = 160px (content-box), NOT 200px */
}
```

### Display & Overflow

```css
/* Block elements */
width: auto;    /* fills parent (inherited) */
height: auto;   /* shrinks to content (calculated) */

/* This asymmetry is why X-axis "just works" but Y-axis needs explicit heights */
```

### Quick Checks

| Issue | First Check |
|-------|-------------|
| Element too small | `box-sizing` + padding interaction |
| `height: 100%` fails | Parent has explicit height? |
| Container query wrong size | Padding on container? (measures content-box) |
| Child overflows parent | `min-height: 0` on flex/grid children |
| Flex child doesn't shrink | `min-width: 0` or `overflow: hidden` |

---

## Debug Checklist

### Before Debugging

1. [ ] What EXACTLY is the symptom?
2. [ ] What do I EXPECT to happen?
3. [ ] Start at Level 1, not Level 5

### During Debugging

1. [ ] Verify, don't assume
2. [ ] One change at a time
3. [ ] If Level N fails, don't proceed to Level N+1

### After Fix

1. [ ] Do I understand WHY it failed?
2. [ ] Is this a pattern that needs documentation?
3. [ ] Could this have been caught earlier?

---

## Anti-Patterns

**❌ Jumping to Level 5:**
> "It must be a race condition!"
> → But the import was missing.

**❌ Assumptions instead of verification:**
> "The config is definitely correct"
> → Typo in attribute name.

**❌ Complex solutions for simple problems:**
> "Let's add Container Queries and flex chains"
> → `box-sizing: content-box` was the fix.

**❌ Changing multiple things at once:**
> Changed 3 properties, it works now
> → Which one fixed it? Unknown.
