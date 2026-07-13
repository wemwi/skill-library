# Salesperson — neuen Vertriebler anlegen (pos-salesperson)

Legt einen neuen Vertriebler **dialog-initiiert** über zwei Fachsysteme an: Lexware (Kontakt als **Lieferant** + `POS-SHEET`-Notiz) und Google Sheets (Kopie der leeren Provisions-Vorlage in einen eigenen Vertriebler-Ordner, umbenannt, Stammdaten gesetzt, Ordner optional freigegeben). Der Agent führt **keinen** Dialog — der fertige Auftrag kommt von der `agent-bridge` als `user.message` (Onboarding-Entry-Point Topic `92`, `registry.md` §3). Anders als `pos-restock`/`pos-inventory` reagiert dieser Agent auf **kein** eingehendes Artefakt — er ist **erzeugend**: der Lexware-Kontakt und der `POS-SHEET`-Marker, an denen alle anderen POS-Agenten hängen (`registry.md` §4), entstehen erst in diesem Lauf. Kein Sprung in `store.md`/`invoice.md` nötig — beide lesen später nur das Ergebnis dieses Laufs.

---

## 1. Input-Kontrakt (Bridge-Injektion)

Die `agent-bridge` injiziert in die `user.message`:

| Feld | Pflicht | Inhalt | Nutzung |
|---|---|---|---|
| `first_name` | ja | Vorname des Vertrieblers | Lexware `person.firstName` (§3), Anzeige-/Kontaktname `<first_name> <last_name>` (§3, §6), Ordnername (§4) |
| `last_name` | ja | Nachname des Vertrieblers | Lexware `person.lastName` (§3), Ordnername `<last_name>, <first_name>` (§4), Dateiname `Provision · <last_name> · <year>` (§4) |
| `year` | ja | Abrechnungsjahr als Zahl | Dateiname (§4), `Allgemein!Jahr`-Wert (§6) |
| `taxation` | ja | Besteuerung, zeichengenau `Kleinunternehmer` **oder** `Regelbesteuert` | `Allgemein!Besteuerung`-Wert (§6) |
| `email` | optional | E-Mail des Vertrieblers, falls erfasst | Ordner-Freigabe als `reader` (§7) |
| `chat_id` + `message_thread_id` | ja | Quell-Topic des Auftrags | Ziel der Status-/Rückfrage-Posts (§8) |

Fehlt `first_name`, `last_name`, `year` oder `taxation` → fail-closed **vor** jedem Read/Write, Status ins Topic (§8). `email` ist **kein** Pflichtfeld — fehlt es, wird der Kontakt angelegt und das Sheet erstellt, aber der Ordner **nicht** freigegeben (§7, fail-open; manuelle Nachpflege wie `store.md` bei USt-ID/Rechtsform).

**`year` wird injiziert, nicht aus der Sandbox-Uhr abgeleitet.** Der Jahres-Anker ist Stammdaten, an dem die gesamte `invoice.md`-Kette hängt (§2.3-Jahres-Guard) — eine geratene oder aus Systemzeit abgeleitete Zahl ist hier keine zulässige Quelle (Invariante 2, `SKILL.md`).

**`taxation` ist zeichengenau.** Erlaubt sind exakt `Kleinunternehmer` oder `Regelbesteuert`. Diese Strings steuern per Sheet-Formel die USt-Behandlung: `Auszahlung!MwSt.` und `Allgemein!Offene Auszahlung` verzweigen auf `="Kleinunternehmer"`. Ein abweichender String triggert stumm die falsche Formel-Verzweigung oder eine Data-Validation-Warnung — der Agent schreibt den Wert deshalb **unverändert**, ohne Normalisierung.

---

## 2. Ablauf-Prinzip — Kontakt zuerst, find-or-create pro Schritt

Fünf Schritte, drei Invarianten (Konkretisierung von `SKILL.md` §Invarianten):

