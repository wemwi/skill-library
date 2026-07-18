# Rollover — Jahres-Rollover der Vertriebler-Provisions-Sheets (pos-rollover)

Legt zum **Jahreswechsel** für **jeden** Vertriebler ein neues Provisions-Sheet an (Kopie der leeren Vorlage, `registry.md` §2), befüllt es mit den **aktuell** zugeordneten Stores und den Stammdaten, und setzt den `POS-SHEET`-Marker am Lexware-Kontakt auf das neue Sheet um. Der Agent ist **cron-getrieben** (Scheduled Deployment, kein `agent-bridge`-Event, keine `user.message` mit Auftrag) und **erzeugend** — er reagiert auf **kein** eingehendes Artefakt. Diese reference ist **selbsttragend**: sie referenziert zur Laufzeit **keine** andere reference (Router-Invariante `SKILL.md`), nur `registry.md` für statische Werte. Die Sheet-Sequenz ist **bewusst identisch** zu `salesperson.md` §4/§6 — dort steht das ausführliche *Warum*; hier steht das *Was* eigenständig, damit der Agent mit `rollover.md` + `registry.md` auskommt.

---

## 1. Trigger & Zieljahr

**Cron — Scheduled Deployment**, einmal jährlich am **01. Januar, 04:00 Europe/Berlin** (`global-agent-framework` §8). Kein Webhook — es gibt kein externes „Neujahr"-Event; der Jahreswechsel ist planbar, also Cron.

- **Warum 04:00, nicht 00:00:** Der Zeitpunkt braucht **weiten Abstand zur Mitternacht**, weil das Zieljahr aus der Sandbox-Uhr abgeleitet wird (unten). 04:00 liegt eindeutig im neuen Jahr, klärt jede Verarbeitungs-Latenz, und meidet die DST-Falle (01–03 Uhr lokal) — im Januar ist ohnehin kein DST-Wechsel, der Abstand ist reine Absicherung.
- **Zieljahr = `date +%Y` zur Laufzeit** (bash in der Sandbox). Anders als `pos-salesperson` (dort ist `year` ein injiziertes Stammdatum, `salesperson.md` §1) hat Rollover **keine** Injektion — der Cron-Lauf trägt keinen Auftrag. Die Uhr ist hier die zulässige Quelle, **weil** der Trigger selbst das Jahres-Ereignis ist und der 04:00-Abstand die Silvester-Kippgefahr ausschließt. **Falsifizierbar:** Wäre das Jahr falsch, trüge jedes neue Sheet ein falsches `Allgemein!Jahr` → `invoice.md` §2.3 lehnte ab da **jeden** Beleg des laufenden Jahres ab (lautes Signal, keine stille Fehlbuchung).
- **Manual-Run-Endpoint** (`global-agent-framework` §8) ist der Test- **und** Heal-Weg: ein Teil-Ausfall im Batch wird durch erneutes manuelles Auslösen geheilt (§2, §4). Bei Manual-Run gilt dasselbe Zieljahr aus der Uhr — deshalb Manual-Runs zum Heilen **innerhalb** des Zieljahres auslösen, nicht im Vorjahr.

---

## 2. Batch-Rahmen — ein Voll-Scan, dann Loop

**Ein einziger Voll-Scan aller Lexware-Kontakte pro Lauf**, dann in-memory verarbeiten. Grund: Lexware hat **keinen** serverseitigen `note`-Filter — dieselbe Lage wie `agent-bridge.fetchVertriebler()`, das alle Kontakte paginiert und client-seitig filtert. Ein Scan **pro Vertriebler** wäre O(Vertriebler × alle Kontakte); der eine Voll-Scan ist O(alle Kontakte) **und** liefert einen konsistenten Snapshot (kein Mid-Run-Drift der Zuordnung).

