---
name: selectedleafs-pos-operations
description: >-
  Mentales Modell und Betriebsmethoden der selectedleafs POS-Operations auf Make + Airtable
  (Kommissionsware an Kiosk-Partner-Stores). IMMER laden, sobald an POS-Operations gearbeitet
  wird — Airtable-Base gelesen oder geändert, ein Make-Szenario gebaut/gemappt/gedebuggt, ein
  Feld oder eine Formel angefasst, eine neue Konditionen-/Kalkulations-Version angelegt, eine
  Auszahlung oder ein Saldo geprüft. Auch bei reinen Fragen ("warum ist der Saldo so hoch",
  "rechnet das richtig", "darf ich das Feld umbenennen"). Trigger u.a.: POS Operations,
  appiIkOaz1ID1FjfE, Umsätze, Lieferungen, Bestandsprüfungen, Auszahlungen, Konditionen,
  Kalkulationen, Vertriebler, Saldo, Provision, Kostenanteil, Leistungsdatum, Regelbesteuerung,
  Kleinunternehmer, Belegeingang, Lexware-Sync nach Airtable, [Sync]/[Create]/[Process]/
  [Dispatch]/[Notify]/[Maintain]. Ersetzt selectedleafs-pos-operations (v1) und
  selectedleafs-pos-operations-v2.
metadata:
  version: "1.9.0"
---

# selectedleafs · POS Operations

Das Betriebssystem hinter der **Kommissionsware an Kiosk-Partner-Stores**: Vertriebler beliefern Stores, selectedleafs rechnet ab, alles läuft über **Make + Airtable**. Diese Datei ist die **Landkarte** — sie reicht für die meisten Fragen allein. Tiefe steckt in `references/`, exakte Feld-/Szenario-Fakten in den generierten Assets.

> **Leitplanken (gelten überall):**
> 1. **Drift-Firewall.** Diese Datei und die references tragen **Muster + „wo live nachsehen"**, nie eine `fld…`-ID oder Formel **als Fakt**. Volatile Fakten leben in datierten, generierten Blöcken (`airtable/…`-Feld-Block) mit „verify-live"-Kopf; Szenario-Innereien tragen **kein** gespeichertes Zuhause — sie werden bei Bedarf **live** aus dem Szenario gelesen (Make-MCP `scenarios_get`). **Im Zweifel gewinnt die Base / das Live-Szenario.**
> 2. **Ein Fakt, ein Zuhause.** Rechenformel nur in der Tabellen-Datei, hier nur das Muster · Szenario-Innereien nur im Live-Szenario (per Make-MCP gelesen) · Meldetexte nur im Nachrichtenkatalog.
> 3. **Vertrag statt Innereien.** Szenarien über Aufgabe/Trigger/r-w-Felder/Notify-Keys, nicht Modul-für-Modul.

---

## Die sechs Layer — wer schreibt was

Ein Beleg wandert von der Post bis zum Saldo durch sechs Systeme. Jedes hat **eine** Rolle:

| Layer | Rolle | schreibt |
|---|---|---|
| **JTL** | Warenwirtschaft (Quelle der Ausgangsrechnung) | — (Quelle) |
| **Mail-Ingress** (Proton / JTL) | Belege kommen per Mail herein | — (Transport) |
| **Lexware** | Buchhaltung, Belege, Zahlstatus; Vertriebler = **Kreditor/Lieferant** | Belege, Zahlungen |
| **Shopify** | Store-/Produkt-Layer (`liftr_store`-Metaobjekt) | Store-/Produktstamm |
| **Airtable** `appiIkOaz1ID1FjfE` | **Single Source of Truth** | — (Formeln rechnen hier) |
| **Make** (Team 2174024) | **Orchestrierung** | **nur Rohdaten + Links**, nie berechnete Geldwerte |
| **Telegram** | Ausgabe an Operations / Vertriebler / Öffentlichkeit | — (Ausgabe) |