1. **Reihenfolge ist fest, nicht neu abzuwägen:** (1) Lexware-Kontakt (Lieferant) anlegen/finden → UUID · (2) Vertriebler-Ordner sicherstellen + Vorlage hineinkopieren/umbenennen → neue Sheet-ID · (3) `POS-SHEET`-Marker in die `note` schreiben (read-modify-write) · (4) Stammdaten im Tab `Allgemein` setzen (Name, Jahr, Besteuerung — label-basiert) · (5) Ordner freigeben (optional, best-effort, §7). Jeder Schritt braucht das Ergebnis des vorherigen — kein Parallelisieren.
2. **find-or-create pro Schritt, kein globaler Vorab-Check.** Genau wie `store.md` §2: ein einziger Vorab-Check würde bei einem Ausfall nach Schritt 2 (Sheet kopiert, aber Marker-Write gescheitert) den Re-Run zwingen, alles neu zu prüfen. Stattdessen prüft **jeder** Schritt einzeln, ob sein Artefakt schon existiert (§3–§6), und ein Re-Run heilt nur das Fehlende.
3. **fail-closed statt Improvisation.** Schlägt ein Tool-Aufruf fehl oder liefert Unerwartetes, sofort abbrechen, Status ins Quell-Topic (§8), keine Wege außerhalb der Tool-Oberfläche suchen. **Ausnahme:** die Ordner-Freigabe (§7) ist fail-open — ihr Scheitern bricht die Kette nicht ab.

**Idempotenz-Wurzel = der Lexware-Kontakt-`find` in §3.** Er entscheidet, ob dieser Lauf ein Erst-Onboarding oder ein Heal ist. Die Sheet-Suche in §4 (deterministischer Name `Provision · <last_name> · <year>` **im Vertriebler-Ordner**) läuft **zusätzlich** und unabhängig — sie ist die Heal-Sicherung für den Fall, dass Schritt 2 schon lief, Schritt 3 aber nicht: kein Re-Copy, nur der Marker-Write wird nachgeholt.

---

## 3. Lexware-Kontakt find-or-create (Idempotenz-Wurzel)

**find:** `list_contacts`/Suche nach `<first_name> <last_name>`.

| Treffer-Lage | Verhalten |
|---|---|
| **Kein Treffer** | `create_contact` mit **Rolle `vendor`** und `person.firstName`/`person.lastName` aus §1. `note` bleibt zunächst leer — der Marker kommt erst in §5, **nicht** in diesem Call (anders als `store.md` §8.2: hier existiert die Sheet-ID zum Anlage-Zeitpunkt noch nicht). |
| **Genau ein Treffer, `note` trägt bereits `POS-SHEET:`** | **fail-closed + Rückfrage** (§8) — der Vertriebler existiert schon vollständig, ein zweiter Lauf wäre eine Doppelanlage. Kein Adoptieren, keine Änderung. |
| **Genau ein Treffer, `note` trägt `POS-SHEET:` (noch) nicht** | **Heal-Pfad:** Kontakt wiederverwenden (Schritt 3 muss vor diesem Lauf abgebrochen sein), weiter zu §4 mit dieser UUID. |
| **Mehr als ein Treffer** | **fail-closed + Rückfrage** (§8) — Namensvetter sind nicht automatisch unterscheidbar; nicht raten (Invariante 2). |

**Read-back:** `get_contact` der neuen/gefundenen ID → Kontakt-**UUID** für §4/§5.

> **Warum `vendor`, nicht `customer`.** Der Vertriebler bekommt Provision ausgezahlt — buchhalterisch ein **Kreditor/Lieferant**, kein Kunde. Der **Store** ist der Lexware-Kunde (`roles.customer.number` = Store-Match-Key, `invoice.md` §2). Kein Agent liest die *Rolle* des Vertrieblers (er wird ausschließlich über den `POS-SHEET`-Marker + Name gefunden, §2.2 in `invoice.md`) — `vendor` hält daher den Kundennummernraum sauber (kein Vertriebler zwischen den Store-Kundennummern, `registry.md` §4).