1. `list_contacts` **vollständig paginieren** → aus dem Ergebnis zwei Strukturen bauen:
   - **Vertriebler-Liste:** jeder Kontakt mit `note.includes("POS-SHEET:")` (Präsenz, nicht Wert — Bridge-Vertrag `registry.md` §4). Pro Eintrag: Kontakt-**UUID**, Name, aktueller `POS-SHEET`-Wert (die **Alt-Sheet-ID**).
   - **Store-Index:** jeder Kontakt mit `note.includes("POS-PARTNER:")` → Map `{ vertriebler-uuid → [ { customerNumber, name } ] }`, wobei `vertriebler-uuid` = getrimmter Wert nach `POS-PARTNER:` und `customerNumber` = `roles.customer.number` des Store-Kontakts (Match-Key, `registry.md` §4). Store-Kontakte **ohne** wohlgeformte `roles.customer.number` werden **nicht** in den Index aufgenommen (kein Blank-Key ins Sheet, §5.2).
2. **Loop über die Vertriebler-Liste.** Jeder Vertriebler ist eine **eigene fail-closed-Einheit** (§3): Ein Fehler in einem heilt via Manual-Run, ohne die bereits erfolgreichen erneut zu kopieren (§4). **Kein** Voll-Abbruch des Batches bei Einzel-Fehler — nur diese eine Einheit endet, der Loop läuft weiter, der Fehler geht in die Abschluss-Meldung (§7).
3. **Abschluss:** genau **eine** Summenzeile ins Ops-Topic (§7), plus der Late-Voucher-Hinweis. Das ist das Lebenssignal des Laufs — sein **Ausbleiben** ist das Ausfallsignal (Muster wie `invoice.md` §1b).

**fail-closed als Default** (`global-agent-framework` §13): Schlägt innerhalb einer Einheit ein Tool-Aufruf fehl oder liefert Unerwartetes, endet **diese Einheit** mit konkretem Fehler in der Sammelmeldung; der Agent sucht **keine** Wege außerhalb seiner Tool-Oberfläche.

---

## 3. Ablauf pro Vertriebler — Reihenfolge ist fest

Sechs Schritte, Reihenfolge **nicht** neu abzuwägen. Der Marker-Flip ist **zwingend der letzte** Schritt — erst wenn Stammdaten **und** Stores stehen, sonst zeigt `pos-invoice` auf ein halbfertiges Sheet.

0. **Idempotenz-Gate** (§4) → entscheidet skip / heal / create.
1. **Alt-Sheet lesen:** `Besteuerung` (und `Name`-Abgleich) aus dem **aktuellen** (Vorjahres-)Sheet — dessen ID ist der Pre-Flip-`POS-SHEET`-Wert aus §2.1. `get_range("Allgemein!B:C")`, label-basiert (§5.1). Die Besteuerung steht **nur** im Sheet, nicht in Lexware — ohne diesen Read wäre die Auszahlungsformel des neuen Sheets falsch.
2. **Ordner + neues Sheet find-or-create** (§5, Sequenz wie `salesperson.md` §4): `ensure_folder_path(<Invoice-Wurzel>, ["<Nachname>, <Vorname>"])` → leere Vorlage `copy_file` → `rename_file` → `Provision · <Nachname> · <Zieljahr>` → `move_file` in den Ordner. Der Ordner ist **derselbe** wie bei `salesperson` — Rollover legt **keinen** neuen an, `ensure_folder_path` löst den bestehenden idempotent auf.
3. **Stammdaten setzen:** `Name` (aus Lexware-Kontakt), `Jahr` (Zieljahr), `Besteuerung` (aus Schritt 1) — label-basiert (§5.1).
4. **Stores befüllen:** aktuelle Stores dieses Vertrieblers aus dem Store-Index (§2) → `Partner`-Table im `Stores`-Tab (§5.2).
5. **`POS-SHEET`-Marker umsetzen** (§6) — read-modify-write, **nur** die eigene Marker-Zeile, auf die neue Sheet-ID. **Letzter Schritt.**

