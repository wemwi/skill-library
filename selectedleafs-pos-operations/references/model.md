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

Make spricht Airtable auf **zwei** Wegen an — und nur einer davon ist zerbrechlich:

- **Über die Feld-ID** (`returnFieldsByFieldId`, `fields[]`, `useColumnId:true`, `record`-Maps). Die ID ist unveränderlich; das Feld darf beliebig heißen. **Umbenennen ist folgenlos.**
- **Über den Klartext-Namen** — ausschließlich dort, wo Airtable keine Feld-IDs zulässt: in `filterByFormula` und in `sort`. Plus in den dort gematchten **Options-Werten** von Selects. **Umbenennen bricht den Match still** — kein Fehler, kein Log, nur ein Treffer weniger.

Der zweite Fall ist selten (26 von 250 Feldern), aber er trägt die Idempotenz, die eff-dated Versionswahl und die Brücken zu Lexware. Deshalb bekommt genau er den Marker.

### Der 🟣-Marker (Stand 2026-08-21)

Die **erste Zeile** der Feldbeschreibung trägt bei diesen Feldern:

- **`🟣 make.com (KEY · Name)`** — Make matcht über den **Feldnamen**. Name einfrieren.
- **`🟣 make.com (KEY · Options)`** — Make matcht über Feldname **und Optionswert**. Beides einfrieren. Gilt nur für Selects; `Options` ist die Steigerung von `Name`, nie ein anderer Fall (eine Options-Kopplung setzt die Namens-Kopplung immer voraus, weil `filterByFormula` den Feldnamen zwangsläufig mitschreibt).

Die Beschreibung trägt **genau diese eine Zeile** — kein Zusatztext. Wo und warum gematcht wird, steht in `airtable/<tabelle>.md`: ein Fakt, ein Zuhause (Leitplanke 2). Stünde die Begründung zusätzlich in der Base, gäbe es zwei Orte, die bei einer Szenario-Änderung nachgezogen werden müssten — und die Base ist der, den niemand versioniert.

Bewusst in der Beschreibung, nicht im Namen — ein Glyph im Namen bräche den Match, den er schützt. Der Marker ist **Doku, kein Laufzeit-Gate**: eine Beschreibung zu ändern hat auf Make keinen Effekt.

**Was der Marker NICHT trägt: die Richtung.** Ob Make ein Feld liest oder schreibt, ändert an der Handlung nichts, die der Marker auslöst — Namen einfrieren gilt so oder so. Die Richtung steht vollständig in `airtable/<tabelle>.md`, je Tabelle mit Zählung und Feldliste.

**Die Base trägt ausschließlich diese 26 Feld-Marker.** Keine Tabellenbeschreibungen, keine Zusatztexte — alles Erklärende lebt im Skill, wo es versioniert ist und im Review auffällt.

**Prozess-Gegenmaßnahme:** neuer `filterByFormula`- oder `sort`-Zugriff auf ein Feld → 🟣-Marker im selben Zug setzen.

### Die 26 namens-gekoppelten Felder

| Zweck | Felder |
|---|---|
| **Dedup / Idempotenz** | `Umsätze.ID` · `Lieferungen.ID` · `Bestandsprüfungen.ID` · `Bestandsprüfungspositionen.ID` · `Bestände.ID` · `Produktvarianten.ID` · `Stores.ID` |
| **Eff-dated Versionswahl** | `Preise.Gültig ab` + `Preise.Produkt` · `Konditionen.Gültig ab` + `Konditionen.Gültig für` |
| **Lexware-Brücken** | `Stores.Lexware ID` · `Vertriebler.Lexware ID` · `Auszahlungen.Lexware ID` |
| **Namens-Match** | `Stores.Name` · `Vertriebler.Name` · `Städte.Name` · `Stadtteile.Name` |
| **Options-Match** (Selects) | `Belege.Belegtyp` · `Bestandsprüfungen.Status` · `Stores.Status` · `Stores.Modell` · `Konditionen.Gültig für` |
| **Filter / Sort** | `Belege.Datum` · `Belege.Umsatz` · `Stores.Zuletzt geprüft` · `Stores.Fällig gemeldet am` |

`Konditionen.Gültig für` steht bewusst in zwei Zeilen — Zweck ist die eff-dated Auswahl, Mechanismus der Options-Match. Die Tabelle nennt damit 27 Einträge für 26 Felder.

`Konditionen.Gültig für` steht bewusst in zwei Zeilen — Zweck ist die eff-dated Auswahl, Mechanismus der Options-Match. Die Tabelle nennt damit 27 Einträge für 26 Felder.

Feld-Detail (fld-ID, Szenarien, Bruchmodus) je Tabelle in `airtable/<tabelle>.md`, Sektion „🟣 Make-Zugriff".

### Vollständigkeit

Die Karte ist **vollständig**: alle 17 Szenarien des Teams 2174024 wurden am 2026-08-21 per Make-MCP `scenarios_get` gegen die Live-Blueprints gescannt. Ergebnis: 156 der 250 Felder werden von Make berührt — 26 namens-gekoppelt (Marker am Feld), 130 rein fld-ID-fest (Zählung auf Tabellenebene, kein Marker). 94 Felder haben **keinen** Make-Bezug und sind frei.

Drei Tabellen sind **rein lesend** — Make schreibt dort nie: `Konditionen`, `Städte`, `Steuersätze`. Drei sind **rein schreibend**: `Lieferpositionen`, `Umsatzpositionen` (INSERT-only) sowie `Produkte`.

Bruchmodi: Name/Option geändert = **still** · Feld gelöscht oder umtypisiert = **laut** (422) · Bedeutung gewandert = **unsichtbar**. Der Marker deckt den ersten Fall ab. Für den zweiten gibt es kein Signal in der Base — wer ein Feld löschen oder umtypisieren will, prüft `airtable/<tabelle>.md`, Sektion „🟣 Make-Zugriff".

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
