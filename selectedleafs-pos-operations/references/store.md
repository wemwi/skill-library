# Store — neuen POS-Partner anlegen (pos-store)

Legt einen neuen POS-Partner-Store in **einem headless One-Shot-Lauf** über die vier Fachsysteme an: Shopify (`liftr_store`-Metaobjekt, ggf. `liftr_district`), Lexware (Store-Kontakt + `POS-PARTNER`-Notiz), Google Sheets (Provisionszeile im `Stores`-Tab des Vertriebler-Sheets) und Drive (zwei Ablage-Ordner). Der Agent führt **keinen Dialog** — der komplette Auftrag kommt fertig von der `agent-bridge` als `user.message`. Diese reference ist **selbsttragend** (kein Sprung in `telegram.md`): das gesamte Telegram-Handwerk dieser Domäne — Bild holen, Status/Rückfrage ins Operations-Topic posten **und** der öffentliche 🎉-„Neuer Partner"-Broadcast in den City-Channel (§8.5) — steht hier inline. Für den Broadcast lädt der Agent zusätzlich `registry.md` (§1, City→Channel). Der 🎉-Post ist **der einzige** öffentliche Post dieses Agenten und feuert nur bei echter Neuanlage (§8.5).

---

## 1. Input-Kontrakt (Bridge-Injektion)

Die `agent-bridge` injiziert in die `user.message` (der Agent scannt **kein** Topic selbst):

| Feld | Inhalt | Nutzung |
|---|---|---|
| `place_id` | Google **Place ID** des Stores | Places-Zug (§3), Idempotenz-Wurzel (§2/§8.1) |
| `vertriebler_contact_id` | Lexware-**KontaktID** (UUID) des Vertrieblers | Vertriebler-Auflösung (§6) |
| `product_list` | Array von Produkt-**GIDs** | `liftr_store.product_list` (§8.1) |
| `collection_list` | Array von Collection-**GIDs** (aus den gepickten Produkten abgeleitet) | `liftr_store.collection_list` (§8.1) |
| `image_file_id` | Telegram-**file_id** des hochgeladenen Teaser-Bilds | Bild → Shopify Files (§7) |
| `district` | Bezirksname im Klartext (Stadtteil) | `liftr_district`-Match, ggf. Create (§5.2 / §8.1.0) |
| `chat_id` + `message_thread_id` | Operations-Quell-Topic (wo der Auftrag/das Bild herkam) | Ziel der Status-/Rückfrage-Posts (§9) |

Fehlt ein **Pflichtfeld** (`place_id`, `vertriebler_contact_id`, `image_file_id`, `district`) → fail-closed **vor** jedem Read/Write, Status ins Topic (§9). `product_list`/`collection_list` dürfen leer sein (Store wird ohne Sortiment angelegt), sind aber Pflichtfelder im Schema (§8.1) — leere Liste ist zulässig, fehlendes Feld nicht.

> **`district` ist Bridge-Vertrag, kein Ratefeld.** Die Bridge ermittelt den **Stadtteil** (nicht den Stadtbezirk) per Reverse-Geocoding auf OSM-Daten und prüft dort drei Bedingungen: Land ist `de`, die Geocoder-Stadt stimmt mit der Places-`locality` überein, und ein Stadtteil ist überhaupt vorhanden. Kann sie ihn nicht auflösen — kleinere Städte führen oft keine Stadtteil-Grenzrelation —, fragt sie im Dialog nach. Der Agent bekommt in **jedem** Fall einen Namen oder gar keine Session. Er ergänzt, korrigiert oder errät hier **nichts**.

---

## 2. Ablauf-Prinzip — erst Vorbedingungen, dann Writes; fail-closed; per-Write-Idempotenz

Drei Invarianten, die den ganzen Lauf tragen (Konkretisierung von `SKILL.md` §Invarianten + `global-agent-framework` §13):

1. **Erst alle Vorbedingungen, dann Writes.** Sämtliche Reads/Matches (§3–§7: Places-Zug, Ableitungen, City-Match, District-**Match**, Vertriebler-Auflösung, Bild-Bereitstellung) laufen **vollständig und erfolgreich**, bevor **irgendein** Fachsystem-Write (§8) passiert. Scheitert eine Vorbedingung → fail-closed, kein Write.
2. **fail-closed statt Improvisation.** Schlägt ein Tool-Aufruf fehl oder liefert Unerwartetes, brichst du **sofort** ab, postest einen konkreten Fehler-Status ins Quell-Topic (§9) und suchst **keine** Wege außerhalb deiner Tool-Oberfläche. Kein halber Store.
3. **Idempotenz-Wurzel = `place_id`, Durchsetzung per Write (find-or-create).** Die `place_id` ist die Store-Identität. **Jeder** der vier Writes prüft zuerst, ob sein Artefakt schon existiert, und legt nur an, was fehlt — so **heilt ein Re-Run einen Teil-Write**, statt einen Halbzustand einzufrieren. Die Reihenfolge (§8) bleibt Shopify→Lexware→Sheets→Drive; der find-or-create pro Schritt ist der eigentliche Schutz, nicht ein globaler Vorab-Kurzschluss.

> **Warum find-or-create pro Write, nicht ein globaler `place_id`-Check:** Ein einziger Vorab-Check „existiert der Store in Shopify?" würde bei einem Ausfall **nach** dem Shopify-Write (z. B. Sheets-Fehler) den Re-Run sofort abbrechen lassen — die fehlende Provisionszeile bliebe für immer aus, still. Deshalb re-prüft jeder Write einzeln (§8.1–§8.4).

> **Der District-Create ist ein WRITE, keine Vorbedingung.** §5.2 löst in der Vorbedingungs-Phase nur den **Namen** und die **GID-oder-`null`** auf. Das `metaobjectCreate` für einen fehlenden `liftr_district` passiert erst in §8.1, unmittelbar vor dem Store-Create — also **nach** §7. Anders herum hinterließe ein Fehler in §7 (Bild) einen **verwaisten Bezirk**: ein Metaobjekt ohne Store, das kein Re-Run aufräumt und das im Store-Finder als leerer Filter auftaucht. Ein Write, der einen Zustand hinterlässt, gehört hinter die letzte Abbruchmöglichkeit.

