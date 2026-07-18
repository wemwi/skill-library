# Registry — Werte-Verzeichnis (Entität → Ziel)

Dieses Verzeichnis hält **statische Werte** (IDs, Maps, Pfade) aus dem Always-on-Body heraus, damit der Skill bei wachsender Städte-/Store-Zahl nicht in der Breite explodiert. Die City→Channel-Map (§1) ist hier vollständiger Wert **und** alleinige Logik (direkter Lookup) — anders als z. B. der Drive-Pfad, dessen Konstruktionsregel in `restock.md` §6 lebt.

**Abgrenzung — was NICHT hier steht:**
- **Lauf-spezifische IDs** (`file_id` des eingehenden PDFs, per-Lauf `chat_id`/`message_id`) kommen aus der **Webhook-Injektion** in die Session, nie aus diesem Verzeichnis.
- **Build-time-Secrets** (Bot-Token, OAuth-Refresh-Tokens, R2-/Upload-Hosts) liegen im Agent-Vault/der Agent-Config (`global-agent-framework`), nicht hier.

---

## 1. City → Channel

**Direkter Lookup, kein Ableitungsmechanismus, kein Override.** Jede Stadt hat genau einen Eintrag — Test- und Prod-Agenten sind getrennte Deployments mit eigenem System-Prompt/Config (`global-agent-framework`), daher kein Per-Run-Schalter und keine Vorrangregel nötig. Konkrete Einträge:

| Stadt | Channel-Username | Numerische `chat_id` | Status |
|-------|------------------|----------------------|--------|
| Hannover | `kratom_hannover` | `-1003904362997` | live (Pilot) |

- Jede live geschaltete Stadt braucht hier einen Eintrag (Restock postet ausschließlich gegen diese Tabelle, ohne Fallback-Ableitung). Weitere Städte werden ergänzt, sobald ihr Channel live geht (Aktivierungsschwelle, vgl. `city.md` §1).
- Test-Channel (nicht öffentlich, für Posting-Dry-Runs): `Broadcast Test` = `-1004399731658`.

---

## 2. Drive — Ablage-Wurzeln

Top-Root `selectedleafs.com` = `1QAgUUIafV8HQiIP7j-nxNALbco2UAA6N` (Parent der Domänen-Ordner unten).

Pfad-Template je Ablage-Domäne (Logik in `restock.md` §6): `<Domänen-Wurzel>/{city.name}/{postal_code} {store.name}/`. Die **City-Unterordner legt `ensure_folder_path` per Name an / löst sie auf** — sie werden hier bewusst **nicht** hinterlegt (sonst Breiten-Engpass bei Städte-Skalierung).

| Ablage-Domäne | Wurzel `parentFolderId` |
|---------------|-------------------------|
| Restock (Übergabeprotokolle) | `1PL9_bKYMCLN6EH8qy1L_WsaE3p_7vC0g` |
| Inventory (Bestandsprotokolle) | `1YbYciT2C2NuqsZrX6ghZnOxxHag9hXwW` |
| Invoice (Provisionsabrechnung) | `1u2e9sd5sXL7wuesl0VeyIiHkKL3UpFvf` — nur Ablageort der Vertriebler-Sheets; **kein Agent liest diesen Ordner.** `pos-invoice` löst seine Ziel-Datei über den `POS-SHEET`-Marker auf (§4) und hat kein Drive-Tool. |

**Provisions-Sheet-Vorlage (leere Datei, kein Ordner):** `1coPnoXdNgjuaNvyS6UriH5vjk8NZMMEPce1bxJzlAyY` — Quelle, aus der `pos-salesperson` (neuer Vertriebler) und `pos-rollover` (Jahreswechsel) je eine Kopie erzeugen. Als stabile Einzeldatei bewusst per ID hinterlegt (kein Namens-Lookup, der beim Umbenennen bricht).

**Ablage-Konvention Vertriebler-Sheets (`pos-salesperson` §4):** Pro Vertriebler ein eigener Ordner `<Nachname>, <Vorname>` (z. B. `Schlegel, Christian`) direkt unter der Invoice-Wurzel, per `ensure_folder_path` idempotent angelegt/aufgelöst. Darin die Kopie mit Dateiname `Provision · <Nachname> · <Jahr>` (z. B. `Provision · Schlegel · 2026`; Trenner ` · `). Der Ordner wird optional als `reader` an die E-Mail des Vertrieblers freigegeben (Vererbung deckt das Sheet). Der deterministische Dateiname **im Vertriebler-Ordner** ist der Heal-Key des find (`list_files` im Ordner, kein Re-Copy bei Re-Run) — nicht mehr die flache Wurzel.

Pfad-Segmente: `{city.name}` / `{postal_code} {store.name}` (Klartext aus `liftr_store`-Metaobjekt, keine Slugifizierung). Die jeweilige Wurzel-Folder-ID wird build-time in die Agent-Config gesetzt (`restock.md` §6 hardcodet sie bewusst nicht); dieses Verzeichnis ist die **Quelle** dafür.

