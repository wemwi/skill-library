# Datenmodell

Wie die Base **denkt** — Tabellen-Kategorien, die Make-Kopplung, wo Geldwerte entstehen, wie Versionen und Datum zusammenspielen. **Konzept-Ebene.** Die konkreten Felder/Formeln je Tabelle stehen in `airtable/<tabelle>.md` (mit datiertem Feld-Block); hier steht das *Muster*.

> **Stand 2026-08-15**, gegen `appiIkOaz1ID1FjfE` verifiziert. Namen/Struktur sind stabil, aber **im Zweifel gewinnt die Base** — bei Feld-Fragen `airtable/…` bzw. `get_table_schema`.

---

## 1. Vier Tabellen-Kategorien

Jede Tabelle fällt in genau eine Rolle. Wer die Rolle kennt, weiß, was er anfassen darf:

**Ereignis-Tabellen — INSERT-only.** Eine Zeile = eine Geschäftshandlung, unveränderlich:
`Lieferungen` · `Bestandsprüfungen` · `Umsätze` · `Auszahlungen`.
Make fügt ein, ändert nie. **Einziger definierter Sonderfall:** der Zahlungs-Status auf `Umsätze`/`Auszahlungen` (jetzt über `[Sync] Lexware Payments`).

**Positions-Tabellen — INSERT-only Kinder.** Die Zeilen unter einem Ereignis:
`Lieferpositionen` · `Bestandsprüfungspositionen` · `Umsatzpositionen`.
Hier entstehen die Positionswerte, die nach oben rollup-en. (`Auszahlungen` hat kein Positionskind.)

**Versions-Tabellen — append-only, eff-dated.** Nie editieren, nur neu versionieren:
`Konditionen` (Provision % + Kostenanteil %) · `Preise` (VK je Produkt) · `Steuersätze`.
Die Wahl fällt am **Leistungsdatum** (§4).

**Stammdaten & Silos.** `Stores` · `Vertriebler` · `Produkte` · `Produktvarianten` · `Städte` · `Stadtteile` · `Bestände` (abgeleiteter Silo, make-getrieben) · `Belege` (Dokument-Drehscheibe mit vier Fach-Links: Umsatz/Lieferung/Bestandsprüfung/Auszahlung).

---

## 2. Feld-Konvention & Make-Kopplung

**Die einzige verbliebene Namenskopplung sitzt in `filterByFormula`-Strings** (Airtable erlaubt dort keine Feld-IDs) — plus in den dort gematchten Options-Werten und Sortier-Feldern. Reads/Writes sind sonst überall ID-fest (`returnFieldsByFieldId` / `useColumnId:true`). Drei Kopplungsarten:

- **Dedup-/Match-Schlüssel.** `Lieferungen.ID` = Belegnummer aus dem PDF · `Bestandsprüfungen.ID` = `"BSP-" & Store ID & "-" & Datum` (Make baut denselben Wert als `dedupkey` und sucht per `filterByFormula {ID} = …`) · `Bestände.ID` = `"BST-" & Store-Nr & "-" & SKU` · `Produktvarianten.ID` = SKU. **Präfix/Trennzeichen/Datumsformat ändern bricht den Match still.**
- **Namens-Match & Werte-Match.** `Stores.Name`/`Vertriebler.Name` (zeichengenau) · Selects, deren **Optionen** als String gematcht werden (`Belegtyp`, `Status`, `Modell`, `Typ`, `Gültig für`). Umbenennen von Feld **oder** Option bricht still.
- **Volle GIDs.** `Stores.Shopify GID` (Metaobjekt), `Produkte.Shopify GID`, `Produktvarianten.Shopify GID` — **immer inkl. `gid://shopify/…`-Präfix**, Make normalisiert nicht.

Bruchmodi: umbenannt = **laut** (422) · Wert/Option geändert = **still** · Bedeutung gewandert = **unsichtbar**.

### Marker (Stand 2026-08-20)

Feld-Beschreibungen tragen in der **ersten Zeile** einen 🟣-Zugriffsmarker — er sagt, **wie Make das Feld anfasst**:

- **`🟣 make.com (READ)`** — Make liest/matcht (filterByFormula-Match, eff-dated Versionsauswahl, Lookup-Quelle), schreibt den Wert aber nicht.
- **`🟣 make.com (WRITE)`** — Make setzt den Wert (Status/Optionen als String, gesetzte Links).
- **`🟣 make.com (READ+WRITE)`** — Make schreibt beim Insert **und** liest/matcht (Dedup-/Idempotenz-Schlüssel).

Bewusst in der Beschreibung, nicht im Namen (ein Glyph im Namen bräche den Match, den er schützt) — kein Namens-Glyph, keine View, keine Feldberechtigungen. Der Marker ist **Doku, kein Laufzeit-Gate**: eine Beschreibung zu ändern hat keinen Effekt auf Make; das Umbenennen des Feld- oder Optionsnamens dagegen bricht READ-Matches still. Prozess-Gegenmaßnahme: **neuer Make-Zugriff (`filterByFormula`/String-Write) → 🟣-Marker im selben Zug setzen.**

