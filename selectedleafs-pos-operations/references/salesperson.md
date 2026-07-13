# Salesperson — neuen Vertriebler anlegen (pos-salesperson)

Legt einen neuen Vertriebler **dialog-initiiert** über zwei Fachsysteme an: Lexware (Kontakt + `POS-SHEET`-Notiz) und Google Sheets (Kopie der leeren Provisions-Vorlage, umbenannt, Jahr gesetzt). Der Agent führt **keinen** Dialog — der fertige Auftrag kommt von der `agent-bridge` als `user.message` (Onboarding-Entry-Point Topic `92`, `registry.md` §3). Anders als `pos-restock`/`pos-inventory` reagiert dieser Agent auf **kein** eingehendes Artefakt (PDF, Protokoll) — er ist **erzeugend**: der Lexware-Kontakt und der `POS-SHEET`-Marker, an denen alle anderen POS-Agenten hängen (`registry.md` §4), entstehen erst in diesem Lauf. Kein Sprung in `store.md`/`invoice.md` nötig — beide lesen später nur das Ergebnis dieses Laufs.

---

## 1. Input-Kontrakt (Bridge-Injektion)

Die `agent-bridge` injiziert in die `user.message`:

| Feld | Pflicht | Inhalt | Nutzung |
|---|---|---|---|
| `salesperson_name` | ja | Klartext-Name des Vertrieblers (Person oder Firma) | Lexware-Kontaktname (§3), Sheet-Name (§4) |
| `year` | ja | Abrechnungsjahr als Zahl | Sheet-Name-Suffix (§4), `Allgemein!Jahr`-Wert (§6) |
| `contact_fields` | optional | Adresse/E-Mail/Telefon, falls vom Vertriebler erfasst | in `create_contact` mitgeben, falls vorhanden |
| `chat_id` + `message_thread_id` | ja | Quell-Topic des Auftrags | Ziel der Status-/Rückfrage-Posts (§7) |

Fehlt `salesperson_name` oder `year` → fail-closed **vor** jedem Read/Write, Status ins Topic (§7). `contact_fields` ist kein Kontrakt-Pflichtfeld — fehlt es, wird der Kontakt ohne diese Felder angelegt (manuelle Nachpflege, wie `store.md` bei USt-ID/Rechtsform).

**`year` wird injiziert, nicht aus der Sandbox-Uhr abgeleitet.** Der Jahres-Anker ist Stammdaten, an dem die gesamte `invoice.md`-Kette hängt (§2.3-Jahres-Guard) — eine geratene oder aus Systemzeit abgeleitete Zahl ist hier keine zulässige Quelle (Invariante 2, `SKILL.md`).

---

## 2. Ablauf-Prinzip — Kontakt zuerst, find-or-create pro Schritt

Drei Invarianten, die den ganzen Lauf tragen (Konkretisierung von `SKILL.md` §Invarianten):

1. **Reihenfolge ist fest, nicht neu abzuwägen:** (1) Lexware-Kontakt anlegen/finden → UUID · (2) Vorlage kopieren → neue Sheet-ID, umbenennen, in die Invoice-Wurzel ablegen · (3) `POS-SHEET`-Marker in die `note` schreiben (read-modify-write) · (4) Jahr im Tab `Allgemein` setzen (label-basiert). Jeder Schritt braucht das Ergebnis des vorherigen — kein Parallelisieren.
2. **find-or-create pro Schritt, kein globaler Vorab-Check.** Genau wie `store.md` §2: ein einziger Vorab-Check würde bei einem Ausfall nach Schritt 2 (Sheets-Kopie erstellt, aber Marker-Write gescheitert) den Re-Run zwingen, alles neu zu prüfen. Stattdessen prüft **jeder** Schritt einzeln, ob sein Artefakt schon existiert (§3–§6), und ein Re-Run heilt nur das Fehlende.
3. **fail-closed statt Improvisation.** Schlägt ein Tool-Aufruf fehl oder liefert Unerwartetes, sofort abbrechen, Status ins Quell-Topic (§7), keine Wege außerhalb der Tool-Oberfläche suchen.

**Idempotenz-Wurzel = der Lexware-Kontakt-`find` in §3.** Er entscheidet, ob dieser Lauf ein Erst-Onboarding oder ein Heal ist. Die Sheet-Suche in §4 (deterministischer Name `<salesperson_name> <year>` in der Invoice-Wurzel) läuft **zusätzlich** und unabhängig — sie ist die Heal-Sicherung für genau den Fall, dass Schritt 2 schon lief, Schritt 3 aber nicht: kein Re-Copy, nur der Marker-Write wird nachgeholt.

---

## 3. Lexware-Kontakt find-or-create (Idempotenz-Wurzel)

**find:** `list_contacts`/Suche nach `salesperson_name`.