> **Warum der Kontakt-`find` die Idempotenz-Wurzel ist, nicht die UUID.** Die UUID entsteht erst in diesem Schritt und wird im weiteren Verlauf selbst nirgends als Vergleichswert konsumiert (der `POS-SHEET`-Marker trägt die Sheet-ID, nicht die UUID) — sie ist reines Durchreichfeld für §4/§5. Die tragende Frage „gibt es diesen Vertriebler schon" beantwortet ausschließlich der Namens-`find` oben.

---

## 4. Ordner + Sheet find-or-create — eigener Vertriebler-Ordner, Kopie der Vorlage

Pro Vertriebler ein eigener Ordner (wie manuell für bestehende Partner), darin die Provisions-Sheet-Kopie:

- **Ordnername:** `<last_name>, <first_name>` (z. B. `Schlegel, Christian`).
- **Dateiname:** `Provision · <last_name> · <year>` (z. B. `Provision · Schlegel · 2026`). Trenner ist ` · ` (Leerzeichen–Mittelpunkt–Leerzeichen).
- **Ordner-Wurzel:** Invoice-Wurzel (`registry.md` §2).

**Schritte:**

1. **Ordner sicherstellen:** `ensure_folder_path(<Invoice-Wurzel>, ["<last_name>, <first_name>"])` → Ordner-ID. Idempotent — ein bestehender Ordner wird wiederverwendet, nie ein zweiter gleichnamiger angelegt.
2. **find:** `list_files(folderId=<Ordner-ID>)`, Name = `Provision · <last_name> · <year>`. **Treffer** → dessen Datei-ID wiederverwenden (Heal — Schritt 2 lief bereits, weiter zu §5), **keine** Neu-Kopie. **Kein Treffer:**
   1. `copy_file` der Vorlage (`registry.md` §2, ID `1coPnoXdNgjuaNvyS6UriH5vjk8NZMMEPce1bxJzlAyY`) → neue Spreadsheet-ID.
   2. `rename_file` → `Provision · <last_name> · <year>`.
   3. `move_file` in den Vertriebler-Ordner (Ordner-ID aus Schritt 1).

> **Der find läuft im Vertriebler-Ordner, nicht in der Invoice-Wurzel.** Läge das Sheet flach in der Wurzel, ein Re-Run aber suchte im Ordner (oder umgekehrt), würde ein bereits kopiertes Sheet nicht gefunden → **Doppel-Kopie**. Weil `ensure_folder_path` idempotent denselben Ordner liefert und die Suche **dort** läuft, bleibt der Heal-Pfad dicht. `move_file` **vor** jedem Abbruchpunkt als eigener, read-back-geprüfter Schritt — sonst läge die Kopie außerhalb des Ordners und der Re-Run-find verfehlte sie.

**Read-back:** `list_files(folderId=<Ordner-ID>)` mit Ziel-Name → genau ein Treffer, ID notiert für §5/§6.

---

## 5. `POS-SHEET`-Marker schreiben (read-modify-write)

Ziel: Lexware-Kontakt aus §3, Feld `note`.

1. `get_contact` → aktuelle `note` lesen.
2. **Nur die eigene Zeile ändern:** trägt `note` bereits eine `POS-SHEET:`-Zeile (Heal-Fall) → per Regex **ausschließlich** diese eine Zeile ersetzen, Rest der `note` unangetastet lassen. Trägt sie noch keine → Zeile `POS-SHEET: <sheet-id>` anhängen.
3. `update_contact` mit der vollständigen, so modifizierten `note` (**einziges** geändertes Feld, volles Objekt + `version` mitsenden — wie `store.md` §8.2).

**Format zwingend** (`registry.md` §4): Präfix inkl. Doppelpunkt, genau ein Leerzeichen, dann der getrimmte Wert. **Kein Jahres-Suffix** — der Marker ist jahresblind (Bridge-Vertrag, `registry.md` §4); `pos-rollover` setzt später nur den Wert um, dieser Agent legt ihn erstmalig an.

**Read-back:** `get_contact` → `note` enthält exakt eine `POS-SHEET:`-Zeile mit der Sheet-ID aus §4.

