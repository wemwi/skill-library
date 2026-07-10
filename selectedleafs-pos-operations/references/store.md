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
| `assortment_list` | Array von `liftr_assortment`-**Handles** | GID-Auflösung (§5.3) → `liftr_store.assortment_list` (§8.1) |
| `service_extra` | Array von `liftr_service`-**Handles**, die Places nicht kennt | GID-Auflösung (§5.3) → `service_list` (§4.5) |
| `parcel_carriers` | Array aus `dhl` `hermes` `dpd` `gls` `ups` `andere` | Paketshop-Highlight (§4.4) + `paketannahme-moeglich` (§4.5) |
| `socials` | Objekt mit `tiktok` / `facebook` / `instagram` / `whatsapp` | `liftr_store` (§8.1), je einzeln optional |
| `chat_id` + `message_thread_id` | Operations-Quell-Topic (wo der Auftrag/das Bild herkam) | Ziel der Status-/Rückfrage-Posts (§9) |

Fehlt ein **Pflichtfeld** (`place_id`, `vertriebler_contact_id`, `image_file_id`, `district`) → fail-closed **vor** jedem Read/Write, Status ins Topic (§9). `product_list`/`collection_list` dürfen leer sein (Store wird ohne Sortiment angelegt), sind aber Pflichtfelder im Schema (§8.1) — leere Liste ist zulässig, fehlendes Feld nicht.

**Die vier Dialog-Felder sind KEINE Kontrakt-Pflichtfelder.** Fehlt eines oder ist es ein leeres Array/Objekt, wird das entsprechende Metaobjekt-Feld schlicht **nicht geschrieben** — kein fail-closed, keine Rückfrage. Ein *fehlerhafter* Wert ist dagegen kein zulässiger Zustand (§5.3: unbekannter Handle → fail-closed).

> **Dialog-Pflicht ≠ Kontrakt-Pflicht.** Zwei verschiedene Wände, und sie stehen an verschiedenen Stellen.
>
> `assortment_list` ist im Dialog **Pflicht: mindestens ein Handle.** Die Bridge lässt den Vertriebler nicht weiter, bis er wählt — ein Store ohne Sortiment ist ein leerer Filter im Store-Finder.
>
> Der **Agent** erzwingt das trotzdem nicht. Fehlt das Feld, hat nicht der Vertriebler etwas ausgelassen, sondern die Bridge es nicht mitgeschickt. Ein fail-closed an dieser Stelle bestraft den falschen Akteur: der Store wird nicht angelegt, der Vertriebler steht im Laden, und die Statusmeldung nennt ihm ein Feld, von dem er nie gehört hat. Eine Regel gehört dorthin, wo ein Mensch sie erfüllen kann.
>
> `service_extra` und `parcel_carriers` sind auch im Dialog **überspringbar** — „keiner der drei Services" und „kein Paketshop" sind gültige Antworten. Skip und bewusstes Nein sind hier ununterscheidbar und führen zum selben Ergebnis. `socials` ist je Kanal einzeln überspringbar.

