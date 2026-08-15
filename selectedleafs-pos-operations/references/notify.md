# Benachrichtigungen (Telegram)

> Quelle: `[Notify] Telegram` (Szenario **6862968**), live gelesen **Stand 2026-08-14**. Die **Meldetexte** stehen ausschließlich im `assets/catalog.md` (Text-SSoT) — hier steht die **Mechanik**, nicht die Wortlaute.

## Zweck & Form

**Ein zentraler Hub**, alle Szenarien „klingeln" per **`StartSubscenario`** (on-demand child) mit drei Eingaben:

- **`key`** — der Meldeschlüssel (z. B. `delivery.booked`). Pflicht.
- **`id`** — Record-ID des Fachdatensatzes (optional; leer ⇒ reine ctx-Meldung).
- **`ctx`** — JSON mit Zusatzwerten, die nicht in der Base stehen (optional).

Der Hub liest selbst nach und rendert — der Aufrufer liefert nur Schlüssel + ID + ctx. **Unbekannter `key`** wird nie verworfen, sondern roh nach **⁉️ Unsortiert** (Topic 1) gepostet.

## Drei Register / Channels

Welcher Text im Meldesatz **gesetzt** ist, entscheidet über den Empfänger:

| Register | Ziel | Chat | Bot-Connection | Thread |
|---|---|---|---|---|
| **`text`** | Operations | `-1003918922935` | 9134912 (Operations) | Topic aus `topic` |
| **`vtext`** | Vertriebler | `Vertriebler.⚙ Telegram ID` | 9664308 (Sales) | — (kein Forum) |
| **`ctext`** | City (öffentlich) | `Stores.⚙ Telegram ID` (aus der Stadt) | 9307335 (Broadcast) | — |

**Operations-Topics:** 📥 Vorgänge **586** · 👉 Aufgaben **585** · 🛑 Störungen **584** · ⚙️ System **583** · ⁉️ Unsortiert **1**.

**Router (4 Wege, `builtin:BasicRouter`):** → Operations · → Vertriebler · → City·Foto (`SendPhoto`, wenn `foto` gesetzt) · → City·Text. Geschaltet über explizite Flaggen (`ops`/`vtrb`/`city_foto`/`city_text`), nicht über Leerstring-Vergleiche.

## Die Ereignis-Landkarte (Modul 2 „Ereignis-Landkarte")

Reine **Daten**, kein Code: eine Zeile je `key` mit `topic · tabelle · vertrieblerFeld · storeFeld · foto · saldo · felder/vfelder/sfelder · text/vtext/ctext`. Navigation:

- **`vertrieblerFeld`** = Link-Feld auf Vertriebler · `'*'` = der Fachdatensatz **ist** der Vertriebler.
- **`storeFeld`** = Link-Feld auf Stores · `'*'` = der Fachdatensatz **ist** der Store.
- **`saldo`** = `created` | `settled` — Vergleichsart für `{Saldoabruf}`.

## Der Renderer (Modul 6 „Text bauen")

Ein generischer Renderer für alle drei Register. **Geldwerte werden nur formatiert, nie gerechnet.**

- **Token-Auflösung in Reihenfolge:** `felder` (Fachdatensatz) → `vfelder` (Vertriebler) → `sfelder` (Store) → `ctx`.
- **Spezial-Token:** `{abs X}` (Betrag ohne Vorzeichen — Rückholungen buchen negativ) · `{Vorname}` (erstes Wort aus Vertriebler) · `{Maps-URL}` (aus Store-Name + `⚙ Google Place ID`) · `{Saldoabruf}` (Vergleich Betrag ggü. Offen: `created` → Betrag ≥ Offen; `settled` → Betrag ≥ Offen + Betrag → »Voller Saldo« / »Teilbetrag«).
- **Zeilen-Modifier** (am Zeilenanfang): `{leer FELD}…` (Zeile nur wenn leer — Vorbehaltszeilen) · `{gesetzt FELD}…` (Zeile nur wenn gefüllt). Zeilen, deren Token alle leer bleiben, fallen weg; leere ` · `-Segmente lösen sich auf.
- **Formatierung:** Euro `1.234,56 €` · ISO-Datum → `TT.MM.JJJJ` · HTML-Escaping · **Betreffzeile (Zeile 1) generell fett** — kein Template trägt `<b>` in Zeile 1.