---

## 3. Places Place Details ziehen (Vorbedingung)

**Places API (New) — Place Details** per **direktem HTTPS-`GET` aus der Sandbox** (kein MCP-Tool — Places ist eine öffentliche, key-authentifizierte API; ein eigener MCP-Worker wäre Overhead ohne Sicherheitsgewinn). Der Aufruf trägt `place_id` im Pfad und eine **FieldMask** im Header (nur diese Felder, kein `*` — Kosten/Datensparsamkeit):

```bash
curl -sS -f "https://places.googleapis.com/v1/places/${PLACE_ID}" \
  -H "X-Goog-Api-Key: ${GOOGLE_PLACES_API_KEY}" \
  -H "X-Goog-FieldMask: displayName,addressComponents,formattedAddress,location,regularOpeningHours,rating,userRatingCount,nationalPhoneNumber,timeZone"
```

- **`formattedAddress` gehört in die FieldMask** — §4.2 braucht es für das `google_place`-JSON. Fehlt es, muss der Agent Places ein zweites Mal ziehen (verifiziert in Session `sesn_01ANYcDhXVzH3JTjS3GFBoR5`).
- **FieldMask ohne Leerzeichen** — Google lehnt Leerzeichen in der Feldliste ab.
- **Kein FieldMask = Fehler.** Es gibt keine Default-Feldliste; der Header ist Pflicht.
- **`${GOOGLE_PLACES_API_KEY}` kommt aus dem Vault** (Anmeldedaten-Tresor des Agenten, Typ Umgebungsvariable). Der Wert wird **nie** geloggt, nie in eine Statusmeldung (§9) geschrieben und nie in ein anderes Ziel gesendet: die Zugangsdaten sind auf den Host `places.googleapis.com` und den Injektionsort **Request-Header** beschränkt. Der Variablenname ist Konfiguration und darf im Code stehen — der **Wert** gehört auf keine Skill-/Prompt-/Message-Ebene (`global-agent-framework` §6).
- **Egress:** `places.googleapis.com` ist über die Host-Bindung der Zugangsdaten freigegeben. Fehlt sie, schlägt der `curl` als Netzwerkfehler fehl → fail-closed (§9), **nicht** auf einen anderen Weg ausweichen (`global-agent-framework` §13).

Antwort ist ein `Place`-JSON; die `place_id` steht darin als `id`, der Name als `displayName.text`. Scheitert der Zug (kein Treffer, HTTP ≠ 2xx, leere Antwort) → fail-closed (§9). Aus dem Ergebnis werden §4/§5 gespeist. `timeZone` trägt die Über-Mitternacht-Logik der Öffnungszeiten (§4.1); es wird **nicht** ins Metaobjekt geschrieben.

---

## 4. Ableitungen aus dem Places-Ergebnis (Vorbedingung)

### 4.1 `opening_hours` — Places-`periods` → LIFTR-Format

Zielformat (exakt, verifiziert gegen `liftr-store`): Objekt mit Keys `mon tue wed thu fri sat sun`, Wert je ein Array von `[open, close]`-Paaren, Zeiten als `"HH:MM"`.

```json
{ "mon": [["09:00","00:00"]], "fri": [["10:00","01:00"]], "sun": [["11:00","23:30"]], "wed": [] }
```

Konvertierung aus `regularOpeningHours.periods` (jedes `period` = `open{day,hour,minute}` + `close{day,hour,minute}`, `day` 0=So..6=Sa):

- **Gruppierung nach dem OPEN-Tag.** Jedes Paar landet unter dem Wochentag-Key seines `open.day` (0→`sun`, 1→`mon`, …, 6→`sat`).
- **Über-Mitternacht-Wrap:** Schließt ein Period am **Folgetag** (`close.day ≠ open.day`), bleibt es **unter dem Open-Tag** stehen; `close` ist die tatsächliche Folgetag-Zeit (z. B. `["10:00","01:00"]` = Fr 10:00 → Sa 01:00). Schluss exakt Mitternacht → `"00:00"`.
- **Split-Hours:** Mehrere Periods am selben Open-Tag → mehrere Paare im Array desselben Keys (z. B. Mittagspause).
- **Ruhetag:** Kein Period → leeres Array `[]` für diesen Key (nicht weglassen — alle sieben Keys sind gesetzt).
- **24 h durchgehend** (Places: ein Period ohne `close` bzw. `open` 00:00 ohne Schluss): als `[["00:00","00:00"]]` abbilden.
- Zeitformat: zweistellig, führende Null (`"09:00"`, nicht `"9:00"`).

### 4.2 `google_place`-JSON bauen

Exakte Struktur (verifiziert):

```json
{ "id": "<place_id>", "displayName": "<displayName.text>",
  "formattedAddress": "<formattedAddress>", "location": { "lat": <lat>, "lng": <lng> } }
```

`location.lat`/`lng` aus dem Places-`location`-Objekt. Wird als JSON-String ins `google_place`-Feld geschrieben (§8.1).

### 4.3 `adress` + `postal_code` aus `addressComponents`

- **`adress`** (Schema-Key mit **einem** `d` — beibehalten): **nur Straße + Hausnummer** (z. B. `Gerberstraße 14`), zusammengesetzt aus den `addressComponents` `route` + `street_number`. **Nicht** die `formattedAddress`, **nicht** Stadt/PLZ.
- **`postal_code`**: aus `addressComponents` `postal_code`, als **Ganzzahl** (`number_integer`, z. B. `30169`).

Fehlt eine dieser Komponenten in Places → fail-closed (§9): eine unvollständige Adresse ist kein ratbarer Zustand.