---

## 3. Operations-Chat (interne Topics)

Telegram-Gruppe `-1003918922935` mit Topics, in die Belege eingehen und Status-Zeilen zurücklaufen (`restock.md` §1/§7).

| Topic | `message_thread_id` |
|-------|---------------------|
| General | `1` |
| Übergabeprotokolle (Restock-Eingang) | `2` |
| Bestandsprotokolle (Inventory-Eingang) | `34` |
| Vertriebler anlegen (Salesperson-Onboarding) | `92` |

Hinweis: Dies ist der **interne Operations-Chat**, nicht ein öffentlicher City-Channel (§1). Statusmeldungen bleiben hier; öffentliche Posts gehen in den abgeleiteten City-Channel.

---

## 4. POS-Marker in Lexware (Vertriebler & Ziel-Sheet)

**Dies ist kein Wert-Verzeichnis, sondern eine Konvention.** Die Wahrheit steht auf den Lexware-Kontakten, nicht hier. Ein neuer Vertriebler braucht **keinen** Skill-Bump und keine Zeile in dieser Datei — er wird angelegt, bekommt seine `POS-SHEET`-Notiz, und ist damit für alle POS-Agenten und die `agent-bridge` sichtbar.

| Marker | Sitzt auf | Wert | Wer liest |
|---|---|---|---|
| `POS-PARTNER: <uuid>` | **Store**-Kontakt | Lexware-**Kontakt-UUID** des zuständigen Vertrieblers | `invoice.md` §2 (Wert) · `agent-bridge` (**nur Präsenz**, note-Gate) |
| `POS-SHEET: <id>` | **Vertriebler**-Kontakt | Spreadsheet-ID des **aktuellen** Provisions-Sheets | `store.md` §6 · `invoice.md` §2 (Wert) · `agent-bridge` (**nur Präsenz**, Vertriebler-Enumeration) |
| `POS-TG: <tg_id>` | **Vertriebler**-Kontakt | Numerische Telegram-User-ID des Vertrieblers (Absender-Erkennung) | `agent-bridge` (Wert, Skip des Vertriebler-Schritts) · geschrieben von `store.md` §8.6 |

**Format (zwingend, alle Marker):** Präfix inkl. Doppelpunkt, dann genau ein Leerzeichen, dann der Wert. Der Wert ist der getrimmte String nach dem Doppelpunkt **derselben Zeile**.

> **⚠️ Marker-Invariante — eine Zeile je Marker, zeilen-gebunden lesen UND schreiben.** Die `note` ist **ein** menschlich sichtbares Freitextfeld und trägt seit `POS-TG` **mehrere** Marker gleichzeitig (auf dem Vertriebler-Kontakt: `POS-SHEET` **und** `POS-TG`). Ab diesem Moment gilt für **jeden** Marker-Zugriff, egal welcher Agent:
> - **Lesen** extrahiert den Wert der **eigenen Marker-Zeile** — den getrimmten Rest **dieser** Zeile, **nicht** „alles nach dem ersten Doppelpunkt" (das verschluckte die nächste Marker-Zeile in den Wert). Zeilen-gebundene Regex (`^POS-SHEET:\s*(.+)$` je Zeile), **kein** Dotall.
> - **Schreiben** ändert **nur die eigene Zeile** und lässt jede andere Marker-Zeile (und etwaigen menschlichen Freitext) **unangetastet** — read-modify-write, zeilen-gebundene Ersetzung; existiert die eigene Zeile noch nicht, **anhängen**. **Nie** die ganze `note` neu setzen.
>
> **Warum das tragend ist:** `POS-SHEET` ist geld­relevant (Ziel der Provisionszeile, `invoice.md` §4). Ein naives „alles nach dem Doppelpunkt" oder ein Voll-Neusatz der `note` liefe **still** in die falsche Sheet-ID bzw. löschte `POS-TG` — kein Tool-Fehler, keine Abbruchzeile. Gleiche Klasse wie die `PLACE_CHIP`-Invariante (`SKILL.md` §Invarianten 4): still, geld­relevant. `salesperson.md` §5, `rollover.md` §6 und `store.md` §6/§8.6 erfüllen diese Invariante bereits — sie ist hier zentral festgehalten, damit ein künftiger vierter note-Schreiber nicht unbemerkt davon abweicht.

**Die Brücke koppelt an die Präsenz des Präfixes, nicht an den Wert.**
- `checkPartnerNote()` entscheidet per `note.includes("POS-PARTNER:")`, ob überhaupt eine Session startet. Der Wert dahinter ist ihr egal — deshalb konnte er ohne Bridge-Deploy von Name auf UUID wechseln.
- `fetchVertriebler()` paginiert **alle** Kontakte und nimmt jeden mit `note.includes("POS-SHEET:")` als Vertriebler-Button in den Onboarding-Dialog auf (`id` = Kontakt-UUID, Label = Kontaktname).