> **Bridge-Anforderung (noch nicht geliefert).** Die vier Dialog-Felder oben injiziert die heutige `agent-bridge` noch **nicht**. Bis sie es tut, läuft `pos-store` unverändert durch und lässt die Felder aus — der Kontrakt ist rückwärtskompatibel. Für den Bridge-Auftrag ist die Dialog-Reihenfolge festgehalten, damit sie dort nicht neu erfunden wird: **`vertriebler_contact_id` → `place_id` → `image_file_id`** → *`district`* (nur wenn der Geocoder ihn nicht auflöst) → `product_list` → **`assortment_list`** → `service_extra` → `parcel_carriers` → `socials`. Fett = Pflicht im Dialog, kursiv = bedingt, Rest überspringbar. `assortment_list` zeigt die **Namen** der 13 bestehenden `liftr_assortment`-Einträge und sendet deren **Handles** — nicht slugifizieren, mindestens ein Handle weicht vom Namen ab (`tiefkuehlprodukte-eis` = „Eis & Tiefkühlware"). `service_extra` hat genau **drei** Checkboxen (`lgbtq-freundlich`, `frauenfreundlich`, `haltestelle-in-der-naehe-oepnv`); der vierte Nicht-Places-Service `paketannahme-moeglich` kommt aus `parcel_carriers` (§4.5).
>
> **Die Reihenfolge ist Bridge-Spec, nicht Agenten-Sache.** Der Agent führt keinen Dialog (§Kopf) — er liest, was ankommt.

> **`district` ist Bridge-Vertrag, kein Ratefeld.** Die Bridge ermittelt den **Stadtteil** (nicht den Stadtbezirk) per Reverse-Geocoding auf OSM-Daten und prüft dort drei Bedingungen: Land ist `de`, die Geocoder-Stadt stimmt mit der Places-`locality` überein, und ein Stadtteil ist überhaupt vorhanden. Kann sie ihn nicht auflösen — kleinere Städte führen oft keine Stadtteil-Grenzrelation —, fragt sie im Dialog nach. Der Agent bekommt in **jedem** Fall einen Namen oder gar keine Session. Er ergänzt, korrigiert oder errät hier **nichts**.

---

## 2. Ablauf-Prinzip — erst Vorbedingungen, dann Writes; fail-closed; per-Write-Idempotenz

Drei Invarianten, die den ganzen Lauf tragen (Konkretisierung von `SKILL.md` §Invarianten + `global-agent-framework` §13):

1. **Erst alle Vorbedingungen, dann Writes.** Sämtliche Reads/Matches (§3–§7: Places-Zug, Ableitungen, City-Match, District-**Match**, Handle-Auflösung, Vertriebler-Auflösung, Bild-Bereitstellung) laufen **vollständig und erfolgreich**, bevor **irgendein** Fachsystem-Write (§8) passiert. Scheitert eine Vorbedingung → fail-closed, kein Write.
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
  -H "X-Goog-FieldMask: displayName,addressComponents,formattedAddress,location,regularOpeningHours,rating,userRatingCount,nationalPhoneNumber,timeZone,websiteUri,paymentOptions,parkingOptions,allowsDogs,delivery,accessibilityOptions"
```

- **`formattedAddress` gehört in die FieldMask** — §4.2 braucht es für das `google_place`-JSON. Fehlt es, muss der Agent Places ein zweites Mal ziehen (verifiziert in Session `sesn_01ANYcDhXVzH3JTjS3GFBoR5`).
- **Die hinteren sechs Felder speisen `highlights` (§4.4) und `service_list` (§4.5).** `websiteUri` speist zusätzlich `website` (§8.1).
- **FieldMask ohne Leerzeichen** — Google lehnt Leerzeichen in der Feldliste ab.
- **Kein FieldMask = Fehler.** Es gibt keine Default-Feldliste; der Header ist Pflicht.
- **`${GOOGLE_PLACES_API_KEY}` kommt aus dem Vault** (Anmeldedaten-Tresor des Agenten, Typ Umgebungsvariable). Der Wert wird **nie** geloggt, nie in eine Statusmeldung (§9) geschrieben und nie in ein anderes Ziel gesendet: die Zugangsdaten sind auf den Host `places.googleapis.com` und den Injektionsort **Request-Header** beschränkt. Der Variablenname ist Konfiguration und darf im Code stehen — der **Wert** gehört auf keine Skill-/Prompt-/Message-Ebene (`global-agent-framework` §6).
- **Egress:** `places.googleapis.com` ist über die Host-Bindung der Zugangsdaten freigegeben. Fehlt sie, schlägt der `curl` als Netzwerkfehler fehl → fail-closed (§9), **nicht** auf einen anderen Weg ausweichen (`global-agent-framework` §13).

Antwort ist ein `Place`-JSON; die `place_id` steht darin als `id`, der Name als `displayName.text`. Scheitert der Zug (kein Treffer, HTTP ≠ 2xx, leere Antwort) → fail-closed (§9). Aus dem Ergebnis werden §4/§5 gespeist. `timeZone` trägt die Über-Mitternacht-Logik der Öffnungszeiten (§4.1); es wird **nicht** ins Metaobjekt geschrieben.

> **Kosten — bewusste Entscheidung, einmal pro Onboarding.** `paymentOptions`, `parkingOptions`, `allowsDogs` und `delivery` heben den Zug auf die **Enterprise + Atmosphere**-SKU; `accessibilityOptions` und `websiteUri` liegen auf **Pro**. Der Zug lag vorher unter beiden. Der Aufschlag fällt **einmal pro Store-Anlage** an, nicht pro Seitenaufruf — das ist der Preis dafür, dass Highlights und Services ohne einen Menschen und ohne generierten Text entstehen. Kein Grund, die FieldMask später „aus Sparsamkeit" wieder zu kürzen: ein fehlendes Feld erzeugt keinen Fehler, sondern **still einen ärmeren Store** (§4.5).
>
> **`priceLevel` wird bewusst NICHT angefragt** (§10) — es ist Googles Wertung, nicht die von selectedleafs.

**Fehlende Felder sind kein Fehler.** Places serialisiert Protobuf-JSON und lässt Felder mit Default-Wert **weg** (dieselbe Mechanik wie bei `userRatingCount`, §8.1.1). `paymentOptions` kann komplett fehlen, `allowsDogs` kann fehlen, `delivery` kann fehlen. Der Agent bricht deswegen **nicht** ab — er wertet nur aus, was da ist (§4.4/§4.5). Pflicht bleiben allein die Felder aus §4.3.

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

### 4.4 `highlights` — drei Slots, feste Reihenfolge

`highlights` ist `list.single_line_text_field` mit `list.max 3`, optional. **Der Agent formuliert nie — er wählt aus.** Alle zulässigen Phrasen stehen wörtlich unten. Es gibt keine Regel, die einen Text *erzeugt* (§10).

Die drei Slots werden in dieser Reihenfolge belegt und stehen in dieser Reihenfolge im Array.

**Slot 1 — Zahlung. Vollautomatisch, nie leer.** Bargeld ist eine Kiosk-Konstante, die selectedleafs verantwortet, nicht Google. Deshalb fällt dieser Slot auch dann nicht aus, wenn Places gar kein `paymentOptions` liefert.

```
acceptsCashOnly == true                                  → "Nur Barzahlung"
acceptsCreditCards == true ODER acceptsDebitCards == true → "Barzahlung & Karte"
sonst                                                    → "Barzahlung"
```

Erste zutreffende Regel gewinnt. `acceptsNfc` gehört **nicht** hierher — mobiles Zahlen ist ein Service (§4.5), kein Highlight.

**Slot 2 — Öffnungszeit-Charakter. Vollautomatisch, aus `opening_hours` (§4.1), kein Places-Zug.**

```
durchgehend UND 7 Tage    → "24/7 geöffnet"
7 Tage geöffnet           → "Täglich geöffnet"
Schluss nach 22:00 Uhr    → "Lange geöffnet"
sonst                     → Slot bleibt leer
```

Genau eine Phrase; erste zutreffende Regel gewinnt. Die Reihenfolge ist tragend: „24/7" und „Täglich" treffen beide auf einen durchgehend geöffneten Laden zu, und „24/7" ist die stärkere Aussage.

Präzisierung der Begriffe gegen §4.1:

- **durchgehend** = jeder der sieben Keys trägt genau `[["00:00","00:00"]]`.
- **7 Tage geöffnet** = kein Key ist ein leeres Array `[]`.
- **Schluss nach 22:00 Uhr** = an mindestens einem Tag schließt ein Paar später als `"22:00"`.

> **Der Über-Mitternacht-Wrap zählt IMMER als spät.** Bei `["10:00","01:00"]` ist die Schlusszeit als String **kleiner** als die Öffnungszeit — ein naiver Vergleich `close > "22:00"` sagt „nein" und nimmt ausgerechnet dem Spätkiosk sein Highlight. Regel: ist `close <= open`, wrappt das Paar über Mitternacht und gilt ohne weitere Prüfung als Schluss nach 22:00. Ausnahme: `["00:00","00:00"]` (24 h) — das ist kein Wrap, sondern der Durchgehend-Fall.

**Slot 3 — optional, Priorität von oben nach unten.**

```
1. delivery == true       → "Lieferung möglich"
2. parcel_carriers gesetzt → Paketshop-Label (Regel unten)
3. sonst                  → Slot bleibt leer
```

**Ein Store mit nur zwei Highlights ist ein gültiger Store.** Der dritte Slot wird **nie** aufgefüllt — weder mit einem schwächeren Kandidaten noch mit Freitext (§10).

**Paketshop-Label.** `parcel_carriers` ist eine Mehrfachauswahl; das Label ist deterministisch:

```
1 Carrier    → "{Carrier} Paketshop"     z.B. "DHL Paketshop"
2 Carrier    → "{A} & {B} Paketshop"     z.B. "DHL & Hermes Paketshop"
3+ Carrier   → "Paketannahme"
nur "andere" → "Paketannahme"
```

Die Carrier werden **fest sortiert** (`DHL → Hermes → DPD → GLS → UPS`), **nicht** nach Klickreihenfolge im Dialog. Sonst erzeugen zwei Läufe mit derselben Auswahl zwei verschiedene Labels, und das Feld ist nicht reproduzierbar. `andere` sortiert immer zuletzt und wird im 1er-/2er-Label **nicht** benannt (es gibt keinen Namen) — enthält die Auswahl `andere` plus genau einen echten Carrier, gilt der 2er-Fall nicht, sondern der 1er-Fall mit diesem Carrier.

> **Warum bei 3 Carriern abgeschnitten wird.** Highlights sind P3 in `liftr-card-density` und brechen als Erstes um. „DHL, Hermes & DPD Paketshop" sind 27 Zeichen — das reißt die Zeile auf der Store-Card. „Paketannahme" trägt dieselbe Information für den Kunden vor Ort und passt.

**Ausschlussregel `delivery`.** Belegt „Lieferung möglich" den Slot 3, fällt der Service `lieferung-moeglich` aus `service_list` (§4.5) — Highlights und Services stehen auf derselben Card, eine Dopplung liest sich wie ein Fehler. Umgekehrt: kein Highlight (weil Slot 3 schon durch nichts belegt ist — der Fall existiert nicht, `delivery` hat Priorität 1) — die Regel ist also einseitig: `delivery == true` ⟹ Highlight, **nie** Service.

**Paketshop speist zwei Felder, aber asymmetrisch.** Mindestens ein Carrier gewählt → `paketannahme-moeglich` steht **immer** in `service_list` (§4.5). Das Paketshop-**Highlight** entsteht nur, wenn Slot 3 nicht schon durch `delivery` belegt ist. Ein Store mit Lieferung *und* Paketshop zeigt also „Lieferung möglich" als Highlight und `paketannahme-moeglich` als Service — beides sichtbar, nichts doppelt.

### 4.5 `service_list` — 10 aus Places, 4 aus dem Dialog

Ein Service wird **nur bei explizitem `true`** angehängt. `false` und **fehlend** werden übersprungen: Google weiß es dann nicht, und das ist keine Aussage über den Laden. Ein nicht gesetzter Service ist besser als ein falscher.

| Handle | Places-Feld |
|---|---|
| `zahlen-mit-kreditkarte` | `paymentOptions.acceptsCreditCards` |
| `mobil-zahlen-mit-nfc` | `paymentOptions.acceptsNfc` |
| `barzahlung-moeglich` | `paymentOptions.acceptsCashOnly` ⚠️ |
| `parkplaetze-an-der-strasse-kostenlos` | `parkingOptions.freeStreetParking` |
| `parkplaetze-an-der-strasse-gebuehrenpflichtig` | `parkingOptions.paidStreetParking` |
| `hunde-erlaubt` | `allowsDogs` |
| `lieferung-moeglich` | `delivery` — **nur wenn `false`/fehlend** (Ausschlussregel §4.4) |
| `rollstuhlgerechter-eingang` | `accessibilityOptions.wheelchairAccessibleEntrance` |
| `rollstuhlgerechter-parkplatz` | `accessibilityOptions.wheelchairAccessibleParking` |
| `rollstuhlgerechte-sitzgelegenheiten` | `accessibilityOptions.wheelchairAccessibleSeating` |

> ⚠️ **`acceptsCashOnly` heißt „nur Bargeld", nicht „Bargeld möglich".** Ein `acceptsCash` existiert in Places nicht. `barzahlung-moeglich` wird deshalb **nur** bei `acceptsCashOnly: true` gesetzt. Bei `false` weiß man über Bargeld nichts (nur, dass es nicht das einzige Mittel ist) → Service weglassen. Das ist die einzige Zeile der Tabelle, in der Feldname und Bedeutung auseinanderfallen — sie wurde schon einmal falsch gelesen.

**Aus dem Dialog, kein Places-Feld** (§1): `lgbtq-freundlich`, `frauenfreundlich`, `haltestelle-in-der-naehe-oepnv` kommen aus `service_extra`. `paketannahme-moeglich` kommt aus `parcel_carriers` — mindestens ein Carrier (auch `andere`) ⟹ Service gesetzt.

Die entstehende Handle-Liste (Places + Dialog, dedupliziert) geht in §5.3 zur GID-Auflösung.

> **Der Agent legt niemals einen `liftr_service` an.** Die 14 bestehenden sind eine kuratierte, geschlossene Taxonomie mit `icon`- und `order`-Feld für den Store-Finder. Ein per Agent angelegter Service hätte weder Icon noch Sortierung und stünde still falsch in der Liste. Kein Treffer für einen Handle → fail-closed (§5.3), **kein** Create.

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
> Der Geocoder-Aufruf gehört deshalb in die `agent-bridge` (Cloudflare Worker, Worker-Secret, kein Egress-Proxy). Sie führt den Zug aus, prüft die Guards und liefert **nur den Namen**. Sie kann den `liftr_district` **nicht anlegen** — ihr Shopify-Grant umfasst ausschließlich Lese-Scopes (`read_metaobject_definitions`, `read_metaobjects`, `read_products`). Das Anlegen bleibt beim Agenten (§8.1.0).

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

### 5.3 Service- und Assortment-Handles auf GIDs auflösen (nur MATCH, nie anlegen)

`service_list` und `assortment_list` sind `list.metaobject_reference` — Shopify nimmt dort **GIDs**, keine Handles. Der Dialog liefert Handles (§1). Die Auflösung passiert **hier**, in der Vorbedingungsphase, nicht in §8.1.

**Je ein paginierter Read pro Typ, nicht einer pro Eintrag:**

```graphql
metaobjects(type: "liftr_service",    first: 50, after: $cursor) { nodes { id handle } ... }
metaobjects(type: "liftr_assortment", first: 50, after: $cursor) { nodes { id handle } ... }
```

Beide Sets sind geschlossen und klein (14 Services, 13 Assortments) — **zwei Züge im ganzen Lauf**, unabhängig davon, wie viele Einträge der Vertriebler gewählt hat. Aus den Antworten baut der Agent je eine `handle → id`-Tabelle und schlägt darin nach.

- **Der Handle-Vergleich ist zeichengenau.** Keine Normalisierung, kein Casefold, kein Trim-und-hoffen (anders als beim Bezirksnamen, §5.2). Handles sind Maschinenschlüssel aus einem geschlossenen Set, keine menschliche Eingabe.
- **Handle nicht in der Tabelle → fail-closed (§9), kein Create.** Ein unbekannter Handle ist ein Bridge- oder Tippfehler, keine Aussage über den Laden. Ihn zu überspringen hieße, einen stillen Datenverlust als Erfolg zu melden; ihn anzulegen hieße, die Taxonomie zu verwässern (§4.5).
- **Leeres Array oder Feld fehlt → kein Fehler.** Das Feld wird in §8.1 schlicht weggelassen (§1).

> **Warum das ein Read ist und in §5 gehört.** §2 verlangt: alle Reads vor dem ersten Write. Läge die Auflösung in §8.1, käme sie **nach** dem District-Create (§8.1.0) — ein getippter Handle hinterließe dann einen frisch angelegten Bezirk ohne Store. Genau der verwaiste Zustand, den §2 an anderer Stelle schon einmal beseitigt hat.

> **Keine GIDs im Skill, keine GIDs im Dialog.** Handles sind für den Vertriebler lesbar, überstehen einen Metaobjekt-Rebuild und machen den Bridge-Payload diffbar. Eine hartkodierte GID-Tabelle (hier oder in `registry.md`) driftet still, sobald jemand ein Metaobjekt neu anlegt — sie sähe weiter gültig aus und zeigte ins Leere. Die Auflösung zur Laufzeit kostet zwei Züge und kann nicht altern.

---

## 6. Vertriebler auflösen (Vorbedingung) — Lexware ist die Wahrheitsquelle

**Ein** `get_contact(vertriebler_contact_id)` liefert beides:

1. **Vertrieblername** = der Kontaktname (Firma, sonst `person.firstName person.lastName`). Rein **kosmetisch**: er geht in die Status-Zeile (§9) und den 🎉-Broadcast, ist aber **kein** Lookup-Schlüssel. Nichts hängt an seiner Schreibweise. Kein Registry-Abgleich — die `vertriebler_contact_id` kommt bereits aus dem Bridge-Dialog, der Kontakt ist damit gewählt, nicht geraten.
2. **Ziel-Sheet-Datei-ID** = der getrimmte Wert **nach** dem Notiz-Marker `POS-SHEET:` auf dem Vertriebler-Kontakt (`registry.md` §4 dokumentiert die Konvention). Das ist die Spreadsheet-ID des aktuellen Vertriebler-Sheets für den Stores-Insert (§8.3).
   - **Kein `POS-SHEET`-Marker** → **fail-closed + Rückfrage** (§9): ohne Ziel-Datei kann die Provisionszeile nicht angelegt werden. Das ist der **einzige** echte Guard dieses Abschnitts.

> **Der Vertriebler-Kontakt ist die Registry.** `POS-SHEET` am Vertriebler ist zugleich das Präsenz-Signal, an dem die `agent-bridge` (`fetchVertriebler()`) alle Vertriebler für die Dialog-Buttons enumeriert — ein neuer Vertriebspartner ist mit gesetzter Notiz sofort sichtbar, ohne Skill-Bump. Die `POS-PARTNER`-Notiz am Store trägt die **Kontakt-UUID** dieses Vertrieblers; `invoice.md` §2 springt darüber zurück auf denselben Kontakt und liest dieselbe Sheet-ID. Beide Domänen teilen damit exakt einen Lookup — kein Verzeichnis-Scan, kein Namensmatch, keine Registry-Tabelle.

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
| `assortment_list` | Assortment-GIDs | §5.3; leer/fehlend → **Feld weglassen** |
| `service_list` | Service-GIDs | §4.5 → §5.3; leer → **Feld weglassen** |
| `highlights` | 2–3 Phrasen, feste Reihenfolge | §4.4; nie generiert, nie aufgefüllt |
| `website` | Website-URL | Places `websiteUri`; **fehlt → Feld weglassen** (Typ `url`, kein Leerstring) |
| `new` | `true` | **Nur im CREATE-Zweig.** Im Heal-Zweig nicht anfassen |
| `tiktok` / `facebook` / `instagram` / `whatsapp` | Social-Handles | Input `socials`, je einzeln optional; fehlend → Feld weglassen |
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

**Vier Felder, die der Agent NIE schreibt:**

- **`featured`** — Geschäftsentscheidung, welcher Store auf der Startseite steht. Niemals Agent, in keinem Zweig, auch nicht `false`.
- **`testimonial_list`** — es gibt keine Quelle, aus der ein Agent Testimonials ziehen dürfte (§10).
- **`opening_hours_holiday`** — Feiertagszeiten pflegt der Mensch; Places' `specialOpeningHours` ist ein rollierendes Fenster, kein Dauerzustand.
- **`image_mood`** — Feld wird aus der Definition entfernt. Nicht schreiben, nicht lesen.

> **`new: true` ist heute eine Einbahnstraße.** Der Agent setzt das Flag bei der Anlage; **niemand** setzt es zurück. Ein Rollover-Prozess ist entschieden, aber nicht gebaut. Bis dahin trägt jeder angelegte Store das Flag dauerhaft — bewusst in Kauf genommen, kein Bug, den ein späterer Lauf hier reparieren soll.
>
> **Im Heal-Zweig bleibt `new` unberührt.** Ein Re-Run auf einen Store, dessen Flag ein Mensch bereits entfernt hat, darf es nicht zurücksetzen.

> **Schicht-2-Hinweis (Security):** Der Store-Write geht über das generische `graphql_mutation` — Schicht 1 (`enabled:false`) trägt hier nicht (`global-agent-framework` §7-Sonderfall). Die tragende Wand ist der **Credential-Scope** des Shopify-Tokens im Vault (nur Metaobjekt-/File-Writes), plus `always_ask` in der Testphase. Der Agent operiert auf extern injiziertem Input — deshalb Token-Scope minimal halten.

#### 8.1.1 `rating`/`rating_count` bei Stores ohne Google-Bewertung

Ein frisch gelisteter Kiosk hat bei Google oft **keine** Bewertung → Places liefert `rating`/`userRatingCount` gar nicht. Dann: `rating_count = 0` und `rating` **weglassen** (nicht `0.0` schreiben, sonst zeigt der Store-Finder eine falsche 0-Sterne-Wertung).

**Drei Zustände, eine Regel.** Places serialisiert Protobuf-JSON und lässt Felder mit Default-Wert **weg** — `userRatingCount = 0` erscheint schlicht nicht in der Antwort. „Google hat keine Zählung" und „die Zählung ist 0" sind für den Agenten daher **nicht unterscheidbar**. Beobachtet wurde außerdem ein `rating` **ohne** `userRatingCount`. Deshalb gilt einheitlich:

> **`rating` wird nur geschrieben, wenn `rating` vorliegt UND `userRatingCount ≥ 1`.** In jedem anderen Fall: `rating` **weglassen**, `rating_count = 0`.

Das kollabiert „kein rating" und „rating ohne count" auf denselben Pfad. Andernfalls schriebe der Agent eine 5-Sterne-Wertung mit null Bewertungen in den Store-Finder — die spiegelverkehrte Variante genau des Fehlers, den der Absatz oben vermeidet. Der Zustand ist wohlgeformt und würde von keinem fail-closed gefangen; er wäre still falsch.

**Build-time verifiziert (erledigt).** Die `liftr_store`-Definition führte `rating`, `testimonial_list`, `product_list` und `collection_list` als Pflichtfelder; alle vier sind auf `required: false` gesetzt. Grund: sie beschreiben, was ein Store *erwirbt*, nicht was ihn *konstituiert* — ein frisch gelisteter Kiosk hat weder Bewertung noch Testimonials und ggf. kein Sortiment. Die Regel bleibt: **niemals** ersatzweise eine erfundene Wertung schreiben. Wird die Definition erneut verschärft, bricht §8.1 fail-closed — das ist gewollt.

### 8.2 Lexware Store-Kontakt + `POS-PARTNER`-Notiz

**find:** Store-Kontakt anhand Name + `postal_code` suchen (`list_contacts`/Suche). **Treffer** (Name + PLZ) → bestehenden Kontakt wiederverwenden (Heal); sicherstellen, dass die Notiz `POS-PARTNER: <vertriebler_contact_id>` gesetzt ist (sonst `update_contact`, `note` als **einziges** geändertes Feld, volles Objekt + `version` mitsenden). **Kein Treffer** → `create_contact` (Rolle `customer`) mit Adresse aus §4.3/Places und `note` = `POS-PARTNER: <vertriebler_contact_id>` (§6).

⚠️ Der Marker-Wert ist die **Kontakt-UUID** des Vertrieblers, **nicht** sein Name. Format exakt `POS-PARTNER: <uuid>` — das Präfix inkl. Doppelpunkt ist ein Vertrag mit dem note-Gate der `agent-bridge` (`registry.md` §4).

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
| Unbekannter Handle (§5.3) | „⚠️ Store-Anlage abgebrochen: Handle `<handle>` existiert nicht als `liftr_service`/`liftr_assortment`." |
| **City kein Treffer** (§5.1) | „⚠️ Store-Anlage abgebrochen: Stadt „<Stadt>" hat keinen `liftr_city`-Eintrag — City zuerst anlegen, dann erneut." |
| **District-Create fehlgeschlagen** (§8.1.0) | „⚠️ Store-Anlage abgebrochen: Bezirk „<Name>" konnte nicht angelegt werden — `<konkreter Fehler>`. **Kein** Store-Write erfolgt." |
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
- **Highlights werden NIE generiert.** Nicht aus `reviews`, `editorialSummary`, `generativeSummary`, `reviewSummary`, `neighborhoodSummary`, nicht aus einer Websuche, nicht aus einem Sprachmodell. Zwei Gründe, beide tragend: Places-Freitext unterliegt Speicherverbot und Attributionspflicht, und ein generierter Satz wäre eine **Behauptung über einen fremden Laden**, die niemand gegenliest. Der Agent wählt aus den festen Phrasen in §4.4 aus — mehr nicht. Auch der Freitext-Slot ist bewusst verworfen: ein leerer dritter Slot kostet nichts, ein falscher Satz kostet den Partner.
- **Keine Testimonials aus Google-Reviews.** Weder kopiert noch umgeschrieben noch zusammengefasst. `testimonial_list` bleibt leer (§8.1).
- **Keine Social-Media-Suche.** Places liefert keine Social-Links; die Google-Business-Profile-API greift nur auf **eigene** Profile. Kommerzielle Anbieter lösen Domain→Social auf — Kioske haben keine Domain. Eine Websuche liefert Kandidaten ohne Verifikation, also Verwechslungsrisiko unter fremdem Namen. Die Handles kommen aus dem Dialog oder gar nicht; `web_search`/`web_fetch` bleiben in der Agent-Config auf `enabled: false`.
- **Kein `priceLevel`.** Googles Preis-Wertung ist nicht die von selectedleafs und steht in keinem Feld der Definition. Nicht in der FieldMask (§3).
- **Keine `liftr_service`- oder `liftr_assortment`-Anlage.** Beide Taxonomien sind geschlossen und kuratiert (14 bzw. 13 Einträge). Unbekannter Handle → fail-closed (§5.3).
- **Keine City-Anlage.** Der erste Store einer neuen Stadt läuft fail-closed (§5.1) — City-Onboarding (Kanal etc.) ist ein eigener, bewusst menschlicher Schritt.
- **Keine Bezirks-Ermittlung im Agenten.** Der Name kommt aus §1. Der Agent geocodiert nicht, ruft keinen externen Kartendienst und liest keine Places-Bezirksfelder (§4.3). Grund: Reverse-Geocoder authentifizieren per Query-String-Key, der Vault injiziert nur in Header/Body — der Agent *kann* sie nicht aufrufen (verifiziert). Der Zug gehört in die `agent-bridge`.
- **Kein Bezirk aus der PLZ.** PLZ und Stadtteil stehen in Deutschland in einer **n:m**-Beziehung, nicht in einer Funktion — `30167` überspannt Nordstadt *und* Teile der Calenberger Neustadt. Jede PLZ→Stadtteil-Tabelle ist eine Schätzung mit eingebauter Fehlerrate. Bewusst verworfen.
- **Kein Bezirk aus Google `addressDescriptor`.** Das Feld ist außerhalb Indiens **pre-GA/experimentell** (keine Kompatibilitätszusage), sein `areas`-Array ist eine ML-geschätzte Containment-Liste (`WITHIN`/`OUTSKIRTS`/`NEAR`), kein 1:1-Bezirk — und es kostet zusätzliche Places-Gebühren. Als Quelle für ein Pflichtfeld mit Create-Autorität bewusst verworfen.
- **Kein Produkt-Picking / keine Collection-Ableitung.** `product_list`/`collection_list` kommen fertig injiziert (§1); die Ableitung geschieht upstream (Bridge/Dialog), nicht hier.
- **Keine USt-ID / Rechtsform.** Bewusst nicht im Flow — manuelle Nachpflege am Lexware-Kontakt.
- **Keine Jahres-Logik fürs Sheet.** Die Ziel-Datei-ID kommt aus `POS-SHEET` (§6); Rollover/Copy-based-Jahreswechsel ist separater (späterer) Prozess.
- **Kein Bridge-/Dialog-Bau.** Der Input-Kontrakt (§1) ist die Schnittstelle; die Bridge, die ihn füllt (inkl. `image_file_id`-Injektion), ist ein eigener Schritt.