### Zugriffs-Index (welcher Marker auf welchem Feld — Detail am Feld in `airtable/<tabelle>.md`)

- **READ:** `Belege.Belegtyp` · `Bestandsprüfungen.ID` · `Bestandsprüfungspositionen.ID` · `Bestände.ID` · `Konditionen.Gültig ab`+`Gültig für`+`Provision`+`Kostenanteil` · `Produkte.Typ` · `Preise.Gültig ab`+`Produkt` · `Stadtteile.Name`+`Stadt` · `Städte.Name` · `Stores.Modell`+`Lexware ID`+`Zuletzt geprüft` · `Vertriebler.Name`+`Lexware ID`.
- **WRITE:** `Auszahlungen.Status` · `Bestandsprüfungen.Status` · `Lieferungen.Status` · `Umsätze.Status` · `Belege.Umsatz`.
- **READ+WRITE:** `Auszahlungen.Lexware ID` · `Belege.Datum` · `Lieferungen.ID` · `Produktvarianten.ID` · `Umsätze.ID` · `Stores.Name`+`Status`+`Fällig gemeldet am`.

Was der Marker **nicht** abbildet: fld-ID-feste Zugriffe (`returnFieldsByFieldId`/`useColumnId`) sind rename-sicher und bleiben bewusst markerlos — die Karte umfasst nur die **namens-/options-gekoppelten** Felder, bei denen ein Rename bricht. Goldstandard ohne jede Namenskopplung: `[Sync] Products` (in-Code-GID), `[Notify] Telegram` (`RECORD_ID()`).

*Marker-Menge = die 32 namens-/options-gekoppelten Felder aus dem vollständigen Live-Scan aller 17 Szenarien (2026-08-19/20, Make-MCP `scenarios_get`).*

---

## 3. Wo Geld entsteht (live verifiziert)

Zwei Geldwerte, an **zwei verschiedenen** Ereignis-Tabellen — die Stelle, an der man sich am leichtesten irrt:

| Wert | sitzt auf | Auslöser | Weg zum Vertriebler |
|---|---|---|---|
| **Kostenanteil** | `Lieferungen.Kostenanteil` (Formel) | **Lieferung** | Rollup → `Vertriebler.Kostenanteil` |
| **Provision** | `Umsätze.Provision` (Formel) | **Zahlung** (bezahlter Umsatz) | Rollup → `Vertriebler.Provision` |

Daraus, alles auf `Vertriebler` (live verifiziert):
**`Saldo = Realprovision − Kostenanteil`** · **`Offen = Saldo − Ausgezahlt`**.
Achtung: der Saldo nutzt **`Realprovision`** (Provision auf den *tatsächlich bezahlten* Betrag), **nicht** die nominale `Provision` (auf den vollen Nettoumsatz — die ist nur Anzeige). `Ausgezahlt` = Σ `Auszahlungen.Bezahlt` (real überwiesen). Detail: [[vertriebler]].

**Drei Fallstricke, die hier live sichtbar sind:**

1. **Eingefrorene Kostenwahrheit.** Der Einkaufspreis, mit dem gerechnet wird, steht **eingefroren** auf `Lieferpositionen.EK (netto)` — der Wert zum Lieferzeitpunkt. `Produktvarianten.EK (netto)` ist nur ein **wöchentlicher Spiegel** aus Shopify und **darf nie** in eine Kosten-/Saldoformel. (Gleiches Prinzip macht Historie einfrierbar.)
2. **Erlös ≠ Umsatz.** `Nettoumsatzerlös` (auf `Umsätze`/`Umsatzpositionen`) liegt systematisch **über** `Nettoumsatz` — die Store-Rechnung läuft mit Partnerrabatt. Die Lücke ist die **Storemarge**, kein Fehler. **Geldwahrheit bleibt `Nettoumsatz`**; `Nettoumsatzerlös` fließt in **keine** Provisions-/Saldoformel.
3. **250 € ist Policy, kein Gate.** Keine „Auszahlung möglich"-Meldung; die Schwelle lebt nur in der Onboarding-Kommunikation.

(Nebenwerte, nicht saldo-relevant: `Umsätze.Deckungsbeitrag`, `Stores.Storemarge`, `Realprovision` — Detail in `airtable/umsaetze.md` / `…/vertriebler.md`.)

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

Pro Vertriebler: `Besteuerung` (Kleinunternehmer / Regelbesteuerung) + `Regelbesteuerung ab` (Datum des Wechsels). Kleinunternehmer rechnen mit **0 %** — deshalb gilt durchgängig **brutto gegen brutto**, sonst entstehen latente Fehler beim Jahres-/Statuswechsel. Der Steuersatz selbst ist eff-dated (`Steuersätze.Gültig ab`).

---

## Verweise

Feld- und Formel-Detail je Tabelle: **`airtable/<tabelle>.md`** (z. B. `lieferungen.md`, `umsaetze.md`, `vertriebler.md`, `konditionen.md`, `preise.md`, `bestaende.md`).
Das Beziehungsbild: **`assets/diagrams/er.html`** (datiertes Review-Artefakt).
