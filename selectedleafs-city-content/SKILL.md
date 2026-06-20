---
name: selectedleafs-city-content
description: "Content-Strategie und Textproduktion für lokale City Landing Pages auf selectedleafs.com. Definiert das Stadtteil-Geographie-Template, Content-Architektur, Compliance-Regeln, Daten-Checkliste und Qualitätskriterien für stadtspezifischen SEO-Content. Use whenever writing, reviewing, planning, or briefing city page content — including Textskizzen, page.content-Entwürfe, FAQ-Ergänzungen, Info-Box-Items, oder Content-Audits für lokale Landing Pages. Auch relevant wenn der Content Agent City-Texte generiert. Triggers on: city page, city content, lokale landing page, stadtspezifisch, Kratom kaufen in [Stadt], Stadtteil, Store Finder Content, lokaler SEO-Text, City SEO, Fußgänger-Traffic, Footfall-Content."
---

# City Content — Lokale Landing Pages

Content-Strategie und Produktionsanleitung für stadtspezifische Landing Pages.

**Scope:** Nur der redaktionelle Content (Section 4: SEO Content). Für die technische Section-Implementierung → Briefing-Dokument. Für die Gesamt-Seitenarchitektur (8 Sections) → Briefing-Dokument.

**Abhängigkeiten:**
- Compliance-Regeln → `legal.md` (PK)
- Sortenprofil-Daten → `sortiment.md` (PK)
- Indexierte Collections → `seo.md` (PK)
- Store-Daten → Shopify MCP: `listMetaobjects(type: "liftr_store")`

---

## 1. Kernfunktion der Section

| Rang | Funktion | Was das bedeutet |
|------|----------|------------------|
| Primär | Lokale Orientierung | Mentales Bild der Stadt vermitteln — Stadtteile, Erreichbarkeit, Viertel-Charakter |
| Sekundär | Google-Relevanz | Stadtspezifischer Fließtext, interne Links, lokale Entities (Stadtteilnamen, Straßen, Haltestellen) |
| Tertiär | Audit-Lücken schließen | Preisparität, Anfahrt, Mitnahme-Vorteil — über Info-Box + natürliche Erwähnungen |

**Nicht die Funktion dieser Section:** Kratom erklären (→ FAQ), Qualität beweisen (→ Product Carousel), Stores auflisten (→ Store List), Trust-Badges zeigen (→ Marquee).

---

## 2. Content-Template

### Struktur

```
H2: So kommst du hin — Dein Weg zum nächsten Store in [Stadt]
    ↳ Keyword-frei. Hero + H1 tragen das Primary Keyword.
      H2 signalisiert dem Scanner: "Hier kommt die Wegbeschreibung."
      Keine konkreten Store-Zahlen (skaliert nicht).

    [Intro: ~80 Wörter]
    1. Erster Satz: "Kratom kaufen in [Stadt]" als Phrase
       (Primary Keyword im ersten Fließtext-Satz).
    2. "Warum lokal?": 1 Satz Offline-Vorteil
       (sofort mitnehmen, kein Versand, Sorten direkt vor Ort sehen).
       NIE Beratung — Partner beraten NICHT (siehe §4).
    3. Sortiment als "Auswahl" (NICHT "volles/komplettes Sortiment").
    4. Räuchermischung-Erwähnung.
    5. Skalierbar: Keine konkreten Partner-Zahlen.
    6. Hinleitung zu den Stadtteilen.

<!-- block:store-summary -->

H3: [Stadtteil] — [Tagline mit funktionalem USP]
    ↳ Taglines geben dem Scanner sofort Orientierung:
      Lage-Anker + funktionaler USP.
      Beispiele:
      "Calenberger Neustadt — Zentral am Steintor, 7 Tage geöffnet"
      "Linden-Nord — Szeneviertel mit Spätverkauf bis in die Nacht"
      "Nordstadt — Direkt an der Uni, schon ab 7 Uhr morgens"

    [Stadtteil-Absätze: ~300 Wörter]
    Pro Stadtteil/Cluster ein Absatz.
    Lage → Erreichbarkeit → Besonderheit → Öffnungszeiten-Highlight.
    Stores werden namentlich erwähnt, aber der Text
    handelt vom VIERTEL — nicht vom Store.

    Theme-Blöcke (Sortiments-Übersicht, Testimonial, Info-Box)
    werden ZWISCHEN die Absätze gestreut — als Lese-Auflockerung
    und optischer Rhythmus, NICHT am Ende geclustert (siehe §7).

    [Schluss-Absatz: ~50 Wörter, KEIN eigenes Heading]
    Überleitung zum Sortiment, Collection-Links, Soft-CTA.
    KEINE Wiederholung der Info-Box-Fakten.
    Optional: Online-Fallback ("Nicht in [Stadt]? Wir liefern deutschlandweit.")
```