**Fehlschlag-Verhalten:** Scheitert `update_contact`, ist der Rest der Kette (§6/§7) **nicht** erreichbar — ein Re-Run beginnt wieder bei §3, findet den Kontakt (Heal-Pfad, markerlos), findet Ordner + Sheet über den deterministischen Namen (§4, kein Re-Copy) und holt ausschließlich den Marker-Write nach.

---

## 6. Stammdaten im Tab `Allgemein` setzen (label-basiert)

Ziel-Spreadsheet-ID aus §4. Drei Werte, **alle label-basiert** (Label in Spalte B, Wert in Spalte C) — **nie** Zellen wie `C4`/`C5`/`C11` hardcoden (dieselbe Regel wie `invoice.md` §2.3):

1. `get_range("Allgemein!B:C")` einmal lesen → die drei Label-Zeilen suchen.
2. **`Name`** → zugehörige C-Zelle = `<first_name> <last_name>` (voller Name). Die Kopfzeile `B1` ist `="Provision "&Jahr&" · "&Name` (Named Ranges) und aktualisiert sich dadurch selbst.
3. **`Jahr`** → zugehörige C-Zelle = `year`.
4. **`Besteuerung`** → zugehörige C-Zelle = `taxation` (exakt `Kleinunternehmer`/`Regelbesteuert`, §1).
5. Jeweils nur schreiben, wenn Wert leer oder ≠ Soll (Heal → No-op bei Gleichstand). `update_cell` je Zelle bzw. `batch_update_ranges` für die drei zusammen.

**`MwSt.` wird NIE gesetzt.** Die MwSt-Zeile (`Allgemein!C10`) ist ein konstanter Faktor; ob er greift, entscheiden Formeln anhand von `Besteuerung` (`Auszahlung!MwSt.` = `IF(Allgemein!C11="Kleinunternehmer";0;Allgemein!C10)`, `Allgemein!Offene Auszahlung` analog). Ein Schreibversuch auf MwSt wäre falsch.

**Label nicht gefunden** (`Name`, `Jahr` oder `Besteuerung`) → fail-closed + Rückfrage (§8) — eine frische Kopie der Vorlage muss alle drei Anker tragen; fehlt einer, ist die Vorlage defekt.

**Read-back:** `get_range` auf die drei C-Zellen → Werte bestätigt.

---

## 7. Ordner freigeben (optional, best-effort)

Trägt `email` (§1) einen Wert → den **Vertriebler-Ordner** (§4, nicht die Einzeldatei) als `reader` an diese Adresse freigeben (`share_file`, Rolle `reader`). Die Freigabe vererbt sich auf das enthaltene Sheet und künftige Jahres-Kopien.

- **Kein `email`** → Schritt überspringen, kein Fehler.
- **fail-open:** Scheitert die Freigabe (bereits geteilt, ungültige Adresse, Tool-Fehler) → **kein** Abbruch der Kette; der Vertriebler ist zu diesem Zeitpunkt bereits vollständig angelegt. Die Freigabe ist Komfort, nicht Kern (gleiche Philosophie wie der Broadcast in `store.md` §8.5). „Bereits geteilt" gilt als erreichter Zustand.
- **`reader` genügt:** alle Tabs des Provisions-Sheets sind schreibgeschützt (nur der Ersteller editiert); ein Viewer kann nichts verfälschen. Schreibrecht wäre unnötiges Risiko.

⚠️ **Die Freigabe legt die Kalkulation offen** (Einkauf pro kg, Kostensplit, MwSt) — bewusst so gewollt, damit der Vertriebler seine Abrechnung nachvollziehen kann.

---

## 8. fail-closed & Status-Posts ins Operations-Topic

Ziel jeder Meldung: `chat_id` + `message_thread_id` aus der Injektion (§1) — das Quell-Topic (Onboarding-Entry-Point, `registry.md` §3, Topic `92`).

