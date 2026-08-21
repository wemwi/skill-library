# Handover — DRY-Umbau, offene Liste

> **Stand 2026-08-21.** Datiertes Übergabe-Artefakt. Was hier als *erledigt* steht, ist an einem
> echten Produktionslauf gegengelesen, nicht am Blueprint. Was als *offen* steht, ist nicht
> angefangen. Im Zweifel gewinnt die Live-Base — dieses Dokument ist Arbeitskopie, keine Wahrheit.

Ergänzt [[duplication-map]] (die Kartierung) und [[reference-inventory]] (die Umhäng-Liste). Beide
sind weiterhin gültig; hier steht nur, **was als Nächstes zu tun ist und was dabei schiefgehen kann**.

---

## 1 · Was steht

| Baustein | Nutzer | Verifiziert an |
|---|---|---|
| **`[Resolve] Positions`** | `[Process] Upload PDF (Inventory)` | `BSP-10034-2026-08-13`, 9/9 Positionen, Abgeschlossen |
| | `[Process] Invoice (Store)` | Umsatz `RG-10117-1`, 5/5 Positionen, Hinweisfeld leer |
| **`[Archive] Document PDF`** | beide Uploader | `BLG-00097` → `UL-10048-1.pdf` · `BLG-00096` → `BSP-10034-2026-08-13.pdf` |

Modulzahlen: Inventory 47 → 43 · Invoice (Store) 48 → 49 · Delivery 36 → 34.

Der Zuwachs bei Invoice (Store) ist kein Fehler — dort braucht der Aufruf eine Weiche (§4).

---

## 2 · Das Arbeitsprotokoll, das sich bewährt hat

Es ist an einem verlorenen halben Tag entstanden. **Nicht abkürzen.**

1. **Baustein bauen und für sich beweisen**, bevor ein Aufrufer ihn sieht. Minimalversuch: ein Kind
   aus zwei Modulen, das eine Konstante zurückgibt. Erst wenn der Wert ankommt, den echten bauen.
2. **Werte messen, nie Operations-Zahlen interpretieren.** Ein `code:ExecuteCode` hinter dem Aufruf,
   das mit den Rohwerten **wirft** — die Meldung steht im `scenarios_run`-Ergebnis. Ob
   `CallSubscenario` als Operation zählt, ist ungeklärt; „N Operations" ist zwischen „Sonde lief" und
   „Sonde lief nicht, dafür zählte der Aufruf" nicht unterscheidbar. Genau diese Mehrdeutigkeit hat
   den halben Tag gekostet.
3. **Aufrufer-Umbau als Import-JSON liefern** (Rollback + Migriert), nie per `scenarios_update` auf
   einen Produktions-Worker.
4. **Nach jedem Import zwei Dinge zurücksetzen — in dieser Reihenfolge:**
   **erst Scheduling** (`scenarios_update`, ohne Blueprint) auf `on-demand`, **dann das Interface**
   (`scenarios_set-interface`). Umgekehrt leert das Update das Interface gleich wieder, und solange
   das Scheduling nicht `on-demand` ist, weist Make Pflicht-Eingaben ab. **Der Import kippt beides,
   jedes Mal.** Bisher 5 von 5 Importen.
5. **Live gegen den Blueprint gegenlesen** — Modul für Modul, plus Restreferenzen auf die entfernten
   Modul-IDs.
6. **Echten Lauf abwarten und in Airtable prüfen.** „Lauf ist durch" ist kein Ergebnis.
7. **Erst danach** die Karte fortschreiben.

---

## 3 · Fallen, die schon Blut gekostet haben

Ausführlich in [[tools]]. Hier nur, was beim nächsten Schnitt sofort greift:

- **`Return output` im Kind braucht `metadata.expect`** mit allen Ausgabefeldern (bei `array`
  inklusive `spec`). Fehlt der Block, sendet das Kind eine leere Nutzlast, der Aufrufer bekommt ein
  Bundle mit lauter `null` — der Lauf sieht erfolgreich aus und bucht nichts. Der Designer schreibt
  ihn beim Speichern, per API gebaute Kinder nicht.
- **Rückgabe lesen: `{{<modul-id>.<output-name>}}`, flach.** Nicht `.data.`, nicht `.result.`.
  Arrays von Objekten kommen vollständig an. `executionId` ist beim wartenden Aufruf `null`.
- **Ein leeres Array an einer `required`-Eingabe beendet den Lauf** mit
  `[ValidationError] Scenario input validation failed`.