### Heading-Regeln

| Regel | Begründung |
|---|---|
| H2 enthält KEIN Primary Keyword | Hero + H1 tragen "Kratom kaufen in [Stadt]". H2-Dopplung = Stuffing ohne SEO-Mehrwert |
| Keine H3 als Zwischen-Heading | Die alte H3 ("Kratom in [Stadt] — Wo du uns findest") duplizierte H2 + Keyword. Stadtteile als H3 gliedern sich selbst |
| H3 = Stadtteile mit Taglines | Format: "[Stadtteil] — [Lage-Anker], [funktionaler USP]". Konsistentes Muster, skaliert bei neuen Stores |
| H3-Taglines: keine konkreten Zahlen | "7 Tage geöffnet" statt "3 Stores" — Zahlen veralten bei Store-Netzwerk-Ausbau |

### Wortanzahl

| Ziel | Minimum | Maximum | Begründung |
|------|---------|---------|------------|
| Section 4 gesamt | 450 | 550 | Unter 450 → Thin Content Signal. Über 550 → verführt zu generischem Füllen |
| Gesamtseite (mit FAQ) | 900 | 1100 | Solide für lokale Transaktionsseite |

### Warum Stadtteil-Geographie (nicht Store-Portraits)

- **Skaliert:** Bei 10+ Stores gruppieren sich mehrere pro Stadtteil → Text wird dichter, nicht länger
- **Kein Duplicate Content Risiko:** Stadtteile sind unique pro Stadt
- **Keine Duplikation mit Section 2:** Store List zeigt WELCHE Stores es gibt (Daten). Section 4 erzählt WIE die Stadt aufgebaut ist (Kontext)
- **Kein Partner-Fairness-Problem:** Kein Store bekommt ein eigenes Heading
- **Wartbar:** Neuer Store im bestehenden Viertel = 1 Halbsatz ergänzen, nicht neuen Absatz

### Pro-Stadtteil-Absatz Muster

Jeder Absatz folgt derselben Dramaturgie, aber mit unterschiedlichem Viertel-Charakter:

1. **Lage verorten** — Straßenname, Nachbarschaft, Landmarks ("Nähe Maschsee", "fußläufig zur Uni")
2. **Erreichbarkeit** — ÖPNV (Haltestelle + Linie), Parken wenn relevant
3. **Besonderheit** — Was macht das Viertel / den Store dort besonders? (Rating, Lieferung, Szene, Öffnungszeiten)
4. **Alltagssituation** — Konkreter Anlass ("nach Feierabend", "in der Mittagspause", "vor dem Seminar")

---

## 3. Sortiments-Formulierungen

**Jeder Partner entscheidet selbst, welche Produkte er führt.** Kein Partner führt garantiert das gesamte Sortiment. Der Text muss stimmen, egal ob ein Store 2 oder 9 Sorten anbietet.

### Erlaubt

