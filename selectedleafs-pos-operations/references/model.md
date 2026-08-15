# Datenmodell

Wie die Base **denkt** — Tabellen-Kategorien, die 🟣-Konvention, wo Geldwerte entstehen, wie Versionen und Datum zusammenspielen. **Konzept-Ebene.** Die konkreten Felder/Formeln je Tabelle stehen in `airtable/<tabelle>.md` (mit datiertem Feld-Block); hier steht das *Muster*.

> **Stand 2026-08-15**, gegen `appiIkOaz1ID1FjfE` verifiziert. Namen/Struktur sind stabil, aber **im Zweifel gewinnt die Base** — bei Feld-Fragen `airtable/…` bzw. `get_table_schema`.

---

## 1. Vier Tabellen-Kategorien

Jede Tabelle fällt in genau eine Rolle. Wer die Rolle kennt, weiß, was er anfassen darf:

**Ereignis-Tabellen — INSERT-only.** Eine Zeile = eine Geschäftshandlung, unveränderlich:
`Lieferungen` · `Bestandsprüfungen` · `Umsätze` · `Auszahlungen`.
Make fügt ein, ändert nie. **Einziger definierter Sonderfall:** der Zahlungs-Status auf `Umsätze`/`Auszahlungen` (jetzt über `[Sync] Lexware Payments`).

**Positions-Tabellen (🟣) — INSERT-only Kinder.** Die Zeilen unter einem Ereignis:
`🟣 Lieferpositionen` · `🟣 Bestandsprüfungspositionen` · `🟣 Umsatzpositionen`.
Hier entstehen die Positionswerte, die nach oben rollup-en. (`Auszahlungen` hat kein Positionskind.)

**Versions-Tabellen — append-only, eff-dated.** Nie editieren, nur neu versionieren:
`Konditionen` (Provision % + Kostenanteil %) · `Preise` (VK je Produkt) · `Steuersätze`.
Die Wahl fällt am **Leistungsdatum** (§4).

**Stammdaten & Silos.** `Stores` · `Vertriebler` · `Produkte` · `Produktvarianten` · `Städte` · `Stadtteile` · `Bestände` (abgeleiteter Silo, make-getrieben) · `Belege` (Dokument-Drehscheibe mit vier Fach-Links: Umsatz/Lieferung/Bestandsprüfung/Auszahlung).

---

## 2. Die 🟣-Konvention

**🟣** (im Feld-/Tabellennamen) heißt: **gehört Make oder den Formeln, nicht der Hand.** Drei Sorten, die man kennen muss:

- **Dedup-/Match-Schlüssel.** `Lieferungen.ID` = Belegnummer aus dem PDF · `Bestandsprüfungen.ID` = `"BSP-" & ⚙ Store ID & "-" & Datum` (Make baut denselben Wert als `dedupkey` und sucht per `filterByFormula {ID} = …`) · `Produktvarianten.ID` = SKU (Bestands-Schlüssel `"BST-" & Store-Nr & "-" & SKU`) · `Produkte.ID` = SKU-Präfix. **Präfix/Trennzeichen/Datumsformat ändern bricht den Match still.**
- **Namens-Match.** `Stores.Name` — der Restock-Match läuft zeichengenau darüber. Umbenennen bricht still.
- **Volle GIDs.** `Stores.⚙ Shopify GID` (Metaobjekt), `Produkte.⚙ Shopify GID` (Produkt), `Produktvarianten.⚙ Shopify GID` (Variante) — **immer inkl. `gid://shopify/…`-Präfix**, Make normalisiert nicht. Formate nie mischen.

Die drei Bruchmodi (umbenannt = laut 422 · Wert/Option = still · Bedeutung gewandert = unsichtbar) stehen im SKILL.md; die tabellenscharfen Fälle in `airtable/…`.

---

## 3. Wo Geld entsteht (live verifiziert)

Zwei Geldwerte, an **zwei verschiedenen** Ereignis-Tabellen — die Stelle, an der man sich am leichtesten irrt:

