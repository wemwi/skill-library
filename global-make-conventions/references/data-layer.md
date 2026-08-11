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

## Seitenlimit-Wächter

Airtable-Listen sind paginiert. Ein Verdikt, das auf einer möglicherweise
unvollständigen Trefferliste basiert (z.B. bei 100 Treffern und einem
impliziten Cutoff), muss in die Richtung degradieren, die keinen falschen
positiven Write erzeugen kann — im Zweifel „unklar" statt eines
automatischen Treffers. Bei einer Positionsliste, wo ein fehlender Eintrag
nur zu einem harmloseren „unklar" statt zu einem falschen Link führt, reicht
dagegen ein reiner Hinweis.
