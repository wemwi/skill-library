# B9 — Datenlayer (Airtable)

Dieser Bereich ist bewusst gekapselt: er gilt nur, wenn Airtable als
Datenbackend im Spiel ist. Ein Make-Projekt ohne Airtable überspringt ihn
komplett.

## Datum als reiner String

Belegdaten und andere geschäftskritische Datumsfelder werden als reiner
`YYYY-MM-DD`-String geführt — kein `parseDate`, keine implizite
Zeitzonen-Umrechnung. Datumslogik über String-Vergleich/-Zerlegung
(Substring, Präfix-Match) vermeidet die Klasse von Fehlern, die aus
Zeitzonen-Verschiebung bei Tagesgrenzen entsteht (ein Datum, das durch eine
UTC-Umrechnung einen Tag springt).

## Explizite Formatierungs-Parameter bei REST-Reads

Beim direkten REST-Zugriff (siehe `modules.md`, Musterausnahme — aktuell
`http:MakeRequest` v4, nicht das Legacy-v3-HTTP-Modul) werden `cellFormat`,
`timeZone` und `userLocale` explizit über die `queryParameters`-Liste des
Moduls gesetzt — nicht in die URL konkateniert (siehe B10/Query-String-
Konvention). Ohne diese Parameter ist das Format von Link-Feldern
(Record-ID vs. Klartext) inkonsistent und von Airtable-seitigen Defaults
abhängig, die sich ändern können.

## `typecast: false` als Default

`typecast: true` erlaubt dem Write-Call, einen bislang unbekannten
Single-/Multi-Select-Wert automatisch als neue Option anzulegen — praktisch
beim ersten Prototyping, aber ein stiller Datenqualitäts-Bruch im Betrieb:
ein Tippfehler im geschriebenen Wert erzeugt eine neue, nie beabsichtigte
Auswahloption statt eines Fehlers. Produktive Writes setzen `typecast:
false` und schreiben ausschließlich Konstanten, die als Option bereits
existieren.

Zusätzlich wird der Wert eines produktiven Select-Writes als Options-**ID**
gesetzt (`{ "fld…": { "id": "sel…" } }` im REST-Body bzw. das ID-Objekt im
nativen Modul), nicht als Options-Name. Options-IDs (`sel…`) sind in
Airtable permanent — ein Umbenennen der Option lässt den Write unberührt.
Ein namensbasierter Write bricht bei einem Options-Rename *still*: Airtable
zieht Select-Optionen, anders als Feld-IDs in Formelfeldern/Views, nicht
nach. Damit schließt sich die Asymmetrie zur Read-Seite, die Choice-IDs
bereits nutzt (siehe `airtable-filters`, „Select fields").

Die Entscheidungslogik bleibt in lesbaren Options-Namen; eine einzige
Name→`sel`-ID-Tabelle (Code-Modul oder Mapping) übersetzt erst unmittelbar
vor dem Write. So bleibt der Blueprint lesbar und der Write rename-fest.
Die IDs stammen beim Bau aus dem Feld-Schema (`get_table_schema` →
`choices[].id`); Airtable akzeptiert beim Schreiben eines SingleSelects ein
Objekt mit `{id}` oder `{name}` (MultiSelect: Array solcher Objekte),
`{id}` ist die rename-feste Variante.

## Nie auf Formelfelder schreiben

Airtable weist einen Write auf ein Formelfeld mit HTTP 422 zurück. Ein
Feld, das im Schema als Formel definiert ist, ist ausschließlich Lesequelle
— jede Migration eines vormals beschreibbaren Feldes zu einer Formel zieht
zwingend die Entfernung aller Schreibzugriffe in den betroffenen Szenarien
nach sich.

## `filterByFormula` bindet an Namen, nicht IDs

Airtables Formel-Sprache adressiert Felder über ihren Namen, nicht ihre ID.
Jede Feldumbenennung ist damit potenziell eine stille Szenario-Änderung —
vor jeder Umbenennung wird geprüft, welche `filterByFormula`-Ausdrücke in
aktiven Blueprints den alten Namen referenzieren.

## Namensreferenzierende Prädikate nach innen — die Entscheidungsleiter

Der Feind ist nicht „Formula", sondern eine namensreferenzierende Formel, die
*außerhalb* Airtables lebt. Airtable speichert Feldreferenzen in Formeln intern
über die Feld-ID; benennt man ein Feld um, zieht Airtable jedes **Formelfeld** und
jeden **View-Filter** automatisch nach — die brechen nicht. Ein
`filterByFormula`-String in einem Make-Modul (oder ein im Code zusammengebauter
Filter-/Key-String) ist dagegen nur Klartext, den Airtable nie sieht und nie
umschreibt — der bricht *still*. (Ausnahme auch innen: umbenannte Select-*Optionen*
werden nicht nachgezogen → Lösung: Select-Werte per Options-ID schreiben,
siehe `typecast`-Abschnitt oben.)

Daraus die Reihenfolge im Blueprint — oberste greifende Sprosse gewinnt,
„Formula weglassen" gelingt auf 1–3 fast immer:

1. **Identität in der Hand → GET by Record ID.** Keine Formel.
2. **Parent→Kinder → Link-Feld traversieren:** die verlinkten Record-IDs am
   per-ID geladenen Parent ablesen (feld-ID-basiert) und per ID holen, statt zu
   suchen.
3. **Statisches Prädikat → Airtable-View:** der Filter lebt in Airtable
   (rename-safe), gelesen per `view`. Nur für feste Prädikate — ein View lässt
   sich nicht nach einem Laufzeitwert parametrisieren.
4. **Dynamischer Attribut-Match unvermeidbar →** `RECORD_ID()`-Filter, wo
   Identität reicht (Formel, aber ohne Feldname = rename-safe); sonst genau *eine*
   namensbasierte `filterByFormula`, eingedämmt per Pre-Rename-Check (voriger
   Abschnitt).

Ein dynamischer Attribut-Match („finde den Record, wo Feld = Laufzeitwert") lässt
sich nicht formelfrei lösen — Airtable hat keine feld-ID-basierte Query-Sprache,
`filterByFormula` ist der einzige dynamische Filter der API. Das ist die harte
Grenze, an der Sprosse 4 unvermeidlich wird — nicht der Normalfall.

## Seitenlimit-Wächter

Airtable-Listen sind paginiert. Ein Verdikt, das auf einer möglicherweise
unvollständigen Trefferliste basiert (z.B. bei 100 Treffern und einem
impliziten Cutoff), muss in die Richtung degradieren, die keinen falschen
positiven Write erzeugen kann — im Zweifel „unklar" statt eines
automatischen Treffers. Bei einer Positionsliste, wo ein fehlender Eintrag
nur zu einem harmloseren „unklar" statt zu einem falschen Link führt, reicht
dagegen ein reiner Hinweis.