- "...führen eine Auswahl aus dem selectedleafs Sortiment als Kratom Räuchermischung"
- "Von Red Vein bis White Vein — vor Ort direkt zugreifen"
- "...mit Charakter-Beschreibung und Herkunft — von kräftig-warm bis frisch-intensiv"

### Verboten

- "...führen das **volle/komplette** selectedleafs Sortiment" (faktisch falsch)
- "**Alle** 11 Sorten vor Ort" (faktisch falsch)
- "...hast du vor Ort **alles** in der Hand" (impliziert Vollständigkeit)
- Konkrete Sortenzahlen pro Store, es sei denn aus Metaobject verifiziert und als stadtspezifische Aussage formuliert

---

## 4. Compliance-Checkliste

**VOR jeder Veröffentlichung prüfen. Keine Ausnahmen.**

> **Hartes No-Go: Beratung.** Die Partner beraten NICHT. Niemals „Beratung", „Empfehlung", „Einschätzung", „berät dich", „hilft bei der Sortenwahl" o.ä. — auch nicht implizit. Offline-Vorteil immer als Self-Service framen: *vor Ort sehen, vergleichen, direkt mitnehmen, selbst entscheiden*.

| Regel | Anforderung | Wie prüfen |
|---|---|---|
| "Räuchermischung" | Mind. 1× im Text | Ctrl+F |
| "Wirkung" / "Effekt" | NICHT vorhanden | Ctrl+F |
| "Beratung" / "Empfehlung" / "Einschätzung" | NICHT vorhanden (Partner beraten nicht) | Ctrl+F |
| "Kapseln" / "Extrakte" | NICHT vorhanden | Ctrl+F |
| Dosierungshinweise | KEINE | Manuell lesen |
| Health Claims | KEINE | Manuell lesen |
| "Charakter" / sensorisch | Erlaubt als Alternative zu "Wirkung" | — |
| Interne Links | Nur indexierte Collections | Gegen seo.md prüfen |

### Verbotene Formulierungen

- "...wirkt entspannend" / "...für mehr Energie"
- "...ideal zur Entspannung nach dem Feierabend" (impliziter Health Claim)
- "Kratom Kapseln" / "Kratom Extrakt" (Produkte die nicht existieren)
- "...mit ehrlicher Beratung" / "persönliche Einschätzung" / "bekommt hier ehrliche Empfehlungen" (Partner beraten NICHT — stattdessen: "vor Ort siehst du die Sorten direkt", "entscheidest in Ruhe selbst")

---

## 5. SEO-Optimierung

### Keyword-Platzierung

| Position | Anforderung |
|---|---|
| Erster Satz Fließtext | "Kratom kaufen in [Stadt]" als natürliche Phrase |
| H2 | Keyword-FREI (Hero + H1 tragen es bereits) |
| Stadtteil-Absätze | "Kratom" natürlich verteilt, mind. 1× pro 150 Wörter |
| Gesamttext | "Kratom" 5-8× über den Text, natürlich eingebaut |

### `<strong>`-Tags

Semantisches Signal für Google — sparsam einsetzen, maximal 5 pro Text.

| Was markieren | Warum |
|---|---|
| Store-Namen (bei Erstnennung) | Entity-Signal: "Diese Seite handelt von diesen konkreten Geschäften" |
| "Räuchermischung" | Compliance-Term als Entity-Signal verankern |
| Herausragendes Rating (z.B. "4,9 Sternen bei über 180 Bewertungen") | Social Proof visuell + semantisch hervorheben (E-E-A-T) |

**Regeln:**
- `<strong>`, NICHT `<b>` (semantisch vs. rein visuell)
- Maximal 5 pro Text — wenn alles fett ist, ist nichts fett
- Nur bei Erstnennung des Store-Namens, nicht bei jeder Wiederholung
- Keine `<strong>` auf Keywords — das ist Stuffing-Signal

