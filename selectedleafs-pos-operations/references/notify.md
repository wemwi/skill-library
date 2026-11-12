# Benachrichtigungen (Telegram)

> Quelle: `[Notify] Telegram Channels` (Szenario **6862968**), live gelesen **Stand 2026-08-14**; Eingänge, Router und Fehlerwege **Stand 2026-11-12**. Die **Meldetexte** stehen ausschließlich im `assets/catalog.md` (Text-SSoT) — hier steht die **Mechanik**, nicht die Wortlaute.

## Zweck & Form

**Ein zentraler Hub**, alle Szenarien „klingeln" per **`StartSubscenario`** (on-demand child). Fünf Eingaben, nur `key` ist Pflicht:

- **`key`** — der Meldeschlüssel (z. B. `delivery.booked`). Pflicht.
- **`id`** — Record-ID des Fachdatensatzes (optional; leer ⇒ Meldung nur aus `ctx` und `tokens`).
- **`ctx`** — JSON-Text mit Zusatzwerten, die nicht in der Base stehen (optional).
- **`tokens`** — dieselben Zusatzwerte als Liste aus `name` und `value`, ohne JSON (optional, seit 12.11.2026).
- **`task_key`** — Schlüssel der Aufgabe, die zum Ereignis in `key` gehört: Ereignis und Aufgabe in einem Lauf (optional, seit 12.11.2026).

Der Hub liest selbst nach und rendert — der Aufrufer liefert nur Schlüssel, ID und Zusatzwerte. **Unbekannter `key`** wird nie verworfen, sondern roh in das Thema **🛑 Störungen** (584) gepostet: Ein falscher Schlüssel ist eine Störung (seit 12.11.2026; das frühere eigene Thema mit der Nummer 1 lehnte Telegram ab, „message thread not found“). Aufrufe mit nur `key`, `id`, `ctx` laufen unverändert. *Stand 12.11.2026: `tokens` senden die Störungsmeldungen von acht Szenarien, `task_key` fünf Worker (Listen in den nächsten beiden Abschnitten).*

### `tokens` — Platzhalter ohne JSON

- Die Liste liegt **über** dem gelesenen `ctx`: Bei gleichem Namen gewinnt `tokens`. Ohne `tokens` bleibt `ctx`, wie er gelesen wurde.
- Gedacht für Störungsmeldungen: Ein Fehlertext mit Anführungszeichen oder Zeilenumbruch braucht keinen Code-Schritt mehr, der JSON baut. Der Aufrufer trägt Name und Wert im Aufruf-Modul ein.
- Werte kommen als **Text** an. Leer heißt nicht gesetzt (`{leer …}` / `{gesetzt …}`); ein Wahrheitswert gehört weiter in `ctx`.
- Ein Eintrag ohne Namen zählt nicht, der Lauf bricht daran nicht ab (`name` ist deshalb kein Pflichtfeld).
- Ein kaputter `ctx` bricht „Map event“ weiter ab (`JSON.parse` ohne Fang). Wer nur `tokens` schickt, ist davon frei.
- **Wer `tokens` sendet (seit 12.11.2026, 32 Aufrufe):** `[Maintain] Store New Flag` (2), `[Sync] Google Places to Shopify` (2; die dritte Störung hinter dem Filter „Write rejected“ liest weiter `ctx` aus „Build report“), `[Sync] JTL to Airtable` (1), `[Create] Salesperson` (2: `error.lexware_orphan` mit `id`, `error.salesperson_failed`), `[Create] Store` (10: `error.store_partial`, `error.store_failed`), `[Sync] Airtable to Shopify` (8), `[Dispatch] Upload PDF` (6), `[Dispatch] Lexware Voucher` (1). Der Code-Schritt „Build error context“ vor diesen Aufrufen ist entfallen, die Meldetexte sind gleich geblieben. Noch mit Code-Schritt und `ctx`: `[Sync] Shopify to Airtable` (7) und `[Dispatch] Manual Action` (1, derselbe Code baut dort auch die Zeile für `Bestandsprüfungen.Hinweis`).
- **Werte am Aufruf-Modul:** fester Text, ein Ausdruck oder beides gemischt. Ersatzwert für einen leeren Fehlertext: `{{ifempty(<Modul>.error.message; "unbekannt")}}`. Text nur, wenn ein Wert da ist: `{{if(<Wert>; "<Text>"; "")}}` (so entsteht der Record-Link in `[Create] Store`). Beides am 12.11.2026 mit einer Prüfkopie gegen den Hub geprüft: leerer Wert, fehlender Wert, Anführungszeichen, Zeilenumbruch, Backslash.
- **Form am Aufruf-Modul (Blueprint):** `mapper.data.tokens` ist eine Liste aus `{ "name": …, "value": … }`; in `metadata.expect` steht der Eingang als `type: array` mit `spec: [name, value]`. Der Editor nimmt die Form beim Import an und zeigt die Einträge als „Item 1 …“ (geprüft 12.11.2026).
- Im Interface steht der Eingang als `type: array` mit `spec: [name, value]`. Diese Listenform führt Make selbst (wie `lines` an `[Resolve] Positions`); `validate_scenario_interface` der Make-Anbindung lehnt sie trotzdem ab. Das Interface deshalb nach einem Import am zurückgelesenen Stand prüfen (`scenarios_interface`), nicht an dieser Prüfung.