**find-or-create pro Schritt, kein globaler Vorab-Check** (wie `salesperson.md` §2 / `store.md` §2): Jeder Schritt prüft einzeln, ob sein Artefakt schon existiert, damit ein Heal-Re-Run nur das Fehlende nachzieht statt neu zu kopieren.

---

## 4. Idempotenz — zwei Gates, der Marker-Flip ist das Signal

Cron kann doppelt feuern (Retry, versehentlicher Zweit-Manual-Run); der Batch muss **pro Vertriebler pro Jahr genau einmal** wirken (`global-agent-framework` §9, `SKILL.md` Invariante 1). Zwei unabhängige Gates:

- **Gate A — Marker zeigt schon aufs Zieljahr:** aktueller `POS-SHEET`-Wert (§2.1) auflösen → `get_range("Allgemein!Jahr")` (label-basiert) des referenzierten Sheets. Ist dessen Jahr **== Zieljahr**, ist dieser Vertriebler bereits gerollt → **skip** (No-op, zählt in der Summe als „übersprungen"). Das ist der primäre Idempotenz-Schlüssel: **der Marker-Flip in §6 ist erst der letzte Schritt**, also bedeutet „Marker zeigt aufs Zieljahr" zwingend „alle vorherigen Schritte liefen durch".
- **Gate B — Sheet existiert, Marker aber (noch) nicht geflippt (Heal):** deterministischer find von `Provision · <Nachname> · <Zieljahr>` **im Vertriebler-Ordner** (`list_files(folderId=…)`, **nicht** flache Wurzel). Treffer bei **noch nicht** geflipptem Marker → Schritt 2 lief bereits, aber 3/4/5 (oder nur 5) brach ab. **Kein Re-Copy** — die gefundene Sheet-ID wiederverwenden, fehlende Fill-Schritte + den Marker-Flip nachholen.

> **Der find läuft im Vertriebler-Ordner, nicht in der Invoice-Wurzel** — exakt die Falle aus `salesperson.md` §4: läge das Sheet flach in der Wurzel, der Re-Run suchte aber im Ordner (oder umgekehrt), entstünde eine **Doppel-Kopie**. `ensure_folder_path` liefert idempotent denselben Ordner, die Suche läuft **dort**, `move_file` ist ein read-back-geprüfter Schritt **vor** jedem Abbruchpunkt.

**Kein externer State nötig** (web-only-tauglich): Drive (Sheet-Existenz) + Lexware (`POS-SHEET`-Wert) + das Sheet selbst (`Allgemein!Jahr`) sind gemeinsam die Quelle der Wahrheit. Beide Gates zusammen: Gate A fängt den vollständig gerollten Vertriebler, Gate B den halb gerollten.

---

## 5. Sheet befüllen

### 5.1 Stammdaten im Tab `Allgemein` (label-basiert)

Ziel = neues Sheet (§3.2). Drei Werte, **alle label-basiert** (Label in Spalte B, Wert in Spalte C) — **nie** `C4`/`C5`/`C11` hardcoden (Regel wie `salesperson.md` §6 / `invoice.md` §2.3):

1. `get_range("Allgemein!B:C")` des neuen Sheets → die drei Label-Zeilen suchen.
2. **`Name`** → C = `<Vorname> <Nachname>` (voller Name aus dem Lexware-Kontakt). Die Kopfzeile `B1` (`="Provision "&Jahr&" · "&Name`, Named Ranges) aktualisiert sich dadurch selbst.
3. **`Jahr`** → C = Zieljahr (§1).
4. **`Besteuerung`** → C = der aus dem **Alt-Sheet** gelesene Wert (§3.1), **unverändert** übernommen (exakt `Kleinunternehmer`/`Regelbesteuert` — die Strings steuern per Formel `Auszahlung!MwSt.` und `Allgemein!Offene Auszahlung`; keine Normalisierung).
5. Jeweils nur schreiben, wenn leer oder ≠ Soll (Heal → No-op bei Gleichstand). `batch_update_ranges` für die drei zusammen.

**`MwSt.` wird NIE gesetzt** — konstanter Faktor, formelgesteuert über `Besteuerung` (wie `salesperson.md` §6).

**Label nicht gefunden** (`Name`/`Jahr`/`Besteuerung`) **im neuen Sheet** → fail-closed für diese Einheit (§7): eine frische Vorlagen-Kopie muss alle drei Anker tragen (`salesperson`/`store` verlassen sich produktiv darauf). **`Besteuerung`-Label fehlt im Alt-Sheet** (§3.1) → ebenfalls fail-closed: ohne Quellwert kein korrektes neues Sheet.

**Read-back:** `get_range` auf die drei C-Zellen → Werte bestätigt.

### 5.2 Stores — `Partner`-Table im `Stores`-Tab (Key = Lexware-Kundennummer)

Ziel = `Partner`-Table im `Stores`-Tab des neuen Sheets (dieselbe Table, gegen die `invoice.md` §4 matcht und in die `store.md` §8.3 laufend Zeilen einfügt). Quelle = der **Store-Index** dieses Vertrieblers (§2), also die **aktuell** in Lexware zugeordneten Stores — **nicht** das alte Sheet. Das ist die entschiedene Store-Quelle: Lexware bestimmt das **Set** (ein mid-Jahr geschlossener Partner hat keinen `POS-PARTNER`-Marker mehr und fällt automatisch raus), es gibt **keine** Set-Merge-Logik gegen das Vorjahres-Sheet.

Pro Store aus dem Index **eine** Zeile, Mechanik **identisch** zu `store.md` §8.3 (die den ersten Insert in ein frisch aus derselben Vorlage kopiertes, leeres `Partner`-Table produktiv beherrscht):

**find (Heal):** `get_range("Stores!B5:B")` des neuen Sheets → ist die Kundennummer bereits Key → **kein** erneuter Insert, weiter zum nächsten Store. Sonst Insert:

1. `list_tables(spreadsheetId, sheetId=<Stores-gid>)` → `columnProperties` (Header-Name → Index) **und** aktuelle Table-`range` (`endRowIndex`). Nie Buchstaben/Zeilen hardcoden, **pro Insert neu lesen** (Table wächst mit jeder Zeile).
2. Footer vorhanden: Insert-Index = `endRowIndex − 1` via `insert_dimension` mit `inheritFromBefore: true` (schiebt Footer nach unten, vererbt die Formelspalten). Ohne Footer: an `endRowIndex` innerhalb der Table.
3. `batch_update_ranges` (`USER_ENTERED`), Zuordnung **über Header-Namen** aus Schritt 1:

   | Spalte (Header) | Wert |
   |---|---|
   | **Lexware ID** | `roles.customer.number` aus dem Index, als **Zahl** — numerischer Vergleich in `invoice.md` §4; ein String liefe `SUMIFS` still auf 0 |
   | **Name** | Store-Name aus dem Index (Lexware-Kontaktname) — reine **Anzeige**, kein Match-Key. Siehe Kasten. |
   | **Menge / Einheiten / Umsatz / Provision** | Formelspalten — **nie** schreiben (durch `inheritFromBefore` vererbt) |

   - **`Akquise` wird von Rollover NICHT geschrieben** (bleibt leer) — das Erst-Akquise-Datum steht nur im Ursprungs-Sheet des Anlage-Jahres und ist in Lexware nicht vorhanden; es aus dem Alt-Sheet zu ziehen wäre „Sheet-zu-Sheet" (bewusst vermieden). `Akquise` ist eine reine Record-Spalte, **kein** Formel-Input — leer ist funktional folgenlos.
   - **`Übergabeprotokolle`/`Bestandsprotokolle` (E/F) werden NICHT geschrieben** — Rich-Link-Chips auf Drive-Ordner, die `store.md` §8.4 pro Store setzt; Rollover hat dazu weder die Ordner-Chips noch einen Grund (die Protokoll-Ordner sind jahresübergreifend, nicht pro Sheet). Kein Chip über die Values-API (Invariante 4).
   - Es gibt **keine** Spalte `Status`. Nur die zwei Text-Wertespalten oben.
4. **Read-back:** `get_range` auf die Key-Zelle → Kundennummer numerisch bestätigt; `list_tables` erneut → `endRowIndex` um 1 gewachsen.

> **Name-Quelle = Lexware-Kontaktname, nicht `liftr_store.name`.** `store.md` §8.3 schreibt den Shopify-Metaobjekt-Namen; Rollover ist **Lexware-only** (kein Shopify-MCP, Least-Privilege) und nimmt den Kontaktnamen. Beide bezeichnen denselben Store, können aber zeichenweise minimal abweichen. Weil `Name` reine **Anzeige** ist (Match-Key ist die Kundennummer in `Stores!B`, `invoice.md` §4), ist das folgenlos. Wer strikte Namensgleichheit oder das historische `Akquise`-Datum je Zeile will, müsste Rollover das Vorjahres-`Partner`-Table als Enrichment lesen lassen (per Kundennummer) — das ist **bewusst nicht** der Default (verletzt „keine Sheet-zu-Sheet").

**Vertriebler ohne Stores** (leerer Index-Eintrag oder gar keiner): neues Sheet wird trotzdem angelegt, Stammdaten gesetzt, Marker geflippt — nur `Partner` bleibt leer. Legitim (alle Partner geschlossen). In der Summe als „0 Stores" vermerkt (§7), **kein** Fehler.

---

## 6. `POS-SHEET`-Marker umsetzen (letzter Schritt, read-modify-write)

Ziel = Lexware-Vertriebler-Kontakt (§2.1), Feld `note`. **Erst ausführen, wenn §5.1 und §5.2 durch sind.**

1. `get_contact(<uuid>)` → aktuelle `note` lesen.
2. **Nur die `POS-SHEET`-Zeile ändern** (Marker-Invariante `registry.md` §4, zeilen-gebundenes Schreiben): per Regex ausschließlich die bestehende `POS-SHEET:`-Zeile durch `POS-SHEET: <neue-sheet-id>` ersetzen, Rest der `note` (inkl. etwaiger anderer Marker — insb. `POS-TG`, `store.md` §8.6) **unangetastet**. Format zwingend (`registry.md` §4): Präfix inkl. Doppelpunkt, genau ein Leerzeichen, getrimmter Wert, **kein** Jahres-Suffix (der Marker ist jahresblind — Bridge-Vertrag; ein `POS-SHEET-2026:` bräche `agent-bridge.fetchVertriebler()`).
3. `update_contact` mit der vollständigen, so modifizierten `note` (einziges geändertes Feld, volles Objekt + `version` mitsenden, wie `store.md` §8.2 / `salesperson.md` §5).

**Read-back:** `get_contact` → `note` enthält genau eine `POS-SHEET:`-Zeile mit der neuen Sheet-ID. Ab diesem Read greift Gate A (§4) bei künftigen Läufen.

**Warum zuletzt:** Zwischen altem und neuem Jahr liest `pos-invoice` den Marker (`invoice.md` §2.2). Flippt Rollover ihn **vor** dem Befüllen, zeigt Invoice auf ein leeres/halbes Sheet und der Jahres-Guard (§2.3) oder falsche Summen greifen. Nach dem Flip zeigt der Marker auf ein **vollständiges** Sheet.

---

## 7. Status-Posts ins Ops-Topic + Late-Voucher-Hinweis

`registry.md` §3 hat **keinen** dedizierten Rollover-Topic. Wie `invoice.md` §9 postet Rollover vorerst ins **General**-Topic des Operations-Chats (`chat_id` `-1003918922935`, `message_thread_id` **weglassen** → General; `message_thread_id: 1` wird als „thread not found" abgelehnt). Sobald ein Rollover-Topic existiert, ist das eine einzeilige `registry.md`-Ergänzung.

**Genau zwei Posts pro Lauf**, beide am Ende:

1. **Summenzeile (Lebenssignal, immer — auch bei 0/0):**
   „✅ **Jahres-Rollover {Zieljahr}** — {A} gerollt, {B} übersprungen (bereits {Zieljahr}), {C} Fehler · {Σ Stores} Store-Zeilen.“ (Kopf-Emoji → ⚠️ sobald {C} > 0; Fehler-Einheiten einzeln **mit Grund** darunter — Batch-Format, Invariante 6.)
   Fehler-Einheiten (§2/§3) einzeln anhängen: „⚠️ {Name}: abgebrochen nach `<Alt-Read|Ordner|Sheet|Stammdaten|Stores|Marker>` — `<konkreter Fehler>`. Re-Run (Manual-Run) heilt."
2. **Late-Voucher-Hinweis (einmalig, direkt nach dem Rollover):**
   „ℹ️ Marker zeigen jetzt auf {Zieljahr}. Verspätete {Vorjahr}-Belege (voucherDate im Vorjahr) laufen ab jetzt in den Jahres-Guard von `pos-invoice` (§2.3) → sie werden **nicht** automatisch eingetragen und müssen **manuell** ins archivierte {Vorjahr}-Sheet. Die alten Sheets bleiben dafür erhalten."

```
post_message(
  chat_id = -1003918922935,   # Operations-Chat, registry.md §3
  # message_thread_id weglassen -> General
  text = "<Zeile>",
  parse_mode = "HTML"
)
```

**Kein City-Channel-Post** — Rollover ist rein intern, kein Posting-Recht auf öffentliche Channels (Least-Privilege).

---

## 8. Non-Goals (bewusst außerhalb dieser Kette)

- **Kein Löschen/Archivieren alter Sheets.** Das Vorjahres-Sheet bleibt bestehen — es ist Archiv **und** das Ziel für den manuellen Nachtrag verspäteter Vorjahresbelege (§7, `invoice.md` §2.3). Löschen bräche diesen Pfad.
- **Keine Sonderbehandlung verspäteter Vorjahresbelege.** Rollover baut **keinen** Mechanismus dafür — der Jahres-Guard von `pos-invoice` (§2.3) fängt sie bereits fail-closed ab (Sheet-Jahr ≠ Beleg-Jahr → Abbruch + Rückfrage), der Mensch trägt manuell ins alte Sheet nach. Rollovers einziger Beitrag: das alte Sheet **nicht** anfassen. Diese Interaktion ist der Grund, warum kein neuer Mechanismus nötig ist.
- **Keine Set-Merge-Logik gegen das Vorjahres-Sheet.** Das Store-Set kommt allein aus Lexware (`POS-PARTNER`-Enumeration, §2/§5.2); es gibt keinen Diff/Abgleich „welche Stores fielen weg / kamen dazu" gegen die alte `Partner`-Table.
- **Kein Shopify.** Store-Namen kommen aus dem Lexware-Kontakt, nicht aus `liftr_store` (§5.2-Kasten). Kein Shopify-MCP an diesem Agenten.
- **Kein Anlegen/Löschen von Vertrieblern oder Stores.** Rollover rollt nur bestehende Vertriebler; Onboarding ist `pos-salesperson`, Partner-Anlage ist `pos-store`.
- **Kein Ordner-Anlegen über den Vertriebler-Ordner hinaus.** `ensure_folder_path` löst den bestehenden `<Nachname>, <Vorname>`-Ordner auf; Rollover legt keine neue Struktur an.
- **Kein Umschreiben des Marker-Formats.** `POS-SHEET:` bleibt jahresblind (Bridge-Vertrag, `registry.md` §4) — Rollover ändert nur den **Wert**.
- **Kein Setzen von `MwSt.`, `Akquise`, Protokoll-Chips.** Formel- bzw. Chip-/Record-Spalten (§5).
