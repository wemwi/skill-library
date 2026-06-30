---
name: selectedleafs-pos-operations
metadata:
  version: "1.3.0"
description: "Konsolidierter Runtime-Skill für die selectedleafs POS-Operations-Agenten (Kommissionsware an Kiosk-Partner-Stores). Bündelt die Domänen Restock (Übergabeprotokoll/Lieferschein auswerten → Drive ablegen → City-Channel posten), generisches Telegram-Handwerk (Format, Pinned, Launch) und ein Werte-Verzeichnis (City→Channel-Map, Drive-Root, Operations-Chat) — plus Stubs für Inventory, Invoice, Launch. Jeder Agent liest nur seine reference(s); diese SKILL.md ist die Landkarte (Dispatch + Invarianten), die Tiefe steckt in references/. IMMER laden, sobald ein POS-Operations-Agent eine Aufgabe verarbeitet — auch wenn das Wort Skill nicht fällt. Triggers on: pos-restock, pos-operations, Übergabeprotokoll, Protokoll-Eingang, Kommissionsware, Kommissionär, Lieferschein parsen, Sorten neu vs aufgefüllt, UL-Nummer; telegram post, City-Channel, restock post, neue sorte post, neuer partner post, pinned post, channel setup, channel launch; Bestandsprotokoll, Provisionsabrechnung POS, neuen POS-Partner anlegen."
---

# selectedleafs POS-Operations — Router

Landkarte für die POS-Operations-Agenten. Diese Datei **dispatcht** und hält die domänenübergreifenden **Invarianten** — sie trägt **keine** Domänen-Prozedur. Die operative Tiefe steckt in `references/`. Jeder Agent liest **nur die reference(s) seiner Domäne** (Allowlist), plus `registry.md` für statische Werte. `telegram.md` ist nur für die Launch-Domäne Pflicht, nicht generisch fürs Posten — Restock postet direkt mit dem Channel-Lookup aus `registry.md`.

## Dispatch — welche reference?

| Sub-Task / Auslöser | reference |
|---|---|
| Übergabeprotokoll/Lieferschein auswerten, Store/Stadt/Sorten ableiten, neu vs. aufgefüllt, PDF komprimieren + in Drive ablegen, 📦/🌿 in den City-Channel posten (Channel-Ziel aus `registry.md`, kein `telegram.md`-Load nötig) | `references/restock.md` |
| Generisches Telegram-Handwerk (Launch/Setup-Domäne): Format-System, Emoji-Legende, Pinned/Launch, Posting-Mechanik | `references/telegram.md` |
| Statische Werte nachschlagen: City→Channel-Map (direkter Lookup, kein Override-Mechanismus), Drive-Root-`parentFolderId`, Operations-`chat_id`/Topic, (später) Sheet-IDs | `references/registry.md` |
| Bestandsprotokoll ablegen — Store-Match (Name → Metaobjekt) + Datum lesen, **ohne** Sorten-Parsing/Write-back/Post | `references/inventory.md` |
| Provisionsabrechnung POS-Partner (Lexware → Vertriebler-Sheet) | `references/invoice.md` *(Stub)* |
| Neuen POS-Partner anlegen (Metaobjekt + 🎉-Post) | `references/launch.md` *(Stub)* |

Die Post-Templates der Restock-Domäne (📦/🌿) liegen **in** `restock.md`, damit diese Kette ohne Sprung in `telegram.md` auskommt. City→Channel ist ein direkter Lookup in `registry.md` — kein Ableitungsmechanismus, kein Override, da Test- und Prod-Agenten getrennte System-Prompts/Configs fahren (`global-agent-framework`), nicht einen geteilten Per-Run-Schalter. references referenzieren einander **nicht** quer — wer eine Domäne fährt, kommt mit seiner reference (+ `registry.md`) aus; `telegram.md` ist nur für die Launch-Domäne Pflicht.

## Universelle Invarianten (für alle Domänen)

Diese drei Grundsätze gelten domänenübergreifend; die Domänen-references konkretisieren sie, widersprechen ihnen aber nie:

1. **Idempotenz-Grundsatz — jede Einheit genau einmal.** Vor Posten/Ablegen/Schreiben prüfen, ob die Einheit (Protokoll, Beleg, Partner) schon verarbeitet wurde, und bei Treffer abbrechen. Der **Idempotenz-Schlüssel ist deterministisch aus stabiler Quelle** (z. B. Protokollnummer), nie aus volatilem/geratenem Input. Drive/Ziel ist die Quelle der Wahrheit — kein externer State nötig (web-only-tauglich).
2. **IDs aus Registry oder Webhook — nie raten.** Statische Ziele (Channel, Drive-Root, Operations-Chat) kommen aus `registry.md` bzw. der Agent-Config; lauf-spezifische IDs (`file_id`, per-Lauf `chat_id`) aus der Webhook-Injektion. Ist eine ID nicht eindeutig auflösbar → **nicht öffentlich raten**, sondern still abbrechen + Rückfrage in den Operations-Chat (Mensch-im-Loop-Ersatz).
3. **Append-only bei kuratierten Listen.** Schreibseitige Mutationen an Sortiments-/Listendaten (`product_list` etc.) **nur anhängen, nie entfernen**, idempotent (kein Doppel-Eintrag, kein Clobbern bestehender Werte). Löschen/Auslisten bleibt manueller Menschen-Job.
