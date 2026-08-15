# blueprints/

Datierte JSON-Dumps der Make-Szenarien — die **SSoT der Innereien** (Modulketten), die `references/scenarios.md` bewusst nicht dupliziert. Ein File je Szenario: `<name>.<id>.json`.

**Stand 2026-08-15: befüllt.** Alle 16 Szenarien liegen als unverpackte Blueprint-Objekte (`{name, flow, metadata}`, teils `io`) vor. Verify-live: Dumps altern — bei jeder Szenario-Änderung das betroffene File neu ziehen (Prozedur unten).

## Befüllung / Refresh (Skript-Dump, nicht von Hand)

Je Szenario `scenarios_get(<id>)` → das `blueprint`-Objekt als JSON ablegen. **Nicht durch einen Chat-Kontext ziehen** (Blueprints sind groß) — im Claude-Code-Handover per Skript dumpen.

## Szenarien (Team 2174024, Stand 2026-08-15)

| Datei | ID |
|---|---|
| `dispatch-upload-pdf.6836167.json` | 6836167 |
| `dispatch-lexware-voucher.6872775.json` | 6872775 |
| `process-upload-pdf-delivery.6677862.json` | 6677862 |
| `process-upload-pdf-inventory.6729541.json` | 6729541 |
| `process-invoice-store.6633991.json` | 6633991 |
| `process-invoice-sales.6872651.json` | 6872651 |
| `process-payment-reminder-store.6844567.json` | 6844567 |
| `notify-telegram.6862968.json` | 6862968 |
| `sync-inventory-to-shopify.6805674.json` | 6805674 |
| `sync-shopify-products-to-airtable.6795533.json` | 6795533 |
| `sync-shopify-stores-google-place.6655783.json` | 6655783 |
| `sync-jtl-invoice-to-lexware.6870495.json` | 6870495 |
| `sync-lexware-payments.6955541.json` | 6955541 |
| `create-new-store-partner.6820980.json` | 6820980 |
| `create-new-sales-member.6821121.json` | 6821121 |
| `maintain-airtable-webhooks.6830404.json` | 6830404 |

Verträge (Trigger/Rolle/Notify-Keys): [[scenarios]]. Datum im Dateikopf oder Commit vermerken (verify-live).
