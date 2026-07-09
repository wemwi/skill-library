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

- Jede live geschaltete Stadt braucht hier einen Eintrag (Restock postet ausschließlich gegen diese Tabelle, ohne Fallback-Ableitung). Weitere Städte werden ergänzt, sobald ihr Channel live geht (Aktivierungsschwelle, vgl. `telegram.md` §1).
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

Pfad-Segmente: `{city.name}` / `{postal_code} {store.name}` (Klartext aus `liftr_store`-Metaobjekt, keine Slugifizierung). Die jeweilige Wurzel-Folder-ID wird build-time in die Agent-Config gesetzt (`restock.md` §6 hardcodet sie bewusst nicht); dieses Verzeichnis ist die **Quelle** dafür.

---

## 3. Operations-Chat (interne Topics)

Telegram-Gruppe `-1003918922935` mit Topics, in die Belege eingehen und Status-Zeilen zurücklaufen (`restock.md` §1/§7).

| Topic | `message_thread_id` |
|-------|---------------------|
| General | `1` |
| Übergabeprotokolle (Restock-Eingang) | `2` |
| Bestandsprotokolle (Inventory-Eingang) | `34` |

Hinweis: Dies ist der **interne Operations-Chat**, nicht ein öffentlicher City-Channel (§1). Statusmeldungen bleiben hier; öffentliche Posts gehen in den abgeleiteten City-Channel.

---

## 4. POS-Marker in Lexware (Vertriebler & Ziel-Sheet)

**Dies ist kein Wert-Verzeichnis, sondern eine Konvention.** Die Wahrheit steht auf den Lexware-Kontakten, nicht hier. Ein neuer Vertriebler braucht **keinen** Skill-Bump und keine Zeile in dieser Datei — er wird angelegt, bekommt seine `POS-SHEET`-Notiz, und ist damit für alle POS-Agenten und die `agent-bridge` sichtbar.

| Marker | Sitzt auf | Wert | Wer liest |
|---|---|---|---|
| `POS-PARTNER: <uuid>` | **Store**-Kontakt | Lexware-**Kontakt-UUID** des zuständigen Vertrieblers | `invoice.md` §2 (Wert) · `agent-bridge` (**nur Präsenz**, note-Gate) |
| `POS-SHEET: <id>` | **Vertriebler**-Kontakt | Spreadsheet-ID des **aktuellen** Provisions-Sheets | `store.md` §6 · `invoice.md` §2 (Wert) · `agent-bridge` (**nur Präsenz**, Vertriebler-Enumeration) |

**Format (zwingend, beide Marker):** Präfix inkl. Doppelpunkt, dann genau ein Leerzeichen, dann der Wert. Der Wert ist der getrimmte String nach dem Doppelpunkt.

**Die Brücke koppelt an die Präsenz des Präfixes, nicht an den Wert.**
- `checkPartnerNote()` entscheidet per `note.includes("POS-PARTNER:")`, ob überhaupt eine Session startet. Der Wert dahinter ist ihr egal — deshalb konnte er ohne Bridge-Deploy von Name auf UUID wechseln.
- `fetchVertriebler()` paginiert **alle** Kontakte und nimmt jeden mit `note.includes("POS-SHEET:")` als Vertriebler-Button in den Onboarding-Dialog auf (`id` = Kontakt-UUID, Label = Kontaktname).

⚠️ **Beide Präfixe sind damit ein Vertrag mit der `agent-bridge`.** Wer sie umbenennt oder qualifiziert (`POS-SHEET-2026:` o. ä.), bricht `includes()` still: `fetchVertriebler()` liefert eine leere Liste, der Onboarding-Dialog meldet „keine Vertriebler auflösbar", `pos-store` startet nicht mehr. Marker-Format ändern = Bridge-Deploy, nie einseitig.

**Kein Jahresbezug im Marker.** `POS-SHEET` zeigt immer auf die *aktuelle* Datei; beim Jahres-Rollover wird der Wert umgesetzt (künftig durch einen Rollover-Agent, → `rollover.md`). Weil der Marker damit jahresblind ist, verifiziert `invoice.md` §2 das Jahr **im Sheet selbst** gegen `voucherDate` — ohne diesen Guard liefe ein Januar-Backstop mit Dezember-Belegen still in die falsche Datei.

**Ziel-Sheet — Stammdaten-Anker.** Jedes Provisions-Sheet trägt im Tab `Allgemein` eine Label/Wert-Spalte; die Zeile mit Label `Jahr` (Spalte B) hält das Abrechnungsjahr (Spalte C). Label-basiert lesen, **nie** `C5` hardcoden.

**Store-Match-Nummer.** `roles.customer.number` desselben Store-Kontakts (Lexware-Kundennummer) ist der Match-Key gegen `Stores!B` (`invoice.md` §4). Sheet und Lexware sind auf **einen** Nummernraum vereinheitlicht — die frühere JTL-Nummer aus PDF/Sheet ist **nicht mehr** die Match-Quelle. `POS-PARTNER` und `roles.customer.number` sitzen auf demselben Kontakt: **ein** `get_contact` liefert beide.