> **`sublocality` / `sublocality_level_1` / `neighborhood` in `addressComponents` werden IGNORIERT** — auch wenn Places sie liefert. Nicht als Bezirk, nicht als Fallback, nicht als Cross-Check gegen §5.2. Zwei belegte Gründe: (a) Places liefert sie für deutsche Adressen **inkonsistent** (bei einer Hannoveraner Adresse vorhanden, bei der nächsten nicht); (b) wenn sie da ist, trägt sie die **falsche Granularität** — verifiziert: Franz-Nause-Straße 1-3, 30453 Hannover → `sublocality_level_1: "Linden-Limmer"`, das ist der **Stadtbezirk**, während `liftr_district` **Stadtteile** führt (Limmer, Linden-Nord, …). Ein Cross-Check gegen §5.2 wäre wertlos, weil der Mismatch der Normalfall ist, nicht das Warnsignal.
>
> Abbestellen lässt sich das Feld nicht: `addressComponents` ist **ein** FieldMask-Feld, kein wählbares Set — ohne es fehlen `route`, `street_number` und `postal_code`. Zusatzkosten entstehen dadurch nicht. Die Regel ist deshalb eine Lese-, keine Anfrage-Regel.

---

## 5. City-Match + District-Match (fail-closed, Vorbedingung — kein Create)

Beide Referenzen sind **Pflichtfelder** des `liftr_store` (`city`, `district` — je `metaobject_reference`). Der **Stadtname** kommt aus der Places-`addressComponent` `locality`. Der **Bezirksname kommt nicht aus Places** (§4.3), sondern **fertig injiziert** aus §1; die Bridge ermittelt ihn per Reverse-Geocoding (§5.2).

### 5.1 City — nur MATCH, nie anlegen

`metaobjects(type: "liftr_city", first: 50, after: $cursor)` paginieren, den Places-Stadtnamen gegen das `name`-Feld matchen (NFC-normalisiert, zeichengenau nach Trim).

- **Treffer** → dessen GID ist die `city`-Referenz.
- **Kein Treffer** → **fail-closed + Rückfrage** (§9). Eine neue Stadt anzulegen ist bewusst **nicht** Aufgabe dieses Agenten (Non-Goal §10) — die erste Stadt braucht Kanal/Onboarding-Entscheidungen, die nicht in einen headless One-Shot gehören.

### 5.2 District — injizierten Namen auf eine GID auflösen

Der Bezirksname kommt **fertig injiziert** aus §1 (`district`). Der Agent ermittelt ihn **nicht** selbst.

> **Warum der Agent hier nicht geocodiert.** Die Bezirks-Ermittlung braucht einen Reverse-Geocoder auf OSM-Daten. Alle brauchbaren Anbieter authentifizieren über einen **Query-String-Parameter**; der Anthropic-Vault kann Secrets nur in **Request-Header** oder **Request-Body** injizieren (ein GET hat keinen Body). Ein Agent kann einen solchen Dienst deshalb strukturell nicht aufrufen — der Platzhalter läuft unsubstituiert durch und der Dienst antwortet `401`. Die keylose Alternative (`nominatim.openstreetmap.org`) authentifiziert über die IP und weist den geteilten Datacenter-Egress der Sandbox beim ersten Request mit `429` ab. Beides verifiziert (`sesn_01ANYcDhXVzH3JTjS3GFBoR5`, `sesn_017ozNT6pzonYi74FdY3N47b`).
>
> Der Geocoder-Aufruf gehört deshalb in die `agent-bridge` (Cloudflare Worker, Worker-Secret, kein Egress-Proxy). Sie führt den Zug aus, prüft die Guards und liefert **nur den Namen**. Sie kann den `liftr_district` **nicht anlegen** — ihr Shopify-Grant ist `read_products`, read-only. Das Anlegen bleibt beim Agenten (§8.1.0).

**Places ist hier keine Quelle** — auch nicht hilfsweise. Die `sublocality`-Komponente aus §3 wird nicht gelesen (§4.3). Es gibt genau eine Quelle: das injizierte Feld.

**Auflösen:** `metaobjects(type: "liftr_district", first: 50, after: $cursor)` paginieren, den injizierten Namen gegen `name` matchen **und** die `city`-Referenz des Kandidaten gegen die in §5.1 gematchte City prüfen (gleicher Bezirksname in zwei Städten darf nicht kollidieren).

**Match-Normalisierung** (auf beiden Seiten des Vergleichs, nur für den Vergleich):

```
NFC → casefold → jede Folge aus '-', '–' und Whitespace → ein Leerzeichen → trim
```

Damit kollabieren `"Linden-Nord"` und `"Linden Nord"` auf denselben Schlüssel. Ohne diese Regel legt ein Bindestrich-Unterschied einen **Zwilling** im Store-Finder an — der Bestand hat genau diesen Fall schon einmal produziert. Falsch-Merges sind bei deutschen Stadtteilnamen praktisch ausgeschlossen.

- **Treffer** (normalisierter Name + City stimmen) → dessen GID ist die `district`-Referenz. **Der bestehende `name` wird nicht überschrieben** — der Bestand ist die Wahrheit, nicht der Zug.
- **Kein Treffer** → `district`-GID ist vorerst `null`. Den injizierten Namen in **Original-Schreibweise** merken; das `metaobjectCreate` passiert **nicht hier**, sondern in §8.1.0, unmittelbar vor dem Store-Create. Die Vorbedingungs-Phase legt **nichts** an (§2).
- **Idempotenz:** Der Match läuft **vor** dem Create — zwei Läufe für denselben neuen Bezirk legen ihn nicht doppelt an. Weil der Create in §8.1.0 sitzt, heilt ein Re-Run auch den Fall, in dem §7 beim ersten Versuch scheiterte: es bleibt kein verwaister Bezirk zurück.

> **Warum der Agent den Bezirk anlegen darf und die City (§5.1) nicht:** Ein neuer Bezirk ist eine reine Taxonomie-Zeile unter einer bereits kuratierten Stadt — er zieht keine Folgeentscheidungen nach sich. Eine neue **Stadt** zieht Kanal-, Onboarding- und Broadcast-Entscheidungen nach sich, die nicht in einen headless One-Shot gehören.

> **Bekannter Restfehler:** Liegt der Store exakt auf einer Stadtteilgrenze, kann der Reverse-Geocoder der Bridge einen **plausiblen, aber falschen** Bezirk geliefert haben — wohlgeformt, also von keiner Prüfung fangbar. Einziger Detektor ist die menschliche Sichtprüfung: der Status-Post (§9) und der 🎉-Broadcast (§8.5) nennen den Bezirk deshalb **explizit**.

---

## 6. Vertriebler auflösen (Vorbedingung) — Lexware ist die Wahrheitsquelle

