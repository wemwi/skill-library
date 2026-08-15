# examples/

Echte Belege als Anschauungsmaterial — je ein PDF pro Belegtyp, damit ein Agent sieht, was der Klassifikator (`[Dispatch] Upload PDF`) und die `[Process]`-Szenarien tatsächlich lesen. Repo ist privat; **keine Neutralisierung nötig.**

## Ablage

Ein PDF je Belegtyp, benannt nach dem Belegtyp:

| Datei | Belegtyp | Ziel-Szenario |
|---|---|---|
| `uebergabeprotokoll.pdf` | Übergabeprotokoll | `[Process] Upload PDF (Delivery)` |
| `rueckholprotokoll.pdf` | Rückholprotokoll | `[Process] Upload PDF (Delivery)` |
| `bestandsprotokoll.pdf` | Bestandsprotokoll | `[Process] Upload PDF (Inventory)` |
| `ausgangsrechnung.pdf` | Ausgangsrechnung | `[Process] Invoice (Store)` |
| `eingangsrechnung.pdf` | Eingangsrechnung | `[Process] Invoice (Sales)` |
| `zahlungserinnerung.pdf` | Zahlungserinnerung | `[Process] Payment Reminder (Store)` |
| `mahnung.pdf` | Mahnung | `[Process] Payment Reminder (Store)` |

Belegtyp → Zieltabelle steht in [[belege]]. Die Klassifikation selbst macht `[Dispatch] Upload PDF` (6836167).