| Treffer-Lage | Verhalten |
|---|---|
| **Kein Treffer** | `create_contact` (Rolle `customer`, aus `contact_fields` falls vorhanden), `note` bleibt zunächst leer — der Marker kommt erst in §5, **nicht** in diesem Call (anders als `store.md` §8.2, wo `POS-PARTNER` atomar mitgeschrieben wird: hier existiert die Sheet-ID zum Anlage-Zeitpunkt noch nicht, der Marker-Wert wäre unbekannt). |
| **Genau ein Treffer, `note` trägt bereits `POS-SHEET:`** | **fail-closed + Rückfrage** (§7) — der Vertriebler existiert schon vollständig, ein zweiter Lauf wäre eine Doppelanlage. Kein Adoptieren, keine Änderung. |
| **Genau ein Treffer, `note` trägt `POS-SHEET:` (noch) nicht** | **Heal-Pfad:** Kontakt wiederverwenden (Schritt 3 muss vor diesem Lauf abgebrochen sein), weiter zu §4 mit dieser UUID. |
| **Mehr als ein Treffer** | **fail-closed + Rückfrage** (§7) — Namensvetter sind nicht automatisch unterscheidbar; nicht raten, welcher gemeint ist (Invariante 2). |

**Read-back:** `get_contact` der neuen/gefundenen ID → Kontakt-**UUID** für §4/§5.

> **Warum der Kontakt-`find` die Idempotenz-Wurzel ist, nicht die UUID.** Die UUID entsteht erst in diesem Schritt und wird im weiteren Verlauf dieses Agenten selbst nirgends als Vergleichswert konsumiert (der `POS-SHEET`-Marker trägt die Sheet-ID, nicht die UUID) — sie ist reines Durchreichfeld für §4/§5. Die tragende Frage „gibt es diesen Vertriebler schon" beantwortet ausschließlich der Namens-`find` oben.

---

## 4. Sheet find-or-create — Kopie der Vorlage, umbenannt, in die Invoice-Wurzel

Ziel-Name: `<salesperson_name> <year>` (z. B. `Christian Schlegel 2026`). Ziel-Ordner: Invoice-Wurzel (`registry.md` §2).

**find:** `list_files` in der Invoice-Wurzel, Name = Ziel-Name. **Treffer** → dessen Datei-ID wiederverwenden (Heal — Schritt 2 lief bereits, weiter zu §5), **keine** Neu-Kopie. **Kein Treffer:**

1. `copy_file` der Vorlage (`registry.md` §2, ID `1coPnoXdNgjuaNvyS6UriH5vjk8NZMMEPce1bxJzlAyY`) → neue Spreadsheet-ID.
2. `rename_file` → `<salesperson_name> <year>`.
3. `move_file` in die Invoice-Wurzel (`registry.md` §2, `parentFolderId`).

> **Build-seitig verifizieren:** Falls `copy_file` Ziel-`parents` in einem Aufruf akzeptiert, Schritt 1+3 zu einem Call zusammenziehen — schließt das Crash-Fenster zwischen Kopie und Move, in dem eine Datei außerhalb der Invoice-Wurzel läge. Sonst bleibt es bei drei Calls; ein Re-Run findet die Datei über `list_files` unabhängig vom aktuellen Ordner nicht zuverlässig, wenn sie noch am Vorlagen-Ort liegt — deshalb `move_file` **vor** jedem Abbruchpunkt als eigener, read-back-geprüfter Schritt.

**Read-back:** `list_files` erneut mit Ziel-Name in der Invoice-Wurzel → genau ein Treffer, ID notiert für §5/§6.

---

## 5. `POS-SHEET`-Marker schreiben (read-modify-write)

Ziel: Lexware-Kontakt aus §3, Feld `note`.

1. `get_contact` → aktuelle `note` lesen.
2. **Nur die eigene Zeile ändern:** trägt `note` bereits eine `POS-SHEET:`-Zeile (Heal-Fall, Wert weicht ab oder stimmt schon überein) → per Regex **ausschließlich** diese eine Zeile ersetzen, Rest der `note` unangetastet lassen. Trägt sie noch keine → Zeile `POS-SHEET: <sheet-id>` anhängen.
3. `update_contact` mit der vollständigen, so modifizierten `note` (**einziges** geändertes Feld, volles Objekt + `version` mitsenden — wie `store.md` §8.2).

**Format zwingend** (`registry.md` §4): Präfix inkl. Doppelpunkt, genau ein Leerzeichen, dann der getrimmte Wert. **Kein Jahres-Suffix** — der Marker ist jahresblind (Bridge-Vertrag, `registry.md` §4); `pos-rollover` setzt später nur den Wert um, dieser Agent legt ihn erstmalig an.

**Read-back:** `get_contact` → `note` enthält exakt eine `POS-SHEET:`-Zeile mit der Sheet-ID aus §4.