**Ein** `get_contact(vertriebler_contact_id)` liefert beides:

1. **Vertrieblername** = der Kontaktname (Firma/Person), der **zeichengenau** einem Eintrag in `registry.md` §4 (Spalte „Vertriebler") entspricht. Dieser Name wird der Wert der `POS-PARTNER`-Notiz auf dem **Store**-Kontakt (§8.2) und ist der Lookup-Schlüssel, den `invoice.md` §2 liest.
   - **Name nicht in `registry.md` §4** → **fail-closed + Rückfrage** (§9). Echter Konfigurationsfehler (fehlende registry-Zeile / falscher Kontakt), nie raten.
2. **Ziel-Sheet-Datei-ID** = der getrimmte Wert **nach** dem Notiz-Marker `POS-SHEET:` auf dem Vertriebler-Kontakt (`registry.md` §4 dokumentiert die Konvention). Das ist die Spreadsheet-ID des aktuellen Vertriebler-Sheets für den Stores-Insert (§8.3).
   - **Kein `POS-SHEET`-Marker** → **fail-closed + Rückfrage** (§9): ohne Ziel-Datei kann die Provisionszeile nicht angelegt werden.

> Lexware trägt beide Werte auf **einem** Kontakt — der Name (→ `POS-PARTNER` am Store) und die Sheet-ID (→ `POS-SHEET` am Vertriebler). Kein Verzeichnis-Scan, kein `list_files`-Namensmatch: die Datei-ID kommt direkt aus der Notiz. (Wenn `pos-invoice` später ebenfalls auf diesen Lexware-Weg umzieht, teilen beide Domänen denselben Lookup.)

---

## 7. Teaser-Bild: Telegram-Upload → Shopify Files (Vorbedingung, byte-sicher)

Das Bild (`image_file_id` aus §1) wird nach Shopify Files geladen und dessen GID ist das `image`-Pflichtfeld (§8.1). **Bytes laufen nie durch den Agenten-Kontext** (`global-agent-framework` §12) — Download und Upload gehen direkt aus der Sandbox.

**Namenskonvention:**
- **Dateiname (slugifiziert):** `teaser-store-<city>-<name>` — lowercase, Umlaute aufgelöst (`ä→ae ö→oe ü→ue ß→ss`), Leerzeichen→`-`, sonst `[a-z0-9-]` (z. B. `teaser-store-hannover-kratom-koenig`).
- **Alt-Text (Klartext, nicht slugifiziert):** `<name> <district> <city>` (z. B. `Kratom König Mitte Hannover`).

**Ablauf:**
1. **Idempotenz (find):** Shopify Files nach dem Dateinamen abfragen (`files(query: "filename:teaser-store-<city>-<name>")`). **Treffer** → dessen `MediaImage`-GID wiederverwenden, Upload **überspringen** (kein Orphan-Duplikat beim Re-Run). Sonst weiter:
2. **Telegram-Bytes holen (server-seitig):** `create_download_url(image_file_id)` → kurzlebige URL; Sandbox `curl` lädt die Bytes nach `/tmp` (Credential bleibt serverseitig). Alternativ `download_file`, falls die Datei klein genug ist — im Zweifel den URL-Weg (byte-sicher).
3. **Staged Upload holen:** `stagedUploadsCreate` (via `graphql_mutation`) für einen Bild-Upload → Rückgabe `{ url, resourceUrl, parameters[] }`.
4. **Bytes hochladen:** Sandbox `curl` die `/tmp`-Datei mit den zurückgegebenen `parameters` an `url` (direkter Transfer, kein Kontext). **Erfolg = 2xx**; sonst fail-closed (§9).
5. **File registrieren:** `fileCreate(files: [{ originalSource: resourceUrl, alt: "<Alt-Text>", contentType: IMAGE }])` → `MediaImage`-GID. Bis `fileStatus = READY` pollen (kurz); erst dann ist die GID im Metaobjekt verwendbar.

> **Egress:** Der Staged-Upload-Host (aus `stagedUploadsCreate.url`) muss in der **Environment-Allowed-Hosts-Liste** stehen — einmalig aus einer Test-Session ablesen und build-time eintragen (nicht hardcoden, analog `restock.md` §6 / `global-agent-framework` §11). Fehlt er → Upload-Netzwerkfehler → fail-closed.

---

## 8. Writes — Reihenfolge Shopify → Lexware → Sheets → Drive (je find-or-create)

Erst ausführen, wenn **alle** Vorbedingungen (§3–§7) erfolgreich sind. Nach **jedem** Write ein **Read-back** zur Bestätigung; schlägt einer fehl → fail-closed (§9), die folgenden Writes unterbleiben.

### 8.1 Shopify `liftr_store`-Metaobjekt (Idempotenz-Wurzel)

**find:** `metaobjects(type: "liftr_store", first: 50, after: $cursor)` paginieren, je `google_place.value` parsen, `id == place_id` matchen. **Treffer** → Store existiert (Re-Run/Heal) → GID wiederverwenden, **kein** Create, weiter zu §8.2 (die restlichen Writes werden dort einzeln geheilt). **Kein Treffer** → zuerst §8.1.0, dann `metaobjectCreate`:

#### 8.1.0 District-Create (nur wenn §5.2 kein Treffer hatte)

Ist die `district`-GID aus §5.2 `null`, **jetzt** `liftr_district` anlegen via `metaobjectCreate`: `name` = gemerkter Bezirksname (Original-Schreibweise der Quelle), `city` = City-GID aus §5.1. Rückgabe-GID ist die `district`-Referenz für die Tabelle unten. Read-back: `metaobject(id:)`.

Dieser Schritt sitzt **hier** und nicht in §5.2, weil er ein Write ist (§2). Alle Vorbedingungen — inklusive Bild-Upload (§7) — sind an dieser Stelle bereits erfolgreich; scheitert erst der Store-Create danach, heilt ein Re-Run über den §5.2-Match. Läge der District-Create in der Vorbedingungs-Phase, hinterließe ein Fehler in §6/§7 einen verwaisten Bezirk ohne Store.

Schlägt der District-Create fehl → fail-closed (§9), **kein** Store-Create.

| Feld | Wert | Quelle / Format |
|---|---|---|
| `name` | Store-Name | Places `displayName.text` |
| `image` | Teaser-Bild-GID | §7 (`MediaImage`-GID) |
| `product_list` | Produkt-GIDs | Input `product_list` (JSON-Liste) |
| `collection_list` | Collection-GIDs | Input `collection_list` (JSON-Liste) |
| `rating` | Google-Bewertung | Places `rating` als Rating-Wert `{"value":"<r>","scale_min":"1.0","scale_max":"5.0"}` — Skala **zeichengenau** wie die Definition (`scale_min` `1.0`, `scale_max` `5.0`), sonst weist Shopify den Wert ab; **nur schreiben, wenn `rating` UND `userRatingCount ≥ 1`** — sonst Feld weglassen (§8.1.1) |
| `rating_count` | Anzahl Bewertungen | Places `userRatingCount`; **fehlt → `0`** |
| `adress` | Straße + Nr | §4.3 (ein `d`!) |
| `postal_code` | PLZ | §4.3 (Ganzzahl) |
| `city` | City-GID | §5.1 |
| `district` | District-GID | §5.2 |
| `phone` | Telefon | Places `nationalPhoneNumber` |
| `google_place` | Place-JSON | §4.2 (JSON-String) |
| `opening_hours` | Öffnungszeiten | §4.1 (JSON-String) |

**Read-back:** die zurückgegebene GID via `metaobject(id:)` lesen, `google_place.id == place_id` bestätigen.

> **Schicht-2-Hinweis (Security):** Der Store-Write geht über das generische `graphql_mutation` — Schicht 1 (`enabled:false`) trägt hier nicht (`global-agent-framework` §7-Sonderfall). Die tragende Wand ist der **Credential-Scope** des Shopify-Tokens im Vault (nur Metaobjekt-/File-Writes), plus `always_ask` in der Testphase. Der Agent operiert auf extern injiziertem Input — deshalb Token-Scope minimal halten.

#### 8.1.1 `rating`/`rating_count` bei Stores ohne Google-Bewertung

Ein frisch gelisteter Kiosk hat bei Google oft **keine** Bewertung → Places liefert `rating`/`userRatingCount` gar nicht. Dann: `rating_count = 0` und `rating` **weglassen** (nicht `0.0` schreiben, sonst zeigt der Store-Finder eine falsche 0-Sterne-Wertung).

**Drei Zustände, eine Regel.** Places serialisiert Protobuf-JSON und lässt Felder mit Default-Wert **weg** — `userRatingCount = 0` erscheint schlicht nicht in der Antwort. „Google hat keine Zählung" und „die Zählung ist 0" sind für den Agenten daher **nicht unterscheidbar**. Beobachtet wurde außerdem ein `rating` **ohne** `userRatingCount`. Deshalb gilt einheitlich:

> **`rating` wird nur geschrieben, wenn `rating` vorliegt UND `userRatingCount ≥ 1`.** In jedem anderen Fall: `rating` **weglassen**, `rating_count = 0`.

Das kollabiert „kein rating" und „rating ohne count" auf denselben Pfad. Andernfalls schriebe der Agent eine 5-Sterne-Wertung mit null Bewertungen in den Store-Finder — die spiegelverkehrte Variante genau des Fehlers, den der Absatz oben vermeidet. Der Zustand ist wohlgeformt und würde von keinem fail-closed gefangen; er wäre still falsch.

**Build-time verifiziert (erledigt).** Die `liftr_store`-Definition führte `rating`, `testimonial_list`, `product_list` und `collection_list` als Pflichtfelder; alle vier sind auf `required: false` gesetzt. Grund: sie beschreiben, was ein Store *erwirbt*, nicht was ihn *konstituiert* — ein frisch gelisteter Kiosk hat weder Bewertung noch Testimonials und ggf. kein Sortiment. Die Regel bleibt: **niemals** ersatzweise eine erfundene Wertung schreiben. Wird die Definition erneut verschärft, bricht §8.1 fail-closed — das ist gewollt.

### 8.2 Lexware Store-Kontakt + `POS-PARTNER`-Notiz

**find:** Store-Kontakt anhand Name + `postal_code` suchen (`list_contacts`/Suche). **Treffer** (Name + PLZ) → bestehenden Kontakt wiederverwenden (Heal); sicherstellen, dass die Notiz `POS-PARTNER: <Vertriebler>` gesetzt ist (sonst `update_contact`, `note` als **einziges** geändertes Feld, volles Objekt + `version` mitsenden). **Kein Treffer** → `create_contact` (Rolle `customer`) mit Adresse aus §4.3/Places und `note` = `POS-PARTNER: <Vertriebler>` (§6, zeichengenau).

**Warum die Notiz tragend ist:** Sie ist die **eine** Wahrheitsquelle für „ist POS-Partner" (agent-bridge note-Gate) **und** für den Vertriebler (`invoice.md` §2). Das Design hat **keinen** Fallback — ein Store-Kontakt ohne Marker fällt still durch (kein Event, keine Provision, kein Fehler). Der Marker gehört in **denselben** atomaren Anlage-Schritt wie der Kontakt; schlägt `create_contact`/`update_contact` fehl → fail-closed (§9), **nicht** ohne Marker weiterlaufen.

**Read-back:** `get_contact` der neuen/aktualisierten ID → `note` trägt den Marker; **`roles.customer.number`** auslesen (Lexware-Kundennummer) → das ist der Store-Match-Key für §8.3.

### 8.3 Sheets — Provisionszeile im `Stores`-Tab (Kundennummer als Key)

Ziel-Spreadsheet-ID = `POS-SHEET`-Wert aus §6. Geschrieben wird eine neue Zeile in die native Table **„Partner"** im `Stores`-Tab (dieselbe Table, gegen die `invoice.md` §4 matcht).

**find:** `get_range("Stores!B5:B")` → ist die Lexware-`roles.customer.number` (aus §8.2) bereits als Key vorhanden → **kein** Insert (Heal), weiter. Sonst Insert, header-basiert (Mechanik gespiegelt aus `invoice.md` §6):

1. `list_tables(spreadsheetId, sheetId=<Stores-gid>)` → `columnProperties` (Header-Name → Index) **und** aktuelle Table-`range` (`endRowIndex`). Nie Spaltenbuchstaben/Zeilennummern hardcoden.
2. Hat die Table eine Footer-/Summenzeile: Insert-Index = `endRowIndex − 1` via `insert_dimension` mit `inheritFromBefore: true` (schiebt Footer nach unten, vererbt Formel-Spalten). Ohne Footer: an `endRowIndex` innerhalb der Table einfügen. Pro Run neu lesen (Table wächst).
3. `batch_update_ranges` (`USER_ENTERED`) für die Werte-Spalten der neuen Zeile. Die Table „Partner" führt genau diese Spalten — Zuordnung über den Header-Namen aus Schritt 1, **nie** über einen Spaltenbuchstaben:

   | Spalte | Wert |
   |---|---|
   | **Lexware ID** | `roles.customer.number` (§8.2), als **Zahl** — numerischer Vergleich in `invoice.md` §4; ein String liefe `SUMIFS` still auf 0 |
   | **Name** | `liftr_store.name` (§8.1), Klartext |
   | **Akquise** | Datum des Laufs, `USER_ENTERED` als `TT.MM.JJJJ` (DE-Locale → Sheets parst zur Serienzahl) |
   | **Übergabeprotokolle** | `{postal_code} {store.name}` — **identisch** zum Drive-Ordnernamen (§8.4) |
   | **Bestandsprotokolle** | `{postal_code} {store.name}` |
   | **Menge / Einheiten / Umsatz / Provision** | Formelspalten — **nie** schreiben (durch `inheritFromBefore` vererbt) |

   - Es gibt **keine** Spalte `Status`. Nichts anderes als die fünf Wertespalten oben wird geschrieben.
   - DE-Locale: etwaige Dezimalzahlen mit **Komma** (`USER_ENTERED`).
4. **Read-back:** `get_range` auf die Key-Zelle der neuen Zeile → Kundennummer numerisch bestätigt; `list_tables` erneut → `endRowIndex` um 1 gewachsen.

> Der Key in `Stores!B` ist die **Lexware-Kundennummer** — zum Anlage-Zeitpunkt die einzige stabile, sofort verfügbare Kennung (JTL-Nummer existiert noch nicht). Genau diese Nummer prüft `invoice.md` §4 gegen `Stores!B5:B` und schreibt sie in `Umsatz!E`. Kein Fallback: eine Zeile ohne korrekte Nummer fällt beim §4-Match still durch.

> **Kein Chip-Spaltentyp auf Agent-Spalten** (universelle Invariante 4, SKILL.md). `Stores!C` („Name") trug `columnType: PLACE_CHIP` — die Values-API liefert für Chip-Spalten einen **leeren Wert**, still und ohne Fehler. Ein Read auf `C` hätte den Storenamen nie gesehen. Der Typ ist aus allen Provisions-Sheets entfernt; er darf nicht zurückkommen.

### 8.4 Drive — zwei Ablage-Ordner anlegen

Pro Store je ein Store-Ordner unter der **Übergabeprotokolle-** und der **Bestandsprotokolle-**Wurzel (`registry.md` §2), damit `pos-restock`/`pos-inventory` ihre Zielordner vorfinden. Beide Wurzeln existieren bereits — die Store-Anlage legt nur die Stadt/Store-Unterpfade an, **idempotent**:

```
<Übergabeprotokolle-Wurzel>/{city.name}/{postal_code} {store.name}/
<Bestandsprotokolle-Wurzel>/{city.name}/{postal_code} {store.name}/
```

- Je ein `ensure_folder_path` mit `parentFolderId` = jeweilige Wurzel (§2) und `segments = [ "{city.name}", "{postal_code} {store.name}" ]`. mkdir-p, serverseitig NFC-normalisiert — nie ein zweiter gleichnamiger Ordner (Heal-sicher).
- Segmente **1:1 aus den `liftr_store`-Feldern** des in §8.1 angelegten Stores (`city`→`name`, `postal_code`, `name`), **keine** Slugifizierung — identische Namenslogik wie `restock.md` §6 / `inventory.md`, sonst zielen die anderen Agenten auf falsche Ordner.
- Die Wurzel-IDs stehen in `registry.md` §2 (nicht hardcoden).

### 8.5 🎉-Broadcast in den City-Channel (nur CREATE-Zweig, best-effort, letzter Schritt)

Der einzige **öffentliche** Post dieses Agenten. Läuft als **allerletzter** Schritt, **nach** dem §8.4-Read-back — zu diesem Zeitpunkt sind alle vier Fachsystem-Writes bestätigt, der Store ist **erfolgreich**.

**Gating — nur wenn §8.1 den Store NEU angelegt hat (CREATE-Zweig).** Hat §8.1 einen bestehenden Store gematcht (Heal/Re-Run), wird §8.5 **komplett übersprungen — kein Post**. Das ist die **ganze** Doppel-Post-Sperre: **kein Marker, kein Metafield.** Ein Re-Run trifft zwangsläufig den §8.1-Heal-Zweig und postet nie erneut. Ein 🎉, der bei Abbruch **nach** dem §8.1-Create und **vor/bei** §8.5 verloren geht, ist **bewusst akzeptiert** — er fehlt dann (nicht doppelt) und wird über die Schluss-Statuszeile (§9) im Operations-Topic sichtbar (manueller Nachpost, **kein** Auto-Retry — der Re-Run heilt und schweigt).

**Best-effort — bricht den Store nie.** Ein Fehler **oder** Skip in §8.5 rollt **nichts** zurück und macht den Lauf **nicht** fail-closed. Er annotiert nur die Schluss-Statuszeile (§9). „Store angelegt" bleibt der Ausgang.

**1. Channel auflösen (`registry.md` §1).** City-Name = die in §5.1 gematchte `liftr_city` (`name`). Numerische `chat_id` = **direkter Lookup** in `registry.md` §1 (kein Ableiten, kein Override).
- **Kein Eintrag für die Stadt** → **Broadcast SKIP**, **kein** fail-closed. Store bleibt erfolgreich; Schluss-Status (§9): „✅ Store angelegt · ℹ️ Broadcast übersprungen (kein Channel für `<Stadt>`)".

**2. Bild = Shopify-CDN-URL, nicht Telegram-`file_id`.** `send_photo(photo=<url>)` mit der **`image.url`** des in §7 angelegten `MediaImage` — nach `fileStatus = READY` via `image { url }` auslesen (die öffentliche `cdn.shopify.com`-URL). Die eingehende Telegram-`file_id` wird **nicht** wiederverwendet: sie ist chat-übergreifend nicht stabil (und stammt ohnehin aus einem anderen Bot-Scope, s. Punkt 4).

**3. Caption = 🎉-Template (HTML, selbsttragend — kein Sprung in `telegram.md`).** Der Store *ist* die News → Store **fett** in der Headline, taucht **nicht** zusätzlich in einer Meta-Zeile auf. 🕒-Zeile abgesetzt, dann CTA als Verb-Link:

```
🎉 <b>Neuer Partner: {store_name}</b>
{stadtteil} · {adresse}

🕒 <b>Öffnungszeiten</b>
Mo–Do    08:30–23:30
Fr–Sa    durchgehend
So       09:00–23:30

<a href="{maps_link}">Google Maps öffnen</a>
```

- `{store_name}` = `liftr_store.name` (§8.1) · `{stadtteil}` = `district.name` (§5.2) · `{adresse}` = `adress` (§4.3, ein `d`).
- **Öffnungszeiten = eigener Block, ein Tagesbereich pro Zeile.** Gerendert aus `opening_hours` (§4.1): aufeinanderfolgende Tage mit identischem Intervall werden zu einer Spanne zusammengezogen (`Mo–Do`), 24-Stunden-Tage heißen `durchgehend`, geschlossene Tage `geschlossen`. Die Werte oben sind ein **Beispiel**, kein Default — geschrieben wird, was §4.1 liefert.
- **Nie** die Tage mit `·` zu einer Zeile verketten. Telegram bricht lange Caption-Zeilen weich um; die Umbruchstelle liegt dann mitten in einem Tagesbereich und die letzte Zeile zerreißt. Ein harter Zeilenumbruch pro Bereich ist die einzige Form, die auf jeder Client-Breite hält.
- `{maps_link}` aus `google_place` (§4.2): `https://www.google.com/maps/search/?api=1&query={name}&query_place_id={place_id}` — in HTML **jedes `&` → `&amp;`**.
- **CTA:** „Google Maps öffnen" als `<a href>`-**Verb-Link** — kein roher URL, **kein Underline** (native Telegram-Linkfarbe), Leerzeile davor.
- **Feed-Regeln (inline, wie `telegram.md` §6):** **keine Menge**, **keine Wirkungsangabe**, keine Hashtags, keine „Jetzt"-Urgency. Ton = **lokaler Tipp**, kein Shop-Ton, kein Hard-Sell.

**4. Posten — `send_photo` des `telegram-broadcast`-Servers (öffentlicher City-Channel, NICHT das Operations-Topic):**

```
telegram-broadcast · send_photo(
  chat_id    = <numerische chat_id aus registry.md §1>,   # City-Channel
  photo      = <image.url des §7-MediaImage, cdn.shopify.com>,
  caption    = "<🎉-Caption, HTML>",
  parse_mode = "HTML"
)
```

> **Bot-Trennung (zwingend, verifiziert).** `telegram-operations-mcp` und `telegram-broadcast-mcp` sind **zwei Bots mit zwei Tokens**. Der Operations-Bot sitzt in der Operations-Gruppe, der Broadcast-Bot in den City-Channels. Ein Bot sieht ausschließlich die Chats, in denen er Mitglied ist — `send_photo` über `telegram-operations` an einen City-Channel scheitert mit `400 chat not found` (verifiziert an `-1004399731658` und am Live-Channel Hannover `-1003904362997`). Beide Server tragen ein gleichnamiges `send_photo`; der Server, **nicht** der Toolname, entscheidet. Faustregel: **öffentlich → `telegram-broadcast`, Operations-Topic (§9) → `telegram-operations`.**

- **Erfolg** → Schluss-Status (§9): „… · 🎉 Broadcast gepostet".
- **`send_photo`-Fehler** → Store bleibt erfolgreich; Schluss-Status: „… · ⚠️ Broadcast fehlgeschlagen (Store ist angelegt) — manuell nachposten". **Kein** Rollback, **kein** Auto-Retry.

> **Rest-Verifikationspunkt (Doku, kein Code):** Telegram fetcht die `cdn.shopify.com`-URL server-seitig. Nach dem Cutover einmal an einem realen Store live bestätigen, dass der Staged-Upload-Host bzw. das CDN vom Worker erreichbar ist (analog §7-Egress).

---

## 9. fail-closed & Status-Posts ins Operations-Topic

Ziel jeder Meldung: `chat_id` + `message_thread_id` aus der Injektion (§1) — das Quell-Topic, aus dem der Auftrag kam. Ist kein `message_thread_id` injiziert (General-Topic), wird der Parameter **weggelassen** (`message_thread_id: 1` lehnt die Bot-API mit „message thread not found" ab — verifiziert in `invoice.md` §9).

| Ausgang | Status (Beispiel) |
|---|---|
| Anlage erfolgreich + Broadcast (§8.5) | „✅ Store angelegt: **Kratom König** (Mitte, Hannover) — Shopify + Lexware + Provision (Schlegel) + Drive. Metaobjekt `…`. · 🎉 Broadcast gepostet." |
| Anlage erfolgreich, kein Channel (§8.5) | „✅ Store angelegt: **…** — Shopify + Lexware + Provision + Drive. · ℹ️ Broadcast übersprungen (kein Channel für `<Stadt>`)." |
| Anlage erfolgreich, Broadcast-Fehler (§8.5) | „✅ Store angelegt: **…** — Shopify + Lexware + Provision + Drive. · ⚠️ Broadcast fehlgeschlagen (Store ist angelegt) — manuell nachposten." |
| Re-Run/bereits vorhanden (Heal-Zweig) | „ℹ️ Store zu Place-ID `…` existiert bereits — fehlende Teile ergänzt / nichts zu tun. **Kein** Broadcast (nur CREATE-Zweig postet)." |
| Fehlendes Pflichtfeld (§1) | „⚠️ Store-Anlage abgebrochen: Pflichtfeld `<feld>` fehlt in der Auftrags-Nachricht." |
| Places-Zug fehlgeschlagen (§3) | „⚠️ Store-Anlage abgebrochen: Place Details zu `<place_id>` nicht abrufbar." |
| Adresse unvollständig (§4.3) | „⚠️ Store-Anlage abgebrochen: Straße/Nr oder PLZ fehlt in den Places-Daten." |
| **City kein Treffer** (§5.1) | „⚠️ Store-Anlage abgebrochen: Stadt „<Stadt>" hat keinen `liftr_city`-Eintrag — City zuerst anlegen, dann erneut." |
| **District-Create fehlgeschlagen** (§8.1.0) | „⚠️ Store-Anlage abgebrochen: Bezirk „<Name>" konnte nicht angelegt werden — `<konkreter Fehler>`. **Kein** Store-Write erfolgt." |
| Vertriebler nicht in Registry (§6) | „⚠️ Store-Anlage abgebrochen: Vertriebler „<Name>" nicht in registry.md §4." |
| Kein `POS-SHEET`-Marker (§6) | „⚠️ Store-Anlage abgebrochen: Vertriebler-Kontakt ohne `POS-SHEET`-Notiz — Ziel-Sheet unbekannt." |
| Bild-Upload fehlgeschlagen (§7) | „⚠️ Store-Anlage abgebrochen: Teaser-Bild konnte nicht nach Shopify geladen werden." |
| Write fehlgeschlagen (§8.x) | „⚠️ Store-Anlage abgebrochen nach `<Shopify\|Lexware\|Sheets\|Drive>` — `<konkreter Fehler>`. Re-Run heilt den Rest." |

```
post_message(
  chat_id           = <injiziert>,                 # Operations-Chat
  message_thread_id = <injiziert, sonst weglassen>, # Quell-Topic; General = weglassen
  text              = "<Status-Zeile>",
  parse_mode        = "HTML"
)
```

**Die Erfolgszeile nennt den Bezirk explizit.** Das ist keine Kosmetik: ein Grenzlagen-Fehler im Geocoder der Bridge liefert einen wohlgeformten, aber falschen Bezirk, den keine Prüfung fängt. Die Zeile im Operations-Topic ist der einzige Detektor. Steht dort ein Bezirk, der nicht stimmt, ist die Korrektur ein manueller Eingriff in Shopify — kein Re-Run heilt ihn.

Der Agent postet **nichts**, wenn ein Write erfolgreich war, aber ein späterer scheitert, außer der abschließenden ⚠️-Abbruchzeile — **kein** „halb erfolgreich, ignorier den Rest".

Der 🎉-Broadcast (§8.5) ist davon **ausgenommen**: er läuft **nach** allen vier Writes und ist **best-effort** — sein Skip/Fehler ist **kein** Abbruch, sondern nur ein annotierter Zusatz an der Erfolgs-Statuszeile (siehe die drei §8.5-Ausgänge oben).

---

## 10. Non-Goals (bewusst außerhalb dieser Kette)

- **Nur der 🎉-Milestone auf City-Channels — kein edit/pin/delete.** Der Agent postet ausschließlich den einmaligen 🎉-„Neuer Partner"-Broadcast (§8.5, `send_photo`) und **nur** im CREATE-Zweig. Er **editiert, pinnt, löscht** oder verwaltet **nichts** auf den City-Channels und postet **keine** anderen Stream-Typen (📦/🌿/🕒 gehören zu `pos-restock` bzw. anderen Flows). Das generische Channel-Setup-/Lifecycle-Handwerk (Pinned, Channel-Launch einer Stadt) bleibt in `telegram.md` (separate Domäne). Least-Privilege: das Posting-Recht auf City-Channels beschränkt sich auf `send_photo`.
- **Keine City-Anlage.** Der erste Store einer neuen Stadt läuft fail-closed (§5.1) — City-Onboarding (Kanal etc.) ist ein eigener, bewusst menschlicher Schritt.
- **Keine Bezirks-Ermittlung im Agenten.** Der Name kommt aus §1. Der Agent geocodiert nicht, ruft keinen externen Kartendienst und liest keine Places-Bezirksfelder (§4.3). Grund: Reverse-Geocoder authentifizieren per Query-String-Key, der Vault injiziert nur in Header/Body — der Agent *kann* sie nicht aufrufen (verifiziert). Der Zug gehört in die `agent-bridge`.
- **Kein Bezirk aus der PLZ.** PLZ und Stadtteil stehen in Deutschland in einer **n:m**-Beziehung, nicht in einer Funktion — `30167` überspannt Nordstadt *und* Teile der Calenberger Neustadt. Jede PLZ→Stadtteil-Tabelle ist eine Schätzung mit eingebauter Fehlerrate. Bewusst verworfen.
- **Kein Bezirk aus Google `addressDescriptor`.** Das Feld ist außerhalb Indiens **pre-GA/experimentell** (keine Kompatibilitätszusage), sein `areas`-Array ist eine ML-geschätzte Containment-Liste (`WITHIN`/`OUTSKIRTS`/`NEAR`), kein 1:1-Bezirk — und es kostet zusätzliche Places-Gebühren. Als Quelle für ein Pflichtfeld mit Create-Autorität bewusst verworfen.
- **Kein Produkt-Picking / keine Collection-Ableitung.** `product_list`/`collection_list` kommen fertig injiziert (§1); die Ableitung geschieht upstream (Bridge/Dialog), nicht hier.
- **Keine USt-ID / Rechtsform.** Bewusst nicht im Flow — manuelle Nachpflege am Lexware-Kontakt.
- **Keine Jahres-Logik fürs Sheet.** Die Ziel-Datei-ID kommt aus `POS-SHEET` (§6); Rollover/Copy-based-Jahreswechsel ist separater (späterer) Prozess.
- **Kein Bridge-/Dialog-Bau.** Der Input-Kontrakt (§1) ist die Schnittstelle; die Bridge, die ihn füllt (inkl. `image_file_id`-Injektion), ist ein eigener Schritt.