**Priorität & Verteilung (bei vielen Stores):** Das ≤5-Limit gilt hart — alle Store-Namen zu fetten sprengt es. Reihenfolge der Vergabe: (1) „Räuchermischung" 1×, (2) das herausragendste Rating 1×, (3) die restlichen Bolds als Store-Namen, **über die Section verteilt** (nicht alle oben). Fett ist Betonung der *wenigen* wichtigsten Entitäten — NICHT optischer Rhythmus. Der optische Rhythmus kommt aus den Theme-Blöcken (§7), nicht aus Fettungen.

### Interne Verlinkung

#### Erlaubte Link-Ziele (nur indexierte Collections)

| Ankertext-Muster | Ziel |
|---|---|
| **Kratom kaufen** | /collections/kratom |
| Kratom Räuchermischung / Kratom Sortiment | /collections/kratom |
| Kratom Pulver | /collections/kratom-pulver |
| Red Vein | /collections/red-vein-kratom |
| Green Vein | /collections/green-vein-kratom |
| White Vein | /collections/white-vein-kratom |
| Bali Kratom / Bali Sunset | /collections/bali-kratom |
| Borneo Kratom | /collections/borneo-kratom |
| Indo Kratom | /collections/indo-kratom |
| Sumatra Kratom / Suma Rush | /collections/sumatra-kratom |
| Java Kratom | /collections/java-kratom |
| Testsets & Sparbundles | /collections/kratom-testsets-sparbundles |
| Bestseller | /collections/bestseller |

**Regel:** 5-8 interne Links pro City Page Text. Natürlich im Fließtext eingebaut, nicht als Liste. Mindestens je 1× eine Vein-Collection und 1× die Hauptcollection (bevorzugt als "Kratom kaufen") verlinken.

**Verteilung — nach Ziel-Collection, nicht nach Absatz:** Ein Link sitzt nur dort, wo die Sorte/das Produkt natürlich erwähnt wird. Produktbezug entsteht v.a. in Intro (Sortenwahl), im Sorten-/Charakter-Satz eines Stores und im Schluss-Absatz — **Lage-/Logistik-Absätze** (Öffnungszeiten, Haltestelle, Paketshop) tragen legitim **0 Links** und ranken über lokale Entitäten (Straßen, Haltestellen, Stadtteile). Links NICHT in solche Absätze zwingen — das ist „Liste im Fließtext"/Stuffing.

**First-Link-Priority:** Google wertet bei mehreren Links auf dieselbe URL von einer Seite primär den ersten. Dieselbe Collection mehrfach zu verlinken bringt SEO-seitig kaum etwas (max. 1–2× sinnvoll, z.B. `/collections/kratom` als „Kratom kaufen" + einmal als „Kratom Räuchermischung"). Ziel: viele *verschiedene* Collections über mehrere Absätze, nicht dieselbe oft.

**NICHT verlinken:** noindex-Collections (Energie, Entspannung, Fokus, Balance, Stimmung), Blog (existiert noch nicht), andere City Pages (kein Cross-Linking zwischen Städten).

---

## 6. Daten-Checkliste: Store-Metaobject

Vor dem Schreiben diese Daten per MCP abrufen:

```
shopify-selectedleafs:listMetaobjects(type: "liftr_store")
```

Relevante Felder pro Store:

| Feld | Content-Nutzung |
|------|----------------|
| `name` | Store-Name im Fließtext |
| `adress` | Straßenname für lokale Verortung |
| `postal_code` | Stadtteil-Zuordnung |
| `district` → `.name` | Stadtteil-Name (Metaobject-Referenz auflösen!) |
| `rating` → `.value` | Hervorheben wenn besonders gut (4.5+) |
| `rating_count` | Für Glaubwürdigkeit ("über 180 Bewertungen") |
| `highlights` | Store-Besonderheiten (Lieferung, Paketshop, lange geöffnet, etc.) |
| `opening_hours` | Öffnungszeiten-Highlights (spät, früh, 7 Tage) |
| `product_list` | Welche Produkte der Store führt — KEINE Vollsortiment-Claims ohne Prüfung |
| `google_place` → `.location` | Geo-Koordinaten für ÖPNV-Zuordnung |

