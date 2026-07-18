# Changelog — selectedleafs-pos-operations

Alle nennenswerten Änderungen an diesem Skill. Format angelehnt an [Keep a Changelog](https://keepachangelog.com/), Versionierung folgt SemVer (`global-git-conventions`).

## [5.8.0](https://github.com/wemwi/skill-library) (2026-07-18)

### Added
- **Invariante 6 — Telegram-Post-Konventionen** (SKILL.md): geteilte Nachrichten-Grammatik für alle Posts (Status intern + Broadcast). Trennscharfe Emoji-Ausgänge (✅ Erfolg · ℹ️ No-op · ⚠️ Eingriff nötig · ❌ technischer Fehlschlag), Lauf-Typ im Titel statt im Emoji, zwei Format-Klassen (Single-Unit vs. Batch mit report-by-exception + Zähler-Invariante + Kappung), `parse_mode HTML` + Escaping-Pflicht dynamischer Werte.
- **`references/sync.md`** — `pos-sync` erstmals im Skill verankert (war zuvor nur im Cron-System-Prompt): Batch-Kette + die drei kanonischen Status-Ausgänge. Dispatch-Eintrag ergänzt.

### Changed
- **`references/city.md`** vom fail-closed-Stub zum **manuellen City-Onboarding-Runbook** (Channel-Setup, Pinned, Launch-Post, Legal-Anker) — konsolidiert aus dem aufgelösten `telegram.md`.
- **§Status-Sektionen entdriftet** auf Invariante 6: `↩︎`→`ℹ️` (restock), `♻️`→Batch-Kopf mit ✅/⚠️ (invoice-Backstop, rollover). Deutsche Anführungszeichen vereinheitlicht (U+201D → U+201C).

### Removed
- **`references/telegram.md` aufgelöst** — Channel-Lifecycle → `city.md`, Nachrichten-Konvention → Invariante 6, Broadcast-Templates lagen bereits bei restock/store. Alle Querverweise umgebogen.

## [5.7.1](https://github.com/wemwi/skill-library) (2026-07-18)

### Changed

* **Namenskonvention:** Bridge-Var `OPERATOR_TG_IDS` → `TELEGRAM_ADMIN_IDS` (folgt dem `TELEGRAM_*_*`-Schema der übrigen Telegram-Vars in Cloudflare). Der Begriff „Operator" wird für dieses Konzept stack-weit durch „Admin" ersetzt (Skill: `registry.md` §4 „Admin-Ausschluss", `store.md` §1/§8.6; Bridge separat: `isOperator`→`isAdmin`). Rein terminologisch, **kein** Verhaltensbruch — der Wert (`412739246`) und die Logik (Admins nie gebunden, sehen immer den Picker) bleiben identisch. Der Eigenname „Operations-Topic/-Chat" (Telegram-Kanal) bleibt unangetastet. Bridge-Umsetzung: `agent-bridge` (separater PR)

## [5.7.0](https://github.com/wemwi/skill-library) (2026-07-18)

### Features

* **store:** neues Kontrakt-Feld `binder_tg_id` (optional) — die `agent-bridge` injiziert die Telegram-User-ID des Aufrufers nur für **Nicht-Operatoren**; fehlt es, wird der Bind übersprungen (kein fail-closed) ([`references/store.md`](references/store.md) §1)
* **store:** §8.6 neu — `POS-TG`-Bind am Vertriebler-Kontakt als **best-effort letzter Schritt** (append-only, Guard: nur wenn noch keine `POS-TG`-Zeile). Bindet die Absender-ID an den Kontakt, damit dessen nächster `/new store` den Vertriebler-Picker überspringt. Ein Fehlschlag kippt die Store-Anlage nicht (self-healing)
* **registry:** `POS-TG: <tg_id>`-Marker + Lifecycle dokumentiert (Lazy-Bind beim ersten eigenen `/new store`, Operator-Ausschluss, append-only, Reihenfolge-Garantie gegen Clobber) ([`references/registry.md`](references/registry.md) §4)

### Invariants

* **Marker-Zeilen-Invariante (neu, universell §Invarianten 5):** Lexware-`note`-Marker sind zeilen-gebunden — Lesen extrahiert den Wert **der eigenen Zeile** (nie „alles nach dem ersten Doppelpunkt"), Schreiben ändert **nur die eigene Zeile** und lässt andere Marker unangetastet (kein Voll-Neusatz der `note`). Tragend, seit die Vertriebler-`note` mit `POS-SHEET` **und** `POS-TG` zwei Marker trägt; ein Verstoß liefe **still** in die falsche (geld­relevante) Sheet-ID oder löschte `POS-TG`. Gleiche Klasse wie die `PLACE_CHIP`-Invariante
* **store §6 / invoice §2.2:** `POS-SHEET`-Read auf zeilen-gebundene Extraktion festgezurrt (Vertriebler-`note` trägt jetzt auch `POS-TG`)
* **invoice §2.1:** `POS-PARTNER`-Read auf dieselbe Invariante verwiesen (Futureproof; Store-Kontakt trägt heute nur einen Marker)
* **rollover §6 / salesperson §5:** erfüllten das zeilen-gebundene Schreiben bereits — jetzt explizit auf die zentrale Invariante (`registry.md` §4) verwiesen, kein Verhaltensbruch

### Notes

* Rebased auf `main` **nach** PR #142 (Öffnungszeiten-/Store-Schema-Migration, released als 5.6.0): dessen `store.md`-Änderungen (`required:true`, `cron-pos-sync`-Ownership, Öffnungszeiten) bleiben vollständig erhalten — diese 5.7.0 setzt **nur** die POS-TG-Ebene obendrauf
* Die tg_id → Lexware-Kontakt-Zuordnung ist ein **irreduzibler einmaliger Bind** — Telegram gibt fremde IDs nicht her (keine Mitgliederliste, kein Tag, keine Aktivitäten-API), ein Bot lernt eine ID nur, wenn die Person selbst sendet. Deshalb Lazy-Bind beim ersten eigenen `/new store` statt „beim Anlegen"
* `POS-TG` bewusst als Line-Marker in `note`, **nicht** als JSON-Blob (JSON bräche bei menschlichem Freitext im selben Feld) und **nicht** als Lexware-Aktivität (die Public API kennt Aktivitäten nicht) — `note` ist das einzige API-schreibbare Freitextfeld am Kontakt
* Operator-Ausschluss über Bridge-Var `OPERATOR_TG_IDS`; der Agent prüft die Liste **nicht** selbst, er führt nur aus, was injiziert wurde (Invariante 2). Bridge-Umsetzung: `agent-bridge` PR #45 (merged, byte-verifiziert)

## [5.6.0](https://github.com/wemwi/skill-library) (2026-07-18)

### Fixed

* **store:** §8.1.1 korrigiert — die Behauptung, `product_list`/`collection_list` seien `required:false`, war **falsch**. Am Live-Schema verifiziert: `product_list`, `collection_list`, `assortment_list`, `service_list` sind `required:true`; nur `rating` und `testimonial_list` sind `required:false`
* **store:** §8.1-Tabelle + §1-Blockquote — die vier Pflicht-Listen dürfen bei leerer Liste **nicht** weggelassen werden (Shopify weist den Create ab), sondern lösen **fail-closed** aus (operator-facing Status). `product_list`/`assortment_list` erzwingt zusätzlich der Bridge-Dialog (≥1); `service_list` fällt nur im seltenen Nullfall in den Guard
* **store:** §8.1 — `phone` ist jetzt `required:false`; fehlt Places `nationalPhoneNumber` → Feld **weglassen** (wie `website`), kein Guard-Fehler mehr beim Create

### Changed

* **store:** die `new`-Notiz spiegelt jetzt den `cron-pos-sync`-Worker — `new:false` wird 45 Tage nach `createdAt` vom externen Sync gesetzt (keine „Einbahnstraße" mehr); der Agent setzt es weiterhin nie zurück

### Documentation

* **store:** neue Notiz vor §8.1.1 — `opening_hours`, `rating`, `rating_count`, `phone`, `website` pflegt nach der Anlage der externe wöchentliche `cron-pos-sync` (Google = SSoT); manuelle Shopify-Korrekturen dieser Felder überschreibt der Sync. Korrekturen gehören ins Google-Business-Profil
* **store:** Clear-Idiom festgehalten — Feld leeren = `value: ""` (Read-back `null`), **nie** `value: null` (`MetaobjectFieldInput.value` ist non-nullable, am Prod-Store verifiziert)

### Notes

* Diese Version bringt zugleich die zuvor nur gemountete Öffnungszeiten-Migration (`opening_hours` als rohes `{regular, current}`-Composite, `currentOpeningHours` in der FieldMask, `opening_hours_holiday`-Entfernung) auf `main` — schließt die Drift zwischen gemountetem `.skill` und Repo

## [5.1.0](https://github.com/wemwi/selectedleafs-pos-operations) (2026-07-10)

### Features

* **store:** Feld-Kontrakt für `liftr_store` festgeschrieben — `pos-store` legt das Metaobjekt jetzt vollständig an ([`references/store.md`](references/store.md))
* **store:** §1 um vier optionale Dialog-Felder erweitert (`assortment_list`, `service_extra`, `parcel_carriers`, `socials`); Skip erzeugt kein fail-closed. `assortment_list` ist **Dialog-Pflicht** (≥ 1 Handle, von der Bridge erzwungen), aber bewusst **keine Kontrakt-Pflicht** — ein fehlendes Feld ist ein Bridge-Fehler und darf nicht den Vertriebler vor dem Laden stranden lassen. Dialog-Reihenfolge als Bridge-Anforderung notiert (Bridge liefert die Felder noch nicht — Kontrakt ist rückwärtskompatibel)
* **store:** §3 FieldMask um `websiteUri`, `paymentOptions`, `parkingOptions`, `allowsDogs`, `delivery`, `accessibilityOptions` erweitert, inkl. SKU-/Kostennotiz (Enterprise + Atmosphere, einmal pro Onboarding)
* **store:** §4.4 neu — `highlights` als drei deterministische Slots (Zahlung / Öffnungszeit-Charakter / Lieferung→Paketshop). Feste Phrasenliste, Carrier-Sortierung `DHL → Hermes → DPD → GLS → UPS`, 2er-Deckel wegen P3-Umbruch in `liftr-card-density`
* **store:** §4.5 neu — `service_list` aus 10 Places-Feldern (`true`-only) plus 4 Dialog-Handles; Ausschlussregel `delivery` ↔ `lieferung-moeglich`
* **store:** §5.3 neu — Handle→GID-Auflösung für `liftr_service`/`liftr_assortment` über je einen paginierten Read; unbekannter Handle → fail-closed, nie Create
* **store:** §8.1 schreibt zusätzlich `highlights`, `service_list`, `assortment_list`, `website`, `new: true` (nur CREATE-Zweig) und die vier Social-Felder

### Documentation

* **store:** §10 um Kontrakt D erweitert — Highlights werden nie generiert, keine Testimonials aus Google-Reviews, keine Social-Suche, kein `priceLevel`, keine Service-/Assortment-Anlage
* **store:** §8.1 benennt vier Felder, die der Agent nie schreibt (`featured`, `testimonial_list`, `opening_hours_holiday`, `image_mood`) und hält fest, dass `new` bis zum Rollover eine Einbahnstraße ist
* **store:** §9 um Status-Zeile für unbekannten Handle ergänzt
* **store:** §5.2 — Shopify-Grant der `agent-bridge` korrigiert: `read_metaobject_definitions`, `read_metaobjects`, `read_products` (weiterhin ausschließlich Lese-Scopes; die Bridge kann `liftr_district` nach wie vor nicht anlegen)

### Notes

* Der Über-Mitternacht-Wrap (`close <= open`) zählt in Slot 2 immer als „Schluss nach 22:00" — ein naiver String-Vergleich nähme ausgerechnet dem Spätkiosk sein Highlight
* `acceptsCashOnly` heißt „nur Bargeld", nicht „Bargeld möglich"; ein `acceptsCash` existiert in Places nicht
* Der Freitext-Slot (`highlight_free`) wurde bewusst verworfen: ein leerer dritter Slot kostet nichts, ein ungeprüfter Satz über einen fremden Laden kostet den Partner
* Die acht bestehenden Stores tragen manuell gepflegte Highlights — der Kontrakt gilt nur für Neuanlagen, es wird nicht migriert
* `image_mood` wird aus der Shopify-Definition entfernt; der Theme-Code (`liftr-store`) liest das Feld noch — eigener Auftrag

## [5.0.0](https://github.com/wemwi/selectedleafs-pos-operations) (2026-07-09)

### ⚠ BREAKING CHANGES

* **registry:** Der `POS-PARTNER`-Marker am Store-Kontakt trägt jetzt die **Lexware-Kontakt-UUID** des Vertrieblers statt seines Namens. Bestandsdaten müssen einmalig migriert werden (`update_contact`, `note`). Bis dahin bricht `invoice.md` §2.1 fail-closed am UUID-Format ab.
* **registry:** `registry.md` §4 ist keine Wert-Tabelle mehr (Ordner-ID + Datei-Präfix entfallen ersatzlos) und dokumentiert nur noch die Marker-Konvention. Ein neuer Vertriebler braucht keinen Skill-Bump.
* **invoice:** `pos-invoice` löst das Ziel-Sheet nicht mehr per Drive-`list_files` + Namensmatch auf. Der `google-drive`-MCP-Server ist aus der Agent-Config zu entfernen.

### Features

* **invoice:** Ziel-Sheet-Auflösung über zwei `get_contact` (Store → `POS-PARTNER` → Vertriebler → `POS-SHEET`). Kein Drive, kein Namensmatch, kein Registry-Lookup.
* **invoice:** Neuer Jahres-Guard (§2.3) — das Abrechnungsjahr aus `Allgemein!B:C` (Label `Jahr`) muss zum `voucherDate`-Jahr passen, sonst fail-closed. Fängt den jahresübergreifenden Januar-Backstop und falsch eingetippte `POS-SHEET`-IDs.
* **store:** §6 Registry-Namensabgleich entfällt; einziger Guard ist die Präsenz des `POS-SHEET`-Markers.

### Bug Fixes

* **invoice:** Behebt die Fehlerklasse „0 Treffer für `<Präfix> <Jahr>`" — das Datei-Präfix in `registry.md` §4 wich zeichenweise vom echten Drive-Dateinamen ab (`Provision Schlegel` vs. `Provision Schlegel, Christian`). Der Namensmatch als Auflösungsmechanismus ist entfallen.

### Documentation

* **registry:** Dokumentiert, dass beide Marker-Präfixe ein Vertrag mit der `agent-bridge` sind (`checkPartnerNote()` prüft `POS-PARTNER:`-Präsenz, `fetchVertriebler()` enumeriert über `POS-SHEET:`-Präsenz). Ein qualifiziertes Präfix wie `POS-SHEET-2026:` würde `includes()` still brechen.

## [4.1.0] — 🎉-Broadcast läuft über den Broadcast-Bot; §8.3-Spalten spezifiziert; Chip-Invariante

### Added

- **Universelle Invariante 4 (SKILL.md): kein Chip-Spaltentyp auf Agent-Spalten.** Eine native Sheets-Table-Spalte mit `columnType: PLACE_CHIP` (oder `FILES_CHIP`, `PEOPLE_CHIP`, …) liefert über die Values-API einen **leeren Wert** — ohne Fehler. `Stores!C` („Name") trug genau diesen Typ: ein Read hätte den Storenamen nie gesehen, still. Der Duplikat-Check auf `Stores!B` war nie betroffen, jede künftige Logik auf `C` wäre es gewesen. Der Typ ist inzwischen aus allen drei Provisions-Sheets entfernt; die Invariante hält ihn draußen.

### Fixed

- **§8.5 postete über den falschen Bot.** `telegram-operations-mcp` und `telegram-broadcast-mcp` sind zwei Bots mit zwei Tokens: der Operations-Bot sitzt in der Operations-Gruppe, der Broadcast-Bot in den City-Channels. Ein `send_photo` über `telegram-operations` an einen City-Channel scheitert mit `400 chat not found` (verifiziert an `-1004399731658` und am Live-Channel Hannover `-1003904362997`). Der 🎉-Broadcast läuft jetzt explizit über `telegram-broadcast`; der unbelegte Satz „Der URL-Weg ist im `telegram-operations-mcp` live bestätigt" ist entfernt. §9 (Status-Post ins Operations-Topic) bleibt unverändert bei `telegram-operations`.
- **§8.5 Öffnungszeiten-Template zerriss im Client.** `{oeffnungszeiten}` war als „lesbar gerendert" unspezifiziert; der Agent verkettete die Tage mit `·`, Telegram brach die Caption-Zeile weich um und der letzte Tagesbereich zerfiel. Neues Template: eigener 🕒-Block, ein Tagesbereich pro Zeile, harte Umbrüche, `durchgehend`/`geschlossen` als Sonderfälle. Der Rest von §8.5 (Shopify-CDN-URL als `photo`, HTML-Caption, `&` → `&amp;`, CTA als Verb-Link) ist im Live-Post bestätigt und unverändert.
- **§8.3 spezifizierte die Provisionszeile unvollständig.** Der Skill verlangte eine Spalte `Status = Aktiv`, die es in der Table „Partner" nicht gibt; die real existierenden Spalten `Akquise`, `Übergabeprotokolle` und `Bestandsprotokolle` kamen gar nicht vor — der Agent hat sie geraten (im Lauf zufällig korrekt, aber ungedeckt). §8.3 führt jetzt die vollständige Spaltentabelle: `Lexware ID` (Zahl), `Name`, `Akquise` (`TT.MM.JJJJ`), `Übergabeprotokolle`/`Bestandsprotokolle` (`{postal_code} {store.name}`, identisch zum Drive-Ordner aus §8.4); Formelspalten bleiben unbeschrieben. `Status = Aktiv` gestrichen.

## [4.0.1] — `store.md` §8.1: Publish-Block raus, `rating`-Skala an die Definition angeglichen

### Fixed

- **§8.1 Publish-Block ersatzlos entfernt.** `store.md` verlangte `capabilities: { publishable: { status: ACTIVE } }` im `metaobjectCreate`. Die `liftr_store`-Definition hat `publishable.enabled = false` (ebenso `renderable`, `onlineStore`; `access.storefront = NONE`) — der `metaobjectCreate` scheiterte am ersten Write. Das Theme liest per Liquid, nicht über die Storefront-API; ein Publish-State ist funktionslos. Shopify-Definition bleibt unangetastet.
- **§8.1 `rating`-Skala korrigiert.** Die Feld-Tabelle schrieb `scale_min: "0"` / `scale_max: "5"`; die Definition erzwingt `1.0` / `5.0`. Shopify validiert den Rating-Wert gegen die Definition — der erste Store *mit* Google-Bewertung wäre am Write gescheitert. Die §8.1.1-Regel (`rating` nur bei `userRatingCount >= 1`) ist unverändert und schließt den Wert `0` ohnehin aus.

### Changed

- **§8.1.1 Build-Time-Verifikation als erledigt dokumentiert.** `rating`, `testimonial_list`, `product_list` und `collection_list` waren in der `liftr_store`-Definition `required: true`. Ein `required: true`-Listenfeld weist die **leere Liste** ab (`OBJECT_FIELD_REQUIRED`). Alle vier sind jetzt `required: false` — sie beschreiben, was ein Store *erwirbt*, nicht was ihn *konstituiert*. `§1` bleibt damit gültig („leere Liste zulässig"). Die Regel „niemals ersatzweise Werte erfinden" bleibt bindend.

## [4.0.0] — `store.md`: `district` wird Bridge-Vertrag; `rating`- und Write-Ordering-Defekte geschlossen

### ⚠️ BREAKING CHANGE — Input-Kontrakt (§1)

`district` ist **neues Pflichtfeld** der Bridge-Injektion. Eine `user.message` ohne `district` läuft fail-closed vor jedem Read. Die `agent-bridge` muss das Feld liefern, bevor dieser Skill-Stand produktiv geht.

### Warum

Der `pos-store`-Agent brach an §5.2 fail-closed ab: die Annahme „Places kennt den Bezirk" trug nicht. Der Weg zu einer eigenen Quelle im Agenten ist an zwei unabhängigen, verifizierten Wänden gescheitert:

- `nominatim.openstreetmap.org` authentifiziert über die **IP** und limitiert pro IP. Die Agent-Sandbox nutzt einen geteilten Datacenter-Egress → HTTP 429 beim **ersten** Request (`sesn_01ANYcDhXVzH3JTjS3GFBoR5`, 3 Versuche). Ein Cloudflare-Worker-Proxy hilft nicht, sein Egress ist ebenso geteilt.
- Keybasierte Anbieter (LocationIQ u.a.) authentifizieren über einen **Query-String-Parameter**. Der Anthropic-Vault injiziert Secrets nur in **Request-Header** oder **Request-Body**; ein GET hat keinen Body. Der Platzhalter läuft unsubstituiert durch → HTTP 401 „Invalid key" (`sesn_017ozNT6pzonYi74FdY3N47b`).

Der Geocoder-Zug gehört damit in die `agent-bridge` (Worker-Secret, kein Egress-Proxy). Sie prüft dort die drei Guards (`country_code == "de"`, Geocoder-`city` ≡ Places-`locality`, Stadtteil vorhanden) und liefert **nur den Namen**. Anlegen kann sie nicht — ihr Shopify-Grant ist `read_products`, read-only.

### Geändert

- **§1:** `district` = Pflichtfeld (Stadtteil-Klartext). Der Agent ergänzt, korrigiert und errät hier nichts.
- **§5.2:** Nur noch Auflösung des injizierten Namens auf eine GID. Normalisierter, city-scoped Match (NFC → casefold → `-`/`–`/Whitespace → ein Leerzeichen → trim). Ohne diese Regel legt ein Bindestrich-Unterschied einen Zwilling an — der Bestand hatte genau diesen Fall (`Linden Nord` vs. `Linden-Nord`). Kein Treffer → GID `null`.
- **§2 + neuer §8.1.0: Der District-Create ist ein WRITE, keine Vorbedingung.** Das `metaobjectCreate` sitzt jetzt unmittelbar vor dem Store-Create, also **nach** §7. Vorher hätte ein Fehler in §6/§7 einen **verwaisten Bezirk** hinterlassen — ein Metaobjekt ohne Store, das kein Re-Run aufräumt und im Store-Finder als leerer Filter auftaucht. In `sesn_01RSatdZDM95ot7ith69werZ` ist das nur durch Zufall ausgeblieben.
- **§4.3: `sublocality`/`sublocality_level_1`/`neighborhood` aus Places werden IGNORIERT.** Places liefert die Komponente für DE **inkonsistent** und in **falscher Granularität**: verifiziert an Franz-Nause-Straße 1-3, 30453 Hannover → `sublocality_level_1: "Linden-Limmer"` = Stadt**bezirk**, während `liftr_district` Stadt**teile** führt. Gegengeprüft an Weckenstraße 20 (`suburb: "Linden-Nord"` vs. `city_district: "Linden-Limmer"`). Abbestellen geht nicht — `addressComponents` ist ein einzelnes FieldMask-Feld, §4.3 braucht `route`/`street_number`/`postal_code`. Die Regel ist eine Lese-, keine Anfrage-Regel.
- **§3: `formattedAddress` in die FieldMask ergänzt.** §4.2 braucht das Feld für das `google_place`-JSON, §3 forderte es nicht an — der Agent zog Places pro Lauf ein **zweites Mal** (verifiziert).
- **§8.1.1: dritter `rating`-Zustand geregelt.** Places serialisiert Protobuf-JSON und lässt Default-Werte weg — `userRatingCount = 0` fehlt schlicht. Beobachtet wurde `rating: 5` ohne Count. Neue Regel: `rating` **nur** schreiben, wenn `rating` **und** `userRatingCount ≥ 1` vorliegen. Verhindert eine 5-Sterne-Wertung mit null Bewertungen im Store-Finder — wohlgeformt, von keinem fail-closed fangbar, still falsch.
- **§9:** Erfolgszeile nennt den Bezirk explizit (einziger Detektor für Grenzlagen-Fehler des Geocoders). Neue Abbruchzeile für §8.1.0.
- **§10 Non-Goals:** keine Bezirks-Ermittlung im Agenten; kein Bezirk aus der PLZ (n:m, keine Funktion — `30167` überspannt Nordstadt und Calenberger Neustadt); kein Bezirk aus Google `addressDescriptor` (außerhalb Indiens pre-GA, `areas` ist ML-geschätztes Containment, Zusatzgebühren).

### Deploy-Voraussetzungen

1. `agent-bridge` liefert `district` in der `user.message` **und** postet bei eigenem Abbruch (Geocoder nicht erreichbar, kein Stadtteil) eine fail-closed-Meldung ins Operations-Topic — sonst endet der Dialog still, weil die Session gar nicht erst startet.
2. `allowed_hosts` des Agent-Environments: `places.googleapis.com`, `shopify-staged-uploads.storage.googleapis.com`. Kein Wildcard, kein Geocoder-Host mehr. Ein `LOCATIONIQ_API_KEY` im Agent-Vault wird **nicht** benötigt.

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
