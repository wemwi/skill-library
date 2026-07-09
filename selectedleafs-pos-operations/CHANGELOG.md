# Changelog — selectedleafs-pos-operations

Alle nennenswerten Änderungen an diesem Skill. Format angelehnt an [Keep a Changelog](https://keepachangelog.com/), Versionierung folgt SemVer (`global-git-conventions`).

## [3.1.0] — `store.md` §3: Places-Zug konkretisiert

Der `pos-store`-Agent brach an §3 fail-closed ab („Place Details nicht abrufbar"): §3 beschrieb die Places-API semantisch (Endpoint-Felder, FieldMask), aber nicht den **Aufruf** — der Agent kannte weder Transportweg noch Credential-Namen. Kein Bug im Flow (das fail-closed war korrekt), sondern eine Lücke im Skill.

**Neu in §3:**
- **Konkreter Aufruf** als `curl`-`GET` gegen `https://places.googleapis.com/v1/places/{place_id}` — direkter Sandbox-Call, **kein** MCP-Tool (Places ist eine öffentliche, key-authentifizierte API; ein `google-places-mcp` wäre Overhead ohne Sicherheitsgewinn — bewusst verworfen).
- **Credential-Kontrakt:** Key als `${GOOGLE_PLACES_API_KEY}` aus dem Vault (Typ Umgebungsvariable), Zugangsdaten host-gebunden an `places.googleapis.com` + Injektionsort Request-Header. Variablenname = Konfiguration (darf im Skill stehen), Wert = Secret (nie in Skill/Prompt/Message/Status).
- **Zwei Google-Fallen dokumentiert:** FieldMask ist Pflicht (keine Default-Feldliste) und darf **keine Leerzeichen** enthalten.
- **Egress-Regel:** Host-Freigabe hängt an den Zugangsdaten; fehlt sie → Netzwerkfehler → fail-closed, **kein** Ausweichen auf andere Wege (`global-agent-framework` §13).

Minor, nicht Major: kein Vertrag bricht — §4/§5 lesen dieselben Felder aus derselben Antwort. Nur der Weg dorthin ist jetzt ausgeschrieben.

## [3.0.0] — `launch.md` → `store.md` (BREAKING)

**BREAKING CHANGE.** Domäne `launch` vollständig zu `store` umbenannt (keine Altlast `launch.md`) und der öffentliche 🎉-Broadcast als Agent-Schritt eingezogen. Major, weil zwei tragende Verträge brechen:

1. **Datei-/Dispatch-Rename:** `references/launch.md` → `references/store.md`; Agent `pos-launch` → `pos-store`. Die Agent-Allowlist (welche reference der Agent laden darf) referenziert den alten Pfad — sie muss beim Cutover mitgezogen werden (Console-Agent-Rename + agent-bridge-Routing sind **nachgelagerte** Schritte, nicht Teil dieser Skill-Phase).
2. **Invarianten-Umkehr:** Die bisherige `store`-Invariante „**kein** öffentlicher City-Post" (v2.x Non-Goal §10) ist aufgehoben. Der `pos-store`-Agent postet jetzt genau **einen** öffentlichen Post — den 🎉-„Neuer Partner"-Broadcast (§8.5) — und braucht dafür `send_photo`-Recht auf City-Channels (Least-Privilege-Fläche wächst).

**Neu — `store.md` §8.5 (🎉-Broadcast, selbsttragend):**
- Template **und** Posting-Handwerk inline (kein Sprung in `telegram.md`), Muster wie Restocks 📦/🌿 in `restock.md`.
- **CREATE-Gating als einzige Doppel-Post-Sperre** — feuert nur, wenn §8.1 den Store neu anlegt; ein Re-Run trifft zwangsläufig den Heal-Zweig und postet nie erneut. **Kein Marker, kein Metafield.** Ein bei Abbruch nach §8.1/vor §8.5 verlorener 🎉 ist bewusst akzeptiert (fehlt, nicht doppelt; über die §9-Statuszeile sichtbar → manueller Nachpost, kein Auto-Retry).
- **Best-effort:** §8.5 läuft nach dem §8.4-Read-back; ein Skip/Fehler rollt nichts zurück und macht den Lauf nicht fail-closed — er annotiert nur die Erfolgs-Statuszeile.
- **Bild = `image.url` des §7-`MediaImage` (Shopify-CDN) via `send_photo(photo=url)`** — **nicht** die eingehende Telegram-`file_id` (chat-übergreifend nicht stabil; URL-Weg im `telegram-operations-mcp` live, `send_photo` seit Phase 1).
- **Channel-Lookup:** numerische `chat_id` aus `registry.md` §1 (City-Name aus §5.1). **Kein Eintrag** → Broadcast-SKIP mit Status-Zeile, **kein** fail-closed (Store bleibt erfolgreich).
- §9-Status um drei §8.5-Ausgänge erweitert (gepostet / übersprungen / fehlgeschlagen); §10-Non-Goal von „kein öffentlicher Post" auf „nur 🎉-Milestone, kein edit/pin/delete" umgeschrieben. „Keine City-Anlage" bleibt.

**Dispatch/Registry-Folgeänderungen:**
- `SKILL.md`: Dispatch-Zeile `launch` → `store` (inkl. §8.5-Broadcast + `registry.md` §1-Load); telegram.md-Domäne von „Channel-Setup-/🎉-Post" auf „Channel-Setup-/Lifecycle" umbenannt (der 🎉-Post lebt jetzt in `store.md`); Description + `pos-store`-Trigger.
- `telegram.md`: §5-🎉-Template + Handwerk entfernt, verweist nur noch auf `store.md` §8.5; „Launch-Domäne" → „Store-Domäne"; **§8 Channel-Launch-Strategie inhaltlich unangetastet** (nur der tote `launch.md`-Datei-Zeiger darin auf `store.md` korrigiert).
- `registry.md` §4: toter `launch.md` §6-Zeiger → `store.md` §6.
- `restock.md`: geprüft, unverändert (das dortige „Pinned/Launch" meint `telegram.md` §8, keinen `launch.md`-Zeiger).

**Neu — vier geplante Stub-References** (Status-Header + „fail-closed bei Load", im Dispatch registriert): `city.md`, `salesperson.md`, `rollover.md`, `sync.md`.

## [1.4.0] — `invoice.md`

- `invoice.md` aus dem Stub migriert: Rechnung-Insert + paid-Update in die Vertriebler-Provisionsliste (Google Sheet), Findung per Registry-Map (`registry.md` §4, neu gefüllt).
- Vorab-Stresstest (`global-stress-test`) deckte zwei tragende Annahmen aus dem Ausgangs-Handover auf, die an der realen Sheet-Struktur brachen:
  1. **Insert-Position:** Die Umsatz-Table hat ihre Footer-/Summenzeile als **Teil der nativen Table** direkt nach der letzten Datenzeile — kein freier Zwischenraum, wie ein früherer Plan annahm. `append_row` hätte unterhalb des Footers und außerhalb der Table geschrieben; neue Zeilen wären aus allen `SUM()`/`SUMIFS()` gefallen, ohne sichtbaren Fehler. Fix: `insert_dimension inheritFromBefore` **vor** der Footer-Zeile, deren Index pro Run dynamisch aus `list_tables` gelesen wird (nie hardcoden).
  2. **Datei-Findung:** Ein Vertriebler-Ordner kann mehrere Jahres-Dateien enthalten (z. B. `Provision Schlegel 2025` **und** `2026` gleichzeitig real vorgefunden). Ein Präfix-`contains`-Match ist damit mehrdeutig. Fix: exakter Name-Match `"{Präfix} {Rechnungsjahr}"`, bei ≠ 1 Treffer Abbruch + Rückfrage statt Fallback auf „neueste Datei".
- `paid`-Status-Mapping (`paid`/`paidoff` → „Bezahlt", `open`/`overdue` → „Offen") verifiziert per `get_voucher` an je einem realen offenen und bezahlten Beleg, nicht aus dem Handover übernommen.
- Bewusste Entscheidung: Store-Status (`Aktiv`/`Inaktiv`) ist **kein** Guard — einziges Match-Kriterium ist die Kunden-Nr. in `Stores`. Lexware ist Ground Truth für ein bestehendes Geschäftsverhältnis, ein veralteter Sheet-Status widerspricht dem nicht.
- Storno-/Korrektur-Belege (abweichendes Rechnung-Nr.-Suffix) bewusst **ohne** Sonderbehandlung — laufen naiv als eigene Zeile (Non-Goal, explizit dokumentiert).
- `registry.md` §4 gefüllt: Vertriebler → Drive-Ordner + Datei-Präfix (bewusst **keine** Spreadsheet-IDs — Rollover ist Copy-based, eine zentrale ID-Liste würde bei jedem Jahreswechsel veralten).

## [1.3.0]

**Geändert**
- `telegram.md` §2.1 (Channel-Ableitung `kratom_<stadt>` + Override-Vorrang) ersatzlos entfernt. City→Channel ist jetzt ein direkter Lookup in `registry.md` §1, ohne Ableitungslogik und ohne Override-Mechanismus — Test- und Prod-Agenten sind getrennte Deployments mit eigenem System-Prompt/Config (`global-agent-framework`), ein Per-Run-Schalter war nie nötig.
- Auslöser: Token-Audit zweier produktiver Agent-Sessions zeigte, dass `pos-restock` bei jedem Lauf die komplette `telegram.md` (16 kB) lud, obwohl die Restock-Kette ihre Post-Templates lokal in `restock.md` trägt — einzig die Channel-Ableitung in §2.1 erzwang den Load. Nebenbefund beim Review: Ein Channel-Override (`registry.md`-Eintrag mit Vorrang vor der Default-Ableitung) griff in einer Live-Session nicht — der Bug ist mit der Vereinfachung obsolet, da es keinen Vorrang-Mechanismus mehr gibt, der greifen könnte.
- `restock.md` (vier Stellen) und `telegram.md` (Einleitung) entsprechend auf den `registry.md`-Lookup umgebogen.
- SKILL.md-Dispatch: `telegram.md` ist nicht mehr Pflicht-Load für die Restock-Domäne, nur noch für die Launch-Domäne.
- Geschätzte Einsparung: ~90–100k `cache_read`-Tokens pro Restock-Lauf (~15 % der Session).

**Entfernt**
- `## Herkunft`-Sektion aus SKILL.md (war Always-on-Kost bei jedem Agent-Lauf, rein historisch ohne Laufzeit-Wert) — Inhalt 1:1 hierher migriert, siehe Einträge unten.

## [1.2.1] — `inventory.md`

- `inventory.md` **selbsttragend** gemacht: die anfangs auf `restock.md` §1.1/§2.5/§6 zeigenden Quer-Verweise durch inline-Mechanik ersetzt (Router-Invariante „jede reference fährt allein“ — `restock.md` blieb unangetastet).
- Reduzierter Umfang gegenüber Restock: kein Sorten-/Vein-Parsing, kein Neu-vs-aufgefüllt, kein `product_list`-Write-back, kein City-Channel-Post.
- Zwei bewusste Abweichungen aus dem Vorab-Stresstest:
  1. **Idempotenz-Schlüssel ist `{JJJJ-MM-TT}.pdf` im Store-Ordner**, nicht die Kunden-Nr. auf dem Beleg — letztere ist partner-konstant (nicht protokoll-eindeutig) und liegt zudem nicht im `liftr_store`-Metaobjekt; eine Kunden-Nr.-Kennung hätte jedes Folgeprotokoll desselben Stores fälschlich als Duplikat behandelt. Bei Kollision (zwei Protokolle desselben Stores am selben Tag) **Rückfrage ins Topic statt stillem Überspringen** — anders als Restocks Idempotenz-Skip, weil hier echter Datenverlust drohen würde statt eines harmlosen Doppel-Posts.
  2. **Komprimierung auf 1500 px/q80 statt Restocks 1240 px/q75** — das Bestandsprotokoll ist primär die handschriftliche IST-Bestand-Zählung (Beleginhalt selbst), während bei Restock Mengen für den Post irrelevant sind; die höhere Qualität ist hier Standard, nicht Fallback.

## [1.2.0] — `inventory.md`

- `inventory.md` aus dem Stub migriert (kein Quell-Skill — Neubau, eng an `restock.md`-Mechanik orientiert: Download, Store-Match, Drive-Ablage).

## [1.1.0] — `restock.md`

- §7 um die vollständige `post_message`-Adressierung ergänzt: Status-Zeilen, Rückfragen (§3) und Fehler-Status (§1.1/§6) gehen via `post_message` mit `chat_id` und `message_thread_id` aus `registry.md` §3 — Topic „Übergabeprotokolle“ = `message_thread_id: 2`. Ohne diesen Parameter hätten alle Topic-Posts den General-Thread statt den Restock-Eingang getroffen. Parameter ist seit `telegram-mcp` PR #61 im `post_message`-Tool live.

## [1.0.3] — `restock.md`

Vier Robustheits-Härtungen aus dem ersten grünen End-to-End-Lauf:
- Dedupe per Regex statt Hand-Stripping (§2.4).
- `urllib.parse.quote` auf den Maps-`query`-Wert (Render-Regeln).
- Die **realen** `google_place`-JSON-Keys `id`/`displayName` benannt (§2.5 1b + Render-Regeln) — behebt einen latenten `KeyError`, weil die Prosa zuvor `place_id`/`name` suggerierte, die so im Feld nicht existieren.
- §1-Schrittfolge entwirrt (Idempotenz-Check nach Parse + Store-Match, weiterhin zwingend vor jedem Post).

## [1.0.2] — `restock.md`

Zwei aus `selectedleafs-pos-restock` **vererbte** (nicht durch die Migration entstandene) Alt-Bugs chirurgisch gefixt, erstmals durch einen End-to-End-Lauf sichtbar:
- **§6** — resumable-Upload finalisiert nur mit `Content-Range`-Header; ohne ihn HTTP 308 = nicht committet (vorher fälschlich als Erfolg gewertet).
- **§2.5 1b** — Detail-Query holt jetzt `google_place` (für den `{maps_link}` der Post-Templates; vorher Platzhalter-Link).

`telegram.md` = generisches Handwerk aus `selectedleafs-telegram` (v13), domänenspezifische Templates herausgezogen. Die beiden Quell-Skills (`selectedleafs-pos-restock`, `selectedleafs-telegram`) werden nach Umstellung der Agenten deprecated.

## [1.0.1] — `restock.md`

- Tote Verweise auf den Quell-Skill auf die lokale Template-Sektion bzw. `telegram.md` §2.1 repointet.

## [1.0.0] — Initial

- `restock.md` = Inhalt aus `selectedleafs-pos-restock` v1.8.0, 1:1 migriert (Migration byte-verifiziert) + Restock-Post-Templates eingezogen.