### `task_key` — Ereignis und Aufgabe in einem Lauf

- Der Hub liest den Datensatz **einmal** (über die Zeile des Ereignisses) und sendet die Aufgabe als **zweite Meldung**: nur Operations, im Thema der Aufgabe, Vorlage = `text` der Aufgabe, gerendert mit den Feldern und Lesungen des Ereignisses.
- Gültig ist ein `task_key`, wenn er in der Landkarte steht, mit `task.` beginnt, `key` bekannt ist und beide zur **selben Tabelle** gehören. Sonst geht der Rohtext „⁉️ Aufgabe nicht gesendet“ mit Grund, `key` und `id` in das Thema **🛑 Störungen**, auch wenn der Fachdatensatz fehlt. Das Ereignis selbst bleibt davon unberührt.
- Leer heißt: keine zweite Meldung. Der Aufrufer setzt `task_key` fest oder über seine Zusatzbedingung (z. B. nur beim Übergabeprotokoll).
- Eine gültige Aufgabe ohne Fachdatensatz wird wie das Ereignis nicht gesendet.
- **Neue Aufgabe für `task_key`:** Sie braucht dieselbe Feldzuordnung (`felder`, `vfelder`, `sfelder`) und dieselben Link-Felder wie ihr Ereignis; die `geld`-Liste des Ereignisses gilt auch für die Aufgabe. Für alle 45 Verbindungen aus Schlüssel und Aufgabe gleicher Tabelle ist am 12.11.2026 per Test belegt: Die zweite Meldung ist wortgleich mit der Aufgabe allein.
- **Wer `task_key` sendet (seit 12.11.2026, 7 Aufrufe):** `[Process] Lexware Voucher (Refund · Store)` (Aufruf „refund.settled“ mit `task.jtl_refund`, fest) · `[Process] Upload PDF (Delivery)` (Aufruf „delivery.*“ mit `task.jtl_stock`, nur beim Übergabeprotokoll, auch bei reiner Ausstattung) · `[Process] Upload PDF (Return)` (Aufruf „inventory.checked“ mit `task.jtl_inventory_date`, Aufruf „delivery.returned“ mit `task.jtl_return`, beide fest). · `[Process] Lexware Voucher (Invoice · Store)` (beide Aufrufe „invoice.*“ mit `task.jtl_payment`, nur bei echter Zahlung; der ctx trägt zusätzlich `Zahldatum`) · `[Process] Upload PDF (Inventory)` (Aufruf „inventory.checked“ mit `task.jtl_inventory_date`, fest). Der zweite Aufruf des Hubs samt „Skip notify error“ ist dort entfallen, die Meldetexte sind gleich geblieben. Damit sendet kein Worker mehr Ereignis und Aufgabe in zwei Aufrufen.
- **Zusatzbedingung als Ausdruck:** Trug die Aufgabe einen eigenen Filter, wird er zum Ausdruck am Eingang. In `(Delivery)` wurde aus dem Filter „Protocol only“ (`4.result.kind` ungleich „Lieferschein“) `{{if(4.result.kind = "Lieferschein"; ""; "task.jtl_stock")}}`; der leere Text kommt als leeres `task_key` an. Über alle Fälle (Lieferschein, Übergabeprotokoll, nur Ausstattung, Belegart leer) am 12.11.2026 per Test gegen den Filter belegt. Im Rechnungs-Worker wurde aus den Filtern „Real payment“ und „Payment changed“ `{{if(500.voucher_status = "voided"; ""; if(contains(map(100.body.paymentItems; "paymentItemType"); "irrecoverableReceivable"); ""; "task.jtl_payment"))}}`. Die Aufgabe trug dort einen eigenen ctx (`Zahldatum`); er steht jetzt im ctx des Ereignisses, dessen Text ihn nicht liest.
- **Form am Aufruf-Modul (Blueprint):** `mapper.data.task_key`. Trägt das Modul eine Eingabenform (`metadata.expect`), steht der Eingang dort als `{ "name": "task_key", "type": "text", "required": false }`; ohne Eingabenform liest der Editor sie aus dem Interface des Hubs. Beide Formen hat der Editor am 12.11.2026 beim Import angenommen.
- **Preis des einen Laufs:** Scheitert der Aufruf oder der Hub vor dem Senden, fehlen Ereignis und Aufgabe zusammen statt einzeln. Beide Sendeschritte parken und wiederholen.