- **`metadata.expect` am *Aufrufmodul* gatet zur Laufzeit nichts** — validiert wird gegen das
  aktuelle Interface des Kindes. Ein Interface-Typ lässt sich also am Kind ändern, ohne den Aufrufer
  anzufassen.
- **Durchreich-Eingaben sind `text`** — nicht `url`, nicht `date`.
- **Ein `builtin:BasicIfElse` + `BasicMerge` zwischen Aufruf und Verbraucher ist unschädlich**
  (gemessen, beide Pfade).

---

## 4 · Die Regel für jeden weiteren Aufrufer

> **Hatte die alte Positionsschleife keinen Filter, braucht der Resolver-Aufruf eine Weiche.**

Inventory: der alte Feeder trug den Filter „Positions bookable" — die neuen Module übernehmen ihn,
fertig. Invoice (Store): der alte Feeder hatte **keinen** Filter, lief bei leerer Positionsliste
einfach leer durch, und das nachgelagerte Verdikt schrieb trotzdem den Grund ins Wächterfeld. Ohne
Weiche würde der Worker dort künftig **hart abbrechen statt zu protokollieren**. Deshalb:
`BasicIfElse` auf `anzahl > 0`, beide Zweige `merge: true`, `BasicMerge` dahinter, und das
Join-Modul unterscheidet „nichts geschickt" von „Resolver hat nicht geantwortet".

**Für Delivery ist das noch nicht geprüft.** Erster Schritt dort: hat der Feeder einen Filter?

---

## 5 · Offene Liste, in der Reihenfolge, die ich empfehle

### 5.1 · A9 — echter Fehler, klein, unabhängig

In `[Create] New Sales Member` referenziert das Modul „Airtable: Konditionen (eff-dated)"
`{{3.result.heute}}` — **dieses Feld gibt Modul 3 gar nicht zurück.** Das Datumsprädikat läuft leer;
gezogen wird faktisch nur „neueste Version mit passender Besteuerung". Heute zufällig richtig, weil
es eine Onboarding-Vorschau ist. In einem Geldpfad wäre es falsch.

Kein Resolver nötig, kein Subszenario. Nur reparieren — und dabei entscheiden, ob das Modul das
Datum überhaupt braucht oder ob der Bezug ersatzlos weg kann.

### 5.2 · A2 · A3 · A4 · A6 · A7 · A8 — stille Divergenzen

Keine Entscheidung nötig, alle risikoarm, alle **eigenständig nützlich** — sie lohnen sich auch,
wenn nie ein weiterer Resolver gebaut wird. Und sie sind die Vorbedingung für Stufe 3 und 4.

| # | Was | Vorlage |
|---|---|---|
| A2 | Eine Namens-Normalisierung für `Stores.Name` | Delivery-`norm()` |
| A3 | Ein Namensvergleich für `Vertriebler.Name` + hartes Verhalten bei 0 / >1 Treffern | Delivery |
| A4 | Ein Datumsvergleich für `Konditionen.Gültig ab` + Gleichstand-Guard | Delivery / `IS_AFTER` |
| A6 | Klingel-`onerror`: `Resume` **oder** `Ignore`, nicht beides | — |
| A7 | Fehler-`ctx`: `Stufe` überall als Input | — |
| A8 | Anker-Ausschluss (`RECORD_ID() != …`) auch in Delivery | Inventory |

### 5.3 · Delivery B5 — der letzte Positions-Schnitt

Der schwierigste. **18 Referenzen** (Inventory hatte 6 gezählt/1 echt, Invoice (Store) 6 gezählt/2
echt — bei Delivery also vorher neu zählen, die Schätzungen der Karte lagen zweimal zu hoch).

Zwei Eigenschaften, die kein anderer Nutzer hat und die **beide im Resolver gebaut, aber noch nie
produktiv gelaufen sind**:

- **`create_missing_stock: true`** — Delivery ist der einzige, der über den Resolver **schreibt**
  (`airtable:upsertRecord` auf `Bestände`). Nur eine Lieferung darf ein Sortiment eröffnen.
- **`purchase_source: stock_avg`** — der Rückhol-Zweig zieht `Bestände.Ø EK (netto)` statt
  `Produktvarianten.EK (netto)`.

**Vor dem Bau zu klären:**
1. Hat der Positions-Feeder einen Filter? (§4)
2. Lassen sich `create_missing_stock` und `stock_avg` isoliert testen, bevor sie im Geldpfad laufen?
   Ein Store mit einer SKU ohne Bestandszeile wäre der saubere Prüffall — **vorher mit Joscha
   abstimmen, das legt einen echten Datensatz an.**

