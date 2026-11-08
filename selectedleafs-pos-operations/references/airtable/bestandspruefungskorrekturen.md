# Bestandsprüfungskorrekturen

`tblXzn31tsDItmQUO` · Kategorie **Antrag** (Kind von [[bestandspruefungen]]; Make und Hand schreiben, keine Geldwerte)

> Feld-Block: **Stand 2026-11-07**, per Airtable-MCP gelesen (Gelesen, Produkt, Buchung am 07.11. entfernt). Verify-live — im Zweifel gewinnt die Base.

## Zweck

Eine Zeile = eine **offene Kratom-Zählzeile** einer Bestandsprüfung, die noch nicht gebucht ist. Der Prüflauf legt sie an, Joscha ergänzt die Zahlen oder verwirft sie, `[Process] Correction (Inventory)` bucht sie als Position. Ersetzt seit 06.11.2026 das Textfeld `Bestandsprüfungen.Nachtrag`.

## Beziehungen

- **→ `Bestandsprüfung`** (ein Link) — Elternzeile → [[bestandspruefungen]]; dort Rückfeld `Bestandsprüfungskorrekturen`, Anzahl `Offene Korrekturen`, Formel `Unklar`.

## Tragende Felder

- **`ID`** (Formel, Primär) — `{Bestandsprüfung} & " #" & {Position}`. Make schreibt sie nie.
- **`Position`** · **`Artikelnummer`** · **`SOLL`** · **`IST`** — Make belegt vor, die Hand ergänzt oder ändert. IST nur bei sicher gelesener Zahl **bis höchstens SOLL**; Mehrbestand bleibt ohne IST, bis die Hand die Zählung bestätigt. Beim SOLL-Abgleich steht der kleinere SOLL. Make löst über die Artikelnummer auf.
- **`Grund`** (Langtext) — warum offen bzw. warum abgelehnt; bei unsicherer Lesung mit „gelesen 29 (unsicher)“, bei Mehrbestand mit der Zählung.
- **`Status`** (Select) — Offen · Gebucht · Abgelehnt · Verworfen. Make setzt Offen, Gebucht und Abgelehnt; **Verworfen setzt nur die Hand** (definierte Ausnahme zu „Make-Felder unantastbar“).

## Ablauf

1. Prüflauf (`[Process] Upload PDF (Inventory)`, grid-Zweig): jede offene Kratom-Zeile → Status Offen. Nur bei sauberem Verdikt, nie bei Beleg-Problem.
2. Joscha ergänzt `IST` (oder `SOLL`), setzt `Verworfen` oder lässt die Zeile stehen, und setzt an der Prüfung `Korrekturen buchen`.
3. `[Process] Correction (Inventory)`: gebucht → Gebucht; sonst Abgelehnt mit Grund; IST leer → unverändert. **Mehrbestand** (IST > SOLL) wird gebucht, wenn der Store die Sorte im Bestand hat und der Überschuss ≤ `Bestände.Verkauft`; Differenz negativ, der Hinweis an der Prüfung nennt die Gutschrift: „Gutschrift in JTL über: <Sorte> <N> Stück, …“. Keine Zeile mehr Offen/Abgelehnt → Prüfung Abgeschlossen. Regeln im Vertrag → [[scenarios]].

## Fallstricke

- **Doppelte Werte gewollt:** SOLL/IST stehen nach der Buchung in Korrektur und Position. Die Korrektur ist der Antrag, die Position die Buchung (gleiche Prüfung und Sorte). Doppelschutz: Status Gebucht wird nie neu gebucht, je Prüfung und Sorte höchstens eine Position.
- **Mehrbestand nie über SOLL „passend machen“:** SOLL ist die Buchhaltung (geliefert − berechnet). Mehr gezählt heißt zu viel berechnet (→ Gutschrift) oder Lieferung fehlt (→ Lieferung buchen, dann SOLL der Korrektur anpassen). Die freie Gutschrift legt die Hand in JTL an, eine je Prüfung (→ [[bestaende]]); „Abrechnung offen“ zeigt sie seit 07.11.2026 als negative `Bestände.Differenz` (→ [[bestaende]]).
- Eine Korrektur für eine Sorte, die in der Prüfung schon eine Position hat, wird „schon gebucht“ abgelehnt — die Position korrigiert man nicht über diese Tabelle.
- **Status-Optionen nicht umbenennen** (🟣 Options) — Make schreibt und liest die Namen.

## Feld-Block (Stand 2026-11-07)

| Feld | Typ | fld-ID |
|---|---|---|
| ID | formula (Primär; bis zur Umwandlung in der UI Text) | `fldvwF9I9wpXLOLhL` |
| Bestandsprüfung | link → Bestandsprüfungen | `fldcbslFLOvcvXcvR` |
| Position | number | `fldefXAK65EupOXPK` |
| Artikelnummer | singleLineText | `fld3xzVelPCGUyPaZ` |
| SOLL | number | `fldBzSAcIj9XJZjIE` |
| IST | number | `fldX5BxPgpGrHK0Bf` |
| Grund | multilineText | `fld3K6x4LvM9mufmk` |
| Status | singleSelect | `fldTBI0hFpwJyIBQf` |

*Neu ziehen: `list_tables_for_base` → Bestandsprüfungskorrekturen; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Stand 2026-11-07)

Make schreibt **7** Felder und liest **5**. Eines davon matcht Make über den Optionsnamen — es trägt den 🟣-Marker in der Feldbeschreibung der Base.

### Namens-gekoppelt — trägt den 🟣-Marker am Feld

- **`Status`** — 🟣 `make.com (KEY · Options)` · singleSelect · `fldTBI0hFpwJyIBQf`  
  Schreibt Offen (6729541 „Create corrections“) sowie Gebucht und Abgelehnt (8413130); liest alle vier Namen im Code „Parse corrections“.  
  ⚠ Optionsnamen sind eingefroren — Umbenennen bricht den Match still.

### fld-ID-fest — ohne Marker, umbenennungssicher

**Make schreibt:** `Artikelnummer` · `Bestandsprüfung` · `Grund` · `IST` · `Position` · `SOLL` (6729541 „Create corrections“, REST POST) · `Grund` (8413130 „Write rejections“ / „Write unresolved“, REST PATCH)  
**Make liest:** `Artikelnummer` · `IST` · `Position` · `SOLL` (8413130 „Load corrections“, cellFormat json)

Diese Felder tragen bewusst **keinen** Feld-Marker: Make adressiert sie über die Feld-ID, Umbenennen ist folgenlos. **Löschen oder Umtypisieren bricht Make dagegen sehr wohl.**