## Drei Register / Channels

Welcher Text im Meldesatz **gesetzt** ist, entscheidet über den Empfänger:

| Register | Ziel | Chat | Bot-Connection | Thread |
|---|---|---|---|---|
| **`text`** | Operations | `-1003918922935` | 9134912 (Operations) | Topic aus `topic` |
| **`vtext`** | Vertriebler | `Vertriebler.Telegram Channel ID` | 9664308 (Sales) | — (kein Forum) |
| **`ctext`** | City (öffentlich) | `Stores.Telegram ID` (aus der Stadt) | 9307335 (Broadcast) | — |

**Operations-Topics:** 📥 Vorgänge **586** · 👉 Aufgaben **585** · 🛑 Störungen **584** · ⚙️ System **583**. Ein fünftes Thema gibt es nicht: Die beiden Rohtexte für einen Fehler im Aufruf (unbekannter `key`, nicht zuordenbares `task_key`) und der Rückfall für eine Zeile der Landkarte ohne Thema gehen in 🛑 Störungen (seit 12.11.2026).

**Router „Split by channel“ (5 Wege, `builtin:BasicRouter`):** „Send to Operations“ · „Send to salesperson“ · „Send photo to city channel“ (`SendPhoto`, wenn `foto` gesetzt) · „Send text to city channel“ · „Send second message“ (die Aufgabe zu `task_key`, Operations, Topic aus `topic2`). Geschaltet über explizite Flaggen (`ops`/`vtrb`/`city_foto`/`city_text`/`ops2`), nicht über Leerstring-Vergleiche.

## Die Ereignis-Landkarte (Modul 2 „Map event“)

Reine **Daten**, kein Code: eine Zeile je `key` mit `topic · tabelle · vertrieblerFeld · storeFeld · foto · saldo · felder/vfelder/sfelder · text/vtext/ctext`. Navigation:

- **`vertrieblerFeld`** = Link-Feld auf Vertriebler · `'*'` = der Fachdatensatz **ist** der Vertriebler.
- **`storeFeld`** = Link-Feld auf Stores · `'*'` = der Fachdatensatz **ist** der Store.
- **`saldo`** = `created` | `settled` — Vergleichsart für `{Saldoabruf}`.

## Der Renderer (Modul 6 „Build text“)

Ein generischer Renderer für alle drei Register. **Geldwerte werden nur formatiert, nie gerechnet.**

- **Token-Auflösung in Reihenfolge:** `felder` (Fachdatensatz) → `vfelder` (Vertriebler) → `sfelder` (Store) → `ctx`.
- **Spezial-Token:** `{abs X}` (Betrag ohne Vorzeichen — Rückholungen buchen negativ) · `{Vorname}` (erstes Wort aus Vertriebler) · `{Maps-URL}` (aus Store-Name + `Google Place ID`) · `{Saldoabruf}` (Vergleich Betrag ggü. Offen: `created` → Betrag ≥ Offen; `settled` → Betrag ≥ Offen + Betrag → »Voller Saldo« / »Teilbetrag«).
- **Zeilen-Modifier** (am Zeilenanfang): `{leer FELD}…` (Zeile nur wenn leer — Vorbehaltszeilen) · `{gesetzt FELD}…` (Zeile nur wenn gefüllt). Zeilen, deren Token alle leer bleiben, fallen weg; leere ` · `-Segmente lösen sich auf.
- **Formatierung:** Euro `1.234,56 €` · ISO-Datum → `TT.MM.JJJJ` · HTML-Escaping · **Betreffzeile (Zeile 1) generell fett** — kein Template trägt `<b>` in Zeile 1.

### Zwei-Lese-Mechanik (wichtiger Fallstrick)

Der Hub liest den Fachdatensatz **zweimal**:

