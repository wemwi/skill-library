# Sync — Öffnungszeiten aller Stores (pos-sync)

**Cron-getriebener Batch-Agent, kein Mensch im Loop.** `pos-sync` läuft periodisch (Scheduled Deployment), enumeriert **alle** `liftr_store`-Metaobjekte und gleicht deren `opening_hours` gegen die **native Google-Places**-Öffnungszeiten ab. Kein eingehendes Artefakt, keine Rückfrage, keine interaktive Meldung — die Cron-Natur determiniert den Nachrichtenraum: **genau ein** Batch-Report pro Lauf, nichts dazwischen. Damit fällt `pos-sync` unter die Batch-Klasse von `SKILL.md` Invariante 6.

Die Sync-Mechanik selbst (dual-read-Parsing der bestehenden Formate, Google-Places-Abgleich, Schreib-Idempotenz auf `opening_hours`) trägt der Agent-System-Prompt bzw. die laufende Öffnungszeiten-Migration; diese reference legt das **Status-Format** fest — den Punkt, der bislang nur im Cron-Prompt lebte und aus der Konvention ausbrach.

---

## 1. Ablauf-Prinzip (kompakt)

1. **Alle Stores enumerieren** (`graphql_query`, paginiert über die Standard-Seitengröße hinaus — sonst sind Stores ab dem 51. unsichtbar).
2. Pro Store: Google-Places-Öffnungszeiten holen → mit `liftr_store.opening_hours` vergleichen.
3. **Idempotent schreiben** — nur bei echter Abweichung `update`; Gleichstand = `unverändert` (kein Write). Kein Google-Ergebnis = `übersprungen` (nicht `fehler`).
4. Pro Lauf **genau ein** Batch-Report ins Ops-Topic (§2).

**Zähler-Invariante:** `Stores = aktualisiert + unverändert + übersprungen + fehler`. Die Summe **muss** aufgehen — sie ist der Detektor gegen still fehlgezählte Stores (Invariante 6). Geht sie nicht auf, ist der Lauf verdächtig, nicht der Report.

---

## 2. Status-Report (Batch, Invariante 6)

Genau **ein** Post pro Lauf. `parse_mode = HTML`, dynamische Werte escaped (Handles/Fehler via `<code>`). Report-by-exception: **Erfolge werden nicht einzeln gelistet**, nur Übersprungen/Fehler — **je mit Grund**.

**Ausgang 1 — sauberer Lauf (0 Ausnahmen):**
```
✅ <b>POS-Sync — 8/8 Öffnungszeiten aktualisiert</b>
unverändert 0 · übersprungen 0 · fehler 0
```
Bei reinem No-op-Lauf (nichts hat sich geändert) führt der Kopf trotzdem mit ✅ und nennt die Aufteilung, z. B. „**POS-Sync — 8 Stores geprüft**\naktualisiert 0 · unverändert 8 · übersprungen 0 · fehler 0".

**Ausgang 2 — Lauf mit Ausnahmen (übersprungen/fehler > 0) → Kopf ⚠️:**
```
⚠️ <b>POS-Sync — 6/8 aktualisiert, 2 mit Problem</b>
Öffnungszeiten · Cron

Übersprungen (1):
• <code>kiosk-laves</code> — keine Google-Öffnungszeiten hinterlegt
Fehler (1):
• <code>kiosk-die-ecke</code> — <konkreter Fehler>
```
Kappung bei Masse: erste ~15 Ausnahmen listen, dann „…und {N} weitere" (Telegram-Limit 4096 Zeichen).

**Ausgang 3 — Lauf gar nicht angelaufen (Store-Liste nicht ladbar, Tool-Fehler vor der Schleife) → ❌:**
```
❌ <b>POS-Sync abgebrochen</b>
Store-Liste nicht ladbar — <konkreter Fehler>
```

**Das sind die drei — mehr gibt es nicht.** Kein Mensch wartet, also keine Mid-Flow-Rückfrage, kein interaktiver Skip.

---

## 3. Adressierung

Report ins Operations-Topic (General, solange kein dediziertes Sync-Topic in `registry.md` §3 existiert): `message_thread_id` **weglassen** → General (`message_thread_id: 1` wird als „thread not found" abgelehnt, Invariante 6). Ein **fehlgeschlagener** Report-Post kippt den Lauf nicht — der Sync ist bereits geschrieben (best-effort).

---

## 4. Non-Goals

- **Kein City-Channel-Post.** `pos-sync` meldet ausschließlich intern; die öffentliche 🕒-Öffnungszeiten-Broadcast-Variante (falls je gewünscht) ist ein separater, bewusst manueller/anderer Flow. Least-Privilege: kein `send_photo`/Broadcast-Recht.
- **Keine Store-Anlage, keine `opening_hours`-Erfindung.** Kein Google-Ergebnis → `übersprungen`, nie ein geratener Wert.
- **Keine Einzel-Erfolgsmeldung.** Report-by-exception ist Pflicht — 40 Erfolge einzeln zu posten ist genau der Anti-Zustand, den die Konvention behebt.