### Zwei-Lese-Mechanik (wichtiger Fallstrick)

Der Hub liest den Fachdatensatz **zweimal**:

- **JSON** (`returnFieldsByFieldId=true`) → Zahlen/Datum roh; **Link-Felder liefern Record-IDs** (`rec…`).
- **Klartext** (`cellFormat=string`, `timeZone=Europe/Berlin`) → Link-Felder als Klartext, aber Geld/Datum **formatiert** statt roh.

Deshalb: **Zahlen/Daten aus der JSON-Lesung, Links aus der Klartext-Lesung.** Und: **`Store` steht bewusst nicht im Fach-Feldsatz** — das Primärfeld von Stores ist die JTL-Nummer, ein Link-Feld druckt den Primärwert; `{Store}` würde „10009" zeigen. Der Token fällt auf `sfelder` durch, wo `Stores.Name` gelesen wird. Gleiches gilt für Lieferungen/Bestandsprüfungen.

## Fehlerbehandlung

- **Operations / Vertriebler:** `builtin:Break` mit Retry **3× / 15 s** (Zustellung ist wichtig).
- **City (beide Wege):** `builtin:Ignore` — der öffentliche Broadcast **darf ausfallen**, ohne den Lauf zu stoppen.
- Alle Nachlese-Module haben `builtin:Resume` bei Lesefehler (übergehen statt abbrechen).

## City-Betriebs-Anker (fail-closed)

Die City-Auflösung läuft `Store.Stadt → Städte.⚙ Telegram ID`. **Eine neue Stadt ist ein manueller Schritt:** der City-Channel muss existieren und in `Städte.⚙ Telegram ID` hinterlegt sein, **bevor** ein City-Post dorthin gehen kann. Fehlt die ID, unterbleibt der Post (kein Fehler). Der öffentliche Kanal hängt an genau zwei Anlässen: **`delivery.booked`** (→ `city.restock`/`city.strain_new`) und **`store.created`**.
*Das Marketing-Runbook (Channel-Titel, Pinned-Copy, Launch-Post, Legal) liegt in `selectedleafs-city-content`, nicht hier.*

## Key-Katalog (Index — Texte im `catalog.md`)

**📥 Vorgänge (586):** `store.created` · `salesperson.created` · `salesperson.onboarded` · `delivery.booked` · `delivery.returned` · `inventory.checked` · `inventory.due` · `invoice.created` · `invoice.paid` · `invoice.overdue` · `invoice.reminder_filed` · `invoice.dunning_filed` · `invoice.voided` · `invoice.written_off` · `payout.created` · `payout.settled` · `city.restock` · `city.strain_new`.
**👉 Aufgaben (585):** `task.doctype_unclear` · `task.terms_missing` · `task.jtl_missing` · `task.telegram_missing` · `task.digest`. *(`task.invoice_unlinked` / `task.beleg_no_pdf` haben bewusst keine eigene Meldung — nur Zeile im Digest.)*
**⚙️ System (583):** `sync.products` · `sync.stores` · `system.heartbeat`. *(alle Token ctx; wiederholte Blöcke kommen fertig als `{Zeilen}`.)*
**🛑 Störungen (584):** `error.reminder_unreadable` · `error.reminder_unmatched` · `error.lexware_orphan` · `error.sync_aborted` · `error.store_failed` · `error.store_partial` · `error.salesperson_failed`.

## Fallstricke

- **Texte nie hier pflegen** — der Hub ist die Mechanik, `catalog.md` die Text-SSoT. Bei Änderung: Modul 2 im Szenario **und** `catalog.md`.
- **`geld`-Liste je key** bestimmt, welche Token als Euro formatiert werden — fehlt ein Feld dort, kommt die rohe Zahl.
- **Store-Klartext-Lesung** (Modul 11) nicht auf JSON umstellen — sonst bricht `{Store}` auf die JTL-Nummer.
