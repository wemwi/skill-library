# Invoice — Provisionsabrechnung POS-Partner

Lexware-Rechnung eines Kiosk-Partners in die Provisionsliste (Google Sheet) des zuständigen Vertrieblers eintragen; bei Zahlungseingang dieselbe Zeile aktualisieren. Diese reference ist **selbsttragend** (kein Sprung in `telegram.md`, das nur für die Launch-Domäne Pflicht ist). Der Agent **rechnet keine Beträge** — Netto kommt fertig aus Lexware, Provision/Kosten sind Sheet-Formeln, die der Agent nie überschreibt.

## 1. Trigger & Reihenfolge

Die Kette hat **zwei Eintritts-Modi**, unterschieden am injizierten Input der User-Message. **Der `eventType` verzweigt nicht** — er ist nur Kontext; ob Insert oder paid-Update dran ist, entscheidet immer erst der Idempotenz-Read (§5). Was verzweigt, ist **wie du an den/die Voucher kommst**:

### 1a. Event-Primärpfad — `resourceId` injiziert (Regelfall)

Die `agent-bridge` startet die Session aus einem Lexware-`voucher.*`-Webhook und injiziert **`resourceId` + `eventType` + `eventDate`** in die User-Message (Trigger empirisch bewiesen: `voucher.created` = neuer Beleg, `voucher.status.changed` = u. a. Zahlungseingang).

- **Genau ein Voucher, direkt geholt: `get_voucher(resourceId)`. KEIN Poll, kein `list_vouchers`.** Die `resourceId` ist die Voucher-UUID → direkt in `get_voucher`/`extract_voucher_positions` (§3). **Kein `get_invoice`/`invoice.*`** — Voucher- und Invoice-IDs sind disjunkte ID-Räume (live gegengeprüft); die Webhook-`resourceId` ist immer eine Voucher-ID.
- Danach normal weiter ab §2 (Findung) → §5 (Idempotenz-Read) → §6 Insert **oder** §7 paid-Update.

### 1b. Backstop-Poll — kein `resourceId` (Sicherheitsnetz)

Läuft der Agent **ohne** injizierte `resourceId` (monatlicher Scheduled Deployment / Cron), ist es der **Backstop-Poll**: er fängt Belege, deren Event verloren ging (Zustellfehler, Endpoint-Downtime). Er ist **nicht** der Primärpfad — der Event-Pfad ist es.