| Wert | sitzt auf | Auslöser | Weg zum Vertriebler |
|---|---|---|---|
| **Kostenanteil** | `Lieferungen.Kostenanteil` (Formel) | **Lieferung** | Rollup → `Vertriebler.Kostenanteil` |
| **Provision** | `Umsätze.Provision` (Formel) | **Zahlung** (bezahlter Umsatz) | Rollup → `Vertriebler.Provision` |

Daraus, alles auf `Vertriebler` (live verifiziert):
**`Saldo = ⚙ Realprovision − Kostenanteil`** · **`Offen = Saldo − Ausgezahlt`**.
Achtung: der Saldo nutzt **`⚙ Realprovision`** (Provision auf den *tatsächlich bezahlten* Betrag), **nicht** die nominale `Provision` (auf den vollen Nettoumsatz — die ist nur Anzeige). `Ausgezahlt` = Σ `Auszahlungen.Bezahlt` (real überwiesen). Detail: [[vertriebler]].

**Drei Fallstricke, die hier live sichtbar sind:**

1. **Eingefrorene Kostenwahrheit.** Der Einkaufspreis, mit dem gerechnet wird, steht **eingefroren** auf `🟣 Lieferpositionen.⚙ EK (netto)` — der Wert zum Lieferzeitpunkt. `Produktvarianten.⚙ EK (netto)` ist nur ein **wöchentlicher Spiegel** aus Shopify und **darf nie** in eine Kosten-/Saldoformel. (Gleiches Prinzip macht Historie einfrierbar.)
2. **Erlös ≠ Umsatz.** `⚙ Nettoumsatzerlös` (auf `Umsätze`/`🟣 Umsatzpositionen`) liegt systematisch **über** `Nettoumsatz` — die Store-Rechnung läuft mit Partnerrabatt. Die Lücke ist die **Storemarge**, kein Fehler. **Geldwahrheit bleibt `Nettoumsatz`**; `Nettoumsatzerlös` fließt in **keine** Provisions-/Saldoformel.
3. **250 € ist Policy, kein Gate.** Keine „Auszahlung möglich"-Meldung; die Schwelle lebt nur in der Onboarding-Kommunikation.

(Nebenwerte, nicht saldo-relevant: `Umsätze.Deckungsbeitrag`, `Stores.Storemarge`, `⚙ Realprovision` — Detail in `airtable/umsaetze.md` / `…/vertriebler.md`.)

---

## 4. Versionierung & Datum — money-critical

Preise, Konditionen und Steuersätze sind **eff-dated**: es gewinnt die jüngste Version mit **`Gültig ab ≤ Leistungsdatum`** des Ereignisses.

Das **Leistungsdatum ≠ Run-Zeitpunkt.** Bei einer rückdatierten Rechnung muss die *damals* gültige Version greifen, nicht die heutige — sonst verschiebt sich Geld rückwirkend. Deshalb:

- **Nie** eine bestehende Versionszeile editieren (Freeze-Invariante 1) — immer neu mit neuem `Gültig ab`.
- **Datum-Fallstricke** (Detail in `airtable/…`, weil feld-/format-scharf):
  - **ISO + Zeitzone** → beim Schreiben landet leicht der **Vortag** im Feld.
  - **EU-`D/M/JJJJ`** wird als `M/D` fehlgelesen, wenn die Quelle nicht klar ist.
  - `cellFormat=string` beim Lesen liefert das **angezeigte** Format, nicht ISO — bewusst wählen.

---

## 5. Besteuerung

Pro Vertriebler: `Besteuerung` (Kleinunternehmer / Regelbesteuerung) + `⚙ Regelbesteuerung ab` (Datum des Wechsels). Kleinunternehmer rechnen mit **0 %** — deshalb gilt durchgängig **brutto gegen brutto**, sonst entstehen latente Fehler beim Jahres-/Statuswechsel. Der Steuersatz selbst ist eff-dated (`Steuersätze.Gültig ab`).

---

## Verweise

Feld- und Formel-Detail je Tabelle: **`airtable/<tabelle>.md`** (z. B. `lieferungen.md`, `umsaetze.md`, `vertriebler.md`, `konditionen.md`, `preise.md`, `bestaende.md`).
Das Beziehungsbild: **`assets/diagrams/er.html`** (datiertes Review-Artefakt).
