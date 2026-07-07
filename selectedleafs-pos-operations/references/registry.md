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
| Invoice (Provisionsabrechnung) | `1u2e9sd5sXL7wuesl0VeyIiHkKL3UpFvf` |

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

## 4. Sheets (Provisions-/Abrechnungs-Domäne)

Der Drive-Ordner **Provisionsabrechnung** liegt in §2 (Invoice-Wurzel). Pro Vertriebler steht hier **nur** sein Unterordner + Datei-Präfix — **keine** Spreadsheet-IDs. Grund: Rollover ist Copy-based (jedes Jahr eine neue Datei `{Präfix} {Jahr}`), eine zentrale ID-Liste würde bei jedem Jahreswechsel von Hand nachgepflegt werden müssen. `invoice.md` §2 löst die aktuelle Spreadsheet-ID stattdessen **pro Lauf** über `list_files` + exakten Namens-Match auf — das hier ist die einzige Registry-Pflicht.

| Vertriebler | Ordner-`parentFolderId` | Datei-Präfix |
|---|---|---|
| Christian Schlegel | `1OwQH8AMQYKZtM8KYrLlBjVXF_Y8A1Xbo` | `Provision Schlegel` |

Neuer Vertriebler = neue Zeile hier + Skill-Version-Bump — **kein** Agent-Config-Rebuild (`invoice.md` liest ausschließlich aus dieser Tabelle, kein Vertriebler-Name im Prompt/Config hardcodiert).

**note-Marker-Konvention (Single Source für den Namen).** Derselbe Vertrieblername in Spalte 1 ist zugleich der Wert im `note`-Marker des Lexware-Store-Kontakts: `POS-PARTNER: <Vertriebler>` (gesetzt im Launch, gelesen in `invoice.md` §2). Der Name muss **zeichengenau** zwischen note-Marker und dieser Zeile übereinstimmen — er ist der Lookup-Schlüssel, ein Tippfehler führt zur §9-Rückfrage. ℹ️ Der Vertriebler-Name sitzt auf dem Kontakt-`note`; die **Store-Match-Nummer** ist `roles.customer.number` desselben Kontakts (Lexware-Kundennummer). Sheet (`Stores!B`) und Lexware wurden auf **einen** Nummernraum (Lexware) vereinheitlicht — die frühere JTL-Nummer aus PDF/Sheet ist **nicht mehr** die Match-Quelle (`invoice.md` §4). Beide Werte — Vertriebler und Match-Nummer — kommen aus **einem** `get_contact`.

**`POS-SHEET`-Marker (Ziel-Sheet des Vertrieblers).** Auf dem **Vertriebler**-Kontakt in Lexware trägt eine zweite Notiz die aktuelle Spreadsheet-Datei-ID:

```
POS-SHEET: <spreadsheet-datei-id>
```

`launch.md` §6 liest daraus direkt die Ziel-Datei-ID für den Provisions-Insert (`Stores`-Zeile) — **kein** `list_files`+Namensmatch. Lexware ist damit die eine Wahrheitsquelle für **beide** Launch-Lookups: Vertrieblername (→ `POS-PARTNER` am Store) und Sheet-Datei-ID (→ `POS-SHEET` am Vertriebler). Der Marker ist ein manueller Pflicht-Eintrag am Vertriebler-Kontakt (für Christian Schlegel bereits gesetzt); bei Jahres-Rollover wird der Wert auf die neue Datei umgesetzt. Die Ordner-/Präfix-Spalten oben bleiben für `invoice.md` §2 (dessen `list_files`-Weg) gültig, bis `pos-invoice` ebenfalls auf den `POS-SHEET`-Weg umzieht.