### 5.4 · Stufe 3 — `[Resolve] Store` (aus B1)

Der reichweitenstärkste Baustein: fünf potenzielle Nutzer (Delivery, Inventory, Invoice (Store),
`[Sync] Inventory to Shopify`, `[Notify] Telegram`), plus die Rückholung als sechsten.

**Erst nach A1 und A2.** A1 ist entschieden (2026-08-21: Name-Fallback für beide Worker, mit
Pflicht-Warnung im Verdikt; >1 Namenstreffer bleibt harter Fehler), aber **noch nicht umgesetzt** —
und die Umsetzung ändert das Verhalten von Delivery. Kontrakt-Skizze: K2 in [[duplication-map]].

Der Dedup-Schlüssel gehört **nicht** in diesen Baustein (Schichtvermischung). Der Aufrufer bildet ihn
aus `store_number` + Belegdatum; er muss zeichengleich zur Formel in `Bestandsprüfungen.ID` bleiben.

### 5.5 · Stufe 4 — `[Resolve] Salesperson & Conditions` (aus B2 + B3)

Zuletzt, weil hier das Geld hängt. Erst nach A3–A5.

**Ehrliche Einschränkung, die eine Entscheidung braucht:** heute hat der Baustein nur **zwei** echte
Nutzer im Geldpfad. Bei zwei Nutzern ist ein Subszenario grenzwertig. Er lohnt sich, *weil die
Rückholung der dritte wird* — **kommt die Rückholung nicht, ist die Angleichung A3–A5 der Gewinn und
die Extraktion verzichtbar.** Das ist Joschas Entscheidung, nicht die des Umsetzenden.

A5 ist entschieden: **`Vertriebler.⚙ Regelbesteuerung ab` ist die alleinige Maschinenwahrheit**, das
Select `Besteuerung` ist menschlicher Eingang und Anzeige. Steht in [[airtable/vertriebler]].

---

## 6 · Aufräumen (wartet auf Joschas Wort)

- **Testszenarien im Ordner `Resolver`:** `[Test] Echo Child` · `[Test] Echo Caller` ·
  `[Test] Echo Caller Plain`. `[Test] Resolver Caller` würde ich **behalten** — damit lässt sich der
  Resolver nach jeder Änderung in Sekunden gegenprüfen.
- **Drei Leichen in `Bestandsprüfungen`:** `rec4NRu7Ih0KQ76Jd` (12:18) · `recsQU1Mp2MfZxxEn` (13:42,
  aus einem meiner Läufe) · `recJDByvwmXm8ejfQ` (14.08.). Alle 0 Positionen, Schlüssel `#ERROR!`,
  blockieren nichts. INSERT-only-Tabelle — **nicht ohne Freigabe löschen.**

---

## 7 · Was ohne Rückfrage nicht angefasst wird

- **Keine Schreibvorgänge auf echte Datensätze zum Testen.** Am 2026-08-21 habe ich den Anhang von
  `BLG-00084` für einen Rauchtest zweimal ersetzt (Inhalt identisch, Name am Ende korrekt) — hätte
  ich vorher ansagen müssen.
- **Kein Löschen in den Ereignis-Tabellen** (`Bestandsprüfungen`, `Umsätze`, `Lieferungen` und ihre
  Positionen).
- **Kein `scenarios_update` mit Blueprint auf einen Produktions-Worker** — Änderungen gehen als
  Import-JSON, das Joscha prüft.
- **Kein Vereinheitlichen über eine Divergenz hinweg, ohne sie zu markieren.** Ein geteilter Baustein
  über subtil abweichende Logik bricht still einen der Nutzer.

---

## 8 · Offene Fragen an Joscha

1. **Rückholung** — kommt sie? Davon hängt ab, ob Stufe 4 überhaupt gebaut wird (§5.5).
2. **A1-Umsetzung** — der Name-Fallback ändert Delivery-Verhalten. Wann?
3. **iLovePDF** — fällt intermittierend aus (2 von 8 Läufen am 2026-08-21, beide Größen,
   Wiederholung jeweils erfolgreich). Lohnt ein Blick ins Kontingent, oder bleibt es beim
   `Ignore`-Pfad plus dem neuen Erkennungsmerkmal (2 statt 4 Operations im Kind-Lauf)?