| Ausgang | Status (Beispiel) |
|---|---|
| Anlage erfolgreich (CREATE), mit Freigabe | „✅ Vertriebler angelegt: **Christian Schlegel** — Lexware-Kontakt (Lieferant) + Provisions-Sheet 2026 (`<sheet-id>`). `POS-SHEET`-Marker gesetzt, Ordner freigegeben an `<email>`." |
| Anlage erfolgreich (CREATE), ohne Freigabe | „✅ Vertriebler angelegt: **Christian Schlegel** — Lexware-Kontakt (Lieferant) + Provisions-Sheet 2026 (`<sheet-id>`). `POS-SHEET`-Marker gesetzt. (Keine E-Mail — Ordner nicht freigegeben.)" |
| Re-Run/bereits vorhanden (Heal) | „ℹ️ Vertriebler **<n>** existiert bereits mit vollständigem `POS-SHEET`-Marker — nichts zu tun." |
| Fehlendes Pflichtfeld (§1) | „⚠️ Vertriebler-Anlage abgebrochen: Pflichtfeld `<feld>` fehlt in der Auftrags-Nachricht." |
| Mehrdeutiger Namenstreffer (§3) | „⚠️ Vertriebler-Anlage abgebrochen: `<n>` Kontakte zu „<n>" gefunden — welcher ist gemeint? Bitte Kontakt-ID nennen." |
| Marker existiert bereits (§3) | „⚠️ Vertriebler-Anlage abgebrochen: „<n>" hat bereits einen `POS-SHEET`-Marker (`<sheet-id>`) — keine Doppelanlage." |
| Sheet-Vorlage ohne Anker (§6) | „⚠️ Vertriebler-Anlage abgebrochen: Provisions-Sheet ohne Label `<Name\|Jahr\|Besteuerung>` im Tab `Allgemein` — Vorlage prüfen." |
| Write fehlgeschlagen (§3/§4/§5/§6) | „⚠️ Vertriebler-Anlage abgebrochen nach `<Kontakt\|Ordner\|Sheet\|Marker\|Stammdaten>` — `<konkreter Fehler>`. Re-Run heilt den Rest." |

```
post_message(
  chat_id           = <injiziert>,
  message_thread_id = <injiziert>,
  text              = "<Status-Zeile>",
  parse_mode        = "HTML"
)
```

Der Agent postet **nichts** bei einem Teilerfolg mit späterem Fehlschlag außer der abschließenden ⚠️-Abbruchzeile — **kein** „halb erfolgreich, ignorier den Rest" (gleiche Philosophie wie `store.md` §9). **Ausnahme:** die Freigabe (§7) ist fail-open — ihr Scheitern erscheint nur als Zusatz in der ✅-Zeile („Ordner nicht freigegeben"), nie als Abbruch.

---

## 9. Non-Goals (bewusst außerhalb dieser Kette)

- **Kein Shopify.** Der Vertriebler ist keine `liftr_store`-Entität — `pos-store` verankert später `POS-PARTNER` auf dem *Store*-Kontakt und verweist per UUID hierher.
- **Kein öffentlicher Broadcast.** Vertriebler-Onboarding ist ein rein internes Ops-Ereignis — kein City-Channel-Post, keine `telegram-broadcast`-Anbindung.
- **Kein Jahres-Rollover bestehender Vertriebler.** Ein Vertriebler mit **existierendem** `POS-SHEET`-Marker wird nicht auf ein neues Jahr umgehängt (§3, vorhandener Treffer → fail-closed) — das ist `pos-rollover` (→ `rollover.md`, geplant).
- **Kein Setzen der MwSt-Zelle** — nur `Besteuerung` (§6); die MwSt-Anwendung ist formelgesteuert.
- **Keine USt-ID/Rechtsform-Anreicherung.** Wie `store.md` — manuelle Nachpflege am Lexware-Kontakt.
- **Kein Löschen/Archivieren alter Vertriebler.** Reines Onboarding, keine Lifecycle-Verwaltung.
- **Kein Bridge-/Dialog-Bau.** Der Input-Kontrakt (§1) ist die Schnittstelle; die Bridge, die ihn füllt (Topic `92`-Dialog, Vorname/Nachname/Jahr/Besteuerung/E-Mail), ist ein eigener, downstream Schritt.
