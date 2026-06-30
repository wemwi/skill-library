# Telegram — generisches Channel-Handwerk

Generisches Produktions- und Posting-Playbook für die lokalen selectedleafs-Telegram-Channels (Titel-Muster „Kratom [Stadt] | selectedleafs.com"). Diese reference trägt das **Handwerk** — Channel-Lifecycle/Setup, Format-System, Posting-Mechanik, Pinned/Launch. **Domänen-spezifische Post-Templates leben in der jeweiligen Domänen-reference**, nicht hier:

- **📦 Frisch aufgefüllt / 🌿 Neue Sorte** → `references/restock.md` (Sektion „Restock-Post-Templates"). Die Restock-Kette braucht diese reference **nicht** — sie hat ihre Templates lokal.
- **🎉 Neuer Partner** → gehört zur Launch-Domäne (`references/launch.md`); solange die ein Stub ist, steht das Template übergangsweise unten in §5 (markiert).

**Werte (IDs, Maps, chat_ids) stehen nicht hier**, sondern in `references/registry.md` (Channel-Map, Operations-Chat) bzw. kommen lauf-spezifisch aus der Webhook-Injektion. Diese reference beschreibt **Regeln**, nicht Werte.

---

## 1. Prinzip

- **Ein Channel pro Stadt** mit aktiven Partner-Stores (Channel + Landingpage spiegeln sich: „Kratom Hannover" ↔ `/hannover`). Erst ab Aktivierungsschwelle einen neuen City-Channel öffnen.
- **Drei Ebenen, klare Rollen:**
  - **Landingpage** = das vollständige, wachsende Store-Verzeichnis (Finder mit allen Stores). Skaliert dort.
  - **Channel-Feed** = Live-Schicht (Stream-Updates).
  - **Pinned** = die Brücke: partnerneutrale Eingangstür, die orientiert und mit einem Tap in den Finder schickt.
- **Reiner Broadcast im Feed, ein privater Rückkanal:** wo / wann / was vorrätig. Kein Direktverkauf, keine Konsum-/Wirkungs-Inhalte. **Direktnachrichten (DM)** sind als *privater* Eingang aktiv (Bestandsmeldungen) — der Feed bleibt Broadcast, **Leerbestand wird nie öffentlich gepostet**, sondern privat gemeldet und positiv als Restock (📦) geschlossen.
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
| Direktnachrichten | **AN** — privater Admin-Eingang für Bestandsmeldungen („Lücke melden"). Gebühr (Stars) = **aus/kostenlos**. Schließt die Diskussionsgruppe aus (Entweder-oder). |
| Weiterleiten & Speichern | **AN** (Forwards = Wachstumshebel) |
| Pretty Link | Shopify URL-Redirect `/[stadt]` → `/pages/kratom-kaufen-[stadt]` (301). SEO-Handle nicht umbenennen. UTM ins Ziel baken: `?utm_source=telegram&utm_medium=channel&utm_campaign=[stadt]`. |

Die **Stadt selbst** kommt nie aus einer Belegadresse, sondern aus dem Store-Metaobjekt (redaktionelle Zuordnung — ein Store in Wunstorf kann dem Hannover-Channel zugeordnet sein). Die Auflösung Store → Stadt liegt in der jeweiligen Domänen-reference (restock §2.5), nicht hier. Der Channel selbst (City → `chat_id`/Username) ist ein direkter Lookup in `references/registry.md` §1 — keine Ableitungslogik, kein Override-Mechanismus.

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
- **Payload-Block** (Liste, Info, Zeit-Zeile) wird mit je einer Leerzeile davor und danach abgesetzt. Entfällt, wenn die News komplett in die Headline passt.
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

## 5. Stream-Typen & Template-Verortung

Alle Typen folgen dem generischen Format (§3): **Headline fett**, `{store_name}` mager in der Meta-Zeile, Payload als abgesetzter Block wenn die News nicht in die Headline passt, dann CTA.

**Template-Verortung:**
- **📦 Frisch aufgefüllt** und **🌿 Neue Sorte** → vollständige Templates + Restock-Regeln + kanonischer 9-Strain-Index in `references/restock.md` (die Domäne, die sie erzeugt).
- **🎉 Neuer Partner** → Launch-Domäne (`references/launch.md`, derzeit Stub). Template übergangsweise unten.
- **🕒 Öffnungszeiten** → generisches Store-Update, derzeit ohne eigene Domänen-reference; Template unten.

### 🎉 Neuer Partner (übergangsweise hier — Ziel: launch.md)

Seltener Milestone; der Store *ist* die News → in der fetten Headline. 🕒-Zeile abgesetzt.
```
🎉 **Neuer Partner: {store_name}**
{stadtteil} · {adresse}

🕒 {oeffnungszeiten}

[Google Maps öffnen]({maps_link})
```

### 🕒 Öffnungszeiten

Kurzfristig: heute zu / länger offen / Feiertag. Label-Headline, Info als abgesetzter Block.
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
- **Headline = fett, `{store_name}` nie fett.** Die Headline trägt die News (Strain, Store) oder — wenn die News nicht in eine Zeile passt — ein Typ-Label; der Payload (Liste/Info) steht dann abgesetzt darunter. Der Store steht mager in der Meta-Zeile, außer er *ist* die News (Neuer Partner) → dann in der Headline.
- **Payload abgesetzt:** Liste, Info und Zeit-Zeile je mit Leerzeile davor und danach.
- **CTA = Link-Text** („Google Maps öffnen"), Leerzeile davor, kein Pfeil-Präfix, keine Urgency-/„Jetzt"-Floskeln, kein „zugreifen", kein roher URL, **kein Underline** (native Telegram-Linkfarbe), Link-Preview aus.
- Keine Headline↔Payload-Dopplung.
- Ton: warm, lokaler Tipp — kein Shop-Ton, kein Hard-Sell.

---

## 7. Pinned-Post (kanonisch = Live-Stand)

**Quelle der Wahrheit ist das Live-Pinned im Channel, nicht dieses Dokument.** Untenstehende Version ist der Live-Stand in `@kratom_hannover` und gilt als kanonisch — bei Abweichung gewinnt der Channel.

**Prinzip:** Lean Welcome als partnerneutrale Eingangstür — **routet nur in den Finder** und trägt den Legal-Anker. KEINE einzelnen Stores, **keine Stadtteil-Liste, keine Emoji-Legende**. Arbeitsteilung: Der **Finder** besitzt das Store-Detail (Partner, Öffnungszeiten, Sortiment), der **Feed** besitzt die Wert-Demonstration („was bekomme ich"). Beides muss nicht ins Pinned — das Pinned orientiert und schickt mit einem Tap weiter.

```
📌 Kiosk in der Nähe finden

Alle Partner inkl. Öffnungszeiten, Sortiment & Co. findest du hier: selectedleafs.com/[stadt]

Verkauf ab 18 · Nicht für den menschlichen Verzehr geeignet
```

- **Headline ohne Stadt** — die Stadt steckt in der URL-Zeile darunter.
- **Routing-only:** genau ein Ziel (der Finder). Kein Store-Detail, keine Wert-Demo, keine Sub-Listen.
- **URL-Zeile** = Landingpage-Link. Pinned zeigt bewusst die Telegram-Linkvorschau der Landingpage (Landingpage-Karte als Hero) — **Link-Preview hier NICHT unterdrücken**, anders als bei Stream-Posts.
- **Legal-Anker** „Verkauf ab 18 · Nicht für den menschlichen Verzehr geeignet" einmal im Footer.

**Pinned-Struktur (Launch vs. Steady-State):**
- **Beim Launch = 2 Elemente:** Welcome (Dauer-Pin) + Attributions-Poll (temporär gepinnt, am Ende der Pilot-Laufzeit entpinnt).
- **Steady-State = nur Welcome.**

**Launch-Variante:** In der Startphase eine Zeile ergänzen wie „Frisch gestartet — ab jetzt regelmäßige Updates.", damit ein dünner Feed als *neu* statt *tot* liest. Sobald der Channel läuft, wieder rausnehmen.

**Bot kann das Pinned editieren — verifiziert 2026-05-30:** Auch wenn die Welcome-Nachricht von Joschas Account stammt, ändert der Admin-Bot sie per `edit_message` problemlos. In Channels zählt das Admin-Recht „Nachrichten bearbeiten", nicht die Autorschaft. **Kein Handover / kein Repost nötig.**

> ⚠️ Der `get_pinned`-Output behauptet fälschlich „Absender = Nicht-Bot → kann NICHT editieren". Das ist eine falsche Heuristik im Worker (prüft `from.is_bot`) — **ignorieren**. Fix offen.

### 7.1 Pin-Reihenfolge (verifiziert)

Telegram zeigt in der Pin-Leiste **immer den zuletzt gepinnten Post**; ältere Pins sind nur per Tap auf die Leiste erreichbar. **Priorität ≠ Pin-Zeitpunkt** — der wichtigste Pin muss als *letzter* gesetzt werden.

- **Welcome zuletzt pinnen**, damit er die Leiste hält.
- Wird der Attributions-Poll dazugepinnt, **danach den Welcome erneut pinnen** — sonst übernimmt der Poll die Leiste.

### 7.2 Attributions-Poll (Launch-Element)

Temporäres Pilot-Element, nur während der Launch-/Pilot-Laufzeit gepinnt; danach entpinnt (Steady-State = nur Welcome).

- **Zweck:** Pilot-Metrik — **organische vs. eingeladene Discovery**. Frage im Sinne von „Wie hast du den Kanal gefunden?".
- **Anonym** (Telegram-Poll-Einstellung).
- **Harter Telegram-Fakt:** Ein Poll ist **nach dem Absenden nicht editierbar** (nur stoppbar). Optionen also **vorab final festlegen** — eine Korrektur heißt: Poll stoppen und neu bauen.
- **Poll-Design-Prinzip (Pflicht-Buckets):** Die Optionen **müssen den primären organischen Pfad abdecken — Kiosk-QR / Aufkleber — plus einen „direkt eingeladen"-Bucket**. Fehlt der Kiosk-Bucket, landen Kiosk-Scanner im falschen Topf und die Metrik ist verfälscht. **Exakter Wortlaut und Reihenfolge leben im Channel** (Poll = nicht editierbar, Live ist kanonisch).

---

## 8. Launch-Strategie (Channel-Launch)

Betrifft den **Channel-Start einer Stadt** — nicht das Onboarding eines neuen POS-Partners (das ist die Launch-Domäne, `references/launch.md`).

**Nicht fake-füllen — seeden + Reihenfolge steuern.**

- **KEINE Bulk-„Neuer Store"-Posts** zum Auffüllen: faktisch falsch (Stores sind nicht neu), verbrennt den 🎉-Milestone, sieht nach Dump aus.
- **Seeding (ehrlich):**
  1. Ein einmaliger **Launch-Post** (Erwartung setzen).
  2. **Echte Events ab Tag 1** — bei genügend aktiven Kiosken füllt sich der Feed in Tagen organisch.
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

- **Bild = Hero.** Pro Stadt ein eigenes, erkennbares **Stadt-Landmark**, gebrandet mit Logo-Overlay — **NICHT das Produkt-Mockup** (würde Richtung Produkt-/Verkaufs-Framing kippen).
- **Kein 📣** in der Headline — das Bild trägt das visuelle Gewicht.
- **📍 (Standort-Pin), nicht 📌.** 📌 ist für „Pinned" reserviert.
- **Kein Link.** Der Weg zu den Stores liegt bereits in Channel-Beschreibung und Pinned.
- **Teasert alle vier Stream-Typen** (📦 zuerst = häufigster Typ) = Wert-Demonstration, bringt nebenbei die Emoji-Legende unter die Leute.
- **Launch-Ausnahme von §6:** „JETZT LIVE" / „in Echtzeit" sind hier okay. Hart bleibt: **keine Wirkungsangaben**, kein Link.

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

## 10. Bot-Posting / Posting-Mechanik

- **Fett + Inline-Links nur in Nachrichten** — nicht in Titel, Username oder Beschreibung.
- Bot-API: `parse_mode = HTML` (Default). Inline-Link in HTML: `<a href="…">Text</a>`. **HTML statt MarkdownV2**, weil MarkdownV2 `.`, `-`, `(`, `)` etc. escapen müsste → bricht in Adressen/Maps-Links ständig.
- **Maps-URL:** `&` → `&amp;`, Link-Preview aus (außer im Pinned, §7).
- Posting läuft über die Telegram-Post-Tools (`post_message` / `edit_message` / `pin_message` / `get_pinned`). Tool-Oberfläche, Permission und Worker-Mechanik sind build-time (`global-agent-framework`), nicht hier.
- **Auslöser je Stream-Typ** (das *Wie* des Parsens/Postens liegt in der jeweiligen Domänen-reference):
  - 📦 Frisch aufgefüllt → Lieferung/Übergabeprotokoll → `references/restock.md`
  - 🌿 Neue Sorte → neue Sorte auf dem Beleg bzw. `product_list`-Änderung → `references/restock.md`
  - 🎉 Neuer Partner → neues `liftr_store`-Metaobject (Chat-getrieben) → `references/launch.md`
  - 🕒 Öffnungszeiten → Änderung `opening_hours`; spontane manuell

### 10.1 Privater Rückkanal (DM) — Restock-Input

Die DM-Funktion (§2) ist ein **Input** in den Restock-Workflow, kein Ersatz: Kunde meldet leeres Regal per DM → Mensch triagiert/verifiziert → Partner füllt nach → 📦-Post schließt den Loop sichtbar. **Mensch-im-Loop, keine Automatik.** **Leerbestand wird NIE öffentlich gepostet** — nur die positive Auffüllung (📦) geht in den Feed. Bewerbung der Meldefunktion über einen einmaligen Feed-Teach-Post (nicht ins Pinned), erst in den Pilot hinein, wenn eine Abonnentenbasis existiert.

---

## 11. Legal-Anker

- Anker (**ab 18 · Kratom als Räuchermischung**) steht **einmal** im Pinned-Footer; Stream-Posts bleiben reine Logistik.
- Keine Wirkungsangaben, keine Mengen/Scarcity, keine Konsum-Inhalte.

---

*Externe Strategie-/Compliance-Tiefe (Channel-Zweck, Pilot-Begründung, Compliance-Details) lebt im Project-Knowledge (`marketing.md` / `legal.md`) und ist nicht Teil dieser reference.*