**Wichtig:** ÖPNV-Daten (Haltestellennamen, Liniennummern) NICHT aus den Metaobjects — die müssen separat verifiziert werden (lokaler ÖPNV-Anbieter, z.B. ÜSTRA für Hannover).

---

## 7. Zusatzelemente (Theme Blocks)

### Info-Box "Gut zu wissen"

Standard-Items (gelten für jede Stadt mit live Stores):

1. Gleiche Preise wie im Online-Shop
2. Sorten direkt vor Ort sehen & sofort mitnehmen
3. Bar- & Kartenzahlung möglich
4. 7 Tage die Woche geöffnet *(stadtabhängig gegen Metaobjects prüfen — wenn ein Partner nicht 7/7 öffnet, alternativen Punkt wählen)*

Anpassung pro Stadt wenn nötig (z.B. "Lieferung möglich" wenn alle Stores das bieten). Item-Anzahl: 2–6. Kein Beratungs-Item (Partner beraten nicht, §4).

**Platzierung:** Zwischen die Stadtteil-Absätze gestreut — als Lese-Auflockerung und optischer Rhythmus, NICHT am Ende geclustert. Die Blöcke (Sortiments-Übersicht, Testimonial, Info-Box) sollen den Fließtext angenehm gliedern; konkrete Positionen im Theme-Editor steuerbar. Faustregel: nie mehr als ~2–3 Absätze am Stück ohne auflockerndes Element.

### Testimonial / Kundenstimme

| Feld | Hinweis |
|------|---------|
| Zitat | Kurz (1-2 Sätze), stadtspezifisch, Store-Name erwähnen |
| Quelle | "Google Review, [Stadt]" oder "Kunde aus [Stadt]" |
| Sterne | 4-5 (nur positive Zitate) |

**Offener Punkt:** Rechtsgrundlage für Zitat-Nutzung klären (→ TODO-040). Google Reviews wörtlich zu zitieren kann ToS-Probleme machen. Sicherer: Eigene Kundenzitate mit Einwilligung sammeln, oder sinngemäß paraphrasieren. Kein Beratungs-/Wirkungsbezug im Zitat (§4).

**Platzierung:** Wie die Info-Box ein Auflockerungselement — zwischen die Stadtteil-Absätze gestreut, nicht geclustert.

### Button Group

Standard-CTAs:

| Button | Typ | Ziel | Anker |
|--------|-----|------|-------|
| "Alle Kratom Sorten entdecken" | Primary | /collections/kratom | Neuer Tab / Scroll zu Section 5 |
| "Store in deiner Nähe finden" | Secondary | #store-list | Scroll zu Section 2 |

---

## 8. Tonalität

| Aspekt | Regel |
|---|---|
| Grundton | Warm-informativ, wie ein lokaler Tipp |
| Perspektive | Marke ("wir/unser"), Du-Anrede |
| Nicht | Shop-Ton ("Alles was verkauft") — eher Blog-Ton |
| Aktivierungsgrad | Sachlich, aber persönlich. Kein Hard-Sell, kein Urgency |
| Lokaler Bezug | Alltagssituationen statt abstrakte Vorteile |
| Stores erwähnen | Namentlich, aber eingebettet im Stadtteil-Kontext |
| Skalierbarkeit | Keine konkreten Zahlen (Store-Anzahl, Sorten-Anzahl) die bei Netzwerk-Ausbau veralten |
| Lesefluss | Flüssig, locker, fürs Auge angenehm: kurze Sätze, klare Absätze, ein Gedanke pro Satz. Theme-Blöcke gliedern den Text optisch (§7). Keine Link-/Fett-Wände |