⚠️ **Alle drei Präfixe sind damit ein Vertrag mit der `agent-bridge`.** Wer `POS-PARTNER`/`POS-SHEET` umbenennt oder qualifiziert (`POS-SHEET-2026:` o. ä.), bricht `includes()` still: `fetchVertriebler()` liefert eine leere Liste, der Onboarding-Dialog meldet „keine Vertriebler auflösbar", `pos-store` startet nicht mehr. `POS-TG` liest die Bridge im **Wert** (nicht nur Präsenz): matcht der getrimmte Zeilen-Wert die `from.id` des `/new store`-Aufrufers, entfällt der Vertriebler-Picker (Skip). Ein Format-/Präfix-Wechsel an `POS-TG` bricht den Skip still (Picker erscheint wieder — kein Datenverlust, aber die Bequemlichkeit ist weg). Marker-Format ändern = Bridge-Deploy, nie einseitig.

**Vertriebler-Kontakt = Lieferant.** `pos-salesperson` legt den Vertriebler mit Rolle `vendor` an (Kreditor — er bekommt Provision ausgezahlt). Der **Store** ist der Kunde (`roles.customer.number`, oben). Kein Agent liest die *Rolle* des Vertrieblers (er wird nur über `POS-SHEET` + Name gefunden) — `vendor` hält allein den Kundennummernraum sauber.

**`POS-TG` — Absender-Bind (Lifecycle).** Der Marker entsteht **nicht** beim Anlegen des Vertrieblers (dessen Telegram-ID ist da noch unbekannt), sondern **lazy** beim **ersten eigenen** `/new store` des Vertrieblers: die Bridge zeigt den Vertriebler-Picker, der Vertriebler tippt sich selbst → weil **er** der Absender ist, trägt der `pos-store`-Agent seine `from.id` als `POS-TG` an den Kontakt nach (`store.md` §1 `binder_tg_id`, §8.6). Ab dann matcht die Bridge künftige Aufrufe und überspringt den Picker. Drei Guards:
- **Admin-Ausschluss:** ein Aufrufer aus `TELEGRAM_ADMIN_IDS` (Bridge-Var, z. B. Joscha) wird **nie** gebunden — sein `binder_tg_id` wird nicht injiziert, sein `/new store` zeigt immer den Picker (er legt Stores *für* andere an). Da ein Admin nie `POS-TG` trägt, matcht er auch beim Lesen nie — der Ausschluss ist damit doppelt (Schreib-Guard + automatisch beim Lesen).
- **append-only, kein Clobber:** `POS-TG` wird nur angehängt, wenn der Kontakt **noch keine** `POS-TG`-Zeile trägt (die erste Bindung gewinnt und bleibt stabil). `POS-SHEET` bleibt dabei unangetastet (Marker-Invariante oben).
- **Reihenfolge:** `POS-TG` kann erst existieren, **nachdem** `POS-SHEET` existiert (`pos-store` liest `POS-SHEET` in §6, bevor es bindet). Deshalb kann kein note-Schreiber `POS-TG` versehentlich zerstören: `salesperson.md` schreibt die `note` nur, solange `POS-SHEET` fehlt (dann fehlt `POS-TG` zwangsläufig auch), `rollover.md` §6 fasst ausschließlich die `POS-SHEET`-Zeile an.

Der Marker ist **keine** Wahrheitsquelle für Geschäftsdaten — er ist reine Routing-Bequemlichkeit (Picker-Skip). Fehlt er, ist nichts kaputt: der Vertriebler sieht den Picker einmal mehr. Ein Falsch-Bind (Vertriebler tippt versehentlich einen fremden Vertriebler) ist in der Confirm-Zusammenfassung sichtbar und per Löschen der `POS-TG`-Zeile behebbar.

**Kein Jahresbezug im Marker.** `POS-SHEET` zeigt immer auf die *aktuelle* Datei; beim Jahres-Rollover wird der Wert umgesetzt (künftig durch einen Rollover-Agent, → `rollover.md`). Weil der Marker damit jahresblind ist, verifiziert `invoice.md` §2 das Jahr **im Sheet selbst** gegen `voucherDate` — ohne diesen Guard liefe ein Januar-Backstop mit Dezember-Belegen still in die falsche Datei.

**Ziel-Sheet — Stammdaten-Anker.** Jedes Provisions-Sheet trägt im Tab `Allgemein` eine Label/Wert-Spalte; die Zeile mit Label `Jahr` (Spalte B) hält das Abrechnungsjahr (Spalte C). Label-basiert lesen, **nie** `C5` hardcoden.

**Store-Match-Nummer.** `roles.customer.number` desselben Store-Kontakts (Lexware-Kundennummer) ist der Match-Key gegen `Stores!B` (`invoice.md` §4). Sheet und Lexware sind auf **einen** Nummernraum vereinheitlicht — die frühere JTL-Nummer aus PDF/Sheet ist **nicht mehr** die Match-Quelle. `POS-PARTNER` und `roles.customer.number` sitzen auf demselben Kontakt: **ein** `get_contact` liefert beide.
