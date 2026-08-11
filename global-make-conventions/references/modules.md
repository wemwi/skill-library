# B3 — Modul-Wahl

## Native Module vor generischem HTTP

Native App-Module kapseln Auth, Rate-Limit-Verhalten, Antwortformat und
Feld-Validierung — ein generischer HTTP/API-Call muss all das von Hand
nachbilden und bricht bei API-Änderungen leiser. Native ist deshalb die
Grundregel.

**Dokumentierter Grund reicht für die Ausnahme**, ersetzt sie aber nicht:
jeder HTTP-Call gegen eine App, die auch ein natives Modul hätte, braucht
eine Zeile, warum das native Modul nicht ausreicht.

### Musterausnahme aus der Praxis (Airtable-REST statt nativer Suche)

In einer produktiven POS-Automatisierung wurde bewusst ein HTTP-Modul gegen
die Airtable-REST-API genutzt statt der nativen Airtable-Suche — aus zwei
konkreten, dokumentierten Gründen. **Wichtig für den Audit:** das aktuelle,
korrekte HTTP-Modul dafür ist `http:MakeRequest` (v4, „Make a request") —
die v3-Reihe (`http:ActionSendData*`, u.a. `ActionSendDataAPIKeyAuth`) ist
selbst Legacy und fällt unter das Verbot oben. Bestehende v3-Aufrufe sind
beim nächsten Umbau auf v4 zu migrieren, nicht als Vorbild zu kopieren.

1. **Deterministische Formatierungs-Parameter.** Die native Suche liefert
   Link-Felder wahlweise als Record-ID oder Objekt, aber nicht konfigurierbar
   als lesbarer Klartext. Der REST-Call mit expliziten Query-Parametern
   (`cellFormat=string&timeZone=…&userLocale=…`) liefert Link-Felder direkt
   als Primärwert im Klartext — dadurch entfällt ein sonst nötiges
   Auflösungs-Modul pro Link-Feld.
2. **Ein Bundle statt Suchmodul-Bundle-Overhead.** Mehrere zusammengehörige
   Reads (z.B. Bestandsprüfung + zugehörige Positionen) ließen sich als ein
   REST-Call mit einem Bundle abbilden, wo die native Suche mehrere Bundles
   mit Aggregator-Overhead erzeugt hätte.

Das ist die Referenz für „dokumentierter Grund" — nicht „HTTP ist
bequemer" oder „ich kenne das Modul schon", sondern ein konkretes fehlendes
natives Feature mit belegbarer Notwendigkeit.

## Kein Legacy-/Deprecated-Modul

Make markiert veraltete Modulversionen in der App-Dokumentation. Neubau
verwendet immer die aktuelle Version; bestehende Legacy-Module werden beim
nächsten ohnehin fälligen Umbau mitmigriert — nicht als eigener Anlass, aber
auch nicht stillschweigend weiterkopiert in neue Szenarien.

**Bekanntes Beispiel:** das generische HTTP-Modul `http:ActionSendData*`
(v3, u.a. `ActionSendDataAPIKeyAuth`) ist Legacy — aktuell ist
`http:MakeRequest` (v4). v4 unterscheidet sich strukturell: Auth läuft über
`parameters.authenticationType` (`noAuth`/`apiKey` + `apiKeyKeychain`),
Query-Parameter heißen `queryParameters` als `{name, value}`-Liste, JSON-Body
über `contentType: json` + `inputMethod: jsonString` +
`jsonStringBodyContent`. v3- und v4-Keychains teilen sich denselben
ID-Raum — beim Umstieg wird eine bestehende Keychain-ID übernommen, kein
Tausch nötig.

**Check beim Audit:** `app_modules_list` für jedes im Blueprint verbaute
Modul gegenprüfen — jede als deprecated markierte Version ist ein Befund,
auch wenn sie noch funktioniert. Für das generische HTTP-Modul gezielt auf
`http:ActionSendData*` prüfen.