### Stilregeln (Anti-AI-Patterns)

| Vermeiden | Stattdessen |
|---|---|
| Mehr als 1 rhetorische Frage pro Text | Direkte Aussage oder Aufforderung |
| "[Stadt] hat eine lebendige Kratom-Szene" | Konkreten Fakt setzen, nicht aufblähen |
| "Mitten im Herzen der Stadt" | Konkreten Orientierungspunkt nennen |
| Zusammenhanglose Store-Features (z.B. Paketannahme) | In Alltagskontext einbetten ("beides auf dem gleichen Weg erledigen") |
| "Entdecke jetzt", "Nur das Beste für dich" | Sachlich, warm, ohne Urgency |

**Beispiel-Ton (gut):**
> "Auf der Limmerstraße, einer der belebtesten Straßen Hannovers, findest du den Street Life Kiosk. Wer Linden kennt, kennt die Limmer: Cafés, Plattenläden, Spätis — und eben auch Kratom."

**Beispiel-Ton (zu verkäuferisch):**
> "Entdecke jetzt unsere premium Kratom-Auswahl bei unserem exklusiven Partner in Linden-Nord! Nur das Beste für dich!"

---

## 9. Audit-Matrix: Besucherbedürfnisse × Sections

Beim Erstellen oder Reviewen von City Content prüfen ob alle Bedürfnisse adressiert sind:

### Typ A — Sofort-Käufer (~40%)

| Bedürfnis | Section |
|---|---|
| Wo ist der nächste Store? | §2 Store List |
| Hat der Store offen? | §2 Store Cards |
| Wie komme ich da hin? | **§4 Stadtteil-Text** |
| Haben die meine Sorte? | §2 + §5 Carousel |
| Kann ich mit Karte zahlen? | §2 Highlights + **§4 Info-Box** |

### Typ B — Vergleicher (~35%)

| Bedürfnis | Section |
|---|---|
| Gleiche Qualität wie online? | §3 Marquee + **§4 Info-Box** |
| Gleicher Preis? | **§4 Info-Box** |
| Kann ich den Partnern vertrauen? | §2 Ratings + **§4 Testimonial** |
| Warum lokal statt online? | **§4 Intro** ("Warum lokal?"-Satz) + §3 Marquee |
| Welcher Store passt zu mir? | **§4 Stadtteil-Text** (Viertel-Charakter) + **H3-Taglines** |

### Typ C — Einsteiger (~25%)

| Bedürfnis | Section |
|---|---|
| Was ist Kratom? | §7 FAQ |
| Ist das legal? | §7 FAQ |
| Welche Sorte für mich? | §5 Carousel + **§4 Collection-Links** |
| Wie ist die Store-Erfahrung? | **§4 Testimonial** + §7 FAQ (neu) |
| Ist selectedleafs seriös? | §6 Social Proof + §2 Ratings |
| Online-Alternative? | §8 Fallback CTA |

---

## 10. Skalierung: Städte ohne Stores

Für Städte ohne live Partner-Stores (Hamburg, Berlin, Köln, Frankfurt, München) funktioniert dieses Template NICHT 1:1. Es gibt keine Stadtteile zu beschreiben, keine Stores zu erwähnen, keine ÖPNV-Daten.

**Empfohlener Ansatz:** Eigenes Template entwickeln wenn diese Städte dran sind. Nicht das Hannover-Template mit generischem Content auffüllen — das erzeugt exakt den Duplicate Content den wir vermeiden wollen.

**Mögliche Richtungen für Städte ohne Stores:**
- "Coming Soon" Framing mit Newsletter-Capture
- Online-Bestell-Fokus mit Versand-nach-[Stadt] Messaging
- Lokale Szene/Community beschreiben (wenn recherchierbar)

→ Separater Chat / separate Skill-Erweiterung wenn relevant.

---

