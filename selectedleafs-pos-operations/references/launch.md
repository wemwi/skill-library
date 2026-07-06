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
