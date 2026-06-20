---
name: selectedleafs-telegram
description: "Produktions- und Posting-Playbook für die lokalen Telegram City-Channels von selectedleafs (Titel-Muster Kratom Stadt selectedleafs.com). Definiert Channel-Setup, Format-System, Message-Typen mit Templates, Emoji-Legende, Pinned-Post-Struktur, Launch-Strategie, Platzhalter-zu-Metaobject-Mapping und Bot-Posting-Format. Use whenever writing, reviewing, or automating Telegram channel posts, setting up a new city channel, building the posting pipeline aus Shopify-Metaobjects, planning a channel launch, oder den Pinned-Post pflegen. Triggers on: telegram, telegram channel, telegram post, kanal, stream post, pinned post, restock post, store update, live finder, telegram template, telegram bot posting, channel setup, channel launch, kratom stadt channel, nachschub post, oeffnungszeiten post."
---

# selectedleafs Telegram — Channel-Playbook

Produktions- und Posting-Playbook für die lokalen Telegram-Channels (Titel-Muster „Kratom [Stadt] | selectedleafs.com").

**Scope:** Channel-Setup, Format, Message-Templates, Pinned-Post, Launch, Bot-Posting.
**Abhängigkeiten:**
- Strategie-Ebene (Channel-Zweck, Settings-Begründungen, Pilot) → `marketing.md` (PK)
- Compliance-Details → `legal.md` (PK)
- Store-Daten → Shopify MCP: `listMetaobjects(type: "liftr_store")`
- Posting-Infrastruktur (Worker, Tools, Deploy) → `infrastructure.md` (PK), Sektion „Telegram MCP Server"
- Automatisierungs-Pipeline → `todos.md` TODO-038

---

## 1. Prinzip

- **Ein Channel pro Stadt** mit aktiven Partner-Stores (Channel + Landingpage spiegeln sich: „Kratom Hannover" ↔ `/hannover`). Erst ab Aktivierungsschwelle einen neuen City-Channel öffnen. Pilot: Hannover (8 Partner, wachsend).
- **Drei Ebenen, klare Rollen:**
  - **Landingpage** = das vollständige, wachsende Store-Verzeichnis (Finder mit allen Stores). Skaliert dort.
  - **Channel-Feed** = Live-Schicht (Stream-Updates).
  - **Pinned** = die Brücke: partnerneutrale Eingangstür, die orientiert und mit einem Tap in den Finder schickt.
- **Reiner Broadcast im Feed, ein privater Rückkanal:** wo / wann / was vorrätig. Kein Direktverkauf, keine Konsum-/Wirkungs-Inhalte. **Direktnachrichten (DM)** sind als *privater* Eingang aktiv (Bestandsmeldungen, §10) — der Feed bleibt Broadcast, **Leerbestand wird nie öffentlich gepostet**, sondern privat gemeldet und positiv als Restock (📦) geschlossen.
- **Realistische Funktion:** Retention-/Reaktivierungs-Layer für lokal gewonnene Spontan-Käufer (Kiosk-QR, Sticker, Landingpage) — **nicht** Telegram-Kaltakquise.

---

## 2. Channel-Setup (pro City-Channel)

| Element | Vorgabe |
|---|---|
| Typ | Öffentlich (Pflicht für Auffindbarkeit) |
| Titel | „Kratom [Stadt] \| selectedleafs.com" — Keyword + Marke |
| Username / t.me | keyword-first: `t.me/kratom_[stadt]` (Fallback `selectedleafs_[stadt]`); sauber, keine Sonderzeichen, kein `.com`, lowercase |
| Profilbild | Marken-Logo 512×512, konsistent über alle City-Channels |
| Beschreibung | **Klartext** (Bio rendert kein Markdown; kein Unicode-Fett → bricht die Suche). Keyword „Kratom kaufen in [Stadt]" vorn, „Räuchermischung" + „ab 18", Link. Max. 255 Zeichen. |
| Reaktionen | nur 👍 ❤️ 🔥 👀 (positiv/neutral; kein Negativ, kein Konsum-Emoji). „Einige Reaktionen" statt „Alle". |
| Kommentare / Diskussionsgruppe | **AUS** (reiner Broadcast) |
| Direktnachrichten | **AN** — privater Admin-Eingang für Bestandsmeldungen („Lücke melden", §10). Gebühr (Stars) = **aus/kostenlos**. Schließt die Diskussionsgruppe aus (Entweder-oder). |
| Weiterleiten & Speichern | **AN** (Forwards = Wachstumshebel) |
| Pretty Link | Shopify URL-Redirect `/[stadt]` → `/pages/kratom-kaufen-[stadt]` (301). SEO-Handle nicht umbenennen. UTM ins Ziel baken: `?utm_source=telegram&utm_medium=channel&utm_campaign=[stadt]`. |

---

## 3. Format-System (alle Stream-Posts)

```
[Emoji] **Headline (1 Zeile)**
{store_name} · {Kontext}

{optionaler Payload-Block}

[Google Maps öffnen]({maps_link})
```

- **Emoji-Präfix** = sofortige Typ-Erkennung.
- **Headline = fett.** Inhalt = die News selbst (Strain, Store), wenn sie in eine Zeile passt — sonst ein Typ-Label („Frisch aufgefüllt", „Öffnungszeiten") und die News kommt in den Payload-Block darunter.
- **`{store_name}` nie fett.** Er steht mager in der Meta-Zeile (`{store_name} · {Kontext}`) — außer der Store *ist* die News (Neuer Partner), dann ist er Teil der fetten Headline und taucht nicht zusätzlich in der Meta auf.
- **Payload-Block** (Liste, Info, Zeit-Zeile) wird mit je einer Leerzeile davor und danach abgesetzt. Entfällt, wenn die News komplett in die Headline passt (Neue Sorte).
- **CTA** = Inline-Link mit Verb, nie roher URL, kein Pfeil-Präfix, Leerzeile davor, kein Underline, Link-Preview aus.
- Keine Headline↔Payload-Dopplung.

---

## 4. Emoji-Legende

| Emoji | Typ / Bedeutung |
|---|---|
| 📦 | Frisch aufgefüllt (Restock) |
| 🌿 | Neue Sorte |
| 🎉 | Neuer Partner (seltener Milestone) |
| 🕒 | Öffnungszeiten / Zeit-Marker |
| 📌 | Pinned (Eingangstür) |
| 📣 | Launch-Post |

---

## 5. Stream-Typen (wiederkehrende Events)

Alle vier folgen dem generischen Format (§3): **Headline fett**, `{store_name}` mager in der Meta-Zeile, Payload als abgesetzter Block wenn die News nicht in die Headline passt, dann CTA.

**📦 Frisch aufgefüllt** — häufigster Typ. „Aufgefüllt", nicht „wieder da".
```
📦 **Frisch aufgefüllt**
{store_name} · {stadtteil}

{Strain} ({Vein}), {Strain} ({Vein}), …

[Google Maps öffnen]({maps_link})
```

**Restock-Regeln (typ-spezifisch):**
- **Headline = Typ-Label** „Frisch aufgefüllt" (fett). Die News ist die Lieferung — eine Liste, die nicht in die Headline passt → sie steht als abgesetzter Block darunter. `{store_name}` mager in der Meta-Zeile.
- **Produkte = flache, kommagetrennte Liste**, jeder Strain mit `(Vein)` inline. Keine Vein-Gruppierung, keine Vein-Circles, kein Tier im Post.
- **Keine Menge, keine Größe** — Verfügbarkeit ist binär.
- **Sortierung: Vein (White → Green → Red), innerhalb nach Tier aufsteigend (€ → €€ → €££).** Das Tier ist nur Sort-Key und wird NICHT angezeigt. Kanonischer Index:

  | Tier | White | Green | Red |
  |------|-------|-------|-----|
  | € | Indo Fusion | Borneo Lift | Suma Sooth |
  | €€ | Suma Rush | Indo Fresh | Borneo Bliss |
  | €££ | Java Spark | Bali Oasis | Bali Sunset |

  Lesereihenfolge = White-Spalte oben→unten, dann Green, dann Red. Eine Lieferung wird nach diesem Index sortiert und flach gerendert (z. B. Java Spark + Indo Fresh + Suma Sooth → „Java Spark (White), Indo Fresh (Green), Suma Sooth (Red)").

**🌿 Neue Sorte** — Strain ist die News, passt komplett in die Headline (kein Payload-Block). Headline-Prefix „Neu:", Vein inline `(Vein)` wie in der Restock-Liste.
```
🌿 **Neu: {sorte} ({vein})**
{store_name} · {stadtteil}

[Google Maps öffnen]({maps_link})
```

**🎉 Neuer Partner** — seltener Milestone; der Store *ist* die News → in der fetten Headline. 🕒-Zeile abgesetzt.
```
🎉 **Neuer Partner: {store_name}**
{stadtteil} · {adresse}

🕒 {oeffnungszeiten}

[Google Maps öffnen]({maps_link})
```

**🕒 Öffnungszeiten** — kurzfristig: heute zu / länger offen / Feiertag. Label-Headline, Info als abgesetzter Block (wie Restock).
```
🕒 **Öffnungszeiten**
{store_name} · {stadtteil}

{kurz_info}

[Google Maps öffnen]({maps_link})
```

---

## 6. Regeln (alle Typen)

- **Strain-Name ja, Größe nein** — außer die Größe ist die News.
- **Keine Menge** — Verfügbarkeit ist binär, nicht numerisch.
- **Keine Hashtags.**
- **Headline = fett, `{store_name}` nie fett.** Die Headline trägt die News (Strain, Store) oder — wenn die News nicht in eine Zeile passt — ein Typ-Label; der Payload (Liste/Info) steht dann abgesetzt darunter. Der Store steht mager in der Meta-Zeile, außer er *ist* die News (Neuer Partner) → dann in der Headline. Gilt für alle vier Typen, kein Sonderfall.
- **Payload abgesetzt:** Liste (Restock), Info (Öffnungszeiten) und die 🕒-Zeile (Neuer Partner) je mit Leerzeile davor und danach. Neue Sorte hat keinen Payload-Block.
- **Restock-Sortierung:** flache Strain-Liste mit `(Vein)`, sortiert Vein (White→Green→Red) → Tier aufsteigend — siehe §5. **Neue Sorte = Strain + Vein.**
- **CTA = Link-Text** („Google Maps öffnen"), Leerzeile davor, kein Pfeil-Präfix, keine Urgency-/„Jetzt"-Floskeln, kein „zugreifen", kein roher URL, **kein Underline** (native Telegram-Linkfarbe), Link-Preview aus.
- Keine Headline↔Payload-Dopplung.
- Ton: warm, lokaler Tipp — kein Shop-Ton, kein Hard-Sell.

---

## 7. Pinned-Post (kanonisch = Live-Stand)

**Quelle der Wahrheit ist das Live-Pinned im Channel, nicht dieses Dokument.** Untenstehende Version ist der aktuelle Live-Stand in `@kratom_hannover` und gilt als kanonisch — bei Abweichung gewinnt der Channel.

**Prinzip:** Lean Welcome als partnerneutrale Eingangstür — **routet nur in den Finder** und trägt den Legal-Anker. KEINE einzelnen Stores, **keine Stadtteil-Liste, keine Emoji-Legende**. Begründung der Arbeitsteilung: Der **Finder** besitzt das Store-Detail (Partner, Öffnungszeiten, Sortiment), der **Feed** besitzt die Wert-Demonstration („was bekomme ich"). Beides muss nicht ins Pinned — das Pinned orientiert und schickt mit einem Tap weiter. Bewusst funktional formuliert, nicht launch-flavored.

```
📌 Kiosk in der Nähe finden

Alle Partner inkl. Öffnungszeiten, Sortiment & Co. findest du hier: selectedleafs.com/[stadt]

Verkauf ab 18 · Nicht für den menschlichen Verzehr geeignet
```

- **Headline ohne Stadt** — die Stadt steckt in der URL-Zeile darunter.
- **Routing-only:** genau ein Ziel (der Finder). Kein Store-Detail, keine Wert-Demo, keine Sub-Listen — die gehören in Finder bzw. Feed (siehe Prinzip).
- **URL-Zeile** = Landingpage-Link. Pinned zeigt bewusst die Telegram-Linkvorschau der Landingpage (Landingpage-Karte als Hero) — **Link-Preview hier NICHT unterdrücken**, anders als bei Stream-Posts.
- **Legal-Anker** „Verkauf ab 18 · Nicht für den menschlichen Verzehr geeignet" einmal im Footer.

**Pinned-Struktur (Launch vs. Steady-State):**
- **Beim Launch = 2 Elemente:** Welcome (Dauer-Pin) + Attributions-Poll (temporär gepinnt, am Ende der Pilot-Laufzeit entpinnt).
- **Steady-State = nur Welcome.**

**Launch-Variante:** In der Startphase eine Zeile ergänzen wie „Frisch gestartet — ab jetzt regelmäßige Updates.", damit ein dünner Feed als *neu* statt *tot* liest. Sobald der Channel läuft, wieder rausnehmen.

**Bot kann das Pinned editieren — verifiziert 2026-05-30:** Auch wenn die Welcome-Nachricht von Joschas Account stammt, ändert der Admin-Bot sie per `edit_message` problemlos (real getestet). In Channels zählt das Admin-Recht „Nachrichten bearbeiten", nicht die Autorschaft. **Kein Handover / kein Repost nötig** — die Welcome bleibt bei URL-/Textänderungen editierbar.

> ⚠️ Der `get_pinned`-Output behauptet fälschlich „Absender = Nicht-Bot → kann NICHT editieren". Das ist eine falsche Heuristik im Worker (prüft `from.is_bot`) — **ignorieren**. Fix offen: Wording in `get_pinned` korrigieren (Worker).

### 7.1 Pin-Reihenfolge (verifiziert)

Telegram zeigt in der Pin-Leiste **immer den zuletzt gepinnten Post**; ältere Pins sind nur per Tap auf die Leiste erreichbar. **Priorität ≠ Pin-Zeitpunkt** — der wichtigste Pin muss als *letzter* gesetzt werden, nicht als erster.

- **Welcome zuletzt pinnen**, damit er die Leiste hält.
- Wird der Attributions-Poll dazugepinnt, **danach den Welcome erneut pinnen** — sonst übernimmt der Poll die Leiste.
- **Live-Beleg (@kratom_hannover):** Poll zuerst gepinnt, Welcome zuletzt → Welcome steht in der Leiste, Poll liegt als älterer Pin dahinter. `get_pinned` liefert entsprechend die Welcome-Nachricht (zuletzt gepinnt), nicht den Poll.

### 7.2 Attributions-Poll (Launch-Element)

Temporäres Pilot-Element, nur während der Launch-/Pilot-Laufzeit gepinnt; danach entpinnt (Steady-State = nur Welcome).

- **Zweck:** Pilot-Metrik — **organische vs. eingeladene Discovery** (TODO-038). Frage im Sinne von „Wie hast du den Kanal gefunden?"; misst, über welchen Pfad Abonnenten kommen.
- **Anonym** (Telegram-Poll-Einstellung).
- **Harter Telegram-Fakt:** Ein Poll ist **nach dem Absenden nicht editierbar** (nur stoppbar). Optionen also **vorab final festlegen** — eine Korrektur heißt: Poll stoppen und neu bauen.
- **Poll-Design-Prinzip (Pflicht-Buckets):** Die Optionen **müssen den primären organischen Pfad abdecken — Kiosk-QR / Aufkleber — plus einen „direkt eingeladen"-Bucket** (Admin-/Direkt-Einladung). Fehlt der Kiosk-Bucket, landen Kiosk-Scanner im falschen Topf und die Metrik (organisch vs. eingeladen) ist verfälscht. Weitere organische Pfade (persönliche Empfehlung, Landingpage-Link, Telegram-Suche, weitergeleitete Nachricht) sind sinnvoll zu ergänzen; **exakter Wortlaut und Reihenfolge leben im Channel**, nicht hier (Poll = nicht editierbar, Live ist kanonisch).

---

## 8. Launch-Strategie

**Nicht fake-füllen — seeden + Reihenfolge steuern.**

- **KEINE Bulk-„Neuer Store"-Posts** zum Auffüllen: faktisch falsch (Stores sind nicht neu), verbrennt den 🎉-Milestone, sieht nach Dump aus.
- **Seeding (ehrlich):**
  1. Ein einmaliger **Launch-Post** (Erwartung setzen).
  2. **Echte Events ab Tag 1** — bei 8 aktiven Kiosken füllt sich der Feed in Tagen organisch.
- **Sequencing:** erst ein paar Posts rein + Pinned ab Tag 1 + Finder (`/[stadt]` + Landingpage) live → **dann** den Link verteilen. So trifft kein Besucher auf einen leeren Channel.
- Gestaffelt statt am Stück (8 Posts zur selben Minute wirken unecht).

**Launch-Post (einmalig):** Foto + Caption, einmal pro Stadt. **Manuell gepostet** — der Worker kann nur Text (`post_message`/`sendMessage`); `sendPhoto` ist nicht implementiert und für einen Einmal-Post unnötig.
```
[Bild: Stadt-Landmark, gebrandet mit Logo-Overlay — Hannover: Neues Rathaus]
**JETZT LIVE: Dein Update-Channel rund um Kratom in 📍 [Stadt]**
Ab sofort halten wir dich hier bequem auf dem Laufenden. Du erfährst in Echtzeit alles über:

📦 Lieferungen
🌿 Neue Sorten
🎉 Neue Partner
🕒 Öffnungszeiten

…und vieles mehr.
```

- **Bild = Hero.** Pro Stadt ein eigenes, erkennbares **Stadt-Landmark** (Hannover: Neues Rathaus), gebrandet mit dem Logo-Overlay — **NICHT das Produkt-Mockup** (würde Richtung Produkt-/Verkaufs-Framing kippen). Liefert lokale Identität, Feed-Präsenz und Forward-Gewicht (§2).
- **Kein 📣** in der Headline — das Bild trägt das visuelle Gewicht.
- **📍 (Standort-Pin), nicht 📌.** 📌 ist in §4 für „Pinned" reserviert; 📍 hält die Bedeutung (Ort vs. angepinnt) getrennt.
- **Kein Link.** Der Weg zu den Stores liegt bereits in der **Channel-Beschreibung** und im **Pinned** — der Launch-Post doppelt die Eingangstür nicht.
- **Teasert alle vier Stream-Typen** (📦 zuerst = häufigster Typ) = die Wert-Demonstration („was bekomme ich"), die laut §7 bewusst nicht ins Pinned, sondern in den Feed gehört. Der Launch-Post ist ihre Eröffnung und bringt nebenbei die Emoji-Legende (§4) unter die Leute.
- **Launch-Ausnahme von §6:** „JETZT LIVE" / „in Echtzeit" sind hier okay (das ist die Aufgabe des Posts). Was bleibt hart: **keine Wirkungsangaben**, kein Link. „…und vieles mehr." ist optionales Füllsel — bei Bedarf streichen.

---

## 9. Platzhalter → `liftr_store`-Metaobject

| Platzhalter | Feld |
|---|---|
| `{store_name}` | `name` |
| `{stadtteil}` | `district` → `.name` (GID auflösen) |
| `{stadtteile}` | alle `district`-Namen, dedupliziert (für Pinned-Reassurance) |
| `{adresse}` | `adress` |
| `{oeffnungszeiten}` | `opening_hours` |
| `{rating}` / `{rating_count}` | `rating` → `.value` / `rating_count` |
| `{maps_link}` | `google_place` → Maps-URL: `https://www.google.com/maps/search/?api=1&query={name}&query_place_id={place_id}` (in HTML jedes `&` → `&amp;`) |
| `{sorte}` / `{vein}` | aus `product_list` / Lieferschein / manuell |

---

## 10. Bot-Posting / Automatisierung

- **Fett + Inline-Links nur in Nachrichten** — nicht in Titel, Username oder Beschreibung.
- Bot-API: `parse_mode = HTML` (Default) oder `MarkdownV2`. Inline-Link in HTML: `<a href="…">Text</a>`. **HTML statt MarkdownV2**, weil MarkdownV2 `.`, `-`, `(`, `)` etc. escapen müsste → bricht in Adressen/Maps-Links ständig.
- **Auslöser je Stream-Typ:**
  - 📦 Frisch aufgefüllt → JTL-Lieferung (Übergabeprotokoll), siehe unten
  - 🌿 Neue Sorte → Änderung `product_list` bzw. neue Sorte auf dem Lieferschein
  - 🎉 Neuer Partner → neues `liftr_store`-Metaobject (Chat-getrieben)
  - 🕒 Öffnungszeiten → Änderung `opening_hours`; spontane manuell
- Launch (§8) = manuell/redaktionell.
- Posting läuft über den **Telegram MCP Worker** (`infrastructure.md` → „Telegram MCP Server"): Tools `post_message` / `edit_message` / `pin_message` / `get_pinned`. Mensch-im-Loop: Entwurf zeigen → bestätigen → posten.
- Pipeline-Aufbau → `todos.md` TODO-038.

### Restock aus JTL-Übergabeprotokoll (Schritt für Schritt)

Häufigster Echtfall. **Trigger ist die Lieferung in JTL, nicht Shopify** — Shopify sieht den Kiosk-Nachschub nicht. Lieferschein wird hochgeladen, Post entsteht halb-manuell mit Review.

1. **PDF parsen:** Empfänger = Store-Name. Je Position: Strain aus der Artikelbezeichnung (z. B. „Indo Fusion 25g" → „Indo Fusion"), **Vein aus der Subzeile** (z. B. „White Kratom" → White). Größe und Menge ignorieren.
2. **Store auflösen:** Store-Name → `liftr_store`-Metaobject (Name-Match, kein gespeichertes Mapping). Bei Abweichung (JTL-Rechnungsname ≠ Storefront-Name) Bestätigungszeile zeigen.
3. **Felder ziehen:** `district` → Stadtteil (GID auflösen, NICHT aus PLZ raten), `google_place` → Maps-Link.
4. **Channel ableiten:** Stadt → `kratom_[stadt]` (lowercase).
5. **Typ entscheiden:** Strain in `product_list` des Stores? → 📦 Restock. Nicht enthalten? → 🌿 Neue Sorte.
6. **Posten:** Template aus §5, `parse_mode=HTML`, `&` in der Maps-URL als `&amp;` escapen, Link-Preview aus. Vor dem Absenden Store + Stadt + Channel + Entwurf zur Bestätigung zeigen.

### Restock aus Kundenmeldung (Direktnachricht)

Zweiter Restock-Pfad neben dem JTL-Protokoll — crowdgesourct über die **Direktnachrichten**-Funktion (§2). Schließt die Lücke, dass Partner Ausverkäufe nicht selbst melden und Christian nur ~1×/Woche vor Ort ist.

**Loop:** Kunde meldet leeres Regal per DM → du/Christian triagiert + verifiziert → Christian füllt nach → 📦-Post (§5) schließt den Loop sichtbar. Der Melder sieht „seine" Lücke geschlossen = die eigentliche Belohnung.

**Regeln:**
- **Mensch-im-Loop, keine Automatik.** Die DM ist ein *Input* in Christians Restock-Workflow, kein Ersatz — die Meldung fließt zu Christian, nicht an ihm vorbei.
- **Leerbestand wird NIE öffentlich gepostet** (kein Mangel-/Scarcity-Framing, §6). Nur die positive Auffüllung (📦) geht in den Feed.
- **Belohnung:** v1 **ohne Cash**. Falls später ein Reward → nur für *verifizierte* Lücken, erster Melder pro Store/Sorte/Woche (Gaming-Schutz).
- **Partner-Buy-in zuerst:** als Service am Partner framen („Kunden helfen, dein Regal voll zu halten"), nicht als Kontrolle. Vor Rollout mit dem Partner klären (Mehmet besonders heikel).

**Bewerbung der Meldefunktion:**
- **Einmaliger Feed-Teach-Post** erklärt sie („Siehst du ein leeres Regal, schreib uns kurz."). Das ist Wert-Demo → gehört in den **Feed, nicht ins Pinned** (§7 bleibt routing-only). Ton: positiv-mitmachen, B1, kein Druck, keine Wirkung.
- **Timing:** nicht zur Launch-Minute — erst in den Pilot hinein, wenn eine Abonnentenbasis existiert und jemand realistisch schon vor einem leeren Regal stand.
- **Standing-Affordance:** der DM-Button selbst (Button-Text ist Telegram-vorgegeben, nicht anpassbar). Bleiben Meldungen aus, einmal nachfassen statt sofort eine Kadenz zu bauen.

---

## 11. Legal-Anker

- Anker (**ab 18 · Kratom als Räuchermischung**) steht **einmal** im Pinned-Footer; Stream-Posts bleiben reine Logistik.
- Keine Wirkungsangaben, keine Mengen/Scarcity, keine Konsum-Inhalte. Details → `legal.md`.

---

## Changelog

| Datum | Änderung |
|-------|----------|
| 2026-06-01 | v13 (Direktnachrichten live): Feature integriert. §1 um privaten Rückkanal ergänzt (Feed bleibt Broadcast, Leerbestand nie öffentlich). §2 neue Setup-Zeile **„Direktnachrichten = AN"** (privater Bestandsmeldungs-Eingang, Gebühr aus, schließt Diskussionsgruppe aus — Entweder-oder). §10 neue Subsektion **„Restock aus Kundenmeldung (Direktnachricht)"**: Loop (DM → Triage → Christian → 📦), Mensch-im-Loop, kein öffentlicher Stock-out, v1 ohne Cash + Gaming-Schutz, Partner-Buy-in, Bewerbung via einmaligem Feed-Teach-Post (nicht Pinned). |
| 2026-05-31 | v12 (Hannover-Launch-Post live, kanonisch): §8 Launch-Post auf **Foto + Caption** umgestellt (vorher Text-only). Hero = gebrandetes **Stadt-Landmark** (Hannover: Neues Rathaus), pro Stadt eigenes Bild, nicht das Produkt-Mockup. Headline final **„JETZT LIVE: Dein Update-Channel rund um Kratom in 📍 [Stadt]"** — kein 📣 (Bild trägt das Gewicht), 📍 statt 📌 (📌 = Pinned, §4). Liste auf reine Labels gekürzt, **📦 zuerst** (häufigster Typ). „…und vieles mehr." als optionaler Abschluss. **Manuell posten** (Worker text-only, `sendPhoto` nicht implementiert). §6-Launch-Ausnahme explizit: „JETZT LIVE"/„in Echtzeit" hier erlaubt, Wirkungsangaben + Link bleiben tabu. |
| 2026-05-31 | v11: §8 Launch-Post neu gefasst. **Landingpage-Link raus** — Channel-Beschreibung und Pinned besitzen den Weg zu den Stores schon, der Launch-Post doppelt ihn nicht. Stattdessen **teasert er alle vier Stream-Typen** (📦/🌿/🎉/🕒 mit je einer Erklärzeile) = die Wert-Demo, die laut §7 bewusst nicht ins Pinned, sondern in den Feed gehört; bringt nebenbei die Emoji-Legende (§4) unter die Leute. „Store" → „Kiosk" (Consumer-Sprache wie Lean Welcome). Pfeil-Präfix + roher URL entfallen damit ohnehin. |
| 2026-05-31 | v10: Store-Spotlight (alt §9) **ersatzlos gestrichen** und als IDEA nach `ideas.md` ausgelagert. Begründung: Launch-Dichte-Zweck mit dem Live-Launch erledigt (Feed füllt sich organisch über Restocks), Steady-State-Zweck schwach + Audience-Mismatch (Consumer-Channel vs. B2B-Goodwill) + Compliance-Drift-Risiko + einziger nicht-automatisierbarer Typ (gegen TODO-038). Folgeänderungen: §1 Feed-Rolle „+ Editorial-Spotlights" raus; §4 📣 = nur noch „Launch-Post"; §8 Seeding-Schritt „Store-Spotlight-Reihe" raus (Schritte neu nummeriert); §10 (alt §11) „Editorial (§9)"-Verweis raus; Sektionen ab §10 neu nummeriert (alt §10/§11/§12 → §9/§10/§11); Trigger „store spotlight" aus der Description entfernt. Reaktivierung aus `ideas.md` mit konkretem Trigger möglich, falls Thin-Feed-Problem real wird. |
| 2026-05-31 | v9 (Hannover-Launch live): §7 an den Live-Stand angeglichen. Template ersetzt durch **lean Welcome** — routet nur in den Finder + Legal-Anker; **Stadtteil-Liste mit Zählern und Emoji-Legende raus** (Finder besitzt das Store-Detail, Feed besitzt die Wert-Demo → beides nicht ins Pinned). „Quelle der Wahrheit = Channel" bleibt. **Pinned-Struktur dokumentiert:** Launch = 2 Elemente (Welcome Dauer-Pin + temporär gepinnter Attributions-Poll), Steady-State = nur Welcome. **Neu §7.1 Pin-Reihenfolge:** Telegram zeigt den zuletzt gepinnten Post → Welcome zuletzt pinnen (Priorität ≠ Pin-Zeitpunkt); beim Dazupinnen des Polls Welcome neu pinnen. **Neu §7.2 Attributions-Poll:** Pilot-Metrik (TODO-038), anonym, temporär; Poll nach Absenden nicht editierbar → Optionen vorab final; Pflicht-Buckets Kiosk-QR/Aufkleber + „direkt eingeladen". Bot-Edit-Notiz auf den lean Welcome umgeschrieben (Stadtteil-Zähler-Beispiel obsolet). §9 unverändert. |
| 2026-05-31 | v8 (TODO-043): Stream-Format vereinheitlicht — alle vier Typen folgen jetzt §3. Bold-Regel universell: **Headline fett, `{store_name}` nie fett** (Store mager in der Meta-Zeile; nur bei Neuer Partner *ist* der Store die News → in der fetten Headline). v7-Restock-Detail mitgeflippt (vorher Label mager + Store fett → jetzt Label fett + Store mager). Payload-Block-Muster: Liste (Restock), Info (Öffnungszeiten) und 🕒-Zeile (Neuer Partner) mit Leerzeilen abgesetzt; Neue Sorte ohne Block. Neue Sorte: Headline-Prefix „Neu:" (Satzschreibung, kein „NEU:"/Shop-Ton), Vein inline `(Vein)` statt in der Meta-Zeile. §3-Abweichungsnote entfernt (Deviation aufgelöst). §4 unverändert. |
| 2026-05-31 | v7: Restock-Template (§5) neu — flache, kommagetrennte Strain-Liste mit `(Vein)` inline statt Vein-Summary/Einzelposten-Logik. Headline = reines Typ-Label, Store-Name fett in Meta-Zeile (`**{store_name}** · {stadtteil}`). Sortierung Vein (White→Green→Red) → Tier aufsteigend (Sort-Key, NICHT angezeigt); kanonischer 9-Strain-Index ergänzt. Kein Tier, keine Circles im Post. CTA ohne Underline, Link-Preview aus (§6). `{vein_summary}` aus §10 entfernt. Abweichung vom generischen §3-Format vermerkt; Angleichung der übrigen Stream-Typen offen → TODO-043. |
| 2026-05-30 | v6: Verifiziert — Bot kann das Pinned (msg 9, Account-Absender) per `edit_message` editieren; in Channels zählt das Admin-Recht, nicht Autorschaft. Handover hinfällig (§7). `get_pinned`-Heuristik („Nicht-Bot → kann nicht editieren") als falsch markiert (Worker-Fix offen). |
| 2026-05-30 | v5: §7 an den Live-Stand angeglichen (kanonisch = Live-Pinned „Stores & Öffnungszeiten" mit Stadtteil-Zählern + Emoji-Legende + Legal-Anker „Verkauf ab 18 · Nicht für den menschlichen Verzehr geeignet"). Frühere „Option B / keine Counts"-Fassung war veraltet. Quelle der Wahrheit = Channel, nicht Dokument. |
| 2026-05-30 | v4: CTA auf „Google Maps öffnen" geändert; Leerzeile zwischen Body und CTA eingeführt (§3/§5/§6). |
| 2026-05-30 | v3: Worker live & getestet (`selectedleafs-telegram-mcp`, 4 Tools, `get_pinned` + `post_message` real geprüft). CTA auf „Wegbeschreibung zeigen" festgelegt, Pfeil-Präfix raus (§3/§5/§6); Urgency-/„Jetzt"-Verbot in §6 wieder aufgenommen. Einzelposten-Regel ergänzt (§6: Strain (Vein) bei einer Position, sonst Vein-Summary). Prozedur „Restock aus JTL-Übergabeprotokoll" ergänzt (§11). Maps-URL-Format + HTML-Escaping in §10/§11 fixiert. Pinned-Count-Divergenz + Handover in §7 vermerkt. |
| 2026-05-30 | v2: Pinned auf Option B umgestellt (partnerneutral, Karten-Finder primär, keine Einzel-Stores, kein Featured Store — gelockt für 8+ Partner/wachsend). Launch-Sektion (§8) ergänzt. Store-Spotlight (§9) als Editorial-Typ beschlossen, Inhalt/Gestaltung offen. Emoji-Legende um 📣 erweitert. |
| 2026-05-30 | v1: Channel-Setup, Format-System, 4 Stream-Templates, Pinned-Stand, Mapping, Bot-Posting. |
