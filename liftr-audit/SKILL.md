---
name: liftr-audit
description: >-
  Prüf-Checkliste für LIFTR-Theme-Code (HTML/Liquid, CSS, JS, Schema) mit
  Audit-Szenarien und Grep-Befehlen. Nur laden, wenn ausdrücklich ein Audit,
  Code-Review oder eine Compliance-Prüfung des LIFTR-Themes verlangt wird —
  nicht als Vorab-Check bei normaler Umsetzung.
metadata:
  version: "1.0.0"
---

# LIFTR Audit

Systematische Prüfung von bestehendem LIFTR-Theme-Code. Dieser Skill liefert das **Was und in welcher
Reihenfolge**; das **Warum und Wie** für Fixes steht in liftr-foundation, liftr-components, liftr-liquid und
liftr-commerce. Geprüft gegen liftr-shopify-theme main, Stand 28.10.2026.

## Wann was lesen

| Aufgabe | Datei |
|---|---|
| Szenario wählen (eine Section, ein Modul, alle Sections, ganzes Theme), Checklisten HTML/CSS/JS/Schema, Grep-Befehle für die Schnell-Triage | `references/checklist.md` |

Befunde nach Schwere gruppieren: Kritisch (kaputt) → Warnung (falsch) → Info (suboptimal).
