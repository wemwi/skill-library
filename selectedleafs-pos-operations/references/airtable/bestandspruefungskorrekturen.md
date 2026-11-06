# Bestandsprüfungskorrekturen

`tblXzn31tsDItmQUO` · Kategorie **Antrag** (Kind von [[bestandspruefungen]]; Make und Hand schreiben, keine Geldwerte)

> Feld-Block: **Stand 2026-11-06**, beim Anlegen per Airtable-MCP gelesen. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **offene Kratom-Zählzeile** einer Bestandsprüfung, die noch nicht gebucht ist. Der Prüflauf legt sie an, Joscha ergänzt die Zahlen oder verwirft sie, `[Process] Correction (Inventory)` bucht sie als Position. Ersetzt seit 06.11.2026 das Textfeld `Bestandsprüfungen.Nachtrag`.

## Beziehungen

- **→ `Bestandsprüfung`** (ein Link) — Elternzeile → [[bestandspruefungen]]; dort Rückfeld `Bestandsprüfungskorrekturen`, Anzahl `Offene Korrekturen`, Formel `Unklar`.
- **→ `Produkt`** (→ [[produktvarianten]]) — nur zum Lesen; leer, wenn der Store die Sorte nicht führt.
- **→ `Buchung`** (→ [[bestandspruefungspositionen]]) — die gebuchte Position (Nachweis, Doppelschutz).

## Tragende Felder

- **`ID`** (Formel, Primär) — `{Bestandsprüfung} & " #" & {Position}`. Make schreibt sie nie.
- **`Position`** · **`Artikelnummer`** · **`SOLL`** · **`IST`** — Make belegt vor, die Hand ergänzt oder ändert. IST nur bei sicher gelesener Zahl; beim SOLL-Abgleich steht der kleinere SOLL. Make löst über die Artikelnummer auf, nicht über den Produkt-Link.
- **`Gelesen`** (Text) — was der Leser sah („13“, „29 (unsicher)“, „nicht gezählt“). **`Grund`** (Langtext) — warum offen bzw. warum abgelehnt.
- **`Status`** (Select) — Offen · Gebucht · Abgelehnt · Verworfen. Make setzt Offen, Gebucht und Abgelehnt; **Verworfen setzt nur die Hand** (definierte Ausnahme zu „Make-Felder unantastbar“).

## Ablauf

1. Prüflauf (`[Process] Upload PDF (Inventory)`, grid-Zweig): jede offene Kratom-Zeile → Status Offen. Nur bei sauberem Verdikt, nie bei Beleg-Problem.
2. Joscha ergänzt `IST` (oder `SOLL`), setzt `Verworfen` oder lässt die Zeile stehen, und setzt an der Prüfung `Korrekturen buchen`.
3. `[Process] Correction (Inventory)`: gebucht → Gebucht + `Buchung`; sonst Abgelehnt mit Grund; IST leer → unverändert. Keine Zeile mehr Offen/Abgelehnt → Prüfung Abgeschlossen. Regeln im Vertrag → [[scenarios]].

## Fallstricke

- **Doppelte Werte gewollt:** SOLL/IST stehen nach der Buchung in Korrektur und Position. Die Korrektur ist der Antrag, die Position die Buchung; verbunden über `Buchung`.
- Eine Korrektur für eine Sorte, die in der Prüfung schon eine Position hat, wird „schon gebucht“ abgelehnt — die Position korrigiert man nicht über diese Tabelle.
- **Status-Optionen nicht umbenennen** (🟣 Options) — Make schreibt und liest die Namen.

## Feld-Block (Stand 2026-11-06)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula (Primär; bis zur Umwandlung in der UI Text) | `fldvwF9I9wpXLOLhL` |
| Bestandsprüfung | link → Bestandsprüfungen | `fldcbslFLOvcvXcvR` |
| Position | number | `fldefXAK65EupOXPK` |
| Artikelnummer | singleLineText | `fld3xzVelPCGUyPaZ` |
| Produkt | link → Produktvarianten | `fldHAfmjlCNvtpby8` |
| SOLL | number | `fldBzSAcIj9XJZjIE` |
| IST | number | `fldX5BxPgpGrHK0Bf` |
| Gelesen | singleLineText | `fldcZN7iN8uyXrmD1` |
| Grund | multilineText | `fld3K6x4LvM9mufmk` |
| Status | singleSelect | `fldTBI0hFpwJyIBQf` |
| Buchung | link → Bestandsprüfungspositionen | `fldpJPJnMutRY8Q6Y` |

*Neu ziehen: `list_tables_for_base` → Bestandsprüfungskorrekturen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-11-06)

Make schreibt **10** Felder und liest **5**. Eines davon matcht Make über den Optionsnamen — es trägt den 🟣-Marker in der Feldbeschreibung der Base.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Status`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldTBI0hFpwJyIBQf`  
  Schreibt Offen (6729541 „Create corrections“) sowie Gebucht und Abgelehnt (8413130); liest alle vier Namen im Code „Parse corrections“.  
  ⚠ Optionsnamen sind eingefroren — Umbenennen bricht den Match still.

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Artikelnummer` · `Bestandsprüfung` · `Gelesen` · `Grund` · `IST` · `Position` · `Produkt` · `SOLL` (6729541 „Create corrections“, REST POST) · `Buchung` (8413130 „Mark correction booked“) · `Grund` (8413130 „Write rejections“ / „Write unresolved“, REST PATCH)  
**Make liest:** `Artikelnummer` · `IST` · `Position` · `SOLL` (8413130 „Load corrections“, cellFormat json)

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**
