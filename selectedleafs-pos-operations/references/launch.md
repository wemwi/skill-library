# Launch — neuen POS-Partner anlegen

Telegram-Dialog zum Anlegen eines neuen POS-Partners: Metaobjekt (`liftr_store`) schreiben und anschließend einen „Neuer Partner"-Post (🎉) in den zuständigen City-Channel absetzen.

> **TODO** — Domäne noch nicht migriert. Inhalt folgt in einem späteren Schritt. Das 🎉-Post-Template liegt übergangsweise in `telegram.md` §5 und zieht hierher um, sobald die Domäne gebaut wird.

## note-Marker setzen — Pflichtschritt (schon jetzt verbindlich)

Auch solange der restliche Launch-Flow TODO ist, gilt dieser Schritt **hart**: Bei Anlage eines neuen POS-Partner-Stores bekommt der zugehörige **Lexware-Store-Kontakt** die `note`

```
POS-PARTNER: <Vertriebler>
```

`<Vertriebler>` = der exakte Vertrieblername aus `registry.md` §4 (zeichengenau — er ist der Lookup-Schlüssel in `invoice.md` §2). Gesetzt via `create_contact` (neuer Kontakt) bzw. `update_contact` (bestehender Kontakt; dann `note` als **einziges** geändertes Feld, volles Objekt + `version` mitsenden).

**Warum das der tragende Schritt ist:** Die note ist die EINE Wahrheitsquelle für „ist POS-Partner" (agent-bridge note-Gate) **und** für den Vertriebler (`invoice.md` §2). Das Design hat **keinen** Fallback — ein neu angelegter Partner-Store **ohne** Marker fällt still durch: kein Event startet eine Session, keine Provision wird eingetragen, kein Fehler wird sichtbar. Der note-Marker ist damit kein optionaler Nachtrag, sondern integraler Teil der Partner-Anlage.

**Robustheit:** Schlägt das `create_contact`/`update_contact` fehl, ist die Partner-Anlage **nicht** abgeschlossen — fail-closed abbrechen und Fehler melden (`global-agent-framework` §13), nicht den 🎉-Post absetzen und den Marker „später" nachholen. Der Marker gehört in denselben atomaren Anlage-Schritt wie das Metaobjekt.

> Solange die Launch-Domäne nicht gebaut ist, werden neue Partner manuell angelegt — dann ist dieser Marker ein **manueller Pflicht-Handgriff** bei jedem neuen Store (bis der Flow ihn automatisiert). Bereits bestehende Partner-Stores wurden per Einmal-Migration getaggt.

## Store-Zeile im Provisions-Sheet — Lexware-Kundennummer als Key (schon jetzt verbindlich)

Legt der Launch die Partner-Zeile im `Stores`-Tab des Vertriebler-Sheets an, ist der **Key in `Stores!B` (Spalte „Kunden-Nr“) die Lexware-`roles.customer.number`** des frisch angelegten Kontakts — **nicht** eine JTL-Nummer. Grund fürs Timing: zum Anlage-Zeitpunkt ist der Store neu, eine JTL-Nummer existiert noch nicht; `create_contact` vergibt die Lexware-Nummer sofort, sie ist damit die **einzige** zum Launch verfügbare, stabile Kennung.

Dieselbe Nummer ist der Store-Match-Key, den `invoice.md` §4 gegen `Stores!B5:B` prüft und den der Insert in `Umsatz!E` schreibt (§6.1) — Sheet und Lexware teilen bewusst **einen** Nummernraum (Lexware). Wie beim note-Marker gibt es **keinen Fallback**: eine Partner-Zeile ohne korrekt gesetzte Lexware-`roles.customer.number` in `Stores!B` fällt beim §4-Match still durch (kein Provisions-Eintrag, kein Fehler).

> Bis der Launch-Flow gebaut ist, ist auch das ein **manueller Pflicht-Handgriff**: neue `Stores`-Zeile mit der Lexware-Kundennummer als Key. Die bestehenden 8 Partner-Zeilen (2025 + 2026) wurden per Einmal-Migration auf Lexware-Nummern umgestellt.