- **JSON** (`returnFieldsByFieldId=true`) → Zahlen/Datum roh; **Link-Felder liefern Record-IDs** (`rec…`).
- **Klartext** (`cellFormat=string`, `timeZone=Europe/Berlin`) → Link-Felder als Klartext, aber Geld/Datum **formatiert** statt roh.

Deshalb: **Zahlen/Daten aus der JSON-Lesung, Links aus der Klartext-Lesung.** Und: **`Store` steht bewusst nicht im Fach-Feldsatz** — das Primärfeld von Stores ist die JTL-Nummer, ein Link-Feld druckt den Primärwert; `{Store}` würde „10009" zeigen. Der Token fällt auf `sfelder` durch, wo `Stores.Name` gelesen wird. Gleiches gilt für Lieferungen/Bestandsprüfungen.

## Fehlerbehandlung

- **Alle sechs Sendeschritte** (Operations, Vertriebler, Vertriebler-PDF, City-Foto, City-Text, zweite Meldung): `builtin:Break` „Retry + park“, **3 Versuche im Abstand von 15 Minuten**, danach liegt der Lauf als unvollständige Ausführung im Hub. Die City-Wege parken seit 11.11.2026 wie die anderen; vorher verwarf ein `builtin:Ignore` den gescheiterten Post still.
- Alle Nachlese-Module haben `builtin:Resume` bei Lesefehler („Continue without …“: die Meldung geht mit Lücken hinaus statt gar nicht).

## City-Betriebs-Anker (fail-closed)

Die City-Auflösung läuft `Store.Stadt → Städte.Telegram ID`. **Eine neue Stadt ist ein manueller Schritt:** der City-Channel muss existieren und in `Städte.Telegram ID` hinterlegt sein, **bevor** ein City-Post dorthin gehen kann. Fehlt die ID, unterbleibt der Post (kein Fehler). Der öffentliche Kanal hängt an genau zwei Anlässen: **`delivery.booked`** (→ `city.restock`/`city.strain_new`) und **`store.created`**.
*Das Marketing-Runbook (Channel-Titel, Pinned-Copy, Launch-Post, Legal) liegt in `selectedleafs-city-content`, nicht hier.*

## Key-Katalog (Index — Texte im `catalog.md`)

**📥 Vorgänge (586):** `store.created` · `store.model_changed` · `salesperson.created` · `salesperson.onboarded` · `delivery.booked` · `delivery.note_booked` · `delivery.returned` · `inventory.checked` · `inventory.corrected` · `inventory.due` · `invoice.created` · `invoice.paid` · `invoice.reminder_filed` · `invoice.dunning_filed` · `invoice.voided` · `invoice.written_off` · `payout.created` · `payout.settled` · `city.restock` · `city.strain_new`. *(Runde 26: `invoice.overdue` gestrichen. 05.11.2026: `store.model_changed` und `delivery.note_booked` neu. 06.11.2026: `inventory.corrected` neu.)*
**👉 Aufgaben (585):** `task.doctype_unclear` · `task.terms_missing` · `task.jtl_missing` · `task.jtl_stock` · `task.jtl_inventory_date` · `task.jtl_return` · `task.jtl_payment`. *(Runde 26: `task.digest` gestrichen, `task.telegram_missing` gestrichen. `task.jtl_payment` neu. 05.11.2026: `task.jtl_return` neu.)*
**⚙️ System (583):** `sync.products` · `sync.stores` · `sync.inventory`. *(Runde 26: `system.heartbeat` gestrichen, `sync.inventory` wieder aktiv. Zähler-Token ctx.)*
**🛑 Störungen (584):** `error.reminder_unmatched` · `error.lexware_orphan` · `error.sync_aborted` · `error.store_failed` · `error.store_partial` · `error.salesperson_failed` · `error.payment_unmatched` · `error.return_failed`. *(Runde 26: `error.reminder_unreadable` gestrichen, `error.payment_unmatched` neu. 05.11.2026: `error.return_failed` neu.)*

## Fallstricke

- **Texte nie hier pflegen** — der Hub ist die Mechanik, `catalog.md` die Text-SSoT. Bei Änderung: Modul 2 im Szenario **und** `catalog.md`.
- **`geld`-Liste je key** bestimmt, welche Token als Euro formatiert werden — fehlt ein Feld dort, kommt die rohe Zahl.
- **Store-Klartext-Lesung** (Modul 11) nicht auf JSON umstellen — sonst bricht `{Store}` auf die JTL-Nummer.