**Fehlschlag-Verhalten:** Scheitert `update_contact`, ist Schritt 4 (Rest der Kette) **nicht** erreichbar — ein Re-Run beginnt wieder bei §3, findet den Kontakt (Heal-Pfad, markerlos), findet das Sheet über den deterministischen Namen (§4, kein Re-Copy) und holt ausschließlich den Marker-Write nach.

---

## 6. Jahr im Tab `Allgemein` setzen (label-basiert)

Ziel-Spreadsheet-ID aus §4.

1. `get_range("Allgemein!B:C")` → Zeile mit Label `Jahr` in Spalte B suchen. **Label-basiert, nie `C5` hardcoden** (dieselbe Regel wie `invoice.md` §2.3).
2. **Label nicht gefunden** → fail-closed + Rückfrage (§7) — eine frische Kopie der Vorlage muss den Anker tragen; fehlt er, ist die Vorlage selbst defekt.
3. **Label gefunden, Wert leer oder ≠ `year`** → `update_cell` auf die zugehörige C-Zelle → `year` aus §1.
4. **Label gefunden, Wert bereits = `year`** → No-op (Heal, nichts zu tun).

**Read-back:** `get_range` auf dieselbe Zelle → Wert bestätigt `year`.

---

## 7. fail-closed & Status-Posts ins Operations-Topic

Ziel jeder Meldung: `chat_id` + `message_thread_id` aus der Injektion (§1) — das Quell-Topic, aus dem der Auftrag kam (Onboarding-Entry-Point, `registry.md` §3, Topic `92`).

| Ausgang | Status (Beispiel) |
|---|---|
| Anlage erfolgreich (CREATE) | „✅ Vertriebler angelegt: **Christian Schlegel** — Lexware-Kontakt + Provisions-Sheet 2026 (`<sheet-id>`). `POS-SHEET`-Marker gesetzt." |
| Re-Run/bereits vorhanden (Heal-Zweig) | „ℹ️ Vertriebler **<Name>** existiert bereits mit vollständigem `POS-SHEET`-Marker — nichts zu tun." |
| Fehlendes Pflichtfeld (§1) | „⚠️ Vertriebler-Anlage abgebrochen: Pflichtfeld `<feld>` fehlt in der Auftrags-Nachricht." |
| Mehrdeutiger Namenstreffer (§3) | „⚠️ Vertriebler-Anlage abgebrochen: `<n>` Kontakte zu „<Name>" gefunden — welcher ist gemeint? Bitte Kontakt-ID nennen." |
| Marker existiert bereits (§3) | „⚠️ Vertriebler-Anlage abgebrochen: „<Name>" hat bereits einen `POS-SHEET`-Marker (`<sheet-id>`) — keine Doppelanlage." |
| Sheet-Vorlage ohne `Jahr`-Anker (§6) | „⚠️ Vertriebler-Anlage abgebrochen: Provisions-Sheet ohne `Jahr`-Label im Tab `Allgemein` — Vorlage prüfen." |
| Write fehlgeschlagen (§3/§4/§5/§6) | „⚠️ Vertriebler-Anlage abgebrochen nach `<Kontakt\|Sheet\|Marker\|Jahr>` — `<konkreter Fehler>`. Re-Run heilt den Rest." |

```
post_message(
  chat_id           = <injiziert>,
  message_thread_id = <injiziert>,
  text              = "<Status-Zeile>",
  parse_mode        = "HTML"
)
```

Der Agent postet **nichts**, wenn ein Schritt erfolgreich war, aber ein späterer scheitert, außer der abschließenden ⚠️-Abbruchzeile — **kein** „halb erfolgreich, ignorier den Rest" (gleiche Philosophie wie `store.md` §9).

---

## 8. Non-Goals (bewusst außerhalb dieser Kette)

- **Kein Shopify.** Der Vertriebler ist keine `liftr_store`-Entität — `pos-store` verankert später `POS-PARTNER` auf dem *Store*-Kontakt und verweist per UUID hierher.
- **Kein öffentlicher Broadcast.** Anders als `store.md` §8.5 (🎉-City-Broadcast) ist Vertriebler-Onboarding ein rein internes Ops-Ereignis — kein Post auf einem City-Channel, keine `telegram-broadcast`-Anbindung.
- **Kein Jahres-Rollover bestehender Vertriebler.** Ein Vertriebler mit **existierendem** `POS-SHEET`-Marker wird nicht auf ein neues Jahr umgehängt (§3, mehrdeutiger/vorhandener Treffer → fail-closed) — das ist `pos-rollover` (→ `rollover.md`, geplant).
- **Keine USt-ID/Rechtsform-Anreicherung.** Wie `store.md` — manuelle Nachpflege am Lexware-Kontakt.
- **Kein Löschen/Archivieren alter Vertriebler.** Reines Onboarding, keine Lifecycle-Verwaltung.
- **Kein Bridge-/Dialog-Bau.** Der Input-Kontrakt (§1) ist die Schnittstelle; die Bridge, die ihn füllt (Topic `92`-Watch oder Command), ist ein eigener, downstream Schritt.