- **Gefenstert**, nicht voll: `list_vouchers` (`voucherType: salesinvoice`) mit `updatedDateFrom` = **heute − 35 Tage**. Diese Untergrenze **berechnet der Agent im Backstop-Modus selbst** per bash (`date -d '35 days ago'`) — der Scheduled-Deployment-Trigger injiziert bewusst **keinen** Wert (die „Erste Nachricht" des Deployments trägt kein `resourceId`; genau dieses Fehlen ist die Backstop-Erkennung, §1a/§1b). 35 Tage = Monatskadenz + ~5 Tage Slack; das Fenster **bounded nur den Scan**, es trägt nicht die Korrektheit — die trägt die §5-Idempotenz (jeder bereits eingetragene Beleg wird beim Read übersprungen, auch in der Fenster-Überlappung).
- Gepollt in **zwei** Calls, weil `overdue` in der Lexware-API **nicht** mit anderen Status kombinierbar ist:
  - `voucherStatus: open,paid,paidoff`
  - `voucherStatus: overdue`
- Pro Voucher aus beiden Ergebnissen normal weiter ab §2 → §5 → §6/§7.
- **Lauf-Abschluss — unbedingte Zusammenfassung (Lebenssignal):** Nach beiden Ergebnislisten postet der Backstop **immer genau eine** Zusammenfassung ins General-Topic (§9) — auch bei 0 geprüften / 0 nachgetragenen Belegen. Diese Meldung ist das grobe Lebenssignal; ihr **Ausbleiben** (statt eines „0/0“-Posts) ist das Ausfallsignal. Der Event-Pfad (§1a) postet **keine** solche Sammelmeldung — nur der Backstop.

**Beide Modi teilen ab §2 denselben Code** (Findung, Extraktion, Idempotenz-Read, Insert/paid-Update) — die Verzweigung betrifft ausschließlich die Voucher-Beschaffung in diesem Abschnitt. Der Idempotenz-Read (§5) ist in **beiden** Modi der Entscheider zwischen Insert (§2–§6) und paid-Update (§7).

---

## 2. Partner → Ordner → Datei (Registry-Map, kein Scan)

**Kein Verzeichnis-Scan, kein Raten.** Die Zuordnung Vertriebler → Drive-Ordner → Datei-Präfix steht ausschließlich in `registry.md` §4. Ablauf:

1. `partner` aus `extract_voucher_positions` (Anker „Vertrieb und Betreuung:“) → Lookup in `registry.md` §4. Kein Eintrag → **Abbruch + Rückfrage** (§9), niemals raten.
2. Rechnungsjahr aus `voucherDate` des Vouchers (**nicht** aus dem Verarbeitungsdatum — sonst kippt eine Silvester-Verarbeitung ins Folgejahr).
3. `list_files(folderId = Ordner-ID aus §4)` → exakter Name-Match `"{Datei-Präfix} {Rechnungsjahr}"` (z. B. `Provision Schlegel 2026`).
4. **Genau 1 Treffer** → dessen `id` ist die Spreadsheet-ID für alle folgenden Schritte. **≠ 1 Treffer** (0 oder mehrere) → Abbruch + Rückfrage (§9), **kein** Fallback auf „neueste Datei“ oder Teilstring-Match. Ein Ordner enthält typischerweise mehrere Jahres-Dateien (z. B. `Provision Schlegel 2025` **und** `2026`) — ein reiner `contains`-Match auf den Präfix ist deshalb mehrdeutig und **nicht zulässig**.

Neue Jahres-Datei anlegen ist **kein** Teil dieser Kette (Non-Goal, §8) — die Datei muss bereits existieren (Rollover ist Copy-based, manuell/separater Prozess).

---

## 3. Rechnungsdaten lesen

- `get_voucher(id)` → Netto = `totalGrossAmount − totalTaxAmount`. Der Agent **berechnet nichts selbst**, nur diese eine Subtraktion aus den zwei Voucher-Feldern.
- `extract_voucher_positions(id)` → `partner` (§2), Kunden-Nr (falls im PDF vorhanden — Fallback ist der Stores-Match in §4, nicht diese Zahl), Menge (kg) und Einheiten (Positionszahl). Das Tool liefert außerdem einen Checksum-Abgleich Positionssumme vs. `totalGrossAmount` — **bei Checksum-Mismatch: Abbruch + Rückfrage (§9)**, nicht stillschweigend weiterrechnen.
- `voucherDate` (Serial-kompatibel, §6) und `voucherNumber` (Idempotenz-Key, §5) kommen direkt aus `get_voucher`.

---

## 4. Match gegen Stores — einziger Guard

**Kunden-Nr in `Stores!B5:B` (native Table „Partner“, Spalte „Kunden-Nr“) vorhanden → schreiben. Nicht vorhanden → skip.** Das ist der **einzige** Guard — der `Status`-Wert der Store-Zeile (`Aktiv`/`Inaktiv`) ist **kein** Kriterium: Lexware ist die Ground Truth für „es gibt ein Geschäft“, ein veralteter Sheet-Status widerspricht dem nicht. Ein Skip deckt sowohl echten Privatverkauf als auch einen in `Stores` noch nicht angelegten Partner ab (Partner-Anlage ist `launch`-Domäne, kein Teil dieser Kette).

Kunden-Nr **numerisch** vergleichen (Lexware/PDF liefert ggf. String) — die Zielspalte E ist numerisch (§6), ein String-Wert würde später `SUMIFS` in `Stores` silently auf 0 laufen lassen, ohne dass der Fehler in `Umsatz` selbst sichtbar wird.

---

## 5. Idempotenz — Rechnung-Nr, unmittelbar vor dem Schreiben gelesen

**Schlüssel = volle `voucherNumber`** (inkl. Suffix, z. B. `RG-10102-1`) — Storno-/Korrektur-Belege mit abweichendem Suffix (z. B. `-2`) werden **bewusst nicht** sonderbehandelt und laufen als eigener Key/eigene Zeile durch (Non-Goal, §8).

1. Spreadsheet-ID + Tab `Umsatz` aus §2.
2. `get_range("Umsatz!B:B")` **direkt vor** dem Schreiben (nicht am Run-Start gecacht — zwei Voucher desselben Laufs dürfen sich nicht auf einem veralteten Snapshot gegenseitig überschreiben).
3. `voucherNumber` bereits in Spalte B → **kein Insert**, stattdessen §7 (paid-Update) prüfen, ob sich nur der Status geändert hat. `voucherNumber` nicht vorhanden → Insert-Pfad (§6).

---

## 6. Schreiben — Insert-Mechanik

### 6.1 Spalten header-basiert auflösen — nie Buchstaben hardcoden

`list_tables(spreadsheetId, sheetId=<Umsatz-gid>)` liefert `columnProperties` (Name → tabellenrelativer Index) **und** die aktuelle Table-`range` (insbesondere `endRowIndex`) in einem Call — kein Zusatzaufwand gegenüber einem Fixwert, aber drift-immun, falls Joscha manuell eine Spalte verschiebt. Namen → Ziel:

| Spaltenname (Header) | Agent schreibt | Format |
|---|---|---|
| Rechnung-Nr | `voucherNumber` | Text |
| Datum | `voucherDate` | Serial (Datum, nicht String) |
| Status | `"Offen"` (Insert ist immer eine neue, offene Rechnung) | Text, Dropdown-Wert |
| Kunden-Nr | Kunden-Nr aus §4 | **Zahl**, nicht String |
| Store | — | **nie schreiben** (Formel `XLOOKUP`) |
| Menge | Menge (kg) aus §3 | Zahl |
| Einheiten | Einheiten aus §3 | Zahl |
| Kosten | — | **nie schreiben** (Formel) |
| Nettoumsatz | Netto aus §3 | Zahl |
| Provision | — | **nie schreiben** (Formel) |

**Nie schreiben:** die mit Formel markierten Spalten (Store/Kosten/Provision) — sie werden ausschließlich durch `inheritFromBefore` vererbt (§6.2). Ein direkter Schreibversuch würde die Formel durch einen Literalwert ersetzen und die Zeile von künftigen Änderungen an `Kosten_Ware_KG`/`Kosten_Einheit_Gesamt`/`Allgemein!C8` abkoppeln.

**Dezimaltrenner:** Das Sheet ist DE-Locale (Formeln nutzen `;` als Argumenttrenner). `batch_update_ranges` schreibt `USER_ENTERED` — Dezimalzahlen (Menge, Nettoumsatz) deshalb mit **Komma** übergeben (z. B. `369,57`, nicht `369.57`), sonst riskiert der Punkt eine Fehlinterpretation als Tausendertrenner.

### 6.2 Position — vor der Footer-Zeile einfügen, nicht anhängen

**`append_row`/`values.append` ist hier falsch** — es schreibt unterhalb des belegten Bereichs, also **unter** die Footer-/Summenzeile und **außerhalb** der nativen Table. Die neue Zeile würde dann in keinem `SUM(Umsatz[...])` mehr auftauchen; Provisions- und Auszahlungssummen wären zu niedrig, ohne sichtbaren Fehler.

1. `endRowIndex` aus dem `list_tables`-Read (§6.1) ist GridRange-**exklusiv** — er zeigt eine Zeile **hinter** die Footer-Zeile, nicht auf sie. Der 0-based Einfügeindex ist deshalb **`endRowIndex - 1`**. Wörtlich `endRowIndex` als Einfügeindex genommen landet die neue Zeile **unter** dem Footer, außerhalb der Table — Summenformeln bleiben zu niedrig, ohne sichtbaren Fehler. **Pro Run neu lesen**, nie eine Zeilennummer hardcoden (die Table wächst mit jedem Insert).
2. `insert_dimension` mit `range = {startIndex: endRowIndex - 1, endIndex: endRowIndex}` und `inheritFromBefore: true` (verschiebt die bestehende Footer-Zeile automatisch eine Zeile nach unten und übernimmt deren Formel-Vorlage für die neue Zeile — das erledigt §6.1's „Store/Kosten/Provision nie schreiben“ automatisch mit).
3. `batch_update_ranges` (USER_ENTERED) für **nur** B/C/D/E/G/H/J der neuen Zeile, laut Tabelle in §6.1. L/M bleiben leer (keine Werte in dieser Domäne).
4. **Verifikation (Pflicht vor DoD-Abnahme, danach optional):** `get_range` auf F/I/K der neuen Zeile mit `valueRenderOption: FORMULA` lesen und gegen das Muster der Nachbarzeile prüfen — bestätigt, dass `inheritFromBefore` wirklich vererbt hat und die Table sich erweitert hat (`list_tables` erneut, `endRowIndex` um 1 gewachsen).

---

## 7. paid-Update-Pfad

Voucher, dessen `voucherStatus` (§5.3 Treffer) sich Richtung bezahlt bewegt hat:

- **Mapping** (verifiziert per `get_voucher` an je einem realen `open`- und `paid`-Beleg): `paid`/`paidoff` → Sheet-Status `"Bezahlt"`. `open`/`overdue` → Sheet-Status `"Offen"` (beides derselbe Bucket — `overdue` ist nur „offen, Fälligkeit überschritten“, kein Extra-Fall).
- Zeile über den Idempotenz-Read (§5, Spalte B = `voucherNumber`) finden.
- **Nur** Spalte „Status“ (D) dieser Zeile schreiben. Kein Insert, keine anderen Spalten anfassen.
- Rückwärtsgang (`paid` → `open`) wird identisch behandelt — derselbe Schreibpfad, nur der Zielwert unterscheidet sich.

---

## 8. Non-Goals (bewusst außerhalb dieser Kette)

- Keine Betragsberechnung außer der einen Subtraktion in §3 — Provision/Kosten sind und bleiben Sheet-Formeln.
- Keine Anlage neuer Jahres-Dateien (Rollover ist Copy-based, separater/manueller Prozess).
- Keine Sonderbehandlung von Storno-/Korrektur-Belegen (§5) — läuft naiv als eigene Zeile.
- Keine Entscheidung über `Stores`-Status (Aktiv/Inaktiv) — reiner Anzeigewert, kein Guard (§4).
- Kein Anlegen neuer Partner in `Stores` (das ist `launch`-Domäne).

---

## 9. Status-Rückmeldung ins Topic

**Offen — Platzhalter bis Bestätigung:** `registry.md` §3 hat noch **keinen** dedizierten Topic für die Invoice-Domäne (nur General, Übergabeprotokolle=`2`, Bestandsprotokolle=`34`). Diese reference postet bis auf Weiteres ins **General**-Topic — sobald ein eigener Topic in Telegram angelegt ist, ist die Änderung eine einzeilige `registry.md`-Ergänzung plus Anpassung dieser Zeile, kein Skill-Umbau.

**General adressieren:** In Telegram-Foren ist General **keine** reguläre `message_thread_id` — `message_thread_id: 1` wird von der Bot-API mit „message thread not found“ abgelehnt. General wird ausschließlich durch **Weglassen** des Parameters `message_thread_id` erreicht (verifiziert per realem Test-Post).

| Ausgang | Status (Beispiel) |
|---|---|
| Insert erfolgreich | „✅ RG-10102-1 — Alero Kiosk: Nettoumsatz 369,77 € in Provision Schlegel 2026 eingetragen (Offen).“ |
| paid-Update | „✅ RG-10076-1: Status → Bezahlt (Provision Schlegel 2026).“ |
| Kein Stores-Match (§4) | kein Post — stiller Skip (Privatverkauf ist der Normalfall, keine Rückfrage nötig). |
| Partner nicht in Registry (§2) | „⚠️ Partner „<partner>“ aus RG-… nicht in registry.md §4 — Rückfrage nötig.“ |
| Datei-Findung ≠ 1 Treffer (§2) | „⚠️ RG-…: <0\|N> Treffer für „<Präfix> <Jahr>“ im Ordner — bitte prüfen.“ |
| Checksum-Mismatch (§3) | „⚠️ RG-…: Positionssumme ≠ Rechnungsbetrag laut Extraktion — bitte manuell prüfen.“ |
| Backstop-Lauf abgeschlossen (§1b) | „♻️ Backstop-Lauf: {X} geprüft, {Y} nachgetragen, {Z} Status-Updates.“ — **immer** posten, auch bei 0/0/0. |

```
post_message(
  chat_id           = <Operations-Chat chat_id aus registry.md §3>,   # -1003918922935
  # message_thread_id weglassen -> General, bis Invoice-Topic existiert
  text              = "<Status-Zeile>",
  parse_mode        = "HTML"
)
```

**Kein City-Channel-Post in dieser Kette** — Provisionsdaten sind intern, `pos-invoice` erhält kein Posting-Recht auf City-Channels (Least-Privilege, `global-agent-framework`).