## 11. Qualitäts-Checkliste (vor Veröffentlichung)

- [ ] **Unique:** 0% Copy-Paste von anderen City Pages
- [ ] **Wortanzahl:** 450–550 Wörter (Section 4 allein)
- [ ] **Compliance:** Alle 8 Regeln aus Abschnitt 4 geprüft
- [ ] **Keine Beratung:** Kein "Beratung"/"Empfehlung"/"Einschätzung" — Offline-Vorteil als Self-Service formuliert
- [ ] **Sortiments-Claims:** Keine "volles/komplettes Sortiment"-Aussagen, keine konkreten Sorten-Zahlen ohne Metaobject-Prüfung
- [ ] **Skalierbarkeit:** Keine konkreten Store-Zahlen die bei Netzwerk-Ausbau veralten
- [ ] **ÖPNV verifiziert:** Haltestellennamen + Linien gegen lokalen Anbieter geprüft
- [ ] **Links:** 5-8 interne Links, verschiedene Ziel-Collections, keine erzwungenen Links in Lage-Absätzen, "Kratom kaufen" als Hauptanker
- [ ] **"Räuchermischung":** Mindestens 1× vorhanden
- [ ] **Keyword:** "Kratom kaufen in [Stadt]" im ersten Fließtext-Satz
- [ ] **`<strong>`-Tags:** max. 5 gesamt (Räuchermischung + Rating + verteilte Store-Namen)
- [ ] **Block-Verteilung:** Theme-Blöcke zwischen die Absätze gestreut, nicht geclustert; nie >2–3 Absätze am Stück ohne Auflockerung
- [ ] **Lesefluss:** Flüssig, locker, fürs Auge angenehm — keine Link-/Fett-Wände
- [ ] **Kein generischer Content:** Nichts was auch für eine andere Stadt stimmen würde
- [ ] **Info-Box Items:** Stimmen mit tatsächlichen Store-Features überein (bes. Öffnungszeiten-Claim)
- [ ] **Testimonial:** Quelle verifiziert, Rechtsgrundlage geklärt
- [ ] **Store-Daten aktuell:** Gegen Metaobjects geprüft (Rating, Öffnungszeiten, Highlights, product_list)
- [ ] **Anti-AI:** Max. 1 rhetorische Frage, keine Klischees, keine unbelegten Behauptungen

---

## Changelog

| Datum | Änderung |
|-------|----------|
| 2026-06-01 | v3: **Beratungsverbot** als harte Compliance-Regel (Partner beraten NICHT — keine "Beratung"/"Empfehlung"/"Einschätzung"; Offline-Vorteil = Self-Service). §1/§2/§6/§7 von Beratungs-Framing bereinigt (Info-Box-Item 2 „Persönliche Beratung" → „Sorten vor Ort sehen & mitnehmen"). **Theme-Blöcke neu als Lese-Auflockerung** zwischen die Absätze gestreut statt Info-Box am Ende (§2/§7) — Begründung: optischer Rhythmus, flüssige Lesbarkeit. **Link-Verteilung** nach Ziel-Collection + First-Link-Priority, Lage-Absätze dürfen 0 Links tragen (§5). **Fett-Verteilung**: ≤5-Priorität (Räuchermischung + Rating + verteilte Store-Namen), Fett ≠ Rhythmus (§5). Neue Tonalitäts-Regel „Lesefluss" (§8). Checkliste erweitert. |
| 2026-03-28 | v2: Heading-Struktur (H2 keyword-frei, H3 mit Taglines statt H4), Sortiments-Regeln (keine Vollsortiment-Claims), SEO-Section (Keyword-Platzierung, `<strong>`-Tags, "Kratom kaufen" als Ankertext), Info-Box Item 4 aktualisiert, Skalierbarkeits-Regeln, Anti-AI-Stilregeln, erweiterte Qualitäts-Checkliste |
| 2026-03-10 | v1: Skill angelegt |