Merksatz: **Airtable ist die Wahrheit, Make ist der Schreiber, die Formeln sind der Rechner.** Wer diese Trennung verletzt (Make schreibt einen Geldwert), bricht das Modell. → `references/model.md`

---

## Die drei Freeze-Invarianten

Der Grund, warum Historie verlässlich bleibt. **Strukturell nicht erzwungen** — getragen von Disziplin und Wächter-Views:

1. **Versionen sind append-only.** `Konditionen` und `Kalkulationen` werden nie editiert, nur neu versioniert (`Gültig ab`). Wer eine alte Version ändert, verschiebt rückwirkend Geld — spurlos.
2. **Ereigniszeilen sind INSERT-only.** Make fügt in `Lieferungen`/`Bestandsprüfungen`/`Umsätze`/`Auszahlungen` nur ein, ändert nie. **Einziger definierter Sonderfall:** der Zahlungseingang setzt einen Status (jetzt über `[Sync] Lexware Payments`).
3. **Make-/Formel-Felder sind unantastbar.** Was Make auflöst oder per Name matcht, gehört Make/den Formeln, nicht der Hand.

→ `references/operations.md` (Wächter-Views, ein Bearbeiter, keine Testbase)

---

## Wie Geld entsteht

Zwei Geldwerte, an **zwei verschiedenen** Tabellen — das ist die Stelle, an der man sich am leichtesten irrt:

- **Kostenanteil** sitzt auf **`Lieferungen`** und wird **bei der Lieferung** abgezogen (der Vertriebler trägt seinen fairen Anteil an den Warenkosten).
- **Provision** sitzt auf **`Umsätzen`** und wird **bei der Zahlung** gutgeschrieben (Provision auf den bezahlten Store-Umsatz).
- Daraus: **`Saldo = Realprovision − Kostenanteil`**, **`Offen = Saldo − Ausgezahlt`**. Der Saldo nutzt **Realprovision** (Provision auf den *bezahlten* Betrag), nicht die nominale Provision; `Ausgezahlt` = Σ `Auszahlungen.Bezahlt`.
- Alles **brutto gegen brutto** (0 % bei Kleinunternehmern, sonst latente Fehler).
- **250 € ist Betriebs-Policy, kein System-Gate.** Es gibt keine „Auszahlung möglich"-Meldung; die Schwelle steht nur in der Onboarding-Kommunikation.

Die konkreten Formeln stehen **nicht hier**, sondern in der jeweiligen Tabellen-Datei (`references/airtable/lieferungen.md`, `…/umsaetze.md`, `…/vertriebler.md`) — dort live geprüft.

---

## Ereignis → Positionen, und die Make-Kopplung

Jede Geschäftshandlung ist eine **Haupttabelle mit Positions-Kindtabelle**. Die Ereignis-Trias:

**`Lieferungen` · `Bestandsprüfungen` · `Umsätze`** (+ `Auszahlungen`) — je mit Positionszeilen darunter.

Manche Felder/Tabellen werden von Make aufgelöst oder per Name gematcht. Drei Bruchmodi, nach Sichtbarkeit:

| Änderung | Symptom |
|---|---|
| Feld/Tabelle **umbenannt** | **laut** — 422, `filterByFormula`/Token brechen sofort |
| **Wert/Option** einer Auswahl geändert | **still** — Match schlägt fehl, kein Fehler |
| **Bedeutung** eines Feldes gewandert | **unsichtbar** — rechnet falsch weiter |

→ `references/model.md` (Tabellenrollen, Kopplung im Detail) · `references/tools.md` (die Fallen der Werkzeuge)

---

## Datum ist money-critical

Versioniert wird **ereignisbasiert**: die jüngste Version mit `Gültig ab ≤ Leistungsdatum` gewinnt. Das **Leistungsdatum ≠ Run-Zeitpunkt** — bei rückdatierten Rechnungen fallen sie auseinander, und genau dann muss die richtige (alte) Kondition greifen. Datum-Fallstricke (ISO+Zeitzone = Vortag · EU-`D/M/JJJJ`-Lesefalle · `cellFormat=string`) → `references/model.md`.

