---
name: selectedleafs-pos-operations
metadata:
  version: "1.0.2"
description: "Konsolidierter Runtime-Skill für die selectedleafs POS-Operations-Agenten (Kommissionsware an Kiosk-Partner-Stores). Bündelt die Domänen Restock (Übergabeprotokoll/Lieferschein auswerten → Drive ablegen → City-Channel posten), generisches Telegram-Handwerk (Format, Pinned, Launch, Channel-Ableitung) und ein Werte-Verzeichnis (Channel-Map, Drive-Root, Operations-Chat) — plus Stubs für Inventory, Invoice, Launch. Jeder Agent liest nur seine reference(s); diese SKILL.md ist die Landkarte (Dispatch + Invarianten), die Tiefe steckt in references/. IMMER laden, sobald ein POS-Operations-Agent eine Aufgabe verarbeitet — auch wenn das Wort Skill nicht fällt. Triggers on: pos-restock, pos-operations, Übergabeprotokoll, Protokoll-Eingang, Kommissionsware, Kommissionär, Lieferschein parsen, Sorten neu vs aufgefüllt, UL-Nummer; telegram post, City-Channel, restock post, neue sorte post, neuer partner post, pinned post, channel setup, channel launch; Bestandsprotokoll, Provisionsabrechnung POS, neuen POS-Partner anlegen."
---

# selectedleafs POS-Operations — Router

Landkarte für die POS-Operations-Agenten. Diese Datei **dispatcht** und hält die domänenübergreifenden **Invarianten** — sie trägt **keine** Domänen-Prozedur. Die operative Tiefe steckt in `references/`. Jeder Agent liest **nur die reference(s) seiner Domäne** (Allowlist), plus `registry.md` für statische Werte und — wo er postet — die generische `telegram.md`.

## Dispatch — welche reference?

| Sub-Task / Auslöser | reference |
|---|---|
| Übergabeprotokoll/Lieferschein auswerten, Store/Stadt/Sorten ableiten, neu vs. aufgefüllt, PDF komprimieren + in Drive ablegen, 📦/🌿 in den City-Channel posten | `references/restock.md` |
| Generisches Telegram-Handwerk: Format-System, Emoji-Legende, Pinned/Launch, Posting-Mechanik, **Channel-Ableitung** (Stadt → Channel, Override-Vorrang) | `references/telegram.md` |
| Statische Werte nachschlagen: City→Channel-Map, Drive-Root-`parentFolderId`, Operations-`chat_id`/Topic, (später) Sheet-IDs | `references/registry.md` |
| Bestandsprotokoll ablegen (ohne OCR/Shopify/Post) | `references/inventory.md` *(Stub)* |
| Provisionsabrechnung POS-Partner (Lexware → Vertriebler-Sheet) | `references/invoice.md` *(Stub)* |
| Neuen POS-Partner anlegen (Metaobjekt + 🎉-Post) | `references/launch.md` *(Stub)* |

Die Post-Templates der Restock-Domäne (📦/🌿) liegen **in** `restock.md`, damit diese Kette ohne Sprung in `telegram.md` auskommt. references referenzieren einander **nicht** quer — wer eine Domäne fährt, kommt mit seiner reference (+ `registry.md`, + ggf. `telegram.md` fürs generische Posting) aus.

## Universelle Invarianten (für alle Domänen)

Diese drei Grundsätze gelten domänenübergreifend; die Domänen-references konkretisieren sie, widersprechen ihnen aber nie:

1. **Idempotenz-Grundsatz — jede Einheit genau einmal.** Vor Posten/Ablegen/Schreiben prüfen, ob die Einheit (Protokoll, Beleg, Partner) schon verarbeitet wurde, und bei Treffer abbrechen. Der **Idempotenz-Schlüssel ist deterministisch aus stabiler Quelle** (z. B. Protokollnummer), nie aus volatilem/geratenem Input. Drive/Ziel ist die Quelle der Wahrheit — kein externer State nötig (web-only-tauglich).
2. **IDs aus Registry oder Webhook — nie raten.** Statische Ziele (Channel, Drive-Root, Operations-Chat) kommen aus `registry.md` bzw. der Agent-Config; lauf-spezifische IDs (`file_id`, per-Lauf `chat_id`) aus der Webhook-Injektion. Ist eine ID nicht eindeutig auflösbar → **nicht öffentlich raten**, sondern still abbrechen + Rückfrage in den Operations-Chat (Mensch-im-Loop-Ersatz).
3. **Append-only bei kuratierten Listen.** Schreibseitige Mutationen an Sortiments-/Listendaten (`product_list` etc.) **nur anhängen, nie entfernen**, idempotent (kein Doppel-Eintrag, kein Clobbern bestehender Werte). Löschen/Auslisten bleibt manueller Menschen-Job.

## Herkunft

`restock.md` = Inhalt aus `selectedleafs-pos-restock` v1.8.0, 1:1 migriert (Migration byte-verifiziert) + Restock-Post-Templates eingezogen; in v1.0.1 die toten Verweise auf den Quell-Skill auf die lokale Template-Sektion bzw. `telegram.md` §2.1 repointet. In **v1.0.2** zwei aus `selectedleafs-pos-restock` **vererbte** (nicht durch die Migration entstandene) Alt-Bugs chirurgisch in `restock.md` gefixt, erstmals durch einen End-to-End-Lauf sichtbar: **§6** — resumable-Upload finalisiert nur mit `Content-Range`-Header; ohne ihn HTTP 308 = nicht committet (vorher fälschlich als Erfolg gewertet). **§2.5 1b** — Detail-Query holt jetzt `google_place` (für den `{maps_link}` der Post-Templates; vorher Platzhalter-Link). `telegram.md` = generisches Handwerk aus `selectedleafs-telegram` (v13), domänenspezifische Templates herausgezogen. Die beiden Quell-Skills werden nach Umstellung der Agenten deprecated.
