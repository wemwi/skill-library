# examples/

Echte Belege als Anschauungsmaterial — je ein PDF pro Belegtyp, damit ein Agent sieht, was der Klassifikator (`[Dispatch] Upload PDF`) und die `[Process]`-Szenarien tatsächlich lesen. Repo ist privat; **keine Neutralisierung nötig.**

## Ablage

Ein PDF je Belegtyp, benannt nach dem Belegtyp:

| Datei | Belegtyp | Ziel-Szenario |
|---|---|---|
| `uebergabeprotokoll.pdf` | Übergabeprotokoll | `[Process] Upload PDF (Delivery)` |
| `rueckholprotokoll.pdf` | Rückholprotokoll | `[Process] Upload PDF (Delivery)` |
| `bestandsprotokoll.pdf` | Bestandsprotokoll (alter JTL-Druck) | `[Process] Upload PDF (Inventory)` |
| `bestandsprotokoll-frei.pdf` | Bestandsprotokoll (freies Formular, BLG-00182) | `[Process] Upload PDF (Inventory)` |
| `ausgangsrechnung.pdf` | Ausgangsrechnung | `[Process] Invoice (Store)` |
| `eingangsrechnung.pdf` | Eingangsrechnung | `[Process] Invoice (Sales)` |
| `zahlungserinnerung.pdf` | Zahlungserinnerung | `[Process] Payment Reminder (Store)` |
| `mahnung.pdf` | Mahnung | `[Process] Payment Reminder (Store)` |

`rueckholprotokoll.pdf` ist BLG-00188.

## Was auf dem Papier steht

| Belegtyp | Herkunft | Kundennummer | Store-Name auf dem Papier | Original |
|---|---|---|---|---|
| Übergabeprotokoll | JTL-Druck | gedruckt („Kunden-Nr.“ im Kopf) | JTL-Kundenname im Adressfeld, kann vom Namen in Airtable abweichen | bleibt im Kiosk |
| Rückholprotokoll | JTL-Druck | gedruckt („Kunden-Nr.“ im Kopf) | JTL-Kundenname im Adressfeld, kann vom Namen in Airtable abweichen | bleibt im Kiosk |
| Bestandsprotokoll, alter Druck | JTL-Druck | gedruckt („Kunden-Nr.“ im Kopf) | JTL-Kundenname | bleibt im Kiosk |
| Bestandsprotokoll, freies Formular | gedrucktes Formular, von Hand ausgefüllt | von Hand im Kopfkasten „Kundennummer“; bisher steht dort meist ein Name („AR 1“, „SPÄTKAUF“) | keiner | bleibt im Kiosk |
| Lieferschein | JTL, kommt per Mail | gedruckt | JTL-Kundenname | PDF aus der Mail |

Der Store kommt aus der App, der Name vom Papier spielt keine Rolle. Die Kundennummer auf dem Beleg bestätigt nur die Wahl. Ein neuer Scan ist nicht möglich, das Original bleibt im Kiosk.

Belegtyp → Zieltabelle steht in [[belege]]. Die Klassifikation selbst macht `[Dispatch] Upload PDF` (6836167).