---

## Die Szenario-Achse

Alle Make-Szenarien tragen ein **Rollen-Präfix** (nach der Aufgabe, nicht nach dem Auslöser):

`[Sync]` · `[Create]` · `[Process]` · `[Dispatch]` · `[Notify]` · `[Maintain]` — `[Report]` reserviert, `[Scheduled]` ist **bewusst keine** Achse (ein Zeitplan ist ein Trigger, keine Rolle).

**Dispatch — welche reference wofür:**

| Wenn du … | lies |
|---|---|
| die Base liest/änderst, ein Feld/eine Formel anfasst | `references/model.md` + die passende `references/airtable/<tabelle>.md` |
| ein Feld/eine Option **umbenennst** | `references/model.md` §2 (Marker + Zugriffs-Index) — gekoppeltes Feld erst dort prüfen |
| ein Szenario baust/mappst/debuggst | `references/scenarios.md` (Vertrag) + Live-Szenario per Make-MCP (`scenarios_get(<id>)`) |
| eine Telegram-Meldung baust/prüfst | `references/notify.md` (Grammatik) + `assets/catalog.md` (Texte) + `references/messages.md` (ausgefüllte Übersicht) |
| an Airtable-/Make-MCP-Eigenheiten scheiterst | `references/tools.md` |
| Idempotenz, Fehlerpfad, Registry, Wächter brauchst | `references/operations.md` |

---

## Annahmen (falsifizierbar — Signal, wann sie kippen)

- **Airtable = SSoT, Live gewinnt.** *Bricht, wenn* ein Szenario einen Geldwert schreibt, der nicht aus einer Airtable-Formel/einem Rollup kommt.
- **Der Nachrichtenkatalog ist die Text-SSoT.** *Bricht, wenn* ein Notify-Modul einen Inline-Text trägt, der nicht im Katalog steht.
- **Ein menschlicher Bearbeiter.** Die Freeze-Invarianten sind nur disziplin-getragen. *Bricht, wenn* ein zweiter Schreiber Zugriff auf Versions-/Ereignistabellen bekommt.

---

## Harte Verbote

- **Make schreibt nie einen berechneten Geldwert** — nur Rohdaten + Links.
- **Make-/Formel-Felder nie von Hand anfassen.**
- **Keine Testbase.** Es gibt nur die Produktivbase.
- **Altstand-Base `appAFFDgesKLltBtd` nie anfassen** (eingefroren).
- **Keine volatile `fld…`-ID/Formel als Fakt in Prosa** (Drift-Firewall).

---

## Verzeichnis

**`references/`** — `model.md` (Datenmodell, Geld, Versionierung, Datum, Steuer) · `scenarios.md` (Szenario-Verträge + Topologie) · `notify.md` (Telegram-Grammatik, drei Channels, Renderer-Kontrakt, City-Anker) · `messages.md` (ausgefüllte Nachrichten-Übersicht — Ansicht; Text-SSoT bleibt `assets/catalog.md`) · `tools.md` (Airtable-/Make-MCP-Fallen; Generisches → `global-make-conventions`) · `operations.md` (Idempotenz, Fehlerkonvention, Registry, Wächter-Views) · **`airtable/<tabelle>.md`** (je Tabelle: Zweck · Beziehungen · tragende Felder + datierter Feld-Block).

**`assets/`** — `catalog.md` (Nachrichtenkatalog) · `diagrams/` (`er.html`, `topology.html` — datierte Review-Artefakte) · `examples/` (echte Belege). Szenario-Innereien werden **live** per Make-MCP gelesen (`scenarios_get`) statt als Dump vorgehalten.

**Abgrenzung:** Shopify-Theme → `liftr-*` · City-Marketing/Brand → `selectedleafs-city-content`/`-brand` · generische Make-Mechanik → `global-make-conventions` · Build-Time-Agenten → `global-agent-framework`.
